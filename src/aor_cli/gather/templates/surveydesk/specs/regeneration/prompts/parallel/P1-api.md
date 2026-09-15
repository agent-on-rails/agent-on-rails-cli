# P1 — local API + SQLite (OWNED PATHS ONLY)

You are agent **P1-api** implementing SurveyDesk from specs.

## OWNED PATHS (create only these)
- `apps/api/**`

Do **not** edit `apps/web`, `apps/ios`, `apps/android`, `tests/`, `scripts/`, or root `package.json`.

## Specs (must read)
- `specs/requirements/SD-002`, `SD-003`, `SD-004`, `SD-005`, `SD-007`
- `specs/domain/survey.md`, `lifecycle.md`, `form-spec.md`, `response.md`, `results.md`
- `specs/api/openapi.yaml` — implement **exactly**
- `specs/adr/ADR-002-sqlite.md`, `ADR-003-anonymous-public.md`, **`ADR-010-language-neutral-api.md`**

## Stack (reference implementation)
- **Python 3.11+**
- HTTP framework: **FastAPI** + **uvicorn**
- SQLite: stdlib `sqlite3` (or `aiosqlite` if you prefer async — keep the schema simple)
- Package layout: `apps/api/pyproject.toml` (not an npm package)
- Default listen: `SURVEY_DESK_API_HOST` / `SURVEY_DESK_API_PORT` from `.env-example` (`127.0.0.1:8787`)
- DB path: `SURVEY_DESK_DATABASE_PATH` → `./data/survey-desk.sqlite` (resolve from monorepo root)

The OpenAPI contract is language-neutral. Do **not** generate a Node/TypeScript API unless ADR-010 is explicitly superseded.

## Must implement
1. Schema: `surveys`, `responses` (answers JSON)
2. Routes matching OpenAPI:
   - `GET /health`
   - Operator: list/create/get/patch survey, open, close, results
   - Public: get survey by slug, submit response, public results when allowed
3. Lifecycle: draft/open/closed rules (no FormSpec write while `open`; reject submit unless `open`)
4. Aggregates per `specs/domain/results.md` (instant = fresh read on each GET)
5. Optional `X-SurveyDesk-Token` when `SURVEY_DESK_OPERATOR_TOKEN` is set
6. `pyproject.toml` with runnable entry (e.g. `surveydesk-api` console script or documented `uvicorn` module path) plus `dev` / `start` helpers in README
7. Export a testable ASGI app factory (`create_app` + DB open helper) for P6 in-process tests — avoid listening as a side effect of import
8. README in `apps/api` with how to create a venv, `pip install -e .`, and run locally
9. CORS enabled for local web (`http://127.0.0.1:3091`)

## Done when
- `apps/api` boots and `GET /health` returns `{ ok: true }` within the 15-minute overall regen budget (Wave 1 share ≤ 10m)
- Create → open → public submit → results → close works via curl against OpenAPI shapes

## Speed
Prefer FastAPI + stdlib sqlite3; skip unused frameworks; do not dockerize.
