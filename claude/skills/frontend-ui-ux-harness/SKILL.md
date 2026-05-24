---
name: frontend-ui-ux-harness
description: Always use for frontend, UI, UX, styling, layout, responsive, interaction, component, design-system, and visual tasks. Requires frontend-design, design-taste-frontend, and ui-ux-pro-max when available.
---

# Frontend UI/UX Harness

Use this skill for every frontend/UI/UX task.

## Required Companion Skills

When available in the environment, also load and follow:

- `frontend-design`
- `design-taste-frontend`
- `ui-ux-pro-max`

If one is unavailable, continue with this harness plus `ui-system` and `design-consistency`.

## Workflow

1. Inspect existing UI, components, tokens, layout density, and interaction patterns.
2. Preserve exact UI parity when the user asks for narrow changes.
3. For new UI, prioritize usable product experience over decorative landing-page patterns.
4. Make responsive, keyboard, hover/focus, loading, empty, and error states explicit when relevant.
5. Use existing component libraries and icons before creating new primitives.
6. Run Playwright/browser verification for meaningful UI changes when possible.
7. Run React Doctor if React files changed.

## Do Not

- Do not introduce random colors, shadows, radii, or animation styles.
- Do not redesign when asked for a small fix.
- Do not skip browser/responsive verification for meaningful UI tasks unless impossible; record skipped-check reason.
- Do not ask the user for routine design choices when the existing product style gives enough signal.
