"""Script management service."""
from datetime import datetime
from typing import Optional, List
from uuid import uuid4

from ..models.script import (
    ScriptCreate, ScriptUpdate, ScriptInDB, ScriptResponse,
    DifficultyLevel, ScriptType, ScriptListParams
)


class ScriptService:
    """Manages script CRUD operations."""

    def __init__(self):
        # In-memory store for MVP
        self._scripts: dict[str, ScriptInDB] = {}
        self._title_index: dict[str, str] = {}  # title -> script_id

    async def create_script(self, script_data: ScriptCreate) -> dict:
        """Create a new script."""
        # Check for duplicate title
        if script_data.title in self._title_index:
            return {
                "success": False,
                "error": f"Script with title '{script_data.title}' already exists"
            }

        # Validate player counts
        if script_data.min_players > script_data.max_players:
            return {
                "success": False,
                "error": "min_players must be less than or equal to max_players"
            }

        # Create script
        script_id = str(uuid4())
        now = datetime.utcnow()

        script = ScriptInDB(
            id=script_id,
            title=script_data.title,
            description=script_data.description,
            script_type=script_data.script_type,
            difficulty=script_data.difficulty,
            min_players=script_data.min_players,
            max_players=script_data.max_players,
            duration_minutes=script_data.duration_minutes,
            author=script_data.author,
            tags=script_data.tags,
            cover_image=script_data.cover_image,
            is_published=script_data.is_published,
            created_at=now,
            updated_at=now,
            play_count=0,
            rating=0.0,
            rating_count=0
        )

        # Store script
        self._scripts[script_id] = script
        self._title_index[script.title] = script_id

        return {
            "success": True,
            "script_id": script_id,
            "title": script.title,
            "description": script.description,
            "script_type": script.script_type.value,
            "difficulty": script.difficulty.value,
            "min_players": script.min_players,
            "max_players": script.max_players,
            "duration_minutes": script.duration_minutes,
            "created_at": script.created_at.isoformat()
        }

    async def get_script(self, script_id: str) -> Optional[dict]:
        """Get script by ID."""
        script = self._scripts.get(script_id)
        if not script:
            return None
        return self._script_to_dict(script)

    async def get_script_by_title(self, title: str) -> Optional[dict]:
        """Get script by title."""
        script_id = self._title_index.get(title)
        if script_id:
            return await self.get_script(script_id)
        return None

    async def list_scripts(
        self,
        difficulty: Optional[DifficultyLevel] = None,
        script_type: Optional[ScriptType] = None,
        min_players: Optional[int] = None,
        max_players: Optional[int] = None,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        skip: int = 0,
        limit: int = 20
    ) -> List[dict]:
        """List scripts with filtering and sorting."""
        scripts = list(self._scripts.values())

        # Apply filters
        if difficulty:
            scripts = [s for s in scripts if s.difficulty == difficulty]

        if script_type:
            scripts = [s for s in scripts if s.script_type == script_type]

        if min_players is not None:
            scripts = [s for s in scripts if s.min_players <= min_players]

        if max_players is not None:
            scripts = [s for s in scripts if s.max_players >= max_players]

        if search:
            search_lower = search.lower()
            scripts = [
                s for s in scripts
                if search_lower in s.title.lower()
                or search_lower in s.description.lower()
                or any(search_lower in tag.lower() for tag in s.tags)
            ]

        # Sort
        reverse = sort_order == "desc"
        if sort_by == "rating":
            scripts.sort(key=lambda s: s.rating, reverse=reverse)
        elif sort_by == "play_count":
            scripts.sort(key=lambda s: s.play_count, reverse=reverse)
        else:  # created_at
            scripts.sort(key=lambda s: s.created_at, reverse=reverse)

        # Paginate
        scripts = scripts[skip:skip + limit]

        return [self._script_to_dict(s) for s in scripts]

    async def update_script(self, script_id: str, update_data: ScriptUpdate) -> dict:
        """Update a script."""
        script = self._scripts.get(script_id)
        if not script:
            return {"success": False, "error": "Script not found"}

        # Update fields
        update_dict = update_data.model_dump(exclude_unset=True)

        # Check title uniqueness if updating title
        if "title" in update_dict:
            new_title = update_dict["title"]
            if new_title != script.title and new_title in self._title_index:
                return {
                    "success": False,
                    "error": f"Script with title '{new_title}' already exists"
                }
            # Update title index
            del self._title_index[script.title]
            self._title_index[new_title] = script_id

        # Update script
        for field, value in update_dict.items():
            if hasattr(script, field):
                setattr(script, field, value)

        script.updated_at = datetime.utcnow()

        return {"success": True, "script_id": script_id}

    async def delete_script(self, script_id: str) -> dict:
        """Delete a script."""
        script = self._scripts.get(script_id)
        if not script:
            return {"success": False, "error": "Script not found"}

        # Remove from indexes
        del self._title_index[script.title]
        del self._scripts[script_id]

        return {"success": True}

    async def increment_play_count(self, script_id: str) -> bool:
        """Increment play count for a script."""
        script = self._scripts.get(script_id)
        if script:
            script.play_count += 1
            return True
        return False

    async def rate_script(self, script_id: str, rating: float) -> bool:
        """Add a rating to a script."""
        script = self._scripts.get(script_id)
        if not script:
            return False

        # Update rating using weighted average
        total_rating = script.rating * script.rating_count + rating
        script.rating_count += 1
        script.rating = total_rating / script.rating_count

        return True

    def _script_to_dict(self, script: ScriptInDB) -> dict:
        """Convert script model to dict."""
        return {
            "id": script.id,
            "title": script.title,
            "description": script.description,
            "script_type": script.script_type.value,
            "difficulty": script.difficulty.value,
            "min_players": script.min_players,
            "max_players": script.max_players,
            "duration_minutes": script.duration_minutes,
            "author": script.author,
            "tags": script.tags,
            "cover_image": script.cover_image,
            "is_published": script.is_published,
            "play_count": script.play_count,
            "rating": round(script.rating, 2),
            "rating_count": script.rating_count,
            "created_at": script.created_at.isoformat(),
            "updated_at": script.updated_at.isoformat()
        }


# Singleton instance
script_service = ScriptService()
