---
description: Claim and report the next MCT TODO task or safe parallel batch.
argument-hint: "[optional focus]"
---

Run:

```bash
~/.claude/bin/mct next --claim
```

Use the JSON output as the execution route. If it returns parallel candidates, only execute them in parallel when files and dependencies do not overlap.

Focus, if provided:

`$ARGUMENTS`
