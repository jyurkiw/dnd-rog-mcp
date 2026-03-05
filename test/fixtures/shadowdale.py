"""
Fixture builders for the Shadowdale test adventure.

Every builder returns a plain Python dict matching the exact shape of
the corresponding tool call argument. Builders accept keyword overrides
for targeted mutation in unit tests, e.g. make_elminster(disabled=True).

make_full_fixture() assembles the complete NDJSON-envelope dict expected
by import_database(). All other builders are independent.
"""

from datetime import datetime, timezone

# ── Helpers ───────────────────────────────────────────────────────────────────

_NOW = "2024-01-01T00:00:00Z"


def _base(uid: str, tier: str, **overrides) -> dict:
    """Base properties present on every node."""
    return {
        "uid": uid,
        "tier": tier,
        "disabled": False,
        "disabled_by": [],
        "disabled_at": None,
        "created_at": _NOW,
        "updated_at": _NOW,
        **overrides,
    }


# ── Global Nodes ──────────────────────────────────────────────────────────────

def make_elminster(**overrides) -> dict:
    return {
        **_base("global-npc-elminster", "global"),
        "label": "GlobalNPC",
        "canonical_name": "Elminster Aumar",
        "aliases": ["The Old Mage", "El", "The Archmage of Shadowdale"],
        "summary": (
            "Chosen of Mystra, archmage resident of Shadowdale. "
            "Powerful, eccentric, occasionally lazy, always watching."
        ),
        "source": "Forgotten Realms",
        "is_canonical": True,
        **overrides,
    }


def make_pipe_of_elminster(**overrides) -> dict:
    return {
        **_base("global-item-pipe-of-elminster", "global"),
        "label": "GlobalItem",
        "canonical_name": "Pipe of Elminster",
        "summary": (
            "Elminster's favorite smoking pipe. Faintly magical — "
            "self-protects against minor damage. He is unreasonably attached to it."
        ),
        "source": "Forgotten Realms",
        "rarity": "uncommon",
        "is_canonical": True,
        **overrides,
    }


def make_global_shadowdale(**overrides) -> dict:
    return {
        **_base("global-location-shadowdale", "global"),
        "label": "GlobalLocation",
        "canonical_name": "Shadowdale",
        "summary": (
            "A small, insular dale in the Dalelands. No tavern. "
            "Residents value their privacy. Protected by Elminster's enchantments."
        ),
        "source": "Forgotten Realms",
        "region": "The Dalelands",
        "is_canonical": True,
        **overrides,
    }


def make_tower_of_ashaba(**overrides) -> dict:
    return {
        **_base("global-location-tower-of-ashaba", "global"),
        "label": "GlobalLocation",
        "canonical_name": "Tower of Ashaba",
        "summary": (
            "Ancient tower in Shadowdale, seat of the Lord of Shadowdale. "
            "Has a pool beside it that becomes significant if either monster escapes."
        ),
        "source": "Forgotten Realms",
        "region": "Shadowdale",
        "is_canonical": True,
        **overrides,
    }


def make_river_ashaba(**overrides) -> dict:
    return {
        **_base("global-location-river-ashaba", "global"),
        "label": "GlobalLocation",
        "canonical_name": "River Ashaba",
        "summary": "River running through Shadowdale. The mill sits on its bank.",
        "source": "Forgotten Realms",
        "region": "Shadowdale",
        "is_canonical": True,
        **overrides,
    }


# ── Adventure Node ────────────────────────────────────────────────────────────

def make_adventure(**overrides) -> dict:
    return {
        **_base("adv-troubles-of-shadowdale", "adventure"),
        "label": "Adventure",
        "name": "The Troubles of Shadowdale",
        "status": "draft",
        "setting": "Forgotten Realms",
        "tags": ["investigation", "combat", "social", "forgotten-realms", "tier-1"],
        "summary": (
            "PCs arrive in Shadowdale, meet Elminster, and are hired to deal "
            "with two wounded Underdark monsters — one of which has his pipe."
        ),
        **overrides,
    }


# ── Context Nodes ─────────────────────────────────────────────────────────────

def make_elminster_context(**overrides) -> dict:
    return {
        **_base("ctx-elminster-troubles", "context"),
        "label": "NPCContext",
        "role": "quest-giver, recurring presence",
        "status": "alive",
        "summary": (
            "Elminster is between adventures and content to be lazy. "
            "Needs the PCs more than he'll admit. Currently without his pipe."
        ),
        "has_pipe": False,
        "source_adventure": "adv-troubles-of-shadowdale",
        **overrides,
    }


# ── Adventure-Scoped NPCs ─────────────────────────────────────────────────────

def make_jhaele(**overrides) -> dict:
    return {
        **_base("npc-jhaele-silvermane", "adventure"),
        "label": "NPC",
        "name": "Jhaele Silvermane",
        "summary": (
            "Farmer, ex-adventurer. Missing his sword-arm below the elbow. "
            "Generous with his barn, close with Elminster, steady under pressure."
        ),
        "role": "host, information source",
        "source_adventure": "adv-troubles-of-shadowdale",
        **overrides,
    }


def make_lettinster(**overrides) -> dict:
    return {
        **_base("npc-lettinster", "adventure"),
        "label": "NPC",
        "name": "Lettinster",
        "summary": (
            "A homunculus made from the PCs' letter of introduction. "
            "Folds itself into an origami dragon. Speaks in a male voice "
            "badly pretending to be female. Guides approved visitors into the dale."
        ),
        "role": "guide, comic relief",
        "source_adventure": "adv-troubles-of-shadowdale",
        **overrides,
    }


def make_sister_maeris(**overrides) -> dict:
    return {
        **_base("npc-tymora-priestess", "adventure"),
        "label": "NPC",
        "name": "Sister Maeris Ondil",
        "summary": (
            "Middle-aged priestess running the Temple of Tymora. "
            "No sense of humor. Deeply unhappy about the monster in her graveyard. "
            "Will not fight but will not obstruct the PCs."
        ),
        "role": "information source, atmosphere",
        "source_adventure": "adv-troubles-of-shadowdale",
        **overrides,
    }


def make_graveyard_skulker(**overrides) -> dict:
    return {
        **_base("npc-monster-graveyard", "adventure"),
        "label": "NPC",
        "name": "The Graveyard Skulker",
        "summary": (
            "Wounded Underdark predator holed up in a freshly dug grave. "
            "Aggressive when cornered. Flees at 50% HP to Castle Grimstead, "
            "then at 25% retreats to Cavenauth and the Underdark."
        ),
        "role": "antagonist",
        "cr": 2,
        "xp": 450,
        "source_adventure": "adv-troubles-of-shadowdale",
        **overrides,
    }


def make_millpond_horror(**overrides) -> dict:
    return {
        **_base("npc-monster-millpond", "adventure"),
        "label": "NPC",
        "name": "The Millpond Horror",
        "summary": (
            "Wounded aquatic Underdark predator hiding in the millpond. "
            "Has Elminster's pipe. Hunts deer. Injured a horse at Sylune's Hut. "
            "Flees at 25% HP (water) or 50% HP (land) to the Tower of Ashaba pool."
        ),
        "role": "antagonist, pipe-holder",
        "cr": 3,
        "xp": 700,
        "source_adventure": "adv-troubles-of-shadowdale",
        **overrides,
    }


# ── Locations ─────────────────────────────────────────────────────────────────

def make_northern_road_entry(**overrides) -> dict:
    return {
        **_base("loc-northern-road-entry", "adventure"),
        "label": "Location",
        "name": "Northern Road — Shadowdale Border",
        "summary": (
            "Where the northern road enters Shadowdale's territory. "
            "Elminster's enchantments begin here. Where Lettinster manifests."
        ),
        "type": "wilderness",
        "source_adventure": "adv-troubles-of-shadowdale",
        **overrides,
    }


def make_jhaele_farm(**overrides) -> dict:
    return {
        **_base("loc-jhaele-farm", "adventure"),
        "label": "Location",
        "name": "Jhaele Silvermane's Farm",
        "summary": (
            "A tidy working farm. The barn is the PCs' lodging. "
            "Elminster visits for breakfast and stays most of the day. "
            "Central hub between the two combat paths."
        ),
        "type": "settlement-building",
        "source_adventure": "adv-troubles-of-shadowdale",
        **overrides,
    }


def make_temple_tymora(**overrides) -> dict:
    return {
        **_base("loc-temple-tymora", "adventure"),
        "label": "Location",
        "name": "Temple of Tymora, Shadowdale",
        "summary": (
            "Active temple run by Sister Maeris. "
            "Has an attached walled graveyard where the Graveyard Skulker is hiding."
        ),
        "type": "temple",
        "source_adventure": "adv-troubles-of-shadowdale",
        **overrides,
    }


def make_temple_graveyard(**overrides) -> dict:
    return {
        **_base("loc-temple-graveyard", "adventure"),
        "label": "Location",
        "name": "Temple of Tymora Graveyard",
        "summary": (
            "Walled graveyard adjacent to the temple. "
            "Difficult terrain between headstones. "
            "A freshly dug grave is occupied by the Graveyard Skulker."
        ),
        "type": "outdoor-area",
        "source_adventure": "adv-troubles-of-shadowdale",
        **overrides,
    }


def make_the_mill(**overrides) -> dict:
    return {
        **_base("loc-the-mill", "adventure"),
        "label": "Location",
        "name": "Shadowdale Mill",
        "summary": (
            "Working mill on the River Ashaba. The millpond is home to the Horror. "
            "Evidence of deer hunting visible nearby. "
            "Sylune's Hut is close by with an injured horse outside."
        ),
        "type": "settlement-building",
        "source_adventure": "adv-troubles-of-shadowdale",
        **overrides,
    }


def make_millpond(**overrides) -> dict:
    return {
        **_base("loc-millpond", "adventure"),
        "label": "Location",
        "name": "Millpond",
        "summary": (
            "Deep pond feeding the mill. Aquatic terrain. "
            "PCs fighting here are at a disadvantage. "
            "The pipe is magically protected while the monster is alive."
        ),
        "type": "body-of-water",
        "source_adventure": "adv-troubles-of-shadowdale",
        **overrides,
    }


def make_sylunes_hut(**overrides) -> dict:
    return {
        **_base("loc-sylunes-hut", "adventure"),
        "label": "Location",
        "name": "Sylune's Hut",
        "summary": (
            "A hut near the mill. A horse tied outside was injured by the "
            "Millpond Horror — visible clue for alert PCs."
        ),
        "type": "settlement-building",
        "source_adventure": "adv-troubles-of-shadowdale",
        **overrides,
    }


def make_castle_grimstead(**overrides) -> dict:
    return {
        **_base("loc-castle-grimstead", "adventure"),
        "label": "Location",
        "name": "Ruins of Castle Grimstead",
        "summary": (
            "Ruined castle in the forest near Cavenauth. "
            "The Graveyard Skulker retreats here if driven from the graveyard. "
            "Rubble and collapsed walls for terrain."
        ),
        "type": "ruins",
        "source_adventure": "adv-troubles-of-shadowdale",
        **overrides,
    }


def make_cavenauth(**overrides) -> dict:
    return {
        **_base("loc-cavenauth", "adventure"),
        "label": "Location",
        "name": "Cavenauth",
        "summary": (
            "Cavern network in the forest near Castle Grimstead. "
            "The entry point both monsters used to reach the surface. "
            "If the Skulker is not dealt with at Grimstead, it returns here."
        ),
        "type": "dungeon-entrance",
        "source_adventure": "adv-troubles-of-shadowdale",
        **overrides,
    }


def make_tower_pool(**overrides) -> dict:
    return {
        **_base("loc-tower-pool", "adventure"),
        "label": "Location",
        "name": "Pool beside the Tower of Ashaba",
        "summary": (
            "A pool next to the Tower of Ashaba. Either monster may appear here "
            "the day after escaping. Same tactical conditions as the millpond."
        ),
        "type": "body-of-water",
        "source_adventure": "adv-troubles-of-shadowdale",
        **overrides,
    }


# ── Timeline ──────────────────────────────────────────────────────────────────

def make_timeline(**overrides) -> dict:
    return {
        **_base("timeline-troubles", "adventure"),
        "label": "Timeline",
        "name": "Shadowdale Troubles Timeline",
        "era": "Days before and during the adventure",
        "description": (
            "Tracks events from the monsters' emergence through the "
            "adventure's resolution."
        ),
        "source_adventure": "adv-troubles-of-shadowdale",
        **overrides,
    }


# ── Historical Events ─────────────────────────────────────────────────────────

def make_evt_underdark_fight(**overrides) -> dict:
    return {
        **_base("evt-hist-underdark-fight", "adventure"),
        "label": "Event",
        "name": "The Underdark Battle",
        "summary": (
            "Two Underdark predators fought one another in the tunnels below "
            "Shadowdale. Both were wounded. Both subsequently surfaced through Cavenauth."
        ),
        "is_historical": True,
        "is_anchor": False,
        "event_type": "revelation",
        "source_adventure": "adv-troubles-of-shadowdale",
        **overrides,
    }


def make_evt_pipe_stolen(**overrides) -> dict:
    return {
        **_base("evt-hist-pipe-stolen", "adventure"),
        "label": "Event",
        "name": "Elminster's Pipe is Stolen",
        "summary": (
            "Elminster encountered both monsters by chance the day before the "
            "PCs arrive. During the encounter the Millpond Horror stole his pipe."
        ),
        "is_historical": True,
        "is_anchor": False,
        "event_type": "revelation",
        "source_adventure": "adv-troubles-of-shadowdale",
        **overrides,
    }


# ── Plotline ──────────────────────────────────────────────────────────────────

def make_plotline(**overrides) -> dict:
    return {
        **_base("plot-the-troubles", "adventure"),
        "label": "Plotline",
        "name": "The Troubles of Shadowdale",
        "summary": (
            "Two wounded Underdark monsters have emerged and are causing problems. "
            "Elminster hires the PCs to deal with them. One has his pipe."
        ),
        "status": "draft",
        "theme": ["monster-hunt", "investigation", "social-reward"],
        "source_adventure": "adv-troubles-of-shadowdale",
        **overrides,
    }


# ── Act 1 Events ──────────────────────────────────────────────────────────────

def make_act1_events(**overrides) -> list[dict]:
    base = "adv-troubles-of-shadowdale"
    return [
        {**_base("evt-01-arrival", "adventure"), "label": "Event",
         "name": "Arrival at Shadowdale Border", "event_type": "scene",
         "is_anchor": False, "is_historical": False,
         "summary": "PCs reach the border from the northern road.",
         "source_adventure": base},
        {**_base("evt-02-lettinster", "adventure"), "label": "Event",
         "name": "Lettinster Manifests", "event_type": "scene",
         "is_anchor": False, "is_historical": False,
         "summary": "The letter flies out, folds into an origami dragon, introduces itself.",
         "source_adventure": base},
        {**_base("evt-03-led-to-farm", "adventure"), "label": "Event",
         "name": "Led to Jhaele's Farm", "event_type": "transition",
         "is_anchor": False, "is_historical": False,
         "summary": "Lettinster guides the party to Jhaele Silvermane's farm.",
         "source_adventure": base},
        {**_base("evt-04-jhaele-welcome", "adventure"), "label": "Event",
         "name": "Jhaele Welcomes PCs", "event_type": "scene",
         "is_anchor": False, "is_historical": False,
         "summary": "Jhaele offers the barn, mentions the wizard will come for breakfast.",
         "source_adventure": base},
        {**_base("evt-05-long-rest", "adventure"), "label": "Event",
         "name": "Long Rest — The Barn", "event_type": "transition",
         "is_anchor": False, "is_historical": False,
         "summary": "The PCs rest in the barn.",
         "source_adventure": base},
        {**_base("evt-06-elminster-arrives", "adventure"), "label": "Event",
         "name": "Elminster Arrives for Breakfast", "event_type": "scene",
         "is_anchor": True, "is_historical": False,
         "summary": "Elminster arrives. He does not have his pipe.",
         "source_adventure": base},
        {**_base("evt-07-briefing", "adventure"), "label": "Event",
         "name": "The Briefing", "event_type": "scene",
         "is_anchor": True, "is_historical": False,
         "summary": "Elminster describes the two monsters, makes his offer, admits one has his pipe.",
         "source_adventure": base},
    ]


# ── Act 2A Events ─────────────────────────────────────────────────────────────

def make_act2a_events() -> list[dict]:
    base = "adv-troubles-of-shadowdale"
    return [
        {**_base("evt-08-temple-approach", "adventure"), "label": "Event",
         "name": "Temple Approach — Sister Maeris", "event_type": "scene",
         "is_anchor": False, "is_historical": False,
         "summary": "PCs arrive at the Temple of Tymora. Sister Maeris tells them where the monster is.",
         "source_adventure": base},
        {**_base("evt-09-graveyard-investigation", "adventure"), "label": "Event",
         "name": "Graveyard Investigation", "event_type": "scene",
         "is_anchor": False, "is_historical": False,
         "summary": "PCs enter the graveyard and locate the freshly dug grave.",
         "source_adventure": base},
        {**_base("evt-10a-stealth-contest", "adventure"), "label": "Event",
         "name": "Stealth Contest", "event_type": "scene",
         "is_anchor": False, "is_historical": False,
         "summary": "Party Stealth vs monster passive awareness DC 13. Success grants surprise round.",
         "source_adventure": base},
        {**_base("evt-10b-standup-fight", "adventure"), "label": "Event",
         "name": "Standup Fight — Graveyard", "event_type": "combat",
         "is_anchor": False, "is_historical": False,
         "summary": "Direct combat. Monster aware and defensive.",
         "source_adventure": base},
        {**_base("evt-11-skulker-outcome", "adventure"), "label": "Event",
         "name": "Skulker Combat Outcome", "event_type": "scene",
         "is_anchor": False, "is_historical": False,
         "summary": "Combat resolves. Did the Skulker flee or die?",
         "source_adventure": base},
        {**_base("evt-11a-skulker-grimstead", "adventure"), "label": "Event",
         "name": "Skulker at Castle Grimstead", "event_type": "transition",
         "is_anchor": False, "is_historical": False,
         "summary": "The Skulker has retreated to the ruins. PCs must decide whether to pursue.",
         "source_adventure": base},
        {**_base("evt-11b-grimstead-fight", "adventure"), "label": "Event",
         "name": "Fight at Castle Grimstead", "event_type": "combat",
         "is_anchor": False, "is_historical": False,
         "summary": "Same monster, ruined castle terrain. Flees at 25% HP to Cavenauth.",
         "source_adventure": base},
        {**_base("evt-11c-skulker-gone", "adventure"), "label": "Event",
         "name": "Skulker Returns to Underdark", "event_type": "transition",
         "is_anchor": False, "is_historical": False,
         "summary": "The Skulker escapes back underground.",
         "source_adventure": base},
        {**_base("evt-11d-skulker-dead", "adventure"), "label": "Event",
         "name": "Skulker Defeated", "event_type": "transition",
         "is_anchor": False, "is_historical": False,
         "summary": "The Skulker is dead.",
         "source_adventure": base},
        {**_base("evt-merge-a-temple-complete", "adventure"), "label": "Event",
         "name": "Temple Path Complete", "event_type": "transition",
         "is_anchor": True, "is_historical": False,
         "summary": "The temple threat is resolved, one way or another.",
         "source_adventure": base},
    ]


# ── Act 2B Events ─────────────────────────────────────────────────────────────

def make_act2b_events() -> list[dict]:
    base = "adv-troubles-of-shadowdale"
    return [
        {**_base("evt-12-mill-approach", "adventure"), "label": "Event",
         "name": "Mill Approach — The Millpond", "event_type": "scene",
         "is_anchor": False, "is_historical": False,
         "summary": "PCs arrive at the mill. The pond is still. Evidence of the Horror is present.",
         "source_adventure": base},
        {**_base("evt-13-mill-investigation", "adventure"), "label": "Event",
         "name": "Investigate the Mill Area", "event_type": "scene",
         "is_anchor": False, "is_historical": False,
         "summary": "DC 12 Perception/Survival: deer remains. DC 10 Perception: injured horse.",
         "source_adventure": base},
        {**_base("evt-14a-water-combat", "adventure"), "label": "Event",
         "name": "Underwater Combat", "event_type": "combat",
         "is_anchor": False, "is_historical": False,
         "summary": "PCs at disadvantage in water. Monster at home. Pipe protected while monster lives.",
         "source_adventure": base},
        {**_base("evt-14b-land-combat", "adventure"), "label": "Event",
         "name": "Land Combat", "event_type": "combat",
         "is_anchor": False, "is_historical": False,
         "summary": "Monster lured from pond. Monster at disadvantage on land.",
         "source_adventure": base},
        {**_base("evt-15a-tower-pool", "adventure"), "label": "Event",
         "name": "The Horror at the Tower Pool", "event_type": "scene",
         "is_anchor": False, "is_historical": False,
         "summary": "The Horror reappears at the Tower of Ashaba pool the next day.",
         "source_adventure": base},
        {**_base("evt-merge-b-mill-complete", "adventure"), "label": "Event",
         "name": "Mill Path Complete", "event_type": "transition",
         "is_anchor": True, "is_historical": False,
         "summary": "The mill/pond threat is resolved. Pipe status is now determined.",
         "source_adventure": base},
    ]


# ── Act 3 Events ──────────────────────────────────────────────────────────────

def make_act3_events() -> list[dict]:
    base = "adv-troubles-of-shadowdale"
    return [
        {**_base("evt-16-return-to-farm", "adventure"), "label": "Event",
         "name": "Return to Jhaele's Farm", "event_type": "scene",
         "is_anchor": True, "is_historical": False,
         "summary": "Both paths converge. PCs return with their results. Elminster is there.",
         "source_adventure": base},
        {**_base("evt-17a-elminster-delighted", "adventure"), "label": "Event",
         "name": "Elminster Delighted", "event_type": "scene",
         "is_anchor": False, "is_historical": False,
         "summary": "Eyes light up. Genuine gratitude. Produces a minor magic item.",
         "source_adventure": base},
        {**_base("evt-17b-elminster-pouts", "adventure"), "label": "Event",
         "name": "Elminster Pouts", "event_type": "scene",
         "is_anchor": False, "is_historical": False,
         "summary": "Takes the pipe, pouts, dries it with a cantrip. Extra gold.",
         "source_adventure": base},
        {**_base("evt-17c-elminster-accepts", "adventure"), "label": "Event",
         "name": "Elminster Accepts", "event_type": "scene",
         "is_anchor": False, "is_historical": False,
         "summary": "Takes the pipe quietly. Neutral thanks. No extra reward.",
         "source_adventure": base},
        {**_base("evt-17d-elminster-disappointed", "adventure"), "label": "Event",
         "name": "Elminster Disappointed", "event_type": "scene",
         "is_anchor": False, "is_historical": False,
         "summary": "Says nothing about the pipe. Heavier silence. Pays for monster work only.",
         "source_adventure": base},
        {**_base("evt-18-payment", "adventure"), "label": "Event",
         "name": "Elminster Pays, Thanks the PCs", "event_type": "scene",
         "is_anchor": True, "is_historical": False,
         "summary": "Elminster pays for each monster dealt with. Thanks are given.",
         "source_adventure": base},
        {**_base("evt-19-final-night", "adventure"), "label": "Event",
         "name": "Final Night in the Barn", "event_type": "transition",
         "is_anchor": True, "is_historical": False,
         "summary": "PCs offered one more night. Asked to leave in the morning.",
         "source_adventure": base},
        {**_base("evt-20-adventure-end", "adventure"), "label": "Event",
         "name": "Adventure End", "event_type": "transition",
         "is_anchor": True, "is_historical": False,
         "summary": "The party departs Shadowdale.",
         "source_adventure": base},
    ]


# ── Choices ───────────────────────────────────────────────────────────────────

def make_all_choices() -> list[dict]:
    base = "adv-troubles-of-shadowdale"
    return [
        {**_base("choice-01-where-first", "adventure"), "label": "Choice",
         "prompt": "Where do the PCs go first?", "condition_type": "optional",
         "source_adventure": base},
        {**_base("choice-02-stealth-or-direct", "adventure"), "label": "Choice",
         "prompt": "Stealth or direct approach to the graveyard?", "condition_type": "optional",
         "source_adventure": base},
        {**_base("choice-03-skulker-fled", "adventure"), "label": "Choice",
         "prompt": "Did the Skulker escape at 50% HP?", "condition_type": "optional",
         "source_adventure": base},
        {**_base("choice-04-pursue-grimstead", "adventure"), "label": "Choice",
         "prompt": "Pursue to Castle Grimstead?", "condition_type": "optional",
         "source_adventure": base},
        {**_base("choice-05-grimstead-result", "adventure"), "label": "Choice",
         "prompt": "Did the Skulker escape at 25% HP?", "condition_type": "optional",
         "source_adventure": base},
        {**_base("choice-06-water-or-land", "adventure"), "label": "Choice",
         "prompt": "Fight in the water or lure to land?", "condition_type": "optional",
         "source_adventure": base},
        {**_base("choice-07-pipe-water", "adventure"), "label": "Choice",
         "prompt": "What is the pipe's status after the water fight?", "condition_type": "optional",
         "source_adventure": base},
        {**_base("choice-08-pipe-land", "adventure"), "label": "Choice",
         "prompt": "What is the pipe's status after the land fight?", "condition_type": "optional",
         "source_adventure": base},
        {**_base("choice-09-tower-pool-fight", "adventure"), "label": "Choice",
         "prompt": "Water or land at the tower pool?", "condition_type": "optional",
         "source_adventure": base},
        {**_base("choice-10-pipe-status", "adventure"), "label": "Choice",
         "prompt": "What state is the pipe in?", "condition_type": "optional",
         "source_adventure": base},
    ]


# ── Outcomes ──────────────────────────────────────────────────────────────────

def make_all_outcomes() -> list[dict]:
    base = "adv-troubles-of-shadowdale"
    return [
        # Choice 01
        {**_base("outcome-01a-temple", "adventure"), "label": "Outcome",
         "label_text": "Go to the Temple", "leads_to": "evt-08-temple-approach",
         "source_adventure": base},
        {**_base("outcome-01b-mill", "adventure"), "label": "Outcome",
         "label_text": "Go to the Mill", "leads_to": "evt-12-mill-approach",
         "source_adventure": base},
        # Choice 02
        {**_base("outcome-02a-stealth", "adventure"), "label": "Outcome",
         "label_text": "Attempt stealth", "leads_to": "evt-10a-stealth-contest",
         "source_adventure": base},
        {**_base("outcome-02b-direct", "adventure"), "label": "Outcome",
         "label_text": "Walk in directly", "leads_to": "evt-10b-standup-fight",
         "source_adventure": base},
        # Choice 03
        {**_base("outcome-03a-fled", "adventure"), "label": "Outcome",
         "label_text": "Skulker fled to Castle Grimstead", "leads_to": "evt-11a-skulker-grimstead",
         "source_adventure": base},
        {**_base("outcome-03b-dead", "adventure"), "label": "Outcome",
         "label_text": "Skulker killed at graveyard", "leads_to": "evt-11d-skulker-dead",
         "source_adventure": base},
        # Choice 04
        {**_base("outcome-04a-pursue", "adventure"), "label": "Outcome",
         "label_text": "Pursue to Grimstead", "leads_to": "evt-11b-grimstead-fight",
         "source_adventure": base},
        {**_base("outcome-04b-no-pursue", "adventure"), "label": "Outcome",
         "label_text": "Do not pursue", "leads_to": "evt-11c-skulker-gone",
         "source_adventure": base},
        # Choice 05
        {**_base("outcome-05a-escaped-underdark", "adventure"), "label": "Outcome",
         "label_text": "Escaped to Underdark", "leads_to": "evt-11c-skulker-gone",
         "source_adventure": base},
        {**_base("outcome-05b-killed-grimstead", "adventure"), "label": "Outcome",
         "label_text": "Skulker killed at Grimstead", "leads_to": "evt-11d-skulker-dead",
         "source_adventure": base},
        # Choice 06
        {**_base("outcome-06a-water", "adventure"), "label": "Outcome",
         "label_text": "Fight in the water", "leads_to": "evt-14a-water-combat",
         "source_adventure": base},
        {**_base("outcome-06b-land", "adventure"), "label": "Outcome",
         "label_text": "Lure to land", "leads_to": "evt-14b-land-combat",
         "source_adventure": base},
        # Choice 07 (water fight pipe outcomes)
        {**_base("outcome-07a-pipe-first-water", "adventure"), "label": "Outcome",
         "label_text": "Took pipe before kill — undamaged, waterlogged",
         "leads_to": "evt-merge-b-mill-complete", "source_adventure": base},
        {**_base("outcome-07b-kill-first-water", "adventure"), "label": "Outcome",
         "label_text": "Killed monster, pipe still held — waterlogged",
         "leads_to": "evt-merge-b-mill-complete", "source_adventure": base},
        {**_base("outcome-07c-horror-escaped-water", "adventure"), "label": "Outcome",
         "label_text": "Monster escaped at 25% HP", "leads_to": "evt-15a-tower-pool",
         "source_adventure": base},
        # Choice 08 (land fight pipe outcomes)
        {**_base("outcome-08a-pipe-first-land", "adventure"), "label": "Outcome",
         "label_text": "Took pipe before kill — undamaged, dry",
         "leads_to": "evt-merge-b-mill-complete", "source_adventure": base},
        {**_base("outcome-08b-kill-first-land", "adventure"), "label": "Outcome",
         "label_text": "Killed monster, pipe still held — damaged",
         "leads_to": "evt-merge-b-mill-complete", "source_adventure": base},
        {**_base("outcome-08c-horror-escaped-land", "adventure"), "label": "Outcome",
         "label_text": "Monster escaped at 50% HP", "leads_to": "evt-15a-tower-pool",
         "source_adventure": base},
        # Choice 10 (pipe resolution)
        {**_base("outcome-10a-pipe-fine", "adventure"), "label": "Outcome",
         "label_text": "Pipe returned undamaged and dry", "leads_to": "evt-17a-elminster-delighted",
         "source_adventure": base},
        {**_base("outcome-10b-pipe-waterlogged", "adventure"), "label": "Outcome",
         "label_text": "Pipe returned waterlogged", "leads_to": "evt-17b-elminster-pouts",
         "source_adventure": base},
        {**_base("outcome-10c-pipe-damaged", "adventure"), "label": "Outcome",
         "label_text": "Pipe returned damaged", "leads_to": "evt-17c-elminster-accepts",
         "source_adventure": base},
        {**_base("outcome-10d-no-pipe", "adventure"), "label": "Outcome",
         "label_text": "Pipe not returned", "leads_to": "evt-17d-elminster-disappointed",
         "source_adventure": base},
    ]


# ── Encounters ────────────────────────────────────────────────────────────────

def make_encounters() -> list[dict]:
    base = "adv-troubles-of-shadowdale"
    return [
        {**_base("enc-graveyard-stealth", "adventure"), "label": "SkillChallenge",
         "name": "Finding the Skulker",
         "summary": "Party Stealth vs monster passive awareness DC 13. Success grants surprise round.",
         "skills_involved": ["Stealth"], "dc": 13,
         "consequences": "Success: surprise round. Failure: monster is defensive.",
         "location_uid": "loc-temple-graveyard", "source_adventure": base},
        {**_base("enc-graveyard-fight", "adventure"), "label": "Combat",
         "name": "The Graveyard Skulker — Graveyard Fight",
         "summary": "Combat in the walled graveyard. Monster flees at 50% HP.",
         "cr": 2, "xp": 450,
         "terrain": "graveyard — difficult terrain between headstones",
         "tactics": "Defensive, uses graves as cover, bolts at 50% HP",
         "location_uid": "loc-temple-graveyard",
         "participant_uids": ["npc-monster-graveyard"], "source_adventure": base},
        {**_base("enc-grimstead-fight", "adventure"), "label": "Combat",
         "name": "The Graveyard Skulker — Grimstead Fight",
         "summary": "Same monster, Castle Grimstead ruins. Flees at 25% HP to Underdark.",
         "cr": 2, "xp": 450,
         "terrain": "ruined castle — rubble and collapsed walls",
         "tactics": "More desperate, hard retreat at 25% HP",
         "location_uid": "loc-castle-grimstead",
         "participant_uids": ["npc-monster-graveyard"], "source_adventure": base},
        {**_base("enc-millpond-investigation", "adventure"), "label": "SkillChallenge",
         "name": "Reading the Millpond",
         "summary": "Investigate the mill area. DC 12 deer remains. DC 10 injured horse.",
         "skills_involved": ["Perception", "Survival", "Investigation"], "dc": 12,
         "consequences": "Success: informed tactical choices. Failure: may not think to lure.",
         "location_uid": "loc-the-mill", "source_adventure": base},
        {**_base("enc-millpond-water", "adventure"), "label": "Combat",
         "name": "The Millpond Horror — Aquatic Fight",
         "summary": "PCs at disadvantage in water. Flees at 25% HP. Pipe waterlogged unless retrieved first.",
         "cr": 3, "xp": 700,
         "terrain": "deep millpond — aquatic, PCs at disadvantage",
         "tactics": "Aggressive in water, retreats at 25% HP",
         "location_uid": "loc-millpond",
         "participant_uids": ["npc-monster-millpond"], "source_adventure": base},
        {**_base("enc-millpond-land", "adventure"), "label": "Combat",
         "name": "The Millpond Horror — Land Fight",
         "summary": "Monster lured out. Monster at disadvantage on land. Flees at 50% HP.",
         "cr": 3, "xp": 700,
         "terrain": "mill yard — open ground, pond edge nearby",
         "tactics": "Slower on land, tries to return to water, retreats at 50% HP",
         "location_uid": "loc-the-mill",
         "participant_uids": ["npc-monster-millpond"], "source_adventure": base},
        {**_base("enc-tower-pool", "adventure"), "label": "Combat",
         "name": "The Millpond Horror — Tower Pool",
         "summary": "Horror reappears at Tower of Ashaba pool if it escaped. Identical to millpond.",
         "cr": 3, "xp": 700,
         "terrain": "tower pool — same aquatic conditions as millpond",
         "tactics": "Identical to millpond fight",
         "location_uid": "loc-tower-pool",
         "participant_uids": ["npc-monster-millpond"], "source_adventure": base},
    ]


# ── Rumors & Facts ────────────────────────────────────────────────────────────

def make_rumors() -> list[dict]:
    base = "adv-troubles-of-shadowdale"
    return [
        {**_base("rumor-monsters-wounded", "adventure"), "label": "Rumor",
         "content": "Both monsters were already injured when they surfaced — they fought each other down below.",
         "is_true": True, "spread": "local-knowledge",
         "attached_to_uids": ["npc-jhaele-silvermane", "npc-tymora-priestess"],
         "source_adventure": base},
        {**_base("rumor-elminster-provoked", "adventure"), "label": "Rumor",
         "content": "Word is the old wizard poked at them first and that's why one took his pipe.",
         "is_true": None, "spread": "local-gossip",
         "attached_to_uids": ["npc-jhaele-silvermane"],
         "source_adventure": base},
    ]


def make_facts() -> list[dict]:
    base = "adv-troubles-of-shadowdale"
    return [
        {**_base("fact-pipe-magic", "adventure"), "label": "Fact",
         "content": "Elminster's pipe has minor self-protective magic. It can survive underwater for a limited time without damage.",
         "reliability": "established",
         "attached_to_uids": ["ctx-elminster-troubles"],
         "source_adventure": base},
        {**_base("fact-no-tavern", "adventure"), "label": "Fact",
         "content": "Shadowdale has no inn or tavern. Visitors who pass Elminster's enchantments rely on locals for lodging.",
         "reliability": "established",
         "attached_to_uids": ["global-location-shadowdale"],
         "source_adventure": base},
    ]


# ── Relationships ─────────────────────────────────────────────────────────────

def make_relationships() -> list[dict]:
    """
    All relationships in the adventure as dicts with from_uid, to_uid,
    rel_type, and optional properties.
    """
    return [
        # Global ownership
        {"uid": "rel-elminster-owns-pipe", "rel_type": "OWNS",
         "from_uid": "global-npc-elminster", "to_uid": "global-item-pipe-of-elminster"},
        # Context bridges
        {"uid": "rel-elminster-represented-by", "rel_type": "REPRESENTED_BY",
         "from_uid": "global-npc-elminster", "to_uid": "ctx-elminster-troubles"},
        {"uid": "rel-ctx-within-adventure", "rel_type": "WITHIN_ADVENTURE",
         "from_uid": "ctx-elminster-troubles", "to_uid": "adv-troubles-of-shadowdale"},
        {"uid": "rel-elminster-appears-in", "rel_type": "APPEARS_IN_ADVENTURE",
         "from_uid": "global-npc-elminster", "to_uid": "adv-troubles-of-shadowdale"},
        {"uid": "rel-ctx-seeks-pipe", "rel_type": "SEEKS",
         "from_uid": "ctx-elminster-troubles", "to_uid": "global-item-pipe-of-elminster"},
        # Horror possesses pipe
        {"uid": "rel-horror-possesses-pipe", "rel_type": "POSSESSES",
         "from_uid": "npc-monster-millpond", "to_uid": "global-item-pipe-of-elminster",
         "properties": {"status": "stolen"}},
        # NPC relationships
        {"uid": "rel-jhaele-knows-elminster", "rel_type": "KNOWS",
         "from_uid": "npc-jhaele-silvermane", "to_uid": "ctx-elminster-troubles",
         "properties": {"relationship_type": "old friends", "trust_level": 5}},
        # Location hierarchy
        {"uid": "rel-northern-road-part-of-shadowdale", "rel_type": "PART_OF",
         "from_uid": "loc-northern-road-entry", "to_uid": "global-location-shadowdale"},
        {"uid": "rel-farm-part-of-shadowdale", "rel_type": "PART_OF",
         "from_uid": "loc-jhaele-farm", "to_uid": "global-location-shadowdale"},
        {"uid": "rel-temple-part-of-shadowdale", "rel_type": "PART_OF",
         "from_uid": "loc-temple-tymora", "to_uid": "global-location-shadowdale"},
        {"uid": "rel-graveyard-part-of-temple", "rel_type": "PART_OF",
         "from_uid": "loc-temple-graveyard", "to_uid": "loc-temple-tymora"},
        {"uid": "rel-mill-part-of-shadowdale", "rel_type": "PART_OF",
         "from_uid": "loc-the-mill", "to_uid": "global-location-shadowdale"},
        {"uid": "rel-mill-on-river", "rel_type": "LOCATED_IN",
         "from_uid": "loc-the-mill", "to_uid": "global-location-river-ashaba"},
        {"uid": "rel-millpond-part-of-mill", "rel_type": "PART_OF",
         "from_uid": "loc-millpond", "to_uid": "loc-the-mill"},
        {"uid": "rel-sylune-part-of-shadowdale", "rel_type": "PART_OF",
         "from_uid": "loc-sylunes-hut", "to_uid": "global-location-shadowdale"},
        {"uid": "rel-grimstead-part-of-shadowdale", "rel_type": "PART_OF",
         "from_uid": "loc-castle-grimstead", "to_uid": "global-location-shadowdale"},
        {"uid": "rel-cavenauth-part-of-shadowdale", "rel_type": "PART_OF",
         "from_uid": "loc-cavenauth", "to_uid": "global-location-shadowdale"},
        {"uid": "rel-tower-pool-part-of-tower", "rel_type": "PART_OF",
         "from_uid": "loc-tower-pool", "to_uid": "global-location-tower-of-ashaba"},
        # Timeline
        {"uid": "rel-underdark-fight-on-timeline", "rel_type": "ON_TIMELINE",
         "from_uid": "evt-hist-underdark-fight", "to_uid": "timeline-troubles"},
        {"uid": "rel-pipe-stolen-on-timeline", "rel_type": "ON_TIMELINE",
         "from_uid": "evt-hist-pipe-stolen", "to_uid": "timeline-troubles"},
        {"uid": "rel-underdark-causes-pipe-stolen", "rel_type": "CAUSES",
         "from_uid": "evt-hist-underdark-fight", "to_uid": "evt-hist-pipe-stolen"},
        {"uid": "rel-pipe-stolen-precedes-arrival", "rel_type": "PRECEDES",
         "from_uid": "evt-hist-pipe-stolen", "to_uid": "evt-01-arrival",
         "properties": {"position": 1}},
        # Act 1 causal chain
        {"uid": "rel-evt01-02", "rel_type": "CAUSES",
         "from_uid": "evt-01-arrival", "to_uid": "evt-02-lettinster"},
        {"uid": "rel-evt02-03", "rel_type": "CAUSES",
         "from_uid": "evt-02-lettinster", "to_uid": "evt-03-led-to-farm"},
        {"uid": "rel-evt03-04", "rel_type": "CAUSES",
         "from_uid": "evt-03-led-to-farm", "to_uid": "evt-04-jhaele-welcome"},
        {"uid": "rel-evt04-05", "rel_type": "CAUSES",
         "from_uid": "evt-04-jhaele-welcome", "to_uid": "evt-05-long-rest"},
        {"uid": "rel-evt05-06", "rel_type": "CAUSES",
         "from_uid": "evt-05-long-rest", "to_uid": "evt-06-elminster-arrives"},
        {"uid": "rel-evt06-07", "rel_type": "CAUSES",
         "from_uid": "evt-06-elminster-arrives", "to_uid": "evt-07-briefing"},
        # Plotline memberships (Act 1)
        *[{"uid": f"rel-{eid}-plotline", "rel_type": "PART_OF_PLOTLINE",
           "from_uid": eid, "to_uid": "plot-the-troubles"}
          for eid in [
              "evt-01-arrival", "evt-02-lettinster", "evt-03-led-to-farm",
              "evt-04-jhaele-welcome", "evt-05-long-rest",
              "evt-06-elminster-arrives", "evt-07-briefing",
          ]],
        # Branch from evt-07
        {"uid": "rel-briefing-branches", "rel_type": "BRANCHES_INTO",
         "from_uid": "evt-07-briefing", "to_uid": "choice-01-where-first"},
        {"uid": "rel-choice01-outcome-a", "rel_type": "HAS_OUTCOME",
         "from_uid": "choice-01-where-first", "to_uid": "outcome-01a-temple"},
        {"uid": "rel-choice01-outcome-b", "rel_type": "HAS_OUTCOME",
         "from_uid": "choice-01-where-first", "to_uid": "outcome-01b-mill"},
        {"uid": "rel-outcome01a-leads-to", "rel_type": "LEADS_TO",
         "from_uid": "outcome-01a-temple", "to_uid": "evt-08-temple-approach"},
        {"uid": "rel-outcome01b-leads-to", "rel_type": "LEADS_TO",
         "from_uid": "outcome-01b-mill", "to_uid": "evt-12-mill-approach"},
        # Act 2A merge: stealth + direct both lead to skulker-outcome
        {"uid": "rel-10a-leads-to-11", "rel_type": "LEADS_TO",
         "from_uid": "outcome-02a-stealth", "to_uid": "evt-11-skulker-outcome"},
        {"uid": "rel-10b-leads-to-11", "rel_type": "LEADS_TO",
         "from_uid": "outcome-02b-direct", "to_uid": "evt-11-skulker-outcome"},
        # Act 2A merge: skulker-gone + skulker-dead both lead to temple-complete
        {"uid": "rel-11c-leads-to-merge-a", "rel_type": "LEADS_TO",
         "from_uid": "evt-11c-skulker-gone", "to_uid": "evt-merge-a-temple-complete"},
        {"uid": "rel-11d-leads-to-merge-a", "rel_type": "LEADS_TO",
         "from_uid": "evt-11d-skulker-dead", "to_uid": "evt-merge-a-temple-complete"},
        # Act 2B mill outcomes all lead to mill-complete (or tower pool)
        {"uid": "rel-07a-leads-to-merge-b", "rel_type": "LEADS_TO",
         "from_uid": "outcome-07a-pipe-first-water", "to_uid": "evt-merge-b-mill-complete"},
        {"uid": "rel-07b-leads-to-merge-b", "rel_type": "LEADS_TO",
         "from_uid": "outcome-07b-kill-first-water", "to_uid": "evt-merge-b-mill-complete"},
        {"uid": "rel-08a-leads-to-merge-b", "rel_type": "LEADS_TO",
         "from_uid": "outcome-08a-pipe-first-land", "to_uid": "evt-merge-b-mill-complete"},
        {"uid": "rel-08b-leads-to-merge-b", "rel_type": "LEADS_TO",
         "from_uid": "outcome-08b-kill-first-land", "to_uid": "evt-merge-b-mill-complete"},
        # Grand merge: both paths lead to return-to-farm
        {"uid": "rel-merge-a-to-farm", "rel_type": "LEADS_TO",
         "from_uid": "evt-merge-a-temple-complete", "to_uid": "evt-16-return-to-farm"},
        {"uid": "rel-merge-b-to-farm", "rel_type": "LEADS_TO",
         "from_uid": "evt-merge-b-mill-complete", "to_uid": "evt-16-return-to-farm"},
        # Pipe resolution outcomes all lead to payment
        {"uid": "rel-17a-to-18", "rel_type": "LEADS_TO",
         "from_uid": "evt-17a-elminster-delighted", "to_uid": "evt-18-payment"},
        {"uid": "rel-17b-to-18", "rel_type": "LEADS_TO",
         "from_uid": "evt-17b-elminster-pouts", "to_uid": "evt-18-payment"},
        {"uid": "rel-17c-to-18", "rel_type": "LEADS_TO",
         "from_uid": "evt-17c-elminster-accepts", "to_uid": "evt-18-payment"},
        {"uid": "rel-17d-to-18", "rel_type": "LEADS_TO",
         "from_uid": "evt-17d-elminster-disappointed", "to_uid": "evt-18-payment"},
        # Final act chain
        {"uid": "rel-18-19", "rel_type": "CAUSES",
         "from_uid": "evt-18-payment", "to_uid": "evt-19-final-night"},
        {"uid": "rel-19-20", "rel_type": "CAUSES",
         "from_uid": "evt-19-final-night", "to_uid": "evt-20-adventure-end"},
    ]


# ── Full Fixture ──────────────────────────────────────────────────────────────

def make_full_fixture() -> dict:
    """
    Assembles the complete Shadowdale adventure in the NDJSON-envelope
    format expected by import_database(). Calls all builders above.
    """
    nodes = [
        # Global
        make_elminster(),
        make_pipe_of_elminster(),
        make_global_shadowdale(),
        make_tower_of_ashaba(),
        make_river_ashaba(),
        # Adventure
        make_adventure(),
        # Context
        make_elminster_context(),
        # NPCs
        make_jhaele(),
        make_lettinster(),
        make_sister_maeris(),
        make_graveyard_skulker(),
        make_millpond_horror(),
        # Locations
        make_northern_road_entry(),
        make_jhaele_farm(),
        make_temple_tymora(),
        make_temple_graveyard(),
        make_the_mill(),
        make_millpond(),
        make_sylunes_hut(),
        make_castle_grimstead(),
        make_cavenauth(),
        make_tower_pool(),
        # Timeline
        make_timeline(),
        # Historical events
        make_evt_underdark_fight(),
        make_evt_pipe_stolen(),
        # Plotline
        make_plotline(),
        # Narrative events
        *make_act1_events(),
        *make_act2a_events(),
        *make_act2b_events(),
        *make_act3_events(),
        # Choices and outcomes
        *make_all_choices(),
        *make_all_outcomes(),
        # Encounters
        *make_encounters(),
        # Knowledge
        *make_rumors(),
        *make_facts(),
    ]

    relationships = make_relationships()

    return {
        "meta": {
            "schema_version": 1,
            "exported_at": _NOW,
            "node_count": len(nodes),
            "rel_count": len(relationships),
        },
        "nodes": nodes,
        "relationships": relationships,
        "files": [],  # No prose files written yet
    }
