Feature: Adaptive operator layout (iPad / Android tablet)
  Specs: SD-008, ADR-007, contracts/mobile-operator-ux.md

  Scenario: Wide layout shows sidebar and opens detail
    Given the operator app is running in a wide layout (iPad Simulator or Android tablet emulator)
    And at least one survey exists in the list
    When the operator selects a survey in the left sidebar
    Then the detail pane shows Builder, Lifecycle, and Results for that survey
    And the chrome logo is the transparent PNG (no opaque plate)

  Scenario: Phone layout uses stack navigation
    Given the operator app is running on an iPhone Simulator or Android phone emulator
    When the operator opens a survey from the list
    Then the detail screen is pushed on a navigation stack
