---
name: ui-system
description: Use when creating or changing UI. Enforces existing design system usage, shadcn/ui and Tailwind conventions, accessibility, responsive behavior, semantic spacing, and visual consistency.
---

# UI System

Use the existing UI system before creating new primitives.

## Workflow

1. Inspect nearby UI and shared components.
2. Reuse existing tokens, variants, and layout primitives.
3. Keep interaction controls familiar: icon buttons, inputs, tabs, menus, toggles, sliders, and tooltips where appropriate.
4. Preserve UI parity when the user asks for a narrow change.
5. Verify mobile and desktop behavior for meaningful UI changes.

## Rules

- Do not introduce a new palette, radius scale, or shadow style without a clear reason.
- Avoid landing-page composition for operational dashboards.
- Text must fit its container at mobile and desktop sizes.
- Use semantic buttons, labels, focus states, and keyboard-accessible controls.
- Prefer lucide icons when the project already uses lucide.
