"""aor init — create or validate a control-plane repository (AOR-001)."""

from __future__ import annotations

from pathlib import Path

import click
from rich.table import Table

from aor_cli.bootstrap.layout import scaffold_control_plane, validate_control_plane


@click.command("init")
@click.argument("path", required=False, type=click.Path(path_type=Path))
@click.option("--name", default=None, help="Product name used in scaffold templates.")
@click.option("--validate-only", is_flag=True, help="Only validate; do not create files.")
@click.option("--force", is_flag=True, help="Overwrite existing scaffold files.")
@click.option(
    "--create-github",
    is_flag=True,
    help="After scaffold, create a private GitHub repo with `gh` (requires auth).",
)
@click.option("--org", default="agent-on-rails", show_default=True, help="GitHub org for --create-github.")
@click.option("--public", is_flag=True, help="Make the GitHub repo public (default private).")
@click.pass_context
def init_cmd(
    ctx: click.Context,
    path: Path | None,
    name: str | None,
    validate_only: bool,
    force: bool,
    create_github: bool,
    org: str,
    public: bool,
) -> None:
    """Create or validate a control-plane docs+specs layout."""
    console = ctx.obj["console"]
    root = (path or Path.cwd()).resolve()
    product = name or root.name.removesuffix("-control-plane") or root.name

    if not validate_only:
        written = scaffold_control_plane(root, product, force=force)
        if written:
            console.print(f"[green]Scaffolded[/green] {len(written)} path(s) under {root}")
            for p in written:
                console.print(f"  + {p.relative_to(root)}")
        else:
            console.print(f"[dim]Nothing to write[/dim] (already present). Use --force to overwrite.")

    issues = validate_control_plane(root)
    if issues:
        table = Table(title="Validation issues")
        table.add_column("Path")
        table.add_column("Message")
        for issue in issues:
            table.add_row(issue.path, issue.message)
        console.print(table)
        raise SystemExit(1)

    console.print(f"[green]OK[/green] control-plane contract valid: {root}")

    if create_github:
        _create_github_repo(console, root, org=org, public=public)


def _create_github_repo(console, root: Path, *, org: str, public: bool) -> None:
    import shutil
    import subprocess

    if not shutil.which("gh"):
        console.print("[red]gh not found[/red] — install GitHub CLI or omit --create-github")
        raise SystemExit(2)
    repo_name = root.name
    visibility = "--public" if public else "--private"
    cmd = ["gh", "repo", "create", f"{org}/{repo_name}", visibility, "--source", str(root), "--remote", "origin"]
    # Push only if user already has commits; otherwise just create empty remote link later.
    if (root / ".git").exists():
        console.print(f"Creating GitHub repo [bold]{org}/{repo_name}[/bold] …")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            console.print(result.stderr or result.stdout)
            raise SystemExit(result.returncode)
        console.print(result.stdout or "[green]created[/green]")
    else:
        console.print("[yellow]No .git yet[/yellow] — run `git init` then re-run with --create-github")
