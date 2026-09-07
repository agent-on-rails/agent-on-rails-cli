"""aor review — human final-review handoff."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import click
from rich.panel import Panel

from aor_cli.engine.client import EngineClient
from aor_cli.specs.store import get_spec, set_spec_status
from aor_cli.tasks.store import get_task, list_tasks, save_task
from aor_cli.workspace import aor_dir, require_control_plane


@click.command("review")
@click.argument("target")
@click.option("--path", "start", type=click.Path(path_type=Path), default=".", show_default=True)
@click.option("--approve", is_flag=True, help="Record human approval.")
@click.option("--reject", is_flag=True, help="Record human rejection.")
@click.option("--notes", default="", help="Optional review notes.")
@click.pass_context
def review_cmd(
    ctx: click.Context,
    target: str,
    start: Path,
    approve: bool,
    reject: bool,
    notes: str,
) -> None:
    """Human FINAL_REVIEW handoff for a spec or task id."""
    console = ctx.obj["console"]
    if approve and reject:
        console.print("[red]Choose either --approve or --reject[/red]")
        raise SystemExit(2)

    root = require_control_plane(start)
    task = get_task(root, target)
    if task is None:
        matches = [t for t in list_tasks(root) if t.spec_id.upper() == target.strip().upper()]
        task = matches[-1] if matches else None
    if task is None:
        console.print(f"[red]No local task for[/red] {target}. Run `aor plan` first.")
        raise SystemExit(1)

    spec = get_spec(root, task.spec_id)
    engine = EngineClient(base_url=ctx.obj.get("engine_url"))
    live = engine.task_status(task.id) if not engine.stubbed else {}

    console.print(
        Panel.fit(
            f"Task [bold]{task.id}[/bold]  spec [bold]{task.spec_id}[/bold]\n"
            f"Local state: {task.status}\n"
            f"Engine: {live.get('state', 'local')}\n"
            f"Context: {task.context_path or '(none yet — run `aor run` first)'}\n\n"
            "Evidence must already be attached before human DONE.\n"
            "Heavy collaboration remains on GitHub (Issues/PRs).",
            title="Final review",
        )
    )

    if not approve and not reject:
        console.print("Pass [bold]--approve[/bold] or [bold]--reject[/bold] to record a decision.")
        return

    decision = "approved" if approve else "rejected"
    record = {
        "task_id": task.id,
        "spec_id": task.spec_id,
        "decision": decision,
        "notes": notes,
        "at": datetime.now(UTC).isoformat(),
    }
    review_path = aor_dir(root) / "reviews" / f"{task.id}.json"
    review_path.parent.mkdir(parents=True, exist_ok=True)
    review_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")

    if approve:
        task.status = "done"
        save_task(root, task)
        if spec is not None:
            set_spec_status(root, spec.id, "final_review")
        console.print(
            f"[green]Recorded[/green] human approval for {task.id} → {review_path}\n"
            f"{task.spec_id} is now FINAL_REVIEW. Set it DONE only after evidence is attached."
        )
    else:
        task.status = "failed"
        save_task(root, task)
        if spec is not None:
            set_spec_status(root, spec.id, "retry")
        console.print(f"[yellow]Recorded[/yellow] rejection for {task.id}. Spec moved to RETRY.")

    if notes:
        console.print(f"notes: {notes}")
