"""Turn an approved spec into a local task (AOR-003 local slice)."""

from __future__ import annotations

from pathlib import Path

from aor_cli.specs.store import SpecRecord, get_spec, set_spec_status
from aor_cli.tasks.store import TaskRecord, list_tasks, next_task_id, save_task


def plan_spec(root: Path, spec_id: str) -> tuple[SpecRecord, TaskRecord]:
    spec = get_spec(root, spec_id)
    if spec is None:
        raise FileNotFoundError(f"spec not found: {spec_id}")
    if spec.status.lower() in {"draft", "review"}:
        raise PermissionError(
            f"{spec.id} is {spec.status.upper()} — a human must `aor spec approve {spec.id}` "
            "before Agent On Rails will plan or run implementation."
        )
    existing = [t for t in list_tasks(root) if t.spec_id == spec.id]
    if existing:
        planned = spec
        if spec.status.lower() == "approved":
            planned = set_spec_status(root, spec.id, "ready")
        return planned, existing[0]

    repo = spec.repositories[0] if spec.repositories else ""
    task = TaskRecord(
        id=next_task_id(root),
        spec_id=spec.id,
        title=f"Implement {spec.id}: {spec.title}",
        status="ready",
        description=(
            f"Bounded implementation of {spec.id}. "
            "Do not treat this as an unbounded 'build the product' prompt."
        ),
        repository=repo,
        model_tier=1,
    )
    save_task(root, task)
    planned = set_spec_status(root, spec.id, "ready")
    return planned, task
