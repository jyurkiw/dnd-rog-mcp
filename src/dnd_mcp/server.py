"""MCP server wiring. Registers tool functions as MCP tools. No business logic here."""

import json
import logging
import os
from typing import Optional

from mcp.server.fastmcp import FastMCP

from dnd_mcp.db.connection import get_driver
from dnd_mcp.tools import adventure as adv
from dnd_mcp.tools import entities as ent
from dnd_mcp.tools import narrative as narr
from dnd_mcp.tools import knowledge as know
from dnd_mcp.tools import encounters as enc
from dnd_mcp.tools import timeline as tl
from dnd_mcp.tools import boxed_text as bt
from dnd_mcp.tools import soft_delete as sd
from dnd_mcp.tools import import_export as ie
from dnd_mcp.tools import files as fls

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


# ── Narrative Flow ────────────────────────────────────────────────────────────

@mcp.tool()
def upsert_plotline(uid: str, source_adventure: str, name: str,
                    summary: Optional[str] = None, status: str = "draft",
                    theme: Optional[str] = None) -> str:
    """Create or update a Plotline."""
    with get_driver() as driver:
        return _json(narr.upsert_plotline(driver, uid, source_adventure, name, summary, status, theme))


@mcp.tool()
def add_event(uid: str, plotline_uid: str, name: str, summary: Optional[str] = None,
              event_type: Optional[str] = None, is_anchor: bool = False,
              is_historical: bool = False, source_adventure: Optional[str] = None) -> str:
    """Create an Event and link it to a Plotline."""
    with get_driver() as driver:
        return _json(narr.add_event(driver, uid, plotline_uid, name, summary, event_type,
                                    is_anchor, is_historical, source_adventure))


@mcp.tool()
def add_choice(uid: str, event_uid: str, prompt: str, summary: Optional[str] = None,
               condition: Optional[str] = None, condition_type: Optional[str] = None,
               source_adventure: Optional[str] = None) -> str:
    """Create a Choice branching from an Event."""
    with get_driver() as driver:
        return _json(narr.add_choice(driver, uid, event_uid, prompt, summary,
                                     condition, condition_type, source_adventure))


@mcp.tool()
def add_outcome(uid: str, choice_uid: str, leads_to_event_uid: str, label_text: str,
                consequence_summary: Optional[str] = None, probability: Optional[float] = None,
                source_adventure: Optional[str] = None) -> str:
    """Create an Outcome linking a Choice to the next Event."""
    with get_driver() as driver:
        return _json(narr.add_outcome(driver, uid, choice_uid, leads_to_event_uid, label_text,
                                      consequence_summary, probability, source_adventure))


@mcp.tool()
def link_outcome_to_event(outcome_uid: str, event_uid: str) -> str:
    """Repoint an Outcome to a different Event."""
    with get_driver() as driver:
        return _json(narr.link_outcome_to_event(driver, outcome_uid, event_uid))


@mcp.tool()
def add_causal_link(from_event_uid: str, to_event_uid: str,
                    condition: Optional[str] = None) -> str:
    """Create a direct Event-[:CAUSES]->Event relationship."""
    with get_driver() as driver:
        return _json(narr.add_causal_link(driver, from_event_uid, to_event_uid, condition))


@mcp.tool()
def get_narrative_flow(plotline_uid: str, include_disabled: bool = False) -> str:
    """Return the full directed graph for a plotline (Mermaid/Graphviz ready)."""
    with get_driver() as driver:
        return _json(narr.get_narrative_flow(driver, plotline_uid, include_disabled))


# ── NPC Intelligence ──────────────────────────────────────────────────────────

@mcp.tool()
def set_npc_opinion(driver_uid: str, target_uid: str, sentiment: int,
                    reason: Optional[str] = None) -> str:
    """Set an NPC opinion sentiment (-5 to +5) toward an entity."""
    from dnd_mcp.db.connection import get_database
    from dnd_mcp.db import queries as q
    if not (-5 <= sentiment <= 5):
        return _json({"error": "INVALID_SENTIMENT: sentiment must be between -5 and 5"})
    with get_driver() as driver:
        db = get_database()
        with driver.session(database=db) as session:
            session.run("""
                MATCH (a {uid: $src}), (b {uid: $tgt})
                MERGE (a)-[r:HAS_OPINION]->(b)
                SET r.sentiment = $sentiment, r.reason = $reason
            """, src=driver_uid, tgt=target_uid, sentiment=sentiment, reason=reason)
        return _json({"from_uid": driver_uid, "to_uid": target_uid, "status": "ok"})


@mcp.tool()
def get_npc_opinions(npc_uid: str, include_disabled: bool = False) -> str:
    """Return all opinions held by an NPC."""
    from dnd_mcp.db.connection import get_database
    with get_driver() as driver:
        db = get_database()
        with driver.session(database=db) as session:
            result = session.run("""
                MATCH (n {uid: $uid})-[r:HAS_OPINION]->(target)
                RETURN target.uid AS target_uid, labels(target) AS labels,
                       r.sentiment AS sentiment, r.reason AS reason
            """, uid=npc_uid)
            opinions = [
                {k: v for k, v in {
                    "target_uid": r["target_uid"], "labels": list(r["labels"]),
                    "sentiment": r["sentiment"], "reason": r["reason"],
                }.items() if v is not None}
                for r in result
            ]
        return _json(opinions)


@mcp.tool()
def set_npc_relationship(npc_uid: str, other_uid: str, relationship_type: str,
                          trust_level: Optional[int] = None, history: Optional[str] = None) -> str:
    """Create or update a KNOWS relationship between two NPCs."""
    from dnd_mcp.db.connection import get_database
    with get_driver() as driver:
        db = get_database()
        props = {k: v for k, v in {"relationship_type": relationship_type,
                                    "trust_level": trust_level, "history": history}.items()
                 if v is not None}
        with driver.session(database=db) as session:
            session.run("""
                MATCH (a {uid: $src}), (b {uid: $tgt})
                MERGE (a)-[r:KNOWS]->(b)
                SET r += $props
            """, src=npc_uid, tgt=other_uid, props=props)
        return _json({"from_uid": npc_uid, "to_uid": other_uid, "status": "ok"})


# ── World Knowledge ───────────────────────────────────────────────────────────

@mcp.tool()
def add_rumor(uid: str, content: str, entity_uids: list,
              is_true: Optional[bool] = None, spread: Optional[str] = None,
              source_npc: Optional[str] = None, source_adventure: Optional[str] = None) -> str:
    """Create a Rumor and attach it to one or more entities."""
    with get_driver() as driver:
        return _json(know.add_rumor(driver, uid, content, entity_uids, is_true, spread,
                                    source_npc, source_adventure))


@mcp.tool()
def add_fact(uid: str, content: str, entity_uids: list, reliability: str = "established",
             source_file: Optional[str] = None, source_excerpt_line: Optional[int] = None,
             source_adventure: Optional[str] = None) -> str:
    """Create a Fact and attach it to one or more entities."""
    with get_driver() as driver:
        return _json(know.add_fact(driver, uid, content, entity_uids, reliability,
                                   source_file, source_excerpt_line, source_adventure))


@mcp.tool()
def get_rumors_for(entity_uid: str, include_disabled: bool = False) -> str:
    """Return all Rumors attached to an entity."""
    with get_driver() as driver:
        return _json(know.get_rumors_for(driver, entity_uid, include_disabled))


@mcp.tool()
def get_facts_for(entity_uid: str, include_disabled: bool = False) -> str:
    """Return all Facts attached to an entity."""
    with get_driver() as driver:
        return _json(know.get_facts_for(driver, entity_uid, include_disabled))


@mcp.tool()
def who_knows_what(knowledge_uid: str, include_disabled: bool = False) -> str:
    """Return all NPCs with a path to a given Rumor or Fact."""
    with get_driver() as driver:
        return _json(know.who_knows_what(driver, knowledge_uid, include_disabled))


# ── Encounters ────────────────────────────────────────────────────────────────

@mcp.tool()
def upsert_combat(uid: str, source_adventure: str, name: str, attach_to_uid: str,
                  summary: Optional[str] = None, cr: Optional[float] = None,
                  xp: Optional[int] = None, terrain: Optional[str] = None,
                  tactics: Optional[str] = None) -> str:
    """Create or update a Combat encounter."""
    with get_driver() as driver:
        return _json(enc.upsert_combat(driver, uid, source_adventure, name, attach_to_uid,
                                       summary, cr, xp, terrain, tactics))


@mcp.tool()
def add_combat_participant(combat_uid: str, npc_uid: str) -> str:
    """Link an NPC to a Combat as a participant."""
    with get_driver() as driver:
        return _json(enc.add_combat_participant(driver, combat_uid, npc_uid))


@mcp.tool()
def upsert_skill_challenge(uid: str, source_adventure: str, name: str, attach_to_uid: str,
                            summary: Optional[str] = None, dc: Optional[int] = None,
                            skills_involved: Optional[list] = None,
                            consequences: Optional[str] = None) -> str:
    """Create or update a SkillChallenge."""
    with get_driver() as driver:
        return _json(enc.upsert_skill_challenge(driver, uid, source_adventure, name,
                                                 attach_to_uid, summary, dc,
                                                 skills_involved, consequences))


@mcp.tool()
def upsert_trap(uid: str, source_adventure: str, name: str, attach_to_uid: str,
                summary: Optional[str] = None, dc: Optional[int] = None,
                damage: Optional[str] = None, trigger: Optional[str] = None,
                reset: Optional[str] = None) -> str:
    """Create or update a Trap."""
    with get_driver() as driver:
        return _json(enc.upsert_trap(driver, uid, source_adventure, name, attach_to_uid,
                                     summary, dc, damage, trigger, reset))


@mcp.tool()
def attach_encounter_to_location(encounter_uid: str, location_uid: str) -> str:
    """Attach an existing encounter to an additional Location."""
    with get_driver() as driver:
        return _json(enc.attach_encounter_to_location(driver, encounter_uid, location_uid))


@mcp.tool()
def get_encounters_for_location(location_uid: str, include_disabled: bool = False) -> str:
    """Return all encounters attached to a location."""
    with get_driver() as driver:
        return _json(enc.get_encounters_for_location(driver, location_uid, include_disabled))


# ── Timeline & History ────────────────────────────────────────────────────────

@mcp.tool()
def create_timeline(uid: str, name: str, source_adventure: Optional[str] = None,
                    era: Optional[str] = None, description: Optional[str] = None) -> str:
    """Create a named Timeline."""
    with get_driver() as driver:
        return _json(tl.create_timeline(driver, uid, name, source_adventure, era, description))


@mcp.tool()
def place_event_on_timeline(event_uid: str, timeline_uid: str,
                             precedes_uid: Optional[str] = None) -> str:
    """Place an Event on a Timeline, optionally specifying what it precedes."""
    with get_driver() as driver:
        return _json(tl.place_event_on_timeline(driver, event_uid, timeline_uid, precedes_uid))


@mcp.tool()
def get_timeline(timeline_uid: str, include_disabled: bool = False) -> str:
    """Return events on a timeline in chronological order."""
    with get_driver() as driver:
        return _json(tl.get_timeline(driver, timeline_uid, include_disabled))


@mcp.tool()
def get_history_for(entity_uid: str, include_disabled: bool = False) -> str:
    """Return all events involving an entity, ordered by timeline position."""
    with get_driver() as driver:
        return _json(tl.get_history_for(driver, entity_uid, include_disabled))


# ── Boxed Text ────────────────────────────────────────────────────────────────

@mcp.tool()
def add_boxed_text_sequence(uid: str, name: str, entity_uid: str,
                             source_adventure: Optional[str] = None,
                             summary: Optional[str] = None,
                             context: Optional[str] = None) -> str:
    """Create a BoxedTextSequence and attach it to an entity."""
    with get_driver() as driver:
        return _json(bt.add_boxed_text_sequence(driver, uid, name, entity_uid,
                                                 source_adventure, summary, context))


@mcp.tool()
def add_boxed_text(uid: str, sequence_uid: str, trigger_summary: str, content_summary: str,
                   is_opener: bool = False, tone: Optional[str] = None,
                   sequence_position: Optional[int] = None, is_conditional: bool = False,
                   source_adventure: Optional[str] = None) -> str:
    """Add a BoxedText node to a sequence."""
    with get_driver() as driver:
        return _json(bt.add_boxed_text(driver, uid, sequence_uid, trigger_summary,
                                        content_summary, is_opener, tone,
                                        sequence_position, is_conditional, source_adventure))


@mcp.tool()
def link_boxed_text(from_uid: str, to_uid: str, condition: Optional[str] = None,
                    condition_type: Optional[str] = None) -> str:
    """Create a FOLLOWED_BY relationship between two BoxedText nodes."""
    with get_driver() as driver:
        return _json(bt.link_boxed_text(driver, from_uid, to_uid, condition, condition_type))


@mcp.tool()
def add_alternative_boxed_text(uid_a: str, uid_b: str, reason: str) -> str:
    """Mark two BoxedText nodes as mutually exclusive alternatives."""
    with get_driver() as driver:
        return _json(bt.add_alternative_boxed_text(driver, uid_a, uid_b, reason))


@mcp.tool()
def get_boxed_text_sequence(sequence_uid: str, include_disabled: bool = False) -> str:
    """Return the full BoxedTextSequence graph."""
    with get_driver() as driver:
        return _json(bt.get_boxed_text_sequence(driver, sequence_uid, include_disabled))


@mcp.tool()
def list_unwritten_boxed_text(source_adventure: Optional[str] = None,
                               include_disabled: bool = False) -> str:
    """List BoxedText nodes with no FileRef (prose writing backlog)."""
    with get_driver() as driver:
        return _json(bt.list_unwritten_boxed_text(driver, source_adventure, include_disabled))


# ── File References ───────────────────────────────────────────────────────────

@mcp.tool()
def add_file_reference(uid: str, path: str, entity_uid: str,
                        source_adventure: Optional[str] = None,
                        file_type: Optional[str] = None,
                        description: Optional[str] = None) -> str:
    """Create a FileRef node and link it to an entity."""
    with get_driver() as driver:
        return _json(fls.add_file_reference(driver, uid, path, entity_uid,
                                             source_adventure, file_type, description))


@mcp.tool()
def serve_file_content(uid: str) -> str:
    """Return the content of the file referenced by a FileRef node."""
    with get_driver() as driver:
        return _json(fls.serve_file_content(driver, uid))


# ── Soft Delete ───────────────────────────────────────────────────────────────

@mcp.tool()
def disable(uid: str) -> str:
    """Soft-delete a node and cascade to owned/dependent nodes."""
    with get_driver() as driver:
        return _json(sd.disable(driver, uid))


@mcp.tool()
def undelete(uid: str) -> str:
    """Remove a uid from disabled_by on all cascade-affected nodes; re-enable when list is empty."""
    with get_driver() as driver:
        return _json(sd.undelete(driver, uid))


@mcp.tool()
def true_delete(uid: str) -> str:
    """Permanently delete a node (requires ALLOW_TRUE_DELETE=true and node must be disabled)."""
    with get_driver() as driver:
        return _json(sd.true_delete(driver, uid))


# ── Import / Export ───────────────────────────────────────────────────────────

@mcp.tool()
def export_full_database(include_files: bool = True) -> str:
    """Export all nodes, relationships, and files to an NDJSON structure."""
    with get_driver() as driver:
        return _json(ie.export_full_database(driver, include_files))


@mcp.tool()
def export_adventure(adventure_uid: str, include_files: bool = True) -> str:
    """Export a single adventure and all its associated nodes."""
    with get_driver() as driver:
        return _json(ie.export_adventure(driver, adventure_uid, include_files))


@mcp.tool()
def import_database(lines: list) -> str:
    """Import from NDJSON line list. Only allowed on an empty database."""
    with get_driver() as driver:
        return _json(ie.import_database(driver, lines))


@mcp.tool()
def list_files_in_export(lines: list) -> str:
    """List files in an export without importing."""
    return _json(ie.list_files_in_export(lines))


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    allow_true_delete = os.environ.get("ALLOW_TRUE_DELETE", "false").lower() == "true"
    if allow_true_delete:
        logger.warning("true_delete is ENABLED — permanent node deletion is active")
    else:
        logger.info("true_delete is DISABLED (set ALLOW_TRUE_DELETE=true to enable)")

    mcp.run()
