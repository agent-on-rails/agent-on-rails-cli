# ADR-009 Android build speed (parity with iOS Simulator)

## Decision

Android operator app builds for the live demo MUST complete in wall-clock time **comparable to the iOS Simulator build** of `apps/ios`:

| Metric | Target |
|--------|--------|
| Cold `:app:assembleDebug` (deps already in `~/.gradle`) | **≤ 90 seconds** |
| Warm Daemon rebuild (no source change) | **≤ 15 seconds** |
| Regenerating agent (P4) including writing sources + first assemble | **≤ same Wave-1 window as P3-ios** (do not overrun Wave 1 because of Gradle) |

## Why

Wave 1 is ≤ 10 minutes for four parallel agents. Historically Android burned the budget by: downloading Gradle to `/tmp`, using `--no-daemon`, pulling `material-icons-extended`, and fighting sandbox Gradle locks.

## Required project shape

1. Committed-in-tree (under gitignored `apps/android/`) Gradle Wrapper using a **cached** dist — prefer `gradle-8.11.1-all.zip` already under `~/.gradle/wrapper/dists`.
2. `gradle.properties`: Daemon **on**, `org.gradle.parallel=true`, `org.gradle.caching=true`, Kotlin incremental on. **Never** `--no-daemon` for routine builds.
3. **Do not** depend on `androidx.compose.material:material-icons-extended` (compile-time bomb). Use default Material icons only, or Unicode/text for `+` / stars.
4. Lean network stack: OkHttp + kotlinx.serialization **or** Retrofit without debug logging on the default path. Avoid unused Google Play / Maps / Firebase SDKs.
5. Single `:app` module. No multi-module graph for v1.
6. Brand JPGs may live in `res/drawable` or `assets/`; keep them small (source brand files are already ~50–100KB).
7. Verify with `:app:assembleDebug` only during regen (install/emulator launch is Wave 3 / demo scripts).

## Consequences

P4 agents that re-download Gradle, enable `--no-daemon`, or add `material-icons-extended` are out of spec. iOS remains Simulator-only (no Archive); Android remains `assembleDebug`-first.
