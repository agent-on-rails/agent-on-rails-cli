#!/usr/bin/env bash
# Run API (Python) or web (npm workspace) with a clear error if apps/* is missing.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
NAME="${1:-}"

die() {
  echo "error: $*" >&2
  exit 1
}

case "$NAME" in
  api)
    exec bash "$ROOT/scripts/run-api.sh"
    ;;
  web)
    DIR="$ROOT/apps/web"
    PKG="@survey-desk/web"
    if [[ ! -d "$DIR" || ! -f "$DIR/package.json" ]]; then
      die "apps/web missing. Generate apps first (npm run execute:specs / REGENERATE.md)."
    fi
    cd "$ROOT"
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
    export SURVEY_DESK_WEB_PORT="${SURVEY_DESK_WEB_PORT:-3091}"
    export NEXT_PUBLIC_SURVEY_DESK_API_URL="${NEXT_PUBLIC_SURVEY_DESK_API_URL:-http://${SURVEY_DESK_API_HOST}:${SURVEY_DESK_API_PORT}}"
    export NEXT_PUBLIC_SURVEY_DESK_WEB_ORIGIN="${NEXT_PUBLIC_SURVEY_DESK_WEB_ORIGIN:-http://127.0.0.1:${SURVEY_DESK_WEB_PORT}}"
    export PORT="${PORT:-$SURVEY_DESK_WEB_PORT}"
    exec npm run dev -w "$PKG"
    ;;
  *)
    die "usage: $0 api|web"
    ;;
esac
