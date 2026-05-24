# Skills Hub

Reusable AI engineering toolkit for Claude Code and other coding agents that can read repo instructions such as `AGENTS.md`.

## What Is Included

- Cross-agent instructions: `AGENTS.md`
- Global Claude guide: `claude/CLAUDE.md`
- MCT orchestration guide: `claude/MCT.md`
- Skills: `claude/skills/`
- Subagents: `claude/agents/`
- Slash commands: `claude/commands/`
- Hooks: `claude/hooks/`
- Git hooks: `claude/git-hooks/`
- Deterministic MCT CLI: `claude/bin/mct`
- CI and project templates: `claude/templates/`
- Source-of-truth library context workflow: `opensrc/` via `mct opensrc`
- Frontend/UI/UX harness that routes UI work through design-taste skills when available
- Aceternity UI reference guidance for polished React/Next/Tailwind/Framer Motion animation patterns

## Agent Compatibility

This toolkit is Claude Code-first, but it is structured so other agents can use it too.

| Agent type | How to use |
| --- | --- |
| Claude Code | Install with `./claude/install.sh`; Claude reads `~/.claude/` skills, agents, commands, settings, and hooks. |
| Codex/OpenAI-style agents | Read root `AGENTS.md`, then follow `claude/MCT.md` and relevant files under `claude/skills/`. |
| Cursor/other repo-aware agents | Point the agent at `AGENTS.md` and ask it to use MCT. |
| Generic terminal agents | Use `./claude/bin/mct` directly and read `claude/MCT.md` as the workflow guide. |

Most non-Claude tools do not support Claude's skills/subagents/hooks natively. For them:

- Treat `claude/skills/*/SKILL.md` as reusable instruction packs.
- Treat `claude/agents/*.md` as role prompts.
- Treat `claude/commands/*.md` as workflow prompts.
- Use `claude/bin/mct` as the deterministic orchestration CLI.
- Use `claude/git-hooks/` for platform-independent Git lifecycle automation.
- For frontend/UI/UX work, read `claude/skills/frontend-ui-ux-harness/SKILL.md`; if local skills are available, also load `frontend-design`, `design-taste-frontend`, and `ui-ux-pro-max`.

## Install

Claude Code global install:

```bash
./claude/install.sh
```

This syncs the toolkit into `~/.claude`.

Restart Claude Code after installing so session-start hooks load the fresh context.

Non-Claude agents do not need the global Claude install. They can read `AGENTS.md` and run:

```bash
./claude/bin/mct status --md
```

## Update

From a cloned `skills-hub` repo:

```bash
./claude/update.sh
```

Or from anywhere after installation:

```bash
~/.claude/bin/mct self-update
```

If your clone lives somewhere unusual:

```bash
MCT_SOURCE=/path/to/skills-hub ~/.claude/bin/mct self-update
```

After updating the global toolkit, refresh project automation in each project that uses MCT hooks:

```bash
~/.claude/bin/mct init --project
```

For projects using vendored CI:

```bash
~/.claude/bin/mct init --project --ci
```

## Project Bootstrap

Inside any project:

```bash
~/.claude/bin/mct init --project
```

With GitHub Actions CI:

```bash
~/.claude/bin/mct init --project --ci
```

## Common Commands

```bash
~/.claude/bin/mct status --md
~/.claude/bin/mct config --init
~/.claude/bin/mct opensrc --fetch-metadata
~/.claude/bin/mct audit --warn-only
~/.claude/bin/mct final-check --todo-log
~/.claude/bin/mct next --claim
~/.claude/bin/mct browser-proof --url "http://localhost:3000" --viewport "1440x900,390x844" --flow "changed screen inspected" --result pass
~/.claude/bin/mct done "<task-id-or-slug>" --check "<check-name>" --commit --all
~/.claude/bin/mct done "<ui-task>" --check "playwright-browser-check" --browser-evidence "tool=playwright-mcp | url=http://localhost:3000 | viewport=1440x900,390x844 | result=pass" --commit --all
~/.claude/bin/mct todo-log --md
~/.claude/bin/mct verify --mode pre-commit
~/.claude/bin/mct verify --mode pre-push
```

Repo-local form for non-Claude agents:

```bash
./claude/bin/mct status --md
./claude/bin/mct config --init
./claude/bin/mct opensrc --fetch-metadata
./claude/bin/mct audit --warn-only
./claude/bin/mct final-check --todo-log
./claude/bin/mct next --claim
./claude/bin/mct browser-proof --url "http://localhost:3000" --viewport "1440x900,390x844" --flow "changed screen inspected" --result pass
./claude/bin/mct done "<task-id-or-slug>" --check "<check-name>" --commit --all
./claude/bin/mct done "<ui-task>" --check "playwright-browser-check" --browser-evidence "tool=playwright-mcp | url=http://localhost:3000 | viewport=1440x900,390x844 | result=pass" --commit --all
./claude/bin/mct todo-log --md
```

## TODO.md Workflow

When a project has a root `TODO.md`, MCT treats it as the task queue.

Example:

```markdown
- [ ] Fix pricing toggle #react #ui files:app/pricing/page.tsx
- [ ] Update docs #docs depends:fix-pricing-toggle
- [ ] Audit auth redirect #security #blocked
```

MCT will classify tasks, choose sequential or safe parallel execution, require verification before completion, check off completed tasks, and optionally create descriptive commits.

UI/browser TODOs are strict. A check name alone is not enough. `mct done` requires Playwright/Chrome/browser evidence with a target URL, viewport or tested flow, and pass result, or an explicit skipped-check reason with the blocker.

The strict audit also checks the chain from TODO to receipt to commit. A checked TODO without a receipt is flagged, and a completed TODO receipt without a commit SHA is flagged when TODO commits are required. Use `mct todo-log --md` to inspect task -> checks -> browser proof -> receipt -> commit.

`mct browser-proof` creates a local proof artifact under `.mct/browser-proof/` and prints a `browserEvidence` string you can pass to `mct done`.

## opensrc Workflow

For JavaScript/TypeScript projects, MCT can create a gitignored `opensrc/` directory from `package.json`:

```bash
~/.claude/bin/mct opensrc --fetch-metadata
```

This creates:

```txt
opensrc/
  README.md
  manifest.json
  packages/
```

Agents should then use official source-of-truth docs, official repositories, npm package pages, or framework/vendor docs to fill only the library context relevant to the current task.

`opensrc/` is local context and is added to `.gitignore`.

## Using MCT From Any Agent

Prompt:

```txt
Use MCT. Read AGENTS.md and claude/MCT.md first. Work through TODO.md one verified task at a time.
```

Expected behavior:

1. Read `AGENTS.md`.
2. Read `claude/MCT.md`.
3. If `package.json` exists, run `mct opensrc --fetch-metadata` and fill relevant library docs from official sources.
4. Run `mct status --md`.
5. Run `mct next --claim`.
6. Complete the selected TODO task.
7. Run verification, using `mct browser-proof` for UI/browser work when useful.
8. Run `mct done "<task>" --check "<check>" --commit --all`.
9. Run `mct final-check --todo-log`.
10. Continue to the next task or report blockers.
