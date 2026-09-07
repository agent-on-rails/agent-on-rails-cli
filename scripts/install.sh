#!/usr/bin/env bash
# Install the Agent On Rails CLI (`aor`) from GitHub.
set -euo pipefail

REPO="${AOR_CLI_REPO:-https://github.com/agent-on-rails/agent-on-rails-cli.git}"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required (3.11+)." >&2
  exit 1
fi

if command -v pipx >/dev/null 2>&1; then
  pipx install --force "git+${REPO}"
elif python3 -m pipx --version >/dev/null 2>&1; then
  python3 -m pipx install --force "git+${REPO}"
else
  echo "pipx not found; installing with python3 -m pip --user" >&2
  python3 -m pip install --user --upgrade "git+${REPO}"
fi

if command -v aor >/dev/null 2>&1; then
  aor --version
  echo "Installed. Next: aor guide"
else
  echo "Installed the package, but 'aor' is not on PATH." >&2
  echo "Try: python3 -m aor_cli  or add your user scripts directory to PATH." >&2
fi
