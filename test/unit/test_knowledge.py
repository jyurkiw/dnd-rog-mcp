"""
World Knowledge unit tests — WK category.

These tests verify Rumor and Fact attachment rules, field constraints,
multi-entity attachment, and the who_knows_what query.
All tests in this module are pure unit tests. No DB required.
"""

import pytest
from unittest.mock import MagicMock

import dnd_mcp.tools.knowledge as knowledge

from test.fixtures.shadowdale import make_full_fixture, make_elminster, make_elminster_context, make_adventure, _base


# ── WK-01: Rumor attached to at least one entity ─────────────────────────────

@pytest.mark.unit
def test_WK_01_rumor_attached_to_entity():
    """
    A Rumor must be attached to at least one NPC, Location, or Faction.
    """
    assert hasattr(knowledge, "add_rumor"), (
        "knowledge.add_rumor must be implemented (WK-01: rumor must be attached to at least one entity)"
    )
    driver = MagicMock()

    result_empty = knowledge.add_rumor(
        driver,
        content_summary="Something suspicious is happening",
        attached_to_uids=[],
    )
    assert isinstance(result_empty, dict), "add_rumor() with empty attached_to_uids must return a dict"
    assert "error" in result_empty, (
        "add_rumor() with empty attached_to_uids must return {'error': ...}"
    )

    result_missing = knowledge.add_rumor(
        driver,
        content_summary="Something suspicious is happening",
    )
    assert isinstance(result_missing, dict), "add_rumor() without attached_to_uids must return a dict"
    assert "error" in result_missing, (
        "add_rumor() without attached_to_uids must return {'error': ...}"
    )


# ── WK-02: Rumor is_true field values ────────────────────────────────────────

@pytest.mark.unit
def test_WK_02_rumor_is_true_nullable():
    """
    A Rumor's is_true field may be true, false, or null (unknown).
    """
    assert hasattr(knowledge, "add_rumor"), (
        "knowledge.add_rumor must be implemented (WK-02: rumor is_true can be True, False, or None)"
    )
    driver = MagicMock()

    result_true = knowledge.add_rumor(
        driver,
        content_summary="Elminster is Mystra's Chosen",
        attached_to_uids=["global-npc-elminster"],
        is_true=True,
    )
    assert isinstance(result_true, dict), "add_rumor() with is_true=True must return a dict"
    assert "error" not in result_true, (
        "add_rumor() with is_true=True must succeed (no 'error' key)"
    )

    result_false = knowledge.add_rumor(
        driver,
        content_summary="Elminster is secretly evil",
        attached_to_uids=["global-npc-elminster"],
        is_true=False,
    )
    assert isinstance(result_false, dict), "add_rumor() with is_true=False must return a dict"
    assert "error" not in result_false, (
        "add_rumor() with is_true=False must succeed (no 'error' key)"
    )

    result_none = knowledge.add_rumor(
        driver,
        content_summary="Elminster may have a secret weakness",
        attached_to_uids=["global-npc-elminster"],
        is_true=None,
    )
    assert isinstance(result_none, dict), "add_rumor() with is_true=None must return a dict"
    assert "error" not in result_none, (
        "add_rumor() with is_true=None must succeed (no 'error' key)"
    )


# ── WK-03: Fact reliability field values ─────────────────────────────────────

@pytest.mark.unit
def test_WK_03_fact_reliability_field():
    """
    A Fact must have a reliability field with value: established, rumored,
    or contradicted.
    """
    assert hasattr(knowledge, "add_fact"), (
        "knowledge.add_fact must be implemented (WK-03: fact reliability must be established/rumored/contradicted)"
    )
    driver = MagicMock()

    for valid_reliability in ("established", "rumored", "contradicted"):
        result = knowledge.add_fact(
            driver,
            content_summary="A known fact about Shadowdale",
            attached_to_uids=["global-loc-shadowdale"],
            reliability=valid_reliability,
        )
        assert isinstance(result, dict), (
            f"add_fact() with reliability={valid_reliability!r} must return a dict"
        )
        assert "error" not in result, (
            f"add_fact() with reliability={valid_reliability!r} must succeed (no 'error' key)"
        )

    result_invalid = knowledge.add_fact(
        driver,
        content_summary="Something unclear",
        attached_to_uids=["global-loc-shadowdale"],
        reliability="unknown",
    )
    assert isinstance(result_invalid, dict), "add_fact() with reliability='unknown' must return a dict"
    assert "error" in result_invalid, (
        "add_fact() with reliability='unknown' (invalid value) must return {'error': ...}"
    )


# ── WK-04: Rumors and Facts queryable by entity ──────────────────────────────

@pytest.mark.unit
def test_WK_04_rumors_and_facts_queryable_by_entity():
    """
    Both Rumors and Facts must be queryable by the entity they are attached to.
    """
    assert hasattr(knowledge, "get_rumors_for"), (
        "knowledge.get_rumors_for must be implemented (WK-04: rumors queryable by entity)"
    )
    driver = MagicMock()
    result = knowledge.get_rumors_for(driver, entity_uid="npc-jhaele-silvermane")
    assert isinstance(result, (list, dict)), "get_rumors_for() must return a list or dict"
    if isinstance(result, dict):
        assert "rumors" in result, (
            "get_rumors_for() returning a dict must contain a 'rumors' key"
        )
        assert isinstance(result["rumors"], list), (
            "get_rumors_for() result['rumors'] must be a list"
        )


# ── WK-05: single Rumor or Fact may attach to multiple entities ───────────────

@pytest.mark.unit
def test_WK_05_rumor_fact_attached_to_multiple_entities():
    """
    A single Rumor or Fact may be attached to multiple entities simultaneously.
    """
    assert hasattr(knowledge, "add_rumor"), (
        "knowledge.add_rumor must be implemented (WK-05: single rumor attached to multiple entities)"
    )
    driver = MagicMock()
    result = knowledge.add_rumor(
        driver,
        content_summary="Both Jhaele and the Tymora priestess know something",
        attached_to_uids=["npc-jhaele-silvermane", "npc-tymora-priestess"],
        is_true=None,
    )
    assert isinstance(result, dict), "add_rumor() with multiple attached_to_uids must return a dict"
    assert "error" not in result, (
        "add_rumor() with attached_to_uids=['npc-jhaele-silvermane', 'npc-tymora-priestess'] must succeed"
    )


# ── WK-06: who_knows_what returns NPCs with path to Rumor or Fact ─────────────

@pytest.mark.unit
def test_WK_06_who_knows_what_returns_npc_paths():
    """
    who_knows_what must return all NPCs with a path to a given Rumor or Fact.
    """
    assert hasattr(knowledge, "who_knows_what"), (
        "knowledge.who_knows_what must be implemented (WK-06: who_knows_what returns NPC uids)"
    )
    driver = MagicMock()
    result = knowledge.who_knows_what(driver, target_uid="rumor-pipe-missing")
    assert isinstance(result, (list, dict)), "who_knows_what() must return a list or dict"
    if isinstance(result, dict):
        assert "npcs" in result, (
            "who_knows_what() returning a dict must contain an 'npcs' key"
        )
