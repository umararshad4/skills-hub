---
description: Initialize or refresh opensrc library context from package.json.
argument-hint: "[--fetch-metadata] [--force]"
---

Initialize or refresh project-local source-of-truth library context.

Run:

```bash
~/.claude/bin/mct opensrc --fetch-metadata $ARGUMENTS
```

Then read `opensrc/manifest.json` and fill relevant `opensrc/packages/*.md` files using official docs, official repositories, npm package pages, or framework/vendor docs.

Do not commit `opensrc/` unless explicitly requested.
