---
name: docs-maintainer
description: Use when behavior, setup, commands, APIs, or workflows change and documentation may need to be updated.
---

# Docs Maintainer

Only update docs when behavior or usage actually changed.

## Rules

- Keep docs short, current, and command-accurate.
- Do not document internal implementation details unless users need them.
- Remove stale instructions when replacing workflows.
- Prefer examples that can be run as written.

## Verification

Check links/commands manually where practical. Do not run app builds for docs-only changes unless docs rendering is part of the app.
