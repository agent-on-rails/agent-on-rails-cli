# Parallel multi-agent execution

**Goal:** Implement SurveyDesk from `specs/` in **under 15 minutes** wall clock using **parallel Cursor Agent CLI workers** with exclusive path ownership.

**Create (agents, gitignored):** `apps/api/`, `apps/web/`, `apps/ios/`, `apps/android/`, `packages/`, `tests/` — write them locally for the demo; **do not** `git add` these trees (see root `.gitignore`).

**Keep committed:** `specs/`, `brand/`, `data/README.md`, `AGENTS.md`, `README.md`, `CONTRIBUTING.md`, `LICENSE`, `.env-example`, `.gitignore`, `package.json`, `scripts/` stubs.

## Hard constraints (every agent)

- Specs are source of truth (`SD-001`…`SD-012`, domain, OpenAPI, ADRs).
- Local SQLite only; anonymous public respondents; English UI; product name **SurveyDesk**.
- **Web** = React + Next.js (App Router).
- **Operator mobile** = native **iOS (Swift/SwiftUI)** + **Android (Kotlin/Jetpack Compose)** — not Expo/React Native.
- Demo mobile via **iPhone + iPad Simulators** and **Android phone + tablet Emulators**.
- **Brand:** use `brand/surveydesk-full.jpg` (full + text) and `brand/surveydesk-logo.png` (logo only, transparent); shared theme tokens from `brand/README.md` / `specs/product/brand.md` on every UI.
- **Mobile UX contract:** `specs/regeneration/contracts/mobile-operator-ux.md` (sidebar selection, JDK 17, Android `10.0.2.2` API, dual devices).
- **Shell / demo pitfalls:** `specs/regeneration/contracts/shell-demo-pitfalls.md` (bash 3.2 `set -u`, `$var…` ellipsis, empty arrays, `demo.sh` EADDRINUSE reuse, root `allowScripts`).
- Do **not** edit files outside your OWNED PATHS. Do **not** modify originals under `brand/` — copy into app asset folders.
- Do **not** invent analytics-copilot / SaaS multi-tenant features.
- Author commits as `Iman Suherman <iman.suherman@gmail.com>` only if committing; no Co-authored-by.

## Waves

| Wave | Agents (parallel) | Owns |
|------|-------------------|------|
| 0 | orchestrator (`run-parallel.sh`) | Confirm `agent` CLI; ensure root `package.json` / `.env`; mkdir log dir |
| 1 | `P1-api`, `P2-web`, `P3-ios`, `P4-android` | Exclusive app trees |
| 2 | `P5-root-scripts`, `P6-tests` | Demo/sim scripts + acceptance tests |
| 3 | orchestrator | `npm install`, smoke API health, print simulator demo commands |

Target wall clock (**15 minutes total**): Wave 1 ≤ 10m, Wave 2 ≤ 3m, Wave 3 ≤ 2m.

## Speed rules (hit the 15-minute budget)

1. **Always parallelize Wave 1** (P1–P4 at once). Sequential stack builds will miss the budget.
2. **Ship the demo slice first** — OpenAPI-correct API, FormSpec respond web, operator list/create/builder/open/close/results on mobile. Defer polish that is not in SD-001…SD-012.
3. **Android (ADR-009):** must finish in **similar wall time to iOS Simulator builds**. Cold `:app:assembleDebug` ≤ 90s with warm `~/.gradle`; warm ≤ 15s. Create Wrapper first with **cached** `gradle-8.11.1-all` (not a fresh `-bin` download). Daemon on; never `/tmp` Gradle or `--no-daemon`. **Ban** `material-icons-extended`. Lean OkHttp/serialization stack; single `:app` module; verify assemble only (not install) in Wave 1.
4. **iOS:** Universal iPhone+iPad Simulator builds (`TARGETED_DEVICE_FAMILY=1,2`). Do not archive for App Store. P3 and P4 should complete in the same Wave-1 window. Follow `contracts/mobile-operator-ux.md` for SplitView selection (no sidebar `NavigationLink`).
5. **Web/API:** lean deps; commit lockfiles; do not run production docker builds during regen.
6. **Verify lightly in Wave 3:** API `GET /health`, web `npm run build` or `dev` smoke, `./gradlew :app:assembleDebug` once if time remains — do not clean between builds.

## Owned paths

### P1-api
`apps/api/**`

### P2-web
`apps/web/**`

### P3-ios
`apps/ios/**`

### P4-android
`apps/android/**`

### P5-root-scripts
`scripts/**`, `packages/shared/**` (optional FormSpec TS types), root files: `turbo.json` (optional), updates to root `package.json` scripts only (do not remove `execute:specs`), `.env-example` if needed

### P6-tests
`tests/**` only

## How to run (preferred — one MD in Cursor Agent)

```
@specs/regeneration/prompts/REGENERATE.md
```

The orchestrator agent launches Wave-1 Task agents with prompts from `prompts/parallel/P1`…`P4`, waits, then `P5`+`P6`, then verifies.

## How to run (optional CLI)

```bash
# From repo root:
npm run execute:specs
# or:
bash specs/regeneration/run-parallel.sh
```

Requires Cursor Agent CLI logged in (`agent login`) and `agent` on PATH.
