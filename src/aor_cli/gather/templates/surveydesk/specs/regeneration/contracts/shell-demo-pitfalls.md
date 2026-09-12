# Contract — shell / demo script pitfalls (macOS bash 3.2)

**Audience:** P5-root-scripts (and anyone editing `scripts/*.sh`)  
**Purpose:** Survive regen without post-hoc manual script fixes. Lessons from live SurveyDesk demos.

## Hard rules (MUST)

### 1. Unicode ellipsis after `$var` (unbound variable)

macOS ships **bash 3.2**. With `set -u`, this fails:

```bash
echo "Booting $udid…"   # bash treats variable name as udid… (U+2026)
```

**Always** brace expansions before non-ASCII punctuation, or use ASCII `...`:

```bash
echo "Booting ${udid}..."
echo "Starting emulator @${avd}..."
```

Never write bare `$name…` / `$serial…` / `$avd…` in echo strings.

### 2. Empty arrays under `set -u`

```bash
serials=()
printf '%s\n' "${serials[@]}"   # FAIL on bash 3.2 + set -u → serials[@]: unbound variable
for x in "${device_lines[@]}"; do …; done   # FAIL when array empty
```

**Guard length first**, or use the bash 3.2-safe form:

```bash
if ((${#serials[@]} > 0)); then
  printf '%s\n' "${serials[@]}"
fi
# or:
for x in ${device_lines[@]+"${device_lines[@]}"}; do
  …
done
```

Same for `READY_SERIALS=("${UNIQUE_SERIALS[@]}")` when UNIQUE may be empty.

### 3. `demo.sh` — EADDRINUSE / reuse

Ports **8787** (API) and **3091** (web) are often still held after a previous demo.

`scripts/demo.sh` MUST:

1. If `GET /health` returns `"ok":true` **and** web root responds → **reuse** (print “Already running”; do not bind again; Ctrl+C leaves servers up or document clearly).
2. Else if port is busy but unhealthy → **free** listeners (`lsof -tiTCP:PORT -sTCP:LISTEN` → `kill`) then start.
3. Start API + web in background; after ~1s, **fail fast** if either child exited (still EADDRINUSE).
4. Trap INT/TERM to stop only processes this script started (not reused ones).

### 4. adb stdin steal (Android)

Never call `adb shell` / `adb -s …` inside `while read` over `adb devices` without `</dev/null`. Buffer device lines into an array first; use an `adb_cmd` helper that redirects stdin from `/dev/null`.

### 5. Simulator UDID parse (iOS)

Device names like `iPad mini (A17 Pro)` contain parentheses. Extract UDIDs with a **UUID regex**, not the first `(…)`.

### 6. Root `package.json` npm scripts / allowScripts

- Workspaces: `apps/api`, `apps/web`, `packages/*` only (native apps are not npm workspaces).
- Keep `execute:specs` → `bash specs/regeneration/run-parallel.sh`.
- Add root **`allowScripts`** so workspace installs can build native modules:

```json
"allowScripts": {
  "better-sqlite3": true,
  "esbuild": true
}
```

Without this, `npm install` at the monorepo root may leave `better-sqlite3` unbuilt.

### 7. `.gitignore` (P5 must ensure)

```
apps/
packages/
tests/
.env
data/*.sqlite
data/*.sqlite-*
node_modules/
.next/
dist/
```

Do not commit generated trees.

### 8. Brand assets before Wave 1

Regen assumes `brand/surveydesk-full.jpg` and **transparent** `brand/surveydesk-logo.png` exist. If missing, orchestrator/P5 MUST create placeholders (or fail with a clear error) — never leave P2/P3/P4 without assets to copy.
