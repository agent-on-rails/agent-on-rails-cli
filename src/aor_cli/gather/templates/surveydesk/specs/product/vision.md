# Product vision

**SurveyDesk** is a local-first survey desk: operators design forms on a mobile app, respondents answer on a public web page (anonymous), and answers land in SQLite through a local API — with instant results and in-app start/stop controls.

It is the live-build target for the suherman.net English session that ranked:

1. Form + workflow automation  
2. Internal tooling  
3. Mobile app  

## Goals

1. Drag-and-drop (or equivalent touch-friendly) form builder on mobile
2. Anonymous public web for respondents — no account required
3. Local SQLite storage via a documented HTTP API
4. Instant results for operators (and optionally a public live results view when the survey is open)
5. Internal tooling **inside the mobile app**: create, edit, open (start), close (end), view results
6. Entire stack runnable on one laptop for a one-hour Spec-Driven demo

## Non-goals (v1)

- Multi-tenant SaaS / cloud billing / SSO
- Email invitations or paid SurveyMonkey feature parity
- Offline-first sync across devices beyond same-LAN API access
- Complex branching logic / payment / file upload fields (may land later)
- Non-English UI (English only for this repo)

## Success for the live session

In one continuous demo:

1. Operator creates a survey and builds fields on mobile  
2. Operator opens the survey → public URL is shareable  
3. Respondent submits anonymously on web  
4. Results update instantly on mobile (and/or web results panel)  
5. Operator closes the survey → new submissions are rejected  
