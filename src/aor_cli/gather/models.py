"""Structured outline produced from natural-language requirements."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class RequirementOutline:
    id: str
    title: str
    shall: str
    notes: str = ""


@dataclass
class DomainOutline:
    name: str
    summary: str


@dataclass
class AdrOutline:
    id: str
    title: str
    decision: str


@dataclass
class AcceptanceOutline:
    name: str
    feature: str
    scenarios: list[str] = field(default_factory=list)


@dataclass
class SpecOutline:
    """SurveyDesk-shaped product pack outline (confirm before write)."""

    product_name: str
    tagline: str
    vision: str
    non_goals: list[str] = field(default_factory=list)
    personas: list[dict[str, str]] = field(default_factory=list)
    demo_journey: list[str] = field(default_factory=list)
    brand_notes: str = ""
    requirement_prefix: str = "SD"
    requirements: list[RequirementOutline] = field(default_factory=list)
    domains: list[DomainOutline] = field(default_factory=list)
    adrs: list[AdrOutline] = field(default_factory=list)
    acceptance: list[AcceptanceOutline] = field(default_factory=list)
    api_summary: str = "Local HTTP JSON API."
    source_requirements: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SpecOutline:
        reqs = [
            RequirementOutline(**r) if isinstance(r, dict) else r
            for r in data.get("requirements") or []
        ]
        domains = [
            DomainOutline(**d) if isinstance(d, dict) else d for d in data.get("domains") or []
        ]
        adrs = [AdrOutline(**a) if isinstance(a, dict) else a for a in data.get("adrs") or []]
        acceptance = []
        for item in data.get("acceptance") or []:
            if isinstance(item, dict):
                acceptance.append(
                    AcceptanceOutline(
                        name=str(item.get("name") or "feature"),
                        feature=str(item.get("feature") or ""),
                        scenarios=[str(s) for s in item.get("scenarios") or []],
                    )
                )
        return cls(
            product_name=str(data.get("product_name") or "Product"),
            tagline=str(data.get("tagline") or ""),
            vision=str(data.get("vision") or ""),
            non_goals=[str(x) for x in data.get("non_goals") or []],
            personas=list(data.get("personas") or []),
            demo_journey=[str(x) for x in data.get("demo_journey") or []],
            brand_notes=str(data.get("brand_notes") or ""),
            requirement_prefix=str(data.get("requirement_prefix") or "SD").upper(),
            requirements=reqs,
            domains=domains,
            adrs=adrs,
            acceptance=acceptance,
            api_summary=str(data.get("api_summary") or "Local HTTP JSON API."),
            source_requirements=str(data.get("source_requirements") or ""),
        )
