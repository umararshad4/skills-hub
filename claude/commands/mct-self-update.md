---
description: Pull the skills-hub repo and reinstall the global MCT toolkit.
argument-hint: "[--no-pull]"
---

Update the global toolkit:

```bash
~/.claude/bin/mct self-update $ARGUMENTS
```

If the source repo is not found, rerun with:

```bash
MCT_SOURCE=/path/to/skills-hub ~/.claude/bin/mct self-update
```

After updating, remind the user to refresh project automation:

```bash
~/.claude/bin/mct init --project
```

For projects using vendored CI:

```bash
~/.claude/bin/mct init --project --ci
```
