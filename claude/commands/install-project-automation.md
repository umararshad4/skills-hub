---
description: Install MCT Git hooks into the current project after inspecting existing hooks.
argument-hint: "[project path]"
---

Install MCT project automation for the current repo or `$ARGUMENTS`.

Steps:

1. Confirm the target is a git repo.
2. Inspect existing `.git/hooks/pre-commit` and `.git/hooks/pre-push`.
3. If hooks already exist, preserve them by copying to `.bak` before replacing or merge carefully.
4. Install templates from `~/.claude/git-hooks/`.
5. Make installed hooks executable.
6. Run `~/.claude/bin/mct init --project`.
7. If the user asks for CI too, run `~/.claude/bin/mct init --project --ci`.
8. Report exactly what changed.

Do not overwrite existing project hooks without first showing the existing hook content and explaining the merge/replacement.
