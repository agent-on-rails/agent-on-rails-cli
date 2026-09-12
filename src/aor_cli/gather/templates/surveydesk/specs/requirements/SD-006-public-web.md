# SD-006 Anonymous public respondent web

## Requirement

The public web app SHALL:

- Render a survey by `publicSlug` at a shareable path (e.g. `/s/{slug}`)
- Require **no login** for respondents
- Validate required fields client-side and server-side
- Submit answers to the public API endpoint
- Show a clear success (thank-you) state
- Show a clear error when the survey is not open

The public web SHALL NOT collect name/email unless those are explicit FormSpec fields the operator added.

## Acceptance criteria

```gherkin
Scenario: Anonymous submit
  Given an open survey with slug "session-feedback"
  When a visitor opens /s/session-feedback without signing in
  And submits valid answers
  Then the API stores one response
  And the visitor sees a thank-you screen
```
