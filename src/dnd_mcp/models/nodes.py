"""Dataclasses for all graph node types."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ── Base ──────────────────────────────────────────────────────────────────────

@dataclass
class BaseNode:
    uid: str
    tier: str  # "global" | "adventure" | "context"
    disabled: bool = False
    disabled_by: list = field(default_factory=list)
    disabled_at: Optional[str] = None
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)

    def to_props(self) -> dict:
        """All properties for Neo4j storage."""
        return {k: v for k, v in self.__dict__.items()}

    def to_response(self) -> dict:
        """Filtered for MCP responses — omits None and empty lists."""
        return {
            k: v for k, v in self.__dict__.items()
            if v is not None and v != []
        }


# ── Global Tier ───────────────────────────────────────────────────────────────

@dataclass
class GlobalNPC(BaseNode):
    label: str = "GlobalNPC"
    canonical_name: str = ""
    aliases: list = field(default_factory=list)
    summary: str = ""
    source: str = ""
    is_canonical: bool = True

    def __post_init__(self):
        self.tier = "global"


@dataclass
class GlobalLocation(BaseNode):
    label: str = "GlobalLocation"
    canonical_name: str = ""
    summary: str = ""
    source: str = ""
    region: Optional[str] = None
    type: Optional[str] = None
    is_canonical: bool = True

    def __post_init__(self):
        self.tier = "global"


@dataclass
class GlobalItem(BaseNode):
    label: str = "GlobalItem"
    canonical_name: str = ""
    summary: str = ""
    source: str = ""
    rarity: Optional[str] = None
    is_canonical: bool = True

    def __post_init__(self):
        self.tier = "global"


@dataclass
class GlobalFaction(BaseNode):
    label: str = "GlobalFaction"
    canonical_name: str = ""
    summary: str = ""
    source: str = ""
    alignment: Optional[str] = None
    is_canonical: bool = True

    def __post_init__(self):
        self.tier = "global"


# ── Adventure Tier ────────────────────────────────────────────────────────────

@dataclass
class Adventure(BaseNode):
    label: str = "Adventure"
    name: str = ""
    status: str = "draft"  # "draft" | "in-progress" | "complete"
    setting: Optional[str] = None
    tags: list = field(default_factory=list)
    summary: Optional[str] = None

    def __post_init__(self):
        self.tier = "adventure"


@dataclass
class NPC(BaseNode):
    label: str = "NPC"
    name: str = ""
    summary: Optional[str] = None
    source_adventure: str = ""
    aliases: list = field(default_factory=list)
    role: Optional[str] = None
    status: Optional[str] = None

    def __post_init__(self):
        self.tier = "adventure"


@dataclass
class Location(BaseNode):
    label: str = "Location"
    name: str = ""
    summary: Optional[str] = None
    source_adventure: str = ""
    type: Optional[str] = None
    region: Optional[str] = None

    def __post_init__(self):
        self.tier = "adventure"


@dataclass
class Item(BaseNode):
    label: str = "Item"
    name: str = ""
    summary: Optional[str] = None
    source_adventure: str = ""
    rarity: Optional[str] = None

    def __post_init__(self):
        self.tier = "adventure"


@dataclass
class Faction(BaseNode):
    label: str = "Faction"
    name: str = ""
    summary: Optional[str] = None
    source_adventure: str = ""
    alignment: Optional[str] = None

    def __post_init__(self):
        self.tier = "adventure"


@dataclass
class Plotline(BaseNode):
    label: str = "Plotline"
    name: str = ""
    summary: Optional[str] = None
    status: str = "draft"
    theme: Optional[str] = None
    source_adventure: str = ""

    def __post_init__(self):
        self.tier = "adventure"


@dataclass
class Event(BaseNode):
    label: str = "Event"
    name: str = ""
    summary: Optional[str] = None
    event_type: Optional[str] = None  # "scene|combat|revelation|transition"
    is_anchor: bool = False
    is_historical: bool = False
    source_adventure: Optional[str] = None

    def __post_init__(self):
        self.tier = "adventure"


@dataclass
class Choice(BaseNode):
    label: str = "Choice"
    prompt: str = ""
    summary: Optional[str] = None
    condition: Optional[str] = None
    condition_type: Optional[str] = None  # "optional|required|gated"
    source_adventure: Optional[str] = None

    def __post_init__(self):
        self.tier = "adventure"


@dataclass
class Outcome(BaseNode):
    label: str = "Outcome"
    label_text: str = ""
    consequence_summary: Optional[str] = None
    probability: Optional[float] = None
    source_adventure: Optional[str] = None

    def __post_init__(self):
        self.tier = "adventure"


@dataclass
class Timeline(BaseNode):
    label: str = "Timeline"
    name: str = ""
    era: Optional[str] = None
    description: Optional[str] = None
    source_adventure: Optional[str] = None

    def __post_init__(self):
        self.tier = "adventure"


@dataclass
class BoxedTextSequence(BaseNode):
    label: str = "BoxedTextSequence"
    name: str = ""
    summary: Optional[str] = None
    context: Optional[str] = None
    source_adventure: Optional[str] = None

    def __post_init__(self):
        self.tier = "adventure"


@dataclass
class BoxedText(BaseNode):
    label: str = "BoxedText"
    trigger_summary: str = ""
    content_summary: str = ""
    tone: Optional[str] = None
    sequence_position: Optional[int] = None
    is_conditional: bool = False
    source_adventure: Optional[str] = None

    def __post_init__(self):
        self.tier = "adventure"


@dataclass
class Fact(BaseNode):
    label: str = "Fact"
    content: str = ""
    reliability: str = "established"  # "established|rumored|contradicted"
    source_file: Optional[str] = None
    source_excerpt_line: Optional[int] = None
    source_adventure: Optional[str] = None

    def __post_init__(self):
        self.tier = "adventure"


@dataclass
class Rumor(BaseNode):
    label: str = "Rumor"
    content: str = ""
    is_true: Optional[bool] = None
    spread: Optional[str] = None
    source_npc: Optional[str] = None
    source_adventure: Optional[str] = None

    def __post_init__(self):
        self.tier = "adventure"


@dataclass
class Combat(BaseNode):
    label: str = "Combat"
    name: str = ""
    summary: Optional[str] = None
    cr: Optional[float] = None
    xp: Optional[int] = None
    terrain: Optional[str] = None
    tactics: Optional[str] = None
    source_adventure: Optional[str] = None

    def __post_init__(self):
        self.tier = "adventure"


@dataclass
class SkillChallenge(BaseNode):
    label: str = "SkillChallenge"
    name: str = ""
    summary: Optional[str] = None
    dc: Optional[int] = None
    skills_involved: list = field(default_factory=list)
    consequences: Optional[str] = None
    source_adventure: Optional[str] = None

    def __post_init__(self):
        self.tier = "adventure"


@dataclass
class Trap(BaseNode):
    label: str = "Trap"
    name: str = ""
    summary: Optional[str] = None
    dc: Optional[int] = None
    damage: Optional[str] = None
    trigger: Optional[str] = None
    reset: Optional[str] = None
    source_adventure: Optional[str] = None

    def __post_init__(self):
        self.tier = "adventure"


@dataclass
class FileRef(BaseNode):
    label: str = "FileRef"
    path: str = ""
    file_type: Optional[str] = None
    description: Optional[str] = None
    associated_entity_uid: Optional[str] = None
    source_adventure: Optional[str] = None

    def __post_init__(self):
        self.tier = "adventure"


# ── Context Tier ──────────────────────────────────────────────────────────────

@dataclass
class NPCContext(BaseNode):
    label: str = "NPCContext"
    role: Optional[str] = None
    status: Optional[str] = None  # "alive|dead|missing|unknown"
    summary: Optional[str] = None
    first_appears: Optional[str] = None
    last_known_location: Optional[str] = None

    def __post_init__(self):
        self.tier = "context"
