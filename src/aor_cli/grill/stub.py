"""Stub Discovery writers (offline / no LLM) for aor grill."""

from __future__ import annotations

import re
from pathlib import Path

from aor_cli.grill.personas import get_template


def guess_product_name(brief: str) -> str:
    m = re.search(r"Product name:\s*\*?\*?([^*\n]+)\*?\*?", brief, re.I)
    if m:
        return m.group(1).strip()
    m = re.search(r"Build (?:a |an )?([A-Z][A-Za-z0-9]+)", brief)
    if m:
        return m.group(1).strip()
    m = re.search(r"called\s+([A-Z][A-Za-z0-9]+)", brief)
    if m:
        return m.group(1).strip()
    return "Product"


def write_prd_draft(root: Path, *, name: str, brief: str, architect_questions: list[str]) -> Path:
    path = root / "product" / "prd.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    questions = "\n".join(f"- {q}" for q in architect_questions) or "- (none raised)"
    path.write_text(
        f"""# PRD — {name}

> **Status:** DRAFT (not APPROVED). Written by Discovery Product Manager (`aor grill`).

## Problem

Operator brief describes **{name}**. Discovery captured the intent below for human approval
before architecture authorship.

## Product

**{name}** — see source brief.

## Architect observe questions (not architecture)

{questions}

## Source brief

```text
{brief.strip()}
```

## Open questions

- Confirm non-goals and success metrics with the Product Owner.
- Confirm which constraints are binding for v1.
""",
        encoding="utf-8",
    )
    return path


def write_architecture_draft(
    root: Path,
    *,
    name: str,
    brief: str,
    template_id: str,
) -> Path:
    tmpl = get_template(template_id)
    path = root / "ARCHITECTURE.md"
    path.write_text(
        f"""# Architecture — {name}

> **Status:** DRAFT (not APPROVED). Written by Discovery Solution Architect (`aor grill`).
> Template: `{tmpl["id"]}` — {tmpl["bias"]}

## Summary

{tmpl["author_hint"]}

## Components (draft)

| Component | Responsibility |
| --- | --- |
| Client / UI | Operator or end-user surface |
| API / workers | Business logic and integrations |
| Data store | Persistence for v1 |
| Secrets | Env / secret manager only — never in control plane |

## Key decisions (draft ADRs recommended)

1. Deploy / runtime posture per template bias.
2. Provider-neutral inference or integrations where applicable (ADR-003 spirit).
3. Eval / acceptance before release when the product includes quality gates.

## Trace to brief

```text
{brief.strip()[:1500]}
```

## Out of scope

Application source under `apps/`; coding agents implement only after human APPROVED specs.
""",
        encoding="utf-8",
    )
    return path


def observe_questions(brief: str, template_id: str) -> list[str]:
    tmpl = get_template(template_id)
    base = [
        f"[{tmpl['id']}] {tmpl['observe_hint']}",
        "Which non-functional constraints (latency, offline, compliance) are binding for v1?",
    ]
    lower = brief.lower()
    if "payment" in lower or "midtrans" in lower or "checkout" in lower:
        base.append("How should payment webhooks authenticate and stay idempotent?")
    if "chat" in lower or "rag" in lower or "knowledge" in lower:
        base.append("What happens when retrieval confidence is low — abstain or escalate?")
    return base
