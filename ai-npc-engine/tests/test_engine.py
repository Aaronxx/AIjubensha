"""End-to-end test: single NPC multi-round dialogue simulation."""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.engine import NPCsEngine
from src.models import (
    ArcState,
    ArcTransition,
    GamePhase,
    InfoLevel,
    KnowledgeEntry,
    LieTopic,
    NPCDefinition,
    NPCState,
    PersonalityMatrix,
    RelationType,
    Relationship,
    SelfAwareness,
    SilenceStrategy,
)
from src.state_manager import StateManager
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def build_sample_npc() -> NPCDefinition:
    """Build a sample NPC: Su Wanqing (苏晚晴), gallery owner, NOT the killer."""
    knowledge = [
        KnowledgeEntry(
            fact_id="fact_01", level=InfoLevel.L1,
            content="我是这家画廊的老板苏晚晴，已经经营十年了",
            release_condition="asked_directly",
            time_label="现在", location_label="画廊",
        ),
        KnowledgeEntry(
            fact_id="fact_02", level=InfoLevel.L1,
            content="死者生前常来画廊看画",
            release_condition="asked_directly",
            time_label="过去几个月", location_label="画廊",
        ),
        KnowledgeEntry(
            fact_id="fact_03", level=InfoLevel.L2,
            content="死者最后一次来时情绪异常激动",
            release_condition="asked_about_last_visit",
            time_label="上周四", location_label="画廊",
        ),
        KnowledgeEntry(
            fact_id="fact_04", level=InfoLevel.L2,
            content="案发当晚我也在山庄，我约了死者谈画展的事",
            release_condition="asked_about_night",
            time_label="案发当晚", location_label="山庄晚宴",
        ),
        KnowledgeEntry(
            fact_id="fact_05", level=InfoLevel.L3,
            content="我和死者在三年前曾有过一段感情",
            release_condition="trust>=0.3",
            time_label="三年前", location_label="",
        ),
        KnowledgeEntry(
            fact_id="fact_06", level=InfoLevel.L3,
            content="死者的现任妻子曾经威胁过我",
            release_condition="trust>=0.5",
            time_label="最近一个月", location_label="画廊",
        ),
        KnowledgeEntry(
            fact_id="fact_07", level=InfoLevel.L4,
            content="我曾打算在画展后永远离开这座城市，逃离这一切",
            release_condition="trust>=0.7",
            time_label="近期", location_label="",
        ),
    ]

    relationships = [
        Relationship(
            target_id="char_02",
            relation_type=RelationType.NEUTRAL,
            will_cover_for=False,
        ),
        Relationship(
            target_id="char_03",
            relation_type=RelationType.COMRADE,
            will_cover_for=True,
            will_lie_for=False,
        ),
    ]

    arc_states = [
        ArcState(
            name="distant_polite",
            description="疏离客气",
            dialogue_style="温和礼貌但保持距离感，用词文雅。回答简短，不主动展开话题。",
            attitude_modifier=0.0,
            allowed_info_levels=[InfoLevel.L1],
            available_silence_strategies=[SilenceStrategy.POLITE_REFUSAL],
            emotional_baseline="平静",
        ),
        ArcState(
            name="slightly_interested",
            description="稍显兴趣，愿意多聊几句",
            dialogue_style="语气仍然温和但多了一些温度。可以多透露一些信息。会在回答后反问玩家。",
            attitude_modifier=0.2,
            allowed_info_levels=[InfoLevel.L1, InfoLevel.L2],
            available_silence_strategies=[SilenceStrategy.DEFLECT],
            emotional_baseline="平静",
        ),
        ArcState(
            name="defensive_tense",
            description="防御紧绷，感到被质疑",
            dialogue_style="明显紧张，回答变得谨慎。用沉默或转移话题回避敏感问题。",
            attitude_modifier=-0.3,
            allowed_info_levels=[InfoLevel.L1, InfoLevel.L2, InfoLevel.L3],
            available_silence_strategies=[SilenceStrategy.CHANGE_SUBJECT, SilenceStrategy.EMOTIONAL_AVOIDANCE],
            emotional_baseline="紧张-低",
        ),
        ArcState(
            name="breakdown_honest",
            description="防线崩溃，愿意坦诚相待",
            dialogue_style="不再回避，用轻而颤抖的声音说出真相。对真诚的人敞开心扉。",
            attitude_modifier=0.5,
            allowed_info_levels=[InfoLevel.L1, InfoLevel.L2, InfoLevel.L3, InfoLevel.L4],
            available_silence_strategies=[],
            emotional_baseline="悲伤-中",
        ),
    ]

    arc_transitions = [
        # Forward positive
        ArcTransition("distant_polite", "slightly_interested", "attitude>=0.15"),
        ArcTransition("slightly_interested", "breakdown_honest", "attitude>=0.5 AND emotion_contains=悲伤"),
        ArcTransition("slightly_interested", "breakdown_honest", "attitude>=0.7"),
        ArcTransition("slightly_interested", "breakdown_honest", "attitude>=0.5 AND emotion_contains=懊悔"),
        # Forward negative
        ArcTransition("slightly_interested", "defensive_tense", "attitude<=-0.2"),
        ArcTransition("distant_polite", "defensive_tense", "attitude<=-0.3"),
        ArcTransition("distant_polite", "defensive_tense", "emotion_contains=紧张"),
        # Forward from defensive to breakdown
        ArcTransition("defensive_tense", "breakdown_honest", "attitude>=0.4"),
        ArcTransition("defensive_tense", "breakdown_honest", "emotion_contains=悲伤-中"),
        ArcTransition("defensive_tense", "breakdown_honest", "emotion_contains=悲伤-高"),
        ArcTransition("defensive_tense", "breakdown_honest", "emotion_contains=哀恸"),
        # Reverse (recovery) — requires more effort
        # defensive → interested: needs +0.3 (vs original +0.15), harder to regain
        ArcTransition("defensive_tense", "slightly_interested", "attitude>=0.3"),
        # defensive → polite: needs +0.5, takes real work to fully repair
        ArcTransition("defensive_tense", "distant_polite", "attitude>=0.5"),
        # breakdown → interested: can recover with trust
        ArcTransition("breakdown_honest", "slightly_interested", "attitude>=0.3"),
    ]

    return NPCDefinition(
        npc_id="char_01",
        name="苏晚晴",
        age=30,
        occupation="画廊老板",
        character_anchor=(
            "你叫苏晚晴，30岁，画廊老板。"
            "说话风格：温和礼貌但保持距离，用词文雅，不使用网络俚语。"
            "情绪表达：克制，不轻易表露真实想法，紧张时反而更安静。"
            "对待他人：观察多于表达，对真诚的人会稍放下心防。"
            "底线：绝不主动伤害任何人，对艺术有偏执的真诚。"
            "在压力下：不是崩溃，而是沉默很久后用更轻的声音说话。"
        ),
        personality=PersonalityMatrix(
            extroversion=0.3,
            aggression=0.1,
            honesty_tendency=0.8,
            rationality=0.7,
            speech_style="文雅克制，不疾不徐",
        ),
        self_awareness=SelfAwareness.NEVER_KNOWS,
        is_killer=False,
        knowledge=knowledge,
        relationships=relationships,
        default_silence_strategy=SilenceStrategy.POLITE_REFUSAL,
        silence_triggers=["涉及char_03的话题"],
        arc_states=arc_states,
        arc_transitions=arc_transitions,
        initial_arc_state="distant_polite",
    )


def print_npc_state(npc_def: NPCDefinition, npc_state: NPCState):
    table = Table(title=f"{npc_def.name} — NPC 状态快照")
    table.add_column("属性", style="cyan")
    table.add_column("值", style="green")
    table.add_row("角色弧状态", npc_state.current_arc_state)
    table.add_row("情绪标签", npc_state.emotional_tag)
    table.add_row("对玩家态度", f"{npc_state.attitude_to_player:+.2f}")
    table.add_row("已公开信息数", str(len(npc_state.get_released_knowledge())))
    table.add_row("未公开信息数", str(len(npc_state.get_unreleased_knowledge())))
    table.add_row("事实账本记录数", str(len(npc_state.fact_ledger)))
    console.print(table)


async def run_dialogue_simulation():
    console.print(Panel.fit(
        "[bold yellow]AI NPC 对话引擎 — 原型测试[/bold yellow]\n"
        "模拟玩家与 NPC 苏晚晴的多轮对话",
        border_style="yellow",
    ))

    # Setup
    npc_def = build_sample_npc()
    state_mgr = StateManager()
    npc_state = state_mgr.init_npc_state(npc_def)
    engine = NPCsEngine()

    # Conversation history
    messages: list[dict] = []

    # Test rounds
    test_rounds = [
        {
            "phase": GamePhase.ACT_1,
            "message": "你好，请问你是？",
            "description": "第一幕：初次见面，询问身份",
        },
        {
            "phase": GamePhase.ACT_1,
            "message": "听说死者生前常来你的画廊？",
            "description": "第一幕：聊到死者的话题",
        },
        {
            "phase": GamePhase.ACT_2_DISCUSS,
            "message": "苏女士，你最后一次见到他是什么时候？他当时状态如何？",
            "description": "第二幕：尸体已发现，深入询问",
        },
        {
            "phase": GamePhase.ACT_2_DISCUSS,
            "message": "那天晚上你在山庄做什么？",
            "description": "第二幕：质询她的行踪",
        },
        {
            "phase": GamePhase.ACT_3_DISCUSS,
            "message": "苏女士，你和死者之间是不是不止画商和客户的关系？",
            "description": "第三幕：直接追问隐藏关系",
        },
        {
            "phase": GamePhase.ACT_3_DISCUSS,
            "message": "我知道他妻子威胁过你。你没必要独自承受这些。",
            "description": "第三幕：展现理解和共情",
        },
    ]

    total_tokens = 0
    total_latency = 0.0

    for i, test_round in enumerate(test_rounds):
        console.print(f"\n[bold]━━━ 第 {i + 1} 轮 ━━━[/bold]")
        console.print(f"[dim]场景：{test_round['description']}[/dim]")
        console.print(f"[bold blue]玩家：[/bold blue]{test_round['message']}")

        reply = await engine.process_player_message(
            npc_def=npc_def,
            npc_state=npc_state,
            player_id="user_001",
            player_message=test_round["message"],
            phase=test_round["phase"],
            recent_messages=messages,
            topic_in_lie_range=False,
        )

        # Record the exchange
        messages.append({"speaker": "玩家", "text": test_round["message"]})
        messages.append({"speaker": npc_def.name, "text": reply.reply_text})

        total_tokens += reply.tokens_used
        total_latency += reply.latency_ms

        # Display reply
        console.print(f"[bold green]{npc_def.name}：[/bold green]{reply.reply_text}")
        console.print(
            f"[dim]情绪：{reply.emotional_tag}"
            f" | 态度：{npc_state.attitude_to_player:+.2f}"
            f" | 弧状态：{npc_state.current_arc_state}"
            f" | 延迟：{reply.latency_ms:.0f}ms"
            f" | tokens：{reply.tokens_used}[/dim]"
        )
        if reply.info_revealed:
            console.print(f"[yellow]→ 透露了信息：{reply.info_revealed}[/yellow]")

    # Final summary
    console.print("\n")
    console.print(Panel.fit("[bold]测试完成 — 状态总结[/bold]", border_style="green"))
    print_npc_state(npc_def, npc_state)

    console.print(f"\n[bold]统计：[/bold]")
    console.print(f"  总轮数：{len(test_rounds)}")
    console.print(f"  总 tokens：{total_tokens}")
    console.print(f"  总延迟：{total_latency:.0f}ms")
    console.print(f"  平均延迟：{total_latency / len(test_rounds):.0f}ms/轮")

    # Print fact ledger
    console.print(f"\n[bold]事实账本：[/bold]")
    for entry in npc_state.fact_ledger:
        console.print(f"  [dim]- {entry}[/dim]")


if __name__ == "__main__":
    asyncio.run(run_dialogue_simulation())
