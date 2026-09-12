# FormSpec

FormSpec is the portable form definition edited by the mobile drag-and-drop builder.

```yaml
FormSpec:
  version: 1
  fields:
    - id: string
      type: short_text | long_text | single_choice | multi_choice | rating_1_5 | yes_no
      label: string
      required: boolean
      order: number
      options: # required for choice types
        - id: string
          label: string
```

Example:

```json
{
  "version": 1,
  "fields": [
    {
      "id": "usefulness",
      "type": "rating_1_5",
      "label": "How useful was today’s session?",
      "required": true,
      "order": 0
    },
    {
      "id": "clarity",
      "type": "single_choice",
      "label": "Was the language clear?",
      "required": true,
      "order": 1,
      "options": [
        { "id": "yes", "label": "Yes" },
        { "id": "somewhat", "label": "Somewhat" },
        { "id": "no", "label": "No" }
      ]
    },
    {
      "id": "next_topic",
      "type": "short_text",
      "label": "What should we build next?",
      "required": false,
      "order": 2
    }
  ]
}
```
