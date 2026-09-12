#!/usr/bin/env bash
# Parallel multi-agent execution of SurveyDesk specs via Cursor Agent CLI.
# Mirrors sdd-analytics-copilot/specs/regeneration/run-parallel.sh
# Requires: `agent login`, agent on PATH.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
PROMPT_DIR="$ROOT/specs/regeneration/prompts/parallel"
LOG_DIR="$ROOT/specs/regeneration/.regen-logs"
mkdir -p "$LOG_DIR"

BUDGET_SECS="${SURVEY_DESK_REGEN_BUDGET_SECS:-900}" # default 15 minutes
START_EPOCH="$(date +%s)"
deadline_epoch=$(( START_EPOCH + BUDGET_SECS ))
echo "SurveyDesk execute:specs started $(date -u +%Y-%m-%dT%H:%M:%SZ); deadline +$((BUDGET_SECS / 60))m"

if ! command -v agent >/dev/null 2>&1; then
  echo "ERROR: Cursor Agent CLI ('agent') not on PATH. Install/login, then retry." >&2
  exit 1
fi

# Wave 0 — ensure root scaffold for npm script entry
if [[ ! -f "$ROOT/package.json" ]]; then
  echo "ERROR: root package.json missing" >&2
  exit 1
fi
if [[ ! -f "$ROOT/.env" && -f "$ROOT/.env-example" ]]; then
  cp "$ROOT/.env-example" "$ROOT/.env"
  echo "Created .env from .env-example"
fi

run_agent() {
  local id="$1"
  local prompt_file="$2"
  local logfile="$LOG_DIR/${id}.log"
  echo "[$id] starting → $logfile"
  (
    agent -p --force --trust --sandbox disabled \
      --workspace "$ROOT" \
      "$(cat "$prompt_file")" \
      >"$logfile" 2>&1
    local ec=$?
    echo "[$id] exit=$ec" >>"$logfile"
    exit "$ec"
  ) &
  echo $! >"$LOG_DIR/${id}.pid"
}

wait_wave() {
  local failed=0
  for pidfile in "$LOG_DIR"/*.pid; do
    [[ -f "$pidfile" ]] || continue
    local pid
    pid="$(cat "$pidfile")"
    if ! wait "$pid"; then
      failed=1
      echo "Agent pid $pid failed"
    fi
    rm -f "$pidfile"
  done
  return "$failed"
}

check_deadline() {
  if (( $(date +%s) > deadline_epoch )); then
    echo "ERROR: exceeded ${BUDGET_SECS}s budget" >&2
    exit 2
  fi
}

echo "=== Wave 1: P1-api P2-web P3-ios P4-android (parallel) ==="
run_agent P1 "$PROMPT_DIR/P1-api.md"
run_agent P2 "$PROMPT_DIR/P2-web.md"
run_agent P3 "$PROMPT_DIR/P3-ios.md"
run_agent P4 "$PROMPT_DIR/P4-android.md"
wait_wave || { echo "Wave 1 had failures — inspect $LOG_DIR"; exit 1; }
check_deadline

echo "=== Wave 2: P5-root-scripts P6-tests (parallel) ==="
run_agent P5 "$PROMPT_DIR/P5-root-scripts.md"
run_agent P6 "$PROMPT_DIR/P6-tests.md"
wait_wave || { echo "Wave 2 had failures — inspect $LOG_DIR"; exit 1; }
check_deadline

echo "=== Wave 3: verify ==="
if [[ -f "$ROOT/package-lock.json" || -f "$ROOT/apps/api/package.json" || -f "$ROOT/apps/web/package.json" ]]; then
  npm install || echo "WARN: npm install reported issues — continue smoke checks"
fi

if [[ -f "$ROOT/scripts/demo.sh" ]]; then
  echo "Demo script present: scripts/demo.sh"
else
  echo "WARN: scripts/demo.sh missing (P5)"
fi

echo "Expected layout:"
echo "  apps/api     — local HTTP + SQLite"
echo "  apps/web     — Next.js public respondent UI"
echo "  apps/ios     — Swift operator app (Simulator)"
echo "  apps/android — Kotlin operator app (Emulator)"
echo ""
echo "Next:"
echo "  npm run demo           # API + web"
echo "  npm run demo:ios       # iOS Simulator"
echo "  npm run demo:android   # Android Emulator"
echo "  npm run test:acceptance"
echo ""
echo "execute:specs OK in $(( $(date +%s) - START_EPOCH ))s (logs: $LOG_DIR)"
