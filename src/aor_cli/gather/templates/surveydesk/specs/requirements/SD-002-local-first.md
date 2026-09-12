# SD-002 Local-first runtime

## Requirement

The system SHALL run entirely on the operator’s machine for v1:

- SQLite file on disk (path configurable via env)
- API bound to loopback by default (`127.0.0.1`)
- Optional `0.0.0.0` bind for same-LAN phone testing only

UI copy and documentation SHALL be **English**.

The system SHALL NOT depend on Firestore, Cloud Run, or third-party survey SaaS for core create/respond/results flows.

## Acceptance criteria

```gherkin
Scenario: Local SQLite persistence
  Given SURVEY_DESK_DATABASE_PATH points to a writable local file
  When a survey is created via the API
  Then a row exists in the SQLite surveys table
  And restarting the API still returns that survey
```
