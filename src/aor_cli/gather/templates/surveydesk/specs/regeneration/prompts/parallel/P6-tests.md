# P6 — acceptance tests (OWNED PATHS ONLY)

You are agent **P6-tests** implementing SurveyDesk acceptance coverage from specs.

## OWNED PATHS (create only these)
- `tests/**`

Do **not** edit `apps/**` or `scripts/**`.

## Specs
- `specs/acceptance/*.feature`
- `specs/requirements/SD-003`, `SD-005`, `SD-006`, `SD-007`, `SD-012`
- `specs/api/openapi.yaml`
- `specs/product/demo-journey.md`
- `specs/adr/ADR-010-language-neutral-api.md`

## Stack
- Prefer **pytest** + httpx / FastAPI `TestClient` against the Python API factory and a **temp SQLite** file
- HTTP `fetch`/curl against a spawned API process is fine when `SURVEY_DESK_TEST_API_URL` is set
- Do not use the developer’s `data/survey-desk.sqlite`
- Do **not** require Node for API tests (web UI tests may still use Playwright/Vitest if needed)

## Must implement
1. Happy path: create → open → anonymous respond → results reflect submit within expectations → close → further submit rejected
2. Lifecycle: FormSpec patch rejected while `open`
3. Public results: forbidden when `showPublicResults` is false
4. Map scenarios to Gherkin feature names in comments
5. `tests/README.md` explaining how to run (`npm run test:acceptance` from root once wired — may shell out to `pytest`)

If `apps/api` does not export `create_app`, tests may spawn `scripts/run-api.sh` or use `fetch` against `127.0.0.1` when `SURVEY_DESK_TEST_API_URL` is set — document both modes; prefer in-process ASGI if P1 exports a test helper.

## Done when
- Test files exist covering SD-012 end-to-end path
- Tests use isolated temp DB
