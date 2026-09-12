# SD-007 Instant results

## Requirement

The system SHALL compute aggregate results for a survey:

- Total response count
- Per-field aggregates:
  - `rating_1_5` / `yes_no`: counts and/or average where applicable
  - `single_choice` / `multi_choice`: option tallies
  - `short_text` / `long_text`: recent answers list (capped) and count

Results SHALL be available:

1. To the operator via API (`GET /v1/surveys/{id}/results`) for the mobile app
2. Optionally on the public web when `showPublicResults` is true and status is `open` or `closed`

“Instant” for v1 means: after a successful submit, a subsequent results fetch within **2 seconds** reflects the new response (polling ≤ 2s or push/SSE). A full realtime bus is not required.

## Acceptance criteria

```gherkin
Scenario: Results update after submit
  Given an open survey with zero responses
  When a respondent submits a rating_1_5 answer of 5
  And the operator fetches results within 2 seconds
  Then totalResponses is 1
  And the rating bucket for 5 is at least 1
```
