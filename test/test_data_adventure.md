# Test Data Adventure: The Troubles of Shadowdale

This document serves two purposes:

1. **Narrative description** — a plain-English writeup of the adventure sufficient to regenerate all node and entity data from scratch.
2. **Node & entity catalogue** — the complete structured data for every node, relationship, encounter, boxed text sequence, rumor, fact, and timeline entry required to populate the database for testing.

This adventure is designed to exercise every requirement category defined in DESIGN.md. See the requirement coverage table at the end of this document.

---

## Part One: Narrative Description

### Overview

*The Troubles of Shadowdale* is a Tier 1 adventure (levels 1–4) set in Shadowdale in the Forgotten Realms. The players arrive as outsiders bearing a letter of introduction and are drawn into a pair of monster-hunting jobs by the resident archmage, Elminster Aumar — one of which involves recovering his stolen pipe.

The adventure is structured as a brief social Act 1, a fully branching Act 2 with two independent combat paths (each with their own internal branches and merge points), and a converging Act 3 whose resolution varies based on what state the pipe is in when it is returned (or not returned at all).

---

### Act 1 — Arrival

The players approach Shadowdale from the northern road. Shadowdale is a small, deeply insular dale. There is no tavern. Residents value their privacy fiercely and do not welcome wandering strangers. Elminster's enchantments protect the border of the village and would normally turn uninvited visitors around in a series of cheeky, mildly annoying, entirely non-lethal ways — unless the visitors grow aggressive, in which case the consequences become significantly less pleasant.

The PCs, however, have a letter of introduction. As they reach the border, the letter flies out of whoever is carrying it, folds itself into a small origami dragon, and offers to guide them to lodging for the night. The dragon speaks in a male voice that is quite obviously trying and failing to sound female. It introduces itself as Lettinster, explains that it is a kind of homunculus, and cheerfully sets off ahead of them into the dale.

Lettinster leads the party to the farm of **Jhaele Silvermane**, a retired adventurer missing his sword-arm below the elbow. Jhaele is welcoming in the gruff, practical way of someone who used to do what the PCs do and has no illusions about it. He offers them the use of his barn for the night, feeds them, and mentions offhandedly that *the wizard* will be by tomorrow morning for breakfast, and if they want to talk to him, that would be the time to do it.

The PCs take a long rest in the barn.

---

### Act 2 — The Briefing

The next morning, Elminster arrives for breakfast. He is without his pipe — a detail he does not immediately explain. He sits down, eats Jhaele's food, and begins to hold court. He performs the role of a tired old man who simply cannot be expected to deal with local problems himself — a DC 11 Insight check reveals he is being thoroughly lazy, but his coin is real and his problem is genuine.

Elminster explains that two monsters have emerged from **Cavenauth**, a cavern network in the forest near the ruins of Castle Grimstead. The monsters apparently fought each other somewhere in the Underdark, both emerged wounded, and have since caused problems in the dale:

- One is lurking somewhere in or around the **Temple of Tymora**, terrorizing the priestess and her graveyard.
- The other is aquatic and has taken up residence in the **millpond** on the River Ashaba, disrupting the mill and hunting deer in the surrounding area. It has also injured a horse tied outside Sylune's Hut nearby.

Elminster will pay gold for each monster dealt with. He will also admit, with slightly less performance than the rest of the conversation, that he may have encountered both monsters by chance the previous day. During this encounter, one of them — the aquatic one — stole his favorite pipe. He would be grateful to have it back. In one piece, if possible.

The PCs choose where to go first.

---

### Act 2A — The Temple of Tymora

The Temple of Tymora in Shadowdale is run by **Sister Maeris Ondil**, a middle-aged priestess with no sense of humor and a great deal of righteous indignation about the state of her graveyard. She will not help the PCs fight but she will not get in their way either, and she is perfectly capable of describing exactly where in the graveyard the thing has been sleeping.

The **Graveyard Skulker** is hiding in a freshly dug grave. The PCs can attempt to approach it stealthily (Stealth contested by the monster's passive awareness, DC 13) to gain a surprise round, or they can simply walk in and fight. The monster will attempt to flee once reduced to 50% of its hit points, retreating into the forest toward the ruins of Castle Grimstead.

If the Skulker escapes to **Castle Grimstead**, the PCs can pursue it there. The ruins function the same as the graveyard in terms of the fight, but without the irate priestess. The monster will attempt to flee again at 25% hit points, retreating to Cavenauth and back into the Underdark. If the PCs do not pursue, or if night falls before they do, the monster returns to the Underdark on its own.

---

### Act 2B — The Mill

The mill sits on the River Ashaba. The **Millpond Horror** is hiding in the millpond. Investigation of the area (DC 12 Perception or Survival) reveals deer remains nearby. The injured horse at Sylune's Hut nearby is also visible and easy to notice (DC 10 Perception). The monster has Elminster's pipe.

The PCs have a meaningful tactical choice here:

**Fight in the water.** The PCs are at a disadvantage in the pond. The monster is in its element. The pipe is being passively protected by the monster's magic for now, but if the monster is killed underwater with the pipe still on it, the pipe will be waterlogged. If the PCs take the pipe from the monster before killing it, the pipe will be undamaged but waterlogged. The monster will attempt to flee at 25% hit points and will appear at the pool beside the Tower of Ashaba the following day.

**Lure the monster onto land.** The monster is at a disadvantage on land. Evidence of deer hunting provides a means to understand its behavior and potentially draw it out. The fight is easier. If the monster is killed with the pipe still on it, the pipe is damaged. If the PCs take the pipe first, it is returned undamaged and dry. The monster will attempt to flee at 50% hit points and will appear at the Tower of Ashaba pool the following day.

**The Tower of Ashaba pool** is a follow-up location that functions identically to the millpond if the monster escapes. Same tactical choice, same pipe outcome logic.

---

### Between Encounters — Returning to the Farm

The PCs can return to Jhaele's farm between the two combat paths to rest. Elminster is present and visiting with Jhaele for most of the day. His behavior during these visits depends on what has happened:

- If the PCs take a **short rest** and have not returned the pipe, he chats and mentions missing his tabac. He asks after the pipe obliquely.
- If the PCs take a **long rest** and have not returned the pipe, he grows more concerned — if the monsters go back underground, the pipe goes with them.
- If a monster has **escaped**, he comments on it — resigned and resigned.
- If a monster is **dead**, he comments differently — pleased, possibly a little smug about having hired the right people.

---

### Act 3 — Resolution

Both paths lead back to Jhaele's farm. Elminster pays for each monster dealt with. The pipe resolution is handled separately with four possible outcomes:

- **Pipe returned undamaged and dry:** Elminster's eyes light up. Genuine gratitude. He produces a minor magic item as an additional reward.
- **Pipe returned waterlogged:** Elminster takes the pipe with visible displeasure, dries it with a cantrip while sighing, and produces extra gold as a consolation.
- **Pipe returned damaged:** Elminster takes the pipe quietly. He thanks the PCs. There is no further reward beyond the monster payment.
- **Pipe not returned:** Elminster says nothing about the pipe. There is a slightly heavier silence. He pays for the monster work and nothing more.

The PCs are invited to spend one more night in the barn and asked — politely but firmly — to move on in the morning.

---

## Part Two: Node & Entity Catalogue

---

### Global Nodes

These nodes exist at the global tier, independent of any adventure.

#### Global NPC: Elminster Aumar

| Property | Value |
|---|---|
| uid | `global-npc-elminster` |
| label | GlobalNPC |
| tier | global |
| canonical_name | Elminster Aumar |
| aliases | ["The Old Mage", "El", "The Archmage of Shadowdale"] |
| summary | Chosen of Mystra, archmage resident of Shadowdale. Powerful, eccentric, occasionally lazy, always watching. |
| source | Forgotten Realms |
| is_canonical | true |

#### Global Item: Pipe of Elminster

| Property | Value |
|---|---|
| uid | `global-item-pipe-of-elminster` |
| label | GlobalItem |
| tier | global |
| canonical_name | Pipe of Elminster |
| summary | Elminster's favorite smoking pipe. Faintly magical — self-protects against minor damage. He is unreasonably attached to it. |
| source | Forgotten Realms |
| rarity | uncommon |
| is_canonical | true |

**Global Relationship:**
`global-npc-elminster` -[:OWNS]-> `global-item-pipe-of-elminster`

#### Global Location: Shadowdale

| Property | Value |
|---|---|
| uid | `global-location-shadowdale` |
| label | GlobalLocation |
| tier | global |
| canonical_name | Shadowdale |
| summary | A small, insular dale in the Dalelands. No tavern. Residents value their privacy. Protected by Elminster's enchantments at its borders. |
| source | Forgotten Realms |
| region | The Dalelands |
| is_canonical | true |

#### Global Location: Tower of Ashaba

| Property | Value |
|---|---|
| uid | `global-location-tower-of-ashaba` |
| label | GlobalLocation |
| tier | global |
| canonical_name | Tower of Ashaba |
| summary | Ancient tower in Shadowdale, seat of the Lord of Shadowdale. Has a pool beside it that becomes significant if either monster escapes. |
| source | Forgotten Realms |
| region | Shadowdale |
| is_canonical | true |

#### Global Location: River Ashaba

| Property | Value |
|---|---|
| uid | `global-location-river-ashaba` |
| label | GlobalLocation |
| tier | global |
| canonical_name | River Ashaba |
| summary | River running through Shadowdale. The mill sits on its bank. |
| source | Forgotten Realms |
| region | Shadowdale |
| is_canonical | true |

---

### Adventure Node

| Property | Value |
|---|---|
| uid | `adv-troubles-of-shadowdale` |
| label | Adventure |
| tier | adventure |
| name | The Troubles of Shadowdale |
| status | draft |
| setting | Forgotten Realms |
| tags | ["investigation", "combat", "social", "forgotten-realms", "tier-1"] |
| summary | PCs arrive in Shadowdale, meet Elminster, and are hired to deal with two wounded Underdark monsters — one of which has his pipe. |

---

### Context Nodes

#### Elminster in This Adventure

| Property | Value |
|---|---|
| uid | `ctx-elminster-troubles` |
| label | NPCContext |
| tier | context |
| role | quest-giver, recurring presence |
| status | alive |
| summary | Elminster is between adventures and content to be lazy. Needs the PCs more than he'll admit. Currently without his pipe — stolen by the Millpond Horror. |
| has_pipe | false |

**Relationships:**
- `global-npc-elminster` -[:REPRESENTED_BY]-> `ctx-elminster-troubles`
- `ctx-elminster-troubles` -[:WITHIN_ADVENTURE]-> `adv-troubles-of-shadowdale`
- `global-npc-elminster` -[:APPEARS_IN_ADVENTURE]-> `adv-troubles-of-shadowdale`
- `ctx-elminster-troubles` -[:SEEKS]-> `global-item-pipe-of-elminster`

---

### Adventure-Scoped NPCs

#### Jhaele Silvermane

| Property | Value |
|---|---|
| uid | `npc-jhaele-silvermane` |
| label | NPC |
| tier | adventure |
| name | Jhaele Silvermane |
| summary | Farmer, ex-adventurer. Missing his sword-arm below the elbow. Generous with his barn, close with Elminster, steady under pressure. |
| role | host, information source |
| source_adventure | `adv-troubles-of-shadowdale` |

#### Lettinster

| Property | Value |
|---|---|
| uid | `npc-lettinster` |
| label | NPC |
| tier | adventure |
| name | Lettinster |
| summary | A homunculus made from the PCs' letter of introduction. Folds itself into an origami dragon. Speaks in a male voice badly pretending to be female. Guides Elminster-approved visitors into the dale. Appears once and dissolves when its purpose is complete. |
| role | guide, comic relief |
| source_adventure | `adv-troubles-of-shadowdale` |

#### Sister Maeris Ondil

| Property | Value |
|---|---|
| uid | `npc-tymora-priestess` |
| label | NPC |
| tier | adventure |
| name | Sister Maeris Ondil |
| summary | Middle-aged priestess running the Temple of Tymora. No sense of humor. Deeply unhappy about the monster in her graveyard. Will not fight but will not obstruct the PCs either. |
| role | information source, atmosphere |
| source_adventure | `adv-troubles-of-shadowdale` |

#### The Graveyard Skulker

| Property | Value |
|---|---|
| uid | `npc-monster-graveyard` |
| label | NPC |
| tier | adventure |
| name | The Graveyard Skulker |
| summary | Wounded Underdark predator holed up in a freshly dug grave in the Temple of Tymora's graveyard. Aggressive when cornered. Flees at 50% HP to Castle Grimstead, then at 25% HP retreats to Cavenauth and the Underdark. If not pursued at Grimstead, returns underground when night falls. |
| role | antagonist |
| cr | 2 |
| xp | 450 |
| source_adventure | `adv-troubles-of-shadowdale` |

#### The Millpond Horror

| Property | Value |
|---|---|
| uid | `npc-monster-millpond` |
| label | NPC |
| tier | adventure |
| name | The Millpond Horror |
| summary | Wounded aquatic Underdark predator hiding in the millpond on the River Ashaba. Has Elminster's pipe. Has been hunting deer and injured a horse at Sylune's Hut. Flees at 25% HP (water fight) or 50% HP (land fight), reappearing at the Tower of Ashaba pool the next day. |
| role | antagonist, pipe-holder |
| cr | 3 |
| xp | 700 |
| source_adventure | `adv-troubles-of-shadowdale` |

**Relationship:**
`npc-monster-millpond` -[:POSSESSES {status: "stolen"}]-> `global-item-pipe-of-elminster`

---

### NPC Relationships

| From | Relationship | To | Properties |
|---|---|---|---|
| `npc-jhaele-silvermane` | KNOWS | `ctx-elminster-troubles` | relationship_type: "old friends", trust_level: 5 |
| `ctx-elminster-troubles` | HAS_OPINION | `npc-jhaele-silvermane` | sentiment: 4, reason: "Reliable, discreet, good breakfast" |
| `ctx-elminster-troubles` | HAS_OPINION | `npc-monster-millpond` | sentiment: -3, reason: "Stole his pipe. Rude." |
| `npc-tymora-priestess` | HAS_OPINION | `npc-monster-graveyard` | sentiment: -5, reason: "It is in her graveyard" |

---

### Adventure-Scoped Locations

#### Northern Road Entry

| Property | Value |
|---|---|
| uid | `loc-northern-road-entry` |
| label | Location |
| tier | adventure |
| name | Northern Road — Shadowdale Border |
| summary | Where the northern road enters Shadowdale's territory. Elminster's enchantments begin here. Where Lettinster manifests from the letter of introduction. |
| type | wilderness |
| source_adventure | `adv-troubles-of-shadowdale` |

**Relationship:** `loc-northern-road-entry` -[:PART_OF]-> `global-location-shadowdale`

#### Jhaele's Farm

| Property | Value |
|---|---|
| uid | `loc-jhaele-farm` |
| label | Location |
| tier | adventure |
| name | Jhaele Silvermane's Farm |
| summary | A tidy working farm. The barn is the PCs' lodging. Elminster visits for breakfast and stays most of the day. Central hub between the two combat paths. |
| type | settlement-building |
| source_adventure | `adv-troubles-of-shadowdale` |

**Relationship:** `loc-jhaele-farm` -[:PART_OF]-> `global-location-shadowdale`

#### Temple of Tymora

| Property | Value |
|---|---|
| uid | `loc-temple-tymora` |
| label | Location |
| tier | adventure |
| name | Temple of Tymora, Shadowdale |
| summary | Active temple run by Sister Maeris. Has an attached walled graveyard where the Graveyard Skulker is currently hiding. |
| type | temple |
| source_adventure | `adv-troubles-of-shadowdale` |

**Relationship:** `loc-temple-tymora` -[:PART_OF]-> `global-location-shadowdale`

#### Temple Graveyard

| Property | Value |
|---|---|
| uid | `loc-temple-graveyard` |
| label | Location |
| tier | adventure |
| name | Temple of Tymora Graveyard |
| summary | Walled graveyard adjacent to the temple. Difficult terrain between headstones. A freshly dug grave is occupied by the Graveyard Skulker. |
| type | outdoor-area |
| source_adventure | `adv-troubles-of-shadowdale` |

**Relationship:** `loc-temple-graveyard` -[:PART_OF]-> `loc-temple-tymora`

#### The Mill

| Property | Value |
|---|---|
| uid | `loc-the-mill` |
| label | Location |
| tier | adventure |
| name | Shadowdale Mill |
| summary | Working mill on the River Ashaba. The millpond is home to the Millpond Horror. Evidence of deer hunting visible nearby. Sylune's Hut is close by with an injured horse tied outside. |
| type | settlement-building |
| source_adventure | `adv-troubles-of-shadowdale` |

**Relationships:**
- `loc-the-mill` -[:PART_OF]-> `global-location-shadowdale`
- `loc-the-mill` -[:LOCATED_IN]-> `global-location-river-ashaba`

#### Millpond

| Property | Value |
|---|---|
| uid | `loc-millpond` |
| label | Location |
| tier | adventure |
| name | Millpond |
| summary | Deep pond feeding the mill. Aquatic terrain. PCs fighting here are at a disadvantage. The pipe is magically protected for now by the monster's presence. |
| type | body-of-water |
| source_adventure | `adv-troubles-of-shadowdale` |

**Relationship:** `loc-millpond` -[:PART_OF]-> `loc-the-mill`

#### Sylune's Hut

| Property | Value |
|---|---|
| uid | `loc-sylunes-hut` |
| label | Location |
| tier | adventure |
| name | Sylune's Hut |
| summary | A hut near the mill. A horse tied outside was injured by the Millpond Horror — visible clue for alert PCs. |
| type | settlement-building |
| source_adventure | `adv-troubles-of-shadowdale` |

**Relationship:** `loc-sylunes-hut` -[:PART_OF]-> `global-location-shadowdale`

#### Castle Grimstead Ruins

| Property | Value |
|---|---|
| uid | `loc-castle-grimstead` |
| label | Location |
| tier | adventure |
| name | Ruins of Castle Grimstead |
| summary | Ruined castle in the forest near Cavenauth. The Graveyard Skulker retreats here if driven from the graveyard. No significant other occupants currently. Rubble and collapsed walls for terrain. |
| type | ruins |
| source_adventure | `adv-troubles-of-shadowdale` |

**Relationship:** `loc-castle-grimstead` -[:PART_OF]-> `global-location-shadowdale`

#### Cavenauth

| Property | Value |
|---|---|
| uid | `loc-cavenauth` |
| label | Location |
| tier | adventure |
| name | Cavenauth |
| summary | Cavern network in the forest near Castle Grimstead. The entry point both monsters used to reach the surface from the Underdark. If the Skulker is not dealt with at Grimstead, it returns here. |
| type | dungeon-entrance |
| source_adventure | `adv-troubles-of-shadowdale` |

**Relationship:** `loc-cavenauth` -[:PART_OF]-> `global-location-shadowdale`

#### Tower of Ashaba Pool

| Property | Value |
|---|---|
| uid | `loc-tower-pool` |
| label | Location |
| tier | adventure |
| name | Pool beside the Tower of Ashaba |
| summary | A pool next to the Tower of Ashaba. Either monster may appear here the day after escaping from their initial location. Same tactical conditions as the millpond for the Horror. Same open conditions as the graveyard/ruins for the Skulker. |
| type | body-of-water |
| source_adventure | `adv-troubles-of-shadowdale` |

**Relationship:** `loc-tower-pool` -[:PART_OF]-> `global-location-tower-of-ashaba`

---

### Timeline & Historical Events

#### Timeline

| Property | Value |
|---|---|
| uid | `timeline-troubles` |
| label | Timeline |
| tier | adventure |
| name | Shadowdale Troubles Timeline |
| era | Days before and during the adventure |
| description | Tracks events from the monsters' emergence through the adventure's resolution. |

#### Historical Event: The Underdark Battle

| Property | Value |
|---|---|
| uid | `evt-hist-underdark-fight` |
| label | Event |
| tier | adventure |
| name | The Underdark Battle |
| summary | Two Underdark predators fought one another in the tunnels below Shadowdale. Both were wounded. Both subsequently surfaced through Cavenauth. |
| is_historical | true |
| is_anchor | false |
| event_type | revelation |
| source_adventure | `adv-troubles-of-shadowdale` |

**Relationships:**
- `evt-hist-underdark-fight` -[:ON_TIMELINE]-> `timeline-troubles`
- `evt-hist-underdark-fight` -[:OCCURRED_IN]-> `loc-cavenauth`
- `evt-hist-underdark-fight` -[:INVOLVES {role: "combatant"}]-> `npc-monster-graveyard`
- `evt-hist-underdark-fight` -[:INVOLVES {role: "combatant"}]-> `npc-monster-millpond`
- `evt-hist-underdark-fight` -[:CAUSES]-> `evt-hist-pipe-stolen`

#### Historical Event: The Pipe is Stolen

| Property | Value |
|---|---|
| uid | `evt-hist-pipe-stolen` |
| label | Event |
| tier | adventure |
| name | Elminster's Pipe is Stolen |
| summary | Elminster encountered both monsters by chance the day before the PCs arrive. During the encounter the Millpond Horror stole his pipe. |
| is_historical | true |
| is_anchor | false |
| event_type | revelation |
| source_adventure | `adv-troubles-of-shadowdale` |

**Relationships:**
- `evt-hist-pipe-stolen` -[:ON_TIMELINE]-> `timeline-troubles`
- `evt-hist-pipe-stolen` -[:INVOLVES {role: "victim"}]-> `ctx-elminster-troubles`
- `evt-hist-pipe-stolen` -[:INVOLVES {role: "thief"}]-> `npc-monster-millpond`
- `evt-hist-pipe-stolen` -[:PRECEDES {position: 1}]-> `evt-01-arrival`

---

### Plotline

| Property | Value |
|---|---|
| uid | `plot-the-troubles` |
| label | Plotline |
| tier | adventure |
| name | The Troubles of Shadowdale |
| summary | Two wounded Underdark monsters have emerged and are causing problems. Elminster hires the PCs to deal with them. One has his pipe. |
| status | draft |
| theme | ["monster-hunt", "investigation", "social-reward"] |
| source_adventure | `adv-troubles-of-shadowdale` |

---

### Narrative Flow — Events, Choices, Outcomes

All events below belong to `plot-the-troubles` via `PART_OF_PLOTLINE` unless marked `is_historical: true`.

#### Act 1 Events

| uid | name | event_type | is_anchor | summary |
|---|---|---|---|---|
| `evt-01-arrival` | Arrival at Shadowdale Border | scene | false | PCs reach the border of Shadowdale from the northern road. Enchantments would repel uninvited visitors. |
| `evt-02-lettinster` | Lettinster Manifests | scene | false | The letter of introduction flies from the PC's pack, folds into an origami dragon, and introduces itself as Lettinster. |
| `evt-03-led-to-farm` | Led to Jhaele's Farm | transition | false | Lettinster guides the party through Shadowdale to Jhaele Silvermane's farm. |
| `evt-04-jhaele-welcome` | Jhaele Welcomes PCs | scene | false | Jhaele offers the barn, shares food, mentions the wizard will be by for breakfast tomorrow. |
| `evt-05-long-rest` | Long Rest — The Barn | transition | false | The PCs rest in the barn. |
| `evt-06-elminster-arrives` | Elminster Arrives for Breakfast | scene | **true** | Elminster arrives. He does not have his pipe. Breakfast commences. |
| `evt-07-briefing` | The Briefing | scene | **true** | Elminster describes the two monsters, makes his offer, and admits one has his pipe. |

**Act 1 causal chain:**
`evt-01` → `evt-02` → `evt-03` → `evt-04` → `evt-05` → `evt-06` → `evt-07`

**Choice following evt-07:**

| uid | prompt | condition_type |
|---|---|---|
| `choice-01-where-first` | Where do the PCs go first? | optional |

| uid | label | leads_to |
|---|---|---|
| `outcome-01a-temple` | Go to the Temple | `evt-08-temple-approach` |
| `outcome-01b-mill` | Go to the Mill | `evt-12-mill-approach` |

---

#### Act 2A — Temple Path

| uid | name | event_type | is_anchor | summary |
|---|---|---|---|---|
| `evt-08-temple-approach` | Temple Approach — Sister Maeris | scene | false | PCs arrive at the Temple of Tymora. Sister Maeris is unimpressed and unhappy. She tells them where the monster is. |
| `evt-09-graveyard-investigation` | Graveyard Investigation | scene | false | PCs enter the graveyard and locate the freshly dug grave. |

**Choice following evt-09:**

| uid | prompt | condition_type |
|---|---|---|
| `choice-02-stealth-or-direct` | Stealth or direct approach? | optional |

| uid | label | leads_to |
|---|---|---|
| `outcome-02a-stealth` | Attempt stealth | `evt-10a-stealth-contest` |
| `outcome-02b-direct` | Walk in directly | `evt-10b-standup-fight` |

| uid | name | event_type | summary |
|---|---|---|---|
| `evt-10a-stealth-contest` | Stealth Contest | scene | Party Stealth vs monster passive awareness DC 13. Success grants surprise round. |
| `evt-10b-standup-fight` | Standup Fight — Graveyard | combat | Direct combat. Monster aware and defensive. |

Both `evt-10a` and `evt-10b` -[:LEADS_TO]-> `evt-11-skulker-outcome` *(merge)*

| uid | name | event_type | is_anchor | summary |
|---|---|---|---|---|
| `evt-11-skulker-outcome` | Skulker Combat Outcome | scene | false | Combat resolves. Did the Skulker flee or die? |

**Choice following evt-11:**

| uid | prompt |
|---|---|
| `choice-03-skulker-fled` | Did the Skulker escape at 50% HP? |

| uid | label | leads_to |
|---|---|---|
| `outcome-03a-fled` | Skulker fled to Castle Grimstead | `evt-11a-skulker-grimstead` |
| `outcome-03b-dead` | Skulker killed at graveyard | `evt-11d-skulker-dead` |

| uid | name | event_type | summary |
|---|---|---|---|
| `evt-11a-skulker-grimstead` | Skulker at Castle Grimstead | transition | The Skulker has retreated to the ruins. PCs must decide whether to pursue. |

**Choice following evt-11a:**

| uid | prompt |
|---|---|
| `choice-04-pursue-grimstead` | Pursue to Castle Grimstead? |

| uid | label | leads_to |
|---|---|---|
| `outcome-04a-pursue` | Pursue to Grimstead | `evt-11b-grimstead-fight` |
| `outcome-04b-no-pursue` | Do not pursue | `evt-11c-skulker-gone` |

| uid | name | event_type | summary |
|---|---|---|---|
| `evt-11b-grimstead-fight` | Fight at Castle Grimstead | combat | Same monster, ruined castle terrain. Flees at 25% HP to Cavenauth and the Underdark. |

**Choice following evt-11b:**

| uid | prompt |
|---|---|
| `choice-05-grimstead-result` | Did the Skulker escape at 25% HP? |

| uid | label | leads_to |
|---|---|---|
| `outcome-05a-escaped-underdark` | Escaped to Underdark | `evt-11c-skulker-gone` |
| `outcome-05b-killed-grimstead` | Skulker killed at Grimstead | `evt-11d-skulker-dead` |

| uid | name | event_type | is_anchor | summary |
|---|---|---|---|---|
| `evt-11c-skulker-gone` | Skulker Returns to Underdark | transition | false | The Skulker escapes back underground, either by fleeing or because night fell. |
| `evt-11d-skulker-dead` | Skulker Defeated | transition | false | The Skulker is dead. |

Both `evt-11c` and `evt-11d` -[:LEADS_TO]-> `evt-merge-a-temple-complete` *(merge)*

| uid | name | event_type | is_anchor | summary |
|---|---|---|---|---|
| `evt-merge-a-temple-complete` | Temple Path Complete | transition | **true** | The temple threat is resolved, one way or another. |

---

#### Act 2B — Mill Path

| uid | name | event_type | is_anchor | summary |
|---|---|---|---|---|
| `evt-12-mill-approach` | Mill Approach — The Millpond | scene | false | PCs arrive at the mill. The pond is still. Evidence of the Horror is present if they look. |
| `evt-13-mill-investigation` | Investigate the Mill Area | scene | false | DC 12 Perception/Survival: deer remains. DC 10 Perception: injured horse at Sylune's Hut. |

**Choice following evt-13:**

| uid | prompt |
|---|---|
| `choice-06-water-or-land` | Fight in the water or lure to land? |

| uid | label | leads_to |
|---|---|---|
| `outcome-06a-water` | Fight in the water | `evt-14a-water-combat` |
| `outcome-06b-land` | Lure to land | `evt-14b-land-combat` |

**Water Combat Branch:**

| uid | name | event_type | summary |
|---|---|---|---|
| `evt-14a-water-combat` | Underwater Combat | combat | PCs at disadvantage. Monster at home. Pipe protected while monster lives. |

**Choice following evt-14a:**

| uid | prompt |
|---|---|
| `choice-07-pipe-water` | What is the pipe's status after the water fight? |

| uid | label | leads_to |
|---|---|---|
| `outcome-07a-pipe-first-water` | Took pipe before kill — undamaged, waterlogged | `evt-merge-b-mill-complete` |
| `outcome-07b-kill-first-water` | Killed monster, pipe still held — waterlogged | `evt-merge-b-mill-complete` |
| `outcome-07c-horror-escaped-water` | Monster escaped at 25% HP | `evt-15a-tower-pool` |

**Land Combat Branch:**

| uid | name | event_type | summary |
|---|---|---|---|
| `evt-14b-land-combat` | Land Combat | combat | Monster lured from pond. Monster at disadvantage on land. |

**Choice following evt-14b:**

| uid | prompt |
|---|---|
| `choice-08-pipe-land` | What is the pipe's status after the land fight? |

| uid | label | leads_to |
|---|---|---|
| `outcome-08a-pipe-first-land` | Took pipe before kill — undamaged, dry | `evt-merge-b-mill-complete` |
| `outcome-08b-kill-first-land` | Killed monster, pipe still held — damaged | `evt-merge-b-mill-complete` |
| `outcome-08c-horror-escaped-land` | Monster escaped at 50% HP | `evt-15a-tower-pool` |

**Tower Pool (escape follow-up):**

| uid | name | event_type | is_anchor | summary |
|---|---|---|---|---|
| `evt-15a-tower-pool` | The Horror at the Tower Pool | scene | false | The Millpond Horror reappears the next day at the pool beside the Tower of Ashaba. Same tactical structure as the millpond. |

**Choice following evt-15a (mirrors choices 07/08):**

| uid | prompt |
|---|---|
| `choice-09-tower-pool-fight` | Water or land at the tower pool? Same structure as mill. |

All tower pool outcomes -[:LEADS_TO]-> `evt-merge-b-mill-complete`

| uid | name | event_type | is_anchor | summary |
|---|---|---|---|---|
| `evt-merge-b-mill-complete` | Mill Path Complete | transition | **true** | The mill/pond threat is resolved. Pipe status is now determined. |

---

#### Act 3 — Resolution

`evt-merge-a-temple-complete` and `evt-merge-b-mill-complete` both -[:LEADS_TO]-> `evt-16-return-to-farm` *(grand merge)*

| uid | name | event_type | is_anchor | summary |
|---|---|---|---|---|
| `evt-16-return-to-farm` | Return to Jhaele's Farm | scene | **true** | Both paths converge. The PCs return to the farm with their results. Elminster is there. |

**Choice following evt-16:**

| uid | prompt |
|---|---|
| `choice-10-pipe-status` | What state is the pipe in? |

| uid | label | leads_to |
|---|---|---|
| `outcome-10a-pipe-fine` | Pipe returned undamaged and dry | `evt-17a-elminster-delighted` |
| `outcome-10b-pipe-waterlogged` | Pipe returned waterlogged | `evt-17b-elminster-pouts` |
| `outcome-10c-pipe-damaged` | Pipe returned damaged | `evt-17c-elminster-accepts` |
| `outcome-10d-no-pipe` | Pipe not returned | `evt-17d-elminster-disappointed` |

| uid | name | event_type | summary |
|---|---|---|---|
| `evt-17a-elminster-delighted` | Elminster Delighted | scene | Eyes light up. Genuine gratitude. Produces a minor magic item as additional reward. |
| `evt-17b-elminster-pouts` | Elminster Pouts | scene | Takes the pipe. Dries it with a cantrip while sighing. Extra gold as consolation. |
| `evt-17c-elminster-accepts` | Elminster Accepts | scene | Takes the pipe quietly. Thanks them neutrally. No extra reward. |
| `evt-17d-elminster-disappointed` | Elminster Disappointed | scene | Says nothing about the pipe. Heavier silence. Pays for monster work only. |

All of evt-17a/b/c/d -[:LEADS_TO]-> `evt-18-payment` *(merge)*

| uid | name | event_type | is_anchor | summary |
|---|---|---|---|---|
| `evt-18-payment` | Elminster Pays, Thanks the PCs | scene | **true** | Elminster pays for each monster dealt with. Pipe reward (if any) already handled. Thanks are given. |
| `evt-19-final-night` | Final Night in the Barn | transition | **true** | PCs are offered one more night. They are asked — politely but firmly — to leave in the morning. |
| `evt-20-adventure-end` | Adventure End | transition | **true** | The party departs Shadowdale. |

**Final causal chain:** `evt-18` → `evt-19` → `evt-20`

---

### Encounters

#### Graveyard Stealth Contest

| Property | Value |
|---|---|
| uid | `enc-graveyard-stealth` |
| label | SkillChallenge |
| tier | adventure |
| name | Finding the Skulker |
| summary | Party Stealth vs monster passive awareness. Success grants a surprise round in the following combat. Failure means it is aware and defensive. |
| skills_involved | ["Stealth"] |
| dc | 13 |
| consequences | "Success: surprise round. Failure: monster is defensive, no surprise." |
| source_adventure | `adv-troubles-of-shadowdale` |

**Relationship:** `enc-graveyard-stealth` -[:LOCATED_IN]-> `loc-temple-graveyard`

#### Graveyard Fight

| Property | Value |
|---|---|
| uid | `enc-graveyard-fight` |
| label | Combat |
| tier | adventure |
| name | The Graveyard Skulker — Graveyard Fight |
| summary | Combat in the walled graveyard. Difficult terrain between headstones. Monster flees at 50% HP toward Castle Grimstead. |
| cr | 2 |
| xp | 450 |
| terrain | graveyard — difficult terrain between headstones |
| tactics | Defensive, uses graves as cover, bolts at 50% HP |
| source_adventure | `adv-troubles-of-shadowdale` |

**Relationships:**
- `enc-graveyard-fight` -[:LOCATED_IN]-> `loc-temple-graveyard`
- `enc-graveyard-fight` -[:PARTICIPANT_IN]-> `npc-monster-graveyard`
- `enc-graveyard-fight` -[:TRIGGERED_BY]-> `evt-10b-standup-fight`

#### Castle Grimstead Fight

| Property | Value |
|---|---|
| uid | `enc-grimstead-fight` |
| label | Combat |
| tier | adventure |
| name | The Graveyard Skulker — Grimstead Fight |
| summary | Same monster, now at Castle Grimstead ruins. Flees at 25% HP back to Cavenauth and the Underdark. |
| cr | 2 |
| xp | 450 |
| terrain | ruined castle — rubble and collapsed walls |
| tactics | More desperate, uses rubble for cover, hard retreat at 25% HP |
| source_adventure | `adv-troubles-of-shadowdale` |

**Relationships:**
- `enc-grimstead-fight` -[:LOCATED_IN]-> `loc-castle-grimstead`
- `enc-grimstead-fight` -[:PARTICIPANT_IN]-> `npc-monster-graveyard`
- `enc-grimstead-fight` -[:TRIGGERED_BY]-> `evt-11b-grimstead-fight`

#### Millpond Investigation

| Property | Value |
|---|---|
| uid | `enc-millpond-investigation` |
| label | SkillChallenge |
| tier | adventure |
| name | Reading the Millpond |
| summary | PCs investigate the mill area for signs of the Horror. DC 12 Perception or Survival for deer remains. DC 10 Perception for the injured horse at Sylune's Hut. |
| skills_involved | ["Perception", "Survival", "Investigation"] |
| dc | 12 |
| consequences | "Success: informed tactical choices about luring the monster. Failure: PCs may not think to lure it." |
| source_adventure | `adv-troubles-of-shadowdale` |

**Relationship:** `enc-millpond-investigation` -[:LOCATED_IN]-> `loc-the-mill`

#### Millpond Combat — Water Fight

| Property | Value |
|---|---|
| uid | `enc-millpond-water` |
| label | Combat |
| tier | adventure |
| name | The Millpond Horror — Aquatic Fight |
| summary | PCs fighting in the water are at a disadvantage. Monster is fully in its element. Flees at 25% HP. Pipe takes water damage unless retrieved before the monster dies. |
| cr | 3 |
| xp | 700 |
| terrain | deep millpond — aquatic, PCs at disadvantage |
| tactics | Aggressive in water, uses depth and current, retreats at 25% HP |
| source_adventure | `adv-troubles-of-shadowdale` |

**Relationships:**
- `enc-millpond-water` -[:LOCATED_IN]-> `loc-millpond`
- `enc-millpond-water` -[:PARTICIPANT_IN]-> `npc-monster-millpond`

#### Millpond Combat — Land Fight

| Property | Value |
|---|---|
| uid | `enc-millpond-land` |
| label | Combat |
| tier | adventure |
| name | The Millpond Horror — Land Fight |
| summary | Monster lured out of the pond. Monster at disadvantage on land. Flees at 50% HP. Pipe is damaged if the monster dies with it. |
| cr | 3 |
| xp | 700 |
| terrain | mill yard — open ground, pond edge nearby |
| tactics | Slower and clumsier on land, always tries to return to water, retreats at 50% HP |
| source_adventure | `adv-troubles-of-shadowdale` |

**Relationships:**
- `enc-millpond-land` -[:LOCATED_IN]-> `loc-the-mill`
- `enc-millpond-land` -[:PARTICIPANT_IN]-> `npc-monster-millpond`

#### Tower Pool Combat

| Property | Value |
|---|---|
| uid | `enc-tower-pool` |
| label | Combat |
| tier | adventure |
| name | The Millpond Horror — Tower Pool |
| summary | If the Horror escaped, it reappears at the Tower of Ashaba pool the next day. Identical tactical conditions and pipe-outcome logic to the millpond. |
| cr | 3 |
| xp | 700 |
| terrain | tower pool — same aquatic conditions as millpond |
| tactics | Identical to millpond — aggressive in water, retreats at 25% HP (water) or 50% HP (land) |
| source_adventure | `adv-troubles-of-shadowdale` |

**Relationships:**
- `enc-tower-pool` -[:LOCATED_IN]-> `loc-tower-pool`
- `enc-tower-pool` -[:PARTICIPANT_IN]-> `npc-monster-millpond`

---

### Boxed Text Sequences

#### BTS-01: Lettinster's Introduction
*(All three boxes are unwritten prose backlog — no FileRef)*

| uid | bts_uid | sequence_position | trigger_summary | content_summary | tone | condition | condition_type |
|---|---|---|---|---|---|---|---|
| `bt-lettinster-01` | `bts-lettinster-intro` | 1 | Party reaches the Shadowdale border | Letter flies from pack, folds into origami dragon | whimsical | null | null |
| `bt-lettinster-02` | `bts-lettinster-intro` | 2 | Dragon animates | Dragon speaks — male voice doing a bad female impression, introduces itself as Lettinster | whimsical | null | null |
| `bt-lettinster-03` | `bts-lettinster-intro` | 3 | After introduction | Lettinster explains it is a homunculus and offers to guide them | whimsical | null | null |

**Sequence attached to:** `evt-02-lettinster`

---

#### BTS-02: Elminster's Briefing
*(BT-3a/3b are mutually exclusive — Insight check variant)*

| uid | sequence_position | trigger_summary | content_summary | tone | condition | condition_type |
|---|---|---|---|---|---|---|
| `bt-briefing-01` | 1 | Elminster sits down at breakfast | Elminster performs being a tired old man | neutral | null | null |
| `bt-briefing-02` | 2 | After performance | Describes two monsters, locations, offers gold payment | neutral | null | null |
| `bt-briefing-03a` | 3 | Player succeeds Insight DC 11 | He is clearly being lazy but his coin is real — the PCs can see it | neutral | `skill:Insight:DC11` | skill_check |
| `bt-briefing-03b` | 3 | Player fails Insight DC 11 | He seems genuinely weary | neutral | null | null |
| `bt-briefing-04` | 4 | After 03a or 03b | Elminster admits he may have run into both monsters yesterday. One has his pipe. | tense | null | null |

- `bt-briefing-03a` -[:ALTERNATIVE_TO {reason: "failed Insight check"}]-> `bt-briefing-03b`
- `bt-briefing-03a` -[:DEPENDS_ON_EVENT]-> `evt-07-briefing`

**Sequence attached to:** `evt-07-briefing`

---

#### BTS-03: Elminster at the Farm — Rest Visits
*(State-dependent dialogue during rest periods)*

| uid | sequence_position | trigger_summary | content_summary | tone | condition | condition_type |
|---|---|---|---|---|---|---|
| `bt-farm-01` | 1 | PCs return to farm to rest | Elminster is chatting with Jhaele — unconditional entry | neutral | null | null |
| `bt-farm-02a` | 2 | Short rest, pipe not returned | Mentions missing his tabac. Asks after the pipe obliquely. | neutral | `event_flag:pipe-not-returned` + `visit_count:jhaele-farm >= 1` | event_flag |
| `bt-farm-02b` | 2 | Long rest, pipe not returned | Grows more concerned — pipe will be lost if monsters go home. | tense | `event_flag:pipe-not-returned` + `event_flag:long-rest-taken` | event_flag |
| `bt-farm-03a` | 3 | A monster escaped | Comments on the monster getting away. Resigned. | neutral | `event_flag:any-monster-escaped` | event_flag |
| `bt-farm-03b` | 3 | Skulker is dead | Comments on the Skulker being dead. Pleased, possibly smug. | neutral | `event_flag:skulker-dead` | event_flag |
| `bt-farm-03c` | 3 | Horror escaped | Comments on the aquatic monster escaping. Worried about the pipe. | tense | `event_flag:horror-escaped` | event_flag |
| `bt-farm-03d` | 3 | Horror is dead | Comments on the Horror's death. Pleased. | neutral | `event_flag:horror-dead` | event_flag |

- `bt-farm-02a` -[:ALTERNATIVE_TO {reason: "long rest vs short rest"}]-> `bt-farm-02b`
- `bt-farm-03a`, `bt-farm-03b`, `bt-farm-03c`, `bt-farm-03d` are all ALTERNATIVE_TO one another
- `bt-farm-02a` -[:DEPENDS_ON_ITEM]-> `global-item-pipe-of-elminster`
- `bt-farm-02b` -[:DEPENDS_ON_ITEM]-> `global-item-pipe-of-elminster`

**Sequence attached to:** `ctx-elminster-troubles` + `loc-jhaele-farm`

---

#### BTS-04: Pipe Return Sequence
*(Four mutually exclusive OPENS_WITH nodes — the entire sequence is a single branch)*

| uid | sequence_position | trigger_summary | content_summary | tone | condition | condition_type |
|---|---|---|---|---|---|---|
| `bt-pipe-01a` | 1 | Pipe returned undamaged and dry | Elminster's eyes light up. Genuine gratitude. Produces magic item. | warm | `possession:pipe-of-elminster:undamaged` | possession |
| `bt-pipe-01b` | 1 | Pipe returned waterlogged | Takes pipe, pouts, dries it with a cantrip while sighing. Extra gold. | neutral | `possession:pipe-of-elminster:waterlogged` | possession |
| `bt-pipe-01c` | 1 | Pipe returned damaged | Takes pipe quietly. Neutral thanks. No extra reward. | neutral | `possession:pipe-of-elminster:damaged` | possession |
| `bt-pipe-01d` | 1 | Pipe not retrieved | Says nothing about the pipe. Heavier silence. | tense | `event_flag:pipe-not-retrieved` | event_flag |

- All four nodes are ALTERNATIVE_TO one another
- All four -[:DEPENDS_ON_ITEM]-> `global-item-pipe-of-elminster`

**Sequence attached to:** `evt-17-elminster-pipe-reaction` (bridging node for evt-17a through evt-17d)

---

### Rumors & Facts

#### Rumor: The Monsters Were Already Wounded

| Property | Value |
|---|---|
| uid | `rumor-monsters-wounded` |
| label | Rumor |
| tier | adventure |
| content | Both monsters were already injured when they surfaced — they fought each other down below. |
| is_true | true |
| spread | local-knowledge |
| source_adventure | `adv-troubles-of-shadowdale` |

**Attached to:** `npc-jhaele-silvermane`, `npc-tymora-priestess` *(shared node — WK-05 test)*

#### Rumor: Elminster Provoked Them

| Property | Value |
|---|---|
| uid | `rumor-elminster-provoked` |
| label | Rumor |
| tier | adventure |
| content | Word is the old wizard poked at them first and that's why one took his pipe. |
| is_true | null |
| spread | local-gossip |
| source_adventure | `adv-troubles-of-shadowdale` |

**Attached to:** `npc-jhaele-silvermane`

#### Fact: Pipe is Magically Protected

| Property | Value |
|---|---|
| uid | `fact-pipe-magic` |
| label | Fact |
| tier | adventure |
| content | Elminster's pipe has minor self-protective magic. It can survive underwater for a limited time without damage. |
| reliability | established |
| source_adventure | `adv-troubles-of-shadowdale` |

**Attached to:** `ctx-elminster-troubles`

#### Fact: No Tavern in Shadowdale

| Property | Value |
|---|---|
| uid | `fact-no-tavern` |
| label | Fact |
| tier | adventure |
| content | Shadowdale has no inn or tavern. Visitors who pass Elminster's enchantments rely on locals for lodging. |
| reliability | established |
| source_adventure | `adv-troubles-of-shadowdale` |

**Attached to:** `global-location-shadowdale`

---

### File References (Planned — No Files Written Yet)

All FileRef nodes below represent planned prose. None have content yet. These form the initial prose writing backlog.

| uid | path | file_type | description | associated_entity_uid |
|---|---|---|---|---|
| `fref-lettinster-intro` | `/adventures/troubles-of-shadowdale/boxed-text/lettinster-introduction.md` | prose | Lettinster manifests and introduces himself | `bts-lettinster-intro` |
| `fref-elminster-briefing` | `/adventures/troubles-of-shadowdale/boxed-text/elminster-briefing.md` | prose | Full briefing scene with Insight check variants | `bts-elminster-briefing` |
| `fref-pipe-return` | `/adventures/troubles-of-shadowdale/boxed-text/pipe-return-variants.md` | prose | All four pipe-return dialogue variants | `bts-pipe-return` |
| `fref-jhaele-welcome` | `/adventures/troubles-of-shadowdale/boxed-text/jhaele-welcome.md` | prose | Jhaele welcomes the PCs to the barn | `evt-04-jhaele-welcome` |
| `fref-temple-approach` | `/adventures/troubles-of-shadowdale/boxed-text/temple-approach.md` | prose | Sister Maeris receives the PCs | `evt-08-temple-approach` |
| `fref-mill-approach` | `/adventures/troubles-of-shadowdale/boxed-text/mill-approach.md` | prose | Arrival at the mill, the stillness of the pond | `evt-12-mill-approach` |

---

## Requirement Coverage

| Category | ID Range | Exercised By |
|---|---|---|
| Graph Integrity | GI-01 to GI-10 | All nodes carry unique uids; FileRef paths are unique; Context node for Elminster has exactly one WITHIN_ADVENTURE and one REPRESENTED_BY |
| Tier & Hierarchy | TH-01 to TH-08 | Elminster (GlobalNPC → NPCContext → Adventure); Pipe (GlobalItem with OWNS, SEEKS, POSSESSES relationships); Lettinster as adventure-only node (promote-to-global candidate for SD testing) |
| Narrative Flow | NF-01 to NF-10 | Full branch at choice-01; internal branches at choice-02 through choice-09; merges at evt-10a/10b→evt-11, evt-11c/11d→evt-merge-a, all mill outcomes→evt-merge-b, evt-merge-a/evt-merge-b→evt-16, evt-17a/b/c/d→evt-18; DAG verified; anchor events marked |
| NPC & Relationships | NR-01 to NR-07 | Elminster opinions on pipe/Jhaele; Jhaele KNOWS Elminster with trust_level; Sister Maeris opinion on Skulker; NPCContext summary overrides Global summary; get_npc_profile exercised on ctx-elminster-troubles |
| World Knowledge | WK-01 to WK-06 | rumor-monsters-wounded shared across two NPCs (WK-05); rumor-elminster-provoked on one NPC; fact-pipe-magic on context node; fact-no-tavern on global location; who_knows_what exercisable on pipe rumor |
| Encounters | EN-01 to EN-06 | 2 SkillChallenges, 5 Combats; all attached to locations; cr/xp on all combat encounters; participant relationships on all combats; enc-graveyard-fight has BoxedText trigger candidate |
| Boxed Text | BT-01 to BT-11 | BTS-01 fully unwritten (backlog test); BTS-02 Insight check alternative pair; BTS-03 multi-condition farm visit sequence; BTS-04 four-way pipe-state ALTERNATIVE_TO set; dependency relationships on pipe item; condition types: skill_check, possession, event_flag, visit_count |
| Timeline & History | TL-01 to TL-06 | timeline-troubles with two historical events (no plotline association); PRECEDES relationship with position property; get_history_for exercisable on Elminster and both monsters |
| Soft Delete | SD-01 to SD-20 | Lettinster is ideal disable test candidate — appears in one event, logically complete; cascade from adv-troubles-of-shadowdale disables all adventure-scoped nodes; shared rumor-monsters-wounded tests shared-node protection; true_delete gate tested via ALLOW_TRUE_DELETE env var |
| Import / Export | IE-01 to IE-10 | Full adventure subgraph exportable; Global nodes (Elminster, pipe, Shadowdale, Tower of Ashaba, River Ashaba) flagged read-only in adventure export; FileRef nodes with planned paths but no content; round-trip fidelity testable against this catalogue |
| MCP Protocol | MP-01 to MP-08 | All 14 tool groups exercised by loading this adventure; error paths testable by attempting duplicate uids, missing nodes, cycle creation |
| Low Verbosity | LV-01 to LV-10 | No prose stored in any node; all summaries are one to two sentences; get_narrative_flow on plot-the-troubles is the large-payload permitted exception |
