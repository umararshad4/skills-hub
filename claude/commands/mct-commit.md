---
description: Create a descriptive commit for a completed MCT TODO task.
argument-hint: "<task-id-or-slug>"
---

Create a descriptive commit for this TODO task:

`$ARGUMENTS`

Prefer using `mct done ... --commit --all` immediately after verification. If the TODO is already checked off and changes are still uncommitted, run:

```bash
~/.claude/bin/mct commit --task "$ARGUMENTS" --all
```

Do not mention Claude, MCT, AI, or agent tooling in the commit message.
