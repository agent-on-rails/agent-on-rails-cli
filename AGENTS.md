# AGENTS.md — agent-on-rails-cli

**Read the control-plane [`AGENTS.md`](https://github.com/agent-on-rails/agent-on-rails-control-plane/blob/main/AGENTS.md) first.**

## Boundaries

- This repo is **operator UX** (CLI). It does not own product authority, orchestration core, or agent sandboxes.
- Bootstrap must create/validate control-plane **docs+specs** structure (AOR-001), not application code.
- Engine API calls go through `aor_cli.engine.client`; until the engine exists, use honest stubs and exit codes.

## Prohibited

- Marking specs `DONE` without evidence
- Hard-coding provider/model monopoly (ADR-003 neutrality)
- Putting secrets in repo or command history examples
- Implementing GitHub App / sandbox logic here

## Tests

Run `pytest` for unit tests. Integration against a real engine is gated on `AOR_ENGINE_URL`.
