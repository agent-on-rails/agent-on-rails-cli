"""Click entrypoint for `aor`."""

from __future__ import annotations

import click
from rich.console import Console

from aor_cli import __version__
from aor_cli.commands.guide import guide_cmd
from aor_cli.commands.init import init_cmd
from aor_cli.commands.plan import plan_cmd
from aor_cli.commands.review import review_cmd
from aor_cli.commands.run import run_cmd
from aor_cli.commands.spec import spec_cmd
from aor_cli.commands.status import status_cmd
from aor_cli.commands.team import team_cmd
from aor_cli.commands.watch import watch_cmd

console = Console()

EPILOG = """\
Flow:  aor init → aor spec new → aor spec approve → aor plan → aor run → aor review

Run `aor guide` for the full how-to. The product is Agent On Rails;
the control plane is the contract folder inside your project.
"""


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    epilog=EPILOG,
)
@click.version_option(__version__, prog_name="aor")
@click.option(
    "--engine-url",
    envvar="AOR_ENGINE_URL",
    default=None,
    help="Engine base URL (optional; local mode is the default until the engine ships).",
)
@click.pass_context
def main(ctx: click.Context, engine_url: str | None) -> None:
    """Agent On Rails — from specs to running software."""
    ctx.ensure_object(dict)
    ctx.obj["engine_url"] = engine_url
    ctx.obj["console"] = console


main.add_command(guide_cmd, name="guide")
main.add_command(init_cmd, name="init")
main.add_command(spec_cmd, name="spec")
main.add_command(plan_cmd, name="plan")
main.add_command(status_cmd, name="status")
main.add_command(team_cmd, name="team")
main.add_command(run_cmd, name="run")
main.add_command(watch_cmd, name="watch")
main.add_command(review_cmd, name="review")
