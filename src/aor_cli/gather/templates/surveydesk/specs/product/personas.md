# Personas

## Operator (Iman / demo host)

- Uses the **iOS Simulator** (Swift) and/or **Android Emulator** (Kotlin) operator apps
- Needs to create a survey, arrange fields, start/stop collection, and see counts live
- Trusts that data stays on the local machine for the demo

## Respondent (audience / public)

- Opens a **public Next.js web** link on any browser
- Does not sign in
- Completes the form and sees a thank-you state
- May see a live results summary if the survey is configured to show it (optional toggle; default off for private feedback, on for demo polls)

## Developer / coding agent

- Implements against `SD-*` specs
- Prefers `npm run execute:specs` (parallel agents) or regenerating from specs over inventing architecture
