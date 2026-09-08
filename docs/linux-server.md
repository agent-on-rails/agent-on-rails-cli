# Linux / server setup — Agent On Rails

Lightweight path for a **Linux laptop or agent host** (e.g. Teknopus).
Uses the Python CLI only — no desktop GUI, small footprint.

Product page: https://agent-on-rails.suherman.net  
Full walkthrough: [walkthrough.md](./walkthrough.md)

## What you get

`aor` is a **harness** (like Hermes for IFT): it turns an approved spec into a
bounded task package for Cursor / Claude / Codex / another coding agent.
It does **not** replace your coding agent.

Day-to-day loop:

```text
init → spec → approve → plan → run → review → evidence → done
```

## Requirements

- Linux (x86_64 or arm64)
- Python **3.11+**
- `git`
- Optional but recommended: [pipx](https://pipx.pypa.io/)
- A coding agent elsewhere (laptop IDE or headless runner) to open the packaged prompt

Disk / RAM: CLI + deps are small (Python package). No GPU required.

## 1. Install

### Option A — pipx (preferred)

```bash
# Debian/Ubuntu example
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git pipx
pipx ensurepath
# open a new shell, then:
pipx install git+https://github.com/agent-on-rails/agent-on-rails-cli.git
aor --version
```

### Option B — one-liner

```bash
curl -fsSL https://raw.githubusercontent.com/agent-on-rails/agent-on-rails-cli/main/scripts/install.sh | bash
```

### Option C — clone (dev / easy updates)

```bash
git clone https://github.com/agent-on-rails/agent-on-rails-cli.git
cd agent-on-rails-cli
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
aor --version
```

See also [develop-from-clone.md](./develop-from-clone.md).

## 2. Bootstrap a project (docs + specs only)

```bash
mkdir -p ~/projects && cd ~/projects
aor init ./my-product --name "My Product"
cd my-product
```

This creates the **control plane** folder (`product/`, `specs/`, `adr/`, …).
No application code is written here.

## 3. First real loop (minimal)

```bash
# Draft a contract
aor spec new "First feature" --repo my-product-app
# edit specs/*/spec.md, acceptance.md, evidence.md

# Human gate (required)
aor spec approve PREFIX-001   # use the ID aor printed

# Bounded task + context package
aor plan PREFIX-001
aor run PREFIX-001

# Open the prompt in your coding agent:
#   .aor/packages/TASK-001/prompt.md
# Implement in the *app* repo, open a PR, run tests.

# After evidence exists:
aor review TASK-001 --approve --notes "PR + tests look good"
aor status
```

On a TTY, `aor` opens the terminal UI; on a headless server prefer the
subcommands above (or `aor tui` over SSH with a real TTY).

## 4. Fit on an agent host (Teknopus-style)

Suggested layout:

| Role | Where |
| --- | --- |
| `aor` + control-plane repo | Linux agent host |
| Application code + PR | Same host or sibling checkout |
| Coding agent (Claude / Cursor / Codex / …) | Host agent runner **or** operator laptop |

Agent On Rails packages the task; your existing agent implements it.
Keep API keys in the environment / secret store of the coding agent — not in the control-plane git tree.

## Upgrade

```bash
pipx upgrade agent-on-rails-cli
# or, from a clone: git pull && pip install -e .
```

## Help

- Docs site: https://agent-on-rails.suherman.net/docs#linux
- CLI reference: [getting-started.md](./getting-started.md)
- Authority rules: control-plane `AGENTS.md`
