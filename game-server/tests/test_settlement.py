"""Settlement and achievement system tests."""
import pytest
from datetime import datetime

from src.services.settlement_service import SettlementService
from src.models.settlement import (
    SettlementRequest, GameResult, PlayerRole,
    AchievementRarity, Achievement
)


@pytest.fixture
def settlement_service():
    """Create a fresh settlement service for tests."""
    service = SettlementService()
    # Clear any existing data
    service._settlements.clear()
    service._game_settlements.clear()
    service._player_stats.clear()
    service._achievements.clear()
    service._player_achievements.clear()
    return service


@pytest.fixture
def sample_player_data():
    """Sample player data for settlement."""
    return [
        {
            "player_id": "player_001",
            "player_name": "Alice",
            "character_id": "char_001",
            "character_name": "苏晚晴",
            "script_id": "script_001",
            "script_name": "山庄晚宴",
            "is_detective": True,
            "ap_spent": 8,
            "clues_discovered": 5,
            "clues_revealed": 3,
            "messages_sent": 25,
            "private_chats": 3,
            "game_duration": 75
        },
        {
            "player_id": "player_002",
            "player_name": "Bob",
            "character_id": "char_002",
            "character_name": "周明远",
            "script_id": "script_001",
            "script_name": "山庄晚宴",
            "is_detective": False,
            "ap_spent": 6,
            "clues_discovered": 4,
            "clues_revealed": 2,
            "messages_sent": 20,
            "private_chats": 2,
            "game_duration": 75
        },
        {
            "player_id": "player_003",
            "player_name": "Charlie",
            "character_id": "char_003",
            "character_name": "陈警官",
            "script_id": "script_001",
            "script_name": "山庄晚宴",
            "is_detective": False,
            "ap_spent": 7,
            "clues_discovered": 6,
            "clues_revealed": 4,
            "messages_sent": 30,
            "private_chats": 4,
            "game_duration": 75
        }
    ]


class TestGameSettlement:
    """Test game settlement."""

    @pytest.mark.asyncio
    async def test_settle_game_detective_catches_murderer(self, settlement_service, sample_player_data):
        """Test settlement when detective catches murderer."""
        # Votes: everyone votes for char_002 (Bob/周明远) who is the murderer
        request = SettlementRequest(
            game_session_id="game_001",
            murderer_id="char_002",
            votes={
                "player_001": "char_002",  # Detective votes for murderer
                "player_002": "char_003",  # Murderer votes for someone else
                "player_003": "char_002"   # Civilian votes for murderer
            }
        )

        summary = await settlement_service.settle_game(request, sample_player_data)

        assert summary.game_session_id == "game_001"
        assert summary.murderer_id == "char_002"
        assert summary.murderer_caught is True
        assert summary.votes_for_murderer == 2
        assert len(summary.players) == 3

        # Check detective result
        detective_record = next(
            (r for r in summary.players if r.role == PlayerRole.DETECTIVE),
            None
        )
        assert detective_record is not None
        assert detective_record.voted_correctly is True
        assert detective_record.result == GameResult.VICTORY

        # Check murderer result
        murderer_record = next(
            (r for r in summary.players if r.is_murderer),
            None
        )
        assert murderer_record is not None
        assert murderer_record.result == GameResult.CAUGHT
        assert murderer_record.escaped is False

    @pytest.mark.asyncio
    async def test_settle_game_murderer_escapes(self, settlement_service, sample_player_data):
        """Test settlement when murderer escapes."""
        # Votes: only 1 person votes for murderer (not enough)
        request = SettlementRequest(
            game_session_id="game_002",
            murderer_id="char_002",
            votes={
                "player_001": "char_003",  # Detective votes wrong
                "player_002": "char_003",  # Murderer votes for someone else
                "player_003": "char_002"   # Only 1 vote for murderer
            }
        )

        summary = await settlement_service.settle_game(request, sample_player_data)

        assert summary.murderer_caught is False
        assert summary.votes_for_murderer == 1

        # Check murderer result
        murderer_record = next(
            (r for r in summary.players if r.is_murderer),
            None
        )
        assert murderer_record.result == GameResult.ESCAPE
        assert murderer_record.escaped is True

        # Check detective result
        detective_record = next(
            (r for r in summary.players if r.role == PlayerRole.DETECTIVE),
            None
        )
        assert detective_record.voted_correctly is False
        assert detective_record.result == GameResult.DEFEAT

    @pytest.mark.asyncio
    async def test_settle_game_civilian_wrong_vote(self, settlement_service, sample_player_data):
        """Test civilian with wrong vote."""
        request = SettlementRequest(
            game_session_id="game_003",
            murderer_id="char_002",
            votes={
                "player_001": "char_002",  # Detective correct
                "player_002": "char_003",  # Murderer
                "player_003": "char_001"   # Civilian wrong
            }
        )

        summary = await settlement_service.settle_game(request, sample_player_data)

        civilian_record = next(
            (r for r in summary.players if r.role == PlayerRole.CIVILIAN),
            None
        )
        assert civilian_record.voted_correctly is False
        assert civilian_record.result == GameResult.DEFEAT


class TestPlayerStats:
    """Test player statistics."""

    @pytest.mark.asyncio
    async def test_update_player_stats(self, settlement_service, sample_player_data):
        """Test player stats are updated after settlement."""
        request = SettlementRequest(
            game_session_id="game_001",
            murderer_id="char_002",
            votes={
                "player_001": "char_002",
                "player_002": "char_003",
                "player_003": "char_002"
            }
        )

        await settlement_service.settle_game(request, sample_player_data)

        # Check player_001 stats (detective, voted correctly)
        stats = await settlement_service.get_player_stats("player_001")
        assert stats is not None
        assert stats.total_games == 1
        assert stats.games_as_detective == 1
        assert stats.detective_games == 1
        assert stats.detective_success == 1
        assert stats.correct_votes == 1
        assert stats.vote_accuracy == 1.0
        assert stats.total_ap_spent == 8

        # Check player_002 stats (murderer, caught)
        stats = await settlement_service.get_player_stats("player_002")
        assert stats.total_games == 1
        assert stats.games_as_murderer == 1
        assert stats.murderer_games == 1
        assert stats.murderer_escapes == 0
        assert stats.escape_rate == 0.0

    @pytest.mark.asyncio
    async def test_stats_accumulation(self, settlement_service, sample_player_data):
        """Test stats accumulate over multiple games."""
        # Game 1
        request1 = SettlementRequest(
            game_session_id="game_001",
            murderer_id="char_002",
            votes={"player_001": "char_002"}
        )
        await settlement_service.settle_game(request1, [sample_player_data[0]])

        # Game 2 - player_001 votes wrong
        request2 = SettlementRequest(
            game_session_id="game_002",
            murderer_id="char_003",
            votes={"player_001": "char_002"}
        )
        await settlement_service.settle_game(request2, [sample_player_data[0]])

        stats = await settlement_service.get_player_stats("player_001")
        assert stats.total_games == 2
        assert stats.correct_votes == 1
        assert stats.incorrect_votes == 1
        assert stats.vote_accuracy == 0.5

    @pytest.mark.asyncio
    async def test_get_player_settlements(self, settlement_service, sample_player_data):
        """Test retrieving player settlement history."""
        request = SettlementRequest(
            game_session_id="game_001",
            murderer_id="char_002",
            votes={"player_001": "char_002", "player_002": "char_003"}
        )
        await settlement_service.settle_game(request, sample_player_data)

        settlements = await settlement_service.get_player_settlements("player_001")
        assert len(settlements) == 1
        assert settlements[0].player_id == "player_001"
        assert settlements[0].script_name == "山庄晚宴"


class TestAchievements:
    """Test achievement system."""

    @pytest.mark.asyncio
    async def test_create_achievement(self, settlement_service):
        """Test creating an achievement."""
        achievement = Achievement(
            achievement_id="ach_001",
            name="初出茅庐",
            description="首次投对真凶",
            rarity=AchievementRarity.COMMON,
            condition_type="correct_votes",
            condition_value={"count": 1},
            reward_stars=10
        )

        created = await settlement_service.create_achievement(achievement)
        assert created.achievement_id == "ach_001"
        assert created.name == "初出茅庐"

    @pytest.mark.asyncio
    async def test_check_achievements(self, settlement_service, sample_player_data):
        """Test achievement unlocking."""
        # Create achievement
        achievement = Achievement(
            achievement_id="ach_001",
            name="初出茅庐",
            description="首次投对真凶",
            rarity=AchievementRarity.COMMON,
            condition_type="correct_votes",
            condition_value={"count": 1},
            reward_stars=10
        )
        await settlement_service.create_achievement(achievement)

        # Settle game
        request = SettlementRequest(
            game_session_id="game_001",
            murderer_id="char_002",
            votes={"player_001": "char_002"}
        )
        await settlement_service.settle_game(request, [sample_player_data[0]])

        # Check achievements
        unlocked = await settlement_service.check_achievements("player_001")
        assert len(unlocked) == 1
        assert unlocked[0].achievement_id == "ach_001"

        # Check player stats updated
        stats = await settlement_service.get_player_stats("player_001")
        assert "ach_001" in stats.achievements_unlocked
        assert stats.stars_earned == 10

    @pytest.mark.asyncio
    async def test_check_achievements_not_met(self, settlement_service, sample_player_data):
        """Test achievement not unlocked when condition not met."""
        # Create high requirement achievement
        achievement = Achievement(
            achievement_id="ach_002",
            name="神探",
            description="连续5局投对真凶",
            rarity=AchievementRarity.EPIC,
            condition_type="correct_votes",
            condition_value={"count": 5},
            reward_stars=50
        )
        await settlement_service.create_achievement(achievement)

        # Settle game with only 1 correct vote
        request = SettlementRequest(
            game_session_id="game_001",
            murderer_id="char_002",
            votes={"player_001": "char_002"}
        )
        await settlement_service.settle_game(request, [sample_player_data[0]])

        # Check achievements - should not unlock
        unlocked = await settlement_service.check_achievements("player_001")
        assert len(unlocked) == 0

    @pytest.mark.asyncio
    async def test_get_player_achievements(self, settlement_service, sample_player_data):
        """Test getting player achievements."""
        # Create and unlock achievement
        achievement = Achievement(
            achievement_id="ach_001",
            name="初出茅庐",
            description="首次投对真凶",
            rarity=AchievementRarity.COMMON,
            condition_type="correct_votes",
            condition_value={"count": 1},
            reward_stars=10
        )
        await settlement_service.create_achievement(achievement)

        request = SettlementRequest(
            game_session_id="game_001",
            murderer_id="char_002",
            votes={"player_001": "char_002"}
        )
        await settlement_service.settle_game(request, [sample_player_data[0]])
        await settlement_service.check_achievements("player_001")

        # Get achievements
        achievements = await settlement_service.get_player_achievements("player_001")
        assert len(achievements) == 1
        assert achievements[0]["name"] == "初出茅庐"
        assert achievements[0]["reward_stars"] == 10


class TestLeaderboard:
    """Test leaderboard."""

    @pytest.mark.asyncio
    async def test_get_leaderboard(self, settlement_service, sample_player_data):
        """Test getting leaderboard."""
        # Settle multiple games with different players
        for i in range(3):
            player_data = [{
                **sample_player_data[0],
                "player_id": f"player_00{i+1}",
                "player_name": f"Player{i+1}"
            }]
            request = SettlementRequest(
                game_session_id=f"game_00{i+1}",
                murderer_id="char_002",
                votes={f"player_00{i+1}": "char_002"}
            )
            await settlement_service.settle_game(request, player_data)

        leaderboard = await settlement_service.get_leaderboard(category="overall", limit=10)

        assert len(leaderboard) == 3
        assert leaderboard[0].rank == 1
        assert all(entry.score > 0 for entry in leaderboard)

    @pytest.mark.asyncio
    async def test_get_leaderboard_investigation(self, settlement_service, sample_player_data):
        """Test investigation category leaderboard."""
        request = SettlementRequest(
            game_session_id="game_001",
            murderer_id="char_002",
            votes={"player_001": "char_002"}
        )
        await settlement_service.settle_game(request, [sample_player_data[0]])

        leaderboard = await settlement_service.get_leaderboard(category="investigation")

        assert len(leaderboard) == 1
        # Investigation score based on vote accuracy and correct votes
        assert leaderboard[0].score > 0


class TestSettlementSummary:
    """Test settlement summary retrieval."""

    @pytest.mark.asyncio
    async def test_get_settlement_summary(self, settlement_service, sample_player_data):
        """Test getting settlement summary."""
        request = SettlementRequest(
            game_session_id="game_001",
            murderer_id="char_002",
            votes={
                "player_001": "char_002",
                "player_002": "char_003",
                "player_003": "char_002"
            }
        )
        await settlement_service.settle_game(request, sample_player_data)

        summary = await settlement_service.get_settlement_summary("game_001")

        assert summary is not None
        assert summary.game_session_id == "game_001"
        assert summary.script_name == "山庄晚宴"
        assert summary.murderer_id == "char_002"
        assert len(summary.players) == 3
        assert summary.total_clues_discovered > 0

    @pytest.mark.asyncio
    async def test_get_settlement_summary_not_found(self, settlement_service):
        """Test getting non-existent settlement summary."""
        summary = await settlement_service.get_settlement_summary("non_existent_game")
        assert summary is None
