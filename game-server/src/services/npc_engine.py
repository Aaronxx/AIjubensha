"""AI NPC dialogue engine using DeepSeek API."""
import os
from typing import Optional
import httpx
from dataclasses import dataclass

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"


@dataclass
class NPCContext:
    """NPC conversation context."""
    character_name: str
    character_anchor: str  # 性格锚点
    current_act: str
    arc_state: str
    emotional_tag: str
    knowledge_released: list[str]
    knowledge_hidden: list[str]
    is_killer: bool = False
    lie_topics: list[str] = None


class NPCDialogueEngine:
    """Generates NPC responses using DeepSeek API."""

    def __init__(self):
        self.api_key = DEEPSEEK_API_KEY
        self.api_url = DEEPSEEK_API_URL

    def _build_system_prompt(self, ctx: NPCContext) -> str:
        """Build system prompt for NPC personality."""
        honesty_rule = """
规则：
- 如果话题涉及核心秘密(L3-L4)，选择沉默或回避
- 如果是凶手且话题在谎言范围内，可以撒谎
- 否则必须说真话或保持沉默
"""

        return f"""【角色设定】
{ctx.character_anchor}

【当前状态】
- 当前幕：{ctx.current_act}
- 角色状态：{ctx.arc_state}
- 情绪状态：{ctx.emotional_tag}

【知识边界】
- 已公开信息：{', '.join(ctx.knowledge_released) if ctx.knowledge_released else '无'}
- 隐藏信息：{', '.join(ctx.knowledge_hidden[:3]) + '...' if len(ctx.knowledge_hidden) > 3 else ', '.join(ctx.knowledge_hidden) if ctx.knowledge_hidden else '无'}

{honesty_rule if ctx.is_killer else '- 非凶手角色：必须说真话或保持沉默'}

【回复要求】
- 以角色身份和性格回复
- 不提及你不知道的事实
- 保持情绪一致性
"""

    async def generate_response(
        self,
        ctx: NPCContext,
        player_message: str,
        conversation_history: Optional[list[dict]] = None,
    ) -> dict:
        """Generate NPC response using DeepSeek API."""
        if not self.api_key:
            # Fallback response when API key not available
            return {
                "reply": f"[{ctx.character_name}] 我是{ctx.character_name}，{ctx.emotional_tag}。",
                "emotional_tag": ctx.emotional_tag,
                "info_revealed": [],
                "attitude_shift": None,
            }

        system_prompt = self._build_system_prompt(ctx)

        messages = [{"role": "system", "content": system_prompt}]

        if conversation_history:
            messages.extend(conversation_history)

        messages.append({"role": "user", "content": player_message})

        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.post(
                    self.api_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "deepseek-chat",
                        "messages": messages,
                        "temperature": 0.7,
                        "max_tokens": 300,
                    },
                )
                response.raise_for_status()
                data = response.json()

                reply = data["choices"][0]["message"]["content"]

                # Parse response (in production, would use structured output)
                return {
                    "reply": reply,
                    "emotional_tag": ctx.emotional_tag,
                    "info_revealed": [],  # Would be extracted from response
                    "attitude_shift": None,
                }

            except httpx.HTTPError as e:
                return {
                    "reply": f"[{ctx.character_name}] （陷入沉默）",
                    "emotional_tag": ctx.emotional_tag,
                    "info_revealed": [],
                    "error": str(e),
                }


# Singleton
npc_engine = NPCDialogueEngine()
