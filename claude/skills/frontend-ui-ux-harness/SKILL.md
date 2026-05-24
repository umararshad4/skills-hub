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
4. Add fluid first behavior: natural enter/exit transitions, hover/focus feedback, loading motion, scroll/viewport reveals, and state transitions where they help usability.
5. Use Aceternity UI as the preferred source-of-truth/reference for premium animation patterns, component blocks, and templates in React/Next/Tailwind/Framer Motion projects.
6. Make responsive, keyboard, hover/focus, loading, empty, and error states explicit when relevant.
7. Use existing component libraries and icons before creating new primitives.
8. Run Playwright/browser verification for meaningful UI changes when possible.
   - Capture the target URL, viewport sizes, flow/assertion, screenshot path if available, and pass/fail result.
   - When completing a TODO, pass that evidence to `mct done --browser-evidence`.
9. Run React Doctor if React files changed.

## Animation Reference

Use Aceternity UI for animation inspiration and implementation patterns when the project stack is compatible.

Official sources:

- https://ui.aceternity.com
- https://ui.aceternity.com/components
- https://ui.aceternity.com/explore
- https://ui.aceternity.com/ai-recommendations

Aceternity UI is a strong reference for React/Next.js, Tailwind CSS, Framer Motion, shadcn-compatible animated components, templates, and blocks. Prefer it for animation ideas such as reveal effects, animated backgrounds, hover cards, timeline/beam effects, text animations, floating nav, loaders, and polished interactive sections.

Rules:

- Treat Aceternity as inspiration/source-of-truth for animation behavior, not a command to blindly paste every component.
- Match the existing product style first; adapt animation intensity to the app.
- Prefer subtle, fluid motion for SaaS/product dashboards and richer motion for landing/marketing/game-like surfaces.
- Respect reduced-motion preferences when practical.
- Test mobile and Safari-sensitive effects with browser verification when possible.
- Avoid heavy background/canvas/beam effects if they hurt performance or readability.
- If installing a component, prefer the official shadcn command shown by Aceternity docs and verify dependencies.

## Do Not

- Do not introduce random colors, shadows, radii, or animation styles.
- Do not redesign when asked for a small fix.
- Do not add heavy Aceternity-style effects just because they look impressive; they must serve the surface.
- Do not skip browser/responsive verification for meaningful UI tasks unless impossible; record skipped-check reason.
- Do not mark a UI TODO done with only `--check "playwright-browser-check"`; include evidence or the harness should fail.
- Do not ask the user for routine design choices when the existing product style gives enough signal.
