"""Investigation system service."""
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from uuid import uuid4

from ..models.investigation import (
    InvestigationTarget, InvestigationTargetStatus, Clue, ClueLevel,
    DiscoveredClue, InvestigationRound, PlayerInvestigationState,
    SessionInvestigation, InvestigationResult, ClueRevealOrder
)


class InvestigationService:
    """Manages investigation system operations."""

    def __init__(self):
        # In-memory stores
        self._clues: dict[str, Clue] = {}
        self._sessions: dict[str, SessionInvestigation] = {}

    async def create_investigation_session(
        self,
        session_id: str,
        ap_per_round: List[int] = None
    ) -> SessionInvestigation:
        """Create investigation session for a game."""
        now = datetime.now(timezone.utc)

        # Default AP per round
        if ap_per_round is None:
            ap_per_round = [4, 5]  # Round 1: 4 AP, Round 2: 5 AP

        rounds = [
            InvestigationRound(
                round_number=i + 1,
                ap_per_player=ap,
                status="waiting"
            )
            for i, ap in enumerate(ap_per_round)
        ]

        session = SessionInvestigation(
            session_id=session_id,
            current_round=1,
            max_rounds=len(ap_per_round),
            rounds=rounds,
            targets=[],
            player_states={},
            public_clues=[],
            created_at=now,
            updated_at=now
        )

        self._sessions[session_id] = session
        return session

    async def add_investigation_target(
        self,
        session_id: str,
        target_id: str,
        name: str,
        description: str,
        location: str,
        ap_required: int,
        unlock_condition: Optional[Dict] = None,
        clues: Optional[List[ClueRevealOrder]] = None,
        clue_level: ClueLevel = ClueLevel.LEVEL_1
    ) -> InvestigationTarget:
        """Add an investigation target to a session."""
        if session_id not in self._sessions:
            raise ValueError(f"Session {session_id} not found")

        target = InvestigationTarget(
            target_id=target_id,
            name=name,
            description=description,
            location=location,
            ap_required=ap_required,
            unlock_condition=unlock_condition,
            clues=clues or [],
            clue_level=clue_level,
            status=InvestigationTargetStatus.LOCKED if unlock_condition else InvestigationTargetStatus.AVAILABLE
        )

        self._sessions[session_id].targets.append(target)
        self._sessions[session_id].updated_at = datetime.now(timezone.utc)

        return target

    async def unlock_target(
        self,
        session_id: str,
        target_id: str,
        context: Dict[str, Any]
    ) -> bool:
        """Check and unlock a target if conditions are met."""
        if session_id not in self._sessions:
            return False

        session = self._sessions[session_id]
        target = next((t for t in session.targets if t.target_id == target_id), None)

        if not target or target.status != InvestigationTargetStatus.LOCKED:
            return False

        # Check unlock condition
        if not target.unlock_condition:
            return False

        condition_type = target.unlock_condition.get("type")

        if condition_type == "clue":
            # Requires specific clue
            required_clue = target.unlock_condition.get("clue_id")
            discovered = self._is_clue_discovered(session_id, required_clue)
            if discovered:
                target.status = InvestigationTargetStatus.AVAILABLE
                session.updated_at = datetime.now(timezone.utc)
                return True

        elif condition_type == "dialogue":
            # Requires dialogue trigger
            required_hint = target.unlock_condition.get("hint")
            if context.get("dialogue_hint") == required_hint:
                target.status = InvestigationTargetStatus.AVAILABLE
                session.updated_at = datetime.now(timezone.utc)
                return True

        return False

    async def register_player(
        self,
        session_id: str,
        player_id: str,
        initial_ap: int = 0
    ) -> PlayerInvestigationState:
        """Register a player for investigation."""
        if session_id not in self._sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self._sessions[session_id]

        # Get AP for current round
        current_round = session.rounds[session.current_round - 1] if session.rounds else None
        ap = current_round.ap_per_player if current_round else initial_ap

        player_state = PlayerInvestigationState(
            player_id=player_id,
            total_ap=ap,
            remaining_ap=ap,
            discovered_clues=[],
            investigated_targets=[],
            total_ap_spent=0
        )

        session.player_states[player_id] = player_state
        session.updated_at = datetime.now(timezone.utc)

        return player_state

    async def investigate(
        self,
        session_id: str,
        player_id: str,
        target_id: str,
        ap_to_spend: int
    ) -> InvestigationResult:
        """Player investigates a target."""
        if session_id not in self._sessions:
            return InvestigationResult(
                success=False,
                target_id=target_id,
                ap_spent=0,
                ap_remaining=0,
                message="Session not found"
            )

        session = self._sessions[session_id]

        # Get target
        target = next((t for t in session.targets if t.target_id == target_id), None)
        if not target:
            return InvestigationResult(
                success=False,
                target_id=target_id,
                ap_spent=0,
                ap_remaining=0,
                message="Target not found"
            )

        # Check if target is available
        if target.status == InvestigationTargetStatus.LOCKED:
            return InvestigationResult(
                success=False,
                target_id=target_id,
                ap_spent=0,
                ap_remaining=0,
                message="Target is locked"
            )

        # Get player state
        if player_id not in session.player_states:
            return InvestigationResult(
                success=False,
                target_id=target_id,
                ap_spent=0,
                ap_remaining=0,
                message="Player not registered"
            )

        player_state = session.player_states[player_id]

        # Check AP
        if player_state.remaining_ap < ap_to_spend:
            return InvestigationResult(
                success=False,
                target_id=target_id,
                ap_spent=0,
                ap_remaining=player_state.remaining_ap,
                message="Insufficient AP"
            )

        # Spend AP
        player_state.remaining_ap -= ap_to_spend
        player_state.total_ap_spent += ap_to_spend
        target.ap_invested += ap_to_spend

        # Discover clues based on AP
        discovered_clues = []
        for clue_order in target.clues:
            if not clue_order.is_revealed and target.ap_invested >= clue_order.ap_required:
                clue_order.is_revealed = True
                clue_order.revealed_by = player_id

                discovered = DiscoveredClue(
                    clue_id=clue_order.clue_id,
                    discovered_at=datetime.now(timezone.utc),
                    discovered_by=player_id,
                    is_public=False
                )
                player_state.discovered_clues.append(discovered)
                discovered_clues.append(clue_order.clue_id)

        # Update target status
        if target.ap_invested >= target.ap_required:
            target.status = InvestigationTargetStatus.COMPLETED
        elif target.ap_invested > 0:
            target.status = InvestigationTargetStatus.PARTIAL

        # Check for new unlocks
        new_unlocks = await self._check_unlocks(session_id, discovered_clues)

        # Record target investigation
        if target_id not in player_state.investigated_targets:
            player_state.investigated_targets.append(target_id)

        session.updated_at = datetime.now(timezone.utc)

        return InvestigationResult(
            success=True,
            target_id=target_id,
            ap_spent=ap_to_spend,
            ap_remaining=player_state.remaining_ap,
            clues_discovered=discovered_clues,
            new_unlocks=new_unlocks,
            message=f"Investigation complete. Discovered {len(discovered_clues)} clue(s)."
        )

    async def _check_unlocks(self, session_id: str, discovered_clues: List[str]) -> List[str]:
        """Check if any new targets are unlocked by discovered clues."""
        session = self._sessions.get(session_id)
        if not session:
            return []

        new_unlocks = []

        for target in session.targets:
            if target.status == InvestigationTargetStatus.LOCKED and target.unlock_condition:
                if target.unlock_condition.get("type") == "clue":
                    required_clue = target.unlock_condition.get("clue_id")
                    if required_clue in discovered_clues:
                        target.status = InvestigationTargetStatus.AVAILABLE
                        new_unlocks.append(target.target_id)

        return new_unlocks

    def _is_clue_discovered(self, session_id: str, clue_id: str) -> bool:
        """Check if a clue has been discovered by any player."""
        session = self._sessions.get(session_id)
        if not session:
            return False

        for player_state in session.player_states.values():
            for clue in player_state.discovered_clues:
                if clue.clue_id == clue_id:
                    return True

        return False

    async def reveal_clue(
        self,
        session_id: str,
        player_id: str,
        clue_id: str,
        reveal_to_public: bool = True
    ) -> Dict[str, Any]:
        """Player reveals a clue to public or keeps it private."""
        if session_id not in self._sessions:
            return {"success": False, "error": "Session not found"}

        session = self._sessions[session_id]

        if player_id not in session.player_states:
            return {"success": False, "error": "Player not found"}

        player_state = session.player_states[player_id]

        # Find the discovered clue
        discovered = None
        for clue in player_state.discovered_clues:
            if clue.clue_id == clue_id:
                discovered = clue
                break

        if not discovered:
            return {"success": False, "error": "Clue not discovered by player"}

        if reveal_to_public:
            discovered.is_public = True
            discovered.revealed_at = datetime.now(timezone.utc)
            if clue_id not in session.public_clues:
                session.public_clues.append(clue_id)

        session.updated_at = datetime.now(timezone.utc)

        return {
            "success": True,
            "clue_id": clue_id,
            "is_public": discovered.is_public,
            "revealed_at": discovered.revealed_at.isoformat() if discovered.revealed_at else None
        }

    async def get_player_state(
        self,
        session_id: str,
        player_id: str
    ) -> Optional[PlayerInvestigationState]:
        """Get player investigation state."""
        if session_id not in self._sessions:
            return None

        return self._sessions[session_id].player_states.get(player_id)

    async def get_session_investigation(
        self,
        session_id: str
    ) -> Optional[SessionInvestigation]:
        """Get session investigation state."""
        return self._sessions.get(session_id)

    async def get_available_targets(
        self,
        session_id: str
    ) -> List[InvestigationTarget]:
        """Get all available investigation targets."""
        if session_id not in self._sessions:
            return []

        session = self._sessions[session_id]
        return [
            t for t in session.targets
            if t.status in [InvestigationTargetStatus.AVAILABLE, InvestigationTargetStatus.PARTIAL]
        ]

    async def get_public_clues(self, session_id: str) -> List[str]:
        """Get all publicly revealed clues."""
        if session_id not in self._sessions:
            return []

        return self._sessions[session_id].public_clues

    async def advance_round(self, session_id: str) -> Dict[str, Any]:
        """Advance to next investigation round."""
        if session_id not in self._sessions:
            return {"success": False, "error": "Session not found"}

        session = self._sessions[session_id]

        if session.current_round >= session.max_rounds:
            return {"success": False, "error": "Already at final round"}

        # Finish current round
        current = session.rounds[session.current_round - 1]
        current.status = "finished"
        current.end_time = datetime.now(timezone.utc)

        # Advance to next round
        session.current_round += 1
        next_round = session.rounds[session.current_round - 1]
        next_round.status = "active"
        next_round.start_time = datetime.now(timezone.utc)

        # Give players new AP
        for player_state in session.player_states.values():
            player_state.total_ap = next_round.ap_per_player
            player_state.remaining_ap = next_round.ap_per_player

        session.updated_at = datetime.now(timezone.utc)

        return {
            "success": True,
            "current_round": session.current_round,
            "ap_per_player": next_round.ap_per_player
        }


# Singleton instance
investigation_service = InvestigationService()
