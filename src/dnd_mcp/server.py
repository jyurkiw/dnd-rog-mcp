"""MCP server wiring. Registers tool functions as MCP tools. No business logic here."""

import json
import logging
import os
from typing import Optional

from mcp.server.fastmcp import FastMCP

from dnd_mcp.db.connection import get_driver
from dnd_mcp.tools import adventure as adv
from dnd_mcp.tools import entities as ent

logger = logging.getLogger(__name__)

mcp = FastMCP("dnd-rog-mcp")


def _json(obj) -> str:
    return json.dumps(obj, ensure_ascii=False)


# ── Adventure Management ──────────────────────────────────────────────────────

@mcp.tool()
def create_adventure(
    uid: str,
    name: str,
    status: str = "draft",
    setting: Optional[str] = None,
    tags: Optional[list] = None,
    summary: Optional[str] = None,
) -> str:
    """Create a new Adventure node."""
    with get_driver() as driver:
        return _json(adv.create_adventure(driver, uid, name, status, setting, tags, summary))


@mcp.tool()
def get_adventure(uid: str, include_disabled: bool = False) -> str:
    """Fetch an Adventure node by uid."""
    with get_driver() as driver:
        return _json(adv.get_adventure(driver, uid, include_disabled))


@mcp.tool()
def list_adventures(include_disabled: bool = False, verbose: bool = False) -> str:
    """List all Adventure nodes. Returns uids by default; full properties when verbose=True."""
    with get_driver() as driver:
        return _json(adv.list_adventures(driver, include_disabled, verbose))


@mcp.tool()
def update_adventure(
    uid: str,
    name: Optional[str] = None,
    status: Optional[str] = None,
    setting: Optional[str] = None,
    tags: Optional[list] = None,
    summary: Optional[str] = None,
) -> str:
    """Update mutable fields on an existing Adventure."""
    with get_driver() as driver:
        return _json(adv.update_adventure(driver, uid, name, status, setting, tags, summary))


@mcp.tool()
def link_adventures(
    from_uid: str,
    to_uid: str,
    rel_type: str = "RELATED_TO",
    props: Optional[dict] = None,
) -> str:
    """Create a relationship between two Adventure nodes."""
    with get_driver() as driver:
        return _json(adv.link_adventures(driver, from_uid, to_uid, rel_type, props))


# ── Global Entity Management ──────────────────────────────────────────────────

@mcp.tool()
def create_global_npc(
    uid: str,
    canonical_name: str,
    summary: str,
    source: str,
    aliases: Optional[list] = None,
    is_canonical: bool = True,
) -> str:
    """Create a canonical NPC entity."""
    with get_driver() as driver:
        return _json(ent.create_global_npc(driver, uid, canonical_name, summary, source, aliases, is_canonical))


@mcp.tool()
def create_global_location(
    uid: str,
    canonical_name: str,
    summary: str,
    source: str,
    region: Optional[str] = None,
    type: Optional[str] = None,
    is_canonical: bool = True,
) -> str:
    """Create a canonical Location entity."""
    with get_driver() as driver:
        return _json(ent.create_global_location(driver, uid, canonical_name, summary, source, region, type, is_canonical))


@mcp.tool()
def create_global_item(
    uid: str,
    canonical_name: str,
    summary: str,
    source: str,
    rarity: Optional[str] = None,
    is_canonical: bool = True,
) -> str:
    """Create a canonical Item entity."""
    with get_driver() as driver:
        return _json(ent.create_global_item(driver, uid, canonical_name, summary, source, rarity, is_canonical))


@mcp.tool()
def create_global_faction(
    uid: str,
    canonical_name: str,
    summary: str,
    source: str,
    alignment: Optional[str] = None,
    is_canonical: bool = True,
) -> str:
    """Create a canonical Faction entity."""
    with get_driver() as driver:
        return _json(ent.create_global_faction(driver, uid, canonical_name, summary, source, alignment, is_canonical))


@mcp.tool()
def get_global_entity(uid: str, include_disabled: bool = False) -> str:
    """Fetch any global entity (NPC/Location/Item/Faction) by uid."""
    with get_driver() as driver:
        return _json(ent.get_global_entity(driver, uid, include_disabled))


@mcp.tool()
def list_global_entities(
    entity_type: Optional[str] = None,
    include_disabled: bool = False,
    verbose: bool = False,
) -> str:
    """List global entities. entity_type: npc, location, item, faction (omit for all)."""
    with get_driver() as driver:
        return _json(ent.list_global_entities(driver, entity_type, include_disabled, verbose))


# ── Context Management ────────────────────────────────────────────────────────

@mcp.tool()
def add_entity_to_adventure(
    global_uid: str,
    adventure_uid: str,
    context_uid: str,
    role: Optional[str] = None,
    status: Optional[str] = None,
    summary: Optional[str] = None,
    first_appears: Optional[str] = None,
    last_known_location: Optional[str] = None,
) -> str:
    """Bridge a global entity into an adventure via an NPCContext node."""
    with get_driver() as driver:
        return _json(ent.add_entity_to_adventure(
            driver, global_uid, adventure_uid, context_uid,
            role, status, summary, first_appears, last_known_location,
        ))


@mcp.tool()
def update_entity_context(
    context_uid: str,
    role: Optional[str] = None,
    status: Optional[str] = None,
    summary: Optional[str] = None,
    first_appears: Optional[str] = None,
    last_known_location: Optional[str] = None,
) -> str:
    """Update mutable fields on an NPCContext node."""
    with get_driver() as driver:
        return _json(ent.update_entity_context(
            driver, context_uid, role, status, summary, first_appears, last_known_location,
        ))


@mcp.tool()
def get_entity_in_adventure(
    global_uid: str,
    adventure_uid: str,
    include_disabled: bool = False,
) -> str:
    """Return the NPCContext for a global entity within a specific adventure."""
    with get_driver() as driver:
        return _json(ent.get_entity_in_adventure(driver, global_uid, adventure_uid, include_disabled))


# ── Entity CRUD (Adventure-Scoped) ────────────────────────────────────────────

@mcp.tool()
def upsert_npc(
    uid: str,
    source_adventure: str,
    name: str,
    summary: Optional[str] = None,
    aliases: Optional[list] = None,
    role: Optional[str] = None,
    status: Optional[str] = None,
) -> str:
    """Create or update an adventure-scoped NPC."""
    with get_driver() as driver:
        return _json(ent.upsert_npc(driver, uid, source_adventure, name, summary, aliases, role, status))


@mcp.tool()
def upsert_location(
    uid: str,
    source_adventure: str,
    name: str,
    summary: Optional[str] = None,
    type: Optional[str] = None,
    region: Optional[str] = None,
) -> str:
    """Create or update an adventure-scoped Location."""
    with get_driver() as driver:
        return _json(ent.upsert_location(driver, uid, source_adventure, name, summary, type, region))


@mcp.tool()
def upsert_item(
    uid: str,
    source_adventure: str,
    name: str,
    summary: Optional[str] = None,
    rarity: Optional[str] = None,
) -> str:
    """Create or update an adventure-scoped Item."""
    with get_driver() as driver:
        return _json(ent.upsert_item(driver, uid, source_adventure, name, summary, rarity))


@mcp.tool()
def upsert_faction(
    uid: str,
    source_adventure: str,
    name: str,
    summary: Optional[str] = None,
    alignment: Optional[str] = None,
) -> str:
    """Create or update an adventure-scoped Faction."""
    with get_driver() as driver:
        return _json(ent.upsert_faction(driver, uid, source_adventure, name, summary, alignment))


@mcp.tool()
def get_entity(uid: str, include_disabled: bool = False) -> str:
    """Fetch any adventure-scoped entity (NPC/Location/Item/Faction) by uid."""
    with get_driver() as driver:
        return _json(ent.get_entity(driver, uid, include_disabled))


@mcp.tool()
def list_entities(
    source_adventure: str,
    entity_type: Optional[str] = None,
    include_disabled: bool = False,
    verbose: bool = False,
) -> str:
    """List adventure-scoped entities. entity_type: npc, location, item, faction (omit for all)."""
    with get_driver() as driver:
        return _json(ent.list_entities(driver, source_adventure, entity_type, include_disabled, verbose))


@mcp.tool()
def promote_to_global(
    uid: str,
    canonical_name: str,
    source: str,
    is_canonical: bool = True,
) -> str:
    """Promote an adventure-scoped entity to a Global node."""
    with get_driver() as driver:
        return _json(ent.promote_to_global(driver, uid, canonical_name, source, is_canonical))


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    allow_true_delete = os.environ.get("ALLOW_TRUE_DELETE", "false").lower() == "true"
    if allow_true_delete:
        logger.warning("true_delete is ENABLED — permanent node deletion is active")
    else:
        logger.info("true_delete is DISABLED (set ALLOW_TRUE_DELETE=true to enable)")

    mcp.run()
