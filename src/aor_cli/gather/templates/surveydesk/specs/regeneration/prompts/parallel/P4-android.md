# P4 — Android operator app (Kotlin) (OWNED PATHS ONLY)

You are agent **P4-android** implementing SurveyDesk from specs.

## OWNED PATHS (create only these)
- `apps/android/**`

Do **not** edit `apps/api`, `apps/web`, `apps/ios`, `tests/`, or `scripts/`.

## Specs (must read)
- `specs/requirements/SD-008` … `SD-011`
- `specs/domain/form-spec.md`, `lifecycle.md`, `results.md`
- `specs/api/openapi.yaml` (operator + results)
- `specs/adr/ADR-004`, `ADR-005`, **`ADR-007`**, `ADR-008`, **`ADR-009-android-build-speed.md` (mandatory)**
- `specs/product/demo-journey.md`, `brand.md`
- `brand/README.md` + `brand/surveydesk-logo.png` (transparent) + full JPG
- `specs/regeneration/contracts/Color.kt.txt` → Compose colors
- `specs/regeneration/contracts/gradle.properties.txt` → `gradle.properties` verbatim
- **Required UX contract:** `specs/regeneration/contracts/mobile-operator-ux.md` (follow completely)

## Stack
- Native **Kotlin** + **Jetpack Compose**, single `:app` module
- `BuildConfig.API_BASE_URL = "http://10.0.2.2:8787"` (emulator → host; **do not** use `127.0.0.1` + adb reverse for API — reverse is unreliable on current macOS ARM AVDs)
- `BuildConfig.PUBLIC_WEB_ORIGIN = "http://127.0.0.1:3091"` (copied respondent URLs open in the **host** browser)
- Cleartext HTTP permitted for local demo; network security config must allow `10.0.2.2`, `127.0.0.1`, `localhost`
- Demo: Android Emulator — P4 verifies **`assembleDebug` only** (P5 installs on phone + tablet)

## Build speed — parity with iOS (ADR-009)

**Targets:** cold `:app:assembleDebug` ≤ **90s** (with warm `~/.gradle` cache); warm rebuild ≤ **15s**; finish P4 in the **same Wave-1 window as P3-ios**.

### Do first (before writing lots of UI)
1. Create Wrapper immediately: `gradlew`, `gradle-wrapper.jar`, properties with  
   `distributionUrl=https\://services.gradle.org/distributions/gradle-8.11.1-all.zip`  
   (use **-all**, already common under `~/.gradle/wrapper/dists` — **not** `-bin` if that forces a new download).
2. Copy `gradle.properties.txt` contract → `gradle.properties` (Daemon + parallel + caching).
3. Set `GRADLE_USER_HOME=$HOME/.gradle` — never a sandbox-only cache if avoidable.
4. **Never** `curl` Gradle into `/tmp`, never `--no-daemon`.

### Dependency bans / lean set
- **Banned:** `androidx.compose.material:material-icons-extended` (huge compile cost).
- Prefer Material3 + default icons only, or Text/`+`/`★` for demo chrome.
- Prefer OkHttp + kotlinx.serialization JSON (or Retrofit without logging-interceptor on the main compile path).
- No Firebase / Play Services / multi-module feature graphs.

### Verify
```bash
export JAVA_HOME="$(/usr/libexec/java_home -v 17 2>/dev/null || echo /opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home)"
export GRADLE_USER_HOME="$HOME/.gradle"
cd apps/android
./gradlew :app:assembleDebug --build-cache --parallel
```
If cold build exceeds ~90s with a warm Gradle cache, remove heavy deps before adding more features.

## Must implement (operator app)
1. Brand: copy **transparent** `brand/surveydesk-logo.png` → `res/drawable/surveydesk_logo.png`. Splash/nav/sidebar use a `BrandLogo` composable (no JPG plate, no opaque clip card).
2. Theme colors from contract (`SdPrimary`, `SdAccentGreen`, `SdRating`, …)
3. Survey list + status badges; create survey
4. Detail: Builder (drag reorder), Lifecycle (open/close + copy URL), Results (poll ≤ 2s)
5. Block FormSpec edits while `open`
6. **Tablet (screenWidthDp ≥ 600):** left sidebar (~320dp, logo + list + create) + detail pane; phone: NavHost stack. Selecting a sidebar row MUST show detail (use `key(id)` when id changes).
7. `apps/android/README.md`: JDK 17, `npm run demo:android` (phone **and** tablet AVDs), API via `10.0.2.2`; Studio optional — do not require it

## Done when
- `:app:assembleDebug` succeeds within ADR-009 time targets
- Transparent logo + tablet sidebar behavior match `mobile-operator-ux.md`
- Operator flows work against local API
- No `apps/` paths staged for commit; no `material-icons-extended`
