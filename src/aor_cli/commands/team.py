"""aor team — configure AI Team roles and models."""

from __future__ import annotations

import click
from rich.pretty import Pretty

from aor_cli.team.config import TeamConfig


@click.command("team")
@click.option("--implementor", default=None, help="Implementor adapter id (e.g. codex).")
@click.option("--reviewer", default=None, help="Reviewer adapter id (e.g. claude).")
@click.option("--default-model", default=None, help="Default / cheap model tier.")
@click.option("--escalate-model", default=None, help="Escalate / frontier model tier.")
@click.option("--project", default=None, help="Optional project label.")
@click.option("--show", is_flag=True, help="Print current config and exit.")
@click.pass_context
def team_cmd(
    ctx: click.Context,
    implementor: str | None,
    reviewer: str | None,
    default_model: str | None,
    escalate_model: str | None,
    project: str | None,
    show: bool,
) -> None:
    """Configure or show the local AI Team definition."""
    console = ctx.obj["console"]
    cfg = TeamConfig.load()

    if show and not any([implementor, reviewer, default_model, escalate_model, project]):
        console.print(Pretty(cfg))
        return

    if implementor:
        cfg.implementor = implementor
    if reviewer:
        cfg.reviewer = reviewer
    if default_model:
        cfg.default_model = default_model
    if escalate_model:
        cfg.escalate_model = escalate_model
    if project:
        cfg.project = project

    if any([implementor, reviewer, default_model, escalate_model, project]):
        path = cfg.save()
        console.print(f"[green]Saved[/green] {path}")

    console.print(Pretty(cfg))
