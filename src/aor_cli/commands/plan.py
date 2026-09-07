"""aor plan — approved spec → local task (AOR-003 local slice)."""

from __future__ import annotations

from pathlib import Path

import click
from rich.table import Table

from aor_cli.tasks.plan import plan_spec
from aor_cli.workspace import require_control_plane


@click.command("plan")
@click.argument("spec_id")
@click.option("--path", "start", type=click.Path(path_type=Path), default=".", show_default=True)
@click.pass_context
def plan_cmd(ctx: click.Context, spec_id: str, start: Path) -> None:
    """Create a bounded task from an approved spec."""
    console = ctx.obj["console"]
    root = require_control_plane(start)
    try:
        spec, task = plan_spec(root, spec_id)
    except FileNotFoundError as exc:
        console.print(f"[red]{exc}[/red]")
        raise SystemExit(1) from exc
    except PermissionError as exc:
        console.print(f"[red]Blocked[/red] {exc}")
        raise SystemExit(2) from exc

    table = Table(title=f"Plan {spec.id}")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("spec", spec.id)
    table.add_row("spec.status", spec.status.upper())
    table.add_row("task", task.id)
    table.add_row("task.status", task.status.upper())
    table.add_row("repository", task.repository or "—")
    console.print(table)
    console.print(f"Next: [bold]aor run {spec.id}[/bold]")
