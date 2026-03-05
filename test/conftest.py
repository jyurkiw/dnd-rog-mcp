"""
Shared pytest fixtures and the custom requirement-coverage report hook.
"""

import os
import pytest
from testcontainers.neo4j import Neo4jContainer


# ── Requirement category registry ────────────────────────────────────────────
# Maps prefix → (label, total requirements defined in DESIGN.md)
REQUIREMENT_CATEGORIES = {
    "GI": ("Graph Integrity",        10),
    "TH": ("Tier & Hierarchy",        8),
    "NF": ("Narrative Flow",         10),
    "NR": ("NPC & Relationships",     7),
    "WK": ("World Knowledge",         6),
    "EN": ("Encounters",              6),
    "BT": ("Boxed Text",             11),
    "TL": ("Timeline & History",      6),
    "SD": ("Soft Delete",            20),
    "IE": ("Import / Export",        10),
    "MP": ("MCP Protocol",            8),
    "LV": ("Low Verbosity",          10),
}

TOTAL_REQUIREMENTS = sum(n for _, n in REQUIREMENT_CATEGORIES.values())


# ── Neo4j container helpers ───────────────────────────────────────────────────

def _make_neo4j_container():
    """Spin up a Neo4j 5 test container and return it started."""
    container = Neo4jContainer("neo4j:5")
    container.with_env("NEO4J_AUTH", "neo4j/test-password")
    return container


def _driver_from_container(container):
    """Return a connected Neo4j driver from a running container."""
    from neo4j import GraphDatabase
    uri = container.get_connection_url()
    return GraphDatabase.driver(uri, auth=("neo4j", "test-password"))


# ── Neo4j fixtures ────────────────────────────────────────────────────────────

@pytest.fixture(scope="function")
def neo4j_fresh():
    """
    Fresh Neo4j container per test function.
    Used by: @isolated tests (soft delete, targeted mutation tests).
    Yields a connected driver. Container is torn down after the test.
    """
    with _make_neo4j_container() as container:
        driver = _driver_from_container(container)
        yield driver
        driver.close()


@pytest.fixture(scope="module")
def neo4j_module():
    """
    One Neo4j container shared across all tests in a module.
    Used by: Phase 2 CRUD integration tests.
    Yields a connected driver. Container torn down after the module.
    """
    with _make_neo4j_container() as container:
        driver = _driver_from_container(container)
        yield driver
        driver.close()


@pytest.fixture(scope="session")
def neo4j_seeded():
    """
    Session-scoped Neo4j container.
    The Phase 3 import test loads the full Shadowdale fixture into this
    container. All @requires_fixture tests share this same instance.
    Yields a connected driver. Container torn down at end of session.
    """
    with _make_neo4j_container() as container:
        driver = _driver_from_container(container)
        yield driver
        driver.close()


# ── Execution phase ordering ──────────────────────────────────────────────────

PHASE_ORDER = ["unit", "integration", "requires_fixture", "isolated", "slow"]


def pytest_collection_modifyitems(items, config):
    """Sort collected tests by execution phase marker."""
    def phase_key(item):
        for i, marker_name in enumerate(PHASE_ORDER):
            if item.get_closest_marker(marker_name):
                return i
        return len(PHASE_ORDER)  # unmarked tests run last

    items.sort(key=phase_key)


# ── Custom report hook ────────────────────────────────────────────────────────

def _extract_req_prefix(nodeid: str) -> tuple[str, str] | None:
    """
    Parse a test node ID for a requirement prefix.
    e.g. 'test/unit/test_graph_integrity.py::test_GI_01_uid_uniqueness'
    returns ('GI', 'GI-01').
    Returns None if the test name doesn't match the convention.
    """
    # Grab just the function name part
    if "::" not in nodeid:
        return None
    func_name = nodeid.split("::")[-1]
    parts = func_name.split("_")
    # Pattern: test_{CAT}_{NN}_...
    if len(parts) < 3 or parts[0] != "test":
        return None
    cat = parts[1].upper()
    num = parts[2]
    if cat not in REQUIREMENT_CATEGORIES or not num.isdigit():
        return None
    return cat, f"{cat}-{num.zfill(2)}"


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Print the requirement coverage report after the standard summary."""
    tr = terminalreporter

    # Collect outcomes per requirement ID
    # Structure: {cat: {req_id: "passed"|"failed"|"error"}}
    results: dict[str, dict[str, str]] = {cat: {} for cat in REQUIREMENT_CATEGORIES}

    for outcome in ("passed", "failed", "error"):
        for report in tr.stats.get(outcome, []):
            parsed = _extract_req_prefix(report.nodeid)
            if parsed is None:
                continue
            cat, req_id = parsed
            # Failures/errors take priority over a passing result for the same req
            existing = results[cat].get(req_id)
            if existing in ("failed", "error"):
                continue
            results[cat][req_id] = outcome

    # ── Print report ─────────────────────────────────────────────────────────
    WIDTH = 68
    BAR_WIDTH = 20

    def bar(passed, total):
        if total == 0:
            return "░" * BAR_WIDTH
        filled = round(BAR_WIDTH * passed / total)
        return "█" * filled + "░" * (BAR_WIDTH - filled)

    tr.write_sep("=", "dnd-rog-mcp  REQUIREMENT COVERAGE REPORT")
    tr.write_line("")
    tr.write_line(f"  {'CAT':<4}  {'REQUIREMENT':<26}  {'COVERAGE':<{BAR_WIDTH}}  {'RESULT':>12}")
    tr.write_line("  " + "─" * (WIDTH - 2))

    total_passed = 0
    total_tested = 0
    failing_tests = []

    for cat, (label, req_count) in REQUIREMENT_CATEGORIES.items():
        cat_results = results[cat]
        passed = sum(1 for v in cat_results.values() if v == "passed")
        failed_reqs = [rid for rid, v in cat_results.items() if v in ("failed", "error")]
        tested = len(cat_results)

        total_passed += passed
        total_tested += tested

        progress = f"{passed:>2} / {req_count:<2}"
        pct = f"{round(100 * passed / req_count):>3}%" if req_count else "  N/A"
        b = bar(passed, req_count)

        notes = ""
        if failed_reqs:
            notes = f"  ← {len(failed_reqs)} FAILING"
        elif tested == 0:
            notes = "  ← NOT YET WRITTEN"
        elif passed < req_count:
            not_written = req_count - tested
            notes = f"  ← {not_written} NOT YET WRITTEN"

        line = f"  {cat:<4}  {label:<26}  {b}  {progress}  {pct}{notes}"
        tr.write_line(line)

        # Collect failing test details for the bottom section
        for report in tr.stats.get("failed", []) + tr.stats.get("error", []):
            parsed = _extract_req_prefix(report.nodeid)
            if parsed and parsed[0] == cat:
                failing_tests.append(report)

    tr.write_line("  " + "─" * (WIDTH - 2))
    total_pct = f"{round(100 * total_passed / TOTAL_REQUIREMENTS):>3}%" if TOTAL_REQUIREMENTS else "N/A"
    total_bar = bar(total_passed, TOTAL_REQUIREMENTS)
    tr.write_line(
        f"  {'TOTAL':<4}  {'All Requirements':<26}  {total_bar}"
        f"  {total_passed:>2} / {TOTAL_REQUIREMENTS:<2}  {total_pct}"
    )
    tr.write_line("")

    # ── Failures detail ───────────────────────────────────────────────────────
    if failing_tests:
        tr.write_line("  FAILURES")
        tr.write_line("  " + "─" * (WIDTH - 2))
        seen = set()
        for report in failing_tests:
            if report.nodeid in seen:
                continue
            seen.add(report.nodeid)
            parsed = _extract_req_prefix(report.nodeid)
            req_label = parsed[1] if parsed else "???"
            func_name = report.nodeid.split("::")[-1]
            tr.write_line(f"  {req_label:<8}  {func_name}")
            # First line of the failure reason
            if hasattr(report, "longreprtext"):
                first_line = report.longreprtext.strip().splitlines()[-1]
                tr.write_line(f"            {first_line[:WIDTH - 12]}")
            tr.write_line("")

    tr.write_sep("=", "")
