"""Character management tests."""
import pytest
import asyncio
import uuid
from datetime import datetime

from src.services.character_service import CharacterService
from src.models.character import (
    CharacterCreate, CharacterUpdate, CharacterScriptAssignment,
    PersonalityMatrix, PersonalityDimension, KnowledgeEntry,
    ArcState, ArcTransition, GoalSystem, SilenceStrategy,
    CharacterType, CharacterRoleInScript, RelationshipEntry
)


@pytest.fixture
def character_service():
    """Create a fresh character service for tests."""
    return CharacterService()


def create_test_personality():
    """Create a test personality matrix."""
    return PersonalityMatrix(
        extroversion=PersonalityDimension(value=0.3, description="内向"),
        aggressiveness=PersonalityDimension(value=0.2, description="温和"),
        honesty=PersonalityDimension(value=0.8, description="诚实"),
        rationality=PersonalityDimension(value=0.7, description="理性"),
        speaking_style="温和礼貌但保持距离，用词文雅"
    )


def create_test_knowledge():
    """Create test knowledge entries."""
    return [
        KnowledgeEntry(
            fact_id="fact_001",
            content="我是画廊老板",
            level=1,
            release_condition="直接询问",
            is_secret=False
        ),
        KnowledgeEntry(
            fact_id="fact_002",
            content="昨晚看到死者",
            level=2,
            release_condition="建立信任后",
            is_secret=False
        )
    ]


def create_test_goals():
    """Create test goals."""
    return GoalSystem(
        primary_goal="保护自己的秘密",
        secondary_goals=["维护画廊声誉"],
        red_lines=["不透露商业机密"],
        attitude_to_others={}
    )


def create_test_arc_states():
    """Create test arc states."""
    return [
        ArcState(
            state_id="distant",
            name="疏离客气",
            description="保持距离的礼貌",
            attitude_modifier=0.0,
            info_release_levels=[1],
            silence_strategy=SilenceStrategy.POLITE_REFUSAL
        ),
        ArcState(
            state_id="trusting",
            name="信任",
            description="开始信任对方",
            attitude_modifier=0.3,
            info_release_levels=[1, 2],
            silence_strategy=SilenceStrategy.TOPIC_SHIFT
        )
    ]


def create_test_transitions():
    """Create test arc transitions."""
    return [
        ArcTransition(
            from_state="distant",
            to_state="trusting",
            trigger_condition="attitude >= 0.3",
            required_attitude=0.3
        )
    ]


def create_test_character_data(name_suffix=""):
    """Create test character data."""
    return CharacterCreate(
        name=f"SuWanqing{name_suffix}",
        age=30,
        occupation="Gallery Owner",
        background="Operating a gallery for ten years, had business dealings with the deceased",
        personality=create_test_personality(),
        knowledge=create_test_knowledge(),
        goals=create_test_goals(),
        arc_states=create_test_arc_states(),
        arc_transitions=create_test_transitions(),
        default_silence_strategy=SilenceStrategy.POLITE_REFUSAL,
        character_anchor="You are Su Wanqing, 30 years old, a gallery owner. You speak politely but maintain distance, using refined language. You value your privacy and reputation."
    )


class TestCharacterCreation:
    """Test character creation."""

    @pytest.mark.asyncio
    async def test_create_character_success(self, character_service):
        """Test successful character creation."""
        char_data = create_test_character_data()
        result = await character_service.create_character(char_data)

        assert result["success"] is True
        assert "character_id" in result
        assert result["character"]["name"] == "SuWanqing"
        assert result["character"]["occupation"] == "Gallery Owner"

    @pytest.mark.asyncio
    async def test_create_character_duplicate_name(self, character_service):
        """Test creating character with duplicate name."""
        char_data = create_test_character_data()
        await character_service.create_character(char_data)

        result = await character_service.create_character(char_data)

        assert result["success"] is False
        assert "already exists" in result["error"]


class TestCharacterRetrieval:
    """Test character retrieval."""

    @pytest.mark.asyncio
    async def test_get_character_by_id(self, character_service):
        """Test getting character by ID."""
        char_data = create_test_character_data("_get")
        create_result = await character_service.create_character(char_data)
        char_id = create_result["character_id"]

        retrieved = await character_service.get_character(char_id)

        assert retrieved is not None
        assert retrieved["id"] == char_id
        assert retrieved["name"] == "SuWanqing_get"

    @pytest.mark.asyncio
    async def test_get_nonexistent_character(self, character_service):
        """Test getting non-existent character."""
        result = await character_service.get_character("nonexistent-id")
        assert result is None


class TestCharacterUpdate:
    """Test character updates."""

    @pytest.mark.asyncio
    async def test_update_character_success(self, character_service):
        """Test successful character update."""
        char_data = create_test_character_data("_update")
        create_result = await character_service.create_character(char_data)
        char_id = create_result["character_id"]

        update_data = CharacterUpdate(
            age=35,
            background="Updated background information"
        )
        result = await character_service.update_character(char_id, update_data)

        assert result["success"] is True
        assert result["character"]["age"] == 35


class TestCharacterScriptAssignment:
    """Test character script assignment."""

    @pytest.mark.asyncio
    async def test_assign_to_script(self, character_service):
        """Test assigning character to script."""
        char_data = create_test_character_data("_script")
        create_result = await character_service.create_character(char_data)
        char_id = create_result["character_id"]

        role = CharacterRoleInScript(
            is_murderer=False,
            character_type=CharacterType.UNAWARE,
            self_awareness="不知道自己是凶手",
            lie_topics=[],
            protected_info=["商业机密"]
        )
        assignment = CharacterScriptAssignment(
            script_id="script_001",
            role=role
        )

        result = await character_service.assign_to_script(char_id, assignment)

        assert result["success"] is True
