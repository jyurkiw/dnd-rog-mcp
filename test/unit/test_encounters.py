"""
Encounters unit tests — EN category.

These tests verify encounter attachment rules, optional numeric fields,
participant support, skill challenge / trap schemas, and BoxedText association.
All tests in this module are pure unit tests. No DB required.
"""

import pytest
from unittest.mock import MagicMock

import dnd_mcp.tools.encounters as encounters
import dnd_mcp.tools.boxed_text as boxed_text

from test.fixtures.shadowdale import make_full_fixture, make_elminster, make_elminster_context, make_adventure, _base


# ── EN-01: encounter attached to Location or Event ───────────────────────────

@pytest.mark.unit
def test_EN_01_encounter_attached_to_location_or_event():
    """
    A Combat, SkillChallenge, or Trap must be attached to at least one
    Location or Event.
    """
    assert hasattr(encounters, "upsert_combat"), (
        "encounters.upsert_combat must be implemented (EN-01: encounter must attach to location or event)"
    )
    driver = MagicMock()
    result = encounters.upsert_combat(
        driver,
        uid="combat-graveyard-undead",
        name="Graveyard Skirmish",
    )
    assert isinstance(result, dict), "upsert_combat() without location_uid or event_uid must return a dict"
    assert "error" in result, (
        "upsert_combat() without location_uid and without event_uid must return {'error': ...}"
    )


# ── EN-02: encounter stores cr and xp as optional numerics ───────────────────

@pytest.mark.unit
def test_EN_02_encounter_cr_xp_optional_numeric():
    """
    Encounter nodes must store cr and xp as optional numeric fields.
    """
    assert hasattr(encounters, "upsert_combat"), (
        "encounters.upsert_combat must be implemented (EN-02: cr and xp are optional numerics)"
    )
    driver = MagicMock()

    result_numeric = encounters.upsert_combat(
        driver,
        uid="combat-graveyard-numeric",
        name="Graveyard Skirmish",
        location_uid="global-loc-shadowdale-graveyard",
        cr=2.5,
        xp=450,
    )
    assert isinstance(result_numeric, dict), "upsert_combat() with cr=2.5, xp=450 must return a dict"
    assert "error" not in result_numeric, (
        "upsert_combat() with cr=2.5, xp=450 must succeed (no 'error' key)"
    )

    result_none = encounters.upsert_combat(
        driver,
        uid="combat-graveyard-none",
        name="Graveyard Skirmish (no cr/xp)",
        location_uid="global-loc-shadowdale-graveyard",
        cr=None,
        xp=None,
    )
    assert isinstance(result_none, dict), "upsert_combat() with cr=None, xp=None must return a dict"
    assert "error" not in result_none, (
        "upsert_combat() with cr=None, xp=None must succeed (optional fields)"
    )

    result_string_cr = encounters.upsert_combat(
        driver,
        uid="combat-graveyard-strtype",
        name="Graveyard Skirmish (bad cr)",
        location_uid="global-loc-shadowdale-graveyard",
        cr="high",
    )
    assert isinstance(result_string_cr, dict), "upsert_combat() with cr='high' must return a dict"
    assert "error" in result_string_cr, (
        "upsert_combat() with cr='high' (non-numeric) must return {'error': ...}"
    )


# ── EN-03: Combat supports multiple participant NPCs ─────────────────────────

@pytest.mark.unit
def test_EN_03_combat_multiple_participants():
    """
    A Combat must support multiple participant NPCs via PARTICIPANT_IN
    relationships.
    """
    assert hasattr(encounters, "upsert_combat"), (
        "encounters.upsert_combat must be implemented (EN-03: combat supports multiple participants)"
    )
    driver = MagicMock()
    result = encounters.upsert_combat(
        driver,
        uid="combat-graveyard-multi",
        name="Graveyard Multi-Battle",
        location_uid="global-loc-shadowdale-graveyard",
        participant_uids=["npc-monster-graveyard", "npc-monster-millpond"],
    )
    assert isinstance(result, dict), "upsert_combat() with multiple participants must return a dict"
    assert "uid" in result, (
        "upsert_combat() with participant_uids must return result with 'uid'"
    )


# ── EN-04: SkillChallenge stores applicable skills and DCs ───────────────────

@pytest.mark.unit
def test_EN_04_skill_challenge_stores_skills_and_dcs():
    """
    A SkillChallenge must store applicable skills and their DCs.
    """
    assert hasattr(encounters, "upsert_skill_challenge"), (
        "encounters.upsert_skill_challenge must be implemented (EN-04: skill challenge with skills and DC)"
    )
    driver = MagicMock()
    result = encounters.upsert_skill_challenge(
        driver,
        uid="sc-sneak-into-zhentarim",
        name="Infiltrate the Zhentarim",
        event_uid="evt-03-infiltration",
        skills_involved=["Stealth", "Perception"],
        dc=13,
    )
    assert isinstance(result, dict), "upsert_skill_challenge() with skills and dc must return a dict"
    assert "uid" in result, (
        "upsert_skill_challenge() with skills_involved and dc must return result with 'uid'"
    )


# ── EN-05: Trap stores trigger, effect summary, reset condition ───────────────

@pytest.mark.unit
def test_EN_05_trap_stores_trigger_effect_reset():
    """
    A Trap must store trigger, effect summary, and reset condition.
    """
    assert hasattr(encounters, "upsert_trap"), (
        "encounters.upsert_trap must be implemented (EN-05: trap with trigger, damage, and reset)"
    )
    driver = MagicMock()
    result = encounters.upsert_trap(
        driver,
        uid="trap-tower-entrance",
        name="Tower Floor Plate",
        location_uid="global-loc-elminster-tower",
        trigger="weight plate",
        damage="2d6 piercing",
        reset="manual",
    )
    assert isinstance(result, dict), "upsert_trap() with trigger, damage, reset must return a dict"
    assert "uid" in result, (
        "upsert_trap() with trigger, damage, reset must return result with 'uid'"
    )


# ── EN-06: encounter may have associated BoxedText ───────────────────────────

@pytest.mark.unit
def test_EN_06_encounter_associated_boxed_text():
    """
    An encounter may have an associated BoxedText node for its introduction
    moment.
    """
    assert hasattr(encounters, "upsert_combat"), (
        "encounters.upsert_combat must be implemented (EN-06: encounter can have boxed text)"
    )
    assert hasattr(boxed_text, "add_boxed_text"), (
        "boxed_text.add_boxed_text must be implemented (EN-06: add boxed text to encounter)"
    )
    driver = MagicMock()
    combat_result = encounters.upsert_combat(
        driver,
        uid="combat-graveyard-bt",
        name="Graveyard Encounter (with intro text)",
        location_uid="global-loc-shadowdale-graveyard",
    )
    assert isinstance(combat_result, dict), "upsert_combat() must return a dict"
    encounter_uid = combat_result.get("uid", "combat-graveyard-bt")

    bt_result = boxed_text.add_boxed_text(
        driver,
        attached_to_uid=encounter_uid,
        trigger_summary="Party enters the graveyard at midnight",
        content_summary="Undead rise from the graves, shambling toward you",
        tone="ominous",
        sequence_position=1,
    )
    assert isinstance(bt_result, dict), "add_boxed_text() attached to encounter must return a dict"
    assert "error" not in bt_result, (
        "add_boxed_text() attached to a Combat encounter uid must succeed (no 'error' key)"
    )
    assert "uid" in bt_result, (
        "add_boxed_text() attached to encounter must return result with 'uid'"
    )
