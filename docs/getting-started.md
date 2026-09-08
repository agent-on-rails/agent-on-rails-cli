# How to use Agent On Rails

Agent On Rails turns an approved specification into bounded work for coding
agents — with review and evidence before anything is marked done.

This is the operator guide for the downloadable `aor` CLI. The **control plane**
is the contract folder inside your project (`product/`, `specs/`, `adr/`). It is
not the product name.

Marketing site: [agent-on-rails.suherman.net](https://agent-on-rails.suherman.net)

## Install

Requires Python 3.11+. Prefer [pipx](https://pipx.pypa.io/):

```bash
pipx install git+https://github.com/agent-on-rails/agent-on-rails-cli.git
aor
```

On a TTY, `aor` opens the **terminal UI** (mouse-friendly). Use `aor tui` to force it. Subcommands (`aor init`, `aor spec`, …) still work for scripts.

Or from a clone:

```bash
git clone https://github.com/agent-on-rails/agent-on-rails-cli.git
cd agent-on-rails-cli
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
aor --help
```

One-liner (uses pipx when available, otherwise `pip install --user`):

```bash
curl -fsSL https://raw.githubusercontent.com/agent-on-rails/agent-on-rails-cli/main/scripts/install.sh | bash
```

## The loop

```text
init → spec → approve → plan → run → review → evidence → done
```

| Step | Command | Who |
| --- | --- | --- |
| Open the terminal UI | `aor` | Human |
| Bootstrap the project contract | Init in TUI, or `aor init my-product` | Human |
| Write a spec (`spec.md` + `acceptance.md` + `evidence.md`) | New spec in TUI, or `aor spec new "Short title"` | Human / draft agent |
| Approve the contract | Approve in TUI, or `aor spec approve PREFIX-001` | **Human only** |
| Turn the spec into a bounded task | Plan in TUI, or `aor plan PREFIX-001` | Agent On Rails |
| Package the task for a coding agent | Run in TUI, or `aor run PREFIX-001` | Agent On Rails |
| Implement in the **sibling app repo** | Cursor / Claude / Codex / … | Implementor |
| Human final review | Review in TUI, or `aor review TASK-001 --approve` | **Human only** |

Implementation agents are blocked until the spec is `APPROVED`.
Implementors never mark their own work `DONE`.

## Walkthrough

End-to-end from install until a human can do final review (TUI + commands):

→ **[`docs/walkthrough.md`](./walkthrough.md)**

Short command cheat sheet:

```bash
# 1. New project (docs + specs only — no application code)
aor init ./followup --name FollowUp
cd followup

# 2. Draft a contract
aor spec new "Add contact and follow-up date" --repo followup-web
# edit specs/FOLLOW-001-*/{spec,acceptance,evidence}.md

# 3. Human gate
aor spec approve FOLLOW-001

# 4. Bounded task + context package
aor plan FOLLOW-001
aor run FOLLOW-001
# open .aor/packages/TASK-001/prompt.md in your coding agent

# 5. After the PR and tests exist
aor review TASK-001 --approve --notes "PR looks good; evidence attached"
aor status
```

## What `aor run` does today

The orchestration engine is not shipped yet. In local mode, `aor run`:

1. Refuses to start if the spec is still `DRAFT` or `REVIEW`
2. Plans a `TASK-NNN` if needed
3. Writes `.aor/packages/TASK-NNN/CONTEXT.md` — SPEC + ACCEPTANCE + ADRs +
   `AGENTS.md` + the current task (AOR-004 context package)
4. Tells you to open `prompt.md` in an external headless agent

Agent On Rails does **not** invent its own coding agent. When
`AOR_ENGINE_URL` is set, `aor run` / `watch` / `review` call that engine
instead.

## Authority

1. Product docs (`product/`)
2. ADRs (`adr/`)
3. Policies (`policies/`)
4. Specs + acceptance (`specs/`)
5. Plans (`plans/`)
6. Sibling application repositories

If code disagrees with an approved spec, the spec wins until a human revises it.

## Related

- Authority repo: [`agent-on-rails-control-plane`](https://github.com/agent-on-rails/agent-on-rails-control-plane)
- Full contract how-to: [`guides/using-the-control-plane.md`](https://github.com/agent-on-rails/agent-on-rails-control-plane/blob/main/guides/using-the-control-plane.md)
- ADR-007: Python CLI-first, headless external agents
- AOR-001: project bootstrap
