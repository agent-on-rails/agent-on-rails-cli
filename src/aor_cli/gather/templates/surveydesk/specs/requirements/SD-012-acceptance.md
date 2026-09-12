# SD-012 Acceptance tests and demo script

## Requirement

The repository SHALL include:

- Automated acceptance tests covering create → open → respond → results → close
- Gherkin features under `specs/acceptance/`
- A short operator demo script aligned with `specs/product/demo-journey.md`

Tests SHALL run against a temporary SQLite file, not the developer’s personal database.

## Acceptance criteria

```gherkin
Scenario: End-to-end happy path test
  Given a fresh temporary database
  When the acceptance suite runs
  Then create, open, respond, results, and close all pass
```
