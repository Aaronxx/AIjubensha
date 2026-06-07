"""Character/NPC management service."""
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from uuid import uuid4

from ..models.character import (
    CharacterCreate, CharacterUpdate, CharacterInDB, CharacterResponse,
    CharacterDetailResponse, CharacterScriptAssignment, CharacterRoleInScript,
    KnowledgeEntry, ArcState, ArcTransition, RelationshipEntry,
    SilenceStrategy, CharacterType
)


class CharacterService:
    """Manages character/NPC CRUD operations."""

    def __init__(self):
        # In-memory store for MVP
        self._characters: dict[str, CharacterInDB] = {}
        self._name_index: dict[str, str] = {}  # name -> character_id

    async def create_character(self, char_data: CharacterCreate) -> dict:
        """Create a new character."""
        # Check for duplicate name
        if char_data.name in self._name_index:
            return {
                "success": False,
                "error": f"Character with name '{char_data.name}' already exists"
            }

        # Create character
        char_id = str(uuid4())
        now = datetime.now(timezone.utc)

        character = CharacterInDB(
            id=char_id,
            name=char_data.name,
            age=char_data.age,
            occupation=char_data.occupation,
            background=char_data.background,
            avatar=char_data.avatar,
            personality=char_data.personality,
            knowledge=char_data.knowledge,
            goals=char_data.goals,
            arc_states=char_data.arc_states,
            arc_transitions=char_data.arc_transitions,
            current_arc_state=char_data.arc_states[0].state_id if char_data.arc_states else "default",
            default_silence_strategy=char_data.default_silence_strategy,
            character_anchor=char_data.character_anchor,
            relationships=[],
            script_assignments={},
            created_at=now,
            updated_at=now
        )

        # Store character
        self._characters[char_id] = character
        self._name_index[character.name] = char_id

        return {
            "success": True,
            "character_id": char_id,
            "character": self._character_to_dict(character)
        }

    async def get_character(self, char_id: str) -> Optional[dict]:
        """Get character by ID."""
        char = self._characters.get(char_id)
        if not char:
            return None
        return self._character_to_dict(char)

    async def get_character_by_name(self, name: str) -> Optional[dict]:
        """Get character by name."""
        char_id = self._name_index.get(name)
        if char_id:
            return await self.get_character(char_id)
        return None

    async def list_characters(
        self,
        search: Optional[str] = None,
        occupation: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        skip: int = 0,
        limit: int = 20
    ) -> List[dict]:
        """List characters with filtering."""
        characters = list(self._characters.values())

        # Apply filters
        if occupation:
            characters = [c for c in characters if c.occupation == occupation]

        if search:
            search_lower = search.lower()
            characters = [
                c for c in characters
                if search_lower in c.name.lower()
                or search_lower in c.background.lower()
                or search_lower in c.occupation.lower()
            ]

        # Sort
        reverse = sort_order == "desc"
        if sort_by == "name":
            characters.sort(key=lambda c: c.name, reverse=reverse)
        elif sort_by == "usage_count":
            characters.sort(key=lambda c: c.usage_count, reverse=reverse)
        else:  # created_at
            characters.sort(key=lambda c: c.created_at, reverse=reverse)

        # Paginate
        total = len(characters)
        characters = characters[skip:skip + limit]

        return {
            "characters": [self._character_to_dict(c) for c in characters],
            "total": total,
            "skip": skip,
            "limit": limit
        }

    async def update_character(self, char_id: str, update_data: CharacterUpdate) -> dict:
        """Update a character."""
        char = self._characters.get(char_id)
        if not char:
            return {"success": False, "error": "Character not found"}

        # Check name uniqueness if updating name
        if update_data.name and update_data.name != char.name:
            if update_data.name in self._name_index:
                return {
                    "success": False,
                    "error": f"Character with name '{update_data.name}' already exists"
                }
            # Update name index
            del self._name_index[char.name]
            self._name_index[update_data.name] = char_id
            char.name = update_data.name

        # Update other fields
        if update_data.age:
            char.age = update_data.age
        if update_data.occupation:
            char.occupation = update_data.occupation
        if update_data.background:
            char.background = update_data.background
        if update_data.avatar:
            char.avatar = update_data.avatar
        if update_data.personality:
            char.personality = update_data.personality
        if update_data.character_anchor:
            char.character_anchor = update_data.character_anchor

        char.updated_at = datetime.now(timezone.utc)

        return {"success": True, "character_id": char_id, "character": self._character_to_dict(char)}

    async def delete_character(self, char_id: str) -> dict:
        """Delete a character."""
        char = self._characters.get(char_id)
        if not char:
            return {"success": False, "error": "Character not found"}

        # Remove from indexes
        del self._name_index[char.name]
        del self._characters[char_id]

        return {"success": True}

    async def assign_to_script(self, char_id: str, assignment: CharacterScriptAssignment) -> dict:
        """Assign character to a script with a role."""
        char = self._characters.get(char_id)
        if not char:
            return {"success": False, "error": "Character not found"}

        char.script_assignments[assignment.script_id] = assignment.role
        char.usage_count += 1
        char.updated_at = datetime.now(timezone.utc)

        return {"success": True, "character": self._character_to_dict(char)}

    async def remove_from_script(self, char_id: str, script_id: str) -> dict:
        """Remove character from a script."""
        char = self._characters.get(char_id)
        if not char:
            return {"success": False, "error": "Character not found"}

        if script_id in char.script_assignments:
            del char.script_assignments[script_id]
            char.updated_at = datetime.now(timezone.utc)

        return {"success": True}

    async def add_relationship(self, char_id: str, relationship: RelationshipEntry) -> dict:
        """Add relationship with another character."""
        char = self._characters.get(char_id)
        if not char:
            return {"success": False, "error": "Character not found"}

        # Check target character exists
        if relationship.target_character_id not in self._characters:
            return {"success": False, "error": "Target character not found"}

        # Remove existing relationship if any
        char.relationships = [
            r for r in char.relationships
            if r.target_character_id != relationship.target_character_id
        ]

        char.relationships.append(relationship)
        char.updated_at = datetime.now(timezone.utc)

        return {"success": True, "character": self._character_to_dict(char)}

    async def update_knowledge(self, char_id: str, knowledge: List[KnowledgeEntry]) -> dict:
        """Update character knowledge."""
        char = self._characters.get(char_id)
        if not char:
            return {"success": False, "error": "Character not found"}

        char.knowledge = knowledge
        char.updated_at = datetime.now(timezone.utc)

        return {"success": True}

    async def update_arc_states(self, char_id: str, states: List[ArcState], transitions: List[ArcTransition]) -> dict:
        """Update character arc states and transitions."""
        char = self._characters.get(char_id)
        if not char:
            return {"success": False, "error": "Character not found"}

        char.arc_states = states
        char.arc_transitions = transitions
        char.updated_at = datetime.now(timezone.utc)

        return {"success": True}

    async def transition_arc_state(self, char_id: str, trigger: str, context: dict) -> dict:
        """Attempt to transition character arc state."""
        char = self._characters.get(char_id)
        if not char:
            return {"success": False, "error": "Character not found"}

        current_state = char.current_arc_state

        # Find applicable transition
        for trans in char.arc_transitions:
            if trans.from_state == current_state and trigger in trans.trigger_condition:
                # Check conditions
                if trans.required_attitude is not None:
                    player_id = context.get("player_id")
                    if player_id and char.goals.attitude_to_others.get(player_id, 0) < trans.required_attitude:
                        continue

                # Transition
                char.current_arc_state = trans.to_state
                char.updated_at = datetime.now(timezone.utc)
                return {
                    "success": True,
                    "from_state": trans.from_state,
                    "to_state": trans.to_state
                }

        return {"success": False, "message": "No state transition triggered"}

    async def get_characters_for_script(self, script_id: str) -> List[dict]:
        """Get all characters assigned to a script."""
        characters = [
            self._character_to_dict(c)
            for c in self._characters.values()
            if script_id in c.script_assignments
        ]
        return characters

    def _character_to_dict(self, char: CharacterInDB) -> dict:
        """Convert character to dict."""
        return {
            "id": char.id,
            "name": char.name,
            "age": char.age,
            "occupation": char.occupation,
            "background": char.background,
            "avatar": char.avatar,
            "personality": {
                "extroversion": char.personality.extroversion.dict(),
                "aggressiveness": char.personality.aggressiveness.dict(),
                "honesty": char.personality.honesty.dict(),
                "rationality": char.personality.rationality.dict(),
                "speaking_style": char.personality.speaking_style
            },
            "character_anchor": char.character_anchor,
            "current_arc_state": char.current_arc_state,
            "default_silence_strategy": char.default_silence_strategy.value,
            "knowledge_count": len(char.knowledge),
            "relationship_count": len(char.relationships),
            "script_count": len(char.script_assignments),
            "usage_count": char.usage_count,
            "created_at": char.created_at.isoformat(),
            "updated_at": char.updated_at.isoformat()
        }

    def _character_to_detail_dict(self, char: CharacterInDB) -> dict:
        """Convert character to detailed dict."""
        return {
            "id": char.id,
            "name": char.name,
            "age": char.age,
            "occupation": char.occupation,
            "background": char.background,
            "avatar": char.avatar,
            "personality": {
                "extroversion": char.personality.extroversion.dict(),
                "aggressiveness": char.personality.aggressiveness.dict(),
                "honesty": char.personality.honesty.dict(),
                "rationality": char.personality.rationality.dict(),
                "speaking_style": char.personality.speaking_style
            },
            "character_anchor": char.character_anchor,
            "current_arc_state": char.current_arc_state,
            "default_silence_strategy": char.default_silence_strategy.value,
            "knowledge": [k.dict() for k in char.knowledge],
            "goals": {
                "primary_goal": char.goals.primary_goal,
                "secondary_goals": char.goals.secondary_goals,
                "red_lines": char.goals.red_lines,
                "attitude_to_others": char.goals.attitude_to_others
            },
            "arc_states": [s.dict() for s in char.arc_states],
            "arc_transitions": [
                {"from_state": t.from_state, "to_state": t.to_state,
                 "trigger_condition": t.trigger_condition}
                for t in char.arc_transitions
            ],
            "relationships": [r.dict() for r in char.relationships],
            "script_assignments": {
                script_id: {
                    "is_murderer": role.is_murderer,
                    "character_type": role.character_type.value,
                    "self_awareness": role.self_awareness,
                    "lie_topics": role.lie_topics,
                    "protected_info": role.protected_info
                }
                for script_id, role in char.script_assignments.items()
            },
            "usage_count": char.usage_count,
            "created_at": char.created_at.isoformat(),
            "updated_at": char.updated_at.isoformat()
        }

    async def get_character_detail(self, char_id: str) -> Optional[dict]:
        """Get detailed character by ID."""
        char = self._characters.get(char_id)
        if not char:
            return None
        return self._character_to_detail_dict(char)


# Singleton instance
character_service = CharacterService()
