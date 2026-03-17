"""Tool handlers: global entity management + adventure-scoped entity CRUD."""

from typing import Optional
from neo4j import Driver

from dnd_mcp.db import queries
from dnd_mcp.models.nodes import (
    GlobalNPC, GlobalLocation, GlobalItem, GlobalFaction,
    NPCContext,
    NPC, Location, Item, Faction,
)


def _err(code: str, reason: str) -> dict:
    return {"error": f"{code}: {reason}"}


def _ok(uid: str) -> dict:
    return {"uid": uid, "status": "ok"}


def _response(props: dict) -> dict:
    return {k: v for k, v in props.items() if v is not None and v != []}


# ── Global Entity CRUD ────────────────────────────────────────────────────────

def create_global_npc(
    driver: Driver,
    uid: str,
    canonical_name: str,
    summary: str,
    source: str,
    aliases: Optional[list] = None,
    is_canonical: bool = True,
) -> dict:
    if not uid or not canonical_name:
        return _err("MISSING_REQUIRED", "uid and canonical_name are required")
    if queries.node_exists(driver, uid):
        return _err("DUPLICATE_UID", f"node '{uid}' already exists")

    node = GlobalNPC(
        uid=uid,
        canonical_name=canonical_name,
        summary=summary,
        source=source,
        aliases=aliases or [],
        is_canonical=is_canonical,
    )
    queries.create_node(driver, "GlobalNPC", node.to_props())
    return _ok(uid)


def create_global_location(
    driver: Driver,
    uid: str,
    canonical_name: str,
    summary: str,
    source: str,
    region: Optional[str] = None,
    type: Optional[str] = None,
    is_canonical: bool = True,
) -> dict:
    if not uid or not canonical_name:
        return _err("MISSING_REQUIRED", "uid and canonical_name are required")
    if queries.node_exists(driver, uid):
        return _err("DUPLICATE_UID", f"node '{uid}' already exists")

    node = GlobalLocation(
        uid=uid,
        canonical_name=canonical_name,
        summary=summary,
        source=source,
        region=region,
        type=type,
        is_canonical=is_canonical,
    )
    queries.create_node(driver, "GlobalLocation", node.to_props())
    return _ok(uid)


def create_global_item(
    driver: Driver,
    uid: str,
    canonical_name: str,
    summary: str,
    source: str,
    rarity: Optional[str] = None,
    is_canonical: bool = True,
) -> dict:
    if not uid or not canonical_name:
        return _err("MISSING_REQUIRED", "uid and canonical_name are required")
    if queries.node_exists(driver, uid):
        return _err("DUPLICATE_UID", f"node '{uid}' already exists")

    node = GlobalItem(
        uid=uid,
        canonical_name=canonical_name,
        summary=summary,
        source=source,
        rarity=rarity,
        is_canonical=is_canonical,
    )
    queries.create_node(driver, "GlobalItem", node.to_props())
    return _ok(uid)


def create_global_faction(
    driver: Driver,
    uid: str,
    canonical_name: str,
    summary: str,
    source: str,
    alignment: Optional[str] = None,
    is_canonical: bool = True,
) -> dict:
    if not uid or not canonical_name:
        return _err("MISSING_REQUIRED", "uid and canonical_name are required")
    if queries.node_exists(driver, uid):
        return _err("DUPLICATE_UID", f"node '{uid}' already exists")

    node = GlobalFaction(
        uid=uid,
        canonical_name=canonical_name,
        summary=summary,
        source=source,
        alignment=alignment,
        is_canonical=is_canonical,
    )
    queries.create_node(driver, "GlobalFaction", node.to_props())
    return _ok(uid)


def get_global_entity(
    driver: Driver,
    uid: str,
    include_disabled: bool = False,
) -> dict:
    """Fetch any global entity by uid (searches GlobalNPC/Location/Item/Faction)."""
    for label in ("GlobalNPC", "GlobalLocation", "GlobalItem", "GlobalFaction"):
        props = queries.get_node_by_label(driver, label, uid, include_disabled)
        if props is not None:
            return _response(props)
    return _err("NOT_FOUND", f"global entity '{uid}' not found")


def list_global_entities(
    driver: Driver,
    entity_type: Optional[str] = None,
    include_disabled: bool = False,
    verbose: bool = False,
) -> list | dict:
    """
    List global entities.
    entity_type: one of npc, location, item, faction (None = all types).
    """
    label_map = {
        "npc": "GlobalNPC",
        "location": "GlobalLocation",
        "item": "GlobalItem",
        "faction": "GlobalFaction",
    }

    if entity_type is not None:
        label = label_map.get(entity_type.lower())
        if label is None:
            return _err("INVALID_TYPE", "entity_type must be npc, location, item, or faction")
        results = queries.list_nodes(driver, label, include_disabled=include_disabled, verbose=verbose)
        return [_response(p) for p in results] if verbose else results

    combined = []
    for label in label_map.values():
        results = queries.list_nodes(driver, label, include_disabled=include_disabled, verbose=verbose)
        if verbose:
            combined.extend([_response(p) for p in results])
        else:
            combined.extend(results)
    return combined


# ── Context Management ────────────────────────────────────────────────────────

def add_entity_to_adventure(
    driver: Driver,
    global_uid: str,
    adventure_uid: str,
    context_uid: str,
    role: Optional[str] = None,
    status: Optional[str] = None,
    summary: Optional[str] = None,
    first_appears: Optional[str] = None,
    last_known_location: Optional[str] = None,
) -> dict:
    """
    Bridge a GlobalNPC into an adventure via an NPCContext node.
    Creates: NPCContext, GlobalNPC-[:REPRESENTED_BY]->NPCContext,
             NPCContext-[:WITHIN_ADVENTURE]->Adventure,
             GlobalNPC-[:APPEARS_IN_ADVENTURE]->Adventure.
    """
    if not queries.node_exists(driver, global_uid):
        return _err("NOT_FOUND", f"global entity '{global_uid}' not found")
    if not queries.node_exists(driver, adventure_uid):
        return _err("NOT_FOUND", f"adventure '{adventure_uid}' not found")
    if queries.node_exists(driver, context_uid):
        return _err("DUPLICATE_UID", f"node '{context_uid}' already exists")

    # Check no existing context for this (global, adventure) pair
    db = queries.get_database()
    with driver.session(database=db) as session:
        result = session.run(
            """
            MATCH (g {uid: $g_uid})-[:REPRESENTED_BY]->(ctx)-[:WITHIN_ADVENTURE]->(a {uid: $adv_uid})
            RETURN count(ctx) AS c
            """,
            g_uid=global_uid,
            adv_uid=adventure_uid,
        )
        record = result.single()
        if record and record["c"] > 0:
            return _err(
                "DUPLICATE_CONTEXT",
                f"entity '{global_uid}' already has a context in adventure '{adventure_uid}'",
            )

    node = NPCContext(
        uid=context_uid,
        role=role,
        status=status,
        summary=summary,
        first_appears=first_appears,
        last_known_location=last_known_location,
    )
    queries.create_node(driver, "NPCContext", node.to_props())
    queries.create_relationship(driver, global_uid, context_uid, "REPRESENTED_BY")
    queries.create_relationship(driver, context_uid, adventure_uid, "WITHIN_ADVENTURE")
    queries.create_relationship(driver, global_uid, adventure_uid, "APPEARS_IN_ADVENTURE")
    return _ok(context_uid)


def update_entity_context(
    driver: Driver,
    context_uid: str,
    role: Optional[str] = None,
    status: Optional[str] = None,
    summary: Optional[str] = None,
    first_appears: Optional[str] = None,
    last_known_location: Optional[str] = None,
) -> dict:
    """Update mutable fields on an NPCContext node."""
    updates: dict = {}
    if role is not None:
        updates["role"] = role
    if status is not None:
        updates["status"] = status
    if summary is not None:
        updates["summary"] = summary
    if first_appears is not None:
        updates["first_appears"] = first_appears
    if last_known_location is not None:
        updates["last_known_location"] = last_known_location

    if not updates:
        return _err("NO_UPDATES", "no fields provided to update")

    result = queries.update_node(driver, context_uid, updates)
    if result is None:
        return _err("NOT_FOUND", f"context '{context_uid}' not found")
    return _ok(context_uid)


def get_entity_in_adventure(
    driver: Driver,
    global_uid: str,
    adventure_uid: str,
    include_disabled: bool = False,
) -> dict:
    """Return the NPCContext for a global entity within a specific adventure."""
    db = queries.get_database()
    disabled_filter = "" if include_disabled else "AND ctx.disabled = false"
    with driver.session(database=db) as session:
        result = session.run(
            f"""
            MATCH (g {{uid: $g_uid}})-[:REPRESENTED_BY]->(ctx)-[:WITHIN_ADVENTURE]->(a {{uid: $adv_uid}})
            WHERE true {disabled_filter}
            RETURN properties(ctx) AS p
            """,
            g_uid=global_uid,
            adv_uid=adventure_uid,
        )
        record = result.single()
        if record is None:
            return _err("NOT_FOUND", f"no context for '{global_uid}' in adventure '{adventure_uid}'")
        return _response(dict(record["p"]))


# ── Adventure-Scoped Entity CRUD ──────────────────────────────────────────────

def _upsert_scoped(driver: Driver, label: str, uid: str, source_adventure: str, props: dict) -> dict:
    """Create or update an adventure-scoped entity."""
    if not queries.node_exists(driver, source_adventure):
        return _err("NOT_FOUND", f"adventure '{source_adventure}' not found")

    if queries.node_exists(driver, uid):
        queries.update_node(driver, uid, props)
    else:
        props["uid"] = uid
        props["source_adventure"] = source_adventure
        queries.create_node(driver, label, props)
        queries.create_relationship(driver, uid, source_adventure, "BELONGS_TO")

    return _ok(uid)


def upsert_npc(
    driver: Driver,
    uid: str,
    source_adventure: str,
    name: str,
    summary: Optional[str] = None,
    aliases: Optional[list] = None,
    role: Optional[str] = None,
    status: Optional[str] = None,
) -> dict:
    node = NPC(uid=uid, name=name, source_adventure=source_adventure,
               summary=summary, aliases=aliases or [], role=role, status=status)
    props = node.to_props()
    props.pop("uid", None)
    props.pop("source_adventure", None)
    return _upsert_scoped(driver, "NPC", uid, source_adventure, props)


def upsert_location(
    driver: Driver,
    uid: str,
    source_adventure: str,
    name: str,
    summary: Optional[str] = None,
    type: Optional[str] = None,
    region: Optional[str] = None,
) -> dict:
    node = Location(uid=uid, name=name, source_adventure=source_adventure,
                    summary=summary, type=type, region=region)
    props = node.to_props()
    props.pop("uid", None)
    props.pop("source_adventure", None)
    return _upsert_scoped(driver, "Location", uid, source_adventure, props)


def upsert_item(
    driver: Driver,
    uid: str,
    source_adventure: str,
    name: str,
    summary: Optional[str] = None,
    rarity: Optional[str] = None,
) -> dict:
    node = Item(uid=uid, name=name, source_adventure=source_adventure,
                summary=summary, rarity=rarity)
    props = node.to_props()
    props.pop("uid", None)
    props.pop("source_adventure", None)
    return _upsert_scoped(driver, "Item", uid, source_adventure, props)


def upsert_faction(
    driver: Driver,
    uid: str,
    source_adventure: str,
    name: str,
    summary: Optional[str] = None,
    alignment: Optional[str] = None,
) -> dict:
    node = Faction(uid=uid, name=name, source_adventure=source_adventure,
                   summary=summary, alignment=alignment)
    props = node.to_props()
    props.pop("uid", None)
    props.pop("source_adventure", None)
    return _upsert_scoped(driver, "Faction", uid, source_adventure, props)


def get_entity(
    driver: Driver,
    uid: str,
    include_disabled: bool = False,
) -> dict:
    """Fetch any adventure-scoped entity by uid."""
    for label in ("NPC", "Location", "Item", "Faction"):
        props = queries.get_node_by_label(driver, label, uid, include_disabled)
        if props is not None:
            return _response(props)
    return _err("NOT_FOUND", f"entity '{uid}' not found")


def list_entities(
    driver: Driver,
    source_adventure: str,
    entity_type: Optional[str] = None,
    include_disabled: bool = False,
    verbose: bool = False,
) -> list | dict:
    """
    List adventure-scoped entities for a given adventure.
    entity_type: one of npc, location, item, faction (None = all).
    """
    label_map = {
        "npc": "NPC",
        "location": "Location",
        "item": "Item",
        "faction": "Faction",
    }

    filters = {"source_adventure": source_adventure}

    if entity_type is not None:
        label = label_map.get(entity_type.lower())
        if label is None:
            return _err("INVALID_TYPE", "entity_type must be npc, location, item, or faction")
        results = queries.list_nodes(driver, label, filters=filters,
                                     include_disabled=include_disabled, verbose=verbose)
        return [_response(p) for p in results] if verbose else results

    combined = []
    for label in label_map.values():
        results = queries.list_nodes(driver, label, filters=filters,
                                     include_disabled=include_disabled, verbose=verbose)
        if verbose:
            combined.extend([_response(p) for p in results])
        else:
            combined.extend(results)
    return combined


# ── Promote to global ─────────────────────────────────────────────────────────

def promote_to_global(
    driver: Driver,
    uid: str,
    canonical_name: str,
    source: str,
    is_canonical: bool = True,
) -> dict:
    """
    Promote an adventure-scoped NPC/Location/Item/Faction to a Global node.
    The original node's label is changed and source_adventure is removed.
    BELONGS_TO relationship to the adventure is replaced with APPEARS_IN_ADVENTURE.
    """
    label_map = {
        "NPC": "GlobalNPC",
        "Location": "GlobalLocation",
        "Item": "GlobalItem",
        "Faction": "GlobalFaction",
    }
    current_label = None
    for label in label_map:
        if queries.get_node_by_label(driver, label, uid) is not None:
            current_label = label
            break

    if current_label is None:
        return _err("NOT_FOUND", f"adventure-scoped entity '{uid}' not found")

    new_label = label_map[current_label]
    db = queries.get_database()

    with driver.session(database=db) as session:
        session.run(
            f"""
            MATCH (n:{current_label} {{uid: $uid}})
            REMOVE n:{current_label}
            SET n:{new_label}
            SET n.canonical_name = $canonical_name,
                n.source = $source,
                n.is_canonical = $is_canonical,
                n.tier = 'global'
            REMOVE n.source_adventure
            """,
            uid=uid,
            canonical_name=canonical_name,
            source=source,
            is_canonical=is_canonical,
        )
        session.run(
            """
            MATCH (n {uid: $uid})-[r:BELONGS_TO]->(a:Adventure)
            CREATE (n)-[:APPEARS_IN_ADVENTURE]->(a)
            DELETE r
            """,
            uid=uid,
        )

    return _ok(uid)
