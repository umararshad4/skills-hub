---
name: have-i-missed-something
description: Always use before finishing any MCT workflow, after completing TODO tasks, before committing, and before final responses. Audits whether MCT instructions were actually followed: opensrc, TODO checkmarks, verification, browser testing, receipts, and commits.
---

# Have I Missed Something?

Use this as the final MCT harness before stopping.

## Mandatory Audit

Run:

```bash
~/.claude/bin/mct audit --warn-only
```

Then check manually:

- If `package.json` exists, was `opensrc/` initialized or refreshed?
- Were relevant `opensrc/packages/*.md` files read or updated from official source-of-truth docs?
- If `TODO.md` exists, was the next task selected with `mct next --claim`?
- After each completed TODO, was `mct done` used to check it off?
- Did each completed TODO record `--check` or `--skipped-check`?
- For UI/browser tasks, was Playwright MCP or Chrome MCP verification run when possible?
- For React tasks, was React Doctor or an explicit skipped-check reason recorded?
- Was a descriptive commit created for each verified TODO item when working through the TODO queue?
- Did the final response include completed/open/blocked TODOs, checks, skipped checks, commits, and risks?

## Decision Harness

Do not ask the user about routine engineering choices when the repo gives enough signal. Make a reasonable decision, record the assumption, and continue.

Ask only when the wrong choice would be expensive, destructive, or product-defining.

## If Something Was Missed

Fix it before final response when possible. If it cannot be fixed, record it as a skipped check or risk with the concrete reason.
