#!/usr/bin/env bash
# Install the Agent On Rails CLI (`aor`) from GitHub.
# Prefer an HTTP tarball so a broken git (missing git-remote-https) cannot fail the install.
set -euo pipefail

ARCHIVE="${AOR_CLI_ARCHIVE:-https://github.com/agent-on-rails/agent-on-rails-cli/archive/refs/heads/main.tar.gz}"
GIT_SPEC="${AOR_CLI_GIT:-git+https://github.com/agent-on-rails/agent-on-rails-cli.git}"

if ! command -v python3 >/dev/null 2>&1; then
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

install_spec() {
  local spec="$1"
  if command -v pipx >/dev/null 2>&1; then
    pipx install --force "$spec"
  elif python3 -m pipx --version >/dev/null 2>&1; then
    python3 -m pipx install --force "$spec"
  else
    echo "pipx not found; installing with python3 -m pip --user" >&2
    python3 -m pip install --user --upgrade "$spec"
  fi
}

TMP="$(mktemp -d)"
cleanup() { rm -rf "$TMP"; }
trap cleanup EXIT

echo "Downloading ${ARCHIVE} …"
if command -v curl >/dev/null 2>&1; then
  curl -L --fail --retry 3 -A "agent-on-rails-cli-install" -o "$TMP/cli.tar.gz" "$ARCHIVE"
else
  python3 - "$ARCHIVE" "$TMP/cli.tar.gz" <<'PY'
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
  echo "Try: python3 -m aor_cli  or add ~/.local/bin to PATH." >&2
fi
