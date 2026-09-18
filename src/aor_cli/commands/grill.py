"""aor grill — Discovery AI Team (AOR-011)."""

from __future__ import annotations

from pathlib import Path

import click
from rich.panel import Panel
from rich.table import Table

from aor_cli.grill.personas import list_templates
from aor_cli.grill.session import GrillSession, load_session, new_session_id, save_session
from aor_cli.grill.stages import (
    GrillError,
    approve_architecture,
    approve_prd,
    approve_specs,
    mark_discovery_complete,
    request_architecture_change,
    request_prd_change,
    start_prd_stage,
)
from aor_cli.llm.config import LlmConfig


def _read_brief(brief: str | None, file: Path | None) -> str:
    if file is not None:
        return file.read_text(encoding="utf-8")
    if brief:
        return brief
    if not click.get_text_stream("stdin").isatty():
        return click.get_text_stream("stdin").read()
    return click.edit("# Paste product brief below, then save.\n\n") or ""


def _project(root: Path | None) -> Path:
    return (root or Path.cwd()).resolve()


def _print_session(console, session: GrillSession) -> None:
    console.print(
        Panel.fit(
            f"[bold]{session.product_name}[/bold]\n"
            f"session `{session.session_id}` · stage `[cyan]{session.stage}[/cyan]`\n"
            f"template `{session.architect_template}` · stub={session.stub}",
            title="aor grill (AOR-011)",
        )
    )
    table = Table(show_header=False)
    table.add_column("k")
    table.add_column("v")
    table.add_row("PRD approved", str(session.prd_approved))
    table.add_row("Architecture approved", str(session.architecture_approved))
    if session.pending_change_request:
        table.add_row(
            "Pending change",
            f"{session.pending_change_request.get('type')}: "
            f"{session.pending_change_request.get('reason')}",
        )
    if session.architect_questions:
        table.add_row("Architect observe", "\n".join(session.architect_questions[:5]))
    console.print(table)


def _next_hint(session: GrillSession) -> str:
    hints = {
        "GATE_PRD_APPROVE": "aor grill approve prd --root <project>",
        "GATE_ARCHITECTURE_APPROVE": "aor grill approve architecture --root <project>",
        "GATE_SPECS_APPROVE": (
            "Approve governing specs: `aor grill approve specs` "
            "(SurveyDesk pack) and/or `aor spec approve <ID>` (AOR bundles), "
            "then `aor grill complete`"
        ),
        "DISCOVERY_COMPLETE": "Discovery done. Delivery planner lifecycle is AOR-003 (still draft).",
        "STAGE_PRD": "PRD stage in progress — re-run or wait for GATE_PRD_APPROVE",
        "STAGE_ARCHITECTURE": "Architecture authoring — then approve architecture",
        "STAGE_CONTROL_PLANE": "Control-plane emission in progress",
    }
    return hints.get(session.stage, f"Stage: {session.stage}")


@click.group("grill", invoke_without_command=True)
@click.pass_context
def grill_cmd(ctx: click.Context) -> None:
    """Discovery AI Team: PRD → architecture → control-plane drafts (AOR-011).

    \b
    Flow:
      1. aor grill run \"…brief…\"     # PRD DRAFT + Architect observe
      2. aor grill approve prd         # human APPROVED → Architect authors
      3. aor grill approve architecture
      4. Planner emits specs/ DRAFTs   # then human APPROVED specs separately

    \b
    Alias: aor discover

    \b
    Examples:
      aor grill run --stub --file brief.md --root ./my-project
      aor grill resume --root ./my-project
      aor grill approve prd --root ./my-project
      aor grill request prd-change -m \"missing checkout scope\" --root ./my-project
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@grill_cmd.command("run")
@click.argument("brief", required=False)
@click.option("--file", "file_", type=click.Path(path_type=Path, exists=True), help="Brief file.")
@click.option("--root", type=click.Path(path_type=Path, file_okay=False), default=None)
@click.option(
    "--architect-template",
    "template",
    type=click.Choice(list_templates()),
    default="generic-web",
    show_default=True,
)
@click.option(
    "--owner",
    type=click.Choice(["human", "persona"]),
    default="persona",
    show_default=True,
    help="PO mode (persona seeded from brief; human answers later).",
)
@click.option("--stub", is_flag=True, help="Offline Discovery writers + stub gather extract.")
@click.pass_context
def grill_run(
    ctx: click.Context,
    brief: str | None,
    file_: Path | None,
    root: Path | None,
    template: str,
    owner: str,
    stub: bool,
) -> None:
    """Start a Discovery session: write PRD DRAFT (Architect observes only)."""
    console = ctx.obj["console"]
    project = _project(root)
    project.mkdir(parents=True, exist_ok=True)
    (project / "product").mkdir(parents=True, exist_ok=True)
    text = _read_brief(brief, file_).strip()
    if not text or text.startswith("# Paste product brief"):
        console.print("[red]No brief provided.[/red]")
        raise SystemExit(2)

    cfg = LlmConfig.load()
    use_stub = stub or not cfg.configured
    session = GrillSession(
        session_id=new_session_id(),
        root=str(project),
        stage="BRIEF",
        brief=text,
        product_name="Product",
        architect_template=template,
        owner_mode=owner,
        stub=use_stub,
    )
    save_session(project, session)
    try:
        session = start_prd_stage(project, session)
    except GrillError as exc:
        console.print(f"[red]{exc}[/red]")
        raise SystemExit(1) from exc

    _print_session(console, session)
    console.print(f"[green]Wrote DRAFT[/green] product/prd.md (no disk-write confirm — AOR-011).")
    console.print(f"[dim]Next:[/dim] {_next_hint(session)}")


@grill_cmd.command("resume")
@click.option("--root", type=click.Path(path_type=Path, file_okay=False), default=None)
@click.option("--session", "session_id", default=None, help="Session id (default: active).")
@click.pass_context
def grill_resume(ctx: click.Context, root: Path | None, session_id: str | None) -> None:
    """Show last checkpoint and next human action (persist/resume)."""
    console = ctx.obj["console"]
    project = _project(root)
    try:
        session = load_session(project, session_id)
    except FileNotFoundError as exc:
        console.print(f"[red]{exc}[/red]")
        raise SystemExit(1) from exc
    _print_session(console, session)
    console.print(f"[dim]Next:[/dim] {_next_hint(session)}")


@grill_cmd.command("status")
@click.option("--root", type=click.Path(path_type=Path, file_okay=False), default=None)
@click.option("--session", "session_id", default=None)
@click.pass_context
def grill_status(ctx: click.Context, root: Path | None, session_id: str | None) -> None:
    """Show active grill session status."""
    ctx.invoke(grill_resume, root=root, session_id=session_id)


@grill_cmd.group("approve")
def grill_approve() -> None:
    """Human DRAFT → APPROVED gates."""


@grill_approve.command("prd")
@click.option("--root", type=click.Path(path_type=Path, file_okay=False), default=None)
@click.option("--session", "session_id", default=None)
@click.option("--actor", default=None, help="Approver identity (default: AOR_APPROVER / user).")
@click.pass_context
def approve_prd_cmd(
    ctx: click.Context, root: Path | None, session_id: str | None, actor: str | None
) -> None:
    """Approve PRD; Architect then authors ARCHITECTURE.md DRAFT."""
    console = ctx.obj["console"]
    project = _project(root)
    try:
        session = load_session(project, session_id)
        session = approve_prd(project, session, actor=actor)
    except (FileNotFoundError, GrillError) as exc:
        console.print(f"[red]{exc}[/red]")
        raise SystemExit(1) from exc
    _print_session(console, session)
    console.print("[green]PRD APPROVED[/green] → architecture DRAFT written (+ approval evidence).")
    console.print(f"[dim]Next:[/dim] {_next_hint(session)}")


@grill_approve.command("architecture")
@click.option("--root", type=click.Path(path_type=Path, file_okay=False), default=None)
@click.option("--session", "session_id", default=None)
@click.option("--actor", default=None, help="Approver identity (default: AOR_APPROVER / user).")
@click.pass_context
def approve_architecture_cmd(
    ctx: click.Context, root: Path | None, session_id: str | None, actor: str | None
) -> None:
    """Approve architecture; Planner emits specs/ DRAFT pack."""
    console = ctx.obj["console"]
    project = _project(root)
    try:
        session = load_session(project, session_id)
        session = approve_architecture(project, session, actor=actor)
    except (FileNotFoundError, GrillError) as exc:
        console.print(f"[red]{exc}[/red]")
        raise SystemExit(1) from exc
    _print_session(console, session)
    console.print(
        "[green]Architecture APPROVED[/green] → specs/ DRAFT pack written (+ approval evidence)."
    )
    console.print(f"[dim]Next:[/dim] {_next_hint(session)}")


@grill_approve.command("specs")
@click.option("--root", type=click.Path(path_type=Path, file_okay=False), default=None)
@click.option("--session", "session_id", default=None)
@click.option("--actor", default=None, help="Approver identity (default: AOR_APPROVER / user).")
@click.pass_context
def approve_specs_cmd(
    ctx: click.Context, root: Path | None, session_id: str | None, actor: str | None
) -> None:
    """Approve governing specs pack (durable evidence); required before `grill complete`."""
    console = ctx.obj["console"]
    project = _project(root)
    try:
        session = load_session(project, session_id)
        session = approve_specs(project, session, actor=actor)
    except (FileNotFoundError, GrillError) as exc:
        console.print(f"[red]{exc}[/red]")
        raise SystemExit(1) from exc
    _print_session(console, session)
    console.print("[green]Specs pack APPROVED[/green] (approval evidence recorded).")
    console.print(f"[dim]Next:[/dim] {_next_hint(session)}")


@grill_cmd.group("request")
def grill_request() -> None:
    """Backward transitions (change requests)."""


@grill_request.command("prd-change")
@click.option("-m", "--reason", required=True, help="Why PRD must change.")
@click.option("--root", type=click.Path(path_type=Path, file_okay=False), default=None)
@click.option("--session", "session_id", default=None)
@click.pass_context
def request_prd_change_cmd(
    ctx: click.Context, reason: str, root: Path | None, session_id: str | None
) -> None:
    """REQUEST_PRD_CHANGE → return to STAGE_PRD."""
    console = ctx.obj["console"]
    project = _project(root)
    try:
        session = load_session(project, session_id)
        session = request_prd_change(project, session, reason)
    except (FileNotFoundError, GrillError) as exc:
        console.print(f"[red]{exc}[/red]")
        raise SystemExit(1) from exc
    _print_session(console, session)
    console.print("[yellow]Returned to PRD stage[/yellow] — re-approve PRD before architecture.")
    console.print(f"[dim]Next:[/dim] {_next_hint(session)}")


@grill_request.command("architecture-change")
@click.option("-m", "--reason", required=True, help="Why architecture must change.")
@click.option("--root", type=click.Path(path_type=Path, file_okay=False), default=None)
@click.option("--session", "session_id", default=None)
@click.pass_context
def request_architecture_change_cmd(
    ctx: click.Context, reason: str, root: Path | None, session_id: str | None
) -> None:
    """REQUEST_ARCHITECTURE_CHANGE → return to STAGE_ARCHITECTURE."""
    console = ctx.obj["console"]
    project = _project(root)
    try:
        session = load_session(project, session_id)
        session = request_architecture_change(project, session, reason)
    except (FileNotFoundError, GrillError) as exc:
        console.print(f"[red]{exc}[/red]")
        raise SystemExit(1) from exc
    _print_session(console, session)
    console.print("[yellow]Returned to architecture stage[/yellow] — re-approve architecture.")
    console.print(f"[dim]Next:[/dim] {_next_hint(session)}")


@grill_cmd.command("complete")
@click.option("--root", type=click.Path(path_type=Path, file_okay=False), default=None)
@click.option("--session", "session_id", default=None)
@click.pass_context
def grill_complete(ctx: click.Context, root: Path | None, session_id: str | None) -> None:
    """Mark discovery complete only after governing specs are APPROVED."""
    console = ctx.obj["console"]
    project = _project(root)
    try:
        session = load_session(project, session_id)
        session = mark_discovery_complete(project, session)
    except (FileNotFoundError, GrillError) as exc:
        console.print(f"[red]{exc}[/red]")
        raise SystemExit(1) from exc
    _print_session(console, session)
    console.print("[green]DISCOVERY_COMPLETE[/green]")


@grill_cmd.command("templates")
@click.pass_context
def grill_templates(ctx: click.Context) -> None:
    """List architect persona templates."""
    console = ctx.obj["console"]
    for tid in list_templates():
        console.print(f"- {tid}")
