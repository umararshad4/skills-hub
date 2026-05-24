---
name: opensrc
description: Use at the start of MCT in JavaScript/TypeScript projects and whenever library/framework docs context is needed. Builds and maintains an opensrc/ folder from package.json using official source-of-truth docs, repos, npm pages, and web/search.
---

# opensrc

Use this skill before normal MCT task routing in projects with `package.json`.

## Purpose

Create project-local library context in `opensrc/` so agents can work from real source-of-truth docs instead of guessing APIs.

## Workflow

1. Read the target project's `package.json`.
2. Run:

```bash
~/.claude/bin/mct opensrc --fetch-metadata
```

3. Confirm `opensrc/` is listed in `.gitignore`.
4. Read `opensrc/manifest.json`.
5. For libraries relevant to the current task, use web/search to find official docs, official GitHub repos, npm package pages, framework docs, or vendor docs.
6. Fill or update the matching `opensrc/packages/*.md` file with concise source-of-truth context.
7. Use that context while planning and implementing.

## Source Rules

- Use official documentation, official repositories, npm package pages, or framework/vendor docs.
- Prefer latest stable docs unless the project is pinned to an older major version.
- Do not use random blog posts as authoritative context.
- Do not commit `opensrc/` unless the user explicitly requests it; it is local context.

## What To Capture

- Installed/declared version and latest version.
- Official docs URL and repository URL.
- APIs/components/hooks used in this project.
- Version-specific constraints.
- Examples only when they directly support the current task.

## Completion

Mention which libraries were refreshed in `opensrc/` and which sources were used.
