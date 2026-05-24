---
description: Run React Doctor diagnostics and report score/regressions.
argument-hint: "[--full or optional focus]"
---

Run React Doctor for the current repo.

- Default: `npx -y react-doctor@latest . --verbose --diff`
- If `$ARGUMENTS` contains `--full`, run `npx -y react-doctor@latest . --verbose`

Report score, regression status, errors, warnings, and fixes needed.
