"""aor run — start/resume a task via engine (stub-aware)."""

from __future__ import annotations

import click
from rich.pretty import Pretty

from aor_cli.engine.client import EngineClient


@click.command("run")
@click.argument("task_id")
@click.pass_context
def run_cmd(ctx: click.Context, task_id: str) -> None:
    """Request the engine to run or resume TASK_ID."""
    console = ctx.obj["console"]
    engine = EngineClient(base_url=ctx.obj.get("engine_url"))
    result = engine.run_task(task_id)
    console.print(Pretty(result))
    if not result.get("ok", True) and engine.stubbed:
        raise SystemExit(2)
