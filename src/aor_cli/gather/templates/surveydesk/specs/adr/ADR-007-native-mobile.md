# ADR-007 Native mobile operator apps

## Decision

Operator mobile surfaces are **native**:

- **iOS / iPadOS:** Swift + SwiftUI (`apps/ios`), universal app (`TARGETED_DEVICE_FAMILY = 1,2`), demoed on **iPhone and iPad Simulators**
- **Android (phone + tablet):** Kotlin + Jetpack Compose (`apps/android`), adaptive UI (stack &lt; 600dp; sidebar ≥ 600dp), demoed on **phone and tablet Emulators**

Public respondents remain on **React + Next.js** (`apps/web`). The local API remains Node + SQLite (`apps/api`).

UX details that must survive regeneration: `specs/regeneration/contracts/mobile-operator-ux.md`.

## Why

Live-demo goal: show true native operator tooling on both mobile platforms via simulators/emulators (including large-screen layouts), while keeping anonymous respond on the web.

## Consequences

- Expo / React Native is **out of scope** for v1 operator apps (supersedes the Expo suggestion in older ADR-001 wording).
- Two mobile codebases share the same OpenAPI + FormSpec contracts; they do not share UI code.
- Demo scripts: `npm run demo:ios` (iPhone + iPad), `npm run demo:android` (phone + tablet, JDK 17).
- Android emulator API base is `http://10.0.2.2:8787` (standard emulator → host alias). Copied public URLs use `http://127.0.0.1:3091` for the host browser. `adb reverse` is optional fallback.
