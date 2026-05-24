---
name: code-review
description: Use when reviewing diffs, preparing commits, checking PR readiness, or performing self-review. Prioritizes bugs, regressions, missing tests, accessibility, security, typing, and performance risks.
---

# Code Review

Review like a production engineer. Findings first, summary second.

## Review Order

1. Correctness and behavioral regressions.
2. Security and privacy risks.
3. Type safety and runtime validation gaps.
4. Accessibility and keyboard behavior.
5. Performance and unnecessary rerenders.
6. Missing tests or weak verification.
7. Maintainability concerns.

## Rules

- Cite exact files and lines when possible.
- Do not list style preferences as findings unless they create real risk.
- If no issues are found, say that clearly and mention residual test gaps.
- For self-review, fix actionable findings before calling the work done.
