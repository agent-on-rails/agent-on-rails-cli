"""Discovery AI Team session state (AOR-011)."""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STAGES = (
    "BRIEF",
    "STAGE_PRD",
    "GATE_PRD_APPROVE",
    "STAGE_ARCHITECTURE",
    "GATE_ARCHITECTURE_APPROVE",
    "STAGE_CONTROL_PLANE",
    "GATE_SPECS_APPROVE",
    "DISCOVERY_COMPLETE",
)

ACTIVE_POINTER = "active.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@dataclass
class GrillSession:
    session_id: str
    root: str
    stage: str
    brief: str
    product_name: str
    architect_template: str = "generic-web"
    owner_mode: str = "persona"  # human | persona
    stub: bool = True
    prd_approved: bool = False
    architecture_approved: bool = False
    pending_change_request: dict[str, Any] | None = None
    architect_questions: list[str] = field(default_factory=list)
    artifact_paths: list[str] = field(default_factory=list)
    role_reports: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=_utc_now)
    updated_at: str = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GrillSession:
        return cls(
            session_id=data["session_id"],
            root=data["root"],
            stage=data["stage"],
            brief=data.get("brief", ""),
            product_name=data.get("product_name", "Product"),
            architect_template=data.get("architect_template", "generic-web"),
            owner_mode=data.get("owner_mode", "persona"),
            stub=bool(data.get("stub", True)),
            prd_approved=bool(data.get("prd_approved", False)),
            architecture_approved=bool(data.get("architecture_approved", False)),
            pending_change_request=data.get("pending_change_request"),
            architect_questions=list(data.get("architect_questions") or []),
            artifact_paths=list(data.get("artifact_paths") or []),
            role_reports=list(data.get("role_reports") or []),
            created_at=data.get("created_at") or _utc_now(),
            updated_at=data.get("updated_at") or _utc_now(),
        )


def grill_root(project: Path) -> Path:
    path = project / ".aor" / "grill"
    path.mkdir(parents=True, exist_ok=True)
    return path


def session_dir(project: Path, session_id: str) -> Path:
    path = grill_root(project) / session_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def new_session_id() -> str:
    return uuid.uuid4().hex[:12]


def save_session(project: Path, session: GrillSession) -> Path:
    session.updated_at = _utc_now()
    session.root = str(project.resolve())
    d = session_dir(project, session.session_id)
    path = d / "session.json"
    path.write_text(json.dumps(session.to_dict(), indent=2) + "\n", encoding="utf-8")
    pointer = grill_root(project) / ACTIVE_POINTER
    pointer.write_text(
        json.dumps({"session_id": session.session_id, "updated_at": session.updated_at}, indent=2)
        + "\n",
        encoding="utf-8",
    )
    return path


def load_session(project: Path, session_id: str | None = None) -> GrillSession:
    sid = session_id
    if not sid:
        pointer = grill_root(project) / ACTIVE_POINTER
        if not pointer.is_file():
            raise FileNotFoundError("No active grill session. Pass --session or run `aor grill run`.")
        sid = json.loads(pointer.read_text(encoding="utf-8"))["session_id"]
    path = session_dir(project, sid) / "session.json"
    if not path.is_file():
        raise FileNotFoundError(f"Grill session not found: {sid}")
    return GrillSession.from_dict(json.loads(path.read_text(encoding="utf-8")))


def append_role_report(project: Path, session: GrillSession, role: str, summary: str, artifacts: list[str]) -> Path:
    d = session_dir(project, session.session_id)
    reports = d / "role-reports"
    reports.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = reports / f"{ts}-{role}.md"
    body = (
        f"# Role report — {role}\n\n"
        f"- **session:** `{session.session_id}`\n"
        f"- **stage:** `{session.stage}`\n"
        f"- **ended_at:** {_utc_now()}\n"
        f"- **outcome:** success\n\n"
        f"## Summary\n\n{summary.strip()}\n\n"
        f"## Artifacts\n\n"
        + ("\n".join(f"- `{a}`" for a in artifacts) if artifacts else "- (none)\n")
        + "\n"
    )
    path.write_text(body, encoding="utf-8")
    rel = str(path.relative_to(project))
    session.role_reports.append(rel)
    return path
