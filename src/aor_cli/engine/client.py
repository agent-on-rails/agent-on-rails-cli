"""Engine HTTP client with honest local stub when AOR_ENGINE_URL is unset."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx


@dataclass
class EngineClient:
    base_url: str | None = None
    timeout: float = 30.0

    @property
    def stubbed(self) -> bool:
        return not self.base_url

    def health(self) -> dict[str, Any]:
        if self.stubbed:
            return {"ok": True, "mode": "stub", "message": "engine not configured"}
        with httpx.Client(base_url=self.base_url, timeout=self.timeout) as client:
            r = client.get("/health")
            r.raise_for_status()
            return r.json()

    def run_task(self, task_id: str) -> dict[str, Any]:
        if self.stubbed:
            return {
                "ok": False,
                "mode": "stub",
                "task_id": task_id,
                "state": "BLOCKED",
                "message": "Set AOR_ENGINE_URL to run tasks against the engine.",
            }
        with httpx.Client(base_url=self.base_url, timeout=self.timeout) as client:
            r = client.post(f"/v1/tasks/{task_id}/run")
            r.raise_for_status()
            return r.json()

    def task_status(self, task_id: str) -> dict[str, Any]:
        if self.stubbed:
            return {
                "ok": True,
                "mode": "stub",
                "task_id": task_id,
                "state": "UNKNOWN",
                "message": "stub status — wire engine for live state",
            }
        with httpx.Client(base_url=self.base_url, timeout=self.timeout) as client:
            r = client.get(f"/v1/tasks/{task_id}")
            r.raise_for_status()
            return r.json()
