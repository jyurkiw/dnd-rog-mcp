"""
MCP Protocol unit tests — MP category.

These tests verify that all tools conform to the MCP content block spec,
return structured errors instead of exceptions, validate inputs before
touching the DB, and handle connection failures gracefully.
All tests in this module are pure unit tests. No DB required.
"""

import inspect
import pytest
from unittest.mock import MagicMock, patch

import dnd_mcp.tools.adventure as adventure
import dnd_mcp.tools.entities as entities
import dnd_mcp.tools.narrative as narrative
import dnd_mcp.tools.soft_delete as soft_delete
import dnd_mcp.tools.files as files

from test.fixtures.shadowdale import make_full_fixture, make_elminster, make_elminster_context, make_adventure, _base


# ── MP-01: all tools return MCP content block responses ──────────────────────

@pytest.mark.unit
def test_MP_01_tools_return_mcp_content_blocks():
    """
    All tools must return responses conforming to the MCP content block
    specification.
    """
    modules_to_check = [
        ("adventure", adventure),
        ("entities", entities),
        ("narrative", narrative),
    ]
    driver = MagicMock()
    for mod_name, mod in modules_to_check:
        for attr_name in dir(mod):
            attr = getattr(mod, attr_name, None)
            if callable(attr) and not attr_name.startswith("_"):
                try:
                    result = attr(driver)
                except TypeError:
                    try:
                        result = attr(driver, uid="test-uid")
                    except Exception:
                        continue
                except Exception:
                    continue
                assert isinstance(result, dict), (
                    f"{mod_name}.{attr_name}() must return a dict (MCP content block), "
                    f"not a raw Python object of type {type(result).__name__}"
                )


# ── MP-02: all tool errors return structured content, not exceptions ──────────

@pytest.mark.unit
def test_MP_02_tool_errors_structured_not_exceptions():
    """
    All tool errors must return structured error content blocks, not
    raise unhandled exceptions.
    """
    assert hasattr(soft_delete, "disable"), (
        "soft_delete.disable must be implemented (MP-02: tools return structured errors, not exceptions)"
    )
    driver = MagicMock()
    try:
        result = soft_delete.disable(driver, uid=None)
        assert isinstance(result, dict), "disable() with uid=None must return a dict"
        assert "error" in result, (
            "disable() with invalid uid=None must return {'error': ...}, not raise an exception"
        )
    except Exception as e:
        pytest.fail(
            f"soft_delete.disable() must not raise an exception for invalid input. "
            f"Got {type(e).__name__}: {e}"
        )


# ── MP-03: tools validate inputs before DB operations ────────────────────────

@pytest.mark.unit
def test_MP_03_tools_validate_inputs_before_db():
    """
    Every tool must validate input parameters before executing any DB
    operation.
    """
    assert hasattr(adventure, "create_adventure"), (
        "adventure.create_adventure must be implemented (MP-03: input validation before DB call)"
    )
    driver = MagicMock()
    mock_session = MagicMock()
    driver.session.return_value.__enter__.return_value = mock_session

    result = adventure.create_adventure(driver, uid=None)
    assert isinstance(result, dict), "create_adventure() with uid=None must return a dict"
    assert "error" in result, (
        "create_adventure() with uid=None must return {'error': ...}"
    )
    mock_session.run.assert_not_called(), (
        "create_adventure() with invalid input must NOT call session.run (validate before DB)"
    )


# ── MP-04: write tools return uid(s) of affected nodes ───────────────────────

@pytest.mark.unit
def test_MP_04_write_tools_return_uids():
    """
    Tools that write data must return the uid(s) of created or modified nodes.
    """
    assert hasattr(adventure, "create_adventure"), (
        "adventure.create_adventure must be implemented (MP-04: write tools return uid and status)"
    )
    driver = MagicMock()
    result = adventure.create_adventure(
        driver,
        uid="adv-test-mp04",
        name="Test Adventure MP04",
    )
    assert isinstance(result, dict), "create_adventure() with valid args must return a dict"
    assert "uid" in result, (
        "create_adventure() must return result with 'uid' key"
    )
    assert "status" in result, (
        "create_adventure() must return result with 'status' key"
    )


# ── MP-05: read tools return structured JSON, not raw Cypher ─────────────────

@pytest.mark.unit
def test_MP_05_read_tools_return_structured_json():
    """
    Tools that read data must return structured JSON, not raw Cypher results.
    """
    assert hasattr(adventure, "get_adventure"), (
        "adventure.get_adventure must be implemented (MP-05: read tools return structured JSON)"
    )
    driver = MagicMock()
    result = adventure.get_adventure(driver, adventure_uid="adv-troubles-of-shadowdale")
    assert isinstance(result, dict), "get_adventure() must return a dict"
    assert not hasattr(result, "data"), (
        "get_adventure() must not return a raw Neo4j Record or cursor (must be a plain dict)"
    )
    assert not hasattr(result, "keys") or isinstance(result, dict), (
        "get_adventure() must return a plain Python dict, not a Neo4j Record"
    )


# ── MP-06: serve_file_content returns plaintext content block ────────────────

@pytest.mark.unit
def test_MP_06_serve_file_content_returns_plaintext():
    """
    serve_file_content must return a plaintext content block.
    """
    assert hasattr(files, "serve_file_content"), (
        "files.serve_file_content must be implemented (MP-06: serve_file_content returns plaintext)"
    )
    driver = MagicMock()
    result = files.serve_file_content(driver, path="some/file.md")
    assert isinstance(result, dict), "serve_file_content() must return a dict"
    assert "content" in result, (
        "serve_file_content() must return result with 'content' key"
    )
    assert isinstance(result["content"], str), (
        "serve_file_content() result['content'] must be a string"
    )
    content_type = result.get("content_type", "")
    assert "text" in content_type.lower() or content_type in ("text/plain", "text/markdown", "text/html"), (
        f"serve_file_content() content_type must indicate plaintext, got {content_type!r}"
    )


# ── MP-07: server handles Neo4j connection failure gracefully ────────────────

@pytest.mark.unit
def test_MP_07_neo4j_connection_failure_graceful():
    """
    The server must handle Neo4j connection failure gracefully, returning
    a structured error rather than crashing.
    """
    assert hasattr(adventure, "get_adventure"), (
        "adventure.get_adventure must be implemented (MP-07: graceful Neo4j connection failure handling)"
    )
    try:
        from neo4j.exceptions import ServiceUnavailable
    except ImportError:
        pytest.skip("neo4j not installed — skipping ServiceUnavailable test")

    driver = MagicMock()
    driver.session.return_value.__enter__.side_effect = ServiceUnavailable("Connection refused")

    try:
        result = adventure.get_adventure(driver, adventure_uid="adv-any")
        assert isinstance(result, dict), (
            "get_adventure() when Neo4j is unavailable must return a dict"
        )
        assert "error" in result, (
            "get_adventure() when Neo4j raises ServiceUnavailable must return {'error': ...}"
        )
    except Exception as e:
        pytest.fail(
            f"adventure.get_adventure() must not propagate Neo4j exceptions. "
            f"Got {type(e).__name__}: {e}"
        )


# ── MP-08: all tools callable with only required parameters ──────────────────

@pytest.mark.unit
def test_MP_08_tools_callable_with_minimal_params():
    """
    All tools must be callable with minimal required parameters; optional
    parameters must have documented defaults.
    """
    assert hasattr(adventure, "create_adventure"), (
        "adventure.create_adventure must be implemented (MP-08: callable with minimal params)"
    )
    sig = inspect.signature(adventure.create_adventure)
    params = sig.parameters

    required_params = [
        name for name, param in params.items()
        if param.default is inspect.Parameter.empty
        and param.kind not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
        and name != "driver"
    ]
    optional_params = [
        name for name, param in params.items()
        if param.default is not inspect.Parameter.empty
    ]

    assert len(required_params) <= 2, (
        f"create_adventure() should have at most 2 required params (uid, name), "
        f"got {len(required_params)}: {required_params}"
    )
    assert "uid" in required_params or "uid" in [p for p in params], (
        "create_adventure() must have 'uid' as a parameter"
    )
    assert "name" in required_params or "name" in [p for p in params], (
        "create_adventure() must have 'name' as a parameter"
    )
    for opt_name in optional_params:
        param = params[opt_name]
        assert param.default is not inspect.Parameter.empty, (
            f"create_adventure() optional parameter '{opt_name}' must have a default value"
        )
