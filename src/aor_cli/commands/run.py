"""aor run — package a bounded task; call the engine when configured."""

from __future__ import annotations

from pathlib import Path

import click
from rich.panel import Panel

from aor_cli.context.package import write_context_package
from aor_cli.engine.client import EngineClient
from aor_cli.specs.store import get_spec
from aor_cli.tasks.plan import plan_spec
from aor_cli.tasks.store import get_task, list_tasks, save_task
from aor_cli.workspace import require_control_plane


@click.command("run")
@click.argument("target")
@click.option("--path", "start", type=click.Path(path_type=Path), default=".", show_default=True)
@click.pass_context
def run_cmd(ctx: click.Context, target: str, start: Path) -> None:
    """Run or package TARGET (spec id or task id)."""
    console = ctx.obj["console"]
    root = require_control_plane(start)
    spec, task = _resolve(root, target)
    if spec.status.lower() in {"draft", "review"}:
        console.print(
            f"[red]Blocked[/red] {spec.id} is {spec.status.upper()}. "
            f"A human must run `aor spec approve {spec.id}` first."
        )
        raise SystemExit(2)

    if spec.status.lower() == "approved" or task is None:
        spec, task = plan_spec(root, spec.id)

    context_path = write_context_package(root, spec, task)
    task.status = "running"
    task.attempts += 1
    save_task(root, task)

    engine = EngineClient(base_url=ctx.obj.get("engine_url"))
    if not engine.stubbed:
        result = engine.run_task(task.id)
        console.print(result)
        if not result.get("ok", True):
            raise SystemExit(2)
        return

    console.print(
        Panel.fit(
            f"Task [bold]{task.id}[/bold] for spec [bold]{spec.id}[/bold] is packaged.\n\n"
            f"Context: {context_path}\n"
            f"Prompt:  {context_path.parent / 'prompt.md'}\n\n"
            "The engine is not running yet, so Agent On Rails will not invent a coding agent.\n"
            "Open the prompt in Cursor, Claude Code, Codex, or another headless agent,\n"
            "and keep work in the sibling implementation repo — not this contract folder.\n\n"
            f"When the agent is done: [bold]aor review {task.id}[/bold]",
            title="Agent On Rails — local run",
        )
    )


def _resolve(root: Path, target: str):
    spec = get_spec(root, target)
    if spec is not None:
        existing = next((t for t in list_tasks(root) if t.spec_id == spec.id), None)
        return spec, existing
    task = get_task(root, target)
    if task is None:
        raise SystemExit(f"Unknown spec or task: {target}")
    spec = get_spec(root, task.spec_id)
    if spec is None:
        raise SystemExit(f"Task {task.id} references missing spec {task.spec_id}")
    return spec, task
