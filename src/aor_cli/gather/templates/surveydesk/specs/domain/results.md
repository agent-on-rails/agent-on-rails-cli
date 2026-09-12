# Results aggregate

```yaml
SurveyResults:
  surveyId: string
  totalResponses: number
  fields:
    - fieldId: string
      type: string
      label: string
      # one of:
      rating:
        average: number | null
        buckets: { "1": n, "2": n, "3": n, "4": n, "5": n }
      choice:
        options: [{ optionId, label, count }]
      yesNo:
        yes: number
        no: number
      text:
        count: number
        recent: string[] # capped, newest first
```
