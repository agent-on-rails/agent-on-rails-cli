# P3 — iOS operator app (Swift) (OWNED PATHS ONLY)

You are agent **P3-ios** implementing SurveyDesk from specs.

## OWNED PATHS (create only these)
- `apps/ios/**`

Do **not** edit `apps/api`, `apps/web`, `apps/android`, `tests/`, or `scripts/` (simulator launch scripts are owned by P5; you may document Xcode scheme names in `apps/ios/README.md`).

## Specs (must read)
- `specs/requirements/SD-008`, `SD-009`, `SD-010`, `SD-011`
- `specs/domain/form-spec.md`, `lifecycle.md`, `results.md`
- `specs/api/openapi.yaml` (operator + results)
- `specs/adr/ADR-004-mobile-operator.md`, `ADR-005-formspec-json.md`, **`ADR-007-native-mobile.md`**, `ADR-008-brand-theme.md`
- `specs/product/demo-journey.md`, `specs/product/brand.md`
- `brand/README.md` + `brand/surveydesk-full.jpg`, `brand/surveydesk-logo.png` (transparent; use PNG in UI)
- Prefer verbatim `specs/regeneration/contracts/Theme.swift.txt` → `Theme.swift`
- **Required UX contract:** `specs/regeneration/contracts/mobile-operator-ux.md` (follow completely)

## Stack
- Native **Swift** + **SwiftUI**
- Xcode project/workspace under `apps/ios/` (e.g. `SurveyDesk.xcodeproj` + `project.yml` for XcodeGen)
- Configurable API base URL (default `http://127.0.0.1:8787` for Simulator; support LAN IP for device)
- Optional operator token header `X-SurveyDesk-Token`
- **Universal iPhone + iPad:** `TARGETED_DEVICE_FAMILY = "1,2"` (project **and** target)
- Shared brand theme (same hex tokens as web/Android)

## Must implement (operator app)
1. Bundle **transparent** `brand/surveydesk-logo.png` as `BrandLogo` imageset — splash, toolbar, iPad sidebar. Do **not** ship opaque JPG logo in chrome. Use a `BrandLogoMark` view (height-based, no white plate).
2. Apply `SurveyDeskTheme` colors; create/add uses `accentGreen`; ratings use `rating` gold; primary CTAs use `primary`
3. Survey list with status badges (`draft` / `open` / `closed`)
4. Create survey (title, optional description, `showPublicResults`)
5. Detail with tabs/sections: Builder, Lifecycle, Results (use `switch`/conditional views — **not** page-style `TabView` on iPad detail)
6. FormSpec builder: add/edit/remove fields; **drag-and-drop reorder**; save via PATCH
7. Block FormSpec edits while status is `open`
8. Open / Close actions
9. Show/copy public URL (`http://127.0.0.1:3091/s/{publicSlug}` or configurable web base)
10. Results view auto-refresh ≤ 2s while screen visible
11. `apps/ios/README.md`: open in Xcode; pick **iPhone or iPad** Simulator; ⌘R; note `npm run demo:ios`
12. `project.yml` + pbxproj: `TARGETED_DEVICE_FAMILY = "1,2"`; iPad supported orientations Info.plist keys
13. **iPad:** `NavigationSplitView` left sidebar (logo + list + create) + detail. Drive selection with `selectedSurveyId` — **never** sidebar `NavigationLink(value:)` (causes blank detail). Apply `.id(selectedSurveyId)` on detail. **iPhone:** `NavigationStack`

## Done when
- Builds for **iPhone and iPad** Simulator destinations
- Selecting a survey on iPad fills the detail pane (not blank)
- Transparent logo blends on `surfaceSubtle`
- Operator list/create/build/open/close/results against local API

## Speed
Simulator only — no Archive / App Store. Minimal project; verify one iPad destination builds during Wave 1.
