---
description: Audit whether the current task followed MCT requirements before final response.
argument-hint: "[--warn-only]"
---

Run:

```bash
~/.claude/bin/mct audit --warn-only
```

Then apply the `have-i-missed-something` skill:

- Check opensrc was initialized when `package.json` exists.
- Check TODO items were completed through `mct done`.
- Check each completed TODO has a recorded check or skipped-check.
- Check UI tasks used Playwright/Chrome/browser verification when possible.
- Check receipts and commits exist when the TODO workflow requires them.
