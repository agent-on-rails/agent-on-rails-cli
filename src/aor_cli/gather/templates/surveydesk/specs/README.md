# Specs

This directory is the **source of truth** for Spec-Driven Development in SurveyDesk.

If application code is deleted, regenerate from:

1. This tree (`product` → `requirements` → `domain` → `api` → `adr`)
2. `specs/regeneration/README.md`
3. `specs/regeneration/prompts/*`

## Traceability

```
Requirement (specs/requirements/SD-xxx)
        ↓
Domain / API / ADR contracts
        ↓
Implementation (apps/, packages/)
        ↓
Acceptance tests (tests/) + Gherkin (specs/acceptance/)
```

## Layout

| Path | Purpose |
|------|---------|
| `product/` | Vision, personas, brand theme, live-demo journey |
| `requirements/` | SHALL requirements `SD-001` … `SD-012` |
| `domain/` | Survey, FormSpec, Response, Lifecycle |
| `api/` | OpenAPI for local API |
| `adr/` | Architecture decisions (incl. ADR-009 Android build speed) |
| `acceptance/` | Gherkin scenarios |
| `regeneration/` | Blueprint + **REGENERATE.md** (one-file agent entry) + parallel prompts |

## Requirement index

| ID | Title |
|----|-------|
| SD-001 | Product surfaces (mobile operator, public web, local API) |
| SD-002 | Local-first runtime (SQLite, loopback, English) |
| SD-003 | Survey entity and lifecycle |
| SD-004 | FormSpec — drag-and-drop form schema |
| SD-005 | Local API + SQLite persistence |
| SD-006 | Anonymous public respondent web |
| SD-007 | Instant results (live aggregation) |
| SD-008 | Mobile app — survey list and control |
| SD-009 | Mobile app — form builder (drag and drop) |
| SD-010 | Mobile app — start / end survey workflow |
| SD-011 | Mobile app — results view |
| SD-012 | Acceptance tests and demo script |
