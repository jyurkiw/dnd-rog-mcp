"""
Narrative Flow unit tests — NF category.

These tests verify the Event → Choice → Outcome → Event graph structure,
DAG integrity, anchor reachability, and the get_narrative_flow output shape.
All tests in this module are pure unit tests. No DB required.
"""

import pytest
from unittest.mock import MagicMock

import dnd_mcp.tools.narrative as narrative

from test.fixtures.shadowdale import make_full_fixture, make_elminster, make_elminster_context, make_adventure, _base


# ── NF-01: every Event belongs to at least one Plotline ──────────────────────

@pytest.mark.unit
def test_NF_01_event_belongs_to_plotline():
    """
    Every Event must belong to at least one Plotline via PART_OF_PLOTLINE.
    """
    assert hasattr(narrative, "add_event"), (
        "narrative.add_event must be implemented (NF-01: event without plotline is invalid)"
    )
    driver = MagicMock()
    result = narrative.add_event(driver, name="Orphan Event", summary="No plotline")
    assert isinstance(result, dict), "add_event() without plotline_uid must return a dict"
    assert "error" in result, (
        "add_event() without plotline_uid must return {'error': ...}"
    )


# ── NF-02: Event may have zero or more BRANCHES_INTO relationships ────────────

@pytest.mark.unit
def test_NF_02_event_branches_into_zero_or_more_choices():
    """
    An Event may have zero or more outbound BRANCHES_INTO relationships
    to Choice nodes.
    """
    assert hasattr(narrative, "add_event"), (
        "narrative.add_event must be implemented (NF-02: event with valid plotline, zero choices)"
    )
    driver = MagicMock()
    result = narrative.add_event(
        driver,
        name="The Arrival",
        summary="Party arrives in Shadowdale",
        plotline_uid="plotline-main-troubles",
    )
    assert isinstance(result, dict), "add_event() with plotline_uid must return a dict"
    assert "uid" in result, (
        "add_event() with valid plotline_uid and zero choices must return result with 'uid'"
    )


# ── NF-03: Choice must have at least one HAS_OUTCOME ─────────────────────────

@pytest.mark.unit
def test_NF_03_choice_has_at_least_one_outcome():
    """
    A Choice must have at least one HAS_OUTCOME relationship to an Outcome node.
    """
    assert hasattr(narrative, "add_choice"), (
        "narrative.add_choice must be implemented (NF-03: choice without outcomes is invalid)"
    )
    driver = MagicMock()
    result = narrative.add_choice(
        driver,
        event_uid="evt-01-arrival",
        description="What does the party do?",
        outcomes=[],
    )
    assert isinstance(result, dict), "add_choice() without outcomes must return a dict"
    assert "error" in result, (
        "add_choice() with no outcomes must return {'error': ...}"
    )


# ── NF-04: Outcome has exactly one LEADS_TO ──────────────────────────────────

@pytest.mark.unit
def test_NF_04_outcome_leads_to_exactly_one_event():
    """
    An Outcome must have exactly one LEADS_TO relationship to an Event.
    """
    assert hasattr(narrative, "add_outcome"), (
        "narrative.add_outcome must be implemented (NF-04: outcome must have exactly one LEADS_TO)"
    )
    assert hasattr(narrative, "link_outcome_to_event"), (
        "narrative.link_outcome_to_event must be implemented (NF-04: outcome leads to exactly one event)"
    )
    driver = MagicMock()
    outcome = narrative.add_outcome(
        driver,
        choice_uid="choice-help-or-flee",
        description="Party helps Elminster",
    )
    assert isinstance(outcome, dict), "add_outcome() must return a dict"

    first_link = narrative.link_outcome_to_event(
        driver,
        outcome_uid="outcome-help-success",
        event_uid="evt-02-confrontation",
    )
    assert isinstance(first_link, dict), "link_outcome_to_event() first call must return a dict"
    assert "error" not in first_link, (
        "link_outcome_to_event() first call must succeed (no 'error' key)"
    )

    second_link = narrative.link_outcome_to_event(
        driver,
        outcome_uid="outcome-help-success",
        event_uid="evt-03-resolution",
    )
    assert isinstance(second_link, dict), "link_outcome_to_event() second call must return a dict"
    assert "error" in second_link, (
        "link_outcome_to_event() called twice for the same outcome must return {'error': ...}"
    )


# ── NF-05: Event may receive LEADS_TO from multiple Outcomes (merge) ──────────

@pytest.mark.unit
def test_NF_05_event_merge_multiple_leads_to():
    """
    An Event may be the target of LEADS_TO from multiple Outcomes —
    this constitutes a valid narrative merge point.
    """
    assert hasattr(narrative, "link_outcome_to_event"), (
        "narrative.link_outcome_to_event must be implemented (NF-05: multiple outcomes can lead to same event)"
    )
    driver = MagicMock()
    result1 = narrative.link_outcome_to_event(
        driver,
        outcome_uid="outcome-path-a",
        event_uid="evt-merge-point",
    )
    assert isinstance(result1, dict), "link_outcome_to_event() first call must return a dict"
    assert "error" not in result1, (
        "link_outcome_to_event() linking outcome-path-a to merge event must succeed"
    )

    result2 = narrative.link_outcome_to_event(
        driver,
        outcome_uid="outcome-path-b",
        event_uid="evt-merge-point",
    )
    assert isinstance(result2, dict), "link_outcome_to_event() second call must return a dict"
    assert "error" not in result2, (
        "link_outcome_to_event() linking outcome-path-b to same merge event must succeed (valid merge)"
    )


# ── NF-06: Event may have direct CAUSES link to another Event ────────────────

@pytest.mark.unit
def test_NF_06_event_direct_causes_link():
    """
    An Event may have a direct CAUSES relationship to another Event,
    expressing a causal link without a Choice/Outcome pair.
    """
    assert hasattr(narrative, "add_causal_link"), (
        "narrative.add_causal_link must be implemented (NF-06: direct CAUSES link between events)"
    )
    driver = MagicMock()
    result = narrative.add_causal_link(
        driver,
        from_uid="evt-01-arrival",
        to_uid="evt-02-confrontation",
    )
    assert isinstance(result, dict), "add_causal_link() must return a dict"
    assert "uid" in result or "from_uid" in result, (
        "add_causal_link() must return result with 'uid' or 'from_uid'"
    )


# ── NF-07: anchor events reachable from Plotline root ────────────────────────

@pytest.mark.unit
def test_NF_07_anchor_events_reachable_from_root():
    """
    Anchor events (is_anchor: true) must be reachable from the Plotline root
    via at least one path through the narrative graph.
    """
    assert hasattr(narrative, "get_narrative_flow"), (
        "narrative.get_narrative_flow must be implemented (NF-07: anchor events in plotline flow)"
    )
    driver = MagicMock()
    result = narrative.get_narrative_flow(
        driver,
        plotline_uid="plotline-main-troubles",
    )
    assert isinstance(result, dict), "get_narrative_flow() must return a dict"
    has_anchor_key = "anchor_events" in result or "nodes" in result
    assert has_anchor_key, (
        "get_narrative_flow() must return a dict with 'anchor_events' or 'nodes' key"
    )


# ── NF-08: narrative flow graph is a valid DAG ───────────────────────────────

@pytest.mark.unit
def test_NF_08_dag_no_cycles():
    """
    The narrative flow graph must be a valid DAG — no cycles permitted.
    """
    assert hasattr(narrative, "add_causal_link"), (
        "narrative.add_causal_link must be implemented (NF-08: DAG cycle detection)"
    )
    driver = MagicMock()
    narrative.add_causal_link(driver, from_uid="evt-A", to_uid="evt-B")
    result = narrative.add_causal_link(driver, from_uid="evt-B", to_uid="evt-A")
    assert isinstance(result, dict), "add_causal_link() creating a cycle must return a dict"
    assert "error" in result, (
        "add_causal_link() creating a cycle (A→B→A) must return {'error': ...} (DAG violation)"
    )


# ── NF-09: root event designated per Plotline ────────────────────────────────

@pytest.mark.unit
def test_NF_09_root_event_designated_per_plotline():
    """
    A root event must be designated per Plotline.
    """
    assert hasattr(narrative, "upsert_plotline"), (
        "narrative.upsert_plotline must be implemented (NF-09: plotline with root_event_uid)"
    )
    driver = MagicMock()
    result = narrative.upsert_plotline(
        driver,
        uid="plotline-main-troubles",
        name="The Troubles of Shadowdale",
        root_event_uid="evt-01-arrival",
    )
    assert isinstance(result, dict), "upsert_plotline() must return a dict"
    assert "uid" in result, (
        "upsert_plotline() with root_event_uid must return result with 'uid'"
    )


# ── NF-10: get_narrative_flow returns flowchart-renderable structure ──────────

@pytest.mark.unit
def test_NF_10_get_narrative_flow_returns_renderable_structure():
    """
    get_narrative_flow must return a structure that is directly renderable
    as a Mermaid or Graphviz flowchart.
    """
    assert hasattr(narrative, "get_narrative_flow"), (
        "narrative.get_narrative_flow must be implemented (NF-10: flowchart-renderable structure)"
    )
    driver = MagicMock()
    result = narrative.get_narrative_flow(
        driver,
        plotline_uid="plotline-main-troubles",
    )
    assert isinstance(result, dict), "get_narrative_flow() must return a dict"
    has_nodes = "nodes" in result or "events" in result
    has_edges = "edges" in result or "choices" in result
    assert has_nodes, (
        "get_narrative_flow() must return a dict with 'nodes' or 'events' key for flowchart rendering"
    )
    assert has_edges, (
        "get_narrative_flow() must return a dict with 'edges' or 'choices' key for flowchart rendering"
    )
