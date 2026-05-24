---
description: Use MCT TODO orchestration to complete the next safe TODO.md item or batch.
argument-hint: "[optional focus]"
---

Use MCT TODO orchestration for the current project.

1. Read root `TODO.md`.
2. Run `~/.claude/bin/mct next --claim` and use its JSON output as the deterministic task plan.
3. Complete the next safest item, or a parallel batch only if `todoPlan.mode` is `parallel-candidates`.
4. Route each item through the relevant MCT skills.
5. After each completed item, run the best verification:
   - Playwright MCP for local UI flows, screenshots, responsive checks, and repeatable browser tests.
   - Chrome MCP for real-profile auth/session/extension/remote browser validation.
   - React Doctor/typecheck/targeted tests for non-browser code as appropriate.
6. Update completed checkboxes only after verification.
7. Run `~/.claude/bin/mct done "<task-id-or-slug>" --check "<check>" --commit --all` after verification when working through the TODO queue.
8. If verification cannot run, use `--skipped-check "<reason>"` and explain the risk.
9. Report completed, open, blocked, checks, commits, and risks.

Focus, if provided:

`$ARGUMENTS`
