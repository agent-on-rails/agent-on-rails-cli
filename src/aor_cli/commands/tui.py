"""aor tui — mouse-friendly terminal harness."""

from __future__ import annotations

from pathlib import Path

import click

from aor_cli.tui.app import run_app


@click.command("tui")
@click.option(
    "--path",
    "start",
    type=click.Path(path_type=Path),
    default=".",
    show_default=True,
    help="Directory to look for (or create) a project.",
)
@click.pass_context
def tui_cmd(ctx: click.Context, start: Path) -> None:
    """Open the Agent On Rails terminal UI (mouse-friendly)."""
    raise SystemExit(run_app(start=start.resolve(), engine_url=ctx.obj.get("engine_url")))
