Feature: Instant results
  As an operator
  I want results to update quickly after each submission
  So that I can show live tallies in the session

  Scenario: Results reflect new response
    Given an open survey with zero responses
    When a respondent submits answers
    And the operator requests results within 2 seconds
    Then totalResponses is 1
