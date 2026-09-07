"""aor status — project contract, specs, tasks, team."""

from __future__ import annotations

from pathlib import Path

import click
from rich.table import Table

from aor_cli.bootstrap.layout import validate_control_plane
from aor_cli.engine.client import EngineClient
from aor_cli.specs.store import list_specs
from aor_cli.tasks.store import list_tasks
from aor_cli.team.config import TeamConfig
from aor_cli.workspace import find_control_plane


@click.command("status")
@click.option(
    "--path",
    "start",
    type=click.Path(path_type=Path),
    default=".",
    show_default=True,
    help="Project root (or a subdirectory).",
)
@click.pass_context
def status_cmd(ctx: click.Context, start: Path) -> None:
    """Show Agent On Rails project health."""
    console = ctx.obj["console"]
    root = find_control_plane(start) or start.resolve()
    engine = EngineClient(base_url=ctx.obj.get("engine_url"))

    issues = validate_control_plane(root)
    team = TeamConfig.load()
    health = engine.health()
    specs = list_specs(root) if (root / "specs").is_dir() else []
    tasks = list_tasks(root)

    table = Table(title="Agent On Rails status")
    table.add_column("Check")
    table.add_column("Value")
    table.add_row("project", str(root))
    table.add_row("contract", "OK" if not issues else f"{len(issues)} issue(s)")
    table.add_row("specs", str(len(specs)))
    table.add_row("approved+", str(sum(1 for s in specs if s.implementable)))
    table.add_row("tasks", str(len(tasks)))
    table.add_row("engine", health.get("mode", "unknown"))
    table.add_row("team.implementor", team.implementor)
    table.add_row("team.reviewer", team.reviewer)
    table.add_row("team.default_model", team.default_model)
    console.print(table)

    if specs:
        spec_table = Table(title="Specs")
        spec_table.add_column("ID")
        spec_table.add_column("Status")
        spec_table.add_column("Title")
        for spec in specs:
            spec_table.add_row(spec.id, spec.status.upper(), spec.title)
        console.print(spec_table)

    if tasks:
        task_table = Table(title="Tasks")
        task_table.add_column("ID")
        task_table.add_column("Spec")
        task_table.add_column("Status")
        task_table.add_column("Title")
        for task in tasks:
            task_table.add_row(task.id, task.spec_id, task.status.upper(), task.title)
        console.print(task_table)

    if issues:
        for issue in issues:
            console.print(f"[yellow]! [/yellow]{issue.path}: {issue.message}")
        raise SystemExit(1)
