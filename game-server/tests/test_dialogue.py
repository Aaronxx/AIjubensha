"""Dialogue system tests."""
import pytest
import asyncio
from datetime import datetime

from src.services.dialogue_service import DialogueService
from src.models.dialogue import (
    DialogueContext, StructuredNPCOutput, DialogueStateUpdate,
    MessageType, PrivateChatRequest
)


@pytest.fixture
def dialogue_service():
    """Create a fresh dialogue service for tests."""
    return DialogueService()


class TestDialogueMessageStorage:
    """Test dialogue message storage."""

    @pytest.mark.asyncio
    async def test_store_message(self, dialogue_service):
        """Test storing a dialogue message."""
        message = await dialogue_service.store_message(
            session_id="session_001",
            room_id="room_001",
            sender_id="player_001",
            sender_name="TestPlayer",
            sender_type=MessageType.PLAYER,
            content="Hello everyone!",
            metadata={"test": "data"}
        )

        assert message.message_id is not None
        assert message.content == "Hello everyone!"
        assert message.sender_type == MessageType.PLAYER

    @pytest.mark.asyncio
    async def test_get_session_messages(self, dialogue_service):
        """Test retrieving session messages."""
        # Store multiple messages
        for i in range(5):
            await dialogue_service.store_message(
                session_id="session_test",
                room_id="room_001",
                sender_id=f"player_{i}",
                sender_name=f"Player{i}",
                sender_type=MessageType.PLAYER,
                content=f"Message {i}"
            )

        messages = await dialogue_service.get_messages_for_session("session_test")

        assert len(messages) == 5


class TestNPCPromptBuilding:
    """Test NPC prompt building."""

    def test_build_npc_prompt(self, dialogue_service):
        """Test building NPC prompt."""
        context = DialogueContext(
            character_id="char_001",
            character_anchor="You are a gallery owner named Su Wanqing.",
            current_act="act_2",
            arc_state="distant",
            emotional_tag="neutral",
            knowledge_released=["fact_001"],
            knowledge_hidden=["fact_002", "fact_003"],
            honesty_mode="truth",
            lie_topics=[],
            silence_strategy="polite_refusal",
            recent_context=[],
            fact_ledger=[],
            attitude_to_player=0.2
        )

        prompt = dialogue_service.build_npc_prompt(context, "What do you know?")

        assert "Su Wanqing" in prompt
        assert "act_2" in prompt
        assert "fact_001" in prompt
        assert "必须说真话" in prompt


class TestNPCResponseParsing:
    """Test NPC response parsing."""

    def test_parse_npc_response(self, dialogue_service):
        """Test parsing NPC API response."""
        api_response = {
            "reply": "I saw the victim last night.",
            "emotional_tag": "nervous-low",
            "info_revealed": [
                {"fact_id": "fact_001", "content": "Saw victim last night"}
            ],
            "attitude_shift": None,
            "arc_state_transition": None
        }

        parsed = dialogue_service.parse_npc_response(api_response)

        assert parsed.reply == "I saw the victim last night."
        assert parsed.emotional_tag == "nervous-low"
        assert len(parsed.info_revealed) == 1


class TestSpeechQuota:
    """Test speech quota management."""

    @pytest.mark.asyncio
    async def test_init_speech_quota(self, dialogue_service):
        """Test initializing speech quota."""
        await dialogue_service.init_speech_quota("char_001", "act_2", max_speeches=5)

        quota_key = "char_001_act_2"
        quota = dialogue_service._speech_quotas.get(quota_key)

        assert quota is not None
        assert quota.max_speeches == 5
        assert quota.remaining_speeches == 5

    @pytest.mark.asyncio
    async def test_consume_speech_quota(self, dialogue_service):
        """Test consuming speech quota."""
        await dialogue_service.init_speech_quota("char_002", "act_2", max_speeches=3)

        await dialogue_service.consume_speech_quota("char_002", "act_2")

        quota_key = "char_002_act_2"
        quota = dialogue_service._speech_quotas.get(quota_key)

        assert quota.used_speeches == 1
        assert quota.remaining_speeches == 2


class TestPrivateChat:
    """Test private chat functionality."""

    @pytest.mark.asyncio
    async def test_create_private_chat(self, dialogue_service):
        """Test creating private chat session."""
        session = await dialogue_service.create_private_chat(
            player_id="player_001",
            npc_id="npc_001"
        )

        assert session.session_id is not None
        assert session.player_id == "player_001"
        assert session.npc_id == "npc_001"
        assert session.is_active is True

    @pytest.mark.asyncio
    async def test_end_private_chat(self, dialogue_service):
        """Test ending private chat session."""
        session = await dialogue_service.create_private_chat(
            player_id="player_001",
            npc_id="npc_001"
        )

        result = await dialogue_service.end_private_chat(session.session_id)

        assert result is True

        # Verify session is ended
        ended_session = await dialogue_service.get_private_chat(session.session_id)
        assert ended_session.is_active is False


class TestAutonomousTrigger:
    """Test autonomous speech triggers."""

    @pytest.mark.asyncio
    async def test_check_autonomous_trigger(self, dialogue_service):
        """Test checking autonomous trigger."""
        await dialogue_service.init_speech_quota("char_001", "act_2", max_speeches=5)

        context = {
            "current_act": "act_2",
            "player_id": "player_001",
            "message_id": "msg_001"
        }

        trigger = await dialogue_service.check_autonomous_trigger(
            session_id="session_001",
            character_id="char_001",
            trigger_type="mentioned",
            context=context
        )

        assert trigger is not None
        assert trigger.trigger_type == "mentioned"
        assert trigger.urgency == 3
