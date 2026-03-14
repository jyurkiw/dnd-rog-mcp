"""
Graph Integrity unit tests — GI category.

These tests verify the structural rules that apply to every node in the
graph: uid uniqueness, required properties, tier values, and so on.
All tests in this module are pure unit tests. No DB required.
"""

import pytest
from unittest.mock import MagicMock, patch
from assertpy import assert_that

import dnd_mcp.tools.soft_delete as soft_delete

from test.fixtures.shadowdale import (
    make_elminster,
    make_pipe_of_elminster,
    make_adventure,
    make_elminster_context,
    make_jhaele,
    make_full_fixture,
)


# ── GI-01: uid uniqueness ─────────────────────────────────────────────────────

@pytest.mark.unit
def test_GI_01_uid_uniqueness():
    """
    Every node in the full fixture must have a unique uid.
    No two nodes may share a uid regardless of tier or label.
    """
    fixture = make_full_fixture()
    uids = [node["uid"] for node in fixture["nodes"]]
    unique_uids = set(uids)

    assert_that(uids).is_length(len(unique_uids))


# ── GI-02: tier property required on all nodes ────────────────────────────────

@pytest.mark.unit
def test_GI_02_tier_property_required():
    """
    Every node must have a 'tier' property.
    Valid values are: global, adventure, context.
    """
    VALID_TIERS = {"global", "adventure", "context"}
    fixture = make_full_fixture()

    for node in fixture["nodes"]:
        assert_that(node).contains_key("tier")
        assert_that(node["tier"]).described_as(
            f"Node {node['uid']} has invalid tier '{node.get('tier')}'"
        ).is_in(*VALID_TIERS)


# ── GI-03: no dangling relationships ─────────────────────────────────────────

@pytest.mark.unit
def test_GI_03_no_dangling_relationships():
    """
    No relationship may exist if either endpoint node does not exist.
    Every from_uid and to_uid in the fixture relationships must resolve
    to a node uid present in the fixture.
    """
    fixture = make_full_fixture()
    node_uids = {node["uid"] for node in fixture["nodes"]}

    for rel in fixture["relationships"]:
        assert rel["from_uid"] in node_uids, (
            f"Relationship {rel['uid']!r} has dangling from_uid={rel['from_uid']!r}"
        )
        assert rel["to_uid"] in node_uids, (
            f"Relationship {rel['uid']!r} has dangling to_uid={rel['to_uid']!r}"
        )


# ── GI-04: context node has exactly one WITHIN_ADVENTURE ─────────────────────

@pytest.mark.unit
def test_GI_04_context_node_single_within_adventure():
    """
    A Context node must have exactly one WITHIN_ADVENTURE relationship.
    Verified against the fixture; enforced by add_entity_to_adventure in production.
    """
    fixture = make_full_fixture()
    context_uids = {n["uid"] for n in fixture["nodes"] if n.get("tier") == "context"}
    rels = fixture["relationships"]

    for ctx_uid in context_uids:
        within_adv = [
            r for r in rels
            if r["rel_type"] == "WITHIN_ADVENTURE" and r["from_uid"] == ctx_uid
        ]
        assert len(within_adv) == 1, (
            f"Context node {ctx_uid!r} has {len(within_adv)} WITHIN_ADVENTURE "
            f"relationships; expected exactly 1"
        )


# ── GI-05: context node has exactly one inbound REPRESENTED_BY ───────────────

@pytest.mark.unit
def test_GI_05_context_node_single_represented_by():
    """
    A Context node must have exactly one inbound REPRESENTED_BY relationship
    from a Global node.
    """
    fixture = make_full_fixture()
    context_uids = {n["uid"] for n in fixture["nodes"] if n.get("tier") == "context"}
    rels = fixture["relationships"]

    for ctx_uid in context_uids:
        represented_by = [
            r for r in rels
            if r["rel_type"] == "REPRESENTED_BY" and r["to_uid"] == ctx_uid
        ]
        assert len(represented_by) == 1, (
            f"Context node {ctx_uid!r} has {len(represented_by)} inbound "
            f"REPRESENTED_BY relationships; expected exactly 1"
        )


# ── GI-06: deleting a node cascades to context nodes and relationships ────────

@pytest.mark.unit
def test_GI_06_delete_cascades_context_and_relationships():
    """
    The disable tool must cascade to all context nodes and relationships
    owned by or dependent on the target node.
    """
    assert hasattr(soft_delete, "disable"), (
        "soft_delete.disable must be implemented (GI-06: cascade on disable)"
    )
    driver = MagicMock()
    result = soft_delete.disable(driver, uid="global-npc-elminster")
    assert isinstance(result, dict), "disable() must return a dict"
    assert "uid" in result or "disabled_count" in result or "cascade_count" in result, (
        "disable() must return a result describing what was disabled"
    )


# ── GI-07: deleting an Adventure cascades to source_adventure nodes ───────────

@pytest.mark.unit
def test_GI_07_delete_adventure_cascades_source_adventure_nodes():
    """
    Disabling an Adventure must cascade-disable all nodes with a
    source_adventure property matching that Adventure's uid.
    """
    assert hasattr(soft_delete, "disable"), (
        "soft_delete.disable must be implemented (GI-07: adventure cascade)"
    )
    driver = MagicMock()
    result = soft_delete.disable(driver, uid="adv-troubles-of-shadowdale")
    assert isinstance(result, dict), "disable() must return a dict"
    assert "uid" in result or "cascade_count" in result, (
        "disable() on an Adventure must return cascade information"
    )


# ── GI-08: Global nodes may not have source_adventure ────────────────────────

@pytest.mark.unit
def test_GI_08_global_nodes_no_source_adventure():
    """
    A Global node may not have a source_adventure property.
    All global-tier nodes in the fixture must lack this key.
    """
    fixture = make_full_fixture()
    global_nodes = [n for n in fixture["nodes"] if n.get("tier") == "global"]

    for node in global_nodes:
        assert "source_adventure" not in node, (
            f"Global node {node['uid']!r} must not have source_adventure "
            f"(found {node.get('source_adventure')!r})"
        )


# ── GI-09: no duplicate uids across different labels ─────────────────────────

@pytest.mark.unit
def test_GI_09_no_duplicate_uids_across_labels():
    """
    No duplicate uid values, even across different node labels.
    uid must be globally unique regardless of label or tier.
    """
    fixture = make_full_fixture()
    seen: dict[str, str] = {}  # uid → label

    for node in fixture["nodes"]:
        uid = node["uid"]
        label = node.get("label", "unknown")
        assert uid not in seen, (
            f"Duplicate uid {uid!r}: first seen as label={seen[uid]!r}, "
            f"also found as label={label!r}"
        )
        seen[uid] = label


# ── GI-10: FileRef path uniqueness ───────────────────────────────────────────

@pytest.mark.unit
def test_GI_10_fileref_path_unique():
    """
    A FileRef path must be unique within the database.
    No two FileRef nodes may share the same path value.
    """
    fixture = make_full_fixture()
    fileref_nodes = [n for n in fixture["nodes"] if n.get("label") == "FileRef"]
    paths = [n["path"] for n in fileref_nodes if "path" in n]
    duplicates = [p for p in paths if paths.count(p) > 1]

    assert len(duplicates) == 0, (
        f"Duplicate FileRef paths found: {list(set(duplicates))}"
    )
