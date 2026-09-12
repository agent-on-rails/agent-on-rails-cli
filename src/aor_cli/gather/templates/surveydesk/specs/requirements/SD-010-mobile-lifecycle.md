# SD-010 Mobile app — start / end survey workflow

## Requirement

The mobile app SHALL expose clear actions:

| Action | Transition | Effect |
|--------|------------|--------|
| Start / Open | `draft` or `closed` → `open` | Public web accepts responses |
| End / Close | `open` → `closed` | Public web rejects new responses |

The UI SHALL confirm destructive or confusing transitions with a short confirmation.

After Start, the UI SHALL show the public URL prominently.

## Acceptance criteria

```gherkin
Scenario: Start and end from mobile
  Given a draft survey with at least one field
  When the operator taps Start
  Then status is open
  And the public URL is visible
  When the operator taps End
  Then status is closed
  And public submit returns an error
```
