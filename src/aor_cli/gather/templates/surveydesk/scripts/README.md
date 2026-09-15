# SurveyDesk demo scripts

Live demo order (local machine):

1. **API + web** — `npm run demo`  
   Starts the **Python** SQLite API (`scripts/run-api.sh`, ADR-010) and public Next.js respondent UI. Prints API and web URLs.
2. **iOS / iPadOS Simulator** — `npm run demo:ios`  
   Builds and launches the universal SwiftUI operator app (`apps/ios`) on **iPhone and iPad** Simulators.  
   **Or open in Xcode:** `open apps/ios/SurveyDesk.xcodeproj` → scheme **SurveyDesk** → pick an **iPhone or iPad Simulator** → **⌘R**.
3. **Android Emulator** — `npm run demo:android`  
   Starts **phone + tablet** AVDs (or reuses ones already booted), builds the latest debug APK, force-installs it on each device, and cold-starts the Compose operator app (`apps/android`). Forces **JDK 17+**. Emulator API uses `http://10.0.2.2:8787`. If `Medium_Tablet_API_35` is missing, the script creates a Pixel-Tablet-class AVD (API 35, 2560×1600 @ 320dpi, landscape).
4. **Browser respond** — open the public URL from the operator app (or `http://127.0.0.1:3091/s/<slug>`).

Missing `apps/api`, `apps/web`, `apps/ios`, `apps/android`, or `tests/` fails fast with a message to generate them first (`npm run execute:specs` / `REGENERATE.md`).

## Open iOS in Xcode (Simulator)

```bash
# From repo root (after apps/ios exists)
open apps/ios/SurveyDesk.xcodeproj
```

1. Wait for Xcode to index the project.
2. Top-left toolbar: scheme **SurveyDesk**.
3. Destination: any **iPhone or iPad** Simulator (not “Any iOS Device”).
4. **Product → Run** or **⌘R**.
5. Ensure API is up (`npm run demo`) so the operator app can reach `http://127.0.0.1:8787`.

If the `.xcodeproj` is missing: `cd apps/ios && xcodegen generate` (requires [XcodeGen](https://github.com/yonaskolb/XcodeGen)), then open again.

## Commands

| npm script | Shell | Purpose |
|------------|-------|---------|
| `npm run demo` | `scripts/demo.sh` | Python API + web concurrently |
| `npm run demo:api` | `scripts/run-api.sh` | API only (`apps/api`, Python) |
| `npm run demo:web` | `scripts/run-workspace.sh web` | Web only (`apps/web`) |
| `npm run demo:ios` | `scripts/demo-ios-simulator.sh` | iPhone + iPad Simulators |
| `npm run demo:android` | `scripts/demo-android-emulator.sh` | phone + tablet Emulators |
| `npm run test:acceptance` | `scripts/test-acceptance.sh` | Acceptance tests under `tests/` |

## Prerequisites

- Copy env: `cp .env-example .env`
- **Python 3.11+** for `apps/api` (ADR-010 — OpenAPI is language-neutral; Java implementations are welcome)
- Node.js ≥ 20 for `apps/web` only
- Xcode + iPhone **and** iPad Simulators for `demo:ios` (universal app)
- Android SDK + JDK 17+ for `demo:android`. Default AVDs: `Medium_Phone_API_35`, `Medium_Tablet_API_35` (override with `SURVEY_DESK_ANDROID_PHONE_AVD` / `SURVEY_DESK_ANDROID_TABLET_AVD`)
- Generated app trees under `apps/` (from regeneration / Wave 1); **scripts/** and **brand/** stay committed

Default ports: API `8787`, web `3091`. See `.env-example`:

- Host API / web: `http://127.0.0.1:8787`, `http://127.0.0.1:3091`
- Android emulator API (compiled into the APK): `http://10.0.2.2:8787` (emulator → host)
- Copied respondent URLs still use `http://127.0.0.1:3091` so they open in the host browser

`demo:android` does not require opening Android Studio.
