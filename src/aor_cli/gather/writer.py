"""Write a SurveyDesk-shaped specs tree from an outline."""

from __future__ import annotations

import re
from pathlib import Path

from aor_cli.gather.models import SpecOutline


def write_surveydesk_specs(root: Path, outline: SpecOutline, *, force: bool = False) -> list[Path]:
    """Create specs/product|requirements|domain|api|adr|acceptance|regeneration."""
    root = root.resolve()
    written: list[Path] = []

    def write(rel: str, content: str) -> None:
        path = root / rel
        if path.exists() and not force:
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content.rstrip() + "\n", encoding="utf-8")
        written.append(path)

    name = outline.product_name
    prefix = outline.requirement_prefix or "SD"

    write(
        "specs/README.md",
        f"# {name} specs\n\n"
        "Spec-Driven pack shaped like SurveyDesk.\n\n"
        "| Area | Path |\n"
        "| --- | --- |\n"
        "| Product | `product/` |\n"
        "| Requirements | `requirements/` |\n"
        "| Domain | `domain/` |\n"
        "| API | `api/openapi.yaml` |\n"
        "| ADRs | `adr/` |\n"
        "| Acceptance | `acceptance/` |\n"
        "| Regeneration | `regeneration/` |\n",
    )

    write(
        "specs/product/vision.md",
        f"# Product vision\n\n{outline.vision}\n\n"
        f"## Tagline\n\n{outline.tagline or name}\n\n"
        "## Non-goals (v1)\n\n"
        + "\n".join(f"- {g}" for g in (outline.non_goals or ["TBD"]))
        + "\n",
    )

    persona_blocks = []
    for p in outline.personas or []:
        persona_blocks.append(
            f"## {p.get('name', 'Persona')}\n\n"
            f"- **Role:** {p.get('role', '')}\n"
            f"- **Goals:** {p.get('goals', '')}\n"
        )
    write(
        "specs/product/personas.md",
        f"# Personas\n\n" + ("\n".join(persona_blocks) or "## Operator\n\nPrimary user.\n"),
    )
    write(
        "specs/product/brand.md",
        f"# Brand\n\n**Product name:** {name}\n\n{outline.brand_notes or 'English UI; define colors under brand/.'}\n",
    )
    journey = outline.demo_journey or ["Create", "Open", "Respond", "Results", "Close"]
    write(
        "specs/product/demo-journey.md",
        f"# Demo journey\n\n" + "\n".join(f"{i}. {step}" for i, step in enumerate(journey, 1)) + "\n",
    )

    for req in outline.requirements:
        slug = _slugify(req.title)
        write(
            f"specs/requirements/{req.id}-{slug}.md",
            f"# {req.id} {req.title}\n\n"
            f"## Requirement\n\n{req.shall}\n\n"
            f"## Notes\n\n{req.notes or '_None._'}\n\n"
            "## Acceptance criteria\n\n"
            "```gherkin\n"
            f"Scenario: {req.title}\n"
            f"  Given the system is running\n"
            f"  When the operator exercises {req.id}\n"
            f"  Then the SHALL statement holds\n"
            "```\n",
        )

    for domain in outline.domains:
        write(
            f"specs/domain/{_slugify(domain.name)}.md",
            f"# {domain.name}\n\n{domain.summary}\n",
        )

    for adr in outline.adrs:
        write(
            f"specs/adr/{adr.id}-{_slugify(adr.title)}.md",
            f"# {adr.id} {adr.title}\n\n## Decision\n\n{adr.decision}\n\n"
            "## Consequences\n\n- Specs remain authority over accidental code.\n",
        )

    write(
        "specs/api/openapi.yaml",
        f"openapi: 3.0.3\n"
        f"info:\n"
        f"  title: {name} Local API\n"
        f"  version: 0.1.0\n"
        f"  description: |\n"
        f"    {outline.api_summary}\n"
        f"servers:\n"
        f"  - url: http://127.0.0.1:8787\n"
        f"paths:\n"
        f"  /health:\n"
        f"    get:\n"
        f"      summary: Health check\n"
        f"      responses:\n"
        f"        \"200\":\n"
        f"          description: OK\n"
        f"          content:\n"
        f"            application/json:\n"
        f"              schema:\n"
        f"                type: object\n"
        f"                required: [ok]\n"
        f"                properties:\n"
        f"                  ok:\n"
        f"                    type: boolean\n",
    )

    for feat in outline.acceptance:
        scenarios = feat.scenarios or [f"Scenario: {feat.feature} works"]
        body_lines = [f"Feature: {feat.feature}", ""]
        for sc in scenarios:
            line = sc if sc.strip().lower().startswith("scenario") else f"Scenario: {sc}"
            body_lines.append(f"  {line}")
            body_lines.append("    Given the system is available")
            body_lines.append("    When the actor performs the action")
            body_lines.append("    Then the expected outcome is observed")
            body_lines.append("")
        write(f"specs/acceptance/{_slugify(feat.name)}.feature", "\n".join(body_lines))

    write(
        "specs/regeneration/README.md",
        f"# Regeneration — {name}\n\n"
        "If generated `apps/` trees are missing, rebuild from these specs "
        "(SurveyDesk-style parallel regen).\n\n"
        "Entry prompt: `prompts/REGENERATE.md`.\n",
    )
    tagline_or_vision = outline.tagline or (
        outline.vision.splitlines()[0] if outline.vision else name
    )
    write(
        "specs/regeneration/prompts/REGENERATE.md",
        f"# SINGLE PROMPT — execute all {name} specs\n\n"
        f"Implement **{name}** from Spec-Driven Development specs alone.\n\n"
        "## Mission\n\n"
        f"{tagline_or_vision}\n\n"
        "## Hard constraints\n\n"
        "1. Follow `specs/requirements/*` SHALL contracts.\n"
        "2. Match `specs/api/openapi.yaml` for HTTP shapes.\n"
        "3. English UI; product name **" + name + "** only.\n"
        "4. Prefer parallel agents with exclusive path ownership when regenerating apps.\n\n"
        "## Read first\n\n"
        "1. `specs/product/vision.md`\n"
        "2. `specs/requirements/`\n"
        "3. `specs/domain/`\n"
        "4. `specs/api/openapi.yaml`\n"
        "5. `specs/adr/`\n"
        "6. `specs/acceptance/*.feature`\n",
    )
    write(
        "specs/regeneration/orchestrate-parallel.md",
        f"# Parallel multi-agent execution — {name}\n\n"
        "Mirror the SurveyDesk regen waves: API/web first, then clients, then tests.\n"
        "Exclusive path ownership; do not invent a different product.\n",
    )

    # Keep AOR root product stubs in sync when present / always draft them.
    write(
        "product/vision.md",
        f"# Vision\n\n{outline.vision}\n",
    )
    write(
        "AGENTS.md",
        f"# AGENTS.md — {name}\n\n"
        "**Read this file first.** Specs under `specs/` are authority "
        "(SurveyDesk-shaped pack).\n\n"
        "## Authority\n\n"
        "1. `specs/product/`\n"
        "2. `specs/requirements/`\n"
        "3. `specs/domain/`, `specs/api/`, `specs/adr/`\n"
        "4. `specs/acceptance/`\n"
        "5. `specs/regeneration/`\n\n"
        "Do not invent a different product. Prefer `@specs/regeneration/prompts/REGENERATE.md` "
        "to rebuild missing apps.\n",
    )

    # Source capture for audit
    write(
        "specs/regeneration/source-requirements.md",
        "# Source requirements (natural language)\n\n"
        "Captured by `aor gather` before AI extract / confirm.\n\n"
        "```text\n"
        f"{outline.source_requirements.strip()}\n"
        "```\n",
    )

    return written


def _slugify(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug or "item"
