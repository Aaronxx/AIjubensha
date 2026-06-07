"""Dialogue system service."""
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from uuid import uuid4
import json

from ..models.dialogue import (
    DialogueMessage, MessageType, DialogueContext, StructuredNPCOutput,
    DialogueStateUpdate, NPCAutonomousTrigger, SpeechQuota, PrivateChatSession,
    HonestyRule
)
from ..models.character import CharacterType, SilenceStrategy


class DialogueService:
    """Manages NPC dialogue and interactions."""

    def __init__(self):
        # In-memory stores for MVP
        self._messages: dict[str, DialogueMessage] = {}
        self._session_messages: dict[str, List[str]] = {}  # session_id -> message_ids
        self._private_chats: dict[str, PrivateChatSession] = {}
        self._speech_quotas: dict[str, SpeechQuota] = {}  # f"{char_id}_{act}"
        self._fact_ledgers: dict[str, List[Dict]] = {}  # character_id -> facts

    async def build_dialogue_context(
        self,
        character_id: str,
        player_id: str,
        player_message: str,
        session_id: str,
        current_act: str,
        game_state: dict
    ) -> DialogueContext:
        """Build dialogue context for NPC response."""
        from ..services.character_service import character_service

        char_detail = await character_service.get_character_detail(character_id)
        if not char_detail:
            raise ValueError(f"Character {character_id} not found")

        # Get role in script
        script_id = game_state.get("script_id")
        role = char_detail.get("script_assignments", {}).get(script_id, {})

        # Determine honesty mode
        is_murderer = role.get("is_murderer", False)
        lie_topics = role.get("lie_topics", [])

        honesty_mode = "truth"
        for topic in lie_topics:
            if topic.lower() in player_message.lower():
                honesty_mode = "lie"
                break

        # Get recent context (last 10 messages)
        recent_messages = await self._get_recent_messages(session_id, limit=10)

        # Get fact ledger
        fact_ledger = self._fact_ledgers.get(character_id, [])

        # Get attitude to player
        attitude = char_detail.get("personality", {}).get("attitude_to_players", {}).get(player_id, 0.0)

        # Get released knowledge
        knowledge_released = []
        knowledge_hidden = []
        for k in char_detail.get("knowledge", []):
            if k["fact_id"] in [f["fact_id"] for f in fact_ledger if f.get("revealed")]:
                knowledge_released.append(k["fact_id"])
            else:
                knowledge_hidden.append(k["fact_id"])

        return DialogueContext(
            character_id=character_id,
            character_anchor=char_detail.get("character_anchor", ""),
            current_act=current_act,
            arc_state=char_detail.get("current_arc_state", "default"),
            emotional_tag=game_state.get("emotional_tags", {}).get(character_id, "neutral"),
            knowledge_released=knowledge_released,
            knowledge_hidden=knowledge_hidden,
            honesty_mode=honesty_mode,
            lie_topics=lie_topics,
            silence_strategy=char_detail.get("default_silence_strategy", "polite_refusal"),
            recent_context=recent_messages,
            fact_ledger=fact_ledger,
            attitude_to_player=attitude
        )

    def build_npc_prompt(self, context: DialogueContext, player_message: str) -> str:
        """Build system prompt for NPC."""
        silence_desc = {
            "hard_silence": "完全沉默，不作回应",
            "polite_refusal": "委婉拒绝回答",
            "topic_shift": "转移话题",
            "evasion": "顾左右而言他",
            "emotional": "以情绪为由回避"
        }

        honesty_rules = {
            "truth": "必须说真话",
            "lie": "可以在谎言范围内说假话",
            "avoid": "可以使用回避策略"
        }

        system_prompt = f"""【角色锚点】
{context.character_anchor}

【当前状态】
- 当前幕：{context.current_act}
- 角色弧状态：{context.arc_state}
- 情绪状态：{context.emotional_tag}
- 对该玩家的态度：{context.attitude_to_player:.2f} (-1.0到+1.0)

【知识边界】
- 已释放的信息：{context.knowledge_released}
- 保密的信息：{context.knowledge_hidden}
- 本轮话题诚实度规则：{honesty_rules.get(context.honesty_mode, "说真话")}

【对话规则】
- 回避策略：{silence_desc.get(context.silence_strategy, "委婉拒绝")}
- 如果话题需要回避，使用上述策略
- 不要提及你不知道的事实

【近期对话摘要】
{json.dumps(context.recent_context[-5:], ensure_ascii=False, indent=2)}

【回复要求】
1. 以角色的身份和性格回复
2. 回复要符合当前情绪状态
3. 不要OOC（out of character）
4. 回复后输出结构化元数据（JSON格式）
"""

        return system_prompt

    async def call_npc_api(self, system_prompt: str, user_message: str) -> dict:
        """Call DeepSeek API for NPC response."""
        # For MVP, simulate API response
        # In production, this would call DeepSeek-V3 API

        # Simple response simulation
        responses = [
            "我...我需要想想。",
            "这件事我不太清楚。",
            "你为什么问起这个？",
            "也许你应该问问别人。",
            "抱歉，我不太想说。"
        ]

        import random
        reply = random.choice(responses)

        # Return simulated structured output
        return {
            "reply": reply,
            "emotional_tag": "nervous-low",
            "info_revealed": [],
            "attitude_shift": None,
            "arc_state_transition": None
        }

    def parse_npc_response(self, api_response: dict) -> StructuredNPCOutput:
        """Parse API response to structured output."""
        return StructuredNPCOutput(
            reply=api_response.get("reply", "..."),
            emotional_tag=api_response.get("emotional_tag", "neutral"),
            info_revealed=api_response.get("info_revealed", []),
            attitude_shift=api_response.get("attitude_shift"),
            arc_state_transition=api_response.get("arc_state_transition")
        )

    async def update_dialogue_state(
        self,
        session_id: str,
        character_id: str,
        parsed_output: StructuredNPCOutput,
        player_id: str
    ) -> DialogueStateUpdate:
        """Update state after NPC response."""
        # Update fact ledger
        revealed = [info.get("fact_id") for info in parsed_output.info_revealed]

        for fact_id in revealed:
            if character_id not in self._fact_ledgers:
                self._fact_ledgers[character_id] = []

            self._fact_ledgers[character_id].append({
                "fact_id": fact_id,
                "revealed": True,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "to_player": player_id
            })

        # Calculate attitude change
        attitude_changes = {}
        if parsed_output.attitude_shift:
            # Parse attitude shift like "+0.2" or "-0.1"
            try:
                shift = float(parsed_output.attitude_shift)
                attitude_changes[player_id] = shift
            except ValueError:
                pass

        return DialogueStateUpdate(
            character_id=character_id,
            new_emotional_tag=parsed_output.emotional_tag,
            info_released=revealed,
            attitude_changes=attitude_changes,
            arc_transition=parsed_output.arc_state_transition
        )

    async def store_message(
        self,
        session_id: str,
        room_id: str,
        sender_id: str,
        sender_name: str,
        sender_type: MessageType,
        content: str,
        metadata: Optional[Dict] = None
    ) -> DialogueMessage:
        """Store a dialogue message."""
        msg_id = str(uuid4())
        message = DialogueMessage(
            message_id=msg_id,
            session_id=session_id,
            room_id=room_id,
            sender_id=sender_id,
            sender_name=sender_name,
            sender_type=sender_type,
            content=content,
            timestamp=datetime.now(timezone.utc),
            metadata=metadata or {}
        )

        self._messages[msg_id] = message

        if session_id not in self._session_messages:
            self._session_messages[session_id] = []
        self._session_messages[session_id].append(msg_id)

        return message

    async def _get_recent_messages(self, session_id: str, limit: int = 10) -> List[Dict]:
        """Get recent messages for context."""
        if session_id not in self._session_messages:
            return []

        message_ids = self._session_messages[session_id][-limit:]
        messages = [self._messages[mid].dict() for mid in message_ids if mid in self._messages]

        return messages

    async def get_messages_for_session(
        self,
        session_id: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[DialogueMessage]:
        """Get messages for a session."""
        if session_id not in self._session_messages:
            return []

        message_ids = self._session_messages[session_id]
        paginated_ids = message_ids[skip:skip + limit]

        return [self._messages[mid] for mid in paginated_ids if mid in self._messages]

    async def check_autonomous_trigger(
        self,
        session_id: str,
        character_id: str,
        trigger_type: str,
        context: dict
    ) -> Optional[NPCAutonomousTrigger]:
        """Check if NPC should speak autonomously."""
        # Check speech quota
        current_act = context.get("current_act", "act_1")
        quota_key = f"{character_id}_{current_act}"

        quota = self._speech_quotas.get(quota_key)
        if quota and quota.remaining_speeches <= 0:
            return None

        # Determine urgency
        urgency = 1
        if trigger_type == "mentioned":
            urgency = 3
        elif trigger_type == "emotion_threshold":
            urgency = 4
        elif trigger_type == "conflict":
            urgency = 5

        return NPCAutonomousTrigger(
            trigger_type=trigger_type,
            source_message_id=context.get("message_id"),
            target_player_id=context.get("player_id"),
            urgency=urgency
        )

    async def init_speech_quota(self, character_id: str, act: str, max_speeches: int = 5):
        """Initialize speech quota for a character in an act."""
        quota_key = f"{character_id}_{act}"
        self._speech_quotas[quota_key] = SpeechQuota(
            character_id=character_id,
            act=act,
            max_speeches=max_speeches,
            used_speeches=0,
            remaining_speeches=max_speeches
        )

    async def consume_speech_quota(self, character_id: str, act: str):
        """Consume one speech quota."""
        quota_key = f"{character_id}_{act}"
        if quota_key in self._speech_quotas:
            quota = self._speech_quotas[quota_key]
            quota.used_speeches += 1
            quota.remaining_speeches = max(0, quota.max_speeches - quota.used_speeches)

    async def create_private_chat(self, player_id: str, npc_id: str) -> PrivateChatSession:
        """Create a private chat session."""
        session_id = str(uuid4())
        session = PrivateChatSession(
            session_id=session_id,
            player_id=player_id,
            npc_id=npc_id,
            started_at=datetime.now(timezone.utc),
            message_count=0,
            is_active=True
        )
        self._private_chats[session_id] = session
        return session

    async def end_private_chat(self, session_id: str) -> bool:
        """End a private chat session."""
        if session_id in self._private_chats:
            self._private_chats[session_id].is_active = False
            return True
        return False

    async def get_private_chat(self, session_id: str) -> Optional[PrivateChatSession]:
        """Get private chat session."""
        return self._private_chats.get(session_id)


# Singleton instance
dialogue_service = DialogueService()
