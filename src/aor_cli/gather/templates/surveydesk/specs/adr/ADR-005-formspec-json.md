# ADR-005 FormSpec as JSON contract

## Decision

Forms are data (FormSpec JSON), not generated React trees stored per survey.

## Why

Mobile builder and web renderer share one schema; coding agents can regenerate UIs from the contract.

## Consequences

New field types need FormSpec + renderer + mobile editor updates together.
