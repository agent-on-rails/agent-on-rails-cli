# agent-on-rails-cli

Terminal / operator UX for [Agent On Rails](https://agent-on-rails.suherman.net).

Authority lives in [`agent-on-rails-control-plane`](https://github.com/agent-on-rails/agent-on-rails-control-plane). This CLI implements bootstrap and day-to-day operator flows (ADR-007, AOR-001).

## Install

```bash
cd agent-on-rails-cli
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
aor --help
```

## Commands (MVP slice)

| Command | Purpose |
| --- | --- |
| `aor init` | Create or validate a control-plane repo structure (docs + specs) |
| `aor status` | Show local control-plane health + engine/GitHub connectivity (stub-aware) |
| `aor team` | Configure AI Team (implementor / reviewer + default & escalate models) |
| `aor run` | Start / resume a task (engine stub until engine ships) |
| `aor watch` | Stream task state until `FINAL_REVIEW` or failure |
| `aor review` | Human final-review handoff in the terminal |

## Authority

- Specs: AOR-001 (bootstrap), AOR-003…007 (via engine later)
- Stack: Python (ADR-007)
- Do not invent a proprietary coding agent — headless adapters live in `agent-on-rails-agent-runtime`

## Sibling repos

| Repo | Role |
| --- | --- |
| `agent-on-rails-control-plane` | Authority |
| `agent-on-rails-engine` | Planner / state machine (coming) |
| `agent-on-rails-github` | Issues / PRs / webhooks (coming) |
| `agent-on-rails-android` | Mobile monitoring (Herry) |
