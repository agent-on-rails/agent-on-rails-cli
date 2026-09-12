# SD-004 FormSpec — drag-and-drop form schema

## Requirement

The system SHALL store each survey’s fields as a **FormSpec** JSON document.

FormSpec SHALL support at least these field types in v1:

| Type | Purpose |
|------|---------|
| `short_text` | Single-line text |
| `long_text` | Multi-line text |
| `single_choice` | Radio / one option |
| `multi_choice` | Checkboxes |
| `rating_1_5` | Integer 1–5 |
| `yes_no` | Boolean |

Each field SHALL include:

- `id` (stable within the survey)
- `type`
- `label`
- `required` (boolean)
- `options` (for choice types)
- `order` (integer for display order)

The mobile builder SHALL allow the operator to **add, reorder (drag-and-drop or equivalent), edit, and remove** fields, then persist FormSpec via the API.

The system SHALL NOT execute arbitrary scripts inside FormSpec.

## Acceptance criteria

```gherkin
Scenario: Reorder fields persists
  Given a draft survey with three fields
  When the operator reorders field C before field A and saves
  Then GET survey returns fields sorted by the new order
```
