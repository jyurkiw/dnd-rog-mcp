"""Tool handlers: boxed text sequences."""

from typing import Optional
from neo4j import Driver

from dnd_mcp.db import queries
from dnd_mcp.db.connection import get_database
from dnd_mcp.models.nodes import BoxedTextSequence, BoxedText


def _err(code, reason):
    return {"error": f"{code}: {reason}"}

def _ok(uid):
    return {"uid": uid, "status": "ok"}

def _response(props):
    return {k: v for k, v in props.items() if v is not None and v != []}


def add_boxed_text_sequence(driver, uid, name, entity_uid, source_adventure=None,
                             summary=None, context=None):
    """BT-04: a BoxedTextSequence groups related BoxedText nodes with an OPENS_WITH entry point."""
    if queries.node_exists(driver, uid):
        return _err("DUPLICATE_UID", f"node '{uid}' already exists")
    if not queries.node_exists(driver, entity_uid):
        return _err("NOT_FOUND", f"entity '{entity_uid}' not found")
    node = BoxedTextSequence(uid=uid, name=name, summary=summary, context=context,
                              source_adventure=source_adventure)
    queries.create_node(driver, "BoxedTextSequence", node.to_props())
    queries.create_relationship(driver, entity_uid, uid, "HAS_BOXED_TEXT_SEQUENCE")
    if source_adventure:
        queries.create_relationship(driver, uid, source_adventure, "BELONGS_TO")
    return _ok(uid)


def add_boxed_text(driver, uid, sequence_uid, trigger_summary, content_summary,
                    is_opener=False, tone=None, sequence_position=None,
                    is_conditional=False, source_adventure=None):
    """
    BT-01: stores trigger summary, content summary, tone, sequence_position only.
    BT-07: a BoxedText without a FileRef is valid (planned but unwritten).
    """
    if queries.node_exists(driver, uid):
        return _err("DUPLICATE_UID", f"node '{uid}' already exists")
    if not queries.node_exists(driver, sequence_uid):
        return _err("NOT_FOUND", f"sequence '{sequence_uid}' not found")
    node = BoxedText(uid=uid, trigger_summary=trigger_summary, content_summary=content_summary,
                      tone=tone, sequence_position=sequence_position,
                      is_conditional=is_conditional, source_adventure=source_adventure)
    queries.create_node(driver, "BoxedText", node.to_props())
    if is_opener:
        queries.create_relationship(driver, sequence_uid, uid, "OPENS_WITH")
    else:
        queries.create_relationship(driver, sequence_uid, uid, "HAS_BOXED_TEXT")
    if source_adventure:
        queries.create_relationship(driver, uid, source_adventure, "BELONGS_TO")
    return _ok(uid)


def link_boxed_text(driver, from_uid, to_uid, condition=None, condition_type=None):
    """
    BT-05: FOLLOWED_BY must carry condition (nullable) and condition_type.
    BT-09: dependency relationships created automatically when condition references an entity.
    """
    if not queries.node_exists(driver, from_uid):
        return _err("NOT_FOUND", f"boxed_text '{from_uid}' not found")
    if not queries.node_exists(driver, to_uid):
        return _err("NOT_FOUND", f"boxed_text '{to_uid}' not found")

    props = {}
    if condition is not None:
        props["condition"] = condition
    if condition_type is not None:
        props["condition_type"] = condition_type

    queries.create_relationship(driver, from_uid, to_uid, "FOLLOWED_BY", props)

    # BT-09: auto-create dependency relationship if condition references a known entity
    if condition and ":" in condition:
        _create_condition_dependency(driver, from_uid, condition, condition_type)

    return _ok(from_uid)


def _create_condition_dependency(driver, bt_uid, condition, condition_type):
    """Parse condition string and create a dependency relationship to the referenced entity."""
    try:
        parts = condition.split(":")
        if len(parts) < 2:
            return
        ref_uid = parts[1]
        if not queries.node_exists(driver, ref_uid):
            return
        rel_map = {
            "event_flag": "DEPENDS_ON_EVENT",
            "possession": "DEPENDS_ON_ITEM",
            "choice_made": "DEPENDS_ON_CHOICE",
        }
        rel = rel_map.get(condition_type)
        if rel:
            queries.create_relationship(driver, bt_uid, ref_uid, rel)
    except Exception:
        pass  # dependency creation is best-effort


def add_alternative_boxed_text(driver, uid_a, uid_b, reason):
    """BT-06: mutually exclusive variants linked by ALTERNATIVE_TO with a reason."""
    if not queries.node_exists(driver, uid_a):
        return _err("NOT_FOUND", f"boxed_text '{uid_a}' not found")
    if not queries.node_exists(driver, uid_b):
        return _err("NOT_FOUND", f"boxed_text '{uid_b}' not found")
    queries.create_relationship(driver, uid_a, uid_b, "ALTERNATIVE_TO", {"reason": reason})
    return {"uid_a": uid_a, "uid_b": uid_b, "status": "ok"}


def get_boxed_text_sequence(driver, sequence_uid, include_disabled=False):
    """
    BT-10: get_boxed_text_sequence must return the full sequence graph.
    """
    if not queries.node_exists(driver, sequence_uid):
        return _err("NOT_FOUND", f"sequence '{sequence_uid}' not found")

    db = get_database()
    df = "" if include_disabled else "AND bt.disabled = false"
    with driver.session(database=db) as session:
        nodes_result = session.run(f"""
            MATCH (seq {{uid: $uid}})-[:OPENS_WITH|HAS_BOXED_TEXT]->(bt:BoxedText)
            WHERE true {df}
            RETURN properties(bt) AS props
        """, uid=sequence_uid)
        nodes = [_response(dict(r["props"])) for r in nodes_result]

        edges_result = session.run(f"""
            MATCH (seq {{uid: $uid}})-[:OPENS_WITH|HAS_BOXED_TEXT]->(a:BoxedText)-[r:FOLLOWED_BY|ALTERNATIVE_TO]->(b:BoxedText)
            WHERE true {df} AND b.disabled = false
            RETURN a.uid AS from_uid, b.uid AS to_uid, type(r) AS rel_type, properties(r) AS props
        """, uid=sequence_uid)
        edges = [
            {k: v for k, v in {
                "from_uid": r["from_uid"], "to_uid": r["to_uid"],
                "rel_type": r["rel_type"], **dict(r["props"])
            }.items() if v is not None}
            for r in edges_result
        ]

    return {"sequence_uid": sequence_uid, "nodes": nodes, "edges": edges}


def list_unwritten_boxed_text(driver, source_adventure=None, include_disabled=False):
    """
    BT-08: BoxedText nodes without a FileRef must be listable as a prose writing backlog.
    """
    db = get_database()
    df = "" if include_disabled else "AND bt.disabled = false"
    adv_filter = "AND bt.source_adventure = $adv" if source_adventure else ""
    params = {"adv": source_adventure} if source_adventure else {}
    with driver.session(database=db) as session:
        result = session.run(f"""
            MATCH (bt:BoxedText)
            WHERE true {df} {adv_filter}
            AND NOT (bt)-[:HAS_FILE]->(:FileRef)
            RETURN properties(bt) AS props
            ORDER BY bt.created_at
        """, **params)
        return [_response(dict(r["props"])) for r in result]
