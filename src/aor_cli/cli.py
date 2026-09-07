"""Click entrypoint for `aor`."""

from __future__ import annotations

import click
from rich.console import Console

from aor_cli import __version__
from aor_cli.commands.init import init_cmd
from aor_cli.commands.review import review_cmd
from aor_cli.commands.run import run_cmd
from aor_cli.commands.status import status_cmd
from aor_cli.commands.team import team_cmd
from aor_cli.commands.watch import watch_cmd

console = Console(stderr=True)


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(__version__, prog_name="aor")
@click.option(
    "--engine-url",
    envvar="AOR_ENGINE_URL",
    default=None,
    help="Engine base URL (default: local stub when unset).",
)
@click.pass_context
def main(ctx: click.Context, engine_url: str | None) -> None:
    """Agent On Rails — terminal operator CLI."""
    ctx.ensure_object(dict)
    ctx.obj["engine_url"] = engine_url
    ctx.obj["console"] = console


main.add_command(init_cmd, name="init")
main.add_command(status_cmd, name="status")
main.add_command(team_cmd, name="team")
main.add_command(run_cmd, name="run")
main.add_command(watch_cmd, name="watch")
main.add_command(review_cmd, name="review")
