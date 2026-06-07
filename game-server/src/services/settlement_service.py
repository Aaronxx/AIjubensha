"""Settlement and achievement service."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import uuid4

from ..models.settlement import (
    SettlementRecord, SettlementSummary, SettlementRequest,
    PlayerStats, Achievement, PlayerAchievement,
    GameResult, PlayerRole, AchievementRarity, PlayerRankEntry
)


class SettlementService:
    """Manages game settlement and player statistics."""

    def __init__(self):
        # In-memory stores
        self._settlements: dict[str, SettlementRecord] = {}
        self._game_settlements: dict[str, List[str]] = {}  # game_id -> settlement_ids
        self._player_stats: dict[str, PlayerStats] = {}
        self._achievements: dict[str, Achievement] = {}
        self._player_achievements: dict[str, List[PlayerAchievement]] = {}  # player_id -> achievements

    async def settle_game(
        self,
        request: SettlementRequest,
        player_data: List[Dict[str, Any]]
    ) -> SettlementSummary:
        """Settle a game and generate records."""
        settlement_records = []

        # Calculate total votes for murderer
        votes_for_murderer = sum(
            1 for vote in request.votes.values()
            if vote == request.murderer_id
        )
        total_players = len(player_data)
        murderer_caught = votes_for_murderer > total_players / 2

        for player in player_data:
            player_id = player["player_id"]
            voted_for = request.votes.get(player_id)
            is_murderer = player["character_id"] == request.murderer_id
            voted_correctly = voted_for == request.murderer_id if voted_for else False

            # Determine result
            if is_murderer:
                result = GameResult.CAUGHT if murderer_caught else GameResult.ESCAPE
                escaped = not murderer_caught
            else:
                result = GameResult.VICTORY if voted_correctly else GameResult.DEFEAT
                escaped = None

            # Determine role
            role = PlayerRole.MURDERER if is_murderer else (
                PlayerRole.DETECTIVE if player.get("is_detective") else PlayerRole.CIVILIAN
            )

            record = SettlementRecord(
                settlement_id=str(uuid4()),
                game_session_id=request.game_session_id,
                script_id=player["script_id"],
                script_name=player["script_name"],
                player_id=player_id,
                player_name=player["player_name"],
                character_id=player["character_id"],
                character_name=player["character_name"],
                role=role,
                result=result,
                voted_correctly=voted_correctly,
                is_murderer=is_murderer,
                escaped=escaped,
                vote_target=voted_for,
                actual_murderer=request.murderer_id,
                ap_spent=player.get("ap_spent", 0),
                clues_discovered=player.get("clues_discovered", 0),
                clues_revealed=player.get("clues_revealed", 0),
                messages_sent=player.get("messages_sent", 0),
                private_chats=player.get("private_chats", 0),
                game_duration_minutes=player.get("game_duration", 0)
            )

            self._settlements[record.settlement_id] = record
            settlement_records.append(record)

            # Update player stats
            await self._update_player_stats(record)

        # Create summary
        murderer_record = next(
            (r for r in settlement_records if r.is_murderer),
            None
        )
        votes_for_murderer = sum(
            1 for r in settlement_records
            if r.vote_target == request.murderer_id
        )

        summary = SettlementSummary(
            game_session_id=request.game_session_id,
            script_id=player_data[0]["script_id"],
            script_name=player_data[0]["script_name"],
            players=settlement_records,
            murderer_id=request.murderer_id,
            murderer_name=murderer_record.character_name if murderer_record else "Unknown",
            murderer_caught=votes_for_murderer > len(player_data) / 2,
            votes_for_murderer=votes_for_murderer,
            total_duration_minutes=sum(r.game_duration_minutes for r in settlement_records) // max(1, len(settlement_records)),
            total_clues_discovered=sum(r.clues_discovered for r in settlement_records),
            total_messages=sum(r.messages_sent for r in settlement_records)
        )

        self._game_settlements[request.game_session_id] = [
            r.settlement_id for r in settlement_records
        ]

        return summary

    async def _update_player_stats(self, record: SettlementRecord):
        """Update player statistics."""
        player_id = record.player_id

        if player_id not in self._player_stats:
            self._player_stats[player_id] = PlayerStats(player_id=player_id)

        stats = self._player_stats[player_id]
        stats.total_games += 1

        # Update role-specific stats
        if record.role == PlayerRole.DETECTIVE:
            stats.games_as_detective += 1
            stats.detective_games += 1
            if record.voted_correctly:
                stats.detective_success += 1
        elif record.role == PlayerRole.MURDERER:
            stats.games_as_murderer += 1
            stats.murderer_games += 1
            if record.escaped:
                stats.murderer_escapes += 1
        else:
            stats.games_as_civilian += 1

        # Update vote accuracy
        if not record.is_murderer:
            if record.voted_correctly:
                stats.correct_votes += 1
            else:
                stats.incorrect_votes += 1

        # Recalculate rates
        total_votes = stats.correct_votes + stats.incorrect_votes
        stats.vote_accuracy = stats.correct_votes / total_votes if total_votes > 0 else 0.0

        stats.detective_rate = stats.detective_success / stats.detective_games if stats.detective_games > 0 else 0.0
        stats.escape_rate = stats.murderer_escapes / stats.murderer_games if stats.murderer_games > 0 else 0.0

        # Update cumulative data
        stats.total_ap_spent += record.ap_spent
        stats.total_clues_discovered += record.clues_discovered
        stats.total_messages_sent += record.messages_sent
        stats.total_game_time_minutes += record.game_duration_minutes

        stats.updated_at = datetime.now()

    async def get_player_stats(self, player_id: str) -> Optional[PlayerStats]:
        """Get player statistics."""
        return self._player_stats.get(player_id)

    async def get_player_settlements(
        self,
        player_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[SettlementRecord]:
        """Get player's settlement records."""
        settlements = [
            s for s in self._settlements.values()
            if s.player_id == player_id
        ]
        settlements.sort(key=lambda x: x.created_at, reverse=True)
        return settlements[offset:offset + limit]

    async def create_achievement(self, achievement: Achievement) -> Achievement:
        """Create a new achievement."""
        self._achievements[achievement.achievement_id] = achievement
        return achievement

    async def get_achievements(
        self,
        rarity: Optional[AchievementRarity] = None
    ) -> List[Achievement]:
        """Get all achievements."""
        achievements = list(self._achievements.values())
        if rarity:
            achievements = [a for a in achievements if a.rarity == rarity]
        return achievements

    async def check_achievements(self, player_id: str) -> List[Achievement]:
        """Check and unlock achievements for a player."""
        stats = await self.get_player_stats(player_id)
        if not stats:
            return []

        unlocked = []
        player_achievements = self._player_achievements.get(player_id, [])
        unlocked_ids = {pa.achievement_id for pa in player_achievements}

        for achievement in self._achievements.values():
            if achievement.achievement_id in unlocked_ids:
                continue

            # Check condition
            if await self._check_achievement_condition(stats, achievement):
                player_achievement = PlayerAchievement(
                    player_id=player_id,
                    achievement_id=achievement.achievement_id
                )

                if player_id not in self._player_achievements:
                    self._player_achievements[player_id] = []
                self._player_achievements[player_id].append(player_achievement)

                # Update player stats
                stats.achievements_unlocked.append(achievement.achievement_id)
                stats.stars_earned += achievement.reward_stars

                unlocked.append(achievement)

        return unlocked

    async def _check_achievement_condition(
        self,
        stats: PlayerStats,
        achievement: Achievement
    ) -> bool:
        """Check if player meets achievement condition."""
        condition_type = achievement.condition_type
        value = achievement.condition_value

        if condition_type == "games_played":
            return stats.total_games >= value.get("count", 0)
        elif condition_type == "correct_votes":
            return stats.correct_votes >= value.get("count", 0)
        elif condition_type == "vote_accuracy":
            return stats.vote_accuracy >= value.get("rate", 0.0)
        elif condition_type == "detective_success":
            return stats.detective_success >= value.get("count", 0)
        elif condition_type == "escape_as_murderer":
            return stats.murderer_escapes >= value.get("count", 0)
        elif condition_type == "clues_discovered":
            return stats.total_clues_discovered >= value.get("count", 0)
        elif condition_type == "messages_sent":
            return stats.total_messages_sent >= value.get("count", 0)

        return False

    async def get_player_achievements(self, player_id: str) -> List[Dict[str, Any]]:
        """Get player's unlocked achievements."""
        player_achievements = self._player_achievements.get(player_id, [])
        result = []

        for pa in player_achievements:
            achievement = self._achievements.get(pa.achievement_id)
            if achievement:
                result.append({
                    "achievement_id": achievement.achievement_id,
                    "name": achievement.name,
                    "description": achievement.description,
                    "rarity": achievement.rarity.value,
                    "icon": achievement.icon,
                    "unlocked_at": pa.unlocked_at.isoformat(),
                    "reward_stars": achievement.reward_stars
                })

        return result

    async def get_leaderboard(
        self,
        category: str = "overall",
        limit: int = 100
    ) -> List[PlayerRankEntry]:
        """Get leaderboard."""
        entries = []

        for player_id, stats in self._player_stats.items():
            score = 0.0

            if category == "investigation":
                score = stats.vote_accuracy * 100 + stats.correct_votes * 10
            elif category == "social":
                score = stats.total_messages_sent * 2 + stats.total_clues_discovered * 5
            elif category == "overall":
                score = (
                    stats.vote_accuracy * 50 +
                    stats.detective_rate * 30 +
                    stats.escape_rate * 20 +
                    stats.total_games * 5
                )
            else:
                score = stats.total_games * 10

            entries.append(PlayerRankEntry(
                rank=0,  # Will be calculated
                player_id=player_id,
                player_name=f"Player {player_id[-4:]}",  # Placeholder
                score=score,
                stats={
                    "total_games": stats.total_games,
                    "vote_accuracy": stats.vote_accuracy,
                    "correct_votes": stats.correct_votes
                }
            ))

        # Sort and assign ranks
        entries.sort(key=lambda x: x.score, reverse=True)
        for i, entry in enumerate(entries[:limit], 1):
            entry.rank = i

        return entries[:limit]

    async def get_settlement_summary(
        self,
        game_session_id: str
    ) -> Optional[SettlementSummary]:
        """Get settlement summary for a game."""
        settlement_ids = self._game_settlements.get(game_session_id)
        if not settlement_ids:
            return None

        players = [
            self._settlements[sid]
            for sid in settlement_ids
            if sid in self._settlements
        ]

        if not players:
            return None

        murderer_record = next(
            (r for r in players if r.is_murderer),
            None
        )

        return SettlementSummary(
            game_session_id=game_session_id,
            script_id=players[0].script_id,
            script_name=players[0].script_name,
            players=players,
            murderer_id=murderer_record.character_id if murderer_record else "",
            murderer_name=murderer_record.character_name if murderer_record else "Unknown",
            murderer_caught=not murderer_record.escaped if murderer_record else False,
            total_duration_minutes=sum(p.game_duration_minutes for p in players) // max(1, len(players)),
            total_clues_discovered=sum(p.clues_discovered for p in players),
            total_messages=sum(p.messages_sent for p in players)
        )


# Singleton instance
settlement_service = SettlementService()
