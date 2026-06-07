"""In-memory data store for admin backend MVP."""
from __future__ import annotations
from dataclasses import dataclass, field
import uuid, copy

@dataclass
class ScriptRecord:
    script_id: str
    name: str
    description: str = ""
    script_type: str = "deduction"  # deduction/social/emotional
    difficulty: int = 2  # 1-4 stars
    min_players: int = 4
    max_players: int = 8
    duration_min: int = 75
    timeline_mode: str = "mingzhen"  # mingzhen/realtime
    price_stars: int = 100
    endings: list = field(default_factory=list)
    characters: list = field(default_factory=list)
    status: str = "draft"  # draft/published/archived

@dataclass
class CharacterRecord:
    character_id: str
    script_id: str
    name: str
    age: int = 0
    occupation: str = ""
    character_anchor: str = ""
    is_killer: bool = False
    self_awareness: str = "never_knows"
    personality: dict = field(default_factory=lambda: {
        "extroversion": 0.5, "aggression": 0.5, "honesty_tendency": 0.5,
        "rationality": 0.5, "speech_style": ""
    })
    knowledge: list = field(default_factory=list)
    arc_states: list = field(default_factory=list)
    arc_transitions: list = field(default_factory=list)
    initial_arc_state: str = ""
    relationships: list = field(default_factory=list)
    lie_topics: list = field(default_factory=list)
    silence_strategy: str = ""
    silence_triggers: list = field(default_factory=list)

class Store:
    def __init__(self):
        self.scripts: dict[str, ScriptRecord] = {}
        self.characters: dict[str, CharacterRecord] = {}
        self.achievements: list = []
        self.products: list = []
        self.orders: list = []
        self.users: dict[str, dict] = {}
        self.audit_queue: list = []

    # Scripts
    def create_script(self, data: dict) -> ScriptRecord:
        sid = str(uuid.uuid4())[:8]
        s = ScriptRecord(script_id=sid, **{k: v for k, v in data.items() if k in ScriptRecord.__dataclass_fields__})
        self.scripts[sid] = s
        return s

    def get_script(self, sid: str) -> ScriptRecord | None:
        return self.scripts.get(sid)

    def list_scripts(self) -> list:
        return [s.__dict__ for s in self.scripts.values()]

    def update_script(self, sid: str, data: dict) -> ScriptRecord | None:
        s = self.scripts.get(sid)
        if not s: return None
        for k, v in data.items():
            if hasattr(s, k): setattr(s, k, v)
        return s

    def delete_script(self, sid: str) -> bool:
        if sid in self.scripts:
            del self.scripts[sid]
            return True
        return False

    # Characters
    def create_character(self, data: dict) -> CharacterRecord:
        cid = str(uuid.uuid4())[:8]
        c = CharacterRecord(character_id=cid, **{k: v for k, v in data.items() if k in CharacterRecord.__dataclass_fields__})
        self.characters[cid] = c
        return c

    def get_character(self, cid: str) -> CharacterRecord | None:
        return self.characters.get(cid)

    def list_characters(self, script_id: str | None = None) -> list:
        if script_id:
            return [c.__dict__ for c in self.characters.values() if c.script_id == script_id]
        return [c.__dict__ for c in self.characters.values()]

    def update_character(self, cid: str, data: dict) -> CharacterRecord | None:
        c = self.characters.get(cid)
        if not c: return None
        for k, v in data.items():
            if hasattr(c, k): setattr(c, k, v)
        return c

    def delete_character(self, cid: str) -> bool:
        if cid in self.characters:
            del self.characters[cid]
            return True
        return False

store = Store()
