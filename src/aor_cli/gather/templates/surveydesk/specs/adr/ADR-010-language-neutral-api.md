# ADR-010 Language-neutral API (Python reference)

## Decision

The SurveyDesk **HTTP + OpenAPI + SQLite contract** is the source of truth for the API. The **reference implementation** under `apps/api` is **Python 3.11+** (FastAPI + stdlib `sqlite3` or equivalent).

Any language that honours `specs/api/openapi.yaml` and the lifecycle rules (draft → open → closed) is valid — including **Java**, Go, Kotlin-JVM, or Node. Regeneration prompts generate the Python reference so learners are not forced into Node for the API.

## Why

SDD is stack-agnostic: Node on the public web (Next.js) is an interface choice for the respondent UI, not a requirement for the product contract. Session feedback asked for a path that Java-preferring engineers can follow without adopting Node for the backend.

## Consequences

- `apps/api` is a Python package (`pyproject.toml`), not an npm workspace.
- Root `package.json` workspaces cover `apps/web` (+ optional `packages/*`) only.
- Demo scripts start the API with Python (`uvicorn` / venv) and the web with npm.
- Acceptance tests prefer HTTP or an in-process ASGI client against OpenAPI shapes — language of the API process does not matter.
- If regenerating in another language, update the ADR + P1 prompt first; do not silently diverge from OpenAPI.
