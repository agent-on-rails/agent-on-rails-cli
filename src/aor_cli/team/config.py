"""Local AI Team configuration (implementor / reviewer + models)."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

import yaml

CONFIG_DIR = Path.home() / ".config" / "agent-on-rails"
CONFIG_PATH = CONFIG_DIR / "team.yaml"


@dataclass
class TeamConfig:
    implementor: str = "codex"
    reviewer: str = "claude"
    default_model: str = "cheap"
    escalate_model: str = "frontier"
    project: str | None = None

    @classmethod
    def load(cls, path: Path | None = None) -> TeamConfig:
        cfg_path = path or CONFIG_PATH
        if not cfg_path.is_file():
            return cls()
        data = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
        known = {f.name for f in cls.__dataclass_fields__.values()}  # type: ignore[attr-defined]
        return cls(**{k: v for k, v in data.items() if k in known})

    def save(self, path: Path | None = None) -> Path:
        cfg_path = path or CONFIG_PATH
        cfg_path.parent.mkdir(parents=True, exist_ok=True)
        cfg_path.write_text(yaml.safe_dump(asdict(self), sort_keys=True), encoding="utf-8")
        return cfg_path
