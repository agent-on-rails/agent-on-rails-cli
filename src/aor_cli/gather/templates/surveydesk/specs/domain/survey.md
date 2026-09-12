# Survey

A Survey is the top-level operator artifact.

```yaml
Survey:
  id: string
  title: string
  description: string | null
  status: draft | open | closed
  publicSlug: string
  showPublicResults: boolean
  formSpec: FormSpec
  createdAt: string # ISO-8601
  updatedAt: string
  openedAt: string | null
  closedAt: string | null
```

Public URL path: `/s/{publicSlug}` on the respondent web app.
