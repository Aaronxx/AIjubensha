"""Script management tests."""
import pytest
from datetime import datetime

from src.services.script_service import ScriptService
from src.models.script import ScriptCreate, ScriptUpdate, DifficultyLevel, ScriptType


class TestScriptCreation:
    """Test script creation functionality."""

    @pytest.fixture
    def script_service(self):
        return ScriptService()

    @pytest.mark.asyncio
    async def test_create_script_success(self, script_service):
        """Test successful script creation."""
        script_data = ScriptCreate(
            title="山庄晚宴",
            description="雨夜古堡，名流齐聚。一声枪响，谁是真凶？",
            script_type=ScriptType.BENGGE,
            difficulty=DifficultyLevel.STANDARD,
            min_players=4,
            max_players=6,
            duration_minutes=75,
            author="官方编剧",
            tags=["本格", "推理", "经典"],
            cover_image="https://example.com/cover.jpg"
        )

        result = await script_service.create_script(script_data)

        assert result["success"] is True
        assert "script_id" in result
        assert result["title"] == "山庄晚宴"
        assert result["difficulty"] == "standard"

    @pytest.mark.asyncio
    async def test_create_script_duplicate_title(self, script_service):
        """Test creating script with duplicate title."""
        script_data = ScriptCreate(
            title="UniqueTitle",
            description="Test description",
            script_type=ScriptType.BENGGE,
            difficulty=DifficultyLevel.EASY,
            min_players=4,
            max_players=6,
            duration_minutes=60
        )

        # First creation
        await script_service.create_script(script_data)

        # Second creation with same title
        result = await script_service.create_script(script_data)

        assert result["success"] is False
        assert "error" in result
        assert "already exists" in result["error"]

    @pytest.mark.asyncio
    async def test_create_script_invalid_player_count(self, script_service):
        """Test creating script with invalid player count - should fail Pydantic validation."""
        # This test verifies that Pydantic validates player counts
        # Since Pydantic rejects invalid data before reaching service,
        # we just verify the validator works by trying to create invalid model
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            ScriptCreate(
                title="InvalidScript",
                description="Test description for validation",
                script_type=ScriptType.BENGGE,
                difficulty=DifficultyLevel.EASY,
                min_players=6,
                max_players=4,  # min > max should fail
                duration_minutes=60
            )

        assert "max_players" in str(exc_info.value) or "min_players" in str(exc_info.value)


class TestScriptRetrieval:
    """Test script retrieval functionality."""

    @pytest.fixture
    def script_service_with_data(self):
        return ScriptService()

    @pytest.mark.asyncio
    async def test_get_script_by_id(self, script_service_with_data):
        """Test getting script by ID."""
        service = script_service_with_data
        # Create test script
        result = await service.create_script(ScriptCreate(
            title="TestScript1",
            description="Desc1 for test script",
            script_type=ScriptType.BENGGE,
            difficulty=DifficultyLevel.EASY,
            min_players=4,
            max_players=6,
            duration_minutes=60
        ))
        script_id = result["script_id"]

        retrieved = await service.get_script(script_id)

        assert retrieved is not None
        assert retrieved["id"] == script_id

    @pytest.mark.asyncio
    async def test_get_nonexistent_script(self, script_service_with_data):
        """Test getting non-existent script."""
        service = script_service_with_data

        result = await service.get_script("nonexistent-id")

        assert result is None

    @pytest.mark.asyncio
    async def test_list_scripts(self, script_service_with_data):
        """Test listing all scripts."""
        service = script_service_with_data
        # Create test scripts
        await service.create_script(ScriptCreate(
            title="TestScript1",
            description="Desc1 for test",
            script_type=ScriptType.BENGGE,
            difficulty=DifficultyLevel.EASY,
            min_players=4,
            max_players=6,
            duration_minutes=60
        ))
        await service.create_script(ScriptCreate(
            title="TestScript2",
            description="Desc2 for test",
            script_type=ScriptType.SOCIAL,
            difficulty=DifficultyLevel.HARD,
            min_players=6,
            max_players=8,
            duration_minutes=90
        ))

        result = await service.list_scripts()

        assert len(result) >= 2
        assert all("id" in script for script in result)

    @pytest.mark.asyncio
    async def test_filter_by_difficulty(self, script_service_with_data):
        """Test filtering scripts by difficulty."""
        service = script_service_with_data
        # Create test scripts
        await service.create_script(ScriptCreate(
            title="EasyScript",
            description="Easy description",
            script_type=ScriptType.BENGGE,
            difficulty=DifficultyLevel.EASY,
            min_players=4,
            max_players=6,
            duration_minutes=60
        ))
        await service.create_script(ScriptCreate(
            title="HardScript",
            description="Hard description",
            script_type=ScriptType.SOCIAL,
            difficulty=DifficultyLevel.HARD,
            min_players=6,
            max_players=8,
            duration_minutes=90
        ))

        easy_scripts = await service.list_scripts(difficulty=DifficultyLevel.EASY)

        assert len(easy_scripts) >= 1
        assert all(s["difficulty"] == "easy" for s in easy_scripts)

    @pytest.mark.asyncio
    async def test_filter_by_type(self, script_service_with_data):
        """Test filtering scripts by type."""
        service = script_service_with_data
        # Create test scripts
        await service.create_script(ScriptCreate(
            title="BenggeScript",
            description="Bengge description",
            script_type=ScriptType.BENGGE,
            difficulty=DifficultyLevel.EASY,
            min_players=4,
            max_players=6,
            duration_minutes=60
        ))
        await service.create_script(ScriptCreate(
            title="SocialScript",
            description="Social description",
            script_type=ScriptType.SOCIAL,
            difficulty=DifficultyLevel.HARD,
            min_players=6,
            max_players=8,
            duration_minutes=90
        ))

        bengge_scripts = await service.list_scripts(script_type=ScriptType.BENGGE)
        social_scripts = await service.list_scripts(script_type=ScriptType.SOCIAL)

        assert len(bengge_scripts) >= 1
        assert len(social_scripts) >= 1


class TestScriptUpdate:
    """Test script update functionality."""

    @pytest.fixture
    def script_service_with_script(self):
        return ScriptService()

    @pytest.mark.asyncio
    async def test_update_script_success(self, script_service_with_script):
        """Test successful script update."""
        service = script_service_with_script
        # Create script
        create_result = await service.create_script(ScriptCreate(
            title="UpdateTest",
            description="Original description for test",
            script_type=ScriptType.BENGGE,
            difficulty=DifficultyLevel.EASY,
            min_players=4,
            max_players=6,
            duration_minutes=60
        ))
        script_id = create_result["script_id"]

        update_data = ScriptUpdate(
            description="Updated description",
            difficulty=DifficultyLevel.HARD
        )

        result = await service.update_script(script_id, update_data)

        assert result["success"] is True

        # Verify update
        script = await service.get_script(script_id)
        assert script["description"] == "Updated description"
        assert script["difficulty"] == "hard"

    @pytest.mark.asyncio
    async def test_update_nonexistent_script(self, script_service_with_script):
        """Test updating non-existent script."""
        service = script_service_with_script

        update_data = ScriptUpdate(description="Updated description")
        result = await service.update_script("nonexistent", update_data)

        assert result["success"] is False
        assert result["error"] == "Script not found"


class TestScriptDeletion:
    """Test script deletion functionality."""

    @pytest.fixture
    def script_service_with_script(self):
        return ScriptService()

    @pytest.mark.asyncio
    async def test_delete_script_success(self, script_service_with_script):
        """Test successful script deletion."""
        service = script_service_with_script
        # Create script
        create_result = await service.create_script(ScriptCreate(
            title="DeleteTest",
            description="To be deleted test script",
            script_type=ScriptType.BENGGE,
            difficulty=DifficultyLevel.EASY,
            min_players=4,
            max_players=6,
            duration_minutes=60
        ))
        script_id = create_result["script_id"]

        result = await service.delete_script(script_id)

        assert result["success"] is True

        # Verify deletion
        script = await service.get_script(script_id)
        assert script is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_script(self, script_service_with_script):
        """Test deleting non-existent script."""
        service = script_service_with_script

        result = await service.delete_script("nonexistent")

        assert result["success"] is False
        assert result["error"] == "Script not found"


class TestScriptValidation:
    """Test script data validation."""

    def test_difficulty_levels(self):
        """Test difficulty level enum values."""
        assert DifficultyLevel.EASY.value == "easy"
        assert DifficultyLevel.STANDARD.value == "standard"
        assert DifficultyLevel.HARD.value == "hard"

    def test_script_types(self):
        """Test script type enum values."""
        assert ScriptType.BENGGE.value == "bengge"
        assert ScriptType.SOCIAL.value == "social"
        assert ScriptType.EMOTIONAL.value == "emotional"

    def test_player_count_validation(self):
        """Test player count validation."""
        from pydantic import ValidationError
        import pytest

        with pytest.raises(ValidationError):
            ScriptCreate(
                title="Test",
                description="Test",
                script_type=ScriptType.BENGGE,
                difficulty=DifficultyLevel.EASY,
                min_players=1,  # Too few
                max_players=4,
                duration_minutes=60
            )

        with pytest.raises(ValidationError):
            ScriptCreate(
                title="Test",
                description="Test",
                script_type=ScriptType.BENGGE,
                difficulty=DifficultyLevel.EASY,
                min_players=4,
                max_players=11,  # Too many
                duration_minutes=60
            )
