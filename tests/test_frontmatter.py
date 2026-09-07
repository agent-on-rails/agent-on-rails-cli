from __future__ import annotations

from aor_cli.specs.frontmatter import dump_frontmatter, split_frontmatter


def test_roundtrip() -> None:
    original = """---
id: DEMO-001
title: Checkout
status: draft
intent: >
  Keep totals honest.
---

# Body

Hello
"""
    data, body = split_frontmatter(original)
    assert data["id"] == "DEMO-001"
    assert "Keep totals honest" in str(data["intent"])
    assert body.lstrip().startswith("# Body")
    rewritten = dump_frontmatter(data, body)
    again, body2 = split_frontmatter(rewritten)
    assert again["id"] == "DEMO-001"
    assert "# Body" in body2
