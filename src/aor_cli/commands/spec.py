"""aor spec — create, list, show, and approve contracts."""

from __future__ import annotations

from pathlib import Path

import click
from rich.table import Table

from aor_cli.project import ProjectMeta, default_prefix
from aor_cli.specs.store import approve_spec, create_spec, get_spec, list_specs
from aor_cli.workspace import require_control_plane


@click.group("spec")
def spec_cmd() -> None:
    """Create, list, show, or approve specs."""


@spec_cmd.command("list")
@click.option("--path", "start", type=click.Path(path_type=Path), default=".", show_default=True)
@click.pass_context
def spec_list(ctx: click.Context, start: Path) -> None:
    """List specs in this project."""
    console = ctx.obj["console"]
    root = require_control_plane(start)
    records = list_specs(root)
    if not records:
        console.print("[dim]No specs yet.[/dim] Create one with `aor spec new \"My feature\"`.")
        return
    table = Table(title="Specs")
    table.add_column("ID")
    table.add_column("Status")
    table.add_column("Title")
    table.add_column("Repos")
    for spec in records:
        table.add_row(spec.id, spec.status.upper(), spec.title, ", ".join(spec.repositories) or "—")
    console.print(table)


@spec_cmd.command("show")
@click.argument("spec_id")
@click.option("--path", "start", type=click.Path(path_type=Path), default=".", show_default=True)
@click.pass_context
def spec_show(ctx: click.Context, spec_id: str, start: Path) -> None:
    """Show one spec."""
    console = ctx.obj["console"]
    root = require_control_plane(start)
    spec = get_spec(root, spec_id)
    if spec is None:
        console.print(f"[red]Spec not found:[/red] {spec_id}")
        raise SystemExit(1)
    console.print(f"[bold]{spec.id}[/bold]  {spec.title}")
    console.print(f"status: {spec.status.upper()}")
    console.print(f"path:   {spec.path}")
    console.print(f"repos:  {', '.join(spec.repositories) or '—'}")
    if spec.intent:
        console.print()
        console.print(spec.intent)


@spec_cmd.command("new")
@click.argument("title")
@click.option("--path", "start", type=click.Path(path_type=Path), default=".", show_default=True)
@click.option("--prefix", default=None, help="Spec prefix (default: from project metadata).")
@click.option(
    "--repo",
    "repos",
    multiple=True,
    help="Implementation repository name (repeatable). Default: app.",
)
@click.option("--intent", default=None, help="One-line intent for the frontmatter.")
@click.pass_context
def spec_new(
    ctx: click.Context,
    title: str,
    start: Path,
    prefix: str | None,
    repos: tuple[str, ...],
    intent: str | None,
) -> None:
    """Create a draft spec bundle (spec.md + acceptance.md + evidence.md)."""
    console = ctx.obj["console"]
    root = require_control_plane(start)
    meta = ProjectMeta.load(root)
    use_prefix = prefix or (meta.prefix if meta else default_prefix(root.name))
    record = create_spec(
        root,
        title=title,
        prefix=use_prefix,
        repositories=list(repos) or ["app"],
        intent=intent,
    )
    console.print(f"[green]Created[/green] {record.id} — {record.path.parent.relative_to(root)}")
    console.print(f"Edit the draft, then: [bold]aor spec approve {record.id}[/bold]")


@spec_cmd.command("approve")
@click.argument("spec_id")
@click.option("--path", "start", type=click.Path(path_type=Path), default=".", show_default=True)
@click.pass_context
def spec_approve(ctx: click.Context, spec_id: str, start: Path) -> None:
    """Human-approve a DRAFT/REVIEW spec so it can be planned."""
    console = ctx.obj["console"]
    root = require_control_plane(start)
    try:
        record = approve_spec(root, spec_id)
    except FileNotFoundError as exc:
        console.print(f"[red]{exc}[/red]")
        raise SystemExit(1) from exc
    except ValueError as exc:
        console.print(f"[red]{exc}[/red]")
        raise SystemExit(2) from exc
    console.print(f"[green]Approved[/green] {record.id} — implementation agents may now be planned.")
    console.print(f"Next: [bold]aor plan {record.id}[/bold]")
