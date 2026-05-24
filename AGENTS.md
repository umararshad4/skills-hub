# Agent Instructions

This repository contains a reusable AI engineering toolkit. It is Claude Code-first, but other coding agents can use the same rules by reading this file and the referenced MCT guide.

## Start Here

When working in this repo or using this toolkit, read:

1. `README.md`
2. `claude/MCT.md`
3. `claude/CLAUDE.md`

Treat `claude/MCT.md` as the source of truth for orchestration.

## What MCT Means

MCT means "My Claude Toolkit", but non-Claude agents should treat it as a general engineering orchestration system.

When the user says `use MCT`, `MCT mode`, `run MCT`, or similar:

1. Inspect the project before editing.
2. Look for a root `TODO.md`.
3. If `TODO.md` exists, run or emulate `mct status`, `mct next`, `mct done`, and `mct verify` behavior.
4. Route work through the relevant skill guidance under `claude/skills/`.
5. Run verification before marking TODO items done.
6. Mark completed TODO items with `[x]`.
7. Create a descriptive commit after each verified TODO item when requested by the workflow.
8. Finish with completed/open/blocked TODO items, checks run, skipped checks, commits, and risks.

## CLI

If installed, use:

```bash
~/.claude/bin/mct status --md
~/.claude/bin/mct next --claim
~/.claude/bin/mct done "<task-id-or-slug>" --check "<check-name>" --commit --all
~/.claude/bin/mct verify --mode pre-commit
~/.claude/bin/mct verify --mode pre-push
```

If the CLI is not installed, use the repo-local CLI:

```bash
./claude/bin/mct status --md
```

## Non-Claude Agent Mapping

- Claude skills live in `claude/skills/`; other agents should read the relevant `SKILL.md` files as instruction packs.
- Claude subagents live in `claude/agents/`; other agents can treat them as role prompts.
- Claude slash commands live in `claude/commands/`; other agents can treat them as reusable workflow prompts.
- Hooks live in `claude/hooks/`; other agents can run the scripts manually when their platform has no hook system.
- Git hooks live in `claude/git-hooks/`; these are platform-independent shell hooks.

## Verification Rules

- UI/browser TODOs need Playwright/browser verification when possible.
- Use Chrome/profile-based verification when authenticated browser state or extensions are required.
- React TODOs need React Doctor or targeted React checks.
- TypeScript/shared logic needs typecheck and focused tests where available.
- Do not mark a TODO item complete without a real check or an explicit skipped-check reason.

## Commit Rules

- Commit one verified TODO item at a time unless a safe independent batch was selected.
- Do not mention Claude, MCT, AI, or agent tooling in commit messages.
- Use descriptive commit messages based on the completed task.
- Do not include `.mct/` state or receipts in commits unless explicitly requested.
