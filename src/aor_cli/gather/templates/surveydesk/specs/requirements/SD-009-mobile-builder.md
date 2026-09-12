# SD-009 Mobile app — form builder (drag and drop)

## Requirement

The mobile app SHALL include a FormSpec builder that lets the operator:

- Add a field of a supported type (SD-004)
- Edit label, required flag, and options
- Remove a field
- Reorder fields via **drag and drop** (or long-press drag) on touch devices

Saving SHALL persist FormSpec through the API.

Structural edits SHALL be blocked while status is `open` (operator must close first), unless a future ADR explicitly allows hot-edit of labels only — v1 blocks all FormSpec writes while `open`.

## Acceptance criteria

```gherkin
Scenario: Drag reorder on mobile
  Given a draft survey open in the builder
  When the operator drags the last field to the top and saves
  Then the API FormSpec order matches the new sequence
```
