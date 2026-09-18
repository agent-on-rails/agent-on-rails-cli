"""Durable approval evidence for Discovery gates (human-approval policy)."""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from aor_cli.grill.session import GrillSession, session_dir
from aor_cli.specs.store import IMPLEMENTABLE, list_specs


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def default_actor() -> str:
    for key in ("AOR_APPROVER", "GIT_AUTHOR_NAME", "USER", "LOGNAME"):
        val = os.environ.get(key, "").strip()
        if val:
            return val
    return "unknown"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def sha256_tree(root: Path) -> str:
    """Content hash of all files under root (sorted relative paths)."""
    if not root.exists():
        raise FileNotFoundError(str(root))
    h = hashlib.sha256()
    if root.is_file():
        h.update(root.read_bytes())
        return h.hexdigest()
    files: list[Path] = []
    for path in root.rglob("*"):
        if path.is_file() and ".git" not in path.parts:
            files.append(path)
    for path in sorted(files, key=lambda p: str(p.relative_to(root)).replace("\\", "/")):
        rel = str(path.relative_to(root)).replace("\\", "/")
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        h.update(path.read_bytes())
        h.update(b"\0")
    return h.hexdigest()


def approvals_dir(project: Path, session: GrillSession) -> Path:
    path = session_dir(project, session.session_id) / "approvals"
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_approval_evidence(
    project: Path,
    session: GrillSession,
    *,
    artifact: str,
    artifact_path: Path,
    actor: str | None = None,
    note: str = "",
) -> Path:
    """Record actor + timestamp + artifact SHA (policies/human-approval.md)."""
    actor_name = (actor or default_actor()).strip() or "unknown"
    if artifact_path.is_dir():
        digest = sha256_tree(artifact_path)
        kind = "tree"
    else:
        digest = sha256_file(artifact_path)
        kind = "file"
    payload: dict[str, Any] = {
        "schema_version": "1",
        "kind": "grill-approval",
        "session_id": session.session_id,
        "artifact": artifact,
        "artifact_path": str(artifact_path.relative_to(project))
        if artifact_path.is_relative_to(project)
        else str(artifact_path),
        "artifact_kind": kind,
        "artifact_sha256": digest,
        "actor": actor_name,
        "timestamp": _utc_now(),
        "note": note,
    }
    out = approvals_dir(project, session) / f"{artifact}.json"
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    rel = str(out.relative_to(project))
    if rel not in session.artifact_paths:
        session.artifact_paths.append(rel)
    return out


def load_approval(project: Path, session: GrillSession, artifact: str) -> dict[str, Any] | None:
    path = approvals_dir(project, session) / f"{artifact}.json"
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def aor_bundle_specs_approved(project: Path) -> bool | None:
    """
    Return True/False when AOR-style specs/<ID>-slug/spec.md bundles exist.
    Return None when only SurveyDesk-shaped trees (no approve-able bundles).
    """
    records = list_specs(project)
    if not records:
        return None
    approved_or_later = IMPLEMENTABLE | {"done", "approved"}
    return all(r.status.lower() in approved_or_later for r in records)


def governing_specs_approved(project: Path, session: GrillSession) -> tuple[bool, str]:
    """
    Specs are approved when:
    - every AOR-style bundle is approved+, OR
    - (no AOR bundles) durable grill pack approval evidence exists for artifact \"specs\".
    """
    bundles = aor_bundle_specs_approved(project)
    if bundles is True:
        return True, "all AOR-style spec bundles are approved+"
    if bundles is False:
        pending = [
            f"{r.id}={r.status}"
            for r in list_specs(project)
            if r.status.lower() not in (IMPLEMENTABLE | {"done", "approved"})
        ]
        return False, f"spec bundles not APPROVED yet: {', '.join(pending)}"
    evidence = load_approval(project, session, "specs")
    if evidence and evidence.get("artifact_sha256"):
        return True, f"grill pack approval by {evidence.get('actor')} at {evidence.get('timestamp')}"
    return (
        False,
        "no AOR-style APPROVED specs and no grill pack approval — "
        "run `aor grill approve specs` or `aor spec approve <ID>`",
    )
