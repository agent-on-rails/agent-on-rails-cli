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
2. **Init** — `aor init my-product` creates the docs+specs contract (no app code).
3. **Write a spec** — `aor spec new "Short title"` (or edit `specs/` by hand).
4. **Human approve** — `aor spec approve PREFIX-001` (agents cannot skip this).
5. **Plan** — `aor plan PREFIX-001` turns the spec into a bounded task.
6. **Run** — `aor run PREFIX-001` writes a context package for a headless agent
   (Cursor, Claude, Codex, …). The engine will take this over when it ships.
7. **Review** — `aor review TASK-001` is the human final-review handoff.
8. **Evidence** — a spec is not DONE because an agent said so.

## Commands

| Command | Purpose |
| --- | --- |
| `aor init` | Bootstrap a project contract |
| `aor spec` | Create, list, show, approve specs |
| `aor plan` | Build a task from an approved spec |
| `aor run` | Package (and later execute) a bounded task |
| `aor status` | Project health: specs, tasks, team |
| `aor watch` | Follow a task until final review |
| `aor review` | Human approve / reject |
| `aor team` | Configure implementor / reviewer / models |

## Authority

Docs define intent. Specs define the contract. Agent On Rails governs
execution. Agents implement. Evidence proves completion. Humans own merge.
"""


@click.command("guide")
@click.pass_context
def guide_cmd(ctx: click.Context) -> None:
    """Print the Agent On Rails operator guide."""
    ctx.obj["console"].print(Markdown(GUIDE))
