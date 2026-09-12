Feature: Form builder
  As an operator
  I want to drag fields into order
  So that the public form matches my design

  Scenario: Persist field order
    Given a draft survey with fields A, B, C
    When the operator reorders fields to C, A, B and saves
    Then GET survey returns FormSpec order C, A, B
