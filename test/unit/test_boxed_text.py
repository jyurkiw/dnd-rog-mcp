"""
Boxed Text unit tests — BT category.

These tests verify BoxedText schema rules, sequencing relationships,
conditional dependency auto-creation, backlog queryability, and the
get_boxed_text_sequence output shape.
All tests in this module are pure unit tests. No DB required.
"""

import pytest
from unittest.mock import MagicMock

import dnd_mcp.tools.boxed_text as boxed_text

from test.fixtures.shadowdale import make_full_fixture, make_elminster, make_elminster_context, make_adventure, _base


# ── BT-01: BoxedText stores summaries, never full prose ──────────────────────

@pytest.mark.unit
def test_BT_01_boxed_text_stores_summaries_not_prose():
    """
    A BoxedText node stores trigger summary, content summary, tone, and
    sequence position — never full prose content.
    """
    assert hasattr(boxed_text, "add_boxed_text"), (
        "boxed_text.add_boxed_text must be implemented (BT-01: stores summaries, not full prose)"
    )
    driver = MagicMock()
    result = boxed_text.add_boxed_text(
        driver,
        attached_to_uid="evt-01-arrival",
        trigger_summary="Party enters Shadowdale",
        content_summary="The village square is bustling with anxious townsfolk",
        tone="ominous",
        sequence_position=1,
    )
    assert isinstance(result, dict), "add_boxed_text() with summary fields must return a dict"
    assert "uid" in result, (
        "add_boxed_text() with valid summary fields must return result with 'uid'"
    )

    result_with_prose = boxed_text.add_boxed_text(
        driver,
        attached_to_uid="evt-01-arrival",
        trigger_summary="Party enters Shadowdale",
        content_summary="The village square is bustling with anxious townsfolk",
        tone="ominous",
        sequence_position=2,
        full_content="As you crest the hill, the village of Shadowdale spreads before you...",
    )
    assert isinstance(result_with_prose, dict), "add_boxed_text() with full_content must return a dict"
    if "error" not in result_with_prose:
        assert "full_content" not in result_with_prose, (
            "add_boxed_text() must ignore or strip 'full_content' field (full prose not accepted)"
        )


# ── BT-02: BoxedText may optionally reference a FileRef ──────────────────────

@pytest.mark.unit
def test_BT_02_boxed_text_optional_fileref():
    """
    A BoxedText may optionally reference a FileRef for the full prose file.
    """
    assert hasattr(boxed_text, "add_boxed_text"), (
        "boxed_text.add_boxed_text must be implemented (BT-02: file_ref_uid is optional)"
    )
    driver = MagicMock()

    result_no_ref = boxed_text.add_boxed_text(
        driver,
        attached_to_uid="evt-01-arrival",
        trigger_summary="Party enters Shadowdale",
        content_summary="Anxious townsfolk fill the square",
        tone="neutral",
        sequence_position=1,
        file_ref_uid=None,
    )
    assert isinstance(result_no_ref, dict), "add_boxed_text() with file_ref_uid=None must return a dict"
    assert "error" not in result_no_ref, (
        "add_boxed_text() with file_ref_uid=None must succeed (no 'error' key)"
    )

    result_with_ref = boxed_text.add_boxed_text(
        driver,
        attached_to_uid="evt-02-confrontation",
        trigger_summary="Party confronts the Zhentarim",
        content_summary="A hooded figure blocks your path",
        tone="tense",
        sequence_position=1,
        file_ref_uid="some-file-ref",
    )
    assert isinstance(result_with_ref, dict), "add_boxed_text() with file_ref_uid set must return a dict"
    assert "error" not in result_with_ref, (
        "add_boxed_text() with file_ref_uid='some-file-ref' must succeed (no 'error' key)"
    )


# ── BT-03: BoxedText attachable to multiple node types ───────────────────────

@pytest.mark.unit
def test_BT_03_boxed_text_valid_attachment_types():
    """
    BoxedText may be attached to: Event, Location, NPC/NPCContext, Choice,
    Combat, Trap, or SkillChallenge.
    """
    assert hasattr(boxed_text, "add_boxed_text"), (
        "boxed_text.add_boxed_text must be implemented (BT-03: valid attachment types)"
    )
    driver = MagicMock()
    valid_attachments = [
        ("evt-01-arrival", "Event"),
        ("global-loc-shadowdale", "Location"),
        ("global-npc-elminster", "NPC"),
        ("ctx-elminster-troubles", "NPCContext"),
        ("choice-help-or-flee", "Choice"),
        ("combat-graveyard-undead", "Combat"),
        ("trap-tower-entrance", "Trap"),
        ("sc-sneak-into-zhentarim", "SkillChallenge"),
    ]
    for uid, label in valid_attachments:
        result = boxed_text.add_boxed_text(
            driver,
            attached_to_uid=uid,
            trigger_summary=f"Trigger for {label}",
            content_summary=f"Content for {label}",
            tone="neutral",
            sequence_position=1,
            trigger_condition="always",
        )
        assert isinstance(result, dict), (
            f"add_boxed_text() attached to {label} must return a dict"
        )
        assert "uid" in result, (
            f"add_boxed_text() attached to {label} ({uid}) must return result with 'uid'"
        )


# ── BT-04: BoxedTextSequence groups boxes with OPENS_WITH entry point ─────────

@pytest.mark.unit
def test_BT_04_sequence_opens_with_entry_point():
    """
    A BoxedTextSequence groups related BoxedText nodes with a defined entry
    point via the OPENS_WITH relationship.
    """
    assert hasattr(boxed_text, "add_boxed_text_sequence"), (
        "boxed_text.add_boxed_text_sequence must be implemented (BT-04: sequence with OPENS_WITH)"
    )
    assert hasattr(boxed_text, "add_boxed_text"), (
        "boxed_text.add_boxed_text must be implemented (BT-04: first box creates OPENS_WITH)"
    )
    driver = MagicMock()
    seq_result = boxed_text.add_boxed_text_sequence(
        driver,
        uid="seq-arrival-scene",
        name="Test Sequence",
    )
    assert isinstance(seq_result, dict), "add_boxed_text_sequence() must return a dict"
    assert "uid" in seq_result, (
        "add_boxed_text_sequence() must return result with 'uid'"
    )

    bt_result = boxed_text.add_boxed_text(
        driver,
        attached_to_uid="evt-01-arrival",
        sequence_uid="seq-arrival-scene",
        trigger_summary="First moment of arrival",
        content_summary="Opening scene description",
        tone="dramatic",
        sequence_position=1,
    )
    assert isinstance(bt_result, dict), "add_boxed_text() with sequence_uid must return a dict"
    assert "uid" in bt_result, (
        "add_boxed_text() as first entry in sequence must return result with 'uid' (creates OPENS_WITH)"
    )


# ── BT-05: FOLLOWED_BY carries condition and condition_type ──────────────────

@pytest.mark.unit
def test_BT_05_followed_by_has_condition_and_type():
    """
    FOLLOWED_BY relationships must carry a condition (nullable) and
    a condition_type field.
    """
    assert hasattr(boxed_text, "link_boxed_text"), (
        "boxed_text.link_boxed_text must be implemented (BT-05: FOLLOWED_BY requires condition_type)"
    )
    driver = MagicMock()

    result_no_type = boxed_text.link_boxed_text(
        driver,
        from_uid="bt-01-arrival-open",
        to_uid="bt-02-arrival-crowd",
        condition="party_is_friendly",
    )
    assert isinstance(result_no_type, dict), "link_boxed_text() without condition_type must return a dict"
    assert "error" in result_no_type, (
        "link_boxed_text() without condition_type must return {'error': ...}"
    )

    result_unconditional = boxed_text.link_boxed_text(
        driver,
        from_uid="bt-01-arrival-open",
        to_uid="bt-02-arrival-crowd",
        condition=None,
        condition_type=None,
    )
    assert isinstance(result_unconditional, dict), (
        "link_boxed_text() with condition=None, condition_type=None must return a dict"
    )
    assert "error" not in result_unconditional, (
        "link_boxed_text() with condition=None, condition_type=None (unconditional) must succeed"
    )

    result_conditional = boxed_text.link_boxed_text(
        driver,
        from_uid="bt-01-arrival-open",
        to_uid="bt-03-arrival-pipe",
        condition="party_has:pipe-of-elminster",
        condition_type="possession",
    )
    assert isinstance(result_conditional, dict), (
        "link_boxed_text() with possession condition must return a dict"
    )
    assert "error" not in result_conditional, (
        "link_boxed_text() with condition_type='possession' must succeed (no 'error' key)"
    )


# ── BT-06: ALTERNATIVE_TO carries reason property ────────────────────────────

@pytest.mark.unit
def test_BT_06_alternative_to_has_reason():
    """
    Mutually exclusive variant boxes must be linked by ALTERNATIVE_TO with
    a reason property explaining the exclusivity.
    """
    assert hasattr(boxed_text, "add_alternative_boxed_text"), (
        "boxed_text.add_alternative_boxed_text must be implemented (BT-06: ALTERNATIVE_TO requires reason)"
    )
    driver = MagicMock()

    result_no_reason = boxed_text.add_alternative_boxed_text(
        driver,
        base_uid="bt-01-arrival-open",
        alternative_uid="bt-01b-arrival-open-alt",
    )
    assert isinstance(result_no_reason, dict), "add_alternative_boxed_text() without reason must return a dict"
    assert "error" in result_no_reason, (
        "add_alternative_boxed_text() without reason must return {'error': ...}"
    )

    result_with_reason = boxed_text.add_alternative_boxed_text(
        driver,
        base_uid="bt-01-arrival-open",
        alternative_uid="bt-01b-arrival-open-alt",
        reason="Party has the pipe vs doesn't",
    )
    assert isinstance(result_with_reason, dict), "add_alternative_boxed_text() with reason must return a dict"
    assert "error" not in result_with_reason, (
        "add_alternative_boxed_text() with reason='Party has the pipe vs doesn't' must succeed"
    )


# ── BT-07: BoxedText without FileRef is valid ────────────────────────────────

@pytest.mark.unit
def test_BT_07_boxed_text_without_fileref_is_valid():
    """
    BoxedText without a FileRef is valid — it represents a planned but
    unwritten narrative moment.
    """
    assert hasattr(boxed_text, "add_boxed_text"), (
        "boxed_text.add_boxed_text must be implemented (BT-07: boxed text without file_ref is valid)"
    )
    driver = MagicMock()
    result = boxed_text.add_boxed_text(
        driver,
        attached_to_uid="evt-01-arrival",
        trigger_summary="Party first sees Shadowdale",
        content_summary="Overview of the village at dusk",
        tone="peaceful",
        sequence_position=1,
    )
    assert isinstance(result, dict), "add_boxed_text() without file_ref_uid must return a dict"
    assert "error" not in result, (
        "add_boxed_text() without file_ref_uid must succeed (boxed text without file ref is valid)"
    )
    assert "uid" in result, (
        "add_boxed_text() without file_ref_uid must return result with 'uid'"
    )


# ── BT-08: BoxedText without FileRef listable as backlog ─────────────────────

@pytest.mark.unit
def test_BT_08_unwritten_boxed_text_listable_as_backlog():
    """
    BoxedText nodes without a FileRef must be listable as a prose writing
    backlog via list_unwritten_boxed_text.
    """
    assert hasattr(boxed_text, "list_unwritten_boxed_text"), (
        "boxed_text.list_unwritten_boxed_text must be implemented (BT-08: backlog of unwritten boxed text)"
    )
    driver = MagicMock()
    result = boxed_text.list_unwritten_boxed_text(driver)
    assert isinstance(result, list), (
        "list_unwritten_boxed_text() must return a list"
    )


# ── BT-09: dependency relationships created from conditions ──────────────────

@pytest.mark.unit
def test_BT_09_dependency_rels_created_from_conditions():
    """
    Dependency relationships (DEPENDS_ON_EVENT, DEPENDS_ON_ITEM,
    DEPENDS_ON_CHOICE) must be created automatically when a condition
    referencing that entity is set on a FOLLOWED_BY relationship.
    """
    assert hasattr(boxed_text, "link_boxed_text"), (
        "boxed_text.link_boxed_text must be implemented (BT-09: event_flag condition creates DEPENDS_ON_EVENT)"
    )
    driver = MagicMock()
    result = boxed_text.link_boxed_text(
        driver,
        from_uid="bt-01-arrival-open",
        to_uid="bt-04-pipe-returned",
        condition="event:pipe-returned:completed",
        condition_type="event_flag",
    )
    assert isinstance(result, dict), "link_boxed_text() with event_flag condition must return a dict"
    assert "error" not in result, (
        "link_boxed_text() with condition_type='event_flag' must succeed (no 'error' key)"
    )
    assert result.get("dependency_created") is True, (
        "link_boxed_text() with event_flag condition must return {'dependency_created': True}"
    )


# ── BT-10: get_boxed_text_sequence returns full sequence graph ────────────────

@pytest.mark.unit
def test_BT_10_get_boxed_text_sequence_full_graph():
    """
    get_boxed_text_sequence must return the full sequence graph including
    all BoxedText nodes, FOLLOWED_BY chains, and ALTERNATIVE_TO links.
    """
    assert hasattr(boxed_text, "get_boxed_text_sequence"), (
        "boxed_text.get_boxed_text_sequence must be implemented (BT-10: full sequence graph)"
    )
    driver = MagicMock()
    result = boxed_text.get_boxed_text_sequence(
        driver,
        sequence_uid="seq-arrival-scene",
    )
    assert isinstance(result, dict), "get_boxed_text_sequence() must return a dict"
    required_keys = {"sequence", "boxes", "links"}
    has_required = required_keys.issubset(result.keys())
    assert has_required, (
        f"get_boxed_text_sequence() must return dict with keys {required_keys}. "
        f"Got: {set(result.keys())}"
    )


# ── BT-11: query for prose depending on entity is satisfiable ─────────────────

@pytest.mark.unit
def test_BT_11_query_prose_depending_on_entity():
    """
    A query for 'what prose depends on this entity' must be satisfiable
    via the dependency relationships on BoxedText nodes.
    """
    assert hasattr(boxed_text, "get_boxed_text_sequence"), (
        "boxed_text.get_boxed_text_sequence must be implemented (BT-11: dependency reverse query)"
    )
    driver = MagicMock()
    result = boxed_text.get_boxed_text_sequence(
        driver,
        sequence_uid="seq-arrival-scene",
    )
    assert isinstance(result, dict), "get_boxed_text_sequence() must return a dict"
    has_dependency_info = (
        "boxes" in result
        or "dependencies" in result
        or "links" in result
    )
    assert has_dependency_info, (
        "get_boxed_text_sequence() result must contain dependency information "
        "to support 'what prose depends on event X' queries"
    )
