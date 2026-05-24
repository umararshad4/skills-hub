---
name: frontend-architecture
description: Use when planning, implementing, reviewing, or refactoring React/Next.js frontend architecture. Enforces feature ownership, typed boundaries, clean hooks, server/client separation, and scalable component structure.
---

# Frontend Architecture

Use this skill before broad frontend changes and during review of React/Next.js code.

## Workflow

1. Inspect the existing project conventions before proposing structure.
2. Keep changes inside the smallest feature or route boundary that satisfies the request.
3. Preserve server/client boundaries. Do not move logic into client components unless interactivity requires it.
4. Prefer typed API/client boundaries over untyped fetch payloads.
5. Extract only when it improves ownership, readability, reuse, or testability.
6. Review for component size, prop drilling, duplicate data fetching, duplicated DTOs, and unclear module ownership.

## Defaults

- Feature code should live near the route or feature that owns it.
- Shared components should be genuinely shared, not prematurely global.
- Avoid components over roughly 300 lines unless they are simple static markup.
- Prefer named exports and explicit types at module boundaries.
- Avoid barrel exports if the repo avoids them; use them only when already established.

## Output Expectations

- State the architectural boundary being touched.
- Call out any deviation from existing project conventions.
- Include targeted verification, not blanket build commands for small changes.
