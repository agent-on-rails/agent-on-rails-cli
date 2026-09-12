# SD-001 Product surfaces

## Requirement

The system SHALL expose three cooperating surfaces:

| Surface | Role | Audience |
|---------|------|----------|
| iOS app (Swift) | Operator: build, start/end, results (Simulator demo) | Operator |
| Android app (Kotlin) | Operator: build, start/end, results (Emulator demo) | Operator |
| Public web (React + Next.js) | Anonymous respond (+ optional live results) | Respondent |
| Local API | HTTP JSON API over SQLite | All clients |

The system SHALL NOT require a cloud account for the v1 demo.

## Acceptance criteria

```gherkin
Scenario: Three surfaces are documented and reachable when implemented
  Given the SurveyDesk monorepo is installed
  When the operator starts the local demo stack
  Then the API health endpoint responds
  And the public web home or survey route is reachable
  And the mobile app can list surveys from the API
```
