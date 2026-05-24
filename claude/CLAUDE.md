# AI Engineering Operating System

This is the global operating guide for Claude Code sessions.

## Operating Principles

- Follow explicit user constraints literally. If the user says frontend only, vendor only, no code changes, or preserve the UI, treat it as a hard boundary.
- Prefer current stable tooling and project-local conventions over inventing a new stack.
- Be pragmatic: say when an idea is risky or not worth it, and offer a cleaner alternative.
- Write clean, scalable, readable code with small modules and clear ownership.
- Do not run full builds in normal sessions unless the change is broad, risky, or the user asks.
- Use deterministic checks and scripts where possible instead of relying on memory.

## Default Engineering Loop

1. Understand the request and inspect the repo before changing code.
2. If MCT is requested and root `TODO.md` exists, read it as the task queue before planning.
3. If MCT is requested and `package.json` exists, initialize or refresh `opensrc/` before normal planning.
4. Plan the smallest safe change that satisfies the goal.
5. Implement within the existing architecture.
6. Run targeted checks based on what changed.
7. Run `mct audit --warn-only` before the final response.
8. Summarize changed files, opensrc status, TODO status if relevant, checks run, skipped checks with reasons, and remaining risks.

## Decision Policy

Make routine engineering decisions from repo evidence instead of asking the user. Ask only for destructive, product-defining, credential/account-dependent, expensive-to-reverse, or contradictory choices.

## Frontend Defaults

- Prefer React, Next.js App Router, TypeScript, Tailwind, and shadcn/ui patterns when the project already uses them.
- Keep server/client boundaries explicit.
- Avoid prop drilling when local composition, context, or query/cache patterns are cleaner.
- Keep components focused. If a component grows past roughly 300 lines, consider extraction.
- Preserve existing UI patterns unless the user asks for redesign.
- For UI changes, verify responsive behavior when the affected surface is meaningful.

## Verification Policy

- Tiny copy or style-only edits: inspect diff and run no heavy checks unless requested.
- React component or hook changes: run React Doctor diff scan when available.
- Shared logic, routing, data fetching, auth, payments, or architecture changes: run typecheck and targeted tests.
- PR-ready work: run lint/type/test checks appropriate to the repo and summarize failures honestly.

## Final Response Receipt

Every completed development task should include:

- What changed.
- Checks run.
- Checks skipped and why.
- Risks or follow-up work, if any.
