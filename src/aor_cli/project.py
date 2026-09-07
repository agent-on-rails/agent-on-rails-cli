"""Local project metadata written by `aor init`."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from pathlib import Path

import yaml

from aor_cli.workspace import aor_dir


@dataclass
class ProjectMeta:
    name: str
    prefix: str

    @classmethod
    def from_name(cls, name: str) -> ProjectMeta:
        return cls(name=name, prefix=default_prefix(name))

    @classmethod
    def load(cls, root: Path) -> ProjectMeta | None:
        path = aor_dir(root) / "project.yaml"
        if not path.is_file():
            return None
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        name = str(data.get("name") or root.name)
        prefix = str(data.get("prefix") or default_prefix(name))
        return cls(name=name, prefix=prefix)

    def save(self, root: Path) -> Path:
        path = aor_dir(root) / "project.yaml"
        path.write_text(yaml.safe_dump(asdict(self), sort_keys=True), encoding="utf-8")
        return path


def default_prefix(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]", "", name)
    return (cleaned[:6] or "APP").upper()
