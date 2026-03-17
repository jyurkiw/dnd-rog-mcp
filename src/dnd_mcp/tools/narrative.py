"""Tool handlers: narrative flow — plotlines, events, choices, outcomes."""

from typing import Optional
from neo4j import Driver

from dnd_mcp.db import queries
from dnd_mcp.db.connection import get_database
from dnd_mcp.models.nodes import Plotline, Event, Choice, Outcome


def _err(code: str, reason: str) -> dict:
    return {"error": f"{code}: {reason}"}


def _ok(uid: str) -> dict:
    return {"uid": uid, "status": "ok"}


def _response(props: dict) -> dict:
    return {k: v for k, v in props.items() if v is not None and v != []}


# ── Plotline ──────────────────────────────────────────────────────────────────

def upsert_plotline(
    driver: Driver,
    uid: str,
    source_adventure: str,
    name: str,
    summary: Optional[str] = None,
    status: str = "draft",
    theme: Optional[str] = None,
) -> dict:
    if not queries.node_exists(driver, source_adventure):
        return _err("NOT_FOUND", f"adventure '{source_adventure}' not found")

    if queries.node_exists(driver, uid):
        updates = {}
        if name:
            updates["name"] = name
        if summary is not None:
            updates["summary"] = summary
        if status:
            updates["status"] = status
        if theme is not None:
            updates["theme"] = theme
        queries.update_node(driver, uid, updates)
    else:
        node = Plotline(uid=uid, name=name, summary=summary, status=status,
                        theme=theme, source_adventure=source_adventure)
        queries.create_node(driver, "Plotline", node.to_props())
        queries.create_relationship(driver, uid, source_adventure, "BELONGS_TO")

    return _ok(uid)


# ── Event ─────────────────────────────────────────────────────────────────────

def add_event(
    driver: Driver,
    uid: str,
    plotline_uid: str,
    name: str,
    summary: Optional[str] = None,
    event_type: Optional[str] = None,
    is_anchor: bool = False,
    is_historical: bool = False,
    source_adventure: Optional[str] = None,
) -> dict:
    """
    Create an Event and link it to a Plotline via PART_OF_PLOTLINE.
    NF-01: every Event must belong to at least one Plotline.
    """
    if queries.node_exists(driver, uid):
        return _err("DUPLICATE_UID", f"node '{uid}' already exists")
    if not queries.node_exists(driver, plotline_uid):
        return _err("NOT_FOUND", f"plotline '{plotline_uid}' not found")

    node = Event(uid=uid, name=name, summary=summary, event_type=event_type,
                 is_anchor=is_anchor, is_historical=is_historical,
                 source_adventure=source_adventure)
    queries.create_node(driver, "Event", node.to_props())
    queries.create_relationship(driver, uid, plotline_uid, "PART_OF_PLOTLINE")

    if source_adventure:
        queries.create_relationship(driver, uid, source_adventure, "BELONGS_TO")

    return _ok(uid)


def add_event_to_plotline(driver: Driver, event_uid: str, plotline_uid: str) -> dict:
    """Add an existing Event to an additional Plotline."""
    if not queries.node_exists(driver, event_uid):
        return _err("NOT_FOUND", f"event '{event_uid}' not found")
    if not queries.node_exists(driver, plotline_uid):
        return _err("NOT_FOUND", f"plotline '{plotline_uid}' not found")
    if queries.relationship_exists(driver, event_uid, plotline_uid, "PART_OF_PLOTLINE"):
        return _err("DUPLICATE_REL", "event already belongs to this plotline")
    queries.create_relationship(driver, event_uid, plotline_uid, "PART_OF_PLOTLINE")
    return _ok(event_uid)


# ── Choice ────────────────────────────────────────────────────────────────────

def add_choice(
    driver: Driver,
    uid: str,
    event_uid: str,
    prompt: str,
    summary: Optional[str] = None,
    condition: Optional[str] = None,
    condition_type: Optional[str] = None,
    source_adventure: Optional[str] = None,
) -> dict:
    """
    Create a Choice and link it to an Event via BRANCHES_INTO.
    NF-02: an Event may have zero or more outbound BRANCHES_INTO.
    """
    if queries.node_exists(driver, uid):
        return _err("DUPLICATE_UID", f"node '{uid}' already exists")
    if not queries.node_exists(driver, event_uid):
        return _err("NOT_FOUND", f"event '{event_uid}' not found")

    node = Choice(uid=uid, prompt=prompt, summary=summary, condition=condition,
                  condition_type=condition_type, source_adventure=source_adventure)
    queries.create_node(driver, "Choice", node.to_props())
    queries.create_relationship(driver, event_uid, uid, "BRANCHES_INTO")

    if source_adventure:
        queries.create_relationship(driver, uid, source_adventure, "BELONGS_TO")

    return _ok(uid)


# ── Outcome ───────────────────────────────────────────────────────────────────

def add_outcome(
    driver: Driver,
    uid: str,
    choice_uid: str,
    leads_to_event_uid: str,
    label_text: str,
    consequence_summary: Optional[str] = None,
    probability: Optional[float] = None,
    source_adventure: Optional[str] = None,
) -> dict:
    """
    Create an Outcome, link it to a Choice via HAS_OUTCOME,
    and link it to an Event via LEADS_TO.
    NF-03: a Choice must have at least one HAS_OUTCOME.
    NF-04: an Outcome must have exactly one LEADS_TO.
    """
    if queries.node_exists(driver, uid):
        return _err("DUPLICATE_UID", f"node '{uid}' already exists")
    if not queries.node_exists(driver, choice_uid):
        return _err("NOT_FOUND", f"choice '{choice_uid}' not found")
    if not queries.node_exists(driver, leads_to_event_uid):
        return _err("NOT_FOUND", f"event '{leads_to_event_uid}' not found")
    if probability is not None and not (0.0 <= probability <= 1.0):
        return _err("INVALID_PROBABILITY", "probability must be between 0.0 and 1.0")

    node = Outcome(uid=uid, label_text=label_text, consequence_summary=consequence_summary,
                   probability=probability, source_adventure=source_adventure)
    queries.create_node(driver, "Outcome", node.to_props())
    queries.create_relationship(driver, choice_uid, uid, "HAS_OUTCOME")
    queries.create_relationship(driver, uid, leads_to_event_uid, "LEADS_TO")

    if source_adventure:
        queries.create_relationship(driver, uid, source_adventure, "BELONGS_TO")

    return _ok(uid)


def link_outcome_to_event(driver: Driver, outcome_uid: str, event_uid: str) -> dict:
    """
    Point an existing Outcome at a different (or additional merge) Event.
    NF-05: an Event may be the target of LEADS_TO from multiple Outcomes (merge).
    """
    if not queries.node_exists(driver, outcome_uid):
        return _err("NOT_FOUND", f"outcome '{outcome_uid}' not found")
    if not queries.node_exists(driver, event_uid):
        return _err("NOT_FOUND", f"event '{event_uid}' not found")

    db = get_database()
    with driver.session(database=db) as session:
        # Remove old LEADS_TO first (NF-04: exactly one)
        session.run(
            "MATCH (o {uid: $uid})-[r:LEADS_TO]->() DELETE r",
            uid=outcome_uid,
        )
    queries.create_relationship(driver, outcome_uid, event_uid, "LEADS_TO")
    return _ok(outcome_uid)


# ── Causal links ──────────────────────────────────────────────────────────────

def add_causal_link(
    driver: Driver,
    from_event_uid: str,
    to_event_uid: str,
    condition: Optional[str] = None,
) -> dict:
    """
    Create a direct Event-[:CAUSES]->Event link.
    NF-06: an Event may have a direct CAUSES relationship to another Event.
    """
    if not queries.node_exists(driver, from_event_uid):
        return _err("NOT_FOUND", f"event '{from_event_uid}' not found")
    if not queries.node_exists(driver, to_event_uid):
        return _err("NOT_FOUND", f"event '{to_event_uid}' not found")
    if from_event_uid == to_event_uid:
        return _err("CYCLE", "an event cannot cause itself")

    props = {"condition": condition} if condition else {}
    queries.create_relationship(driver, from_event_uid, to_event_uid, "CAUSES", props)
    return {"from_uid": from_event_uid, "to_uid": to_event_uid, "status": "ok"}


# ── Narrative flow query ──────────────────────────────────────────────────────

def get_narrative_flow(
    driver: Driver,
    plotline_uid: str,
    include_disabled: bool = False,
) -> dict:
    """
    Return the full directed graph for a plotline, structured for Mermaid/Graphviz.
    NF-10: must return a structure renderable as a flowchart.
    """
    if not queries.node_exists(driver, plotline_uid):
        return _err("NOT_FOUND", f"plotline '{plotline_uid}' not found")

    db = get_database()
    disabled_filter = "" if include_disabled else "AND e.disabled = false"

    with driver.session(database=db) as session:
        # Collect all events in the plotline
        events_result = session.run(
            f"""
            MATCH (e:Event)-[:PART_OF_PLOTLINE]->(p {{uid: $uid}})
            WHERE true {disabled_filter}
            RETURN properties(e) AS props
            ORDER BY e.created_at
            """,
            uid=plotline_uid,
        )
        events = [_response(dict(r["props"])) for r in events_result]

        # Collect all choices branching from those events
        choices_result = session.run(
            f"""
            MATCH (e:Event)-[:PART_OF_PLOTLINE]->(p {{uid: $uid}})
            MATCH (e)-[:BRANCHES_INTO]->(c:Choice)
            WHERE true {disabled_filter} AND c.disabled = false
            RETURN properties(c) AS props, e.uid AS from_event
            """,
            uid=plotline_uid,
        )
        choices = [
            {**_response(dict(r["props"])), "_from_event": r["from_event"]}
            for r in choices_result
        ]

        # Collect all outcomes from those choices
        outcomes_result = session.run(
            f"""
            MATCH (e:Event)-[:PART_OF_PLOTLINE]->(p {{uid: $uid}})
            MATCH (e)-[:BRANCHES_INTO]->(c:Choice)-[:HAS_OUTCOME]->(o:Outcome)-[:LEADS_TO]->(target:Event)
            WHERE true {disabled_filter} AND c.disabled = false AND o.disabled = false
            RETURN properties(o) AS props, c.uid AS from_choice, target.uid AS leads_to
            """,
            uid=plotline_uid,
        )
        outcomes = [
            {**_response(dict(r["props"])), "_from_choice": r["from_choice"], "_leads_to": r["leads_to"]}
            for r in outcomes_result
        ]

        # Collect direct causal links between events
        causal_result = session.run(
            f"""
            MATCH (a:Event)-[:PART_OF_PLOTLINE]->(p {{uid: $uid}})
            MATCH (a)-[r:CAUSES]->(b:Event)
            WHERE true {disabled_filter} AND b.disabled = false
            RETURN a.uid AS from_uid, b.uid AS to_uid, r.condition AS condition
            """,
            uid=plotline_uid,
        )
        causal_links = [
            {k: v for k, v in {"from_uid": r["from_uid"], "to_uid": r["to_uid"],
                                "condition": r["condition"]}.items() if v is not None}
            for r in causal_result
        ]

    return {
        "plotline_uid": plotline_uid,
        "events": events,
        "choices": choices,
        "outcomes": outcomes,
        "causal_links": causal_links,
    }
