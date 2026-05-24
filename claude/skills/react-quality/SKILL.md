---
name: react-quality
description: Use when editing React components, hooks, state, effects, memoization, context, forms, or rendering behavior.
---

# React Quality

Use this skill for React implementation and review.

## Check

- State belongs at the lowest useful owner.
- Effects are for synchronization, not derived state.
- Event handlers should not recreate expensive work unnecessarily.
- Memoization should solve a measured or obvious stability problem.
- Context should not cause broad rerenders for frequently changing values.
- Components should be composable, accessible, and testable.

## Verify

Run React Doctor diff after meaningful React changes:

```bash
npx -y react-doctor@latest . --verbose --diff
```
