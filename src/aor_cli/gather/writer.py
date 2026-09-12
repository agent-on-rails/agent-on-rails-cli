"""Write a SurveyDesk-shaped specs tree from an outline."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

from aor_cli.gather.canon import looks_like_surveydesk
from aor_cli.gather.models import SpecOutline

TEMPLATE_ROOT = Path(__file__).parent / "templates" / "surveydesk"


def write_surveydesk_specs(root: Path, outline: SpecOutline, *, force: bool = False) -> list[Path]:
    """Create specs/product|requirements|domain|api|adr|acceptance|regeneration."""
    root = root.resolve()
    if _use_reference_pack(outline):
        return _write_reference_pack(root, outline, force=force)
    return _write_generic(root, outline, force=force)


def _use_reference_pack(outline: SpecOutline) -> bool:
    name = re.sub(r"[\s_]+", "", outline.product_name).lower()
    if name not in {"surveydesk", "survey-desk"}:
        return False
    blob = f"{outline.product_name}\n{outline.tagline}\n{outline.vision}\n{outline.source_requirements}"
    return looks_like_surveydesk(blob)


def _write_reference_pack(root: Path, outline: SpecOutline, *, force: bool) -> list[Path]:
    """Copy the SurveyDesk exemplar specs tree (AOR-010 reference)."""
    src_specs = TEMPLATE_ROOT / "specs"
    if not src_specs.is_dir():
        return _write_generic(root, outline, force=force)
    dest_specs = root / "specs"
    if force and dest_specs.exists():
        shutil.rmtree(dest_specs)
    dest_specs.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src_specs, dest_specs, dirs_exist_ok=True)
    written = [p for p in dest_specs.rglob("*") if p.is_file()]

    # Seed non-specs project files that regen assumes exist (brand, gitignore, cleanup).
    written.extend(_copy_template_file(root, "AGENTS.md", force=force))
    written.extend(_copy_template_tree(root, "brand", force=force))
    written.extend(_copy_template_file(root, ".gitignore", force=force))
    written.extend(_copy_template_file(root, "CLEANUP.md", force=force))
    written.extend(_copy_template_tree(root, "data", force=force))
    written.extend(_ensure_root_package_json(root, force=force))
    written.extend(_ensure_env_example(root, force=force))

    src_cap = root / "specs" / "regeneration" / "source-requirements.md"
    src_cap.parent.mkdir(parents=True, exist_ok=True)
    src_cap.write_text(
        "# Source requirements (natural language)\n\n"
        "Captured by `aor gather` before confirm.\n\n"
        "```text\n"
        f"{outline.source_requirements.strip()}\n"
        "```\n",
        encoding="utf-8",
    )
    written.append(src_cap)
    return written


def _copy_template_file(root: Path, rel: str, *, force: bool) -> list[Path]:
    src = TEMPLATE_ROOT / rel
    dest = root / rel
    if not src.is_file():
        return []
    if dest.exists() and not force:
        return []
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    return [dest]


def _copy_template_tree(root: Path, rel: str, *, force: bool) -> list[Path]:
    src = TEMPLATE_ROOT / rel
    dest = root / rel
    if not src.is_dir():
        return []
    if force and dest.exists():
        shutil.rmtree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dest, dirs_exist_ok=True)
    return [p for p in dest.rglob("*") if p.is_file()]


def _ensure_root_package_json(root: Path, *, force: bool) -> list[Path]:
    dest = root / "package.json"
    if dest.exists() and not force:
        return []
    # Minimal scaffold so execute:specs / allowScripts exist before P5 finishes.
    dest.write_text(
        "{\n"
        '  "name": "survey-desk",\n'
        '  "version": "0.1.0",\n'
        '  "private": true,\n'
        '  "description": "SurveyDesk — local-first survey demo (API + web + native operators)",\n'
        '  "workspaces": ["apps/api", "apps/web", "packages/*"],\n'
        '  "scripts": {\n'
        '    "demo": "bash scripts/demo.sh",\n'
        '    "demo:api": "npm run dev -w @survey-desk/api",\n'
        '    "demo:web": "npm run dev -w @surveydesk/web",\n'
        '    "demo:ios": "bash scripts/demo-ios-simulator.sh",\n'
        '    "demo:android": "bash scripts/demo-android-emulator.sh",\n'
        '    "test:acceptance": "npm --prefix tests test",\n'
        '    "execute:specs": "bash specs/regeneration/run-parallel.sh",\n'
        '    "regen:parallel": "npm run execute:specs"\n'
        "  },\n"
        '  "engines": { "node": ">=20" },\n'
        '  "allowScripts": {\n'
        '    "better-sqlite3": true,\n'
        '    "esbuild": true\n'
        "  }\n"
        "}\n",
        encoding="utf-8",
    )
    return [dest]


def _ensure_env_example(root: Path, *, force: bool) -> list[Path]:
    dest = root / ".env-example"
    if dest.exists() and not force:
        return []
    dest.write_text(
        "# SurveyDesk local demo environment\n"
        "# Copy to .env: cp .env-example .env\n\n"
        "SURVEY_DESK_API_HOST=127.0.0.1\n"
        "SURVEY_DESK_API_PORT=8787\n"
        "SURVEY_DESK_DATABASE_PATH=./data/survey-desk.sqlite\n"
        "SURVEY_DESK_WEB_PORT=3091\n"
        "NEXT_PUBLIC_SURVEY_DESK_API_URL=http://127.0.0.1:8787\n\n"
        "# Android emulator → host API: http://10.0.2.2:8787\n"
        "# Public respondent URLs (host browser): http://127.0.0.1:3091\n"
        "SURVEY_DESK_OPERATOR_TOKEN=\n",
        encoding="utf-8",
    )
    return [dest]


def _write_generic(root: Path, outline: SpecOutline, *, force: bool) -> list[Path]:
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
