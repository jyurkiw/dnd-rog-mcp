"""Tool handlers: encounters -- combat, skill challenges, traps."""

from typing import Optional
from neo4j import Driver

from dnd_mcp.db import queries
from dnd_mcp.db.connection import get_database
from dnd_mcp.models.nodes import Combat, SkillChallenge, Trap


def _err(code, reason):
    return {"error": f"{code}: {reason}"}

def _ok(uid):
    return {"uid": uid, "status": "ok"}

def _response(props):
    return {k: v for k, v in props.items() if v is not None and v != []}


def _attach_encounter(driver, encounter_uid, attach_to_uid):
    db = get_database()
    with driver.session(database=db) as session:
        r = session.run("MATCH (n {uid: $uid}) RETURN labels(n) AS labels", uid=attach_to_uid).single()
        if r is None:
            return False
        labels = list(r["labels"])
    rel = "TRIGGERED_BY" if "Event" in labels else "LOCATED_IN"
    queries.create_relationship(driver, encounter_uid, attach_to_uid, rel)
    return True


def upsert_combat(driver, uid, source_adventure, name, attach_to_uid,
                  summary=None, cr=None, xp=None, terrain=None, tactics=None):
    if not queries.node_exists(driver, source_adventure):
        return _err("NOT_FOUND", f"adventure '{source_adventure}' not found")
    if not queries.node_exists(driver, attach_to_uid):
        return _err("NOT_FOUND", f"attach_to node '{attach_to_uid}' not found")
    if queries.node_exists(driver, uid):
        updates = {k: v for k, v in dict(name=name, summary=summary, cr=cr, xp=xp, terrain=terrain, tactics=tactics).items() if v is not None}
        queries.update_node(driver, uid, updates)
    else:
        node = Combat(uid=uid, name=name, summary=summary, cr=cr, xp=xp, terrain=terrain, tactics=tactics, source_adventure=source_adventure)
        queries.create_node(driver, "Combat", node.to_props())
        queries.create_relationship(driver, uid, source_adventure, "BELONGS_TO")
        _attach_encounter(driver, uid, attach_to_uid)
    return _ok(uid)


def add_combat_participant(driver, combat_uid, npc_uid):
    if not queries.node_exists(driver, combat_uid):
        return _err("NOT_FOUND", f"combat '{combat_uid}' not found")
    if not queries.node_exists(driver, npc_uid):
        return _err("NOT_FOUND", f"npc '{npc_uid}' not found")
    queries.create_relationship(driver, combat_uid, npc_uid, "PARTICIPANT_IN")
    return {"combat_uid": combat_uid, "npc_uid": npc_uid, "status": "ok"}


def upsert_skill_challenge(driver, uid, source_adventure, name, attach_to_uid,
                           summary=None, dc=None, skills_involved=None, consequences=None):
    if not queries.node_exists(driver, source_adventure):
        return _err("NOT_FOUND", f"adventure '{source_adventure}' not found")
    if not queries.node_exists(driver, attach_to_uid):
        return _err("NOT_FOUND", f"attach_to node '{attach_to_uid}' not found")
    if queries.node_exists(driver, uid):
        updates = {k: v for k, v in dict(name=name, summary=summary, dc=dc, skills_involved=skills_involved, consequences=consequences).items() if v is not None}
        queries.update_node(driver, uid, updates)
    else:
        node = SkillChallenge(uid=uid, name=name, summary=summary, dc=dc, skills_involved=skills_involved or [], consequences=consequences, source_adventure=source_adventure)
        queries.create_node(driver, "SkillChallenge", node.to_props())
        queries.create_relationship(driver, uid, source_adventure, "BELONGS_TO")
        _attach_encounter(driver, uid, attach_to_uid)
    return _ok(uid)


def upsert_trap(driver, uid, source_adventure, name, attach_to_uid,
                summary=None, dc=None, damage=None, trigger=None, reset=None):
    if not queries.node_exists(driver, source_adventure):
        return _err("NOT_FOUND", f"adventure '{source_adventure}' not found")
    if not queries.node_exists(driver, attach_to_uid):
        return _err("NOT_FOUND", f"attach_to node '{attach_to_uid}' not found")
    if queries.node_exists(driver, uid):
        updates = {k: v for k, v in dict(name=name, summary=summary, dc=dc, damage=damage, trigger=trigger, reset=reset).items() if v is not None}
        queries.update_node(driver, uid, updates)
    else:
        node = Trap(uid=uid, name=name, summary=summary, dc=dc, damage=damage, trigger=trigger, reset=reset, source_adventure=source_adventure)
        queries.create_node(driver, "Trap", node.to_props())
        queries.create_relationship(driver, uid, source_adventure, "BELONGS_TO")
        _attach_encounter(driver, uid, attach_to_uid)
    return _ok(uid)


def attach_encounter_to_location(driver, encounter_uid, location_uid):
    if not queries.node_exists(driver, encounter_uid):
        return _err("NOT_FOUND", f"encounter '{encounter_uid}' not found")
    if not queries.node_exists(driver, location_uid):
        return _err("NOT_FOUND", f"location '{location_uid}' not found")
    queries.create_relationship(driver, encounter_uid, location_uid, "LOCATED_IN")
    return {"encounter_uid": encounter_uid, "location_uid": location_uid, "status": "ok"}


def get_encounters_for_location(driver, location_uid, include_disabled=False):
    if not queries.node_exists(driver, location_uid):
        return _err("NOT_FOUND", f"location '{location_uid}' not found")
    db = get_database()
    df = "" if include_disabled else "AND enc.disabled = false"
    with driver.session(database=db) as session:
        result = session.run(f"MATCH (enc)-[:LOCATED_IN]->(loc {{uid: $uid}}) WHERE (enc:Combat OR enc:SkillChallenge OR enc:Trap) {df} RETURN properties(enc) AS props, labels(enc) AS labels", uid=location_uid)
        return [{**_response(dict(r["props"])), "label": next(l for l in r["labels"] if l not in ("BaseNode",))} for r in result]
