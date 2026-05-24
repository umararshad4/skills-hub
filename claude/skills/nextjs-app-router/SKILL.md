---
name: nextjs-app-router
description: Use when working on Next.js App Router routes, layouts, server/client components, metadata, loading/error boundaries, route handlers, caching, or data fetching.
---

# Next.js App Router

Inspect the existing app structure before editing.

## Rules

- Keep server components server-side unless interactivity requires a client boundary.
- Put `use client` as low as practical.
- Use route-level `loading.tsx`, `error.tsx`, and `not-found.tsx` only where they improve behavior.
- Keep data fetching, caching, and revalidation explicit.
- Avoid browser-only APIs in server components.
- Preserve existing route conventions.

## Verification

Run typecheck for shared route/data changes. Use targeted route tests or browser checks when behavior or UI changed.
