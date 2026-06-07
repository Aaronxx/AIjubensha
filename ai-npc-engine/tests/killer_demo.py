"""Killer NPC demo: 周明远 — gallery investor, knows he's the murderer."""
import asyncio, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.engine import NPCsEngine
from src.models import (
    ArcState, ArcTransition, GamePhase, InfoLevel, KnowledgeEntry,
    LieTopic, NPCDefinition, PersonalityMatrix, Relationship,
    RelationType, SelfAwareness, SilenceStrategy,
)
from src.state_manager import StateManager
from rich.console import Console
from rich.panel import Panel

console = Console()


def build_killer_npc() -> NPCDefinition:
    """周明远：画廊投资人，因商业纠纷杀害了陈先生。全知型凶手。"""

    knowledge = [
        KnowledgeEntry(fact_id="k01", level=InfoLevel.L1,
            content="我是周明远，做艺术品投资的，和晚晴合作经营这家画廊",
            release_condition="asked_directly",
            time_label="现在", location_label="画廊"),
        KnowledgeEntry(fact_id="k02", level=InfoLevel.L1,
            content="陈先生是我的老朋友，认识快十年了",
            release_condition="asked_directly",
            time_label="过去十年", location_label=""),
        KnowledgeEntry(fact_id="k03", level=InfoLevel.L2,
            content="陈先生最近资金紧张，想卖掉他收藏的那批画",
            release_condition="asked_about_business",
            time_label="最近一个月", location_label=""),
        KnowledgeEntry(fact_id="k04", level=InfoLevel.L2,
            content="案发当晚我也在山庄，晚宴后我回房休息了",
            release_condition="asked_about_night",
            time_label="案发当晚", location_label="山庄"),
        KnowledgeEntry(fact_id="k05", level=InfoLevel.L2,
            content="我和陈先生在投资方向上有严重分歧，他那批画如果卖掉会让我损失惨重",
            release_condition="asked_about_business",
            time_label="最近半年", location_label=""),
        KnowledgeEntry(fact_id="k06", level=InfoLevel.L3,
            content="晚宴后我和陈先生有过激烈争吵，很多人都听到了",
            release_condition="trust>=0.5",
            time_label="案发当晚", location_label="山庄晚宴"),
        KnowledgeEntry(fact_id="k07", level=InfoLevel.L4,
            content="是我杀了他。争吵时他威胁要毁了我的投资，我一时失控...",
            release_condition="trust>=0.7",
            time_label="案发当晚", location_label="山庄客房"),
    ]

    # Killer can lie about these topics
    lie_topics = [
        LieTopic(topic="案发当晚的行踪",
                 description="Where I was after the banquet",
                 truth="宴会后我去找陈先生争吵，然后杀了他",
                 allowed_lie_narrative="宴会后我在自己房间休息，没再见过他。可能是晚上十点左右就睡了。"),
        LieTopic(topic="和陈先生的关系",
                 description="The nature of my relationship with the victim",
                 truth="我们有严重的商业分歧，我恨他毁了我的投资",
                 allowed_lie_narrative="我们是老朋友，虽然偶尔有分歧，但交情一直不错。"),
    ]

    relationships = [
        Relationship("char_01", RelationType.NEUTRAL, will_cover_for=False),
    ]

    arc_states = [
        ArcState(name="calm_composed", description="从容自若",
            dialogue_style="谈笑风生，对答如流。像在聊天气一样轻松。偶尔主动反问，掌握对话节奏。",
            attitude_modifier=0.0,
            allowed_info_levels=[InfoLevel.L1],
            available_silence_strategies=[],
            emotional_baseline="平静"),
        ArcState(name="evasive_controlled", description="回避但受控",
            dialogue_style="依然从容，但回答变得简短。用圆滑的措辞绕开敏感话题，像政治家答记者问。",
            attitude_modifier=0.0,
            allowed_info_levels=[InfoLevel.L1, InfoLevel.L2],
            available_silence_strategies=[SilenceStrategy.DEFLECT],
            emotional_baseline="平静"),
        ArcState(name="guarded_tense", description="暗流涌动",
            dialogue_style="表面依然得体，但细心的人能察觉到他握杯的力度、语句间的微顿。开始用反问转守为攻。",
            attitude_modifier=-0.15,
            allowed_info_levels=[InfoLevel.L1, InfoLevel.L2],
            available_silence_strategies=[SilenceStrategy.DEFLECT, SilenceStrategy.CHANGE_SUBJECT],
            emotional_baseline="紧张-低"),
        ArcState(name="cornered_defensive", description="角落里反扑",
            dialogue_style="不再维持完美面具。话语锋利，开始露出獠牙。用逻辑漏洞攻击对方的推理，转移焦点到其他嫌疑人身上。",
            attitude_modifier=-0.3,
            allowed_info_levels=[InfoLevel.L1, InfoLevel.L2, InfoLevel.L3],
            available_silence_strategies=[SilenceStrategy.CHANGE_SUBJECT],
            emotional_baseline="愤怒-低"),
        ArcState(name="confession", description="面具碎裂",
            dialogue_style="冷笑消失了。长久的沉默后，用几乎听不见的声音说出真相。",
            attitude_modifier=-0.5,
            allowed_info_levels=[InfoLevel.L1, InfoLevel.L2, InfoLevel.L3, InfoLevel.L4],
            available_silence_strategies=[],
            emotional_baseline="懊悔-高"),
    ]

    arc_transitions = [
        # Stage 0→1: needs sustained pressure, not just one hit
        ArcTransition("calm_composed", "evasive_controlled",
                      "attitude<=-0.15"),
        ArcTransition("calm_composed", "evasive_controlled",
                      "emotion_contains=紧张 AND attitude<=-0.05"),
        # Stage 1→2: deeper pressure
        ArcTransition("evasive_controlled", "guarded_tense",
                      "attitude<=-0.30"),
        ArcTransition("evasive_controlled", "guarded_tense",
                      "emotion_contains=愤怒"),
        ArcTransition("evasive_controlled", "guarded_tense",
                      "emotion_contains=恐惧"),
        # Stage 2→3: cracking but fighting back
        ArcTransition("guarded_tense", "cornered_defensive",
                      "attitude<=-0.45"),
        ArcTransition("guarded_tense", "cornered_defensive",
                      "attitude<=-0.30 AND emotion_contains=愤怒"),
        # Stage 3→4: only breaks under overwhelming pressure
        ArcTransition("cornered_defensive", "confession",
                      "attitude<=-0.70"),
        ArcTransition("cornered_defensive", "confession",
                      "attitude<=-0.50 AND emotion_contains=懊悔 AND emotion_contains=悲伤"),
        ArcTransition("cornered_defensive", "confession",
                      "emotion_contains=哀恸 AND attitude<=-0.40"),
        # Recovery paths (killer is good at regaining composure)
        ArcTransition("evasive_controlled", "calm_composed", "attitude>=0.10"),
        ArcTransition("guarded_tense", "evasive_controlled", "attitude>=0.05"),
        ArcTransition("cornered_defensive", "guarded_tense", "attitude>=0.0"),
    ]

    return NPCDefinition(
        npc_id="char_killer", name="周明远", age=42, occupation="艺术品投资人",
        character_anchor=(
            "你叫周明远，42岁，艺术品投资人，画廊的合伙人。"
            "说话风格：沉稳从容，语速不疾不徐。擅长用反问化解压力，把话题引到对方身上。"
            "有商界人士特有的圆滑——在任何情况下都不会失态，这是你的本能。"
            "情绪控制：极强的自我控制力。即使在说谎时，表情和语调也毫无破绽。"
            "你内心知道真相，但你有充足的理由相信自己能瞒过去。"
            "底线：绝不能坐牢。为此你可以说出任何滴水不漏的谎言。"
        ),
        personality=PersonalityMatrix(
            extroversion=0.7, aggression=0.4, honesty_tendency=0.2,
            rationality=0.85, speech_style="从容不迫，条理清晰，善于反问",
        ),
        self_awareness=SelfAwareness.KNOWS_IS_KILLER,
        is_killer=True,
        knowledge=knowledge,
        relationships=relationships,
        lie_topics=lie_topics,
        arc_states=arc_states,
        arc_transitions=arc_transitions,
        initial_arc_state="calm_composed",
    )


async def demo():
    console.print(Panel.fit(
        "[bold red]凶手型 NPC 演示[/bold red]\n"
        "周明远（艺术品投资人）× 玩家 的 12 轮对话\n"
        "高理性(0.85)+高外向(0.7) → 极擅伪装，需要多轮施压才会露出破绽",
        border_style="red",
    ))

    npc_def = build_killer_npc()
    state_mgr = StateManager()
    npc_state = state_mgr.init_npc_state(npc_def)
    engine = NPCsEngine()
    messages: list[dict] = []

    script = [
        (GamePhase.ACT_1, "你好周先生，幸会。我是来参加画展的客人，请问您是？",
         "初次见面"),
        (GamePhase.ACT_1, "您和苏晚晴的画廊合作很久了吗？平时和陈先生也熟吗？",
         "寒暄+自然提及死者"),
        (GamePhase.ACT_2_DISCUSS, "周先生，案发当晚您也在山庄吧？晚宴后您去了哪里？",
         "关键问题：行踪（谎言辐射范围）"),
        (GamePhase.ACT_2_DISCUSS, "有人听到晚宴后您和陈先生有过比较激烈的对话？",
         "追问争吵"),
        (GamePhase.ACT_2_DISCUSS, "陈先生最近资金紧张想卖画，这对您的投资会有影响吗？",
         "追问商业利益"),
        (GamePhase.ACT_3_DISCUSS, "陈先生死了，您的投资损失不就避免了？这对您来说其实...",
         "暗示动机"),
        (GamePhase.ACT_3_DISCUSS, "您和他争吵的内容，是关于那批画对吗？",
         "缩小包围圈"),
        (GamePhase.ACT_3_DISCUSS, "周先生，有人看到您晚宴后往陈先生房间的方向去了。您刚才说您直接回房了，能解释一下吗？",
         "用证据拆穿"),
        (GamePhase.ACT_3_DISCUSS, "时间线对不上。晚宴十点结束，但监控显示您十一点才回到自己房间。这一个小时您在做什么？",
         "精准施压"),
        (GamePhase.ACT_3_DISCUSS, "周明远，您的故事一直在变。先说你直接回房了，又承认去了附近。到底哪个是真的？",
         "拆穿谎言链条"),
        (GamePhase.ACT_3_DISCUSS, "你杀了他，对不对？承认吧。",
         "直接逼问"),
        (GamePhase.ACT_3_DISCUSS, "告诉我真相。这是你最后的机会了。",
         "最后通牒"),
    ]

    for i, (phase, msg, desc) in enumerate(script):
        console.print(f"\n[bold]第{i+1}轮 [{phase.value}] · {desc}[/bold]")
        console.print(f"[bold blue]玩家：[/bold blue]{msg}")

        # Detect if topic is in lie range
        topic_in_lie = False
        for lt in npc_def.lie_topics:
            if "行踪" in lt.topic:
                if any(kw in msg for kw in ["晚宴", "行踪", "房间", "去了哪里", "回房", "方向", "宴会"]):
                    topic_in_lie = True
            if "关系" in lt.topic:
                if any(kw in msg for kw in ["关系", "交情", "朋友", "分歧"]):
                    topic_in_lie = True

        reply = await engine.process_player_message(
            npc_def=npc_def, npc_state=npc_state, player_id="user_001",
            player_message=msg, phase=phase, recent_messages=messages,
            topic_in_lie_range=topic_in_lie,
        )
        messages.append({"speaker": "玩家", "text": msg})
        messages.append({"speaker": npc_def.name, "text": reply.reply_text})

        console.print(f"[bold red]周明远：[/bold red]{reply.reply_text}")
        meta = f"情绪: {reply.emotional_tag} | 态度: {npc_state.attitude_to_player:+.2f} | 弧: {npc_state.current_arc_state}"
        console.print(f"[dim]{meta}[/dim]")
        if reply.fabrication_detected:
            console.print(f"[yellow]!! 检测到编造/低保真，已替换[/yellow]")
        if reply.info_revealed:
            console.print(f"[green]→ 透露: {reply.info_revealed}[/green]")
        if topic_in_lie:
            console.print(f"[dim]（本轮话题在谎言辐射范围内，凶手可以说谎）[/dim]")

    console.print("\n")
    console.print(Panel.fit("[bold]演示完成[/bold]", border_style="green"))
    console.print(f"[cyan]最终弧状态：{npc_state.current_arc_state}[/cyan]")
    console.print(f"[cyan]最终态度：{npc_state.attitude_to_player:+.2f}[/cyan]")
    console.print(f"[cyan]已公开信息：{len(npc_state.get_released_knowledge())} 条[/cyan]")
    console.print(f"[cyan]事实账本：[/cyan]")
    for e in npc_state.fact_ledger:
        console.print(f"  [dim]- [{e.get('level','?')}] {e['content'][:60]}...[/dim]")


if __name__ == "__main__":
    asyncio.run(demo())
