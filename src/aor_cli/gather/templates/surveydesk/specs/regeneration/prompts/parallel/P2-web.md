# P2 — public web (Next.js + React) (OWNED PATHS ONLY)

You are agent **P2-web** implementing SurveyDesk from specs.

## OWNED PATHS (create only these)
- `apps/web/**`

Do **not** edit `apps/api`, `apps/ios`, `apps/android`, `tests/`, or `scripts/`.

## Specs (must read)
- `specs/requirements/SD-001`, `SD-006`, `SD-007`
- `specs/domain/form-spec.md`, `response.md`, `results.md`
- `specs/api/openapi.yaml` (public paths only)
- `specs/adr/ADR-003-anonymous-public.md`, `ADR-005-formspec-json.md`, `ADR-008-brand-theme.md`
- `specs/product/demo-journey.md`, `specs/product/brand.md`
- `brand/README.md` + assets `brand/surveydesk-full.jpg`, `brand/surveydesk-logo.png`
- Prefer verbatim CSS tokens from `specs/regeneration/contracts/theme.css.txt`

## Stack
- **React** + **Next.js** App Router (TypeScript)
- English UI
- API base: `NEXT_PUBLIC_SURVEY_DESK_API_URL` (default `http://127.0.0.1:8787`)
- Dev port: `SURVEY_DESK_WEB_PORT` / `3091`
- Shared brand theme (primary `#0878F8`, ink `#001838`, rating `#F8B000`, etc.)

## Must implement
1. Home/hero using **full brand image** `brand/surveydesk-full.jpg` (copy into `apps/web/public/`)
2. Favicon / compact header mark from **logo only** `brand/surveydesk-logo.png` (transparent background; fall back to `.jpg` only if PNG missing)
3. Apply theme CSS variables; Submit and selected radios use `--sd-primary`
4. `/s/[slug]` — render FormSpec fields, validate required, submit anonymous answers
5. Thank-you state after successful submit
6. Clear error when survey is not `open` (or 403/404)
7. Optional public results panel when `showPublicResults` is true (poll ≤ 2s)
8. Field renderers for: `short_text`, `long_text`, `single_choice`, `multi_choice`, `rating_1_5` (gold stars), `yes_no`
9. `apps/web/package.json` with `dev` / `build` / `start`
10. No login, no PII collection beyond FormSpec fields

## Done when
- `apps/web` runs with Next.js and SurveyDesk brand colors/assets (Wave 1 ≤ 10m share of 15m total)
- Opening `/s/{slug}` against a running API shows the form and can submit

## Speed
Lean Next.js App Router only; no heavy UI kits; commit `package-lock.json`.
