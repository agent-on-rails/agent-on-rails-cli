"""Minimal OpenAI-compatible Chat Completions client."""

from __future__ import annotations

from typing import Any

import httpx

from aor_cli.llm.config import LlmConfig


class LlmError(RuntimeError):
    pass


class ChatClient:
    def __init__(self, config: LlmConfig | None = None) -> None:
        self.config = config or LlmConfig.load()

    def chat(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> str:
        if not self.config.configured:
            raise LlmError(
                "No AOR_LLM_API_KEY set. Sign in at the AI portal or set a gateway token, "
                "or use --stub for offline extract."
            )
        url = f"{self.config.base_url.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }
        payload: dict[str, Any] = {
            "model": self.config.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        try:
            with httpx.Client(timeout=self.config.timeout_s) as client:
                response = client.post(url, headers=headers, json=payload)
        except httpx.HTTPError as exc:
            raise LlmError(f"LLM request failed: {exc}") from exc
        if response.status_code >= 400:
            raise LlmError(f"LLM HTTP {response.status_code}: {response.text[:500]}")
        data = response.json()
        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LlmError(f"Unexpected LLM response shape: {data!r}") from exc
        if not isinstance(content, str) or not content.strip():
            raise LlmError("LLM returned empty content")
        return content
