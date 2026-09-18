"""aor guide — how to use Agent On Rails (not 'the control plane')."""

from __future__ import annotations

import click
from rich.markdown import Markdown

GUIDE = """\
# How to use Agent On Rails

Agent On Rails turns an approved spec into bounded work for coding agents —
with review, escalation, and evidence before anything is done.

The **control plane** is the contract folder inside your project
(`product/`, `specs/`, `adr/`). It is not the product name.

## Flow

1. **Install** — `pipx install git+https://github.com/agent-on-rails/agent-on-rails-cli.git`
2. **Open the TUI** — `aor` (mouse-friendly harness, like OpenCode / Claude Code)
3. **Init** — in the TUI press Init, or `aor init my-product` (docs+specs, no app code).
4. **Gather specs (optional, fast path)** — `aor gather run "…requirements…"`.
5. **Or grill (Discovery Team)** — `aor grill run --stub --file brief.md` then
   `aor grill approve prd` → `aor grill approve architecture` (AOR-011). Alias: `aor discover`.
6. **Write / refine a spec** — New spec in the TUI, or `aor spec new "Short title"`.
7. **Human approve** — Approve in the TUI, or `aor spec approve PREFIX-001`.
8. **Plan / Run** — packages a bounded task for Cursor, Claude, Codex, Gemini, …
9. **Review** — human final-review handoff.
10. **Evidence** — a spec is not DONE because an agent said so.

Step-by-step (start → final review): https://github.com/agent-on-rails/agent-on-rails-cli/blob/main/docs/walkthrough.md

**What to set up (checklist):** https://github.com/agent-on-rails/agent-on-rails-cli/blob/main/docs/what-to-setup.md

## Commands

| Command | Purpose |
| --- | --- |
| `aor` / `aor tui` | Terminal UI (default on a TTY) |
| `aor init` | Bootstrap a project contract |
| `aor gather` | NL requirements → confirm → SurveyDesk-shaped specs (fast path) |
| `aor grill` / `aor discover` | Discovery AI Team: PRD → architecture → specs drafts (AOR-011) |
| `aor spec` | Create, list, show, approve specs |
| `aor plan` | Build a task from an approved spec |
| `aor run` | Package (and later execute) a bounded task |
| `aor status` | Project health: specs, tasks, team |
| `aor watch` | Follow a task until final review |
| `aor review` | Human approve / reject |
| `aor team` | Configure implementor / reviewer / models |

## LLM for gather (ADR-003)

```bash
export AOR_LLM_BASE_URL=https://ai.dentalimplantsandveneers.com.au/v1
export AOR_LLM_API_KEY=…          # DIV gateway token or other Bearer key
export AOR_LLM_MODEL=writer       # optional
```

Or `~/.config/agent-on-rails/llm.yaml`. Without a key, `aor gather run` uses `--stub`.

## Authority

Docs define intent. Specs define the contract. Agent On Rails governs
execution. Agents implement. Evidence proves completion. Humans own merge.
"""


@click.command("guide")
@click.pass_context
def guide_cmd(ctx: click.Context) -> None:
    """Print the Agent On Rails operator guide."""
    ctx.obj["console"].print(Markdown(GUIDE))
