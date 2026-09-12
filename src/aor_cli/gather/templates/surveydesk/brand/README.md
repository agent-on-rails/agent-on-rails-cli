# SurveyDesk brand assets

| File | Use |
|------|-----|
| `surveydesk-full.jpg` | Full lockup (illustration + wordmark + tagline) — marketing/home/splash |
| `surveydesk-logo.png` | Logo only, **transparent** background — nav, favicon, sidebar, splash chrome |

Do **not** use an opaque JPG logo plate in chrome.

## Theme tokens

| Token | Hex | Use |
|-------|-----|-----|
| `color.primary` | `#0878F8` | Primary CTAs (Submit, Open) |
| `color.ink` | `#001838` | Body text / wordmark |
| `color.accentGreen` | `#10A868` | Create / add `+` |
| `color.accentPurple` | `#7828F8` | Secondary accent |
| `color.rating` | `#F8B000` | Rating stars |
| `color.surface` | `#FFFFFF` | Surfaces |
| `color.surfaceSubtle` | `#F5F8FC` / `#F0F4F8` | Subtle backgrounds / splash |

Shared contracts: `specs/regeneration/contracts/theme.css.txt`, `Theme.swift.txt`, `Color.kt.txt` (ADR-008).

`aor gather` seeds this folder. If binary assets are missing after gather, create transparent PNG + full JPG placeholders **before** Wave 1 regen (P2/P3/P4 copy them into apps).
