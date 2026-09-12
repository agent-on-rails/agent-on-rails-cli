# Response

A Response is one anonymous submission.

```yaml
Response:
  id: string
  surveyId: string
  answers:
    # map fieldId -> value
    # short_text/long_text: string
    # single_choice: option id
    # multi_choice: option id[]
    # rating_1_5: number 1..5
    # yes_no: boolean
  createdAt: string
  # Optional soft abuse signal for local demos only — not an identity
  clientFingerprint: string | null
```

The system SHALL NOT require PII. Fingerprints, if used, are for rate limiting demos only and MUST NOT be displayed in results UI.
