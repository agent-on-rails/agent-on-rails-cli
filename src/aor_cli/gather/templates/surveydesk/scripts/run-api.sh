#!/usr/bin/env bash
# Start SurveyDesk local API (Python reference — ADR-010).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
API_DIR="$ROOT/apps/api"

die() {
  echo "error: $*" >&2
  exit 1
}

if [[ ! -d "$API_DIR" ]]; then
  die "apps/api missing. Generate apps first (npm run execute:specs / REGENERATE.md)."
fi

if [[ -f "$ROOT/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$ROOT/.env"
  set +a
elif [[ -f "$ROOT/.env-example" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$ROOT/.env-example"
  set +a
fi

export SURVEY_DESK_API_HOST="${SURVEY_DESK_API_HOST:-127.0.0.1}"
export SURVEY_DESK_API_PORT="${SURVEY_DESK_API_PORT:-8787}"
export SURVEY_DESK_DATABASE_PATH="${SURVEY_DESK_DATABASE_PATH:-$ROOT/data/survey-desk.sqlite}"
export NEXT_PUBLIC_SURVEY_DESK_WEB_ORIGIN="${NEXT_PUBLIC_SURVEY_DESK_WEB_ORIGIN:-http://127.0.0.1:${SURVEY_DESK_WEB_PORT:-3091}}"
mkdir -p "$ROOT/data"

cd "$API_DIR"

# Prefer project venv, then uv, then python3.
if [[ -x "$API_DIR/.venv/bin/python" ]]; then
  PY="$API_DIR/.venv/bin/python"
elif command -v uv >/dev/null 2>&1 && [[ -f "$API_DIR/pyproject.toml" ]]; then
  exec uv run --directory "$API_DIR" python -m surveydesk_api
elif command -v python3 >/dev/null 2>&1; then
  PY="$(command -v python3)"
else
  die "Python 3.11+ is required for apps/api (ADR-010). Install Python, then re-run."
fi

if [[ -f "$API_DIR/pyproject.toml" ]] && [[ ! -d "$API_DIR/.venv" ]] && ! command -v uv >/dev/null 2>&1; then
  echo "Creating apps/api/.venv and installing editable package..."
  python3 -m venv "$API_DIR/.venv"
  PY="$API_DIR/.venv/bin/python"
  "$PY" -m pip install -U pip
  "$PY" -m pip install -e .
fi

# Module path conventions (first that imports wins via uvicorn string in pyproject / README).
if [[ -f "$API_DIR/pyproject.toml" ]] && "$PY" -c "import surveydesk_api" 2>/dev/null; then
  exec "$PY" -m surveydesk_api
fi
if [[ -f "$API_DIR/pyproject.toml" ]] && "$PY" -c "import app.main" 2>/dev/null; then
  exec "$PY" -m uvicorn app.main:app --host "$SURVEY_DESK_API_HOST" --port "$SURVEY_DESK_API_PORT" --reload
fi
if [[ -f "$API_DIR/main.py" ]]; then
  exec "$PY" -m uvicorn main:app --host "$SURVEY_DESK_API_HOST" --port "$SURVEY_DESK_API_PORT" --reload
fi

# Legacy Node API (pre ADR-010) — keep demo working until regenerated.
if [[ -f "$API_DIR/package.json" ]]; then
  if command -v npm >/dev/null 2>&1; then
    exec npm run dev --prefix "$API_DIR"
  fi
fi

die "Could not start apps/api. Expected pyproject.toml (Python FastAPI) or legacy package.json."
