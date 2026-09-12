# SINGLE PROMPT — execute all SurveyDesk specs

**Copy everything below the horizontal rule into one Cursor Agent chat**, or attach:

```
@specs/regeneration/prompts/REGENERATE.md
```

This is the **only** prompt you need. Specs, brand assets, OpenAPI, and contracts are already in the repo; application source (`apps/`, `packages/`, `tests/` beyond placeholders) may be missing on purpose.

To wipe generated trees before a fresh rebuild, follow root **`CLEANUP.md`**, then attach this file.

Optional CLI automation (same waves): `npm run execute:specs` / `bash specs/regeneration/run-parallel.sh` after `agent login`.

---

You are implementing **SurveyDesk** from Spec-Driven Development specs alone. Finish in **under 15 minutes** wall clock. Prefer **parallel multi-agents** (Cursor Task tool) with exclusive path ownership; if you are a single agent, execute the same waves as fast sequential passes without skipping required files.

## Mission

Build the complete local-first stack so it matches `specs/regeneration/README.md` and requirements **SD-001 … SD-012**:

| App | Stack | Role |
|-----|--------|------|
| `apps/api` | Node + TypeScript + SQLite | Local HTTP API |
| `apps/web` | React + Next.js | Anonymous public respond |
| `apps/ios` | Swift + SwiftUI | Operator → **iPhone + iPad** Simulators (universal) |
| `apps/android` | Kotlin + Jetpack Compose | Operator → **phone + tablet** Emulators (adaptive) |

Do not invent a different product (no analytics-copilot / SaaS multi-tenant cloud).

## Hard constraints (never violate)

1. Local SQLite only for v1 core data (`data/survey-desk.sqlite`).
2. Public respondents are **anonymous** — no login on web.
3. Operator tooling is **native mobile only** (Swift iOS + Kotlin Android) — not Expo/React Native.
4. Forms are **FormSpec JSON** (ADR-005); share schema across API, web, mobile.
5. English UI; product name **SurveyDesk** only.
6. Instant results: after submit, results fetch within **≤ 2s** reflects the new response.
7. Match `specs/api/openapi.yaml` exactly for HTTP shapes.
8. **Brand:** use `brand/surveydesk-full.jpg` (full + text) and `brand/surveydesk-logo.png` (logo only, **transparent** background for headers/nav/splash — never opaque JPG logo plate in chrome). Shared theme tokens from `brand/README.md` / `specs/product/brand.md` / ADR-008 on **every** UI (primary `#0878F8`, ink `#001838`). Copy assets into apps; do not delete originals under `brand/`. **If brand files are missing at Wave 1 start, create placeholders first** (do not leave P2/P3/P4 without assets).
9. Prefer verbatim theme contracts: `specs/regeneration/contracts/theme.css.txt`, `Theme.swift.txt`, `Color.kt.txt`. **Mobile UX:** follow `specs/regeneration/contracts/mobile-operator-ux.md` (iPad/tablet sidebar, JDK 17, Android API via `10.0.2.2`, dual simulators). **Shell pitfalls:** follow `specs/regeneration/contracts/shell-demo-pitfalls.md` (bash 3.2, EADDRINUSE reuse, allowScripts).
10. Author commits as `Iman Suherman <iman.suherman@gmail.com>` only if committing; never add Co-authored-by.
11. **15-minute budget:** Wave 1 ≤ 10m (P1–P4 parallel), Wave 2 ≤ 3m, Wave 3 ≤ 2m. Android must match iOS build pace (ADR-009).
12. **Do not commit generated trees.** `apps/`, `packages/`, and `tests/` are gitignored. Implement them on disk for the demo only. **Do** keep/update committed `scripts/` and `brand/surveydesk-logo.png`.
13. **Android build speed = iOS parity (ADR-009):** P4 cold `assembleDebug` ≤ 90s with warm Gradle cache; no `material-icons-extended`; Wrapper uses cached `gradle-8.11.1-all`; Daemon on. P3 and P4 must finish in the same Wave-1 window.

## Read first (in order)

1. `specs/regeneration/orchestrate-parallel.md`
2. `specs/regeneration/README.md`
3. `specs/product/vision.md`, `personas.md`, `demo-journey.md`, `brand.md`
4. `brand/README.md`
5. `specs/requirements/SD-001` … `SD-012`
6. `specs/domain/*`, `specs/api/openapi.yaml`, `specs/adr/*`
7. Phase prompts under `specs/regeneration/prompts/parallel/P1` … `P6` (follow their OWNED PATHS)
8. `specs/regeneration/contracts/mobile-operator-ux.md` (P3/P4/P5)
9. `specs/regeneration/contracts/shell-demo-pitfalls.md` (P5 — bash / demo.sh)

## Execution plan (parallel)

### Wave 1 — launch four agents at once (or do all four yourself in order)

Use the Task tool with four parallel agents. Each agent’s prompt is the **full contents** of its prompt file:

| Agent | Prompt file | Owns only |
|-------|-------------|-----------|
| P1 | `prompts/parallel/P1-api.md` | `apps/api/**` |
| P2 | `prompts/parallel/P2-web.md` | `apps/web/**` |
| P3 | `prompts/parallel/P3-ios.md` | `apps/ios/**` |
| P4 | `prompts/parallel/P4-android.md` | `apps/android/**` |

Wait until Wave 1 completes before Wave 2.

### Wave 2 — after Wave 1 trees exist

| Agent | Prompt file | Owns only |
|-------|-------------|-----------|
| P5 | `prompts/parallel/P5-root-scripts.md` | `scripts/**`, `packages/shared/**`, root `package.json` scripts/workspaces (keep `execute:specs`), `.env-example` if needed |
| P6 | `prompts/parallel/P6-tests.md` | `tests/**` |

### Wave 3 — verify

```bash
cp -n .env-example .env 2>/dev/null || true
npm install
# smoke: start API, GET /health
# optional: npm run test:acceptance
```

Print demo commands:

```bash
npm run demo           # API + web
npm run demo:ios       # iPhone + iPad Simulators
npm run demo:android   # phone + tablet Emulators (JDK 17; API via 10.0.2.2)
```

Fix cross-cutting breaks (ports, CORS, FormSpec shape mismatches). Do not stop until API health works and web can load a public survey route against it; mobile projects must build for Simulator/Emulator; iPad/tablet sidebar must open survey detail when a row is selected.

## Key contracts

- Lifecycle: `draft` → `open` → `closed` (no FormSpec write while `open`; reject submit unless `open`)
- Public paths: `/s/{slug}` on web; API `/v1/public/surveys/{slug}` …
- Operator: list/create/builder (drag reorder)/open/close/results ≤ 2s poll
- Field types: `short_text`, `long_text`, `single_choice`, `multi_choice`, `rating_1_5`, `yes_no`
- Brand: full lockup optional on marketing; **transparent PNG logo** on icon/nav/splash/sidebar; CTAs `#0878F8`; stars `#F8B000`; add `+` `#10A868`
- Adaptive operator UI: iPad + Android tablet **left sidebar**; phone stack navigation (`mobile-operator-ux.md`)

## Demo proof (after apps exist)

1. Create “Session feedback” on iOS or Android Simulator/Emulator.
2. Add rating + single_choice + short_text; Open survey; copy public URL.
3. Submit 2–3 anonymous answers in the browser.
4. Results update on mobile within 2s.
5. Close survey; further submit rejected.

## Start

Start **Wave 1** now: launch P1–P4 in parallel using their prompt files’ instructions and OWNED PATHS.
