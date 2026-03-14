"""
Low Verbosity unit tests — LV category.

These tests verify that all tool responses are minimal, write operations
return only uids + status, errors return the prescribed shape, null/empty
fields are omitted, and documentation stays out of handlers.
All tests in this module are pure unit tests. No DB required.
"""

import ast
import os
import pytest
from unittest.mock import MagicMock

import dnd_mcp.tools.adventure as adventure
import dnd_mcp.tools.narrative as narrative
import dnd_mcp.tools.knowledge as knowledge

from test.fixtures.shadowdale import make_full_fixture, make_elminster, make_elminster_context, make_adventure, _base

# Markers that indicate long parameter doc sections in docstrings
_DOC_SECTION_MARKERS = ("Parameters:", "Args:", "Returns:", "---")


# ── LV-01: responses return minimum data ─────────────────────────────────────

@pytest.mark.unit
def test_LV_01_responses_return_minimum_data():
    """
    All tool responses must return the minimum data necessary to confirm
    success or explain failure.
    """
    assert hasattr(adventure, "create_adventure"), (
        "adventure.create_adventure must be implemented (LV-01: responses return minimum data)"
    )
    driver = MagicMock()
    result = adventure.create_adventure(
        driver,
        uid="adv-lv01-test",
        name="LV01 Test Adventure",
    )
    assert isinstance(result, dict), "create_adventure() must return a dict"
    assert len(result) <= 3, (
        f"create_adventure() success response must have ≤ 3 keys. "
        f"Got {len(result)} keys: {list(result.keys())}"
    )


# ── LV-02: write operations return only uids and status ──────────────────────

@pytest.mark.unit
def test_LV_02_write_operations_return_uid_and_status():
    """
    Write operations must return only affected uid(s) and a status field
    on success.
    """
    assert hasattr(adventure, "create_adventure"), (
        "adventure.create_adventure must be implemented (LV-02: write returns only uid and status)"
    )
    driver = MagicMock()
    result = adventure.create_adventure(
        driver,
        uid="adv-lv02-test",
        name="LV02 Test Adventure",
    )
    assert isinstance(result, dict), "create_adventure() must return a dict"
    assert "uid" in result, "create_adventure() must return result with 'uid'"
    assert "status" in result, "create_adventure() must return result with 'status'"
    assert isinstance(result["uid"], str), "create_adventure() result['uid'] must be a string"
    valid_statuses = ("created", "updated", "ok", "success")
    assert result["status"] in valid_statuses or isinstance(result["status"], str), (
        f"create_adventure() result['status'] must be a status string, got {result['status']!r}"
    )


# ── LV-03: read operations return structured JSON without prose ───────────────

@pytest.mark.unit
def test_LV_03_read_operations_structured_json_no_prose():
    """
    Read operations must return structured JSON with no prose decoration
    and no redundant nesting.
    """
    assert hasattr(adventure, "get_adventure"), (
        "adventure.get_adventure must be implemented (LV-03: read tools return structured JSON without prose)"
    )
    driver = MagicMock()
    result = adventure.get_adventure(driver, adventure_uid="adv-troubles-of-shadowdale")
    assert isinstance(result, dict), "get_adventure() must return a dict"

    prose_keys = {"message", "description", "info", "confirmation", "detail", "explanation"}
    for key in prose_keys:
        assert key not in result, (
            f"get_adventure() must not contain natural-language decoration key '{key}'"
        )


# ── LV-04: error responses use single error field ────────────────────────────

@pytest.mark.unit
def test_LV_04_error_responses_single_error_field():
    """
    Error responses must return a single error field containing a short
    machine-readable code and a one-sentence reason.
    """
    assert hasattr(adventure, "create_adventure"), (
        "adventure.create_adventure must be implemented (LV-04: error responses use single 'error' field)"
    )
    driver = MagicMock()
    result = adventure.create_adventure(driver, uid=None)
    assert isinstance(result, dict), "create_adventure() with uid=None must return a dict"
    assert "error" in result, "create_adventure() with missing uid must return {'error': ...}"
    assert len(result) == 1, (
        f"create_adventure() error response must have exactly 1 key ('error'). "
        f"Got {len(result)} keys: {list(result.keys())}"
    )


# ── LV-05: no confirmation narrative on success ──────────────────────────────

@pytest.mark.unit
def test_LV_05_no_confirmation_narrative_on_success():
    """
    No tool may return confirmation narrative or natural language decoration
    on success.
    """
    assert hasattr(adventure, "create_adventure"), (
        "adventure.create_adventure must be implemented (LV-05: no confirmation narrative on success)"
    )
    driver = MagicMock()
    result = adventure.create_adventure(
        driver,
        uid="adv-lv05-test",
        name="LV05 Test Adventure",
    )
    assert isinstance(result, dict), "create_adventure() must return a dict"

    forbidden_keys = {"message", "description", "info", "confirmation"}
    present = forbidden_keys & set(result.keys())
    assert not present, (
        f"create_adventure() success response must not contain prose keys: {present}"
    )
    assert "uid" in result, "create_adventure() must return result with 'uid'"
    assert "status" in result, "create_adventure() must return result with 'status'"


# ── LV-06: list operations return uid arrays by default ──────────────────────

@pytest.mark.unit
def test_LV_06_list_operations_return_uid_arrays():
    """
    List operations must return arrays of uids by default; a verbose
    parameter must be available for full properties.
    """
    assert hasattr(adventure, "list_adventures"), (
        "adventure.list_adventures must be implemented (LV-06: list returns uid array by default)"
    )
    driver = MagicMock()

    result_default = adventure.list_adventures(driver)
    assert isinstance(result_default, list), (
        "list_adventures() without verbose=True must return a list"
    )
    for item in result_default:
        assert isinstance(item, str), (
            f"list_adventures() default mode must return list of uid strings, got {type(item).__name__}"
        )

    result_verbose = adventure.list_adventures(driver, verbose=True)
    assert isinstance(result_verbose, list), (
        "list_adventures(verbose=True) must return a list"
    )
    for item in result_verbose:
        assert isinstance(item, dict), (
            f"list_adventures(verbose=True) must return list of dicts, got {type(item).__name__}"
        )


# ── LV-07: get_narrative_flow and get_npc_profile omit null and empty ─────────

@pytest.mark.unit
def test_LV_07_large_payload_tools_omit_null_and_empty():
    """
    get_narrative_flow and get_npc_profile are permitted larger payloads
    but must omit null fields and empty arrays.
    """
    assert hasattr(narrative, "get_narrative_flow"), (
        "narrative.get_narrative_flow must be implemented (LV-07: omit null and empty fields)"
    )
    assert hasattr(knowledge, "get_npc_profile"), (
        "knowledge.get_npc_profile must be implemented (LV-07: omit null and empty fields)"
    )
    driver = MagicMock()

    flow_result = narrative.get_narrative_flow(driver, plotline_uid="plotline-main-troubles")
    assert isinstance(flow_result, dict), "get_narrative_flow() must return a dict"
    for key, value in flow_result.items():
        assert value is not None, (
            f"get_narrative_flow() must not include null fields (found {key}=None)"
        )
        if isinstance(value, list):
            assert len(value) > 0, (
                f"get_narrative_flow() must not include empty arrays (found {key}=[])"
            )

    profile_result = knowledge.get_npc_profile(driver, npc_uid="global-npc-elminster")
    assert isinstance(profile_result, dict), "get_npc_profile() must return a dict"
    for key, value in profile_result.items():
        assert value is not None, (
            f"get_npc_profile() must not include null fields (found {key}=None)"
        )
        if isinstance(value, list):
            assert len(value) > 0, (
                f"get_npc_profile() must not include empty arrays (found {key}=[])"
            )


# ── LV-08: null fields and empty arrays omitted from all responses ────────────

@pytest.mark.unit
def test_LV_08_null_fields_and_empty_arrays_omitted():
    """
    Null fields and empty arrays must be omitted from all tool responses.
    """
    assert hasattr(adventure, "get_adventure"), (
        "adventure.get_adventure must be implemented (LV-08: null/empty fields omitted from responses)"
    )
    driver = MagicMock()
    result = adventure.get_adventure(driver, adventure_uid="adv-troubles-of-shadowdale")
    assert isinstance(result, dict), "get_adventure() must return a dict"
    for key, value in result.items():
        assert value is not None, (
            f"get_adventure() must not contain any key with value None (found '{key}': None)"
        )
        if isinstance(value, list):
            assert len(value) > 0, (
                f"get_adventure() must not contain any key with empty list value (found '{key}': [])"
            )


# ── LV-09: tool documentation lives in static reference document ─────────────

@pytest.mark.unit
def test_LV_09_tool_docs_in_reference_document_not_handlers():
    """
    Tool documentation must live in a static reference document, not
    inside any tool handler function.
    """
    tools_dir = os.path.join(
        os.path.dirname(__file__),
        "..", "..", "src", "dnd_mcp", "tools"
    )
    tools_dir = os.path.normpath(tools_dir)
    assert os.path.isdir(tools_dir), (
        f"Tools directory not found at {tools_dir}"
    )

    py_files = [
        os.path.join(tools_dir, f)
        for f in os.listdir(tools_dir)
        if f.endswith(".py") and not f.startswith("_")
    ]
    assert len(py_files) > 0, f"No .py files found in {tools_dir}"

    violations = []
    for filepath in py_files:
        with open(filepath, "r", encoding="utf-8") as fh:
            source = fh.read()
        try:
            tree = ast.parse(source, filename=filepath)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                docstring = ast.get_docstring(node)
                if docstring:
                    for marker in _DOC_SECTION_MARKERS:
                        if marker in docstring:
                            violations.append(
                                f"{os.path.basename(filepath)}:{node.name}() "
                                f"contains doc section marker {marker!r}"
                            )

    assert not violations, (
        "Tool function docstrings must not contain long parameter documentation blocks. "
        "Documentation belongs in a static reference file. Violations:\n"
        + "\n".join(violations)
    )


# ── LV-10: agent system prompt contains terse tool index ─────────────────────

@pytest.mark.unit
def test_LV_10_system_prompt_terse_tool_index():
    """
    The agent system prompt must contain a terse tool index sufficient
    for routine operation without requiring additional reference lookups.
    """
    project_root = os.path.normpath(
        os.path.join(os.path.dirname(__file__), "..", "..")
    )
    candidate_paths = [
        os.path.join(project_root, "SYSTEM_PROMPT.md"),
        os.path.join(project_root, "docs", "system_prompt.md"),
        os.path.join(project_root, "system_prompt.txt"),
        os.path.join(project_root, "docs", "SYSTEM_PROMPT.md"),
    ]
    found_path = None
    for path in candidate_paths:
        if os.path.isfile(path):
            found_path = path
            break

    assert found_path is not None, (
        f"No system prompt file found. Looked for: {candidate_paths}. "
        "Create SYSTEM_PROMPT.md or docs/system_prompt.md at the project root."
    )

    with open(found_path, "r", encoding="utf-8") as fh:
        content = fh.read()

    assert len(content.strip()) > 0, (
        f"System prompt file {found_path} is empty"
    )

    tool_modules = [
        "create_adventure", "get_adventure", "list_adventures",
        "upsert_npc", "get_entity",
        "add_event", "get_narrative_flow",
        "add_rumor", "add_fact",
        "add_boxed_text",
        "upsert_combat",
        "create_timeline",
        "disable", "undelete", "true_delete",
        "export_full_database", "import_database",
    ]
    found_tools = [tool for tool in tool_modules if tool in content]
    assert len(found_tools) >= 5, (
        f"System prompt at {found_path} must contain a terse tool index "
        f"with at least 5 tool names. Found only: {found_tools}"
    )
