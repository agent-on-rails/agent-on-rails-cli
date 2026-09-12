"""Extract SpecOutline from natural language (LLM or stub)."""

from __future__ import annotations

import json
import re
from typing import Any

from aor_cli.gather.canon import looks_like_surveydesk, surveydesk_outline
from aor_cli.gather.models import (
    AcceptanceOutline,
    AdrOutline,
    DomainOutline,
    RequirementOutline,
    SpecOutline,
)
from aor_cli.gather.prompts import SYSTEM_PROMPT, user_extract_prompt
from aor_cli.llm.client import ChatClient, LlmError


def extract_outline(requirements_text: str, *, stub: bool = False) -> SpecOutline:
    text = requirements_text.strip()
    if not text:
        raise ValueError("requirements text is empty")
    if stub:
        return stub_extract(text)
    client = ChatClient()
    raw = client.chat(
        [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_extract_prompt(text)},
        ]
    )
    data = parse_json_object(raw)
    outline = SpecOutline.from_dict(data)
    outline.source_requirements = text
    if looks_like_surveydesk(text):
        return surveydesk_outline(text)
    if not outline.requirements:
        return stub_extract(text)
    return outline


def stub_extract(requirements_text: str) -> SpecOutline:
    """Deterministic offline extract for tests / no API key."""
    if looks_like_surveydesk(requirements_text):
        return surveydesk_outline(requirements_text)
    name = _guess_name(requirements_text)
    prefix = "SD"
    lines = [ln.strip("-• \t") for ln in requirements_text.splitlines() if ln.strip()]
    bullets: list[str] = []
    for ln in lines:
        parts = re.split(r"(?<=[.!])\s+", ln)
        for part in parts:
            part = part.strip()
            if len(part) > 20:
                bullets.append(part)
    bullets = bullets[:12]
    if not bullets:
        bullets = [
            f"{name} operators can create and manage core records",
            f"{name} exposes a local HTTP API",
            f"{name} has a public or shared surface for end users",
            f"{name} stores data locally for the v1 demo",
        ]
    requirements = []
    for i, bullet in enumerate(bullets, start=1):
        requirements.append(
            RequirementOutline(
                id=f"{prefix}-{i:03d}",
                title=_title_from(bullet),
                shall=bullet if bullet.upper().startswith("THE SYSTEM SHALL") else f"The system SHALL {bullet[0].lower() + bullet[1:]}",
                notes="stub extract",
            )
        )
    return SpecOutline(
        product_name=name,
        tagline=f"{name} — drafted from natural-language requirements",
        vision=(
            f"**{name}** is described by the operator requirements below.\n\n"
            f"{requirements_text.strip()}\n\n"
            "This outline was produced by the Agent On Rails stub extractor "
            "(no LLM). Edit before applying."
        ),
        non_goals=["Multi-tenant SaaS billing", "Proprietary coding agent"],
        personas=[
            {"name": "Operator", "role": "Primary user", "goals": "Complete the core job"},
            {"name": "Respondent", "role": "Secondary user", "goals": "Use the public surface"},
        ],
        demo_journey=[
            "Bootstrap specs with aor gather",
            "Approve contracts",
            "Implement surfaces from regeneration prompts",
            "Run the live demo path",
        ],
        brand_notes="Define primary brand color and English product name.",
        requirement_prefix=prefix,
        requirements=requirements,
        domains=[
            DomainOutline(name="core", summary=f"Core domain concepts for {name}."),
            DomainOutline(name="lifecycle", summary="Status transitions and invariants."),
        ],
        adrs=[
            AdrOutline(
                id="ADR-001",
                title="Monorepo or multi-surface layout",
                decision="Keep specs as authority; generate apps from regeneration prompts.",
            ),
            AdrOutline(
                id="ADR-002",
                title="Local-first persistence for v1",
                decision="Prefer local SQLite or equivalent unless requirements demand otherwise.",
            ),
        ],
        acceptance=[
            AcceptanceOutline(
                name="lifecycle",
                feature=f"{name} lifecycle happy path",
                scenarios=[
                    "Scenario: Happy path completes",
                    "Scenario: Invalid state is rejected",
                ],
            ),
            AcceptanceOutline(
                name="api-health",
                feature="Local API health",
                scenarios=["Scenario: Health endpoint returns ok"],
            ),
        ],
        api_summary="Local HTTP JSON API for operators and public surfaces.",
        source_requirements=requirements_text.strip(),
    )


def parse_json_object(raw: str) -> dict[str, Any]:
    text = raw.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence:
        text = fence.group(1).strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start < 0 or end <= start:
            raise LlmError("Could not parse JSON outline from model output")
        data = json.loads(text[start : end + 1])
    if not isinstance(data, dict):
        raise LlmError("Outline JSON must be an object")
    return data


_NAME_STOPWORDS = {
    "called",
    "named",
    "build",
    "building",
    "product",
    "local",
    "first",
    "the",
    "a",
    "an",
}


_TITLE_TAIL_STOP = {
    "a",
    "an",
    "the",
    "and",
    "or",
    "of",
    "for",
    "to",
    "with",
    "on",
    "in",
    "at",
    "by",
    "as",
}


def _guess_name(text: str) -> str:
    desk = re.search(r"\b([A-Z][A-Za-z0-9]*(?:Desk|Hub))\b", text)
    if desk:
        return desk.group(1)
    # Do not use re.I: [A-Z] would match "called" after "product ".
    m = re.search(
        r"(?:called|named|product(?:\s+name)?)\s+[\"']?([A-Z][A-Za-z0-9]+)",
        text,
    )
    if m:
        raw = m.group(1).strip()
        if raw.lower() not in _NAME_STOPWORDS:
            return raw
    first = next((ln.strip() for ln in text.splitlines() if ln.strip()), "Product")
    words = re.findall(r"[A-Za-z][A-Za-z0-9]+", first)
    if words:
        joined = " ".join(words[:3])
        if "surveydesk" in joined.lower().replace(" ", ""):
            return "SurveyDesk"
        return joined.title()
    return "Product"


def _title_from(bullet: str) -> str:
    cleaned = re.sub(r"^(the system shall|shall)\s+", "", bullet, flags=re.I).strip()
    cleaned = cleaned.rstrip(".,;:")
    if not cleaned:
        return "Requirement"
    if len(cleaned) <= 100:
        return _cap_title(_trim_title_stopwords(cleaned))
    cut = cleaned[:100]
    if " " in cut:
        cut = cut.rsplit(" ", 1)[0]
    return _cap_title(_trim_title_stopwords(cut))


def _trim_title_stopwords(title: str) -> str:
    words = title.split()
    while len(words) > 4 and words[-1].lower().strip(".,;:()") in _TITLE_TAIL_STOP:
        words.pop()
    return " ".join(words)


def _cap_title(text: str) -> str:
    if not text:
        return "Requirement"
    return text[0].upper() + text[1:]
