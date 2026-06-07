"""9-phase Mingzhen mode game session state machine."""
from __future__ import annotations

from .models import GamePhase, PlayerRole, PlayerSession

PHASE_ORDER = [
    GamePhase.PREPARATION,
    GamePhase.ACT_1_TURN_TALK,
    GamePhase.ROUND_1_SEARCH,
    GamePhase.ACT_2_DISCUSS,
    GamePhase.DETECTIVE_VOTE,
    GamePhase.ROUND_2_SEARCH,
    GamePhase.ACT_3_DISCUSS,
    GamePhase.FINAL_VOTE,
    GamePhase.RESULT,
    GamePhase.FINISHED,
]

ROUND_1_AP = 15
ROUND_2_AP = 20
DETECTIVE_AP_BONUS = 1


class GameSession:
    """Manages a single game session through 9 phases."""

    def __init__(self, session_id: str, script_id: str):
        self.session_id = session_id
        self.script_id = script_id
        self.current_phase = GamePhase.PREPARATION
        self.players: dict[str, PlayerSession] = {}
        self._phase_index = 0
        self._turn_order: list[str] = []
        self._turn_index: int = -1
        self.is_free_exchange = False

    # ── Player management ──

    def add_player(self, player_id: str, character_id: str, role: PlayerRole, is_ai: bool = False):
        self.players[player_id] = PlayerSession(
            player_id=player_id, character_id=character_id, role=role, is_ai=is_ai,
        )

    def get_player(self, player_id: str) -> PlayerSession | None:
        return self.players.get(player_id)

    # ── Phase control ──

    def player_confirm(self, player_id: str):
        """Player confirms preparation complete."""
        p = self.players.get(player_id)
        if p:
            p.has_confirmed = True
        if self.current_phase == GamePhase.PREPARATION and self._all_confirmed():
            self._advance()

    def force_phase_advance(self):
        """Admin/timeout: force advance to next phase."""
        self._advance()

    def _all_confirmed(self) -> bool:
        return all(p.has_confirmed for p in self.players.values())

    def _advance(self):
        self._phase_index += 1
        if self._phase_index < len(PHASE_ORDER):
            self.current_phase = PHASE_ORDER[self._phase_index]
            self._on_phase_enter()

    def _on_phase_enter(self):
        """Phase-specific initialization."""
        phase = self.current_phase

        if phase == GamePhase.ACT_1_TURN_TALK:
            self._init_turn_order()
            self.is_free_exchange = False

        elif phase == GamePhase.ROUND_1_SEARCH:
            for p in self.players.values():
                p.ap_remaining = ROUND_1_AP + (DETECTIVE_AP_BONUS if p.role == PlayerRole.DETECTIVE else 0)

        elif phase == GamePhase.ROUND_2_SEARCH:
            for p in self.players.values():
                p.ap_remaining = ROUND_2_AP + (DETECTIVE_AP_BONUS if p.role == PlayerRole.DETECTIVE else 0)

        elif phase in (GamePhase.ACT_2_DISCUSS, GamePhase.ACT_3_DISCUSS):
            for p in self.players.values():
                p.speech_count = 0
                p.question_count = {}
            self.is_free_exchange = True

        elif phase == GamePhase.DETECTIVE_VOTE:
            pass  # Detective-only vote

        elif phase == GamePhase.FINAL_VOTE:
            for p in self.players.values():
                p.vote_target = None

        elif phase == GamePhase.RESULT:
            pass  # Display results

        elif phase == GamePhase.FINISHED:
            pass  # Game over

    # ── Act 1: Turn-taking ──

    def _init_turn_order(self):
        # Detective speaks first, then others
        order = []
        for pid, p in self.players.items():
            if p.role == PlayerRole.DETECTIVE:
                order.insert(0, pid)
            else:
                order.append(pid)
        self._turn_order = order
        self._turn_index = 0

    @property
    def current_speaker(self) -> str | None:
        if self._turn_index < len(self._turn_order):
            return self._turn_order[self._turn_index]
        return None

    def next_speaker(self):
        self._turn_index += 1
        if self._turn_index >= len(self._turn_order):
            self.is_free_exchange = True

    # ── Speech tracking ──

    def can_speak(self, player_id: str) -> bool:
        p = self.players.get(player_id)
        if not p:
            return False
        if not self.is_free_exchange:
            return False
        return p.speech_count < p.speech_limit

    def record_speech(self, player_id: str):
        p = self.players.get(player_id)
        if p:
            p.speech_count += 1

    # ── Question limits ──

    def can_question(self, from_player: str, to_player: str) -> bool:
        p = self.players.get(from_player)
        if not p:
            return False
        count = p.question_count.get(to_player, 0)
        return count < p.question_limit_per_player

    def record_question(self, from_player: str, to_player: str):
        p = self.players.get(from_player)
        if p:
            p.question_count[to_player] = p.question_count.get(to_player, 0) + 1

    # ── Voting ──

    def cast_vote(self, voter_id: str, target_id: str):
        p = self.players.get(voter_id)
        if p:
            p.vote_target = target_id

    def get_vote_result(self) -> dict:
        """Count votes and return result with tie detection."""
        counts: dict[str, int] = {}
        for p in self.players.values():
            if p.vote_target:
                counts[p.vote_target] = counts.get(p.vote_target, 0) + 1

        if not counts:
            return {"winner": None, "is_tie": False, "counts": {}}

        max_votes = max(counts.values())
        winners = [pid for pid, c in counts.items() if c == max_votes]
        is_tie = len(winners) > 1

        return {
            "winner": winners[0] if not is_tie else None,
            "is_tie": is_tie,
            "tied_players": winners if is_tie else None,
            "counts": counts,
        }
