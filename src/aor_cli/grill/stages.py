"""Discovery stage machine (AOR-011)."""

from __future__ import annotations

from pathlib import Path

from aor_cli.gather.extract import extract_outline
from aor_cli.gather.writer import write_surveydesk_specs
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


def start_prd_stage(project: Path, session: GrillSession) -> GrillSession:
    """STAGE_PRD: PM writes PRD DRAFT; Architect observes (questions only)."""
    get_template(session.architect_template)
    session.stage = "STAGE_PRD"
    session.product_name = guess_product_name(session.brief)
    session.architect_questions = observe_questions(session.brief, session.architect_template)
    prd = write_prd_draft(
        project,
        name=session.product_name,
        brief=session.brief,
        architect_questions=session.architect_questions,
    )
    rel = str(prd.relative_to(project))
    if rel not in session.artifact_paths:
        session.artifact_paths.append(rel)
    report = append_role_report(
        project,
        session,
        role="product-manager",
        summary=(
            f"Drafted PRD for {session.product_name}. "
            f"Architect observe raised {len(session.architect_questions)} question(s); "
            "no ARCHITECTURE.md authored."
        ),
        artifacts=[rel],
    )
    session.artifact_paths.append(str(report.relative_to(project)))
    session.stage = "GATE_PRD_APPROVE"
    session.prd_approved = False
    save_session(project, session)
    return session


def approve_prd(project: Path, session: GrillSession) -> GrillSession:
    if session.stage not in ("GATE_PRD_APPROVE", "STAGE_PRD"):
        raise GrillError(f"Cannot approve PRD from stage {session.stage}")
    prd = project / "product" / "prd.md"
    if not prd.is_file():
        raise GrillError("product/prd.md missing — run grill PRD stage first")
    text = prd.read_text(encoding="utf-8")
    text = text.replace("**Status:** DRAFT (not APPROVED).", "**Status:** APPROVED (human).")
    if "**Status:** APPROVED" not in text:
        text = f"> **Status:** APPROVED (human).\n\n{text}"
    prd.write_text(text, encoding="utf-8")
    session.prd_approved = True
    session.pending_change_request = None
    session.stage = "STAGE_ARCHITECTURE"
    save_session(project, session)
    return author_architecture(project, session)


def author_architecture(project: Path, session: GrillSession) -> GrillSession:
    if not session.prd_approved:
        raise GrillError("Architect must not author ARCHITECTURE.md before PRD APPROVED")
    if session.stage != "STAGE_ARCHITECTURE":
        raise GrillError(f"Cannot author architecture from stage {session.stage}")
    arch = write_architecture_draft(
        project,
        name=session.product_name,
        brief=session.brief,
        template_id=session.architect_template,
    )
    rel = str(arch.relative_to(project))
    if rel not in session.artifact_paths:
        session.artifact_paths.append(rel)
    report = append_role_report(
        project,
        session,
        role="solution-architect",
        summary=(
            f"Authored ARCHITECTURE.md using template `{session.architect_template}` "
            f"after PRD APPROVED."
        ),
        artifacts=[rel],
    )
    session.artifact_paths.append(str(report.relative_to(project)))
    session.stage = "GATE_ARCHITECTURE_APPROVE"
    session.architecture_approved = False
    save_session(project, session)
    return session


def approve_architecture(project: Path, session: GrillSession) -> GrillSession:
    if session.stage not in ("GATE_ARCHITECTURE_APPROVE", "STAGE_ARCHITECTURE"):
        raise GrillError(f"Cannot approve architecture from stage {session.stage}")
    arch = project / "ARCHITECTURE.md"
    if not arch.is_file():
        raise GrillError("ARCHITECTURE.md missing — approve PRD / author architecture first")
    text = arch.read_text(encoding="utf-8")
    text = text.replace("**Status:** DRAFT (not APPROVED).", "**Status:** APPROVED (human).")
    if "**Status:** APPROVED" not in text:
        text = f"> **Status:** APPROVED (human).\n\n{text}"
    arch.write_text(text, encoding="utf-8")
    session.architecture_approved = True
    session.pending_change_request = None
    session.stage = "STAGE_CONTROL_PLANE"
    save_session(project, session)
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
    # Supersede: mark architecture back to draft if present
    arch = project / "ARCHITECTURE.md"
    if arch.is_file():
        text = arch.read_text(encoding="utf-8")
        text = text.replace("**Status:** APPROVED (human).", "**Status:** DRAFT (superseded; PRD change).")
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
    return start_prd_stage(project, session)


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
    arch = project / "ARCHITECTURE.md"
    if arch.is_file():
        text = arch.read_text(encoding="utf-8")
        text = text.replace("**Status:** APPROVED (human).", "**Status:** DRAFT (superseded; architecture change).")
        if "**Status:** DRAFT" not in text:
            text = text.replace("**Status:** APPROVED", "**Status:** DRAFT (superseded)")
        arch.write_text(text, encoding="utf-8")
    session.stage = "STAGE_ARCHITECTURE"
    save_session(project, session)
    append_role_report(
        project,
        session,
        role="implementation-planner",
        summary=f"REQUEST_ARCHITECTURE_CHANGE: {reason}",
        artifacts=["ARCHITECTURE.md"],
    )
    return author_architecture(project, session)


def mark_discovery_complete(project: Path, session: GrillSession) -> GrillSession:
    """Optional explicit close after specs APPROVED externally."""
    if session.stage not in ("GATE_SPECS_APPROVE", "DISCOVERY_COMPLETE"):
        raise GrillError(f"Cannot complete discovery from stage {session.stage}")
    session.stage = "DISCOVERY_COMPLETE"
    save_session(project, session)
    return session
