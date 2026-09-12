# Regeneration blueprint

**Purpose:** If `apps/` is missing or deleted, rebuild SurveyDesk from specs.

**Cleanup first:** see root [`CLEANUP.md`](../CLEANUP.md) — remove `apps/`, `packages/`, `tests/` (and local sqlite/env), keep `specs/`, `brand/`, `scripts/`.

## One MD file (preferred — Cursor Agent)

Same as sdd-analytics-copilot: attach **one** prompt in a Cursor Agent chat:

```
@specs/regeneration/prompts/REGENERATE.md
```

Or copy everything below the `---` in [`prompts/REGENERATE.md`](./prompts/REGENERATE.md).

That prompt tells the agent to launch parallel Task agents (P1–P6) with exclusive path ownership. See [`orchestrate-parallel.md`](./orchestrate-parallel.md).

## Optional CLI

```bash
npm run execute:specs
```

Runs [`run-parallel.sh`](./run-parallel.sh) via Cursor Agent CLI (`agent login` required). Alias: `npm run regen:parallel`.

## Read order

1. `prompts/REGENERATE.md` (entrypoint)
2. `orchestrate-parallel.md`
3. `specs/product/vision.md`, `personas.md`, `demo-journey.md`, `brand.md`
4. `specs/requirements/SD-001` … `SD-012`
5. `specs/domain/*`, `specs/api/openapi.yaml`
6. `specs/adr/*` (including ADR-007 native mobile, ADR-008 brand)
7. `prompts/parallel/P1` … `P6`

## Non-negotiable invariants

1. Local SQLite only for v1 core data
2. Anonymous public respondents
3. Operator tooling is **native mobile** (Swift iOS + Kotlin Android)
4. Public web is **React + Next.js**
5. FormSpec JSON is the form source of truth
6. English product name **SurveyDesk** only
7. Instant results ≤ 2s poll window after submit
8. Mobile demos via **iPhone + iPad Simulators** and **Android phone + tablet Emulators**
9. Brand assets in `brand/` (including **transparent** `surveydesk-logo.png`) + shared theme tokens on every UI (ADR-008)
10. Regeneration wall clock **≤ 15 minutes** with parallel agents (see `specs/regeneration/orchestrate-parallel.md`)
11. Android build speed parity with iOS (ADR-009); do not commit `apps/`, `packages/`, or `tests/`
12. Mobile adaptive UX per `contracts/mobile-operator-ux.md` (SD-008 / ADR-007)

## Target stack

| App | Stack |
|-----|--------|
| API | Node.js + TypeScript + better-sqlite3 (or Drizzle) + Hono/Express |
| Web | React + Next.js App Router |
| iOS | Swift + SwiftUI |
| Android | Kotlin + Jetpack Compose |

### Parallel multi-agent (preferred, **≤ 15 min**)

See **`orchestrate-parallel.md`** + **`prompts/REGENERATE.md`** + prompts in **`prompts/parallel/`**.  
Wall clock: Wave 1 ≤ 10m, Wave 2 ≤ 3m, Wave 3 ≤ 2m. **Android must match iOS build pace (ADR-009):** cold `assembleDebug` ≤ 90s, warm ≤ 15s; cached `gradle-8.11.1-all`; ban `material-icons-extended`. Do not commit `apps/`, `packages/`, or `tests/`.

## Definition of done

- `npm run demo` starts API + web
- `npm run demo:ios` launches operator app on **iPhone and iPad** Simulators
- `npm run demo:android` launches operator app on **phone and tablet** Emulators (JDK 17; API `http://10.0.2.2:8787`)
- Anonymous respond works at `/s/{slug}`
- `npm run test:acceptance` covers create → open → respond → results → close
- Transparent logo + adaptive sidebar layouts match `contracts/mobile-operator-ux.md`
