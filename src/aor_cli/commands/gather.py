"""aor gather — natural language → SurveyDesk-shaped specs (AOR-010)."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import click
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from aor_cli.gather.extract import extract_outline
from aor_cli.gather.models import SpecOutline
from aor_cli.gather.writer import write_surveydesk_specs
from aor_cli.llm.config import LlmConfig


def _read_requirements(requirements: str | None, file: Path | None) -> str:
    if file is not None:
        return file.read_text(encoding="utf-8")
    if requirements:
        return requirements
    if not click.get_text_stream("stdin").isatty():
        return click.get_text_stream("stdin").read()
    return click.edit("# Paste natural-language requirements below, then save.\n\n") or ""


def _outline_path(root: Path) -> Path:
    return root / ".aor" / "gather" / "outline.json"


def _save_outline(root: Path, outline: SpecOutline) -> Path:
    path = _outline_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(outline.to_dict(), indent=2) + "\n", encoding="utf-8")
    return path


def _load_outline(path: Path) -> SpecOutline:
    data = json.loads(path.read_text(encoding="utf-8"))
    return SpecOutline.from_dict(data)


def _print_outline(console, outline: SpecOutline) -> None:
    console.print(
        Panel.fit(
            f"[bold]{outline.product_name}[/bold]\n{outline.tagline}",
            title="Outline (confirm before write)",
        )
    )
    table = Table(title="Requirements")
    table.add_column("ID")
    table.add_column("Title")
    table.add_column("SHALL")
    for req in outline.requirements:
        table.add_row(req.id, req.title, req.shall[:80] + ("…" if len(req.shall) > 80 else ""))
    console.print(table)
    console.print(f"[dim]Domains:[/dim] {', '.join(d.name for d in outline.domains) or '—'}")
    console.print(f"[dim]ADRs:[/dim] {', '.join(a.id for a in outline.adrs) or '—'}")
    console.print(
        f"[dim]Acceptance:[/dim] {', '.join(a.name for a in outline.acceptance) or '—'}"
    )


def _edit_outline(path: Path) -> SpecOutline:
    editor = os.environ.get("EDITOR") or os.environ.get("VISUAL") or "vi"
    subprocess.run([editor, str(path)], check=False)
    return _load_outline(path)


@click.group("gather", invoke_without_command=True)
@click.pass_context
def gather_cmd(ctx: click.Context) -> None:
    """Gather SurveyDesk-shaped specs from natural-language requirements (AOR-010).

    \b
    Flow:
      1. Paste requirements
      2. AI (or --stub) extracts an outline
      3. Confirm / edit
      4. Write specs/ like SurveyDesk

    \b
    Examples:
      aor gather run "Build a local survey desk with mobile operators"
      aor gather run --file requirements.md --edit
      aor gather apply --edit
      aor gather show
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@gather_cmd.command("run")
@click.argument("requirements", required=False)
@click.option("--file", "file_", type=click.Path(path_type=Path, exists=True), help="Requirements file.")
@click.option(
    "--root",
    type=click.Path(path_type=Path, file_okay=False),
    default=None,
    help="Project root (default: cwd).",
)
@click.option(
    "--profile",
    type=click.Choice(["surveydesk"]),
    default="surveydesk",
    show_default=True,
    help="Specs pack profile (SurveyDesk layout).",
)
@click.option("--stub", is_flag=True, help="Offline heuristic extract (no LLM).")
@click.option("--yes", "-y", is_flag=True, help="Skip confirm (still saves outline first).")
@click.option("--edit", is_flag=True, help="Open outline JSON in $EDITOR before confirm.")
@click.option("--force", is_flag=True, help="Overwrite existing generated files.")
@click.pass_context
def gather_run(
    ctx: click.Context,
    requirements: str | None,
    file_: Path | None,
    root: Path | None,
    profile: str,
    stub: bool,
    yes: bool,
    edit: bool,
    force: bool,
) -> None:
    """Extract an outline, confirm, then write the specs tree."""
    console = ctx.obj["console"]
    project = (root or Path.cwd()).resolve()
    text = _read_requirements(requirements, file_).strip()
    if not text or text.startswith("# Paste natural-language"):
        console.print("[red]No requirements provided.[/red]")
        raise SystemExit(2)

    cfg = LlmConfig.load()
    use_stub = stub or not cfg.configured
    if use_stub and not stub:
        console.print(
            "[yellow]No AOR_LLM_API_KEY[/yellow] — using stub extract. "
            f"Set key for {cfg.base_url} (DIV AI gateway token or other OpenAI-compatible key)."
        )

    console.print(f"[dim]Extracting outline[/dim] (profile={profile}, stub={use_stub}) …")
    outline = extract_outline(text, stub=use_stub)
    outline_path = _save_outline(project, outline)
    console.print(f"Outline saved: [bold]{outline_path}[/bold]")

    if edit:
        console.print("Opening outline in editor …")
        outline = _edit_outline(outline_path)
        _save_outline(project, outline)

    _print_outline(console, outline)
    console.print(
        Panel(
            "This will write a SurveyDesk-like tree under specs/ "
            "(product, requirements, domain, api, adr, acceptance, regeneration).",
            title="Confirm",
        )
    )
    if not yes and not click.confirm("Generate the full specs pack now?", default=False):
        console.print(
            "[yellow]Aborted.[/yellow] Edit the outline, then run:\n"
            f"  [bold]aor gather apply --root {project}[/bold]"
        )
        raise SystemExit(0)

    written = write_surveydesk_specs(project, outline, force=force)
    console.print(f"[green]Wrote[/green] {len(written)} file(s) under {project}")
    for path in written[:30]:
        console.print(f"  + {path.relative_to(project)}")
    if len(written) > 30:
        console.print(f"  … and {len(written) - 30} more")
    console.print("Next: review drafts, then approve contracts before implementation agents run.")


@gather_cmd.command("apply")
@click.option(
    "--root",
    type=click.Path(path_type=Path, file_okay=False),
    default=None,
    help="Project root (default: cwd).",
)
@click.option(
    "--outline",
    "outline_file",
    type=click.Path(path_type=Path, exists=True),
    default=None,
    help="Outline JSON (default: .aor/gather/outline.json).",
)
@click.option("--edit", is_flag=True, help="Open outline in $EDITOR before apply.")
@click.option("--yes", "-y", is_flag=True, help="Skip confirm.")
@click.option("--force", is_flag=True, help="Overwrite existing generated files.")
@click.pass_context
def gather_apply(
    ctx: click.Context,
    root: Path | None,
    outline_file: Path | None,
    edit: bool,
    yes: bool,
    force: bool,
) -> None:
    """Write specs from a saved/edited outline (no LLM call)."""
    console = ctx.obj["console"]
    project = (root or Path.cwd()).resolve()
    path = outline_file or _outline_path(project)
    if not path.is_file():
        console.print(f"[red]Outline not found:[/red] {path}")
        raise SystemExit(2)
    if edit:
        outline = _edit_outline(path)
        _save_outline(project, outline)
    else:
        outline = _load_outline(path)
    _print_outline(console, outline)
    if not yes and not click.confirm("Apply outline and write specs now?", default=True):
        console.print("[yellow]Aborted.[/yellow]")
        raise SystemExit(0)
    written = write_surveydesk_specs(project, outline, force=force)
    console.print(f"[green]Wrote[/green] {len(written)} file(s)")


@gather_cmd.command("show")
@click.option(
    "--root",
    type=click.Path(path_type=Path, file_okay=False),
    default=None,
)
@click.pass_context
def gather_show(ctx: click.Context, root: Path | None) -> None:
    """Show the saved gather outline JSON."""
    console = ctx.obj["console"]
    project = (root or Path.cwd()).resolve()
    path = _outline_path(project)
    if not path.is_file():
        console.print(f"[red]No outline at[/red] {path}")
        raise SystemExit(2)
    console.print(Syntax(path.read_text(encoding="utf-8"), "json", theme="monokai"))
