---
name: refactor-safely
description: Use when refactoring, cleaning up architecture, extracting components, or improving code without changing behavior.
---

# Refactor Safely

Behavior preservation is the default.

## Workflow

1. Identify the behavior that must not change.
2. Prefer small staged edits.
3. Add or identify behavior checks before risky movement.
4. Avoid unrelated cleanup.
5. Review diff for accidental API, UI, or data-flow changes.

## Report

State preserved behavior, files moved or extracted, checks run, and residual risk.
