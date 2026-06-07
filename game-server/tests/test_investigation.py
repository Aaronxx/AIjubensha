"""Investigation system tests."""
import pytest
from datetime import datetime

from src.services.investigation_service import InvestigationService
from src.models.investigation import (
    InvestigationTarget, InvestigationTargetStatus, ClueRevealOrder,
    ClueLevel, InvestRequest
)


@pytest.fixture
def investigation_service():
    """Create a fresh investigation service for tests."""
    return InvestigationService()


class TestInvestigationSession:
    """Test investigation session management."""

    @pytest.mark.asyncio
    async def test_create_session(self, investigation_service):
        """Test creating investigation session."""
        session = await investigation_service.create_investigation_session(
            session_id="session_001",
            ap_per_round=[4, 5]
        )

        assert session.session_id == "session_001"
        assert session.max_rounds == 2
        assert len(session.rounds) == 2
        assert session.rounds[0].ap_per_player == 4

    @pytest.mark.asyncio
    async def test_add_target(self, investigation_service):
        """Test adding investigation target."""
        await investigation_service.create_investigation_session("session_002")

        target = await investigation_service.add_investigation_target(
            session_id="session_002",
            target_id="target_001",
            name="死者房间",
            description="搜查死者生前的房间",
            location="死者房间",
            ap_required=2,
            clues=[
                ClueRevealOrder(clue_id="clue_001", ap_required=1),
                ClueRevealOrder(clue_id="clue_002", ap_required=2)
            ]
        )

        assert target.target_id == "target_001"
        assert target.ap_required == 2
        assert len(target.clues) == 2


class TestPlayerRegistration:
    """Test player registration."""

    @pytest.mark.asyncio
    async def test_register_player(self, investigation_service):
        """Test registering player for investigation."""
        await investigation_service.create_investigation_session(
            "session_003",
            ap_per_round=[4]
        )

        player_state = await investigation_service.register_player(
            session_id="session_003",
            player_id="player_001"
        )

        assert player_state.player_id == "player_001"
        assert player_state.total_ap == 4
        assert player_state.remaining_ap == 4


class TestInvestigation:
    """Test investigation mechanics."""

    @pytest.mark.asyncio
    async def test_investigate_success(self, investigation_service):
        """Test successful investigation."""
        # Setup
        await investigation_service.create_investigation_session("session_004", [5])
        await investigation_service.register_player("session_004", "player_001")
        await investigation_service.add_investigation_target(
            "session_004", "target_001", "测试目标", "描述", "位置", 3,
            clues=[
                ClueRevealOrder(clue_id="clue_001", ap_required=1),
                ClueRevealOrder(clue_id="clue_002", ap_required=3)
            ]
        )

        # Make target available
        target = investigation_service._sessions["session_004"].targets[0]
        target.status = InvestigationTargetStatus.AVAILABLE

        # Investigate
        result = await investigation_service.investigate(
            session_id="session_004",
            player_id="player_001",
            target_id="target_001",
            ap_to_spend=2
        )

        assert result.success is True
        assert result.ap_spent == 2
        assert result.ap_remaining == 3
        assert len(result.clues_discovered) >= 1  # At least clue_001

    @pytest.mark.asyncio
    async def test_investigate_insufficient_ap(self, investigation_service):
        """Test investigation with insufficient AP."""
        await investigation_service.create_investigation_session("session_005", [2])
        await investigation_service.register_player("session_005", "player_001")
        await investigation_service.add_investigation_target(
            "session_005", "target_001", "测试目标", "描述", "位置", 3
        )

        target = investigation_service._sessions["session_005"].targets[0]
        target.status = InvestigationTargetStatus.AVAILABLE

        result = await investigation_service.investigate(
            session_id="session_005",
            player_id="player_001",
            target_id="target_001",
            ap_to_spend=5
        )

        assert result.success is False
        assert "Insufficient AP" in result.message


class TestClueRevealing:
    """Test clue revealing mechanics."""

    @pytest.mark.asyncio
    async def test_reveal_clue(self, investigation_service):
        """Test revealing clue to public."""
        # Setup
        await investigation_service.create_investigation_session("session_006", [5])
        await investigation_service.register_player("session_006", "player_001")
        await investigation_service.add_investigation_target(
            "session_006", "target_001", "测试", "描述", "位置", 2,
            clues=[ClueRevealOrder(clue_id="clue_001", ap_required=1)]
        )

        target = investigation_service._sessions["session_006"].targets[0]
        target.status = InvestigationTargetStatus.AVAILABLE

        # Discover clue first
        await investigation_service.investigate(
            "session_006", "player_001", "target_001", ap_to_spend=1
        )

        # Reveal to public
        result = await investigation_service.reveal_clue(
            session_id="session_006",
            player_id="player_001",
            clue_id="clue_001",
            reveal_to_public=True
        )

        assert result["success"] is True
        assert result["is_public"] is True


class TestRoundAdvancement:
    """Test investigation round advancement."""

    @pytest.mark.asyncio
    async def test_advance_round(self, investigation_service):
        """Test advancing to next round."""
        await investigation_service.create_investigation_session(
            "session_007",
            ap_per_round=[4, 5]
        )
        await investigation_service.register_player("session_007", "player_001")

        # Spend some AP in first round
        player = investigation_service._sessions["session_007"].player_states["player_001"]
        player.remaining_ap = 1

        # Advance round
        result = await investigation_service.advance_round("session_007")

        assert result["success"] is True
        assert result["current_round"] == 2
        assert result["ap_per_player"] == 5

        # Verify player got new AP
        player = investigation_service._sessions["session_007"].player_states["player_001"]
        assert player.remaining_ap == 5
