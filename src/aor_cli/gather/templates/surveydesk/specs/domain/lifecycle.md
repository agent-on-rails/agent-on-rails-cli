# Lifecycle

```
        create
          │
          ▼
       ┌──────┐
       │draft │◀──────────────┐
       └──┬───┘               │
          │ start/open        │ optional re-open
          ▼                   │
       ┌──────┐               │
       │ open │───────────────┤
       └──┬───┘               │
          │ end/close         │
          ▼                   │
       ┌──────┐               │
       │closed│───────────────┘
       └──────┘
```

| Status | Edit FormSpec | Accept responses | Typical operator action |
|--------|---------------|------------------|-------------------------|
| draft | yes | no | Build fields |
| open | no | yes | Share public URL |
| closed | yes | no | Review results / reopen |
