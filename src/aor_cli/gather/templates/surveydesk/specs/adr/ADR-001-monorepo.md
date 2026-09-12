# ADR-001 Monorepo local demo

## Decision

Ship SurveyDesk as a single git monorepo with:

- `apps/api` — local HTTP API + SQLite
- `apps/web` — public respondent UI (React + Next.js)
- `apps/ios` — operator app (Swift + SwiftUI)
- `apps/android` — operator app (Kotlin + Jetpack Compose)

## Why

One-hour live build and Spec-Driven parallel regeneration need a single checkout. Separate repos would slow the demo.

## Consequences

Shared FormSpec contracts live in `specs/` (+ optional `packages/shared` for TS). Mobile platforms are native (see ADR-007), not Expo.
