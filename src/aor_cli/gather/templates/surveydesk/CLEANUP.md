# Cleanup before fresh regen

Wipe **generated** trees only. Keep specs, brand, and committed scripts.

```bash
# From repo root:
rm -rf apps packages tests
rm -f data/*.sqlite data/*.sqlite-* .env
# Optional: kill demo ports
# lsof -tiTCP:8787 -sTCP:LISTEN | xargs kill -9
# lsof -tiTCP:3091 -sTCP:LISTEN | xargs kill -9
```

Then rebuild:

```bash
@specs/regeneration/prompts/REGENERATE.md
# or:
npm run execute:specs
```

Do **not** delete `specs/`, `brand/`, or hand-maintained `scripts/` unless you intend a full re-gather from AOR.
