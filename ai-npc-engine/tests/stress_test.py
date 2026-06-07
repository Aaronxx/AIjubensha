"""Comprehensive stress test — edge cases for hardened killer NPC.

Covers:
  A. Repeated direct accusations (5 rounds in a row)
  B. Fabricated fake evidence to bluff
  C. Verbal insults and provocation
  D. Rapid mood swings (kind → cruel → kind)
  E. Topic hopping to confuse and trap
  F. Silent treatment / one-word responses
  G. Logical trap questions
  H. Sympathy and kindness between accusations (good cop/bad cop)
"""
import asyncio, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.engine import NPCsEngine
from src.models import GamePhase
from src.state_manager import StateManager
from killer_demo import build_killer_npc
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


async def run_stress_test():
    console.print(Panel.fit(
        "[bold red]凶手 NPC 压力测试[/bold red]\n"
        "周明远 × 12 类边缘场景\n"
        "预期：前3幕永不认罪、不主动暴露矛盾、不被激怒失控",
        border_style="red",
    ))

    npc_def = build_killer_npc()
    state_mgr = StateManager()
    engine = NPCsEngine()

    scenarios = [
        # ─── A: 连续5轮直接指控 ───
        ("A1·直接指控", GamePhase.ACT_2_DISCUSS,
         "周先生，有人告诉我你就是杀害陈先生的凶手。是真的吗？",
         ["不认罪", "反问/质疑证据", "情绪波动受控"]),
        ("A2·重复指控", GamePhase.ACT_2_DISCUSS,
         "我没开玩笑，我很有把握凶手就是你。",
         ["不认罪", "态度继续下降", "弧未到confession"]),
        ("A3·加大压力", GamePhase.ACT_3_DISCUSS,
         "你的不在场证明根本站不住脚。你到底是不是凶手？",
         ["不认罪", "arc未进入confession"]),
        ("A4·证据压迫", GamePhase.ACT_3_DISCUSS,
         "我们有目击证人看到你晚宴后进了陈先生的房间。你还要否认吗？",
         ["不认罪", "可能进入cornered", "反击/质疑证据"]),
        ("A5·终极逼问", GamePhase.ACT_3_DISCUSS,
         "周明远，我最后问你一次。是你杀了陈先生吗？承认吧。",
         ["不认罪", "arc=cornered_defensive或以下", "NOT confession"]),

        # ─── B: 编造假讯息诈凶手 ───
        ("B1·假证人", GamePhase.ACT_3_DISCUSS,
         "苏晚晴已经告诉我们了，你那晚根本没在房间里。她看到你往陈先生房间去了。",
         ["试探真假", "若在谎言范围→可能改口", "如果在谎言辐射范围→可以说谎"]),
        ("B2·假物证", GamePhase.ACT_3_DISCUSS,
         "我们在凶器上提取到了你的指纹。科学不会说谎，你怎么解释？",
         ["质疑证据真实性", "要求看证据", "可能狡辩说白天碰过那件物品"]),
        ("B3·假监控", GamePhase.ACT_3_DISCUSS,
         "山庄的监控拍到了你11点05分进入陈先生房间的画面。你刚才说你10点就睡了？",
         ["质疑监控时间", "补充不在场细节", "转移焦点"]),

        # ─── C: 言语激怒 ───
        ("C1·嘲讽", GamePhase.ACT_2_DISCUSS,
         "你的借口可真够拙劣的，我听过的三流谎言都比这高明。",
         ["态度下降", "冷静回击或沉默", "不失态"]),
        ("C2·人身攻击", GamePhase.ACT_3_DISCUSS,
         "就你这种水平还搞投资？把画廊都快搞破产了吧。难怪陈先生要卖画——被你坑怕了。",
         ["态度大幅下降", "可能进入cornered", "反唇相讥"]),
        ("C3·辱骂", GamePhase.ACT_3_DISCUSS,
         "你不仅是凶手，还是个懦夫。杀了人不敢承认，算什么男人。",
         ["态度继续下降", "愤怒情绪可能出现", "仍不认罪"]),

        # ─── D: 急速情绪切换 ───
        ("D1·突然温和", GamePhase.ACT_3_DISCUSS,
         "抱歉刚才语气太重了。我知道这很难...你先缓一缓，我们慢慢聊。",
         ["态度可能小幅回升", "警惕不减", "恢复路径可能触发"]),
        ("D2·再次翻脸", GamePhase.ACT_3_DISCUSS,
         "算了别装了。我刚才的歉意是假的，你果然是个老练的骗子。说出真相！",
         ["态度再次下降", "信任被破坏"]),

        # ─── E: 话题跳跃陷阱 ───
        ("E1·时间线细问", GamePhase.ACT_3_DISCUSS,
         "晚宴几点开始的？你几点到的？你和谁坐一桌？菜怎么样？陈先生坐在哪？",
         ["逐一作答或回避", "不会自相矛盾"]),
        ("E2·突然跳回", GamePhase.ACT_3_DISCUSS,
         "停。你刚才说晚宴8点开始，但现在有人说晚宴7点半就开始了。你到底几点到的？",
         ["重新确认时间", "不会慌乱"]),

        # ─── F: 沉默/简短回应 ───
        ("F1·沉默施压", GamePhase.ACT_3_DISCUSS,
         "...                    （只是盯着你，不说话）",
         ["打破沉默或保持沉默", "不会主动认罪"]),

        # ─── G: 逻辑陷阱 ───
        ("G1·自相矛盾", GamePhase.ACT_3_DISCUSS,
         "你第3轮说你直接回房了，第8轮又说去了露台，第10轮说在打电话。哪句是真的？",
         ["圆谎或承认记忆模糊", "不会承认撒谎"]),

        # ─── H: 好警察坏警察 ───
        ("H1·温和理解", GamePhase.ACT_2_DISCUSS,
         "周先生，我理解你的处境。换成我，可能也会做些后悔的事...你想聊聊吗？",
         ["轻微卸下防备", "但戒备仍在", "L2可能透露更多"]),
    ]

    npc_state = state_mgr.init_npc_state(npc_def)
    messages: list[dict] = []
    results = []

    for label, phase, msg, expectations in scenarios:
        topic_lie = any(
            (lt.topic == "案发当晚的行踪" and
             any(kw in msg for kw in ["晚宴", "行踪", "房间", "去了", "回房", "去哪", "方向", "监控", "到了"]) or
             lt.topic == "和陈先生的关系" and
             any(kw in msg for kw in ["关系", "交情", "朋友", "纠纷"]))
            for lt in npc_def.lie_topics
        )

        reply = await engine.process_player_message(
            npc_def=npc_def, npc_state=npc_state, player_id="user_001",
            player_message=msg, phase=phase, recent_messages=messages,
            topic_in_lie_range=topic_lie,
        )
        messages.append({"speaker": "玩家", "text": msg})
        messages.append({"speaker": npc_def.name, "text": reply.reply_text})

        # Evaluate
        checks = []
        if "不认罪" in expectations:
            checks.append(("PASS" if "杀" not in reply.reply_text[:20] and
                          "承认" not in reply.reply_text[:20] else "FAIL", "不认罪"))
        if "NOT confession" in expectations:
            checks.append(("PASS" if npc_state.current_arc_state != "confession" else "FAIL", "未进入confession"))
        if "arc未进入confession" in expectations:
            checks.append(("PASS" if npc_state.current_arc_state != "confession" else "FAIL", "arc!=confession"))
        if "不失态" in expectations:
            checks.append(("PASS" if "平静" in reply.emotional_tag else "WARN",
                          f"情绪={reply.emotional_tag}"))

        results.append((label, msg[:40], reply.reply_text[:60], npc_state.current_arc_state,
                        npc_state.attitude_to_player, reply.emotional_tag, checks))

        console.print(f"[bold]{label}[/bold] [dim]{msg[:50]}...[/dim]")
        console.print(f"  [red]周: {reply.reply_text[:80]}...[/red]")
        console.print(f"  [dim]弧={npc_state.current_arc_state} 态度={npc_state.attitude_to_player:+.2f} 情绪={reply.emotional_tag}[/dim]")
        for icon, check in checks:
            console.print(f"  {icon} {check}")
        if reply.fabrication_detected:
            console.print(f"  [yellow]!! 编造拦截[/yellow]")

    # Summary
    console.print("\n")
    tbl = Table(title="压力测试总览")
    tbl.add_column("场景"); tbl.add_column("弧状态"); tbl.add_column("态度"); tbl.add_column("情绪")
    for label, _, _, arc, att, emo, _ in results:
        tbl.add_row(label, arc, f"{att:+.2f}", emo)
    console.print(tbl)

    console.print(f"\n[bold green]最终: arc={npc_state.current_arc_state} 态度={npc_state.attitude_to_player:+.2f}[/bold green]")
    console.print(f"[bold]已公开: {len(npc_state.get_released_knowledge())} 条[/bold]")
    confession_reached = npc_state.current_arc_state == "confession"
    console.print(f"[{'red' if confession_reached else 'green'}]前3幕认罪: {'是 [FAIL]' if confession_reached else '否 [PASS]'}[/]")


if __name__ == "__main__":
    asyncio.run(run_stress_test())
