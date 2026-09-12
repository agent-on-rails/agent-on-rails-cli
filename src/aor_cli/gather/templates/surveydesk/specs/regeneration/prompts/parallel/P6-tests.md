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

## Stack
- Prefer Vitest (or Node test runner) calling the API module/HTTP against a **temp SQLite** file
- Do not use the developer’s `data/survey-desk.sqlite`

## Must implement
1. Happy path: create → open → anonymous respond → results reflect submit within expectations → close → further submit rejected
2. Lifecycle: FormSpec patch rejected while `open`
3. Public results: forbidden when `showPublicResults` is false
4. Map scenarios to Gherkin feature names in comments
5. `tests/README.md` explaining how to run (`npm run test:acceptance` from root once wired)

If `apps/api` is not importable as a library, tests may spawn the API process or use `fetch` against `127.0.0.1` when `SURVEY_DESK_TEST_API_URL` is set — document both modes; prefer in-process if P1 exports a test helper.

## Done when
- Test files exist covering SD-012 end-to-end path
- Tests use isolated temp DB
