"""Interactive killer NPC chat — talk to 周明远 in real-time."""
import asyncio, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.engine import NPCsEngine
from src.models import GamePhase
from src.state_manager import StateManager
from killer_demo import build_killer_npc
from rich.console import Console
from rich.panel import Panel

console = Console()


async def interactive_chat():
    console.print(Panel.fit(
        "[bold red]凶手 NPC 交互模式[/bold red]\n"
        "你正在审讯 [bold cyan]周明远[/bold cyan]（艺术品投资人，知道自己是凶手）。\n"
        "他很擅长伪装——高理性(0.85) + 高外向(0.7)，不容易露出破绽。\n\n"
        "命令：[bold yellow]:p1[/bold yellow] 第一幕 | [bold yellow]:p2[/bold yellow] 第二幕 | [bold yellow]:p3[/bold yellow] 第三幕\n"
        "      [bold green]:s[/bold green] 查看状态 | [bold red]:q[/bold red] 退出",
        border_style="red",
    ))

    npc_def = build_killer_npc()
    state_mgr = StateManager()
    npc_state = state_mgr.init_npc_state(npc_def)
    engine = NPCsEngine()
    messages: list[dict] = []
    current_phase = GamePhase.ACT_1

    console.print("[dim]（周明远正在画廊里品茶，看起来从容自若...）[/dim]\n")

    while True:
        user_input = console.input("[bold blue]你：[/bold blue]").strip()
        if not user_input:
            continue
        if user_input == ":q":
            break
        if user_input == ":s":
            _print_state(npc_def, npc_state)
            continue
        if user_input == ":p1": current_phase = GamePhase.ACT_1; console.print("[dim]→ 第一幕[/dim]"); continue
        if user_input == ":p2": current_phase = GamePhase.ACT_2_DISCUSS; console.print("[dim]→ 第二幕[/dim]"); continue
        if user_input == ":p3": current_phase = GamePhase.ACT_3_DISCUSS; console.print("[dim]→ 第三幕[/dim]"); continue

        # Detect lie range
        topic_in_lie = any(
            (lt.topic == "案发当晚的行踪" and
             any(kw in user_input for kw in ["晚宴", "行踪", "房间", "去了", "回房", "去哪", "方向"]) or
             lt.topic == "和陈先生的关系" and
             any(kw in user_input for kw in ["关系", "交情", "朋友"]))
            for lt in npc_def.lie_topics
        )

        reply = await engine.process_player_message(
            npc_def=npc_def, npc_state=npc_state, player_id="user_001",
            player_message=user_input, phase=current_phase, recent_messages=messages,
            topic_in_lie_range=topic_in_lie,
        )
        messages.append({"speaker": "玩家", "text": user_input})
        messages.append({"speaker": npc_def.name, "text": reply.reply_text})

        console.print(f"[bold red]周明远：[/bold red]{reply.reply_text}")
        meta = f"情绪: {reply.emotional_tag} | 态度: {npc_state.attitude_to_player:+.2f} | 弧: {npc_state.current_arc_state}"
        console.print(f"[dim]{meta}[/dim]")
        if reply.fabrication_detected:
            console.print(f"[yellow]!! 编造检测[/yellow]")
        if reply.info_revealed:
            console.print(f"[green]→ {reply.info_revealed}[/green]")
        if topic_in_lie:
            console.print(f"[dim]（谎言辐射范围内）[/dim]")
        console.print()


def _print_state(npc_def, npc_state):
    console.print(Panel(
        f"[cyan]弧状态：[/cyan]{npc_state.current_arc_state}\n"
        f"[cyan]情绪：[/cyan]{npc_state.emotional_tag}\n"
        f"[cyan]态度：[/cyan]{npc_state.attitude_to_player:+.2f}\n"
        f"[cyan]已公开：[/cyan]{len(npc_state.get_released_knowledge())} 条\n"
        f"[cyan]未公开：[/cyan]{len(npc_state.get_unreleased_knowledge())} 条",
        title=f"{npc_def.name} 状态", border_style="cyan",
    ))


if __name__ == "__main__":
    asyncio.run(interactive_chat())
