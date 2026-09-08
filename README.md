# Agent On Rails CLI

Terminal / operator app for [Agent On Rails](https://agent-on-rails.suherman.net).

**From specs to running software.** Define a contract, let agents deliver it —
with review, escalation, and evidence before done.

```bash
pipx install git+https://github.com/agent-on-rails/agent-on-rails-cli.git
aor
```

`aor` with no arguments opens a **terminal UI** (mouse-friendly harness — same idea as OpenCode / Claude Code / Gemini). It does not run a model; it packages bounded work for whatever coding agent you already use.

Commands still work for scripts: `aor init`, `aor spec`, `aor plan`, …

Or:

```bash
curl -fsSL https://raw.githubusercontent.com/agent-on-rails/agent-on-rails-cli/main/scripts/install.sh | bash
```

Full walkthrough: [`docs/getting-started.md`](./docs/getting-started.md) ·
Start → final review: [`docs/walkthrough.md`](./docs/walkthrough.md) ·
Dev from clone: [`docs/develop-from-clone.md`](./docs/develop-from-clone.md)

## Flow

```text
aor init → aor spec new → aor spec approve → aor plan → aor run → aor review
```

| Command | Purpose |
| --- | --- |
| `aor` / `aor tui` | Terminal UI (default on a TTY) |
| `aor guide` | How to use Agent On Rails |
| `aor init` | Create the project contract (docs + specs, no app code) |
| `aor spec` | Create, list, show, approve specs |
| `aor plan` | Turn an approved spec into a bounded task |
| `aor run` | Write a context package (or call the engine when configured) |
| `aor status` | Specs, tasks, team, contract health |
| `aor watch` | Follow a task |
| `aor review` | Human final-review handoff |
| `aor team` | Implementor / reviewer + default & escalate models |

The **control plane** is the contract folder this CLI creates (`product/`,
`specs/`, `adr/`). The product you download and run is **Agent On Rails**.

## Develop from a clone

One-time editable install, then `git pull` without reinstalling each time —
full guide: [`docs/develop-from-clone.md`](./docs/develop-from-clone.md).

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
aor --help
```

Requires Python 3.11+.

## Authority

- Specs: AOR-001 (bootstrap); AOR-003…007 via engine later
- Stack: Python (ADR-007)
- Do not invent a proprietary coding agent — `aor run` packages work for
  headless external agents (Cursor, Claude, Codex, …)

## Sibling repos

| Repo | Role |
| --- | --- |
| `agent-on-rails-control-plane` | Authority (what / how success is proven) |
| `agent-on-rails-engine` | Planner / state machine (coming) |
| `agent-on-rails-github` | Issues / PRs / webhooks (coming) |
| `agent-on-rails-agent-runtime` | Sandboxed execution (coming) |
| `agent-on-rails-android` | Mobile monitoring (Herry) |
