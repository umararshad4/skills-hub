---
name: performance-audit
description: Use when investigating or reviewing frontend performance, bundle size, render cost, image loading, caching, lazy loading, or runtime mismatch.
---

# Performance Audit

Start from the concrete symptom or changed surface.

## Check

- Avoid unnecessary client components in Next.js.
- Look for avoidable rerenders, broad context updates, and expensive render work.
- Check image sizing, lazy loading, and priority usage.
- Check bundle additions and dynamic imports for heavy UI.
- Check cache/revalidation/runtime choices.

## Verification

Use targeted profiling, bundle analysis, Lighthouse, or browser checks only when relevant. Do not run heavyweight performance tooling for tiny changes.
