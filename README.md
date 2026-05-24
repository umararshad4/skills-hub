# Skills Hub

Reusable AI engineering toolkit for Claude Code workflows.

## What Is Included

- Global Claude guide: `claude/CLAUDE.md`
- MCT orchestration guide: `claude/MCT.md`
- Skills: `claude/skills/`
- Subagents: `claude/agents/`
- Slash commands: `claude/commands/`
- Hooks: `claude/hooks/`
- Git hooks: `claude/git-hooks/`
- Deterministic MCT CLI: `claude/bin/mct`
- CI and project templates: `claude/templates/`

## Install

```bash
./claude/install.sh
```

This syncs the toolkit into `~/.claude`.

Restart Claude Code after installing so session-start hooks load the fresh context.

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
~/.claude/bin/mct next --claim
~/.claude/bin/mct done "<task-id-or-slug>" --check "<check-name>" --commit --all
~/.claude/bin/mct verify --mode pre-commit
~/.claude/bin/mct verify --mode pre-push
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
