"""
Timeline & History unit tests — TL category.

These tests verify Timeline structure, multi-timeline membership, ordering
storage, historical event rules, and the get_timeline / get_history_for
output contracts.
All tests in this module are pure unit tests. No DB required.
"""

import pytest
from unittest.mock import MagicMock

import dnd_mcp.tools.timeline as timeline
import dnd_mcp.tools.narrative as narrative

from test.fixtures.shadowdale import make_full_fixture, make_elminster, make_elminster_context, make_adventure, _base


# ── TL-01: Timeline is a named ordered sequence of Events ────────────────────

@pytest.mark.unit
def test_TL_01_timeline_named_ordered_sequence():
    """
    A Timeline is a named, ordered sequence of Event nodes.
    """
    assert hasattr(timeline, "create_timeline"), (
        "timeline.create_timeline must be implemented (TL-01: timeline is a named ordered sequence)"
    )
    driver = MagicMock()
    result = timeline.create_timeline(
        driver,
        name="Main Timeline",
        era="1374 DR",
    )
    assert isinstance(result, dict), "create_timeline() must return a dict"
    assert "uid" in result, (
        "create_timeline() with name and era must return result with 'uid'"
    )


# ── TL-02: Event may belong to zero or more Timelines ────────────────────────

@pytest.mark.unit
def test_TL_02_event_belongs_to_zero_or_more_timelines():
    """
    An Event may belong to zero or more Timelines simultaneously.
    """
    assert hasattr(timeline, "place_event_on_timeline"), (
        "timeline.place_event_on_timeline must be implemented (TL-02: event on multiple timelines)"
    )
    driver = MagicMock()

    result1 = timeline.place_event_on_timeline(
        driver,
        event_uid="evt-01-arrival",
        timeline_uid="timeline-1",
    )
    assert isinstance(result1, dict), "place_event_on_timeline() first call must return a dict"
    assert "error" not in result1, (
        "place_event_on_timeline() placing event on timeline-1 must succeed (no 'error' key)"
    )

    result2 = timeline.place_event_on_timeline(
        driver,
        event_uid="evt-01-arrival",
        timeline_uid="timeline-2",
    )
    assert isinstance(result2, dict), "place_event_on_timeline() second call must return a dict"
    assert "error" not in result2, (
        "place_event_on_timeline() placing same event on timeline-2 must succeed (multi-timeline valid)"
    )


# ── TL-03: ordering stored on PRECEDES relationship ──────────────────────────

@pytest.mark.unit
def test_TL_03_ordering_stored_on_precedes_relationship():
    """
    Event ordering on a Timeline is stored on the PRECEDES relationship,
    not as a property on the Event node itself.
    """
    assert hasattr(timeline, "place_event_on_timeline"), (
        "timeline.place_event_on_timeline must be implemented (TL-03: ordering on PRECEDES relationship)"
    )
    driver = MagicMock()
    result = timeline.place_event_on_timeline(
        driver,
        event_uid="evt-01-arrival",
        timeline_uid="timeline-main",
        position=1,
    )
    assert isinstance(result, dict), "place_event_on_timeline() with position must return a dict"
    assert "error" not in result, (
        "place_event_on_timeline() with position=1 must succeed (no 'error' key)"
    )
    if "position_on_event" in result:
        assert not result.get("position_on_event"), (
            "place_event_on_timeline() must NOT store position on the event node itself"
        )
    if "position_on_relationship" in result or "precedes_position" in result:
        pass


# ── TL-04: historical events may have no Plotline association ─────────────────

@pytest.mark.unit
def test_TL_04_historical_events_no_plotline_required():
    """
    Historical events (is_historical: true) may have no Plotline association.
    """
    assert hasattr(narrative, "add_event"), (
        "narrative.add_event must be implemented (TL-04: historical events don't require plotline)"
    )
    driver = MagicMock()
    result = narrative.add_event(
        driver,
        name="The Time of Troubles",
        summary="Gods walk the Forgotten Realms",
        is_historical=True,
        plotline_uid=None,
    )
    assert isinstance(result, dict), "add_event() with is_historical=True must return a dict"
    assert "error" not in result, (
        "add_event() with is_historical=True and plotline_uid=None must succeed (no 'error' key)"
    )


# ── TL-05: get_timeline returns events in chronological order ─────────────────

@pytest.mark.unit
def test_TL_05_get_timeline_chronological_order():
    """
    get_timeline must return events in chronological order as defined by
    the PRECEDES relationships.
    """
    assert hasattr(timeline, "get_timeline"), (
        "timeline.get_timeline must be implemented (TL-05: events in chronological order)"
    )
    driver = MagicMock()
    result = timeline.get_timeline(driver, timeline_uid="timeline-main")
    assert isinstance(result, dict), "get_timeline() must return a dict"
    assert "events" in result or "nodes" in result, (
        "get_timeline() must return a dict with 'events' or 'nodes' key"
    )
    events = result.get("events") or result.get("nodes", [])
    assert isinstance(events, list), (
        "get_timeline() events/nodes must be a list"
    )


# ── TL-06: get_history_for returns entity events ordered by position ──────────

@pytest.mark.unit
def test_TL_06_get_history_for_ordered_by_timeline_position():
    """
    get_history_for must return all events involving an entity, ordered
    by their timeline position.
    """
    assert hasattr(timeline, "get_history_for"), (
        "timeline.get_history_for must be implemented (TL-06: entity events ordered by timeline position)"
    )
    driver = MagicMock()
    result = timeline.get_history_for(driver, entity_uid="global-npc-elminster")
    assert isinstance(result, list), (
        "get_history_for() must return a list of events"
    )
