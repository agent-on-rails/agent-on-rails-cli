#!/usr/bin/env bash
# Start SurveyDesk API + public web for the local live demo.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

API_DIR="$ROOT/apps/api"
WEB_DIR="$ROOT/apps/web"

die() {
  echo "error: $*" >&2
  exit 1
}

if [[ ! -d "$API_DIR" ]]; then
  die "apps/api missing. Generate apps first (npm run execute:specs / REGENERATE.md)."
fi
if [[ ! -d "$WEB_DIR" || ! -f "$WEB_DIR/package.json" ]]; then
  die "apps/web missing. Generate apps first (npm run execute:specs / REGENERATE.md)."
fi
if ! command -v npm >/dev/null 2>&1; then
  die "npm is required for apps/web (Node.js >= 20). Install Node, then re-run: npm run demo"
fi

if [[ -f "$ROOT/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$ROOT/.env"
  set +a
elif [[ -f "$ROOT/.env-example" ]]; then
  echo "Note: no .env found — using .env-example defaults. Copy with: cp .env-example .env"
  set -a
  # shellcheck disable=SC1091
  source "$ROOT/.env-example"
  set +a
fi

API_HOST="${SURVEY_DESK_API_HOST:-127.0.0.1}"
API_PORT="${SURVEY_DESK_API_PORT:-8787}"
WEB_PORT="${SURVEY_DESK_WEB_PORT:-3091}"
API_URL="${NEXT_PUBLIC_SURVEY_DESK_API_URL:-http://${API_HOST}:${API_PORT}}"
WEB_URL="${NEXT_PUBLIC_SURVEY_DESK_WEB_ORIGIN:-http://127.0.0.1:${WEB_PORT}}"
mkdir -p "$ROOT/data"

ensure_web_deps() {
  local dir="$1"
  if [[ ! -d "$dir/node_modules" && ! -d "$ROOT/node_modules" ]]; then
    echo "Installing workspace dependencies at repo root..."
    (cd "$ROOT" && npm install)
  fi
  if [[ ! -d "$dir/node_modules" && ! -d "$ROOT/node_modules" ]]; then
    echo "Installing dependencies in $dir ..."
    (cd "$dir" && npm install)
  fi
}

ensure_web_deps "$WEB_DIR"

API_PID=""
WEB_PID=""

cleanup() {
  echo ""
  echo "Stopping SurveyDesk demo..."
  if [[ -n "${WEB_PID}" ]] && kill -0 "$WEB_PID" 2>/dev/null; then
    kill "$WEB_PID" 2>/dev/null || true
  fi
  if [[ -n "${API_PID}" ]] && kill -0 "$API_PID" 2>/dev/null; then
    kill "$API_PID" 2>/dev/null || true
  fi
  wait 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo "Starting API on ${API_HOST}:${API_PORT} (Python reference / ADR-010) ..."
(
  export SURVEY_DESK_API_HOST="$API_HOST"
  export SURVEY_DESK_API_PORT="$API_PORT"
  export SURVEY_DESK_DATABASE_PATH="${SURVEY_DESK_DATABASE_PATH:-$ROOT/data/survey-desk.sqlite}"
  export NEXT_PUBLIC_SURVEY_DESK_WEB_ORIGIN="$WEB_URL"
  bash "$ROOT/scripts/run-api.sh"
) &
API_PID=$!

echo "Starting web on port ${WEB_PORT} ..."
(
  cd "$WEB_DIR"
  export SURVEY_DESK_WEB_PORT="$WEB_PORT"
  export PORT="$WEB_PORT"
  export NEXT_PUBLIC_SURVEY_DESK_API_URL="$API_URL"
  export NEXT_PUBLIC_SURVEY_DESK_WEB_ORIGIN="$WEB_URL"
  npm run dev
) &
WEB_PID=$!

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  SurveyDesk demo"
echo "  API:  ${API_URL}  (OpenAPI contract — language-neutral)"
echo "  Web:  ${WEB_URL}"
echo "  Health: ${API_URL}/health"
echo "  Respondent forms: ${WEB_URL}/s/<slug>"
echo "  Android emulator API: http://10.0.2.2:${API_PORT} (emulator → host)"
echo "  Copied web origin: ${WEB_URL} (host browser)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Next (leave this running):"
echo "  npm run demo:ios        # iPhone + iPad Simulators"
echo "  npm run demo:android    # phone + tablet Emulators"
echo "Then respond in the browser at ${WEB_URL}/s/<slug>"
echo ""
echo "Press Ctrl+C to stop both processes."
echo ""

# Best-effort readiness (do not fail the demo if curl is missing / slow start).
if command -v curl >/dev/null 2>&1; then
  tries=30
  while (( tries > 0 )); do
    if ! kill -0 "$API_PID" 2>/dev/null; then
      break
    fi
    if curl -sf --max-time 1 "${API_URL}/health" >/dev/null; then
      echo "API health OK: ${API_URL}/health"
      break
    fi
    sleep 1
    tries=$((tries - 1))
  done
  if (( tries == 0 )); then
    echo "warning: API /health not up yet (still starting?)." >&2
  fi
fi

# Fail fast if either child exits
while kill -0 "$API_PID" 2>/dev/null && kill -0 "$WEB_PID" 2>/dev/null; do
  sleep 1
done

if ! kill -0 "$API_PID" 2>/dev/null; then
  die "API process exited unexpectedly (pid ${API_PID})."
fi
die "Web process exited unexpectedly (pid ${WEB_PID})."
