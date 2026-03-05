# Test Architecture — dnd-rog-mcp

This document defines the testing architecture, dependency choices, configuration, reporting strategy, naming conventions, and execution order for the `dnd-rog-mcp` test suite.

---

## Table of Contents

1. [Philosophy](#philosophy)
2. [Project Structure](#project-structure)
3. [Dependencies](#dependencies)
4. [pytest Configuration](#pytest-configuration)
5. [Custom Test Report](#custom-test-report)
6. [Test Naming Conventions](#test-naming-conventions)
7. [Markers](#markers)
8. [Execution Order Strategy](#execution-order-strategy)
9. [Neo4j Fixture Scopes](#neo4j-fixture-scopes)
10. [Fixture Organization](#fixture-organization)
11. [Docker Test Environment](#docker-test-environment)

---

## Philosophy

The MCP server layer is intentionally kept thin. All business logic lives in `src/dnd_mcp/tools/` as pure functions that accept a Neo4j driver and arguments, perform work, and return structured results. `server.py` does nothing but register those functions as MCP tools.

This means the entire tool layer is testable by importing it directly. No MCP server is ever started during testing.

The import/export function is not just a feature under test — it is also a test infrastructure tool. The full Shadowdale adventure fixture is loaded into Neo4j via the `import_database` tool function, which both tests the import function itself and seeds the database for downstream read and query tests. There is no separate fixture-loading mechanism.

---

## Project Structure

```
dnd-rog-mcp/
├── src/
│   └── dnd_mcp/
│       ├── __init__.py
│       ├── db/
│       │   ├── __init__.py
│       │   ├── connection.py        ← Neo4j driver setup
│       │   └── queries.py           ← raw Cypher query functions
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── adventure.py         ← tool handlers grouped by domain
│       │   ├── entities.py
│       │   ├── narrative.py
│       │   ├── boxed_text.py
│       │   ├── encounters.py
│       │   ├── knowledge.py
│       │   ├── timeline.py
│       │   ├── soft_delete.py
│       │   ├── import_export.py
│       │   └── files.py
│       ├── models/
│       │   ├── __init__.py
│       │   └── nodes.py             ← dataclasses/schemas for all node types
│       └── server.py                ← MCP wiring only, no business logic
├── test/
│   ├── README.md
│   ├── test_architecture.md         ← this document
│   ├── test_data_adventure.md       ← Shadowdale adventure fixture spec
│   ├── conftest.py                  ← shared fixtures + custom report hook
│   ├── fixtures/
│   │   └── shadowdale.py            ← builder functions returning raw dicts
│   ├── unit/
│   │   ├── test_adventure.py
│   │   ├── test_entities.py
│   │   ├── test_narrative.py
│   │   ├── test_boxed_text.py
│   │   ├── test_encounters.py
│   │   ├── test_knowledge.py
│   │   ├── test_timeline.py
│   │   ├── test_soft_delete.py
│   │   ├── test_import_export.py
│   │   └── test_files.py
│   └── integration/
│       ├── test_graph_integrity.py
│       ├── test_tier_hierarchy.py
│       ├── test_narrative_flow.py
│       ├── test_npc_relationships.py
│       ├── test_soft_delete_cascade.py
│       └── test_import_export_roundtrip.py
├── docker-compose.yml               ← production stack
├── docker-compose.test.yml          ← test runner stack
├── Dockerfile
├── Dockerfile.test
├── pyproject.toml
├── .env.example
├── README.md
└── DESIGN.md
```

---

## Dependencies

Defined in `pyproject.toml` under `[project.optional-dependencies]`.

```toml
[project.optional-dependencies]
test = [
    "pytest>=8.0",
    "assertpy>=1.1",
    "testcontainers[neo4j]>=4.0",
    "pytest-timeout>=2.3",
    "pytest-order>=1.2",
]
```

### Dependency Rationale

| Package | Role | Why |
|---|---|---|
| `pytest` | Test runner and discovery | Industry standard; fixture system, markers, hooks |
| `unittest` | Base class and mocking | `unittest.mock.patch` and `MagicMock` for Neo4j driver mocking in unit tests; no additional install required |
| `assertpy` | Fluent assertions | `assert_that(result).contains_key("uid").is_not_empty()` reads clearly in failure output; chaining reduces boilerplate |
| `testcontainers[neo4j]` | Live Neo4j for integration tests | Spins up a real Neo4j container per fixture scope; tears down cleanly; no persistent volume between runs |
| `pytest-timeout` | Hard timeouts on integration tests | Container startup and graph queries need bounded execution time |
| `pytest-order` | Execution phase ordering | Enforces the six-phase test execution strategy without manual intervention |

### What Is Intentionally Excluded

- **`pytest-cov`** — coverage is useful but not a current requirement. Add later.
- **`pytest-html`** — replaced by the custom report hook (see below).
- **`faker`** — fixture data is fixed and defined in `shadowdale.py`, not randomly generated. Deterministic fixtures make failures reproducible.

---

## pytest Configuration

Defined in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
verbosity = 3
testpaths = ["test"]
timeout = 30
log_cli = true
log_cli_level = "WARNING"
markers = [
    "unit: pure unit tests, no DB required",
    "integration: requires a live Neo4j instance",
    "requires_fixture: depends on the Shadowdale fixture having been imported (Phase 3+)",
    "isolated: receives its own fresh DB, does not share state",
    "slow: long-running tests, skippable in fast dev cycles",
]
```

### What `--verbosity=3` Provides

- Full test node ID on each line (`test/unit/test_graph_integrity.py::test_GI_01_uid_uniqueness`)
- PASSED / FAILED / SKIPPED / ERROR per test with no truncation
- Full assertion diff output on failure via assertpy
- Collected item count and duration per test
- Summary counts at the end grouped by outcome

---

## Custom Test Report

### Approach: `pytest_terminal_summary` Hook in `conftest.py`

Rather than an HTML report or third-party plugin, the custom report is implemented as a `pytest_terminal_summary` hook. This hook fires after all tests complete and before pytest exits, giving it access to the full result set.

The hook exploits the test naming convention (see below) to group results by requirement category and print a structured summary to stdout.

### Report Output Format

```
════════════════════════════════════════════════════════════
 dnd-rog-mcp  TEST REPORT
════════════════════════════════════════════════════════════

 REQUIREMENT COVERAGE
 ─────────────────────────────────────────────────────────
  GI  Graph Integrity          ██████████  10 / 10   100%
  TH  Tier & Hierarchy         ████████░░   8 / 8    100%
  NF  Narrative Flow           ██████████  10 / 10   100%
  NR  NPC & Relationships      ███████░░░   5 / 7     71%  ← 2 FAILING
  WK  World Knowledge          ██████████   6 / 6    100%
  EN  Encounters                ██████░░░░   4 / 6     67%  ← 2 NOT YET WRITTEN
  BT  Boxed Text               ░░░░░░░░░░   0 / 11     0%  ← NOT YET WRITTEN
  TL  Timeline & History       ██████████   6 / 6    100%
  SD  Soft Delete              ████████████ 20 / 20  100%
  IE  Import / Export          ██████████  10 / 10   100%
  MP  MCP Protocol             ████████░░   6 / 8     75%  ← 2 FAILING
  LV  Low Verbosity            ██████████  10 / 10   100%
 ─────────────────────────────────────────────────────────
  TOTAL                        ██████████  95 / 102   93%

 FAILURES
 ─────────────────────────────────────────────────────────
  NR-04  test_NR_04_knows_relationship_type_required
         AssertionError: Expected key 'relationship_type' ...

  MP-07  test_MP_07_neo4j_connection_failure_graceful
         AssertionError: Expected error code 'DB_UNAVAILABLE' ...

════════════════════════════════════════════════════════════
```

### Implementation Overview

```python
# test/conftest.py (excerpt)

REQUIREMENT_CATEGORIES = {
    "GI": ("Graph Integrity",       10),
    "TH": ("Tier & Hierarchy",       8),
    "NF": ("Narrative Flow",        10),
    "NR": ("NPC & Relationships",    7),
    "WK": ("World Knowledge",        6),
    "EN": ("Encounters",             6),
    "BT": ("Boxed Text",            11),
    "TL": ("Timeline & History",     6),
    "SD": ("Soft Delete",           20),
    "IE": ("Import / Export",       10),
    "MP": ("MCP Protocol",           8),
    "LV": ("Low Verbosity",         10),
}

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """
    Parse test node IDs for requirement prefixes (e.g. test_GI_01_*).
    Group passed/failed/not-written per category.
    Print structured report to terminalreporter.
    """
    ...
```

The hook reads from `terminalreporter.stats` which contains lists of
`passed`, `failed`, `error`, and `skipped` report objects. Each report's
`nodeid` is parsed for the requirement prefix pattern `test_{CAT}_{NN}_`.

Categories with no tests matching a prefix show as `0 / N` rather than
being omitted, making unwritten test coverage visible at a glance. This
makes the report a live TDD progress tracker throughout development.

---

## Test Naming Conventions

All test functions are named with a requirement ID prefix:

```
test_{CATEGORY}_{NUMBER}_{short_description}
```

### Examples

```python
# Graph Integrity
def test_GI_01_uid_uniqueness(): ...
def test_GI_02_tier_property_required(): ...
def test_GI_10_fileref_path_unique(): ...

# Narrative Flow
def test_NF_05_event_merge_multiple_leads_to(): ...
def test_NF_08_dag_no_cycles(): ...
def test_NF_09_root_event_designated_per_plotline(): ...

# Soft Delete
def test_SD_11_true_delete_requires_disabled_node(): ...
def test_SD_17_true_delete_disabled_by_default(): ...
def test_SD_07_disable_respects_shared_node_protection(): ...

# Import / Export
def test_IE_05_import_fails_on_populated_db(): ...
def test_IE_09_full_roundtrip_fidelity(): ...
```

### Rules

- The prefix must exactly match a key in `REQUIREMENT_CATEGORIES` for the report hook to count it.
- The number must match the requirement ID in `DESIGN.md`.
- The short description is free-form snake_case, as descriptive as needed.
- A single requirement may have multiple test functions. All are counted toward that requirement's pass/fail total. The requirement is considered passing only when all of its test functions pass.
- Helper functions and fixtures do not use this prefix. Only `def test_*` functions that directly test a requirement are named this way.

---

## Markers

```python
@pytest.mark.unit
# Pure unit test. No DB. Mocks the Neo4j driver.
# Runs in Phase 1. Always runs first.

@pytest.mark.integration
# Requires a live Neo4j instance via testcontainers.
# Runs in Phases 2–6.

@pytest.mark.requires_fixture
# Depends on the Shadowdale fixture having been imported
# by the Phase 3 import test. Will fail or produce incorrect
# results if run before Phase 3 completes.

@pytest.mark.isolated
# This test manages its own fresh DB.
# Gets a function-scoped Neo4j fixture.
# Used for soft delete tests and any test that mutates state
# in ways that would corrupt shared fixture data.

@pytest.mark.slow
# Long-running. Safe to skip during fast dev iteration.
# docker-compose.test.yml always runs these.
# Local dev can skip with: pytest -m "not slow"
```

Markers are not mutually exclusive. A typical integration test that reads
from the seeded fixture looks like:

```python
@pytest.mark.integration
@pytest.mark.requires_fixture
def test_NF_05_event_merge_multiple_leads_to(neo4j_seeded):
    ...
```

A soft delete test looks like:

```python
@pytest.mark.integration
@pytest.mark.isolated
def test_SD_07_disable_respects_shared_node_protection(neo4j_fresh):
    ...
```

---

## Execution Order Strategy

Tests execute in six phases, enforced by `pytest-order` and marker grouping.

```
Phase 1 — Unit Tests                        @unit
           No DB. All mocked.
           Runs first, always.
           Fast. Should complete in seconds.

Phase 2 — Integration: Core CRUD            @integration, @isolated
           Graph integrity, tier hierarchy,
           entity CRUD tests.
           Fresh DB per test module.
           Proves the basic write/read cycle works
           before the fixture is loaded.

Phase 3 — Integration: Import               @integration, @isolated
           test_IE_import_database_succeeds_on_empty_db
           Loads the full Shadowdale fixture via
           import_database(). This is simultaneously:
             - a test of the import function itself
             - the DB seeding step for Phases 4 and 6
           If Phase 3 fails, Phases 4 and 6 are skipped.

Phase 4 — Integration: Read & Query         @integration, @requires_fixture
           Narrative flow, NPC profiles,
           timeline, knowledge queries,
           world knowledge, encounters,
           boxed text retrieval.
           All read from the seeded DB.
           No mutations permitted in these tests.

Phase 5 — Integration: Soft Delete          @integration, @isolated
           Disable, undelete, true_delete.
           Cascade behavior, shared node protection.
           Each test gets a fresh DB.
           These tests are intentionally isolated
           because they mutate and destroy data.

Phase 6 — Integration: Export & Round-trip  @integration, @requires_fixture, @slow
           Export the seeded DB.
           Verify node count, rel count, file content.
           Import the export into a fresh DB.
           Re-export and compare byte-for-byte.
           Depends on Phase 3 having run.
```

### pytest-order Configuration

```toml
[tool.pytest.ini_options]
# Run markers in this order
addopts = "--order-group-by=marker"
```

The marker ordering is defined in `conftest.py`:

```python
def pytest_collection_modifyitems(items, config):
    PHASE_ORDER = ["unit", "isolated", "integration", "requires_fixture", "slow"]
    # sort items by their first matching phase marker
    ...
```

---

## Neo4j Fixture Scopes

Three fixtures in `conftest.py`, each scoped differently:

```python
@pytest.fixture(scope="function")
def neo4j_fresh(request):
    """
    Spins up a fresh Neo4j container for a single test function.
    Used by: @isolated tests (soft delete, mutation tests).
    Torn down immediately after the test function completes.
    """

@pytest.fixture(scope="module")
def neo4j_module(request):
    """
    One Neo4j container shared across all tests in a module.
    Used by: Phase 2 CRUD integration tests.
    Torn down after the module completes.
    """

@pytest.fixture(scope="session")
def neo4j_seeded(request):
    """
    One Neo4j container for the full session.
    Phase 3 import test runs inside this fixture's scope,
    loading the Shadowdale fixture.
    All @requires_fixture tests use this same container.
    Torn down at the end of the full test session.
    """
```

All three fixtures yield a connected Neo4j driver, not the container
itself. Tests never interact with testcontainers directly.

---

## Fixture Organization

All fixture data lives in `test/fixtures/shadowdale.py` as **builder
functions that return raw dicts**. The raw dicts match the exact shape
of tool call arguments, so tests can pass them directly to tool functions
with no transformation.

### Structure

```python
# test/fixtures/shadowdale.py

# ── Global entities ──────────────────────────────────────

def make_elminster() -> dict: ...
def make_pipe_of_elminster() -> dict: ...
def make_shadowdale() -> dict: ...
def make_tower_of_ashaba() -> dict: ...
def make_river_ashaba() -> dict: ...

# ── Adventure ────────────────────────────────────────────

def make_adventure() -> dict: ...

# ── Context nodes ────────────────────────────────────────

def make_elminster_context() -> dict: ...

# ── Adventure-scoped NPCs ────────────────────────────────

def make_jhaele() -> dict: ...
def make_lettinster() -> dict: ...
def make_sister_maeris() -> dict: ...
def make_graveyard_skulker() -> dict: ...
def make_millpond_horror() -> dict: ...

# ── Locations ────────────────────────────────────────────

def make_northern_road_entry() -> dict: ...
def make_jhaele_farm() -> dict: ...
# ... all locations

# ── Narrative flow ───────────────────────────────────────

def make_plotline() -> dict: ...
def make_act1_events() -> list[dict]: ...
def make_act2a_events() -> list[dict]: ...
def make_act2b_events() -> list[dict]: ...
def make_act3_events() -> list[dict]: ...
def make_all_choices() -> list[dict]: ...
def make_all_outcomes() -> list[dict]: ...

# ── Encounters ───────────────────────────────────────────

def make_encounters() -> list[dict]: ...

# ── Boxed text ───────────────────────────────────────────

def make_boxed_text_sequences() -> list[dict]: ...

# ── Knowledge ────────────────────────────────────────────

def make_rumors() -> list[dict]: ...
def make_facts() -> list[dict]: ...

# ── Full fixture ─────────────────────────────────────────

def make_full_fixture() -> dict:
    """
    Assembles the complete Shadowdale adventure in the NDJSON
    envelope format expected by import_database().
    Calls all builders above and returns a single importable dict.
    Used by the Phase 3 import test and the round-trip export test.
    """
    ...
```

### Design Rules

- Builders return plain Python dicts. No custom classes, no ORM objects.
- Every builder is callable with no arguments and returns valid data.
- Builders may accept keyword overrides for targeted mutation in unit tests:
  `make_elminster(disabled=True)` returns an Elminster node with `disabled: True`.
- `make_full_fixture()` is the only function that calls other builders.
  All other builders are independent.

---

## Docker Test Environment

### `Dockerfile.test`

Installs the package with test extras and sets the entrypoint to pytest
with `--verbosity=3`. The full test run is the container's default command.

### `docker-compose.test.yml`

```
services:
  neo4j-test:
    image: neo4j:5
    environment:
      NEO4J_AUTH: neo4j/test-password
    healthcheck:
      test: cypher-shell RETURN 1
      interval: 5s
      retries: 10
    # No ports exposed externally
    # No named volume — data is ephemeral

  test-runner:
    build:
      dockerfile: Dockerfile.test
    environment:
      NEO4J_URI: bolt://neo4j-test:7687
      NEO4J_USER: neo4j
      NEO4J_PASSWORD: test-password
      NEO4J_DATABASE: neo4j
      ALLOW_TRUE_DELETE: "true"    ← enabled for SD tests
    depends_on:
      neo4j-test:
        condition: service_healthy
    command: pytest --verbosity=3
```

`docker compose -f docker-compose.test.yml up --abort-on-container-exit`
runs the tests and exits with the pytest exit code when the runner
finishes. Both containers are torn down automatically.

The `--abort-on-container-exit` flag is set in the compose file itself
so a plain `docker compose -f docker-compose.test.yml up` is sufficient.
