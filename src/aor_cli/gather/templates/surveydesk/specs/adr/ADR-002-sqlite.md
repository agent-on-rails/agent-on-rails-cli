# ADR-002 SQLite for persistence

## Decision

Use a single local SQLite database file for surveys and responses.

## Why

Matches the webinar constraint “still running locally”, easy to wipe/reset, no cloud credentials for core flows.

## Consequences

Not a multi-region SaaS store. Backup = copy the file. Concurrent writers are limited to one API process.
