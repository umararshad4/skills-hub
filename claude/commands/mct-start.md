---
description: Activate MCT and print the required first-step checklist for the current project.
argument-hint: "[--md]"
---

Run:

```bash
~/.claude/bin/mct start --md
```

Treat the output as the MCT activation checklist. If the CLI is unavailable, manually apply the same steps: inspect the repo, initialize opensrc for every declared package when `package.json` exists, route through TODO.md when present, verify before completion, and run final audit before stopping.

The command prints `MCT Toolkit Active`, an execution trace, and the visible agent message that should appear in the terminal or extension before work continues.
