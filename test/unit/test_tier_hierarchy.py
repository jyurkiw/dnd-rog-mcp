"""
Tier & Hierarchy unit tests — TH category.

These tests verify the three-tier (global / adventure / context) ownership
model: promotion, scoping rules, and the constraint that Global identity
is never mutated by adventure-scoped tools.
All tests in this module are pure unit tests. No DB required.
"""

import pytest
from unittest.mock import MagicMock

import dnd_mcp.tools.entities as entities

from test.fixtures.shadowdale import make_full_fixture, make_elminster, make_elminster_context, make_adventure, _base


# ── TH-01: Global entity may exist with no Adventure link ────────────────────

@pytest.mark.unit
def test_TH_01_global_entity_exists_without_adventure():
    """
    A Global entity may exist with no relationship to any Adventure.
    """
    assert hasattr(entities, "create_global_npc"), (
        "create_global_npc must be implemented (TH-01: global entity with no adventure link)"
    )
    driver = MagicMock()
    result = entities.create_global_npc(
        driver,
        uid="global-npc-test",
        canonical_name="Test NPC",
        summary="A test",
    )
    assert isinstance(result, dict), "create_global_npc() must return a dict"
    assert "uid" in result, "create_global_npc() result must contain 'uid'"
    assert result["uid"] == "global-npc-test", (
        "create_global_npc() must return the uid that was passed in"
    )


# ── TH-02: Global entity may link to many Adventures ─────────────────────────

@pytest.mark.unit
def test_TH_02_global_entity_links_to_multiple_adventures():
    """
    A Global entity may be linked to zero, one, or many Adventures.
    """
    assert hasattr(entities, "add_entity_to_adventure"), (
        "add_entity_to_adventure must be implemented (TH-02: global entity links to many adventures)"
    )
    driver = MagicMock()
    result1 = entities.add_entity_to_adventure(
        driver,
        global_uid="global-npc-elminster",
        adventure_uid="adv-1",
    )
    assert isinstance(result1, dict), "add_entity_to_adventure() must return a dict"
    assert "uid" in result1, (
        "add_entity_to_adventure() first call must return result with 'uid' (linking to adv-1)"
    )

    result2 = entities.add_entity_to_adventure(
        driver,
        global_uid="global-npc-elminster",
        adventure_uid="adv-2",
    )
    assert isinstance(result2, dict), "add_entity_to_adventure() second call must return a dict"
    assert "uid" in result2, (
        "add_entity_to_adventure() second call must return result with 'uid' (linking to adv-2)"
    )


# ── TH-03: one Context node per (Global, Adventure) pair ─────────────────────

@pytest.mark.unit
def test_TH_03_at_most_one_context_per_global_adventure_pair():
    """
    Each (Global entity, Adventure) pair may have at most one Context node.
    """
    assert hasattr(entities, "add_entity_to_adventure"), (
        "add_entity_to_adventure must be implemented (TH-03: one context per global+adventure pair)"
    )
    driver = MagicMock()
    entities.add_entity_to_adventure(
        driver,
        global_uid="global-npc-elminster",
        adventure_uid="adv-1",
    )
    result2 = entities.add_entity_to_adventure(
        driver,
        global_uid="global-npc-elminster",
        adventure_uid="adv-1",
    )
    assert isinstance(result2, dict), "add_entity_to_adventure() duplicate call must return a dict"
    assert "error" in result2, (
        "add_entity_to_adventure() with same global_uid and adventure_uid must return {'error': ...}"
    )


# ── TH-04: adventure-scoped entity promotion preserves uid ───────────────────

@pytest.mark.unit
def test_TH_04_promotion_preserves_uid():
    """
    An adventure-scoped entity may be promoted to a Global node,
    preserving its uid.
    """
    assert hasattr(entities, "promote_to_global"), (
        "promote_to_global must be implemented (TH-04: promotion preserves uid)"
    )
    driver = MagicMock()
    result = entities.promote_to_global(driver, uid="npc-jhaele-silvermane")
    assert isinstance(result, dict), "promote_to_global() must return a dict"
    assert "uid" in result, "promote_to_global() must return result with 'uid'"
    assert result["uid"] == "npc-jhaele-silvermane", (
        "promote_to_global() must preserve the original uid"
    )


# ── TH-05: promoted node becomes a Context node ──────────────────────────────

@pytest.mark.unit
def test_TH_05_promoted_node_becomes_context():
    """
    After promotion, the original adventure-scoped node becomes a Context node.
    """
    assert hasattr(entities, "promote_to_global"), (
        "promote_to_global must be implemented (TH-05: promoted node becomes context)"
    )
    assert hasattr(entities, "get_entity"), (
        "get_entity must be implemented (TH-05: verify promoted node is context)"
    )
    driver = MagicMock()
    entities.promote_to_global(driver, uid="npc-jhaele-silvermane")
    result = entities.get_entity(driver, uid="npc-jhaele-silvermane")
    assert isinstance(result, dict), "get_entity() must return a dict"
    label_or_tier = result.get("label", "") or result.get("tier", "")
    assert "context" in label_or_tier.lower() or result.get("tier") == "context", (
        "After promote_to_global, get_entity must show the node as a context node "
        f"(got label={result.get('label')!r}, tier={result.get('tier')!r})"
    )


# ── TH-06: adventure-scoped entities have valid source_adventure ──────────────

@pytest.mark.unit
def test_TH_06_adventure_scoped_entity_has_valid_source_adventure():
    """
    Adventure-scoped entities must have a source_adventure property that
    matches a valid Adventure uid.
    """
    assert hasattr(entities, "upsert_npc"), (
        "upsert_npc must be implemented (TH-06: adventure entity requires valid source_adventure)"
    )
    driver = MagicMock()
    result = entities.upsert_npc(
        driver,
        uid="npc-test-invalid",
        source_adventure="nonexistent-adventure-uid",
        canonical_name="Test",
    )
    assert isinstance(result, dict), "upsert_npc() must return a dict"
    assert "error" in result, (
        "upsert_npc() with a nonexistent source_adventure must return {'error': ...}"
    )


# ── TH-07: Global identity fields not modifiable via adventure tools ──────────

@pytest.mark.unit
def test_TH_07_global_identity_immutable_via_adventure_tools():
    """
    Global identity fields (canonical_name, source, is_canonical, etc.)
    may not be modified via adventure-scoped tools.
    """
    assert hasattr(entities, "upsert_npc"), (
        "upsert_npc must be implemented (TH-07: global identity fields are immutable via adventure tools)"
    )
    driver = MagicMock()
    result = entities.upsert_npc(
        driver,
        uid="npc-jhaele-silvermane",
        source_adventure="adv-troubles-of-shadowdale",
        canonical_name="New Canonical Name Override",
    )
    assert isinstance(result, dict), "upsert_npc() must return a dict"
    assert "error" in result, (
        "upsert_npc() attempting to set canonical_name (a global identity field) must return {'error': ...}"
    )


# ── TH-08: Context nodes store adventure state without affecting Global ────────

@pytest.mark.unit
def test_TH_08_context_stores_state_without_affecting_global():
    """
    Context nodes may store any adventure-specific state without affecting
    the Global node.
    """
    assert hasattr(entities, "update_entity_context"), (
        "update_entity_context must be implemented (TH-08: context stores state without affecting global)"
    )
    assert hasattr(entities, "get_entity"), (
        "get_entity must be implemented (TH-08: verify global node unchanged)"
    )
    driver = MagicMock()
    ctx_result = entities.update_entity_context(
        driver,
        uid="ctx-elminster-troubles",
        summary="Adventure-specific override",
    )
    assert isinstance(ctx_result, dict), "update_entity_context() must return a dict"
    assert "uid" in ctx_result, "update_entity_context() must return result with 'uid'"
    assert ctx_result["uid"] == "ctx-elminster-troubles", (
        "update_entity_context() must return the context uid"
    )

    elminster = make_elminster()
    global_result = entities.get_entity(driver, uid="global-npc-elminster")
    assert isinstance(global_result, dict), "get_entity() for global must return a dict"
    if "summary" in global_result:
        assert global_result["summary"] != "Adventure-specific override", (
            "update_entity_context() must not modify the global node's summary"
        )
