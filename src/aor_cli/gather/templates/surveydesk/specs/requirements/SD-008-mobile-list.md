# SD-008 Mobile app — survey list and control

## Requirement

The mobile app SHALL be the **internal tooling** surface for operators on **iPhone, iPad, Android phone, and Android tablet**.

It SHALL provide:

- List of surveys with status badges (`draft` / `open` / `closed`)
- Create survey (title, optional description)
- Open survey detail (builder, lifecycle actions, results tabs)
- Copy / show public respondent URL when a slug exists
- **Compact / phone:** stack navigation (list → detail)
- **Regular / tablet & iPad (width ≥ 600dp or iPad size class):** persistent **left sidebar** (brand + survey list) and detail pane; tapping a survey SHALL show that survey’s detail (not a blank pane)

The mobile app SHALL talk only to the local API (configurable base URL).

Chrome SHALL use the **transparent** logo (`brand/surveydesk-logo.png`) so it blends with `surfaceSubtle` / surface backgrounds (SHALL NOT use the opaque JPG logo plate in nav/splash/sidebar).

## Acceptance criteria

```gherkin
Scenario: Create from mobile
  Given the API is reachable from the mobile app
  When the operator creates a survey titled "Live poll"
  Then the survey appears in the list with status draft

Scenario: Tablet or iPad sidebar opens detail
  Given the operator app is running in a wide layout (iPad or Android tablet)
  And at least one survey exists
  When the operator selects a survey in the left sidebar
  Then the detail pane shows that survey’s Builder / Lifecycle / Results
```
