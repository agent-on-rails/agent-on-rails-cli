"""OpenAI-compatible LLM settings (ADR-003 provider-neutral)."""

from __future__ import annotations

import os
from dataclasses import asdict, dataclass
from pathlib import Path

import yaml

CONFIG_DIR = Path.home() / ".config" / "agent-on-rails"
CONFIG_PATH = CONFIG_DIR / "llm.yaml"

# Default points at the DIV AI OpenAI-compatible gateway; override freely.
DEFAULT_BASE_URL = "https://ai.dentalimplantsandveneers.com.au/v1"
DEFAULT_MODEL = "writer"


@dataclass
class LlmConfig:
    base_url: str = DEFAULT_BASE_URL
    api_key: str = ""
    model: str = DEFAULT_MODEL
    timeout_s: float = 180.0

    @classmethod
    def load(cls, path: Path | None = None) -> LlmConfig:
        cfg = cls()
        cfg_path = path or CONFIG_PATH
        if cfg_path.is_file():
            data = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
            known = {f.name for f in cls.__dataclass_fields__.values()}  # type: ignore[attr-defined]
            for key, value in data.items():
                if key in known and value is not None:
                    setattr(cfg, key, value)
        # Env wins over file (secrets + CI).
        cfg.base_url = os.environ.get("AOR_LLM_BASE_URL", cfg.base_url).rstrip("/")
        cfg.api_key = os.environ.get("AOR_LLM_API_KEY", cfg.api_key)
        cfg.model = os.environ.get("AOR_LLM_MODEL", cfg.model)
        if os.environ.get("AOR_LLM_TIMEOUT"):
            cfg.timeout_s = float(os.environ["AOR_LLM_TIMEOUT"])
        return cfg

    def save(self, path: Path | None = None) -> Path:
        cfg_path = path or CONFIG_PATH
        cfg_path.parent.mkdir(parents=True, exist_ok=True)
        payload = asdict(self)
        # Never write empty key from env bleed if operator clears it intentionally.
        cfg_path.write_text(yaml.safe_dump(payload, sort_keys=True), encoding="utf-8")
        return cfg_path

    @property
    def configured(self) -> bool:
        return bool(self.api_key.strip())
