# Walkthrough — start → ready for final review

Step-by-step from a clean machine until a human can do **final review**.
Use either the **TUI** (recommended) or the **commands**. Same loop either way.

```text
install → init → write spec → human approve → plan → run → agent implements → evidence → final review
```

Marketing: [agent-on-rails.suherman.net/docs](https://agent-on-rails.suherman.net/docs)

---

## 0. What you need

- Python **3.11+**
- A terminal (iTerm, Terminal, Warp, …)
- A coding agent you already use (Cursor, Claude Code, Codex, Gemini, …)
- Optional: [pipx](https://pipx.pypa.io/)

Agent On Rails is a **harness**. It does not invent a coding agent. It packages a bounded task; your agent does the implementation.

---

## 1. Install

```bash
pipx install git+https://github.com/agent-on-rails/agent-on-rails-cli.git
aor --version
```

Or:

```bash
curl -fsSL https://raw.githubusercontent.com/agent-on-rails/agent-on-rails-cli/main/scripts/install.sh | bash
```

**Following `main` / development?** Clone once with editable install — then
`git pull` and run `aor` without reinstalling each time:
[`develop-from-clone.md`](./develop-from-clone.md).

---

## 2. Start the TUI

```bash
mkdir -p ~/src/followup && cd ~/src/followup
aor
```

You should see the Agent On Rails terminal UI (mouse works). Footer keys:

| Key | Action |
| --- | --- |
| `i` | Init |
| `n` | New spec |
| `a` | Approve (human) |
| `p` | Plan |
| `r` | Run (package task) |
| `v` | Final review approve |
| `x` | Reject → retry |
| `g` | Toggle guide |
| `q` | Quit |

*(Prefer commands? Skip to [Command-line path](#command-line-path-same-loop).)*

---

## 3. Init — create the contract folder

1. Click **Init** (or press `i`).
2. Path: e.g. `/Users/you/src/followup`
3. Product name: e.g. `FollowUp`
4. Confirm **Create**

This creates docs + specs only (`product/`, `specs/`, `adr/`, `AGENTS.md`, …). **No application code** goes here. That is the control plane — the contract, not the app.

### 3b. Gather specs from natural language (optional, AOR-010)

Paste product requirements and generate a **SurveyDesk-shaped** pack
(`specs/product`, `requirements`, `domain`, `api`, `adr`, `acceptance`, `regeneration`):

```bash
export AOR_LLM_BASE_URL=https://ai.dentalimplantsandveneers.com.au/v1
export AOR_LLM_API_KEY=…   # gateway Bearer token from DIV AI / compatible provider

aor gather run "Build a local survey desk: mobile operators, anonymous web, SQLite API"
# shows outline → confirm y/N → writes files

# Or edit the outline first:
aor gather run --file ./requirements.md --edit
aor gather apply --edit
```

If the pasted text is **SurveyDesk** (local-first survey desk, FormSpec, native
iOS/Android operators, anonymous web), gather writes the SurveyDesk **reference
pack** (SD-001…SD-012, FormSpec domain, full OpenAPI, ADR-001…009, P1–P6) instead
of sentence-split stubs. Use `--force` to replace a previous draft `specs/` tree.

Without an API key, add `--stub` for an offline heuristic extract. Gathering only drafts
specs — humans still approve before implementation.

Check:

```bash
ls
# AGENTS.md  README.md  adr/  plans/  policies/  product/  specs/  .aor/
```

---

## 4. New spec — draft the contract

1. Click **New spec** (or `n`).
2. Title: e.g. `Add contact and follow-up date`
3. Implementation repo: e.g. `followup-web` (sibling app repo name — create that repo separately when you implement)
4. Confirm **Create**

AOR writes something like:

```text
specs/FOLLOW-001-add-contact-and-follow-up-date/
  spec.md
  acceptance.md
  evidence.md
```

**Edit the draft before approving:**

- `spec.md` — behavior, in/out of scope
- `acceptance.md` — checkboxes that are testable
- `evidence.md` — what proves done (PR, tests, log)

Status is still **DRAFT**. Agents cannot run yet.

---

## 5. Human approve — gate

1. Click the spec row in the table.
2. Click **Approve** (or `a`).
3. Confirm.

Only a human should do this. After approve, status becomes **APPROVED**.

---

## 6. Plan + Run — package work for an agent

1. With the spec selected, click **Plan** (or `p`) → creates `TASK-001`.
2. Click **Run** (or `r`) → writes the context package.

Look for:

```text
.aor/packages/TASK-001/CONTEXT.md   # full contract package
.aor/packages/TASK-001/prompt.md    # short prompt for your agent
```

The log will say something like: *Packaged TASK-001. Open …/prompt.md in Cursor / Claude / Codex.*

You are now **ready to hand off to a coding agent**. Final review is still later — after the agent ships evidence.

---

## 7. Implement — outside the control plane

1. Open `prompt.md` (or `CONTEXT.md`) in Cursor / Claude / Codex / Gemini.
2. Implement in the **sibling app repo** named in the spec (e.g. `followup-web`), **not** in the control-plane folder.
3. Follow: branch → implement → tests named in the spec → commit → PR.
4. Do **not** mark the spec DONE yourself. Implementor ≠ reviewer.

When the PR + tests exist, you have enough evidence to enter final review.

---

## 8. Final review — human again

Back in the TUI (`aor`):

1. Select the spec (or matching task).
2. Click **Review** (or `v`) when you accept the PR + evidence.
3. Or press `x` to reject → RETRY.

After approve, AOR records the decision under `.aor/reviews/` and moves the spec toward **FINAL_REVIEW**.

You are **ready for final review** once:

- [ ] Spec was human-approved before the agent ran
- [ ] Task was planned and packaged (`aor run` / Run button)
- [ ] Agent opened a PR in the implementation repo
- [ ] Acceptance checks / tests named in the spec pass
- [ ] Evidence listed in `evidence.md` exists (PR link, test results, execution notes)
- [ ] A human clicks Review (or `aor review TASK-001 --approve`)

Heavy collaboration (discussion, merge) stays on GitHub.

---

## Command-line path (same loop)

```bash
# 1. Install (once)
pipx install git+https://github.com/agent-on-rails/agent-on-rails-cli.git

# 2. Init
mkdir -p ~/src/followup && cd ~/src/followup
aor init . --name FollowUp

# 3. Draft spec
aor spec new "Add contact and follow-up date" --repo followup-web
# edit specs/FOLLOW-001-*/{spec,acceptance,evidence}.md

# 4. Human gate
aor spec approve FOLLOW-001

# 5. Plan + package
aor plan FOLLOW-001
aor run FOLLOW-001
# open .aor/packages/TASK-001/prompt.md in your coding agent

# 6. After PR + tests
aor review TASK-001 --approve --notes "PR looks good; tests green"
aor status
```

---

## Quick map: who does what

| Step | Who |
| --- | --- |
| Init / write draft spec | Human (or draft help from an agent) |
| Approve spec | **Human only** |
| Plan / Run | Agent On Rails |
| Implement + PR + tests | Coding agent (Implementor) |
| Final review / merge | **Human only** |

---

## Stuck?

| Symptom | Fix |
| --- | --- |
| Plan/Run blocked | Spec still DRAFT — Approve first |
| “No project found” | `cd` into the folder you `init`’d, or Init again |
| Agent changed the contract folder | Wrong cwd — implement in the sibling **app** repo |
| Not sure what to open | `.aor/packages/TASK-00N/prompt.md` |

More detail: [`getting-started.md`](./getting-started.md) ·
[`develop-from-clone.md`](./develop-from-clone.md) ·
site: [agent-on-rails.suherman.net/docs](https://agent-on-rails.suherman.net/docs)
