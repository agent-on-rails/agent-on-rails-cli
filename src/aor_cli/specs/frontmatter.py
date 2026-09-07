"""YAML frontmatter helpers for spec.md files."""

from __future__ import annotations

from typing import Any

import yaml

FRONTMATTER_RE_START = "---"


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    raw = text.lstrip("\ufeff")
    if not raw.startswith(FRONTMATTER_RE_START):
        return {}, text
    rest = raw[len(FRONTMATTER_RE_START) :].removeprefix("\n")
    end = rest.find(f"\n{FRONTMATTER_RE_START}")
    if end < 0:
        return {}, text
    yaml_block = rest[:end]
    body = rest[end + len(f"\n{FRONTMATTER_RE_START}") :].removeprefix("\n")
    data = yaml.safe_load(yaml_block) or {}
    if not isinstance(data, dict):
        return {}, text
    return data, body


def dump_frontmatter(data: dict[str, Any], body: str) -> str:
    dumped = yaml.safe_dump(data, sort_keys=False, allow_unicode=True).rstrip()
    body = body.lstrip("\n")
    return f"---\n{dumped}\n---\n\n{body}"
