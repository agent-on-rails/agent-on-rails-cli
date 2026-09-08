# AGENTS.md — agent-on-rails-cli

**Read the control-plane [`AGENTS.md`](https://github.com/agent-on-rails/agent-on-rails-control-plane/blob/main/AGENTS.md) first.**

## Boundaries

- This repo is the **Agent On Rails operator UX** (`aor`). Default on a TTY is the Textual TUI (`aor tui`). It does not own product authority, the future engine, or agent sandboxes.
- `aor init` creates/validates the docs+specs contract (AOR-001), not application code.
- Until `agent-on-rails-engine` exists, local mode is the product: specs, human approve, plan, context package, review. Be honest — do not pretend a remote engine is running.
- Engine API calls go through `aor_cli.engine.client` when `AOR_ENGINE_URL` is set.

## Prohibited

- Marking specs `DONE` without evidence
- Hard-coding a provider/model monopoly (ADR-003 neutrality)
- Putting secrets in repo or command-history examples
- Implementing GitHub App / sandbox logic here
- Inventing a proprietary coding agent (ADR-007) — package work for headless external agents

## Tests

Run `pytest` for unit tests. Live engine tests are gated on `AOR_ENGINE_URL`.
