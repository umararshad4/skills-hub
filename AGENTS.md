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
2. If `package.json` exists, initialize or refresh `opensrc/` and use official source-of-truth library docs for relevant dependencies.
3. Look for a root `TODO.md`.
4. If `TODO.md` exists, run or emulate `mct status`, `mct next`, `mct done`, and `mct verify` behavior.
5. Route work through the relevant skill guidance under `claude/skills/`.
6. Run verification before marking TODO items done.
7. Mark completed TODO items with `[x]`.
8. Create a descriptive commit after each verified TODO item when requested by the workflow.
9. Run `mct audit --warn-only` or manually apply the same audit.
10. Finish with opensrc status, completed/open/blocked TODO items, checks run, skipped checks, commits, and risks.

## CLI

If installed, use:

```bash
~/.claude/bin/mct status --md
~/.claude/bin/mct config --init
~/.claude/bin/mct opensrc --fetch-metadata
~/.claude/bin/mct audit --warn-only
~/.claude/bin/mct final-check --todo-log
~/.claude/bin/mct next --claim
~/.claude/bin/mct browser-proof --url "http://localhost:3000" --viewport "1440x900,390x844" --flow "changed screen inspected" --result pass
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
- UI/browser TODOs need evidence-grade verification: tool, target URL/test/screenshot/command, viewport or flow, and `result=pass`. A check label alone is not enough.
- Completed TODOs need a receipt and, in the TODO automation workflow, a descriptive commit SHA in that receipt.
- Use `mct todo-log --md` or `mct final-check --todo-log` to inspect the task -> check -> proof -> receipt -> commit chain.
- Frontend/UI/UX tasks should use `frontend-ui-ux-harness`; when available, also use `frontend-design`, `design-taste-frontend`, and `ui-ux-pro-max`.
- For frontend animation and fluid behavior, use Aceternity UI official docs/components/templates as the preferred reference, then adapt to the existing product style.
- Use Chrome/profile-based verification when authenticated browser state or extensions are required.
- React TODOs need React Doctor or targeted React checks.
- TypeScript/shared logic needs typecheck and focused tests where available.
- Do not mark a TODO item complete without a real check or an explicit skipped-check reason.

## opensrc Rules

- `opensrc/` is local, gitignored source-of-truth library context.
- Build it from the target project's `package.json`.
- Use official docs, official repos, npm package pages, or framework/vendor docs.
- Do not use random blog posts as authoritative context.
- Do not commit `opensrc/` unless explicitly requested.

## MCT Audit Rules

- Run `mct audit --warn-only` before final response when available.
- Use `claude/skills/have-i-missed-something/SKILL.md` as the final checklist.
- Fix missed steps before final response when practical.
- If a missed step cannot be fixed, record it as a skipped check or risk.

## Commit Rules

- Commit one verified TODO item at a time unless a safe independent batch was selected.
- Do not mention Claude, MCT, AI, or agent tooling in commit messages.
- Use descriptive commit messages based on the completed task.
- Do not include `.mct/` state or receipts in commits unless explicitly requested.
