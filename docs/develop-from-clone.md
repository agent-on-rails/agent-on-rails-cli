# Develop from a clone (no reinstall each time)

Use this when you follow `main` and want `git pull` → run `aor` without
`pipx install` on every change.

**End users** should still prefer [pipx](https://pipx.pypa.io/) (see
[`walkthrough.md`](./walkthrough.md)). **Contributors / early testers** use
editable install once, then pull.

Requires Python **3.11+**.

---

## One-time setup

```bash
git clone https://github.com/agent-on-rails/agent-on-rails-cli.git
cd agent-on-rails-cli
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
aor --version
```

`-e` is **editable**: the `aor` command points at this checkout. Edits and
`git pull` apply immediately — you do **not** reinstall after every pull.

Optional check:

```bash
pytest
```

---

## Every day (after pull)

```bash
cd agent-on-rails-cli
git pull
source .venv/bin/activate          # if the venv is not already active
aor
```

Run the TUI against any control-plane project:

```bash
cd ~/path/to/your-control-plane-project
aor
```

(`aor` must still come from the activated venv, or from a shell where that
venv’s `bin` is on `PATH`.)

---

## When do you need to reinstall?

| Situation | Action |
| --- | --- |
| Code / docs only changed on `main` | `git pull` — done |
| Dependencies in `pyproject.toml` changed | `pip install -e ".[dev]"` again (still no `pipx`) |
| Fresh machine / new clone | Repeat [One-time setup](#one-time-setup) |
| You want a stable global `aor` (not following git) | `pipx install git+https://github.com/agent-on-rails/agent-on-rails-cli.git` |

---

## pipx vs editable clone

| Mode | Best for | Update |
| --- | --- | --- |
| **pipx** | Operators / “just run it” | `pipx upgrade` / reinstall from git |
| **`pip install -e`** | Development, try latest `main` | `git pull` (+ reinstall deps only when lock/deps change) |

Do not mix both for the same shell session unless you know which `aor` wins
(`which aor`). Prefer one: either pipx **or** the clone venv.

---

## Stuck?

| Symptom | Fix |
| --- | --- |
| `aor: command not found` | Activate `.venv` (`source .venv/bin/activate`) |
| Old behavior after pull | Confirm `which aor` points at `…/agent-on-rails-cli/.venv/…` |
| Import / package errors after pull | `pip install -e ".[dev]"` again |
| Wrong project | `cd` into the folder you `aor init`’d |

Full product loop: [`walkthrough.md`](./walkthrough.md) ·
[`getting-started.md`](./getting-started.md)
