# Contract — mobile operator UX (iOS + Android)

**Audience:** P3-ios, P4-android, P5-root-scripts  
**Purpose:** Survive `apps/` deletion. Regen MUST recreate these behaviors.

## Brand chrome (both platforms)

1. Copy `brand/surveydesk-logo.png` into app assets (iOS `BrandLogo` imageset; Android `res/drawable/surveydesk_logo.png`).
2. **Never** use opaque `surveydesk-logo.jpg` in splash, nav, sidebar, or toolbar — JPG has a solid plate and does not blend.
3. Provide a small reusable mark composable/view (`BrandLogoMark` / `BrandLogo`) that:
   - uses the PNG with original/as-is colors
   - scales with height (≈28dp phone toolbar, ≈36–72dp sidebar/splash)
   - has **no** opaque clip plate / rounded white card behind the logo
4. Splash: `surfaceSubtle` (`#F0F4F8`) background + transparent logo + optional muted tagline `SURVEYS. LOCALLY YOURS.`
5. Theme tokens from `Theme.swift.txt` / `Color.kt.txt` (ADR-008).

## Adaptive layout

| Form factor | Layout |
|-------------|--------|
| iPhone / Android phone (compact / width &lt; 600dp) | Stack navigation (list → detail) |
| iPad / Android tablet (regular / width ≥ 600dp) | **Left sidebar** (brand + survey list + create) + **detail pane** |

### iOS (P3) — MUST

- Universal binary: `TARGETED_DEVICE_FAMILY = "1,2"` in `project.yml` and Xcode project (project-level **and** target-level).
- iPad orientations via `INFOPLIST_KEY_UISupportedInterfaceOrientations_iPad` (portrait + landscape).
- iPad: `NavigationSplitView` + sidebar list.
- **Critical:** In the iPad sidebar, do **not** use `NavigationLink(value:)` for row selection. That pushes an empty destination into the detail column (blank white screen). Drive detail with an explicit `selectedSurveyId` binding (e.g. `Button` / plain row tap). Put `.id(selectedSurveyId)` on `SurveyDetailView` so `@StateObject` reloads when selection changes.
- Detail tabs: prefer `switch` / conditional content — **avoid** `.tabViewStyle(.page)` in SplitView detail (often zero-height on iPad).
- iPhone: `NavigationStack` + `NavigationLink(value:)` is fine.

### Android (P4) — MUST

- `BuildConfig.API_BASE_URL = "http://10.0.2.2:8787"` (emulator special host loopback — reliable on macOS ARM AVDs). `PUBLIC_WEB_ORIGIN = "http://127.0.0.1:3091"` so copied respondent URLs open in the **host** browser.
- Cleartext allowed (`usesCleartextTraffic` + network security config); include `10.0.2.2` / `127.0.0.1` / `localhost` in network security config.
- Optional: `adb reverse` for USB devices or tooling — not required for emulator API calls when using `10.0.2.2`.
- Width ≥ **600dp** → `Row` sidebar (~320dp) + detail; else NavHost stack.
- Sidebar selection highlights the active survey; detail uses `key(surveyId)` / equivalent when id changes.
- Ban `material-icons-extended` (ADR-009). Copy `gradle.properties.txt` verbatim.

## Demo scripts (P5) — MUST

**Also follow** `specs/regeneration/contracts/shell-demo-pitfalls.md` (bash 3.2 `set -u`, unicode ellipsis, EADDRINUSE reuse, `allowScripts`, `.gitignore`).

### `scripts/demo.sh`

- Start API (8787) + web (3091); print URLs.
- If `/health` is healthy **and** web responds → reuse (do not double-bind → EADDRINUSE).
- If port busy but unhealthy → free listeners then start.
- Fail fast if a child exits immediately after launch.

### `scripts/demo-ios-simulator.sh`

- Resolve UDIDs with UUID regex (device names like `iPad mini (A17 Pro)` contain parentheses — do not parse the first `(…)` as UDID).
- Build + install + launch on **both** an iPhone and an iPad Simulator when available.
- Scheme `SurveyDesk`, bundle `local.surveydesk.ios`.
- Echo strings: use `${udid}...` — never bare `$udid…` (unicode ellipsis → unbound variable on bash 3.2 + `set -u`).

### `scripts/demo-android-emulator.sh`

- Force **JDK 17+** for Gradle (detect Homebrew/`java_home`; ignore stale Java 11 `JAVA_HOME`). Oracle JDK 11 banners contain `18.9` — parse major from the quoted version only.
- Start **both** AVDs when present: `Medium_Phone_API_35` and `Medium_Tablet_API_35` (override via `SURVEY_DESK_ANDROID_PHONE_AVD` / `SURVEY_DESK_ANDROID_TABLET_AVD`).
- If missing, create/document tablet AVD (API 35, ~2560×1600 @ 320dpi landscape) alongside phone.
- Detect already-running AVDs via **adb serial / AVD name** (not fragile `pgrep`).
- **Critical adb stdin pitfall:** `adb` reads stdin. Never call `adb shell` / `adb -s …` inside a `while read` over `adb devices` output — it consumes the next serial and the wait loop sticks at `1/2 ready`. Always `adb … </dev/null` (helper `adb_cmd`) and/or buffer serials into an array before nested adb calls.
- **Empty arrays:** before `"${serials[@]}"` / `"${device_lines[@]}"`, guard with `((${#arr[@]} > 0))` (bash 3.2 + `set -u`).
- Echo strings: use `${avd}...` — never bare `$avd…`.
- For **each** ready emulator serial: optional `adb -s SERIAL reverse` for 8787/3091 (fallback only; app API uses `10.0.2.2`).
- Always `:app:assembleDebug`, then per serial: `am force-stop` → `adb install -r` of **that** APK → re-apply reverse → `am start -S` (cold start). Never resume a snapshot’s previous SurveyDesk task; never rely on Gradle `installDebug` alone across multiple devices.
- Warn if host `http://127.0.0.1:8787/health` fails.
- **Do not** print Android Studio `open -a` instructions.

### Root npm scripts

- `demo`, `demo:ios`, `demo:android`, `test:acceptance` as today.
- Root `allowScripts` for `better-sqlite3` and `esbuild`.
- `.gitignore` must list `apps/`, `packages/`, `tests/`.
- `.env-example`: Android API note `http://10.0.2.2:8787` (emulator→host); copied web origin `http://127.0.0.1:3091` (host browser).

## Definition of done (mobile)

- `npm run demo:ios` launches on iPhone **and** iPad Simulators.
- `npm run demo:android` launches on phone **and** tablet emulators.
- Transparent logo blends on `#F0F4F8` / white chrome.
- Tablet/iPad sidebar opens survey detail when a row is tapped (no blank detail pane).
- Second `npm run demo` while servers are healthy does not EADDRINUSE.
