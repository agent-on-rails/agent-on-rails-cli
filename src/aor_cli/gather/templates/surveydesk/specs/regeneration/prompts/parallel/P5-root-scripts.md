# P5 — root scripts + shared package (OWNED PATHS ONLY)

You are agent **P5-root-scripts** wiring SurveyDesk demo + monorepo scripts after Wave 1 apps exist (or in parallel — create scripts that tolerate missing apps with clear errors).

## OWNED PATHS (create/update only these)
- `scripts/**`
- `packages/shared/**` (optional shared FormSpec JSON Schema / TS types for web+api docs; do not duplicate into mobile)
- Root `package.json` **scripts**, `workspaces`, and **`allowScripts`** (keep existing `execute:specs`; add `demo`, `demo:api`, `demo:web`, `demo:ios`, `demo:android`, `test:acceptance`)
- `.env-example` (Android API `http://10.0.2.2:8787` for emulator→host; web copy origin `http://127.0.0.1:3091`)
- Root `.gitignore` entries for generated trees if missing (`apps/`, `packages/`, `tests/`, `.env`, `data/*.sqlite*`)

Do **not** edit `apps/api/**`, `apps/web/**`, `apps/ios/**`, `apps/android/**` — leave app trees to P1–P4.
Do **not** edit `tests/**` (P6).

## Specs
- `specs/product/demo-journey.md`, `specs/product/brand.md`
- `specs/requirements/SD-001`, `SD-002`, `SD-008`, `SD-012`
- `specs/regeneration/orchestrate-parallel.md`
- `specs/adr/ADR-001-monorepo.md`, **`ADR-007-native-mobile.md`**, `ADR-008-brand-theme.md`, `ADR-009-android-build-speed.md`
- **`specs/regeneration/contracts/mobile-operator-ux.md`** (script section — follow completely)
- **`specs/regeneration/contracts/shell-demo-pitfalls.md`** (bash 3.2 / EADDRINUSE / allowScripts — follow completely)
- `brand/README.md` (do not delete brand originals; if PNG/JPG missing, create transparent logo + full lockup placeholders)

## Must implement
1. `scripts/demo.sh` — start API + web concurrently; print URLs. **Per `shell-demo-pitfalls.md`:** reuse when `/health` + web already healthy; free unhealthy listeners on 8787/3091; fail fast if a child exits immediately (EADDRINUSE).
2. `scripts/demo-ios-simulator.sh` — per `mobile-operator-ux.md` + pitfalls:
   - Build/install/launch on **iPhone and iPad** Simulators when available
   - Parse simulator UDIDs with UUID regex (names may contain parentheses)
   - Fail with Xcode install hints if tools missing
   - **Never** `$udid…` (unicode ellipsis) — use `${udid}...`
3. `scripts/demo-android-emulator.sh` — per `mobile-operator-ux.md` + pitfalls:
   - Force **JDK 17+** (Homebrew / `java_home`; do not trust Java 11 `JAVA_HOME`)
   - Start **phone + tablet** AVDs (`Medium_Phone_API_35`, `Medium_Tablet_API_35` by default)
   - If tablet AVD missing, create a Pixel-Tablet-class AVD (API 35, 2560×1600 @ 320dpi, landscape) using the same system image as the phone when possible
   - Detect already-running AVDs via adb (not pgrep)
   - **Never** call `adb shell` inside a `while read` over `adb devices` without `</dev/null`
   - **Never** expand empty `"${serials[@]}"` under `set -u` without a length guard (bash 3.2)
   - **Never** `$avd…` — use `${avd}...`
   - Always assembleDebug → per serial: force-stop → `adb install -r` → optional reverse → `am start -S`
   - Warn if host `/health` is down
   - **Do not** print Android Studio open/`open -a` instructions
4. Root `package.json` workspaces: `apps/api`, `apps/web`, `packages/*` (native apps are not npm workspaces)
5. Root `allowScripts`: at least `better-sqlite3` and `esbuild` → `true` (npm may block install scripts otherwise)
6. npm scripts: `demo`, `demo:ios`, `demo:android`, `test:acceptance`
7. `scripts/README.md` — live demo order: API+web → iOS (iPhone+iPad) → Android (phone+tablet) → browser respond
8. Ensure `.gitignore` ignores `apps/`, `packages/`, `tests/`, `.env`, sqlite files under `data/`

## Done when
- `npm run demo`, `demo:ios`, `demo:android` match the UX + pitfalls contracts
- Second `npm run demo` while healthy does **not** crash with EADDRINUSE
- Scripts tolerate missing `apps/*` with clear errors
- `.env-example` documents Android emulator API `10.0.2.2` and host web origin `127.0.0.1`
- `npm install` at repo root can build `better-sqlite3` (allowScripts present)
