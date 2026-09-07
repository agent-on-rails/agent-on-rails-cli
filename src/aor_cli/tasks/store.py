"""Local task graph stored under .aor/tasks.json."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from aor_cli.workspace import aor_dir

TASKS_FILE = "tasks.json"


@dataclass
class TaskRecord:
    id: str
    spec_id: str
    title: str
    status: str
    description: str = ""
    repository: str = ""
    depends_on: list[str] = field(default_factory=list)
    model_tier: int = 1
    attempts: int = 0
    max_attempts: int = 3
    context_path: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TaskRecord:
        known = {f.name for f in cls.__dataclass_fields__.values()}  # type: ignore[attr-defined]
        return cls(**{k: v for k, v in data.items() if k in known})


def _path(root: Path) -> Path:
    return aor_dir(root) / TASKS_FILE


def list_tasks(root: Path) -> list[TaskRecord]:
    path = _path(root)
    if not path.is_file():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    raw = payload.get("tasks") if isinstance(payload, dict) else payload
    if not isinstance(raw, list):
        return []
    return [TaskRecord.from_dict(item) for item in raw if isinstance(item, dict)]


def get_task(root: Path, task_id: str) -> TaskRecord | None:
    wanted = task_id.strip().upper()
    for task in list_tasks(root):
        if task.id.upper() == wanted:
            return task
    return None


def save_task(root: Path, task: TaskRecord) -> TaskRecord:
    tasks = list_tasks(root)
    replaced = False
    for i, existing in enumerate(tasks):
        if existing.id == task.id:
            tasks[i] = task
            replaced = True
            break
    if not replaced:
        tasks.append(task)
    _write(root, tasks)
    return task


def next_task_id(root: Path) -> str:
    numbers = []
    for task in list_tasks(root):
        _, _, num = task.id.partition("-")
        if num.isdigit():
            numbers.append(int(num))
    nxt = (max(numbers) + 1) if numbers else 1
    return f"TASK-{nxt:03d}"


def _write(root: Path, tasks: list[TaskRecord]) -> None:
    path = _path(root)
    payload = {"tasks": [asdict(t) for t in tasks]}
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
