---
name: debugging-loop
description: Use when fixing bugs, investigating failures, or handling repeated errors. Forces reproduce, isolate, root cause, patch, regression test, and summary.
---

# Debugging Loop

Do not patch blindly. Use this sequence:

1. Reproduce or confirm the reported behavior.
2. Identify the smallest failing surface.
3. Trace the real call path, data path, or render path.
4. State the root cause before editing.
5. Patch the narrowest cause.
6. Run a regression check that would have caught the issue.
7. Summarize cause, fix, and remaining risk.

## Rules

- If reproduction is impossible, explain exactly what was verified and what remains unknown.
- If multiple causes are plausible, test the cheapest differentiator first.
- Do not mix cleanup with bug fixes unless cleanup is required for the fix.
- If a command fails twice, stop and diagnose the failure mode before retrying.
