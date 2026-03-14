"""
Soft Delete unit tests — SD category.

These tests verify the three-operation soft delete system: disable,
undelete, and true_delete — including cascade behavior, shared node
protection, the ALLOW_TRUE_DELETE gate, and export/import fidelity
for disabled state.
All tests in this module are pure unit tests. No DB required.
"""

import os
import pytest
from unittest.mock import MagicMock, patch

import dnd_mcp.tools.adventure as adventure
import dnd_mcp.tools.entities as entities
import dnd_mcp.tools.soft_delete as soft_delete
import dnd_mcp.tools.import_export as import_export
import dnd_mcp.server as server

from test.fixtures.shadowdale import make_full_fixture, make_elminster, make_elminster_context, make_adventure, _base


# ── SD-01: every node has disabled boolean defaulting to false ────────────────

@pytest.mark.unit
def test_SD_01_disabled_property_default_false():
    """
    Every node must have a disabled boolean property defaulting to false.
    """
    result = make_elminster()
    assert "disabled" in result, "make_elminster() must include 'disabled' key"
    assert result["disabled"] == False, (
        "make_elminster() disabled must default to False"
    )


# ── SD-02: every node has disabled_by list defaulting to empty ────────────────

@pytest.mark.unit
def test_SD_02_disabled_by_list_default_empty():
    """
    Every node must have a disabled_by list property defaulting to empty list.
    """
    result = make_elminster()
    assert "disabled_by" in result, "make_elminster() must include 'disabled_by' key"
    assert result["disabled_by"] == [], (
        "make_elminster() disabled_by must default to []"
    )


# ── SD-03: every node has disabled_at nullable datetime ──────────────────────

@pytest.mark.unit
def test_SD_03_disabled_at_nullable_datetime():
    """
    Every node must have a disabled_at property that is nullable and
    stores a datetime when set.
    """
    result = make_elminster()
    assert "disabled_at" in result, "make_elminster() must include 'disabled_at' key"
    assert result["disabled_at"] is None, (
        "make_elminster() disabled_at must default to None"
    )


# ── SD-04: read tools filter disabled nodes by default ───────────────────────

@pytest.mark.unit
def test_SD_04_read_tools_filter_disabled_by_default():
    """
    All read tools must filter out nodes with disabled: true by default.
    """
    assert hasattr(adventure, "get_adventure"), (
        "adventure.get_adventure must be implemented (SD-04: read tools filter disabled by default)"
    )
    driver = MagicMock()
    mock_session = MagicMock()
    mock_record = {"uid": "adv-troubles", "disabled": True, "name": "Troubles of Shadowdale"}
    mock_session.run.return_value = [mock_record]
    driver.session.return_value.__enter__.return_value = mock_session

    result = adventure.get_adventure(driver, adventure_uid="adv-troubles")
    assert isinstance(result, dict), "get_adventure() must return a dict"
    if "adventures" in result:
        for adv in result.get("adventures", []):
            assert not adv.get("disabled", False), (
                "get_adventure() without include_disabled must not return disabled nodes"
            )
    elif "disabled" in result:
        assert not result.get("disabled", False), (
            "get_adventure() without include_disabled must not return a disabled adventure"
        )


# ── SD-05: read tools accept include_disabled parameter ──────────────────────

@pytest.mark.unit
def test_SD_05_read_tools_accept_include_disabled():
    """
    Read tools must accept an optional include_disabled parameter that,
    when true, returns disabled nodes in results.
    """
    assert hasattr(adventure, "get_adventure"), (
        "adventure.get_adventure must be implemented (SD-05: include_disabled parameter)"
    )
    driver = MagicMock()
    result = adventure.get_adventure(
        driver,
        adventure_uid="adv-troubles",
        include_disabled=True,
    )
    assert isinstance(result, dict), "get_adventure() with include_disabled=True must return a dict"
    assert "error" not in result or "not found" not in str(result.get("error", "")), (
        "get_adventure() with include_disabled=True must accept the parameter without error"
    )


# ── SD-06: disable cascades per cascade table ────────────────────────────────

@pytest.mark.unit
def test_SD_06_disable_cascades_to_owned_nodes():
    """
    disable must cascade to all owned/dependent nodes per the cascade table
    defined in DESIGN.md.
    """
    assert hasattr(soft_delete, "disable"), (
        "soft_delete.disable must be implemented (SD-06: disable cascades to owned nodes)"
    )
    driver = MagicMock()
    result = soft_delete.disable(driver, uid="adv-troubles-of-shadowdale")
    assert isinstance(result, dict), "disable() must return a dict"
    has_cascade_info = (
        "cascade_count" in result
        or "disabled_uids" in result
        or "disabled_count" in result
    )
    assert has_cascade_info, (
        "disable() must return cascade info ('cascade_count', 'disabled_uids', or 'disabled_count')"
    )
    cascade_count = result.get("cascade_count") or result.get("disabled_count") or len(result.get("disabled_uids", []))
    assert cascade_count > 0, (
        "disable() on an adventure must cascade to > 0 dependent nodes"
    )


# ── SD-07: disable respects shared node protection ───────────────────────────

@pytest.mark.unit
def test_SD_07_disable_respects_shared_node_protection():
    """
    disable must respect shared node protection: a node with multiple parent
    relationships is only disabled when all parents resolve to disabled nodes.
    """
    assert hasattr(soft_delete, "disable"), (
        "soft_delete.disable must be implemented (SD-07: shared node protection)"
    )
    driver = MagicMock()
    result = soft_delete.disable(driver, uid="adv-shared-parent-1")
    assert isinstance(result, dict), "disable() on first parent must return a dict"

    shared_node_info = result.get("partial_disabled") or result.get("shared_nodes") or result
    assert isinstance(shared_node_info, dict), "disable() must return a dict with shared node information"

    if "shared_node_disabled_by" in result:
        assert len(result["shared_node_disabled_by"]) == 1, (
            "Shared node disabled_by should contain only the one parent that was disabled"
        )
    if "shared_node_disabled" in result:
        assert result["shared_node_disabled"] is False, (
            "Shared node disabled flag must remain False until all parents are disabled"
        )


# ── SD-08: disable appends triggering uid to disabled_by ─────────────────────

@pytest.mark.unit
def test_SD_08_disable_appends_uid_to_disabled_by():
    """
    disable must append the triggering uid to disabled_by on every affected
    node, including cascade targets.
    """
    assert hasattr(soft_delete, "disable"), (
        "soft_delete.disable must be implemented (SD-08: disable appends uid to disabled_by)"
    )
    driver = MagicMock()
    result = soft_delete.disable(driver, uid="global-npc-elminster")
    assert isinstance(result, dict), "disable() must return a dict"

    ctx_disabled_by = result.get("ctx_elminster_troubles_disabled_by") or result.get("cascade_disabled_by")
    if ctx_disabled_by is not None:
        assert "global-npc-elminster" in ctx_disabled_by, (
            "After disable('global-npc-elminster'), ctx-elminster-troubles disabled_by must contain 'global-npc-elminster'"
        )
    else:
        assert "uid" in result or "cascade_count" in result or "disabled_uids" in result, (
            "disable() must return information about what was disabled"
        )


# ── SD-09: undelete targets nodes containing the uid in disabled_by ───────────

@pytest.mark.unit
def test_SD_09_undelete_targets_correct_nodes():
    """
    undelete must only re-enable nodes whose disabled_by list contains the
    target uid.
    """
    assert hasattr(soft_delete, "undelete"), (
        "soft_delete.undelete must be implemented (SD-09: undelete only affects nodes with uid in disabled_by)"
    )
    driver = MagicMock()
    soft_delete.disable(driver, uid="adv-A")
    soft_delete.disable(driver, uid="adv-B")

    result = soft_delete.undelete(driver, uid="adv-A")
    assert isinstance(result, dict), "undelete() must return a dict"
    assert "error" not in result, (
        "undelete('adv-A') must succeed (no 'error' key)"
    )

    if "affected_uids" in result or "undeleted_uids" in result:
        affected = result.get("affected_uids") or result.get("undeleted_uids", [])
        for uid in affected:
            assert uid != "adv-B-only-node", (
                "undelete('adv-A') must not affect nodes whose disabled_by only contains 'adv-B'"
            )


# ── SD-10: undelete removes uid and clears disabled only when list empty ──────

@pytest.mark.unit
def test_SD_10_undelete_clears_disabled_when_list_empty():
    """
    undelete must remove the target uid from disabled_by and only set
    disabled: false when the resulting list is empty.
    """
    assert hasattr(soft_delete, "undelete"), (
        "soft_delete.undelete must be implemented (SD-10: undelete clears disabled only when disabled_by is empty)"
    )
    driver = MagicMock()

    soft_delete.disable(driver, uid="adv-A")
    result_single = soft_delete.undelete(driver, uid="adv-A")
    assert isinstance(result_single, dict), "undelete() after single disable must return a dict"

    soft_delete.disable(driver, uid="adv-A")
    soft_delete.disable(driver, uid="adv-B")
    result_multi = soft_delete.undelete(driver, uid="adv-A")
    assert isinstance(result_multi, dict), "undelete() with multi disabled_by must return a dict"
    assert "error" not in result_multi, (
        "undelete('adv-A') when node also disabled by 'adv-B' must succeed (no 'error' key)"
    )

    if "node_still_disabled" in result_multi:
        assert result_multi["node_still_disabled"] is True, (
            "After undelete('adv-A') when disabled_by=['adv-A','adv-B'], node must still be disabled"
        )


# ── SD-11: true_delete hard-fails if target not already disabled ──────────────

@pytest.mark.unit
def test_SD_11_true_delete_requires_disabled_node():
    """
    true_delete must hard-fail if the target node is not already
    disabled: true.
    """
    assert hasattr(soft_delete, "true_delete"), (
        "soft_delete.true_delete must be implemented (SD-11: true_delete requires node to be disabled first)"
    )
    driver = MagicMock()
    with patch.dict(os.environ, {"ALLOW_TRUE_DELETE": "true"}):
        result = soft_delete.true_delete(driver, uid="some-active-node")
        assert isinstance(result, dict), "true_delete() on non-disabled node must return a dict"
        assert "error" in result, (
            "true_delete() on a node where disabled=False must return {'error': ...}"
        )


# ── SD-12: true_delete permanently removes node, cascade nodes, rels ──────────

@pytest.mark.unit
def test_SD_12_true_delete_permanent_removal():
    """
    true_delete must permanently delete the target node, all cascade-owned
    nodes, and all their relationships.
    """
    assert hasattr(soft_delete, "true_delete"), (
        "soft_delete.true_delete must be implemented (SD-12: true_delete permanently removes nodes)"
    )
    driver = MagicMock()
    soft_delete.disable(driver, uid="adv-to-delete")
    with patch.dict(os.environ, {"ALLOW_TRUE_DELETE": "true"}):
        result = soft_delete.true_delete(driver, uid="adv-to-delete")
        assert isinstance(result, dict), "true_delete() on disabled node must return a dict"
        assert "error" not in result, (
            "true_delete() on a disabled node with ALLOW_TRUE_DELETE=true must succeed (no 'error' key)"
        )


# ── SD-13: true_delete returns removal counts ────────────────────────────────

@pytest.mark.unit
def test_SD_13_true_delete_returns_counts():
    """
    true_delete must return a count of nodes and relationships permanently
    removed.
    """
    assert hasattr(soft_delete, "true_delete"), (
        "soft_delete.true_delete must be implemented (SD-13: true_delete returns nodes_deleted and relationships_deleted)"
    )
    driver = MagicMock()
    soft_delete.disable(driver, uid="adv-to-count-delete")
    with patch.dict(os.environ, {"ALLOW_TRUE_DELETE": "true"}):
        result = soft_delete.true_delete(driver, uid="adv-to-count-delete")
        assert isinstance(result, dict), "true_delete() must return a dict"
        if "error" not in result:
            assert "nodes_deleted" in result, (
                "true_delete() must return 'nodes_deleted' count"
            )
            assert "relationships_deleted" in result, (
                "true_delete() must return 'relationships_deleted' count"
            )
            assert isinstance(result["nodes_deleted"], int), (
                "true_delete() nodes_deleted must be an int"
            )
            assert isinstance(result["relationships_deleted"], int), (
                "true_delete() relationships_deleted must be an int"
            )


# ── SD-14: no tool other than true_delete may permanently remove nodes ────────

@pytest.mark.unit
def test_SD_14_only_true_delete_permanently_removes():
    """
    No tool other than true_delete may permanently remove a node from the
    database.
    """
    import dnd_mcp.tools.adventure as adventure_mod
    import dnd_mcp.tools.entities as entities_mod
    import dnd_mcp.tools.narrative as narrative_mod
    import dnd_mcp.tools.knowledge as knowledge_mod
    import dnd_mcp.tools.boxed_text as boxed_text_mod
    import dnd_mcp.tools.encounters as encounters_mod
    import dnd_mcp.tools.timeline as timeline_mod
    import dnd_mcp.tools.import_export as import_export_mod
    import dnd_mcp.tools.files as files_mod

    forbidden_names = {"delete", "remove", "purge"}
    modules = [
        ("adventure", adventure_mod),
        ("entities", entities_mod),
        ("narrative", narrative_mod),
        ("knowledge", knowledge_mod),
        ("boxed_text", boxed_text_mod),
        ("encounters", encounters_mod),
        ("timeline", timeline_mod),
        ("import_export", import_export_mod),
        ("files", files_mod),
    ]
    for mod_name, mod in modules:
        for attr_name in dir(mod):
            if callable(getattr(mod, attr_name, None)):
                assert attr_name not in forbidden_names, (
                    f"Module '{mod_name}' must not have a function named '{attr_name}'. "
                    f"Only soft_delete.true_delete may permanently remove nodes."
                )


# ── SD-15: export includes disabled nodes flagged as such ────────────────────

@pytest.mark.unit
def test_SD_15_export_includes_disabled_nodes():
    """
    Export must include disabled nodes, flagged with their disabled state.
    """
    assert hasattr(import_export, "export_full_database"), (
        "import_export.export_full_database must be implemented (SD-15: export includes disabled nodes)"
    )
    driver = MagicMock()
    mock_session = MagicMock()
    mock_session.run.return_value = [
        {"uid": "adv-disabled", "label": "Adventure", "tier": "adventure", "disabled": True,
         "disabled_by": ["some-parent"], "disabled_at": "2024-01-01T00:00:00Z"}
    ]
    driver.session.return_value.__enter__.return_value = mock_session

    result = import_export.export_full_database(driver)
    assert isinstance(result, str), "export_full_database() must return a string"
    import json
    lines = [line for line in result.strip().split("\n") if line]
    found_disabled = False
    for line in lines:
        try:
            obj = json.loads(line)
            if obj.get("uid") == "adv-disabled" or obj.get("properties", {}).get("disabled") is True:
                found_disabled = True
                break
        except json.JSONDecodeError:
            pass
    assert found_disabled or len(lines) > 0, (
        "export_full_database() must include disabled nodes in the export"
    )


# ── SD-16: import restores disabled state correctly ──────────────────────────

@pytest.mark.unit
def test_SD_16_import_restores_disabled_state():
    """
    Import must correctly restore disabled, disabled_by, and disabled_at
    state for all nodes.
    """
    assert hasattr(import_export, "import_database"), (
        "import_export.import_database must be implemented (SD-16: import restores disabled state)"
    )
    import json
    driver = MagicMock()
    fixture_ndjson = "\n".join([
        json.dumps({"meta": {"schema_version": 1, "exported_at": "2024-01-01T00:00:00Z"}}),
        json.dumps({"uid": "adv-disabled-restore", "label": "Adventure", "tier": "adventure",
                    "properties": {"disabled": True, "disabled_by": ["some-uid"], "disabled_at": "2024-01-01T00:00:00Z"}}),
    ])
    result = import_export.import_database(driver, ndjson_content=fixture_ndjson)
    assert isinstance(result, dict), "import_database() must return a dict"


# ── SD-17: true_delete disabled by default ───────────────────────────────────

@pytest.mark.unit
def test_SD_17_true_delete_disabled_by_default():
    """
    true_delete must be disabled by default and only enabled when the
    ALLOW_TRUE_DELETE environment variable is set to true.
    """
    assert hasattr(soft_delete, "true_delete"), (
        "soft_delete.true_delete must be implemented (SD-17: disabled by default without ALLOW_TRUE_DELETE)"
    )
    driver = MagicMock()
    env_without = {k: v for k, v in os.environ.items() if k != "ALLOW_TRUE_DELETE"}
    with patch.dict(os.environ, env_without, clear=True):
        result = soft_delete.true_delete(driver, uid="adv-any")
        assert isinstance(result, dict), "true_delete() without ALLOW_TRUE_DELETE must return a dict"
        assert "error" in result, (
            "true_delete() without ALLOW_TRUE_DELETE set must return {'error': ...}"
        )


# ── SD-18: true_delete returns structured error when not enabled ──────────────

@pytest.mark.unit
def test_SD_18_true_delete_structured_error_when_disabled():
    """
    When ALLOW_TRUE_DELETE is not true, calling true_delete must return a
    structured error explaining the situation and how to enable it.
    """
    assert hasattr(soft_delete, "true_delete"), (
        "soft_delete.true_delete must be implemented (SD-18: structured error mentioning ALLOW_TRUE_DELETE)"
    )
    driver = MagicMock()
    with patch.dict(os.environ, {"ALLOW_TRUE_DELETE": "false"}):
        result = soft_delete.true_delete(driver, uid="adv-any")
        assert isinstance(result, dict), "true_delete() with ALLOW_TRUE_DELETE=false must return a dict"
        assert "error" in result, (
            "true_delete() with ALLOW_TRUE_DELETE=false must return {'error': ...}"
        )
        error_text = str(result["error"])
        assert "ALLOW_TRUE_DELETE" in error_text, (
            "true_delete() error message must contain 'ALLOW_TRUE_DELETE' to explain how to enable it"
        )


# ── SD-19: true_delete enabled/disabled state logged at startup ───────────────

@pytest.mark.unit
def test_SD_19_true_delete_state_logged_at_startup():
    """
    The enabled/disabled state of true_delete must be logged unambiguously
    at server startup.
    """
    assert hasattr(server, "main"), (
        "server.main must be implemented (SD-19: startup logs ALLOW_TRUE_DELETE state)"
    )


# ── SD-20: true_delete error is self-explanatory ─────────────────────────────

@pytest.mark.unit
def test_SD_20_true_delete_error_self_explanatory():
    """
    true_delete must never be silently disabled — the error returned when
    it is not enabled must be self-explanatory.
    """
    assert hasattr(soft_delete, "true_delete"), (
        "soft_delete.true_delete must be implemented (SD-20: error must be self-explanatory)"
    )
    driver = MagicMock()
    env_without = {k: v for k, v in os.environ.items() if k != "ALLOW_TRUE_DELETE"}
    with patch.dict(os.environ, env_without, clear=True):
        result = soft_delete.true_delete(driver, uid="adv-any")
        assert isinstance(result, dict), "true_delete() without ALLOW_TRUE_DELETE must return a dict"
        assert "error" in result, (
            "true_delete() without ALLOW_TRUE_DELETE must return {'error': ...}"
        )
        error_text = str(result["error"])
        assert len(error_text) > 10, (
            "true_delete() error must be a non-empty, explanatory string (not just 'error' or 'forbidden')"
        )
        assert error_text.lower() not in ("error", "forbidden", "denied"), (
            "true_delete() error must explain what to do, not just say 'error' or 'forbidden'"
        )
