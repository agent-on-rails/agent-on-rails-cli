# What you need to set up — Agent On Rails

Short checklist for first use (laptop or agent host).  
`aor` is a **harness** (Hermes-style): it packages work. It does **not** replace Cursor / Claude / Codex.

Product: https://agent-on-rails.suherman.net  
Walkthrough: [walkthrough.md](./walkthrough.md)

## Checklist

| # | Item | Required? | Notes |
| --- | --- | --- | --- |
| 1 | **Python 3.11+** + **git** | Yes | macOS: Xcode CLT / Homebrew; Linux: `apt install python3 git` |
| 2 | **`aor` CLI** | Yes | `pipx install git+https://github.com/agent-on-rails/agent-on-rails-cli.git` — if `aor guide` already works, you’re done |
| 3 | **Project contract** (`aor init`) | Yes | Creates docs+specs folder only — no app code |
| 4 | **Coding agent** | Yes | Cursor, Claude Code, Codex, Gemini, … — whatever you already use to implement |
| 5 | **Human approver** | Yes | Someone who can `aor spec approve` and final-review |
| 6 | **`aor team` config** | Optional | Default implementor/reviewer model names for later engine wiring |
| 7 | **GitHub `gh` + auth** | Optional | Only if you use `aor init --create-github` |
| 8 | **API keys for the coding agent** | On the agent | Keep keys in Cursor/Claude/Codex env — **not** in the control-plane git tree |
| 9 | **`AOR_ENGINE_URL`** | No (MVP) | Local mode packages prompts without a remote engine |
| 10 | **Desktop setup app** | No | Optional wizard on macOS/Windows; Linux uses CLI only |

## Minimum path (you already have `aor`)

```bash
# 1. New contract folder
mkdir -p ~/projects && cd ~/projects
aor init ./ticktopus --name "Ticktopus"   # or any product name
cd ticktopus

# 2. Open TUI (or keep using commands)
aor

# 3. In TUI / commands: New spec → edit files → Approve → Plan → Run
# 4. Open .aor/packages/TASK-001/prompt.md in Cursor / Claude / Codex
# 5. Implement in the *app* repo → PR + tests → aor review …
```

## Two machines (common)

| Role | Where |
| --- | --- |
| `aor` + control-plane repo | Your laptop **or** Linux agent host (Teknopus) |
| Coding agent implements | Same machine **or** operator laptop |
| Human approve / final review | You (or a teammate) |

## Not required to start

- GPU / heavy server
- Replacing Hermes’ coding agent with a proprietary one
- Running the full Agent On Rails engine in production

## Links

- Linux / Teknopus steps: [linux-server.md](./linux-server.md)
- macOS / Windows wizard: https://github.com/agent-on-rails/agent-on-rails-desktop
- Docs site: https://agent-on-rails.suherman.net/docs#checklist
