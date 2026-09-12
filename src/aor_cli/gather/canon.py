"""Canonical SurveyDesk outline (reference pack SD-001…SD-012)."""

from __future__ import annotations

import re

from aor_cli.gather.models import (
    AcceptanceOutline,
    AdrOutline,
    DomainOutline,
    RequirementOutline,
    SpecOutline,
)

SURVEYDESK_VISION = """\
**SurveyDesk** is a local-first survey desk: operators design forms on a mobile app, \
respondents answer on a public web page (anonymous), and answers land in SQLite \
through a local API — with instant results and in-app start/stop controls.

## Goals

1. Drag-and-drop (or equivalent touch-friendly) form builder on mobile
2. Anonymous public web for respondents — no account required
3. Local SQLite storage via a documented HTTP API
4. Instant results for operators (and optionally a public live results view when the survey is open)
5. Internal tooling **inside the mobile app**: create, edit, open (start), close (end), view results
6. Entire stack runnable on one laptop for a one-hour Spec-Driven demo
"""

SURVEYDESK_NON_GOALS = [
    "Multi-tenant SaaS / cloud billing / SSO",
    "Email invitations or paid SurveyMonkey feature parity",
    "Offline-first sync across devices beyond same-LAN API access",
    "Complex branching logic / payment / file upload fields (may land later)",
    "Non-English UI (English only for this repo)",
]

SURVEYDESK_REQUIREMENTS = [
    RequirementOutline(
        id="SD-001",
        title="Product surfaces",
        shall="The system SHALL expose three cooperating surfaces: iOS (Swift) and Android (Kotlin) operator apps, public React + Next.js web for anonymous respondents, and a local HTTP JSON API over SQLite. The system SHALL NOT require a cloud account for the v1 demo.",
        notes="Reference: specs/requirements/SD-001-product-surfaces.md",
    ),
    RequirementOutline(
        id="SD-002",
        title="Local-first runtime",
        shall="The system SHALL run entirely on the operator's machine for v1: SQLite on disk, API bound to 127.0.0.1 by default, English UI. The system SHALL NOT depend on Firestore, Cloud Run, or third-party survey SaaS for core flows.",
        notes="Reference: specs/requirements/SD-002-local-first.md",
    ),
    RequirementOutline(
        id="SD-003",
        title="Survey entity and lifecycle",
        shall="A Survey SHALL have id, title, description, status (draft|open|closed), formSpec, publicSlug, showPublicResults, and timestamps. New surveys SHALL start as draft. open SHALL accept anonymous responses; closed and draft SHALL reject them. FormSpec edits SHALL be blocked while open.",
        notes="Reference: specs/requirements/SD-003-survey-lifecycle.md",
    ),
    RequirementOutline(
        id="SD-004",
        title="FormSpec — drag-and-drop form schema",
        shall="The system SHALL store fields as FormSpec JSON with types short_text, long_text, single_choice, multi_choice, rating_1_5, yes_no. The mobile builder SHALL add, reorder, edit, and remove fields. The system SHALL NOT execute scripts inside FormSpec.",
        notes="Reference: specs/requirements/SD-004-form-spec.md",
    ),
    RequirementOutline(
        id="SD-005",
        title="Local API + SQLite persistence",
        shall="The system SHALL provide a local HTTP JSON API (default 127.0.0.1:8787) that creates/reads/updates surveys, transitions lifecycle, accepts anonymous responses for open surveys, and returns aggregates. Persistence SHALL use SQLite (./data/survey-desk.sqlite). Public respond routes SHALL NOT require an operator token.",
        notes="Reference: specs/requirements/SD-005-local-api.md",
    ),
    RequirementOutline(
        id="SD-006",
        title="Anonymous public respondent web",
        shall="The public web SHALL render a survey at /s/{publicSlug} with no login, validate required fields, submit to the public API, and show thank-you or not-open errors. The public web SHALL NOT collect name/email unless those are FormSpec fields.",
        notes="Reference: specs/requirements/SD-006-public-web.md",
    ),
    RequirementOutline(
        id="SD-007",
        title="Instant results",
        shall="The system SHALL compute aggregate results (counts, option tallies, recent text). After a successful submit, a results fetch within 2 seconds SHALL reflect the new response. Optional public live results when showPublicResults is true.",
        notes="Reference: specs/requirements/SD-007-instant-results.md",
    ),
    RequirementOutline(
        id="SD-008",
        title="Mobile app — survey list and control",
        shall="The mobile app SHALL be the operator tooling on iPhone, iPad, Android phone, and Android tablet: list with status, create, detail, copy public URL. Phones use stack navigation; iPad/tablet use a left sidebar + detail. Chrome SHALL use the transparent logo, not an opaque JPG plate.",
        notes="Reference: specs/requirements/SD-008-mobile-list.md",
    ),
    RequirementOutline(
        id="SD-009",
        title="Mobile app — form builder",
        shall="The operator mobile apps SHALL provide a FormSpec builder: add field types, edit labels/required/options, drag-and-drop reorder, persist via API. The system SHALL block FormSpec edits while the survey is open.",
        notes="Reference: specs/requirements/SD-009-mobile-builder.md",
    ),
    RequirementOutline(
        id="SD-010",
        title="Mobile app — start / end survey workflow",
        shall="The operator SHALL open (draft→open) and close (open→closed) a survey from mobile, copy the public URL when open, and see that closed surveys reject further submits.",
        notes="Reference: specs/requirements/SD-010-mobile-lifecycle.md",
    ),
    RequirementOutline(
        id="SD-011",
        title="Mobile app — results view",
        shall="The operator mobile apps SHALL show live results (totalResponses and per-field aggregates) that refresh within 2 seconds after a new public submit.",
        notes="Reference: specs/requirements/SD-011-mobile-results.md",
    ),
    RequirementOutline(
        id="SD-012",
        title="Acceptance tests and demo script",
        shall="The repository SHALL include automated acceptance covering create → open → respond → results → close, Gherkin under specs/acceptance/, and a demo journey aligned with specs/product/demo-journey.md.",
        notes="Reference: specs/requirements/SD-012-acceptance.md",
    ),
]


def looks_like_surveydesk(text: str) -> bool:
    blob = re.sub(r"\s+", " ", text).lower()
    compact = blob.replace(" ", "")
    if "surveydesk" in compact:
        return True
    signals = (
        "formspec" in compact
        or "form spec" in blob
        or "local-first survey" in blob
        or "local first survey" in blob
    )
    surfaces = ("swift" in blob or "ios" in blob) and (
        "kotlin" in blob or "android" in blob
    )
    web = "next.js" in blob or "nextjs" in compact or "anonymous" in blob
    return signals and surfaces and web


def surveydesk_outline(source_requirements: str) -> SpecOutline:
    return SpecOutline(
        product_name="SurveyDesk",
        tagline="Local-first survey desk — native operators, anonymous web, SQLite API",
        vision=SURVEYDESK_VISION.strip(),
        non_goals=list(SURVEYDESK_NON_GOALS),
        personas=[
            {
                "name": "Operator",
                "role": "Demo host / survey designer",
                "goals": "Create surveys, arrange fields, start/stop collection, see counts live on iOS Simulator and Android Emulator",
            },
            {
                "name": "Respondent",
                "role": "Audience / public",
                "goals": "Open a public Next.js link, submit anonymously, see thank-you (optional live results)",
            },
            {
                "name": "Developer / coding agent",
                "role": "Implementer",
                "goals": "Implement against SD-* specs; regenerate apps from regeneration prompts",
            },
        ],
        demo_journey=[
            "Spec first — show SD-003 and SD-004",
            "API + SQLite — start apps/api",
            "Build on mobile — create Session feedback; add rating + single choice + short text",
            "Start — Open survey; copy public URL",
            "Respond on web — anonymous submit",
            "Instant results — mobile updates within 2s",
            "Close — further submit rejected",
            "Traceability — map steps back to SD-* IDs",
        ],
        brand_notes=(
            "Primary #0878F8, ink #001838, green #10A868, purple #7828F8, rating gold #F8B000. "
            "Transparent logo in chrome (never opaque JPG plate). English product name SurveyDesk only."
        ),
        requirement_prefix="SD",
        requirements=list(SURVEYDESK_REQUIREMENTS),
        domains=[
            DomainOutline(name="survey", summary="Top-level operator artifact with lifecycle and publicSlug."),
            DomainOutline(name="form-spec", summary="Portable form definition edited by the mobile builder."),
            DomainOutline(name="response", summary="One anonymous submission per respondent attempt."),
            DomainOutline(name="results", summary="Aggregates for operator mobile and optional public live view."),
            DomainOutline(name="lifecycle", summary="draft → open → closed invariants."),
        ],
        adrs=[
            AdrOutline(
                id="ADR-001",
                title="Monorepo",
                decision="Keep specs as authority; generate apps/ from regeneration prompts.",
            ),
            AdrOutline(
                id="ADR-002",
                title="SQLite",
                decision="Local SQLite file for v1; no cloud database.",
            ),
            AdrOutline(
                id="ADR-003",
                title="Anonymous public",
                decision="Respondents never sign in.",
            ),
            AdrOutline(
                id="ADR-004",
                title="Mobile operator",
                decision="Operator UX is native iOS + Android only.",
            ),
            AdrOutline(
                id="ADR-005",
                title="FormSpec JSON",
                decision="Share one FormSpec schema across API, web, and mobile.",
            ),
            AdrOutline(
                id="ADR-006",
                title="English naming",
                decision="English UI and product name SurveyDesk only.",
            ),
            AdrOutline(
                id="ADR-007",
                title="Native mobile",
                decision="Swift/SwiftUI and Kotlin/Compose; iPad/tablet sidebar layouts.",
            ),
            AdrOutline(
                id="ADR-008",
                title="Brand theme",
                decision="Shared tokens; transparent logo in chrome.",
            ),
            AdrOutline(
                id="ADR-009",
                title="Android build speed",
                decision="Android assemble must match iOS Simulator pace.",
            ),
        ],
        acceptance=[
            AcceptanceOutline(
                name="lifecycle",
                feature="Survey lifecycle happy path",
                scenarios=[
                    "Scenario: Reject responses when closed",
                    "Scenario: Accept responses when open",
                ],
            ),
            AcceptanceOutline(
                name="form-builder",
                feature="FormSpec builder",
                scenarios=["Scenario: Reorder fields persists"],
            ),
            AcceptanceOutline(
                name="instant-results",
                feature="Instant results",
                scenarios=["Scenario: Results update after submit"],
            ),
            AcceptanceOutline(
                name="adaptive-layout",
                feature="Adaptive operator layout",
                scenarios=["Scenario: Tablet or iPad sidebar opens detail"],
            ),
        ],
        api_summary=(
            "Local-first HTTP API for SurveyDesk (SQLite). Operator routes may require "
            "X-SurveyDesk-Token; public respond routes do not. Default http://127.0.0.1:8787."
        ),
        source_requirements=source_requirements.strip(),
    )
