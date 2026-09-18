"""Discovery stage machine (AOR-011)."""

from __future__ import annotations

from pathlib import Path

from aor_cli.gather.extract import extract_outline
from aor_cli.gather.writer import write_surveydesk_specs
from aor_cli.grill.approval import (
    governing_specs_approved,
    write_approval_evidence,
)
from aor_cli.grill.personas import get_template
from aor_cli.grill.session import GrillSession, append_role_report, save_session
from aor_cli.grill.stub import (
    guess_product_name,
    observe_questions,
    write_architecture_draft,
    write_prd_draft,
)


class GrillError(RuntimeError):
    pass


def _mark_status_draft(text: str, reason: str) -> str:
    """Force DRAFT status line without wiping body content."""
    lines = text.splitlines()
    status_line = f"> **Status:** DRAFT (not APPROVED). {reason}"
    out: list[str] = []
    replaced = False
    for line in lines:
        if "**Status:**" in line and not replaced:
            out.append(status_line)
            replaced = True
        else:
            out.append(line)
    if not replaced:
        # Insert after title if possible
        if out and out[0].startswith("#"):
            out = [out[0], "", status_line, *out[1:]]
        else:
            out = [status_line, "", *out]
    return "\n".join(out).rstrip() + "\n"


def _mark_status_approved(text: str) -> str:
    lines = text.splitlines()
    status_line = "> **Status:** APPROVED (human)."
    out: list[str] = []
    replaced = False
    for line in lines:
        if "**Status:**" in line and not replaced:
            out.append(status_line)
            replaced = True
        else:
            out.append(line)
    if not replaced:
        if out and out[0].startswith("#"):
            out = [out[0], "", status_line, *out[1:]]
        else:
            out = [status_line, "", *out]
    return "\n".join(out).rstrip() + "\n"


def _append_change_request_note(text: str, reason: str) -> str:
    note = (
        "\n## Change request (pending re-approval)\n\n"
        f"{reason.strip()}\n\n"
        "_Human edits above this note are preserved. Re-approve after addressing the request._\n"
    )
    if "## Change request (pending re-approval)" in text:
        # Replace last change-request section body lightly: append new reason block
        return text.rstrip() + f"\n\n### Additional request\n\n{reason.strip()}\n"
    return text.rstrip() + "\n" + note


def start_prd_stage(project: Path, session: GrillSession, *, preserve_existing: bool = False) -> GrillSession:
    """STAGE_PRD: PM writes PRD DRAFT; Architect observes (questions only)."""
    get_template(session.architect_template)
    session.stage = "STAGE_PRD"
    session.product_name = guess_product_name(session.brief) or session.product_name
    session.architect_questions = observe_questions(session.brief, session.architect_template)
    prd_path = project / "product" / "prd.md"
    if preserve_existing and prd_path.is_file():
        reason = ""
        if session.pending_change_request:
            reason = str(session.pending_change_request.get("reason") or "change requested")
        text = prd_path.read_text(encoding="utf-8")
        text = _mark_status_draft(text, f"Returned for revision: {reason}" if reason else "Returned for revision.")
        if reason:
            text = _append_change_request_note(text, reason)
        prd_path.write_text(text, encoding="utf-8")
        summary = (
            f"Reopened existing PRD for {session.product_name} without regenerating from brief "
            f"(preserve human edits). Architect observe questions refreshed "
            f"({len(session.architect_questions)})."
        )
    else:
        prd_path = write_prd_draft(
            project,
            name=session.product_name,
            brief=session.brief,
            architect_questions=session.architect_questions,
        )
        summary = (
            f"Drafted PRD for {session.product_name}. "
            f"Architect observe raised {len(session.architect_questions)} question(s); "
            "no ARCHITECTURE.md authored."
        )
    rel = str(prd_path.relative_to(project))
    if rel not in session.artifact_paths:
        session.artifact_paths.append(rel)
    report = append_role_report(
        project,
        session,
        role="product-manager",
        summary=summary,
        artifacts=[rel],
    )
    session.artifact_paths.append(str(report.relative_to(project)))
    session.stage = "GATE_PRD_APPROVE"
    session.prd_approved = False
    save_session(project, session)
    return session


def approve_prd(
    project: Path, session: GrillSession, *, actor: str | None = None
) -> GrillSession:
    if session.stage not in ("GATE_PRD_APPROVE", "STAGE_PRD"):
        raise GrillError(f"Cannot approve PRD from stage {session.stage}")
    prd = project / "product" / "prd.md"
    if not prd.is_file():
        raise GrillError("product/prd.md missing — run grill PRD stage first")
    text = _mark_status_approved(prd.read_text(encoding="utf-8"))
    prd.write_text(text, encoding="utf-8")
    evidence = write_approval_evidence(
        project,
        session,
        artifact="prd",
        artifact_path=prd,
        actor=actor,
        note="GATE_PRD_APPROVE",
    )
    session.prd_approved = True
    session.pending_change_request = None
    session.stage = "STAGE_ARCHITECTURE"
    save_session(project, session)
    append_role_report(
        project,
        session,
        role="human-approver",
        summary=f"PRD APPROVED; evidence `{evidence.relative_to(project)}`.",
        artifacts=[str(prd.relative_to(project)), str(evidence.relative_to(project))],
    )
    return author_architecture(project, session, preserve_existing=False)


def author_architecture(
    project: Path, session: GrillSession, *, preserve_existing: bool = False
) -> GrillSession:
    if not session.prd_approved:
        raise GrillError("Architect must not author ARCHITECTURE.md before PRD APPROVED")
    if session.stage != "STAGE_ARCHITECTURE":
        raise GrillError(f"Cannot author architecture from stage {session.stage}")
    arch_path = project / "ARCHITECTURE.md"
    if preserve_existing and arch_path.is_file():
        reason = ""
        if session.pending_change_request:
            reason = str(session.pending_change_request.get("reason") or "change requested")
        text = arch_path.read_text(encoding="utf-8")
        text = _mark_status_draft(
            text, f"Returned for revision: {reason}" if reason else "Returned for revision."
        )
        if reason:
            text = _append_change_request_note(text, reason)
        arch_path.write_text(text, encoding="utf-8")
        summary = (
            f"Reopened existing ARCHITECTURE.md without regenerating from brief "
            f"(preserve human edits). Template remains `{session.architect_template}`."
        )
    else:
        arch_path = write_architecture_draft(
            project,
            name=session.product_name,
            brief=session.brief,
            template_id=session.architect_template,
        )
        summary = (
            f"Authored ARCHITECTURE.md using template `{session.architect_template}` "
            f"after PRD APPROVED."
        )
    rel = str(arch_path.relative_to(project))
    if rel not in session.artifact_paths:
        session.artifact_paths.append(rel)
    report = append_role_report(
        project,
        session,
        role="solution-architect",
        summary=summary,
        artifacts=[rel],
    )
    session.artifact_paths.append(str(report.relative_to(project)))
    session.stage = "GATE_ARCHITECTURE_APPROVE"
    session.architecture_approved = False
    save_session(project, session)
    return session


def approve_architecture(
    project: Path, session: GrillSession, *, actor: str | None = None
) -> GrillSession:
    if session.stage not in ("GATE_ARCHITECTURE_APPROVE", "STAGE_ARCHITECTURE"):
        raise GrillError(f"Cannot approve architecture from stage {session.stage}")
    arch = project / "ARCHITECTURE.md"
    if not arch.is_file():
        raise GrillError("ARCHITECTURE.md missing — approve PRD / author architecture first")
    text = _mark_status_approved(arch.read_text(encoding="utf-8"))
    arch.write_text(text, encoding="utf-8")
    evidence = write_approval_evidence(
        project,
        session,
        artifact="architecture",
        artifact_path=arch,
        actor=actor,
        note="GATE_ARCHITECTURE_APPROVE",
    )
    session.architecture_approved = True
    session.pending_change_request = None
    session.stage = "STAGE_CONTROL_PLANE"
    save_session(project, session)
    append_role_report(
        project,
        session,
        role="human-approver",
        summary=f"Architecture APPROVED; evidence `{evidence.relative_to(project)}`.",
        artifacts=[str(arch.relative_to(project)), str(evidence.relative_to(project))],
    )
    return emit_control_plane(project, session)


def emit_control_plane(project: Path, session: GrillSession) -> GrillSession:
    if not session.architecture_approved:
        raise GrillError("Planner must not emit pack before architecture APPROVED")
    session.stage = "STAGE_CONTROL_PLANE"
    enriched = (
        f"Build {session.product_name} from Discovery grill.\n\n"
        f"{session.brief.strip()}\n\n"
        f"See product/prd.md and ARCHITECTURE.md (APPROVED).\n"
    )
    outline = extract_outline(enriched, stub=session.stub)
    outline.product_name = session.product_name
    written = write_surveydesk_specs(project, outline, force=True)
    rels = [str(p.relative_to(project)) for p in written]
    session.artifact_paths.extend(r for r in rels if r not in session.artifact_paths)
    report = append_role_report(
        project,
        session,
        role="implementation-planner",
        summary=(
            f"Emitted SurveyDesk-shaped DRAFT pack ({len(written)} files). "
            "Governing specs remain draft until human APPROVED (AOR-003 delivery planner "
            "lifecycle not locked while AOR-003 is draft)."
        ),
        artifacts=rels[:20],
    )
    session.artifact_paths.append(str(report.relative_to(project)))
    session.stage = "GATE_SPECS_APPROVE"
    save_session(project, session)
    return session


def approve_specs(
    project: Path, session: GrillSession, *, actor: str | None = None
) -> GrillSession:
    """Durable approval of the governing specs pack (SurveyDesk or after AOR bundles)."""
    if session.stage not in ("GATE_SPECS_APPROVE", "DISCOVERY_COMPLETE"):
        raise GrillError(f"Cannot approve specs from stage {session.stage}")
    specs_dir = project / "specs"
    if not specs_dir.is_dir():
        raise GrillError("specs/ missing — approve architecture / emit pack first")
    evidence = write_approval_evidence(
        project,
        session,
        artifact="specs",
        artifact_path=specs_dir,
        actor=actor,
        note="GATE_SPECS_APPROVE (grill pack)",
    )
    append_role_report(
        project,
        session,
        role="human-approver",
        summary=f"Specs pack APPROVED; evidence `{evidence.relative_to(project)}`.",
        artifacts=["specs/", str(evidence.relative_to(project))],
    )
    save_session(project, session)
    return session


def request_prd_change(project: Path, session: GrillSession, reason: str) -> GrillSession:
    reason = reason.strip()
    if not reason:
        raise GrillError("Change request requires a reason")
    if session.stage not in (
        "STAGE_ARCHITECTURE",
        "GATE_ARCHITECTURE_APPROVE",
        "STAGE_CONTROL_PLANE",
        "GATE_SPECS_APPROVE",
    ):
        raise GrillError(f"REQUEST_PRD_CHANGE not valid from stage {session.stage}")
    session.pending_change_request = {"type": "REQUEST_PRD_CHANGE", "reason": reason}
    session.prd_approved = False
    session.architecture_approved = False
    arch = project / "ARCHITECTURE.md"
    if arch.is_file():
        text = arch.read_text(encoding="utf-8")
        text = _mark_status_draft(text, "Superseded pending PRD change.")
        arch.write_text(text, encoding="utf-8")
    session.stage = "STAGE_PRD"
    save_session(project, session)
    append_role_report(
        project,
        session,
        role="solution-architect",
        summary=f"REQUEST_PRD_CHANGE: {reason}",
        artifacts=["product/prd.md"],
    )
    # Preserve human PRD edits — do not regenerate from original brief
    return start_prd_stage(project, session, preserve_existing=True)


def request_architecture_change(project: Path, session: GrillSession, reason: str) -> GrillSession:
    reason = reason.strip()
    if not reason:
        raise GrillError("Change request requires a reason")
    if session.stage not in ("STAGE_CONTROL_PLANE", "GATE_SPECS_APPROVE", "DISCOVERY_COMPLETE"):
        raise GrillError(f"REQUEST_ARCHITECTURE_CHANGE not valid from stage {session.stage}")
    if not session.prd_approved:
        raise GrillError("PRD must remain APPROVED to request architecture change")
    session.pending_change_request = {"type": "REQUEST_ARCHITECTURE_CHANGE", "reason": reason}
    session.architecture_approved = False
    session.stage = "STAGE_ARCHITECTURE"
    save_session(project, session)
    append_role_report(
        project,
        session,
        role="implementation-planner",
        summary=f"REQUEST_ARCHITECTURE_CHANGE: {reason}",
        artifacts=["ARCHITECTURE.md"],
    )
    # Preserve human architecture edits — do not regenerate from brief
    return author_architecture(project, session, preserve_existing=True)


def mark_discovery_complete(project: Path, session: GrillSession) -> GrillSession:
    """Close discovery only when governing specs are actually APPROVED."""
    if session.stage not in ("GATE_SPECS_APPROVE", "DISCOVERY_COMPLETE"):
        raise GrillError(f"Cannot complete discovery from stage {session.stage}")
    if session.stage == "DISCOVERY_COMPLETE":
        return session
    ok, detail = governing_specs_approved(project, session)
    if not ok:
        raise GrillError(f"Cannot complete discovery: {detail}")
    session.stage = "DISCOVERY_COMPLETE"
    save_session(project, session)
    append_role_report(
        project,
        session,
        role="implementation-planner",
        summary=f"DISCOVERY_COMPLETE — {detail}",
        artifacts=["specs/"],
    )
    return session
