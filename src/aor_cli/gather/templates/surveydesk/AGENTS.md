# Guidance for coding agents

You are implementing **SurveyDesk** against the specs in this repository.

## Authority

1. `specs/product/vision.md` — product intent and non-goals
2. `specs/requirements/SD-001` … `SD-012` — SHALL / SHALL NOT contracts
3. `specs/domain/*`, `specs/api/openapi.yaml`, `specs/adr/*`
4. `specs/acceptance/*.feature` — scenarios that must pass
5. `specs/regeneration/` — rebuild prompts if source is missing

Do **not** invent a different product (analytics copilot, SaaS multi-tenant cloud, etc.). Stay inside the local SurveyDesk demo scope.

## Hard rules

- Specs are source of truth. Code follows specs; do not rewrite specs to match accidental UI.
- Public respondent web is **anonymous** — no login for people filling surveys.
- Operator actions (create, edit, open, close, view results) happen in the **native mobile apps** via the API.
- Persistence is **local SQLite** only for v1.
- All services run **locally** for the live demo (loopback or same LAN).
- English UI and documentation.
- Author commits as `Iman Suherman <iman.suherman@gmail.com>`. Never add `Co-authored-by` / Cursor attribution.

## Stack

| Surface | Tech |
|---------|------|
| API | Node.js + TypeScript + SQLite |
| Public web | React + Next.js |
| Operator iOS | Swift + SwiftUI (iPhone **and** iPad Simulator, universal) |
| Operator Android | Kotlin + Jetpack Compose (phone **and** tablet Emulator) |

## Brand

- Full lockup: `brand/surveydesk-full.jpg`
- Logo only (transparent): `brand/surveydesk-logo.png` — required for regen; never use opaque JPG logo in chrome
- Shared colors: `brand/README.md` / `specs/product/brand.md` (primary `#0878F8`, ink `#001838`)
- Apply the same theme on web + both mobile apps (ADR-008).
- Adaptive operator UI (ADR-007 / `specs/regeneration/contracts/mobile-operator-ux.md`): iPad + Android tablet left sidebar.
- Android builds must match iOS Simulator pace (ADR-009): no `material-icons-extended`; cold `assembleDebug` ≤ 90s.

## Generated source (do not commit)

`apps/`, `packages/`, and `tests/` are produced by regeneration and listed in `.gitignore`. Keep the repo **specs + brand + scripts** only. To wipe generated trees before a fresh rebuild, follow root **`CLEANUP.md`**, then `@specs/regeneration/prompts/REGENERATE.md`.

## Shell / demo pitfalls (do not rediscover)

See `specs/regeneration/contracts/shell-demo-pitfalls.md`:

- macOS **bash 3.2** + `set -u`: never `$var…` (unicode ellipsis); never empty `"${arr[@]}"` without a length guard
- `demo.sh` must **reuse** healthy 8787/3091 or free them — avoid EADDRINUSE
- Root `allowScripts` for `better-sqlite3` / `esbuild`
- Brand PNG/JPG must exist under `brand/` before Wave 1 (gather should seed `brand/README.md` + assets)

## Timebox (15 minutes)

Prefer `@specs/regeneration/prompts/REGENERATE.md` in Cursor Agent (parallel P1–P6). Wall clock ≤ 15m (Wave 1 ≤ 10m, Wave 2 ≤ 3m, Wave 3 ≤ 2m). See `specs/regeneration/orchestrate-parallel.md`. Optional CLI: `npm run execute:specs`.

## Suggested build order (if running waves yourself)

1. API + SQLite schema (`SD-003`, `SD-004`, `SD-005`)
2. Public web respond + live results (`SD-006`, `SD-007`)
3. iOS + Android operator apps (`SD-008`…`SD-011`)
4. Acceptance tests (`SD-012`)

## Commands (once implemented)

```bash
npm install
cp .env-example .env
npm run demo           # API + web
npm run demo:ios       # iPhone + iPad Simulators
npm run demo:android   # phone + tablet Emulators
npm run test:acceptance
```
