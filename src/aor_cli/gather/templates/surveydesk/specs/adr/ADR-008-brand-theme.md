# ADR-008 Shared brand theme

## Decision

Canonical brand assets live in `brand/`:

- `surveydesk-full.jpg` — full lockup with text
- `surveydesk-logo.png` — logo only (transparent background for headers/nav)
- `surveydesk-logo.jpg` — legacy opaque source (prefer PNG in UI)

All UIs (Next.js web, Swift iOS, Kotlin Android) share the color tokens documented in `brand/README.md` / `specs/product/brand.md`.

## Why

One live-demo visual identity across simulators and the public survey page.

## Consequences

Parallel agents copy assets into their owned `apps/*` trees; they must not restyle primary actions away from `#0878F8` without updating the brand spec first. Mobile chrome (splash/nav/sidebar) MUST use the transparent PNG per `specs/regeneration/contracts/mobile-operator-ux.md`.
