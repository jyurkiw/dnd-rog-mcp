"""
Import / Export unit tests — IE category.

These tests verify the NDJSON export format, import pre-flight checks,
transactionality, schema version validation, adventure-scoped export,
round-trip fidelity, and list_files_in_export.
All tests in this module are pure unit tests. No DB required.
"""

import json
import pytest
from unittest.mock import MagicMock

import dnd_mcp.tools.import_export as import_export

from test.fixtures.shadowdale import make_full_fixture, make_elminster, make_elminster_context, make_adventure, _base


# ── IE-01: export serializes nodes, rels, and files to NDJSON ────────────────

@pytest.mark.unit
def test_IE_01_export_serializes_to_ndjson():
    """
    Export must serialize all nodes, relationships, and inlined file contents
    to NDJSON format.
    """
    assert hasattr(import_export, "export_full_database"), (
        "import_export.export_full_database must be implemented (IE-01: NDJSON export format)"
    )
    driver = MagicMock()
    result = import_export.export_full_database(driver)
    assert isinstance(result, str), "export_full_database() must return a string"

    lines = [line for line in result.strip().split("\n") if line.strip()]
    assert len(lines) >= 1, "export_full_database() must produce at least one NDJSON line"
    for i, line in enumerate(lines):
        try:
            obj = json.loads(line)
            assert isinstance(obj, dict), f"NDJSON line {i+1} must be a JSON object (dict), got {type(obj)}"
        except json.JSONDecodeError as e:
            pytest.fail(f"NDJSON line {i+1} is not valid JSON: {e}\nLine content: {line!r}")

    first_obj = json.loads(lines[0])
    assert "meta" in first_obj, (
        "First NDJSON line must be a metadata object with 'meta' key"
    )


# ── IE-02: exported node includes uid, label, tier, and all properties ────────

@pytest.mark.unit
def test_IE_02_exported_node_has_required_fields():
    """
    Every exported node must include uid, label, tier, and all properties.
    """
    assert hasattr(import_export, "export_full_database"), (
        "import_export.export_full_database must be implemented (IE-02: exported nodes have uid, label, tier, properties)"
    )
    driver = MagicMock()
    result = import_export.export_full_database(driver)
    assert isinstance(result, str), "export_full_database() must return a string"

    lines = [line for line in result.strip().split("\n") if line.strip()]
    node_lines = []
    for line in lines:
        try:
            obj = json.loads(line)
            if "meta" not in obj and "from_uid" not in obj and "file_path" not in obj:
                if "uid" in obj or "label" in obj:
                    node_lines.append(obj)
        except json.JSONDecodeError:
            pass

    for node in node_lines:
        required = {"uid", "label", "tier", "properties"}
        missing = required - set(node.keys())
        assert not missing, (
            f"Exported node {node.get('uid', '?')} is missing required keys: {missing}"
        )


# ── IE-03: exported relationship includes from_uid, to_uid, rel_type ──────────

@pytest.mark.unit
def test_IE_03_exported_relationship_has_required_fields():
    """
    Every exported relationship must include from_uid, to_uid, rel_type,
    and all relationship properties.
    """
    assert hasattr(import_export, "export_full_database"), (
        "import_export.export_full_database must be implemented (IE-03: exported relationships have required fields)"
    )
    driver = MagicMock()
    result = import_export.export_full_database(driver)
    assert isinstance(result, str), "export_full_database() must return a string"

    lines = [line for line in result.strip().split("\n") if line.strip()]
    rel_lines = []
    for line in lines:
        try:
            obj = json.loads(line)
            if "from_uid" in obj:
                rel_lines.append(obj)
        except json.JSONDecodeError:
            pass

    for rel in rel_lines:
        required = {"from_uid", "to_uid", "rel_type", "properties"}
        missing = required - set(rel.keys())
        assert not missing, (
            f"Exported relationship is missing required keys: {missing}. Got: {set(rel.keys())}"
        )


# ── IE-04: file content inlined as UTF-8 or base64 ───────────────────────────

@pytest.mark.unit
def test_IE_04_file_content_inline_encoding():
    """
    File content in export must be inlined as UTF-8 plaintext; binary files
    must be base64-encoded with the encoding flagged.
    """
    assert hasattr(import_export, "export_full_database"), (
        "import_export.export_full_database must be implemented (IE-04: file content encoding)"
    )
    driver = MagicMock()
    result = import_export.export_full_database(driver)
    assert isinstance(result, str), "export_full_database() must return a string"

    lines = [line for line in result.strip().split("\n") if line.strip()]
    file_lines = []
    for line in lines:
        try:
            obj = json.loads(line)
            if "content" in obj and "encoding" in obj:
                file_lines.append(obj)
        except json.JSONDecodeError:
            pass

    for file_entry in file_lines:
        assert "content" in file_entry, "File entry must have 'content' field"
        assert "encoding" in file_entry, "File entry must have 'encoding' field"
        assert file_entry["encoding"] in ("utf-8", "base64"), (
            f"File entry encoding must be 'utf-8' or 'base64', got {file_entry['encoding']!r}"
        )


# ── IE-05: import hard-fails on non-empty database ───────────────────────────

@pytest.mark.unit
def test_IE_05_import_fails_on_populated_db():
    """
    Import must perform a node count pre-flight check and hard-fail if the
    database is not empty.
    """
    assert hasattr(import_export, "import_database"), (
        "import_export.import_database must be implemented (IE-05: import fails on non-empty DB)"
    )
    driver = MagicMock()
    mock_session = MagicMock()
    mock_session.run.return_value = [{"count": 5}]
    driver.session.return_value.__enter__.return_value = mock_session

    fixture_ndjson = "\n".join([
        json.dumps({"meta": {"schema_version": 1, "exported_at": "2024-01-01T00:00:00Z"}}),
        json.dumps({"uid": "adv-1", "label": "Adventure", "tier": "adventure", "properties": {}}),
    ])
    result = import_export.import_database(driver, ndjson_content=fixture_ndjson)
    assert isinstance(result, dict), "import_database() on non-empty DB must return a dict"
    assert "error" in result, (
        "import_database() on non-empty DB must return {'error': ...}"
    )


# ── IE-06: import is transactional ───────────────────────────────────────────

@pytest.mark.unit
def test_IE_06_import_transactional():
    """
    Import must be transactional — all or nothing. Any error must trigger
    a full rollback.
    """
    assert hasattr(import_export, "import_database"), (
        "import_export.import_database must be implemented (IE-06: import is transactional)"
    )
    driver = MagicMock()
    malformed_ndjson = "\n".join([
        json.dumps({"meta": {"schema_version": 1, "exported_at": "2024-01-01T00:00:00Z"}}),
        json.dumps({"uid": "adv-good", "label": "Adventure", "tier": "adventure", "properties": {}}),
        "THIS IS NOT VALID JSON }{",
    ])
    result = import_export.import_database(driver, ndjson_content=malformed_ndjson)
    assert isinstance(result, dict), "import_database() with malformed JSON must return a dict"
    assert "error" in result, (
        "import_database() with malformed JSON line must return {'error': ...} and roll back"
    )


# ── IE-07: import validates schema version ───────────────────────────────────

@pytest.mark.unit
def test_IE_07_import_validates_schema_version():
    """
    Import must validate schema version compatibility before writing any data.
    """
    assert hasattr(import_export, "import_database"), (
        "import_export.import_database must be implemented (IE-07: import validates schema version)"
    )
    driver = MagicMock()
    future_schema_ndjson = "\n".join([
        json.dumps({"meta": {"schema_version": 99, "exported_at": "2024-01-01T00:00:00Z"}}),
        json.dumps({"uid": "adv-1", "label": "Adventure", "tier": "adventure", "properties": {}}),
    ])
    result = import_export.import_database(driver, ndjson_content=future_schema_ndjson)
    assert isinstance(result, dict), "import_database() with schema_version=99 must return a dict"
    assert "error" in result, (
        "import_database() with future schema_version=99 must return {'error': ...}"
    )
    error_text = str(result["error"])
    assert "schema" in error_text.lower() or "version" in error_text.lower(), (
        "import_database() schema version error must mention 'schema' or 'version'"
    )


# ── IE-08: export_adventure includes all required node types ─────────────────

@pytest.mark.unit
def test_IE_08_export_adventure_includes_all_node_types():
    """
    export_adventure must include: the Adventure node, all adventure-scoped
    nodes, all Context nodes, all referenced Global nodes (flagged read-only),
    and all FileRefs with inlined content.
    """
    assert hasattr(import_export, "export_adventure"), (
        "import_export.export_adventure must be implemented (IE-08: adventure export includes all node types)"
    )
    driver = MagicMock()
    result = import_export.export_adventure(
        driver,
        adventure_uid="adv-troubles-of-shadowdale",
    )
    assert isinstance(result, str), "export_adventure() must return a string"

    lines = [line for line in result.strip().split("\n") if line.strip()]
    assert len(lines) >= 1, "export_adventure() must produce at least one NDJSON line"

    all_objects = []
    for line in lines:
        try:
            obj = json.loads(line)
            all_objects.append(obj)
        except json.JSONDecodeError as e:
            pytest.fail(f"export_adventure() produced invalid JSON line: {e}")

    has_adventure = any(
        obj.get("label") == "Adventure" or obj.get("uid") == "adv-troubles-of-shadowdale"
        for obj in all_objects
    )
    assert has_adventure, (
        "export_adventure() must include the Adventure node itself"
    )

    global_nodes = [obj for obj in all_objects if obj.get("tier") == "global" or obj.get("read_only") is True]
    if global_nodes:
        for gn in global_nodes:
            assert gn.get("read_only") is True or gn.get("properties", {}).get("read_only") is True, (
                f"Global node {gn.get('uid')} in export_adventure() must be flagged read_only=True"
            )


# ── IE-09: full import → export round-trip is byte-equivalent ────────────────

@pytest.mark.unit
def test_IE_09_full_roundtrip_fidelity():
    """
    A full import followed by a full export must produce byte-equivalent
    output to the original export file.
    """
    assert hasattr(import_export, "export_full_database"), (
        "import_export.export_full_database must be implemented (IE-09: round-trip fidelity)"
    )
    assert hasattr(import_export, "import_database"), (
        "import_export.import_database must be implemented (IE-09: round-trip fidelity)"
    )
    driver = MagicMock()
    export1 = import_export.export_full_database(driver)
    assert isinstance(export1, str), "export_full_database() must return a string"

    result = import_export.import_database(driver, ndjson_content=export1)
    assert isinstance(result, dict), "import_database() must return a dict"

    export2 = import_export.export_full_database(driver)
    assert isinstance(export2, str), "Second export_full_database() must return a string"

    assert export1 == export2, (
        "export → import → export round-trip must produce byte-equivalent output"
    )


# ── IE-10: list_files_in_export works on raw NDJSON without importing ─────────

@pytest.mark.unit
def test_IE_10_list_files_in_export_no_import_required():
    """
    list_files_in_export must work without importing, operating directly
    on the raw NDJSON content.
    """
    assert hasattr(import_export, "list_files_in_export"), (
        "import_export.list_files_in_export must be implemented (IE-10: list files without importing)"
    )
    sample_ndjson = "\n".join([
        json.dumps({"meta": {"schema_version": 1, "exported_at": "2024-01-01T00:00:00Z"}}),
        json.dumps({"uid": "file-01", "label": "FileRef", "tier": "adventure",
                    "properties": {"path": "prose/arrival.md"}, "content": "...", "encoding": "utf-8"}),
        json.dumps({"uid": "file-02", "label": "FileRef", "tier": "adventure",
                    "properties": {"path": "prose/confrontation.md"}, "content": "...", "encoding": "utf-8"}),
    ])
    result = import_export.list_files_in_export(ndjson_content=sample_ndjson)
    assert isinstance(result, list), "list_files_in_export() must return a list"
    assert len(result) >= 2, (
        "list_files_in_export() must find both file paths in the NDJSON content"
    )
    assert "prose/arrival.md" in result or any("arrival" in str(f) for f in result), (
        "list_files_in_export() must include 'prose/arrival.md' in results"
    )
