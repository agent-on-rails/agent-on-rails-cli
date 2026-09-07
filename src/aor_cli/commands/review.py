"""aor review — human final-review handoff in the terminal."""

from __future__ import annotations

import click
from rich.panel import Panel

from aor_cli.engine.client import EngineClient


@click.command("review")
@click.argument("task_id")
@click.option("--approve", is_flag=True, help="Record human approval (engine call when live).")
@click.option("--reject", is_flag=True, help="Record human rejection.")
@click.option("--notes", default="", help="Optional review notes.")
@click.pass_context
def review_cmd(
    ctx: click.Context,
    task_id: str,
    approve: bool,
    reject: bool,
    notes: str,
) -> None:
    """Human FINAL_REVIEW handoff for TASK_ID."""
    console = ctx.obj["console"]
    if approve and reject:
        console.print("[red]Choose either --approve or --reject[/red]")
        raise SystemExit(2)

    engine = EngineClient(base_url=ctx.obj.get("engine_url"))
    status = engine.task_status(task_id)

    console.print(
        Panel.fit(
            f"Task [bold]{task_id}[/bold]\n"
            f"State: {status.get('state')}\n"
            f"Mode: {status.get('mode', 'live')}\n\n"
            "Evidence must already be attached before human DONE.\n"
            "Heavy collaboration remains on GitHub (Issues/PRs).",
            title="Final review",
        )
    )

    if not approve and not reject:
        console.print("Pass [bold]--approve[/bold] or [bold]--reject[/bold] to record a decision.")
        return

    decision = "approved" if approve else "rejected"
    if engine.stubbed:
        console.print(
            f"[yellow]Stub[/yellow] recorded local intent: {decision}"
            + (f" — notes: {notes}" if notes else "")
        )
        console.print("Wire engine + GitHub to persist FINAL_REVIEW decisions.")
        return

    # Live path reserved for engine API.
    console.print(f"[green]Would POST[/green] /v1/tasks/{task_id}/final-review decision={decision}")
