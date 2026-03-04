# Design Document — dnd-mcp

A purpose-specific MCP server backed by Neo4j for developing D&D adventures and supplements.

---

## Table of Contents

1. [Purpose & Workflow](#purpose--workflow)
2. [Architecture](#architecture)
3. [Data Model — Tier Hierarchy](#data-model--tier-hierarchy)
4. [Data Model — Node Schemas](#data-model--node-schemas)
5. [Data Model — Relationships](#data-model--relationships)
6. [Narrative Flow](#narrative-flow)
7. [Boxed Text & Sequencing](#boxed-text--sequencing)
8. [Soft Delete System](#soft-delete-system)
9. [Import / Export](#import--export)
10. [Tool Groups](#tool-groups)
11. [Environment Variables](#environment-variables)
12. [Docker Composition](#docker-composition)
13. [Documentation & Verbosity Strategy](#documentation--verbosity-strategy)
14. [Requirements](#requirements)
15. [Build Order](#build-order)

---

## Purpose & Workflow

> The database is the **authoritative knowledgebase** that drives and validates prose creation. Prose files are the **output artifact**. The DB is not derived from prose — prose is derived from (and checked against) the DB.

```
Brainstorm/Plan          Write                    Validate
──────────────           ─────                    ────────
Agent + Human      →     Human writes       →     Agent compares
build the DB             prose files              prose against DB
(facts, NPCs,            (flavor text,            and flags
events, choices,         dialogue, room           inconsistencies,
relationships)           descriptions)            contradictions,
                                                  missing context
```

The agent performs the comparison. The DB serves clean, complete, queryable data. Prose files are read by the agent via `serve_file_content` — the DB never parses or stores prose content.

**Fact extraction from prose is explicitly out of scope** for this version. It may be revisited as a future feature if the workflow ever reverses (e.g., importing a legacy adventure that already has prose).

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  MCP Client (Claude)                │
└──────────────────────┬──────────────────────────────┘
                       │ stdio (MCP protocol)
┌──────────────────────▼──────────────────────────────┐
│              Python MCP Server                      │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────┐  │
│  │  Tool Layer │  │ Graph Layer  │  │ I/O Layer │  │
│  │  (handlers) │  │ (Cypher ORM) │  │(import/   │  │
│  └──────┬──────┘  └──────┬───────┘  │ export)   │  │
│         └────────────────┘          └─────┬─────┘  │
└──────────────────────────────────────────┬──────────┘
                       │                   │
┌──────────────────────▼───────────────────▼──────────┐
│                 Neo4j Database                      │
│              (Docker container)                     │
└─────────────────────────────────────────────────────┘
```

Both the MCP server and Neo4j run as services in a single `docker-compose.yml`. The MCP server communicates with Neo4j over the internal Docker network via the Bolt protocol. No external ports are exposed by default.

---

## Data Model — Tier Hierarchy

The graph has three tiers of ownership:

```
GLOBAL tier    — entities that exist independent of any adventure
                 (Elminster, his pipe, the city of Waterdeep)

ADVENTURE tier — the adventure itself + its unique entities
                 (The Sunless Citadel, its unique NPCs, its dungeon rooms)

CONTEXT tier   — relationship nodes that capture how a global entity
                 participates in a specific adventure
                 (Elminster-in-Sunless-Citadel: his role, current state,
                  what he knows, what he has WITH HIM)
```

This means **no duplication of core identity data**, while still allowing full per-adventure divergence.

### Tier 1 — Global Nodes

Canonical identity of an entity. Never store adventure-specific state.

```
(:GlobalNPC {
    uid: "elminster-of-shadowdale",
    canonical_name: "Elminster Aumar",
    aliases: ["The Old Mage", "El"],
    summary: "Archmage of Shadowdale, Chosen of Mystra",
    source: "Forgotten Realms",
    is_canonical: true
})

(:GlobalLocation { uid, canonical_name, summary, source, region, is_canonical })
(:GlobalItem     { uid, canonical_name, summary, source, rarity, is_canonical })
(:GlobalFaction  { uid, canonical_name, summary, source, alignment, is_canonical })
```

### Tier 2 — Adventure Nodes

```
(:Adventure {
    uid: "sunless-citadel-2024",
    name: "The Sunless Citadel",
    status: "draft | in-progress | complete",
    setting: "Forgotten Realms",
    tags: ["dungeon", "undead", "tier-1"],
    summary: "..."
})
```

Adventure-unique entities (a random bandit, a room in this specific dungeon) are created directly under an adventure with no Global counterpart unless promoted.

```
(:NPC      { uid, name, summary, source_adventure, ... })
(:Location { uid, name, summary, source_adventure, ... })
(:Item     { uid, name, summary, source_adventure, ... })
```

### Tier 3 — Context Nodes

When a Global entity appears in an adventure, a Context node bridges them. This is where adventure-specific state lives.

```
(:NPCContext {
    uid: "elminster-in-sunless-citadel",
    role: "quest giver",
    status: "alive | dead | missing | unknown",
    summary: "Sends party to retrieve the Gulthias staff",
    first_appears: "event-uid-001",
    last_known_location: "location-uid-shadowdale-inn",
    has_pipe: false
})
```

Bridge relationships:

```
(:GlobalNPC)-[:APPEARS_IN_ADVENTURE]->(:Adventure)
(:GlobalNPC)-[:REPRESENTED_BY]->(:NPCContext)
(:NPCContext)-[:WITHIN_ADVENTURE]->(:Adventure)
```

### The Pipe Problem — Solved

```
Elminster owns his pipe globally:
  (:GlobalNPC)-[:OWNS]->(:GlobalItem {uid: "pipe-of-elminster"})

In Adventure A (he has it):
  (:NPCContext {uid: "elminster-in-A"})-[:POSSESSES {status:"present"}]->(:GlobalItem)

In Adventure B (finding it is the goal):
  (:NPCContext {uid: "elminster-in-B"})-[:SEEKS]->(:GlobalItem)
  (:Adventure {uid: "B"})-[:FEATURES_RETRIEVAL_OF]->(:GlobalItem)
```

The pipe node never changes. The relationships tell the story.

---

## Data Model — Node Schemas

### Base Properties (every node)

```
{
    uid:          string,      // globally unique
    tier:         "global | adventure | context",
    disabled:     false,       // soft delete flag
    disabled_by:  [],          // cascade source tracking
    disabled_at:  null,
    created_at:   datetime,
    updated_at:   datetime
}
```

### Domain Node Labels

| Label | Key Domain Properties |
|---|---|
| `Adventure` | name, status, setting, tags, summary |
| `GlobalNPC` / `NPC` | canonical_name/name, aliases, summary, source, is_canonical |
| `GlobalLocation` / `Location` | canonical_name/name, summary, source, region, type |
| `GlobalItem` / `Item` | canonical_name/name, summary, source, rarity |
| `GlobalFaction` / `Faction` | canonical_name/name, summary, source, alignment |
| `NPCContext` | role, status, summary, first_appears, last_known_location |
| `Plotline` | name, summary, status, theme |
| `Event` | name, summary, event_type, is_anchor, is_historical |
| `Choice` | prompt, summary, condition |
| `Outcome` | label, consequence_summary, probability |
| `Timeline` | name, era, description |
| `BoxedText` | trigger_summary, content_summary, tone, sequence_position, is_conditional |
| `BoxedTextSequence` | name, summary, context |
| `Fact` | content, reliability, source_file, source_excerpt_line |
| `Rumor` | content, is_true, spread, source_npc |
| `Combat` | name, summary, cr, xp, terrain, tactics |
| `SkillChallenge` | name, summary, dc, skills_involved, consequences |
| `Trap` | name, summary, dc, damage, trigger, reset |
| `FileRef` | path, file_type, description, associated_entity_uid |

---

## Data Model — Relationships

### Tier & Ownership

```
(:GlobalNPC)-[:APPEARS_IN_ADVENTURE]->(:Adventure)
(:GlobalNPC)-[:REPRESENTED_BY]->(:NPCContext)
(:NPCContext)-[:WITHIN_ADVENTURE]->(:Adventure)
(any)-[:BELONGS_TO]->(:Adventure)
```

### Entity Relationships

```
(:NPC/NPCContext)-[:KNOWS {relationship_type, trust_level, history}]->(:NPC/NPCContext)
(entity)-[:LOCATED_IN {is_permanent}]->(:Location)
(:Location)-[:PART_OF]->(:Location)
(:NPC/NPCContext)-[:POSSESSES {status}]->(:GlobalItem/Item)
(:GlobalNPC)-[:OWNS]->(:GlobalItem)
(:NPCContext)-[:SEEKS]->(:GlobalItem)
```

### Narrative Flow

```
(:Event)-[:PART_OF_PLOTLINE]->(:Plotline)
(:Event)-[:BRANCHES_INTO]->(:Choice)
(:Choice)-[:HAS_OUTCOME]->(:Outcome)
(:Outcome)-[:LEADS_TO]->(:Event)           // merges are natural graph topology
(:Event)-[:CAUSES {condition}]->(:Event)   // direct causal link
(:Event)-[:PRECEDES]->(:Event)             // timeline ordering
```

### Knowledge

```
(:NPC/NPCContext)-[:HAS_OPINION {sentiment: int(-5..5), reason}]->(entity)
(:NPC/NPCContext)-[:SPEAKS {trigger_condition}]->(:BoxedText)
(entity)-[:KNOWS_RUMOR]->(:Rumor)
(entity)-[:HAS_FACT]->(:Fact)
(:Event)-[:OCCURRED_IN]->(:Location)
(:Event/Plotline)-[:INVOLVES {role}]->(:NPC/Item/Faction)
```

### Encounters

```
(encounter)-[:LOCATED_IN]->(:Location)
(encounter)-[:TRIGGERED_BY]->(:Event)
(:Combat)-[:PARTICIPANT_IN]->(:NPC/NPCContext)
```

### Boxed Text

```
(entity)-[:HAS_BOXED_TEXT]->(:BoxedText)
(entity)-[:HAS_BOXED_TEXT_SEQUENCE]->(:BoxedTextSequence)
(:BoxedTextSequence)-[:OPENS_WITH]->(:BoxedText)
(:BoxedText)-[:FOLLOWED_BY {condition, condition_type}]->(:BoxedText)
(:BoxedText)-[:ALTERNATIVE_TO {reason}]->(:BoxedText)
(:BoxedText)-[:DEPENDS_ON_EVENT]->(:Event)
(:BoxedText)-[:DEPENDS_ON_ITEM]->(:GlobalItem/Item)
(:BoxedText)-[:DEPENDS_ON_CHOICE]->(:Choice)
(entity)-[:HAS_FILE]->(:FileRef)
```

### Timeline

```
(:Event)-[:ON_TIMELINE]->(:Timeline)
(:Event)-[:PRECEDES {position}]->(:Event)
```

---

## Narrative Flow

Choices are full nodes. Merges are natural graph topology — multiple `LEADS_TO` edges pointing to the same `Event` node constitute a merge. No special merge node is needed.

```
(:Event {is_anchor: true/false, event_type: "scene|combat|revelation|transition"})
(:Choice {prompt, summary, condition, condition_type: "optional|required|gated"})
(:Outcome {label, consequence_summary, probability: null|float})
```

`probability: null` means player-driven. A float means random or weighted.

Anchor events (`is_anchor: true`) must be reachable from the Plotline root via at least one path. The narrative flow graph must be a valid DAG — no cycles permitted.

`get_narrative_flow` returns the full directed graph structured for direct rendering by Mermaid or Graphviz.

---

## Boxed Text & Sequencing

Boxed text in D&D tradition is read-aloud narrative delivered at a specific moment. It is:
- Triggered by something (entering a room, an event firing, an NPC interaction)
- Directed at the players
- A planned narrative beat

### Key Design Decisions

- `BoxedText` stores **summaries only** — never full prose
- Full prose lives in filesystem files, referenced via `FileRef`
- `BoxedText` without a `FileRef` is valid — it represents a **planned but unwritten** narrative moment
- Unwritten `BoxedText` nodes form a queryable **prose writing backlog**

### Conditional Sequencing

```
(:BoxedTextSequence)-[:OPENS_WITH]->(:BoxedText)   // always the first box

(:BoxedText)-[:FOLLOWED_BY {
    condition: null | "party_has:pipe-of-elminster" | "event:pipe-returned:completed" | ...,
    condition_type: null | "possession" | "event_flag" | "skill_check" | "npc_opinion" | "visit_count" | "choice_made"
}]->(:BoxedText)

(:BoxedText)-[:ALTERNATIVE_TO {reason}]->(:BoxedText)  // mutually exclusive variants
```

### Condition Types

| condition_type | Example | Meaning |
|---|---|---|
| `null` | — | Unconditional |
| `possession` | `party_has:pipe-of-elminster` | Party inventory state |
| `event_flag` | `event:found-pipe:completed` | Named event has occurred |
| `skill_check` | `skill:Persuasion:DC15` | Inline skill check gate |
| `npc_opinion` | `opinion:elminster:party >= 3` | NPC sentiment threshold |
| `visit_count` | `visit:shadowdale-inn >= 2` | Location visit count |
| `choice_made` | `choice:uid:outcome-uid` | Specific prior choice was made |

### Elminster Pipe Example

```
Sequence: "Elminster — Return to Shadowdale"
│
├── [BT-1] OPENS_WITH
│   "Elminster greets party, asks how the road treated them" (always fires)
│
├── [BT-2] FOLLOWED_BY (condition: null)
│   "Elminster asks obliquely if they found anything interesting"
│
├── [BT-3a] FOLLOWED_BY (condition: possession:pipe-of-elminster)
│   "Elminster spots his pipe, eyes light up, grateful monologue"
│   ALTERNATIVE_TO [BT-3b]
│
├── [BT-3b] FOLLOWED_BY (condition: event_flag:pipe-location-known)
│   "Elminster grows quiet, asks them to describe where they saw it"
│   ALTERNATIVE_TO [BT-3c]
│
└── [BT-3c] FOLLOWED_BY (condition: null — fallback)
    "Elminster changes subject, seems distracted"
```

---

## Soft Delete System

> **Delete means hide. True Delete means gone.**

### The `disabled` Property

Every node carries:

```
disabled:    false,    // default — node is active
disabled_by: [],       // list of uids that triggered cascade-disable
disabled_at: null      // datetime of most recent disable
```

### The Three Operations

| Operation | Behavior |
|---|---|
| `disable(uid)` | Sets `disabled: true`, cascades to owned/dependent nodes, appends triggering uid to `disabled_by` |
| `undelete(uid)` | Removes uid from `disabled_by` on all cascade-affected nodes; sets `disabled: false` only when list is empty |
| `true_delete(uid)` | Hard-fails if target is not already disabled; permanently deletes target and cascade-owned nodes |

### Cascade Table

| Disabled Node | Cascades To |
|---|---|
| `Adventure` | All adventure-scoped nodes, all Context nodes, all attached BoxedTextSequences |
| `GlobalNPC/Item/Location/Faction` | All Context nodes representing that entity |
| `NPCContext` | All Opinions, BoxedText sequences attached to that context |
| `Plotline` | All Events, all Choices and Outcomes on those Events |
| `Event` | All Choices branching from it, all Outcomes, all attached BoxedText |
| `Choice` | All Outcomes, all attached BoxedText |
| `BoxedTextSequence` | All BoxedText nodes in the sequence |
| `Location` | All Encounters attached solely to that location |

### Shared Node Protection

If a node has multiple parent relationships, it is only disabled when **all** parent relationships resolve to disabled nodes. `disabled_by` is a list to support this — all sources must `undelete` before the node resurfaces.

### true_delete Gate

`true_delete` is **disabled by default**. It must be explicitly enabled via environment variable:

```
ALLOW_TRUE_DELETE=false    // default — safe mode
ALLOW_TRUE_DELETE=true     // opt-in destructive mode
```

`true_delete` is always registered as a tool regardless of this setting. The gate is inside the handler. When disabled, it returns a structured error explaining the situation and how to enable it. The enabled/disabled state is logged unambiguously at server startup.

---

## Import / Export

### Hard Rules

- Import is **only permitted on an empty database** — enforced by a pre-flight node count check
- Attempting to import to a populated DB returns a hard error
- No merge logic. Merging means something went wrong and should be done by hand
- Export is always permitted and non-destructive

### Export Format (NDJSON)

```jsonl
{"meta": {"schema_version": 1, "exported_at": "...", "node_count": 412, "rel_count": 891}}
{"type": "node", "tier": "global", "label": "GlobalNPC", "uid": "elminster", "properties": {...}}
{"type": "node", "tier": "adventure", "label": "Adventure", "uid": "sunless-citadel", "properties": {...}}
{"type": "node", "tier": "context", "label": "NPCContext", "uid": "elminster-in-sc", "properties": {...}}
{"type": "relationship", "uid": "rel-001", "rel_type": "REPRESENTED_BY", "from_uid": "elminster", "to_uid": "elminster-in-sc", "properties": {...}}
{"type": "file", "path": "/adventures/sunless-citadel/npcs/elminster-intro.md", "content": "plaintext or base64", "encoding": "utf-8 | base64"}
```

- All strings, no binary in the envelope itself
- Human-readable, diff-friendly, version-control friendly
- File content inlined — export is fully self-contained
- Disabled nodes included in export (flagged) — backup/restore is lossless
- Import must be transactional — all or nothing, rollback on any error
- Round-trip fidelity required: full import → full export must produce byte-equivalent output

---

## Tool Groups

### 1. Adventure Management
`create_adventure`, `get_adventure`, `list_adventures`, `link_adventures`

### 2. Global Entity Management
`create_global_npc`, `create_global_location`, `create_global_item`, `create_global_faction`,
`get_global_entity`, `list_global_entities`, `promote_to_global`

### 3. Context Management
`add_entity_to_adventure`, `update_entity_context`, `get_entity_in_adventure`, `set_possession_state`

### 4. Entity CRUD (Adventure-Scoped)
`upsert_npc`, `upsert_location`, `upsert_item`, `upsert_faction`,
`get_entity`, `list_entities`

### 5. Narrative Flow
`upsert_plotline`, `add_event`, `add_choice`, `add_outcome`,
`link_outcome_to_event`, `add_causal_link`, `get_narrative_flow`

### 6. NPC Intelligence
`set_npc_opinion`, `get_npc_opinions`, `get_npc_profile`, `set_npc_relationship`

### 7. Boxed Text
`add_boxed_text_sequence`, `add_boxed_text`, `link_boxed_text`,
`add_alternative_boxed_text`, `get_boxed_text_sequence`, `list_unwritten_boxed_text`

### 8. World Knowledge
`add_rumor`, `add_fact`, `get_rumors_for`, `who_knows_what`

### 9. Encounters
`upsert_combat`, `upsert_skill_challenge`, `upsert_trap`,
`attach_encounter_to_location`, `get_encounters_for_location`

### 10. Timeline & History
`create_timeline`, `place_event_on_timeline`, `get_timeline`, `get_history_for`

### 11. File References
`add_file_reference`, `serve_file_content`

### 12. Graph Queries
`find_connections`, `get_neighborhood`, `query_by_tag`, `impact_analysis`

### 13. Soft Delete
`disable`, `undelete`, `true_delete`

### 14. Import / Export
`export_full_database`, `export_adventure`, `import_database`, `list_files_in_export`

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `NEO4J_URI` | `bolt://neo4j:7687` | Neo4j Bolt URI |
| `NEO4J_USER` | `neo4j` | Neo4j username |
| `NEO4J_PASSWORD` | — | Neo4j password (required) |
| `NEO4J_DATABASE` | `dnd` | Neo4j database name |
| `MCP_LOG_LEVEL` | `INFO` | Server log level |
| `ALLOW_TRUE_DELETE` | `false` | Enable permanent destructive deletes |

---

## Docker Composition

Two services in `docker-compose.yml`:

**`neo4j`** — Official Neo4j image. No externally exposed ports. Data persisted to a named volume. Internal network only.

**`mcp-server`** — Python image. Reads from stdin / writes to stdout for MCP stdio transport. Depends on `neo4j`. Receives env vars from `.env` file. Communicates with Neo4j via Bolt on the internal Docker network only.

The MCP client connects to the `mcp-server` container's stdio via `docker exec` or by running it as a subprocess.

---

## Documentation & Verbosity Strategy

### Two-Layer Documentation

**Layer 1 — Agent System Prompt** (always present, zero tool calls):
- Conceptual model (three tiers, soft delete, narrative flow)
- Terse tool index (name + one-line description)
- UID conventions and naming rules
- Error response shape

**Layer 2 — Searchable Reference Document** (fetched on demand via filesystem MCP):
- Full parameter signatures
- Constraint notes
- Examples
- Fetched as a targeted file read, not a tool call

### Low Verbosity Rules

- Write operations return only affected `uid`(s) and a status field
- Read operations return structured JSON with no prose decoration
- Errors return a single `error` field: machine-readable code + one-sentence reason
- No confirmation narrative, no natural language decoration on success
- Null fields and empty arrays omitted from all responses
- List operations return arrays of uids by default; `verbose` parameter for full properties
- `get_narrative_flow` and `get_npc_profile` are explicitly permitted larger payloads

---

## Requirements

### Graph Integrity (GI)

| ID | Requirement |
|---|---|
| GI-01 | Every node must have a `uid` unique across the entire database |
| GI-02 | Every node must have a `tier` property: `global`, `adventure`, or `context` |
| GI-03 | No relationship may exist if either endpoint node does not exist |
| GI-04 | A Context node must have exactly one `WITHIN_ADVENTURE` relationship |
| GI-05 | A Context node must have exactly one inbound `REPRESENTED_BY` from a Global node |
| GI-06 | Deleting a node must cascade-delete all context nodes and relationships |
| GI-07 | Deleting an Adventure must cascade-delete all nodes with matching `source_adventure` |
| GI-08 | A Global node may not have a `source_adventure` property |
| GI-09 | No duplicate `uid` values, even across different node labels |
| GI-10 | A `FileRef` path must be unique within the database |

### Tier & Hierarchy (TH)

| ID | Requirement |
|---|---|
| TH-01 | A Global entity may exist with no relationship to any Adventure |
| TH-02 | A Global entity may be linked to zero, one, or many Adventures |
| TH-03 | Each (Global entity, Adventure) pair may have at most one Context node |
| TH-04 | An adventure-scoped entity may be promoted to a Global node, preserving its uid |
| TH-05 | After promotion, the original node becomes a Context node |
| TH-06 | Adventure-scoped entities must have a `source_adventure` matching a valid Adventure uid |
| TH-07 | Global identity fields may not be modified via adventure-scoped tools |
| TH-08 | Context nodes may store any adventure-specific state without affecting the Global node |

### Narrative Flow (NF)

| ID | Requirement |
|---|---|
| NF-01 | Every Event must belong to at least one Plotline via `PART_OF_PLOTLINE` |
| NF-02 | An Event may have zero or more outbound `BRANCHES_INTO` relationships |
| NF-03 | A Choice must have at least one `HAS_OUTCOME` relationship |
| NF-04 | An Outcome must have exactly one `LEADS_TO` relationship to an Event |
| NF-05 | An Event may be the target of `LEADS_TO` from multiple Outcomes — valid merge |
| NF-06 | An Event may have a direct `CAUSES` relationship to another Event |
| NF-07 | Anchor events must be reachable from the Plotline root via at least one path |
| NF-08 | The narrative flow graph must be a valid DAG — no cycles |
| NF-09 | A root event must be designated per Plotline |
| NF-10 | `get_narrative_flow` must return a structure renderable as a flowchart |

### NPC & Relationships (NR)

| ID | Requirement |
|---|---|
| NR-01 | NPC Opinion sentiment must be an integer from -5 to +5 |
| NR-02 | An Opinion must reference both a source and a target entity |
| NR-03 | Opinion targets may be: NPC, NPCContext, Faction, Item, Location, or Event |
| NR-04 | A `KNOWS` relationship must specify `relationship_type`, may specify `trust_level` |
| NR-05 | NPC dialogue (BoxedText) must be associated with a trigger condition |
| NR-06 | An NPCContext may override the Global NPC summary without modifying the Global node |
| NR-07 | `get_npc_profile` must return: global identity, context, opinions, rumors, facts, NPC relationships, BoxedText |

### World Knowledge (WK)

| ID | Requirement |
|---|---|
| WK-01 | A Rumor must be attached to at least one NPC, Location, or Faction |
| WK-02 | A Rumor's `is_true` field may be `true`, `false`, or `null` |
| WK-03 | A Fact must have a `reliability` field: `established`, `rumored`, or `contradicted` |
| WK-04 | Both Rumors and Facts must be queryable by the entity they are attached to |
| WK-05 | A single Rumor or Fact may be attached to multiple entities |
| WK-06 | `who_knows_what` must return all NPCs with a path to a given Rumor or Fact |

### Encounters (EN)

| ID | Requirement |
|---|---|
| EN-01 | A Combat, SkillChallenge, or Trap must be attached to at least one Location or Event |
| EN-02 | Encounter nodes must store `cr` and `xp` as optional numeric fields |
| EN-03 | A Combat must support multiple participant NPCs via `PARTICIPANT_IN` |
| EN-04 | A SkillChallenge must store applicable skills and DCs |
| EN-05 | A Trap must store trigger, effect summary, and reset condition |
| EN-06 | An encounter may have an associated BoxedText for its introduction moment |

### Boxed Text (BT)

| ID | Requirement |
|---|---|
| BT-01 | A BoxedText node stores trigger summary, content summary, tone, sequence position — never full prose |
| BT-02 | A BoxedText may optionally reference a FileRef for the full prose |
| BT-03 | BoxedText may be attached to: Event, Location, NPC/NPCContext, Choice, Combat, Trap, SkillChallenge |
| BT-04 | A BoxedTextSequence groups related BoxedText nodes with a defined entry point via `OPENS_WITH` |
| BT-05 | `FOLLOWED_BY` relationships must carry a `condition` (nullable) and `condition_type` |
| BT-06 | Mutually exclusive variant boxes must be linked by `ALTERNATIVE_TO` with a `reason` property |
| BT-07 | BoxedText without a FileRef is valid — represents a planned but unwritten narrative moment |
| BT-08 | BoxedText nodes without a FileRef must be listable as a prose writing backlog |
| BT-09 | Dependency relationships must be created automatically when a condition referencing that entity is set |
| BT-10 | `get_boxed_text_sequence` must return the full sequence graph |
| BT-11 | A query for "what prose depends on this entity" must be satisfiable via dependency relationships |

### Timeline & History (TL)

| ID | Requirement |
|---|---|
| TL-01 | A Timeline is a named, ordered sequence of Event nodes |
| TL-02 | An Event may belong to zero or more Timelines |
| TL-03 | Event ordering on a Timeline is stored on the `PRECEDES` relationship, not on the Event |
| TL-04 | Historical events (`is_historical: true`) may have no Plotline association |
| TL-05 | `get_timeline` must return events in chronological order |
| TL-06 | `get_history_for` must return all events involving an entity, ordered by timeline position |

### Soft Delete (SD)

| ID | Requirement |
|---|---|
| SD-01 | Every node must have a `disabled` boolean property defaulting to `false` |
| SD-02 | Every node must have a `disabled_by` list property defaulting to empty |
| SD-03 | Every node must have a `disabled_at` nullable datetime property |
| SD-04 | All read tools must filter `disabled: false` by default |
| SD-05 | Read tools must accept an optional `include_disabled` parameter |
| SD-06 | `disable` must cascade to all owned/dependent nodes per the cascade table |
| SD-07 | `disable` must respect shared node protection |
| SD-08 | `disable` must append the triggering uid to `disabled_by` on every affected node |
| SD-09 | `undelete` must only re-enable nodes whose `disabled_by` list contains the target uid |
| SD-10 | `undelete` must remove the target uid from `disabled_by` and only set `disabled: false` when the list is empty |
| SD-11 | `true_delete` must hard-fail if the target node is not already `disabled: true` |
| SD-12 | `true_delete` must permanently delete the target node, all cascade-owned nodes, and all their relationships |
| SD-13 | `true_delete` must return a count of nodes and relationships permanently removed |
| SD-14 | No tool other than `true_delete` may permanently remove a node from the database |
| SD-15 | Export must include disabled nodes, flagged as such |
| SD-16 | Import must correctly restore `disabled`, `disabled_by`, and `disabled_at` state |
| SD-17 | `true_delete` must be disabled by default and only enabled when `ALLOW_TRUE_DELETE=true` |
| SD-18 | When `ALLOW_TRUE_DELETE` is not `true`, calling `true_delete` must return a structured error explaining the situation and how to enable it |
| SD-19 | The enabled/disabled state of `true_delete` must be logged unambiguously at server startup |
| SD-20 | `true_delete` must never be silently disabled — the error must be self-explanatory |

### Import / Export (IE)

| ID | Requirement |
|---|---|
| IE-01 | Export must serialize all nodes, relationships, and inlined file contents to NDJSON |
| IE-02 | Every exported node must include `uid`, `label`, `tier`, and all properties |
| IE-03 | Every exported relationship must include `from_uid`, `to_uid`, `rel_type`, and all properties |
| IE-04 | File content in export must be inlined as UTF-8 plaintext; binary as base64 with encoding flagged |
| IE-05 | Import must perform a node count pre-flight check and hard-fail if the database is not empty |
| IE-06 | Import must be transactional — all or nothing, rollback on any error |
| IE-07 | Import must validate schema version compatibility before writing any data |
| IE-08 | `export_adventure` must include the Adventure node, all adventure-scoped nodes, all Context nodes, all referenced Global nodes (flagged read-only), and all FileRefs with inlined content |
| IE-09 | A full import followed by a full export must produce byte-equivalent output |
| IE-10 | `list_files_in_export` must work without importing, operating on raw NDJSON |

### MCP Protocol (MP)

| ID | Requirement |
|---|---|
| MP-01 | All tools must return responses conforming to the MCP content block specification |
| MP-02 | All tool errors must return structured error content blocks, not exceptions |
| MP-03 | Every tool must validate input parameters before executing any DB operation |
| MP-04 | Tools that write data must return the uid(s) of created or modified nodes |
| MP-05 | Tools that read data must return structured JSON, not raw Cypher results |
| MP-06 | `serve_file_content` must return a plaintext content block |
| MP-07 | The server must handle Neo4j connection failure gracefully |
| MP-08 | All tools must be callable with minimal required parameters; optional parameters must have documented defaults |

### Low Verbosity (LV)

| ID | Requirement |
|---|---|
| LV-01 | All tool responses must return the minimum data necessary to confirm success or explain failure |
| LV-02 | Write operations must return only affected uid(s) and a status field on success |
| LV-03 | Read operations must return structured JSON with no prose, no redundant nesting |
| LV-04 | Error responses must return a single `error` field: short machine-readable code + one-sentence reason |
| LV-05 | No tool may return confirmation narrative or natural language decoration on success |
| LV-06 | List operations must return arrays of uids by default; `verbose` parameter for full properties |
| LV-07 | `get_narrative_flow` and `get_npc_profile` are permitted larger payloads but must omit null fields and empty arrays |
| LV-08 | Null fields and empty arrays must be omitted from all responses |
| LV-09 | Tool documentation must live in a static reference document, not in any tool handler |
| LV-10 | The agent system prompt must contain a terse tool index sufficient for routine operation |

---

## Build Order

1. Docker Compose + Neo4j connection layer + env config
2. Global entity CRUD + Adventure CRUD
3. Context node bridge (`add_entity_to_adventure` family)
4. Narrative flow nodes (Event → Choice → Outcome → Event)
5. Import / Export
6. Boxed Text + Sequencing
7. Remaining tool groups (encounters, timeline, knowledge, graph queries)
8. Soft delete system
9. `serve_file_content`
10. `extract_facts_from_file` — **potential future feature, not current scope**

---

## Potential Future Features

- **Fact extraction from prose** — parsing prose files to automatically create Fact nodes in the graph. Descoped because the DB drives prose creation, not the reverse. May be useful for importing legacy adventures.
- **Automatic inconsistency detection** — the agent already performs this natively using `get_entity_in_adventure` + `serve_file_content`.
