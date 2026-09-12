Feature: Survey lifecycle happy path
  As an operator
  I want to open and close a survey
  So that respondents can only answer while it is open

  Scenario: Reject responses when closed
    Given a survey with status "closed"
    When a respondent submits answers to its public slug
    Then the API rejects the submission
    And the response count is unchanged

  Scenario: Accept responses when open
    Given a survey with status "open" and a required rating field
    When a respondent submits a valid rating
    Then the API stores the response
    And totalResponses increases by 1
