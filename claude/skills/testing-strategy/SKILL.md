---
name: testing-strategy
description: Use when deciding what tests or checks to run or add for a frontend/full-stack change.
---

# Testing Strategy

Match test weight to risk.

## Defaults

- Copy-only: diff review.
- Pure styling: responsive/browser check if layout risk.
- Component behavior: focused unit or interaction test.
- Shared logic: unit tests plus typecheck.
- Route/data fetching: route-level or integration test.
- Auth/payment/security: targeted negative and permission tests.
- Refactor: before/after behavior checks.

Do not add broad tests that do not protect the changed behavior.
