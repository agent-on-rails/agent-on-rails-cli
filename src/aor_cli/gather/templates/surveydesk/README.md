# SurveyDesk reference pack (AOR-010)

Copied from the SurveyDesk exemplar (`survey-desk` specs). When `aor gather`
detects a SurveyDesk-shaped product (local-first survey desk, FormSpec, native
mobile operators, anonymous web), it writes this tree instead of sentence-split
stubs.

## What gather emits

| Path | Role |
|------|------|
| `specs/` | Full SD-* / ADR / OpenAPI / regen prompts + contracts |
| `AGENTS.md` | Agent authority |
| `brand/` | README + transparent logo PNG + full JPG (required before Wave 1) |
| `.gitignore` | Ignores `apps/`, `packages/`, `tests/`, sqlite, `.env` |
| `CLEANUP.md` | Wipe generated trees before re-regen |
| `data/README.md` | SQLite location |
| `package.json` | workspaces + `execute:specs` + `allowScripts` for better-sqlite3 |
| `.env-example` | API/web ports + Android `10.0.2.2` note |

## Lessons baked into regen contracts (avoid manual post-fixes)

See `specs/regeneration/contracts/shell-demo-pitfalls.md`:

- bash 3.2 + `set -u`: `${var}...` not `$var…`; guard empty `"${arr[@]}"`
- `demo.sh` reuses healthy 8787/3091 (no EADDRINUSE)
- Root `allowScripts` for native modules
- Brand assets seeded at gather time

Do not invent a different layout. Update this pack when the exemplar changes.
