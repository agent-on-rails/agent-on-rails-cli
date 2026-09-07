"""aor watch — poll task state until terminal or timeout."""

from __future__ import annotations

import time

import click
from rich.live import Live
from rich.table import Table

from aor_cli.engine.client import EngineClient

TERMINAL = frozenset({"DONE", "FAILED", "FINAL_REVIEW", "CANCELLED", "BLOCKED"})


@click.command("watch")
@click.argument("task_id")
@click.option("--interval", default=2.0, show_default=True, help="Poll interval seconds.")
@click.option("--max-polls", default=30, show_default=True, help="Stop after N polls (stub safety).")
@click.pass_context
def watch_cmd(ctx: click.Context, task_id: str, interval: float, max_polls: int) -> None:
    """Watch TASK_ID until FINAL_REVIEW / DONE / FAILED (or stub limit)."""
    console = ctx.obj["console"]
    engine = EngineClient(base_url=ctx.obj.get("engine_url"))

    def render(state: str, payload: dict) -> Table:
        table = Table(title=f"watch {task_id}")
        table.add_column("Field")
        table.add_column("Value")
        table.add_row("state", state)
        table.add_row("mode", str(payload.get("mode", "live")))
        table.add_row("message", str(payload.get("message", "")))
        return table

    last_state = "UNKNOWN"
    with Live(render(last_state, {}), console=console, refresh_per_second=4) as live:
        for _ in range(max_polls):
            payload = engine.task_status(task_id)
            last_state = str(payload.get("state", "UNKNOWN"))
            live.update(render(last_state, payload))
            if last_state in TERMINAL:
                break
            if engine.stubbed:
                # Stub never advances; exit after first poll.
                break
            time.sleep(interval)

    if last_state == "FINAL_REVIEW":
        console.print("[cyan]Ready for human final review[/cyan] — run: aor review " + task_id)
    elif engine.stubbed:
        console.print("[dim]Engine stubbed; watching is a no-op until AOR_ENGINE_URL is set.[/dim]")
