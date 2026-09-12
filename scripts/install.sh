#!/usr/bin/env bash
# Install the Agent On Rails CLI (`aor`) from GitHub.
# Prefer an HTTP tarball so a broken git (missing git-remote-https) cannot fail the install.
set -euo pipefail

ARCHIVE="${AOR_CLI_ARCHIVE:-https://github.com/agent-on-rails/agent-on-rails-cli/archive/refs/heads/main.tar.gz}"
GIT_SPEC="${AOR_CLI_GIT:-git+https://github.com/agent-on-rails/agent-on-rails-cli.git}"

pick_python() {
  local cand ver fallback=""
  # Prefer 3.11–3.13: Homebrew python@3.14 often breaks ensurepip / pipx shared venvs.
  for cand in \
    python3.12 python3.13 python3.11 \
    /opt/homebrew/bin/python3.12 /opt/homebrew/bin/python3.13 /opt/homebrew/bin/python3.11 \
    /usr/local/bin/python3.12 /usr/local/bin/python3.13 /usr/local/bin/python3.11 \
    python3
  do
    if ! command -v "$cand" >/dev/null 2>&1 && [[ ! -x "$cand" ]]; then
      continue
    fi
    ver="$("$cand" --version 2>&1 || true)"
    case "$ver" in
      "Python 3.1"[1-9]*|"Python 3."[2-9]*)
        if "$cand" -c "import ensurepip, venv" >/dev/null 2>&1; then
          echo "$cand"
          return 0
        fi
        if [[ -z "$fallback" ]]; then
          fallback="$cand"
        fi
        ;;
    esac
  done
  if [[ -n "$fallback" ]]; then
    echo "$fallback"
    return 0
  fi
  return 1
}

if ! PYTHON="$(pick_python)"; then
  echo "python3 is required (3.11+)." >&2
  exit 1
fi

# Prefer Apple / Homebrew git helpers when /usr/local/bin/git is incomplete.
if [[ -z "${GIT_EXEC_PATH:-}" ]]; then
  for git_bin in /opt/homebrew/bin/git /usr/bin/git; do
    if [[ -x "$git_bin" ]]; then
      exec_path="$("$git_bin" --exec-path 2>/dev/null || true)"
      if [[ -n "$exec_path" && -x "$exec_path/git-remote-https" ]]; then
        export GIT_EXEC_PATH="$exec_path"
        break
      fi
    fi
  done
fi

install_with_pip_user() {
  local spec="$1"
  echo "Installing with $PYTHON -m pip --user" >&2
  "$PYTHON" -m pip install --user --upgrade "$spec"
}

install_spec() {
  local spec="$1"
  if command -v pipx >/dev/null 2>&1; then
    if pipx install --force --python "$PYTHON" "$spec"; then
      return 0
    fi
    echo "pipx failed (often Homebrew python@3.14 ensurepip / shared venv); falling back to pip --user" >&2
    install_with_pip_user "$spec"
    return $?
  fi
  if "$PYTHON" -m pipx --version >/dev/null 2>&1; then
    if "$PYTHON" -m pipx install --force --python "$PYTHON" "$spec"; then
      return 0
    fi
    echo "python -m pipx failed; falling back to pip --user" >&2
    install_with_pip_user "$spec"
    return $?
  fi
  echo "pipx not found; installing with $PYTHON -m pip --user" >&2
  install_with_pip_user "$spec"
}

TMP="$(mktemp -d)"
cleanup() { rm -rf "$TMP"; }
trap cleanup EXIT

echo "Using Python: $PYTHON ($("$PYTHON" --version 2>&1))"
echo "Downloading ${ARCHIVE} …"
if command -v curl >/dev/null 2>&1; then
  curl -L --fail --retry 3 -A "agent-on-rails-cli-install" -o "$TMP/cli.tar.gz" "$ARCHIVE"
else
  "$PYTHON" - "$ARCHIVE" "$TMP/cli.tar.gz" <<'PY'
import sys, urllib.request
urllib.request.urlretrieve(sys.argv[1], sys.argv[2])
PY
fi

mkdir -p "$TMP/src"
tar -xzf "$TMP/cli.tar.gz" -C "$TMP/src" --strip-components=1
install_spec "$TMP/src" || {
  echo "Local archive install failed; retrying ${GIT_SPEC}" >&2
  install_spec "$GIT_SPEC"
}

if command -v aor >/dev/null 2>&1; then
  aor --version
  echo "Installed. Next: aor guide"
else
  echo "Installed the package, but 'aor' is not on PATH." >&2
  echo "Try: $PYTHON -m aor_cli  or add ~/.local/bin to PATH." >&2
fi
