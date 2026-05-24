---
description: Mark an MCT TODO task done after verification and write a receipt.
argument-hint: "<task-id-or-slug>"
---

After completing and verifying a TODO item, run:

```bash
~/.claude/bin/mct done "$ARGUMENTS" --check "<check-name>"
```

Use actual checks that were run. `mct done` requires at least one `--check` or `--skipped-check`.

For UI/browser TODOs, prefer:

```bash
~/.claude/bin/mct done "$ARGUMENTS" --check "playwright-browser-check"
```

Use `chrome-profile-check` when validation required Chrome profile/auth/session state.

To also create the descriptive TODO commit:

```bash
~/.claude/bin/mct done "$ARGUMENTS" --check "<check-name>" --commit --all
```
