"""aor watch — follow a local or engine task until a terminal state."""

from __future__ import annotations

import time
from pathlib import Path

import click
from rich.live import Live
from rich.table import Table

from aor_cli.engine.client import EngineClient
from aor_cli.tasks.store import get_task, list_tasks
from aor_cli.workspace import require_control_plane

TERMINAL = frozenset({"DONE", "FAILED", "FINAL_REVIEW", "CANCELLED", "BLOCKED", "REVIEW"})


@click.command("watch")
@click.argument("target")
@click.option("--path", "start", type=click.Path(path_type=Path), default=".", show_default=True)
@click.option("--interval", default=2.0, show_default=True, help="Poll interval seconds.")
@click.option("--max-polls", default=30, show_default=True, help="Stop after N polls.")
@click.pass_context
def watch_cmd(ctx: click.Context, target: str, start: Path, interval: float, max_polls: int) -> None:
    """Watch TARGET (spec or task id) until a terminal state."""
    console = ctx.obj["console"]
    root = require_control_plane(start)
    task = get_task(root, target)
    if task is None:
        matches = [t for t in list_tasks(root) if t.spec_id.upper() == target.strip().upper()]
        task = matches[-1] if matches else None
    if task is None:
        console.print(f"[red]No local task for[/red] {target}")
        raise SystemExit(1)

    engine = EngineClient(base_url=ctx.obj.get("engine_url"))

    def render(state: str, message: str) -> Table:
        table = Table(title=f"watch {task.id}")
        table.add_column("Field")
        table.add_column("Value")
        table.add_row("spec", task.spec_id)
        table.add_row("state", state)
        table.add_row("mode", "stub" if engine.stubbed else "live")
        table.add_row("message", message)
        return table

    last_state = task.status.upper()
    with Live(render(last_state, ""), console=console, refresh_per_second=4) as live:
        for _ in range(max_polls):
            current = get_task(root, task.id)
            last_state = (current.status if current else last_state).upper()
            message = ""
            if not engine.stubbed:
                payload = engine.task_status(task.id)
                last_state = str(payload.get("state", last_state)).upper()
                message = str(payload.get("message", ""))
            live.update(render(last_state, message))
            if last_state in TERMINAL:
                break
            if engine.stubbed:
                break
            time.sleep(interval)

    if last_state in {"FINAL_REVIEW", "REVIEW"}:
        console.print(f"[cyan]Ready for human final review[/cyan] — run: aor review {task.id}")
    elif engine.stubbed:
        console.print("[dim]Local mode: state is whatever `aor run` / `aor review` last wrote.[/dim]")
