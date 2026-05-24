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
~/.claude/bin/mct done "$ARGUMENTS" \
  --check "playwright-browser-check" \
  --browser-evidence "tool=playwright-mcp | url=http://localhost:3000 | viewport=1440x900,390x844 | flow=changed screen inspected | result=pass"
```

Use `chrome-profile-check` when validation required Chrome profile/auth/session state.

To also create the descriptive TODO commit:

```bash
~/.claude/bin/mct done "$ARGUMENTS" --check "<check-name>" --commit --all
```

For UI/browser TODOs, a check name alone is invalid. Include `--browser-evidence` with tool, target URL/test/screenshot/command, viewport or flow, and `result=pass`; otherwise use `--skipped-check` with the exact blocker.
