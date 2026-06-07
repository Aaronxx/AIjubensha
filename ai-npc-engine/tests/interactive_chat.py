"""Interactive NPC chat — talk to Su Wanqing in real-time."""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.engine import NPCsEngine
from src.models import GamePhase
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from test_engine import build_sample_npc
from src.state_manager import StateManager

console = Console()


async def interactive_chat():
    console.print(Panel.fit(
        "[bold yellow]AI NPC 对话引擎 — 交互模式[/bold yellow]\n"
        "你现在是剧本杀中的一名角色，正在与 [bold cyan]苏晚晴[/bold cyan]（画廊老板）对话。\n"
        "输入消息与她交流，输入 [bold red]:q[/bold red] 退出，"
        "输入 [bold green]:s[/bold green] 查看她的状态。\n"
        "输入 [bold yellow]:p1[/bold yellow] 进入第一幕，"
        "[bold yellow]:p2[/bold yellow] 进入第二幕，"
        "[bold yellow]:p3[/bold yellow] 进入第三幕。",
        border_style="yellow",
    ))

    npc_def = build_sample_npc()
    state_mgr = StateManager()
    npc_state = state_mgr.init_npc_state(npc_def)
    engine = NPCsEngine()

    messages: list[dict] = []
    current_phase = GamePhase.ACT_1

    console.print("[dim]（苏晚晴正在画廊里整理画作，你走了进去...）[/dim]\n")

    while True:
        user_input = console.input("[bold blue]你：[/bold blue]").strip()

        if not user_input:
            continue

        if user_input == ":q":
            console.print("[dim]对话结束。[/dim]")
            break

        if user_input == ":s":
            _print_state(npc_def, npc_state)
            continue

        if user_input == ":p1":
            current_phase = GamePhase.ACT_1
            console.print("[dim]→ 切换到第一幕：迷雾开场[/dim]")
            continue

        if user_input == ":p2":
            current_phase = GamePhase.ACT_2_DISCUSS
            console.print("[dim]→ 切换到第二幕：尸体已发现，暗流涌动[/dim]")
            continue

        if user_input == ":p3":
            current_phase = GamePhase.ACT_3_DISCUSS
            console.print("[dim]→ 切换到第三幕：真相逼近，深入质问[/dim]")
            continue

        if user_input.startswith(":t"):
            # Toggle topic in lie range for testing
            parts = user_input.split(maxsplit=1)
            topic_in_lie = True if len(parts) < 2 else parts[1].lower() == "true"
            console.print(f"[dim]话题在谎言范围内: {topic_in_lie}[/dim]")
            continue

        console.print(f"[dim]（{_phase_name(current_phase)}，苏晚晴正在思考...）[/dim]")

        reply = await engine.process_player_message(
            npc_def=npc_def,
            npc_state=npc_state,
            player_id="user_001",
            player_message=user_input,
            phase=current_phase,
            recent_messages=messages,
        )

        messages.append({"speaker": "玩家", "text": user_input})
        messages.append({"speaker": npc_def.name, "text": reply.reply_text})

        console.print(f"[bold green]苏晚晴：[/bold green]{reply.reply_text}")
        meta = (
            f"情绪: {reply.emotional_tag}"
            f" | 态度: {npc_state.attitude_to_player:+.2f}"
            f" | 弧状态: {npc_state.current_arc_state}"
            f" | {reply.dialogue_latency_ms:.0f}+{reply.extraction_latency_ms:.0f}ms"
        )
        console.print(f"[dim]{meta}[/dim]")
        if reply.info_revealed:
            console.print(f"[yellow]→ 新线索: {reply.info_revealed}[/yellow]")
        console.print()


def _phase_name(phase: GamePhase) -> str:
    names = {
        GamePhase.ACT_1: "第一幕·迷雾开场",
        GamePhase.ACT_2_SEARCH: "第二幕·搜证",
        GamePhase.ACT_2_DISCUSS: "第二幕·讨论",
        GamePhase.ACT_3_SEARCH: "第三幕·搜证",
        GamePhase.ACT_3_DISCUSS: "第三幕·讨论",
        GamePhase.ACT_4_VOTE: "第四幕·投票",
    }
    return names.get(phase, phase.value)


def _print_state(npc_def, npc_state):
    console.print(Panel(
        f"[cyan]角色弧状态：[/cyan]{npc_state.current_arc_state}\n"
        f"[cyan]情绪标签：[/cyan]{npc_state.emotional_tag}\n"
        f"[cyan]对玩家态度：[/cyan]{npc_state.attitude_to_player:+.2f}\n"
        f"[cyan]已公开信息：[/cyan]{len(npc_state.get_released_knowledge())} 条\n"
        f"[cyan]未公开信息：[/cyan]{len(npc_state.get_unreleased_knowledge())} 条\n"
        f"[cyan]事实账本记录：[/cyan]{len(npc_state.fact_ledger)} 条",
        title=f"{npc_def.name} 状态",
        border_style="cyan",
    ))


if __name__ == "__main__":
    asyncio.run(interactive_chat())
