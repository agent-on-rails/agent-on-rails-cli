# SD-011 Mobile app — results view

## Requirement

The mobile app SHALL display survey results from the API:

- Total responses
- Charts or clear tallies for choice/rating fields
- Recent text answers for text fields

The results view SHALL refresh automatically at least every 2 seconds while the screen is open (or via SSE).

## Acceptance criteria

```gherkin
Scenario: Operator sees live tallies
  Given an open survey on the results tab
  When two respondents submit different single_choice answers
  Then the tallies update without leaving the screen
```
