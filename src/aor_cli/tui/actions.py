"""Shared operator actions used by the TUI (and safe to call without Click)."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from aor_cli.bootstrap.layout import scaffold_control_plane, validate_control_plane
from aor_cli.context.package import write_context_package
from aor_cli.project import ProjectMeta, default_prefix
from aor_cli.specs.store import approve_spec, create_spec, get_spec, list_specs, set_spec_status
from aor_cli.tasks.plan import plan_spec
from aor_cli.tasks.store import get_task, list_tasks, save_task
from aor_cli.workspace import aor_dir, find_control_plane


def init_project(path: Path, name: str) -> tuple[bool, str, Path]:
    root = path.expanduser().resolve()
    product = name.strip() or root.name.removesuffix("-control-plane") or root.name
    written = scaffold_control_plane(root, product, force=False)
    ProjectMeta.from_name(product).save(root)
    issues = validate_control_plane(root)
    if issues:
        detail = "; ".join(f"{i.path}: {i.message}" for i in issues)
        return False, f"Validation failed: {detail}", root
    extra = f" ({len(written)} new paths)" if written else " (already present)"
    return True, f"Project ready{extra}: {root}", root


def new_spec(root: Path, title: str, repo: str) -> tuple[bool, str]:
    title = title.strip()
    if not title:
        return False, "Spec title is required."
    meta = ProjectMeta.load(root)
    prefix = meta.prefix if meta else default_prefix(root.name)
    try:
        record = create_spec(
            root,
            title=title,
            prefix=prefix,
            repositories=[repo.strip()] if repo.strip() else ["app"],
        )
    except (OSError, ValueError, FileExistsError) as exc:
        return False, str(exc)
    return True, f"Created {record.id} (draft). Edit it, then Approve."


def human_approve(root: Path, spec_id: str) -> tuple[bool, str]:
    try:
        record = approve_spec(root, spec_id)
    except (FileNotFoundError, ValueError) as exc:
        return False, str(exc)
    return True, f"Approved {record.id}. You can Plan / Run it now."


def plan_and_message(root: Path, spec_id: str) -> tuple[bool, str]:
    try:
        spec, task = plan_spec(root, spec_id)
    except (FileNotFoundError, PermissionError) as exc:
        return False, str(exc)
    return True, f"Planned {task.id} for {spec.id} → {task.repository or 'app'}."


def run_and_message(root: Path, spec_id: str) -> tuple[bool, str]:
    spec = get_spec(root, spec_id)
    if spec is None:
        return False, f"Spec not found: {spec_id}"
    if spec.status.lower() in {"draft", "review"}:
        return False, f"{spec.id} is {spec.status.upper()} — a human must Approve first."
    try:
        if spec.status.lower() == "approved" or not any(t.spec_id == spec.id for t in list_tasks(root)):
            spec, task = plan_spec(root, spec.id)
        else:
            task = next(t for t in list_tasks(root) if t.spec_id == spec.id)
        context_path = write_context_package(root, spec, task)
        task.status = "running"
        task.attempts += 1
        save_task(root, task)
    except (FileNotFoundError, PermissionError) as exc:
        return False, str(exc)
    return True, f"Packaged {task.id}. Open {context_path} in Cursor / Claude / Codex."


def review_and_message(root: Path, spec_id: str, *, approve: bool, notes: str = "") -> tuple[bool, str]:
    matches = [t for t in list_tasks(root) if t.spec_id.upper() == spec_id.strip().upper()]
    task = matches[-1] if matches else get_task(root, spec_id)
    if task is None:
        return False, f"No local task for {spec_id}. Plan / Run first."
    record = {
        "task_id": task.id,
        "spec_id": task.spec_id,
        "decision": "approved" if approve else "rejected",
        "notes": notes,
        "at": datetime.now(UTC).isoformat(),
    }
    review_path = aor_dir(root) / "reviews" / f"{task.id}.json"
    review_path.parent.mkdir(parents=True, exist_ok=True)
    review_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    spec = get_spec(root, task.spec_id)
    if approve:
        task.status = "done"
        save_task(root, task)
        if spec is not None:
            set_spec_status(root, spec.id, "final_review")
        return True, f"Human approval recorded for {task.id} → FINAL_REVIEW ({review_path.name})."
    task.status = "failed"
    save_task(root, task)
    if spec is not None:
        set_spec_status(root, spec.id, "retry")
    return True, f"Rejection recorded for {task.id}. Spec moved to RETRY."


def snapshot(start: Path) -> dict:
    root = find_control_plane(start)
    if root is None:
        return {"root": None, "specs": [], "tasks": []}
    return {
        "root": root,
        "specs": list_specs(root),
        "tasks": list_tasks(root),
        "meta": ProjectMeta.load(root),
    }
