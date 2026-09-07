"""aor status — local control-plane + engine connectivity."""

from __future__ import annotations

from pathlib import Path

import click
from rich.table import Table

from aor_cli.bootstrap.layout import validate_control_plane
from aor_cli.engine.client import EngineClient
from aor_cli.team.config import TeamConfig


@click.command("status")
@click.option(
    "--path",
    "control_plane",
    type=click.Path(path_type=Path, exists=False),
    default=".",
    show_default=True,
    help="Control-plane root to validate.",
)
@click.pass_context
def status_cmd(ctx: click.Context, control_plane: Path) -> None:
    """Show control-plane validity, team config, and engine health."""
    console = ctx.obj["console"]
    root = control_plane.resolve()
    engine = EngineClient(base_url=ctx.obj.get("engine_url"))

    issues = validate_control_plane(root)
    team = TeamConfig.load()
    health = engine.health()

    table = Table(title="Agent On Rails status")
    table.add_column("Check")
    table.add_column("Value")
    table.add_row("control-plane", str(root))
    table.add_row("contract", "OK" if not issues else f"{len(issues)} issue(s)")
    table.add_row("engine", health.get("mode", "unknown"))
    table.add_row("engine.ok", str(health.get("ok")))
    table.add_row("team.implementor", team.implementor)
    table.add_row("team.reviewer", team.reviewer)
    table.add_row("team.default_model", team.default_model)
    table.add_row("team.escalate_model", team.escalate_model)
    console.print(table)

    if issues:
        for issue in issues:
            console.print(f"[yellow]! [/yellow]{issue.path}: {issue.message}")
        raise SystemExit(1)
