# SD-005 Local API + SQLite persistence

## Requirement

The system SHALL provide a local HTTP JSON API that:

- Creates, reads, updates surveys
- Transitions survey lifecycle (open / close)
- Accepts anonymous public responses for `open` surveys
- Returns aggregate results for a survey
- Health check at `GET /health`

Persistence SHALL use SQLite with tables at least for:

- `surveys`
- `responses` (one row per submission; answers as JSON)

The API contract SHALL match `specs/api/openapi.yaml`.

Operator-mutating routes (create/update/open/close) MAY use a simple shared demo token header for LAN demos (`X-SurveyDesk-Token`) — not full auth productization.

Public respond routes SHALL NOT require that token.

## Acceptance criteria

```gherkin
Scenario: Health and create
  Given the API is running
  When GET /health
  Then status is 200
  When POST /v1/surveys with a title
  Then status is 201
  And the survey appears in GET /v1/surveys
```
