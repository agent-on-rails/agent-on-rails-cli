"""Control-plane directory contract (AOR-001 / guides/using-the-control-plane.md)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REQUIRED_DIRS = (
    "product",
    "adr",
    "policies",
    "specs",
    "plans",
)

REQUIRED_FILES = (
    "AGENTS.md",
    "README.md",
)

AGENTS_TEMPLATE = """# AGENTS.md

**Read this file first.** This repository is the **authority plane** for this product.

## Mission

Define *what* should be built and *how success is proven*. Do not implement production application logic here.

## Authority hierarchy (highest first)

1. `product/`
2. `adr/`
3. `policies/`
4. `specs/**`
5. `plans/`
6. Sibling application repositories

## Specs

Each spec lives under `specs/<PREFIX>-NNN-slug/` with:

- `spec.md`
- `acceptance.md`
- `evidence.md`

Implementation agents are blocked until governing specs reach `APPROVED`.
"""

README_TEMPLATE = """# {name}

Authority repository for **{name}**, governed by [Agent On Rails](https://agent-on-rails.suherman.net).

> Docs define intent. Specs define the contract. Agent On Rails governs execution. Agents implement. Evidence proves completion.

## Layout

```text
product/     Vision, proposition, principles, PRD drafts
adr/         Architecture Decision Records
policies/    Human approval, security, escalation, evidence
specs/       Spec contracts + acceptance + evidence templates
plans/       MVP / milestones / backlog
schemas/     Optional JSON schemas (or reuse AOR schemas)
```

Bootstrap with [`aor init`](https://github.com/agent-on-rails/agent-on-rails-cli).
"""

PRODUCT_VISION = """# Vision

{name} — product vision (draft).

Replace this with the problem, product, and north-star outcome.
"""

PRODUCT_PRINCIPLES = """# Principles

1. Docs-first — no unbounded coding agents without an approved contract.
2. Specs are authority — code loses when it disagrees with an approved spec.
3. Evidence before done — agents cannot self-certify completion.
"""

PRODUCT_PROPOSITION = """# Proposition

{name} — product proposition (draft).

Who it is for, what job it does, and what it is not.
"""

GITIGNORE = """# Agent On Rails local runtime
.aor/packages/
.aor/reviews/
.venv/
__pycache__/
*.pyc
"""

PLANS_MVP = """# MVP

## Goal

Prove the core delivery loop for {name} under Agent On Rails.

## In scope

- Control-plane docs + first approved specs
- Engine-planned tasks → agent → PR → review → evidence → human final review

## Out of scope

- Full SaaS multi-tenant
- Proprietary coding agent
"""

POLICIES_HUMAN = """# Human approval

Specs must reach `APPROVED` via human review before implementation agents run.

Final merge / production promotion requires human `FINAL_REVIEW` after evidence is attached.
"""


@dataclass(frozen=True)
class ValidationIssue:
    path: str
    message: str


def validate_control_plane(root: Path) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if not root.exists():
        return [ValidationIssue(str(root), "path does not exist")]
    if not root.is_dir():
        return [ValidationIssue(str(root), "not a directory")]

    for name in REQUIRED_FILES:
        if not (root / name).is_file():
            issues.append(ValidationIssue(name, "required file missing"))
    for name in REQUIRED_DIRS:
        if not (root / name).is_dir():
            issues.append(ValidationIssue(name + "/", "required directory missing"))

    specs = root / "specs"
    if specs.is_dir():
        children = [p for p in specs.iterdir() if p.is_dir() and not p.name.startswith(".")]
        for child in children:
            for required in ("spec.md", "acceptance.md", "evidence.md"):
                if not (child / required).is_file():
                    issues.append(
                        ValidationIssue(
                            f"specs/{child.name}/{required}",
                            "spec bundle incomplete",
                        )
                    )
    return issues


def scaffold_control_plane(root: Path, name: str, *, force: bool = False) -> list[Path]:
    """Create minimum control-plane layout. Returns paths written."""
    written: list[Path] = []
    root.mkdir(parents=True, exist_ok=True)

    def write(rel: str, content: str) -> None:
        path = root / rel
        if path.exists() and not force:
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        written.append(path)

    write("AGENTS.md", AGENTS_TEMPLATE)
    write("README.md", README_TEMPLATE.format(name=name))
    write("product/vision.md", PRODUCT_VISION.format(name=name))
    write("product/principles.md", PRODUCT_PRINCIPLES)
    write("product/proposition.md", PRODUCT_PROPOSITION.format(name=name))
    write("plans/MVP.md", PLANS_MVP.format(name=name))
    write("policies/human-approval.md", POLICIES_HUMAN)
    write(".gitignore", GITIGNORE)
    write("adr/.gitkeep", "")
    write("specs/.gitkeep", "")
    return written
