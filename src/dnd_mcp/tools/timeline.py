"""Tool handlers: timeline and history."""

from typing import Optional
from neo4j import Driver

from dnd_mcp.db import queries
from dnd_mcp.db.connection import get_database
from dnd_mcp.models.nodes import Timeline


def _err(code, reason):
    return {"error": f"{code}: {reason}"}

def _ok(uid):
    return {"uid": uid, "status": "ok"}

def _response(props):
    return {k: v for k, v in props.items() if v is not None and v != []}


def create_timeline(driver, uid, name, source_adventure=None, era=None, description=None):
    """TL-01: a Timeline is a named, ordered sequence of Event nodes."""
    if queries.node_exists(driver, uid):
        return _err("DUPLICATE_UID", f"node '{uid}' already exists")
    node = Timeline(uid=uid, name=name, era=era, description=description,
                    source_adventure=source_adventure)
    queries.create_node(driver, "Timeline", node.to_props())
    if source_adventure:
        queries.create_relationship(driver, uid, source_adventure, "BELONGS_TO")
    return _ok(uid)


def place_event_on_timeline(driver, event_uid, timeline_uid, precedes_uid=None):
    """
    Place an Event on a Timeline.
    TL-02: an Event may belong to zero or more Timelines.
    TL-03: ordering stored on the PRECEDES relationship.
    """
    if not queries.node_exists(driver, event_uid):
        return _err("NOT_FOUND", f"event '{event_uid}' not found")
    if not queries.node_exists(driver, timeline_uid):
        return _err("NOT_FOUND", f"timeline '{timeline_uid}' not found")
    queries.create_relationship(driver, event_uid, timeline_uid, "ON_TIMELINE")
    if precedes_uid:
        if not queries.node_exists(driver, precedes_uid):
            return _err("NOT_FOUND", f"event '{precedes_uid}' not found")
        queries.create_relationship(driver, event_uid, precedes_uid, "PRECEDES")
    return _ok(event_uid)


def get_timeline(driver, timeline_uid, include_disabled=False):
    """
    Return events on a timeline in chronological order.
    TL-05: get_timeline must return events in chronological order.
    """
    if not queries.node_exists(driver, timeline_uid):
        return _err("NOT_FOUND", f"timeline '{timeline_uid}' not found")

    db = get_database()
    df = "" if include_disabled else "AND e.disabled = false"
    with driver.session(database=db) as session:
        # Topological sort via PRECEDES chain
        result = session.run(f"""
            MATCH (e:Event)-[:ON_TIMELINE]->(t {{uid: $uid}})
            WHERE true {df}
            OPTIONAL MATCH (e)-[:PRECEDES]->(next:Event)
            RETURN properties(e) AS props, next.uid AS next_uid
            ORDER BY e.created_at
        """, uid=timeline_uid)
        rows = [{"event": _response(dict(r["props"])), "precedes": r["next_uid"]} for r in result]
    return {"timeline_uid": timeline_uid, "events": rows}


def get_history_for(driver, entity_uid, include_disabled=False):
    """
    Return all events involving an entity, ordered by timeline position.
    TL-06: get_history_for must return all events involving an entity.
    """
    if not queries.node_exists(driver, entity_uid):
        return _err("NOT_FOUND", f"entity '{entity_uid}' not found")

    db = get_database()
    df = "" if include_disabled else "AND e.disabled = false"
    with driver.session(database=db) as session:
        result = session.run(f"""
            MATCH (e:Event)-[:INVOLVES]->(entity {{uid: $uid}})
            WHERE true {df}
            OPTIONAL MATCH (e)-[:ON_TIMELINE]->(t:Timeline)
            RETURN properties(e) AS props, t.uid AS timeline_uid
            ORDER BY e.created_at
        """, uid=entity_uid)
        return [{"event": _response(dict(r["props"])), "timeline_uid": r["timeline_uid"]} for r in result]
