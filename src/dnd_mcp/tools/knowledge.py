"""Tool handlers: world knowledge — rumors and facts."""

from typing import Optional
from neo4j import Driver

from dnd_mcp.db import queries
from dnd_mcp.db.connection import get_database
from dnd_mcp.models.nodes import Rumor, Fact


def _err(code: str, reason: str) -> dict:
    return {"error": f"{code}: {reason}"}


def _ok(uid: str) -> dict:
    return {"uid": uid, "status": "ok"}


def _response(props: dict) -> dict:
    return {k: v for k, v in props.items() if v is not None and v != []}


# ── Rumors ────────────────────────────────────────────────────────────────────

def add_rumor(
    driver: Driver,
    uid: str,
    content: str,
    entity_uids: list,
    is_true: Optional[bool] = None,
    spread: Optional[str] = None,
    source_npc: Optional[str] = None,
    source_adventure: Optional[str] = None,
) -> dict:
    """
    Create a Rumor and attach it to one or more entities via KNOWS_RUMOR.
    WK-01: a Rumor must be attached to at least one NPC, Location, or Faction.
    WK-02: is_true may be true, false, or null.
    """
    if not entity_uids:
        return _err("MISSING_REQUIRED", "entity_uids must contain at least one uid")
    if queries.node_exists(driver, uid):
        return _err("DUPLICATE_UID", f"node '{uid}' already exists")

    for entity_uid in entity_uids:
        if not queries.node_exists(driver, entity_uid):
            return _err("NOT_FOUND", f"entity '{entity_uid}' not found")

    node = Rumor(uid=uid, content=content, is_true=is_true, spread=spread,
                 source_npc=source_npc, source_adventure=source_adventure)
    queries.create_node(driver, "Rumor", node.to_props())

    for entity_uid in entity_uids:
        queries.create_relationship(driver, entity_uid, uid, "KNOWS_RUMOR")

    if source_adventure:
        queries.create_relationship(driver, uid, source_adventure, "BELONGS_TO")

    return _ok(uid)


def get_rumors_for(
    driver: Driver,
    entity_uid: str,
    include_disabled: bool = False,
) -> list | dict:
    """
    Return all Rumors attached to an entity.
    WK-04: rumors must be queryable by the entity they are attached to.
    """
    if not queries.node_exists(driver, entity_uid):
        return _err("NOT_FOUND", f"entity '{entity_uid}' not found")

    db = get_database()
    disabled_filter = "" if include_disabled else "AND r.disabled = false"
    with driver.session(database=db) as session:
        result = session.run(
            f"MATCH (e {{uid: $uid}})-[:KNOWS_RUMOR]->(r:Rumor) WHERE true {disabled_filter} RETURN properties(r) AS props",
            uid=entity_uid,
        )
        return [_response(dict(rec["props"])) for rec in result]


# ── Facts ─────────────────────────────────────────────────────────────────────

def add_fact(
    driver: Driver,
    uid: str,
    content: str,
    entity_uids: list,
    reliability: str = "established",
    source_file: Optional[str] = None,
    source_excerpt_line: Optional[int] = None,
    source_adventure: Optional[str] = None,
) -> dict:
    """
    Create a Fact and attach it to one or more entities via HAS_FACT.
    WK-03: reliability must be established, rumored, or contradicted.
    """
    if not entity_uids:
        return _err("MISSING_REQUIRED", "entity_uids must contain at least one uid")
    if reliability not in ("established", "rumored", "contradicted"):
        return _err("INVALID_RELIABILITY", "reliability must be established, rumored, or contradicted")
    if queries.node_exists(driver, uid):
        return _err("DUPLICATE_UID", f"node '{uid}' already exists")

    for entity_uid in entity_uids:
        if not queries.node_exists(driver, entity_uid):
            return _err("NOT_FOUND", f"entity '{entity_uid}' not found")

    node = Fact(uid=uid, content=content, reliability=reliability,
                source_file=source_file, source_excerpt_line=source_excerpt_line,
                source_adventure=source_adventure)
    queries.create_node(driver, "Fact", node.to_props())

    for entity_uid in entity_uids:
        queries.create_relationship(driver, entity_uid, uid, "HAS_FACT")

    if source_adventure:
        queries.create_relationship(driver, uid, source_adventure, "BELONGS_TO")

    return _ok(uid)


def get_facts_for(
    driver: Driver,
    entity_uid: str,
    include_disabled: bool = False,
) -> list | dict:
    """Return all Facts attached to an entity."""
    if not queries.node_exists(driver, entity_uid):
        return _err("NOT_FOUND", f"entity '{entity_uid}' not found")

    db = get_database()
    disabled_filter = "" if include_disabled else "AND f.disabled = false"
    with driver.session(database=db) as session:
        result = session.run(
            f"MATCH (e {{uid: $uid}})-[:HAS_FACT]->(f:Fact) WHERE true {disabled_filter} RETURN properties(f) AS props",
            uid=entity_uid,
        )
        return [_response(dict(rec["props"])) for rec in result]


# ── who_knows_what ────────────────────────────────────────────────────────────

def who_knows_what(
    driver: Driver,
    knowledge_uid: str,
    include_disabled: bool = False,
) -> list | dict:
    """
    Return all NPCs with a path to a given Rumor or Fact.
    WK-06: who_knows_what must return all NPCs with a path to the knowledge node.
    """
    if not queries.node_exists(driver, knowledge_uid):
        return _err("NOT_FOUND", f"knowledge node '{knowledge_uid}' not found")

    db = get_database()
    disabled_filter = "" if include_disabled else "AND npc.disabled = false"
    with driver.session(database=db) as session:
        result = session.run(
            f"""
            MATCH (npc)-[:KNOWS_RUMOR|HAS_FACT]->(k {{uid: $uid}})
            WHERE (npc:NPC OR npc:NPCContext OR npc:GlobalNPC) {disabled_filter}
            RETURN npc.uid AS uid, labels(npc) AS labels
            """,
            uid=knowledge_uid,
        )
        return [{"uid": r["uid"], "labels": list(r["labels"])} for r in result]
