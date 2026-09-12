# Live demo journey

**Audience:** English webinar attendees  
**Theme:** Spec-Driven Development applied to SurveyDesk  

## Storyboard (≈ 45–60 minutes)

1. **Spec first** — Open `specs/requirements/SD-003` and `SD-004`. Show SHALL contracts for lifecycle and FormSpec.
2. **API + SQLite** — Point at OpenAPI and the empty database; start `apps/api`.
3. **Build on mobile** — Create “Session feedback” survey on **iPhone or Android phone**; also show **iPad / Android tablet** sidebar layout when demoing large screens; drag fields: rating, short text, single choice.
4. **Start** — Tap Open; copy public URL.
5. **Respond on web** — Browser (anonymous) submits 2–3 answers.
6. **Instant results** — Mobile results screen updates without refresh ritual (poll or SSE).
7. **Close** — End survey; attempt another web submit → rejected.
8. **Traceability** — Map each step back to an `SD-*` ID.

Demo CLI after regen: `npm run demo` → `npm run demo:ios` (iPhone+iPad) → `npm run demo:android` (phone+tablet) → browser `/s/{slug}`.

## Sample survey for demo

| Field key | Type | Label |
|-----------|------|--------|
| usefulness | rating_1_5 | How useful was today’s session? |
| clarity | single_choice | Was the language clear? |
| next_topic | short_text | What should we build next? |
