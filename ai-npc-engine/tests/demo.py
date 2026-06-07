"""Demo mode: pre-scripted NPC conversation showcase."""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.engine import NPCsEngine
from src.models import GamePhase
from rich.console import Console
from rich.panel import Panel

from test_engine import build_sample_npc
from src.state_manager import StateManager

console = Console()


async def demo():
    console.print(Panel.fit(
        "[bold yellow]AI NPC 对话引擎 — 演示模式[/bold yellow]\n"
        "苏晚晴（画廊老板）× 玩家 的 8 轮对话演示",
        border_style="yellow",
    ))

    npc_def = build_sample_npc()
    state_mgr = StateManager()
    npc_state = state_mgr.init_npc_state(npc_def)
    engine = NPCsEngine()
    messages: list[dict] = []

    # Full conversation script
    script = [
        (GamePhase.ACT_1, "你好，我是来参加晚宴的客人。请问你是？",
         "初次见面，询问身份"),
        (GamePhase.ACT_1, "这个山庄真漂亮。听说你是个画家？",
         "寒暄，尝试拉近距离"),
        (GamePhase.ACT_1, "我也很喜欢艺术，虽然不太懂。你最喜欢哪位画家？",
         "表达对艺术的兴趣，建立共鸣"),
        (GamePhase.ACT_2_DISCUSS, "苏女士，我听说死者生前常来你的画廊？",
         "案件发生，开始询问"),
        (GamePhase.ACT_2_DISCUSS, "你最后一次见到他是什么时候？他状态如何？",
         "追问最后见面细节"),
        (GamePhase.ACT_3_DISCUSS, "苏女士，我查到了一些事。你和死者之间的关系，不只是画商和客户吧？",
         "直接追问隐藏关系"),
        (GamePhase.ACT_3_DISCUSS, "他妻子威胁过你，对不对？你不用一个人承担这一切。",
         "展现共情和理解"),
        (GamePhase.ACT_3_DISCUSS, "把真相告诉我。只有说出来，才能真正放下。",
         "最终推进，寻求真相"),
    ]

    total_tokens = 0
    total_ms = 0

    for i, (phase, msg, desc) in enumerate(script):
        console.print(f"\n[bold]━━━ 第{i+1}轮 [{phase.value}] · {desc} ━━━[/bold]")
        console.print(f"[bold blue]玩家：[/bold blue]{msg}")

        reply = await engine.process_player_message(
            npc_def=npc_def, npc_state=npc_state, player_id="user_001",
            player_message=msg, phase=phase, recent_messages=messages,
        )
        messages.append({"speaker": "玩家", "text": msg})
        messages.append({"speaker": npc_def.name, "text": reply.reply_text})

        total_tokens += reply.tokens_used
        total_ms += reply.dialogue_latency_ms + reply.extraction_latency_ms

        console.print(f"[bold green]苏晚晴：[/bold green]{reply.reply_text}")
        meta_parts = [f"情绪: {reply.emotional_tag}"]
        if npc_state.attitude_to_player != 0.0:
            meta_parts.append(f"态度: {npc_state.attitude_to_player:+.2f}")
        meta_parts.append(f"弧: {npc_state.current_arc_state}")
        meta_parts.append(f"对话{reply.dialogue_latency_ms:.0f}ms+提取{reply.extraction_latency_ms:.0f}ms")
        console.print(f"[dim]{' | '.join(meta_parts)}[/dim]")
        if reply.fabrication_detected:
            console.print(f"[red]!! 编造检测！已替换为回避话术[/red]")
            console.print(f"[dim]原回复: {reply.original_reply}[/dim]")
        if reply.info_revealed:
            console.print(f"[yellow]→ 新线索: {reply.info_revealed}[/yellow]")

    # Final summary
    console.print("\n")
    console.print(Panel.fit("[bold]演示完成[/bold]", border_style="green"))
    _print_state(npc_def, npc_state)
    console.print("\n[bold cyan]分幕信息门控规则：[/bold cyan]")
    console.print("  第一幕 → 仅 L1 | 第二幕 → L1-L2 | 第三幕 → L1-L3 | 第四幕 → 全部")
    console.print(f"  演示使用了 ACT_1(3轮) → ACT_2_DISCUSS(2轮) → ACT_3_DISCUSS(3轮)")
    console.print(f"\n[bold]统计：[/bold]")
    console.print(f"  对话轮数: {len(script)}")
    console.print(f"  总 tokens: {total_tokens}")
    console.print(f"  总耗时: {total_ms/1000:.1f}s | 平均: {total_ms/len(script):.0f}ms/轮")
    console.print(f"\n[bold]事实账本：[/bold]")
    for entry in npc_state.fact_ledger:
        console.print(f"  [dim]- [{entry.get('level','?')}] {entry['content'][:50]}...[/dim]")


def _print_state(npc_def, npc_state):
    console.print(Panel(
        f"[cyan]角色弧状态：[/cyan]{npc_state.current_arc_state}\n"
        f"[cyan]情绪标签：[/cyan]{npc_state.emotional_tag}\n"
        f"[cyan]对玩家态度：[/cyan]{npc_state.attitude_to_player:+.2f}\n"
        f"[cyan]已公开信息：[/cyan]{len(npc_state.get_released_knowledge())} 条\n"
        f"[cyan]未公开信息：[/cyan]{len(npc_state.get_unreleased_knowledge())} 条\n"
        f"[cyan]事实账本：[/cyan]{len(npc_state.fact_ledger)} 条",
        title=f"{npc_def.name} 最终状态",
        border_style="cyan",
    ))


if __name__ == "__main__":
    asyncio.run(demo())
