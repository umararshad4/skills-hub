---
name: react-doctor
description: Use when finishing a React feature, fixing a React bug, before committing React code, or when improving React code quality. Runs React Doctor and prevents score regression.
---

# React Doctor

React Doctor scans React codebases for correctness, accessibility, performance, security, and architecture issues.

## After React Code Changes

Run:

```bash
npx -y react-doctor@latest . --verbose --diff
```

If the score regresses, fix the regression before committing or marking the task complete.

## Cleanup Or Audit Work

Run a full scan:

```bash
npx -y react-doctor@latest . --verbose
```

Fix errors first, then warnings. Do not mix broad cleanup into unrelated feature work.

## Reporting

Include:

- Score and whether it regressed.
- Errors and warnings fixed.
- Issues intentionally left for later.
- Any command failure and the exact reason.
