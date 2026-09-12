# SD-003 Survey entity and lifecycle

## Requirement

A **Survey** SHALL have at least:

| Field | Description |
|-------|-------------|
| `id` | Stable unique id (UUID or ULID) |
| `title` | Human title |
| `description` | Optional short description |
| `status` | `draft` \| `open` \| `closed` |
| `formSpec` | FormSpec document (see SD-004) |
| `publicSlug` | URL-safe slug for public web |
| `showPublicResults` | Boolean — whether respondents may see aggregate results |
| `createdAt` / `updatedAt` | Timestamps |
| `openedAt` / `closedAt` | Nullable lifecycle timestamps |

Lifecycle rules:

- New surveys SHALL start as `draft`
- Only `draft` or `closed` surveys MAY be edited structurally (FormSpec)
- `open` SHALL accept anonymous responses
- `closed` and `draft` SHALL reject new responses
- Operator SHALL be able to transition `draft → open`, `open → closed`, and optionally `closed → open` (re-open)

## Acceptance criteria

```gherkin
Scenario: Closed survey rejects responses
  Given a survey with status "closed"
  When a respondent POSTs a response to the public API
  Then the API returns 409 or 403
  And no new response row is stored
```
