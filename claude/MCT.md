# MCT: My Claude Toolkit

MCT means: use this Claude toolkit as the operating system for the current task.

When the user says `use MCT`, `MCT mode`, `run MCT`, or similar, Claude should:

1. Inspect the project before deciding.
2. If the project has `package.json`, initialize or refresh `opensrc/` context from source-of-truth library docs.
3. Check for a root `TODO.md` file and treat it as the task queue when present.
4. Classify the request, TODO items, dependencies, and changed surfaces.
5. Select the right skills/subagents from this file.
6. Choose sequential or parallel execution based on dependency risk.
7. Use the smallest safe workflow.
8. Run event-appropriate checks.
9. Finish with a completion receipt and TODO status.

MCT does not mean "run every tool." It means "route the work through the correct engineering loop."

## opensrc Context

At the start of MCT in JavaScript/TypeScript projects, read `package.json` and initialize `opensrc/`:

```bash
~/.claude/bin/mct opensrc --fetch-metadata
```

`opensrc/` is a gitignored local context directory for library and framework docs. It is not for dumping entire libraries or `node_modules`.

Use it this way:

1. Run the `mct opensrc` command.
2. Read `opensrc/manifest.json`.
3. Identify libraries relevant to the current task.
4. Use web/search against official source-of-truth docs only: official docs, official repositories, npm package pages, or framework/vendor docs.
5. Fill the relevant `opensrc/packages/*.md` files with concise API/pattern/version context.
6. Use that context before planning or editing.

Do not commit `opensrc/` unless the user explicitly asks.

## TODO.md Orchestration

Whenever MCT is requested, first look for `TODO.md` in the project root. If present, read it before planning or editing.

`TODO.md` is treated as the project task queue, not loose notes.

Use `~/.claude/bin/mct plan` as the deterministic planner when available. It parses TODO checkboxes, tags, dependency hints, file hints, changed files, recommended checks, and `.mct/state.json`.

### TODO.md Priority

| Case | Behavior |
| --- | --- |
| User gives a specific task and `TODO.md` exists | Use `TODO.md` as constraints/context, then complete the requested task if it is compatible. |
| User says only "use MCT", "start MCT", "continue", or similar | Work from `TODO.md` top to bottom. |
| `TODO.md` has checked items | Treat checked items as done unless current repo state contradicts them. |
| `TODO.md` has unchecked items | Triage unchecked items into independent, dependent, blocked, and risky. |
| `TODO.md` conflicts with the user prompt | The user prompt wins; mention the conflict. |
| No `TODO.md` exists | Continue normal MCT prompt routing. |

### Sequential vs Parallel

Use sequential execution when:

- items touch the same files or same feature area;
- one item depends on another;
- behavior, schema, auth, routing, or architecture could conflict;
- verification for one item determines the next step.

Use parallel subagents when:

- items touch clearly independent areas;
- tasks are read-only audits or reviews;
- one task is docs and another is implementation;
- each task has separate verification and no shared files.

Before parallel work, state the task split and expected merge/review point. After parallel work, review combined changes for conflicts.

### TODO.md Completion Rules

- Complete items one by one unless independent parallel execution is clearly safer/faster.
- After completing an item, update `TODO.md` by checking it off with `[x]`; do this through `~/.claude/bin/mct done` whenever possible.
- Do not mark a TODO complete until post-task verification has run, or a skipped-check reason is explicitly recorded.
- Do not delete TODO items unless explicitly requested.
- If an item is ambiguous, convert it into a short clarifying note or ask the user when the wrong choice would be expensive.
- If an item is blocked, leave it unchecked and add the blocker under it.
- Final response must include completed TODO items, skipped/blocked items, and checks run.

### Post-Task Verification

After every completed `TODO.md` task, run the best available verification for that item before checking it off.

Use this order:

1. UI/browser task: run browser verification. Prefer Playwright MCP for local app flows, screenshots, responsive checks, and repeatable interactions. Use Chrome MCP when the task needs the user's real Chrome profile, authenticated browser state, extensions, or remote/profile-dependent pages.
2. React task: run React Doctor diff plus targeted behavior checks.
3. Next.js route/data task: run typecheck plus route/browser verification where practical.
4. Docs-only task: run content/link sanity; browser check only if docs render in-app.
5. Security/auth/payment task: run targeted negative checks and security sanity review.

Record the check in `mct done`:

```bash
~/.claude/bin/mct done "<task-id-or-slug>" --check "playwright-browser-check"
~/.claude/bin/mct done "<task-id-or-slug>" --check "chrome-profile-check"
~/.claude/bin/mct done "<task-id-or-slug>" --check "react-doctor-diff"
```

If the task should be committed immediately after verification, use:

```bash
~/.claude/bin/mct done "<task-id-or-slug>" --check "playwright-browser-check" --commit --all
```

This checks off the TODO item, writes a receipt, stages changes when `--all` is used, and creates a descriptive commit. Without `--all`, it only commits already staged files.

`--all` intentionally excludes `.mct/` state and receipt files from the commit.

If verification cannot run, do not silently check off the task. Either fix the blocker or record the skipped check explicitly:

```bash
~/.claude/bin/mct done "<task-id-or-slug>" --skipped-check "Playwright unavailable: no runnable app script"
```

### Optional TODO.md Structure

Plain checkboxes work:

```markdown
- [ ] Fix pricing toggle persistence
```

Structured hints improve orchestration:

```markdown
- [ ] Fix pricing toggle persistence #react #ui files:app/pricing/page.tsx,components/pricing-toggle.tsx
- [ ] Update pricing docs #docs depends:fix-pricing-toggle-persistence
- [ ] Audit auth redirect #security #blocked
```

Supported hints:

- `#tag` for grouping and skill routing.
- `files:path-a,path-b` for overlap detection.
- `depends:task-id-or-slug` for sequencing.
- `#blocked` or `blocked` for blocked tasks.

## Core Routing

| Situation | Use Skills | Use Subagents | Checks |
| --- | --- | --- | --- |
| Library/framework context needed | `opensrc`, plus task-specific skills | `planner` | official docs/source search, update `opensrc/` stubs |
| New feature or behavior change | `frontend-architecture`, `ui-system`, Superpowers `brainstorming` for ambiguous/creative work | `planner`, then `frontend-implementer` | targeted tests, React Doctor if React changed |
| TODO.md queue execution | `todo-orchestrator`, plus routed skills per item | `planner`, `frontend-implementer`, `reviewer`, parallel subagents only for independent items | per-item verification plus combined review |
| Multi-step implementation from approved requirements | Superpowers `writing-plans`, `frontend-architecture` | `planner`, `frontend-implementer`, `test-runner` | task-level tests, typecheck if shared logic changed |
| Bug fix | `debugging-loop`, maybe `react-doctor` | `planner` for diagnosis, `frontend-implementer`, `test-runner` | regression check that proves the fix |
| UI change | `ui-system`, `design-consistency`, `react-doctor` | `frontend-implementer`, `ui-verifier` if meaningful UI changed | browser/responsive check for meaningful surfaces |
| React component/hook change | `react-quality`, `react-doctor`, `code-review` | `react-doctor-runner`, `reviewer` | `npx -y react-doctor@latest . --verbose --diff` |
| Next.js routing/data change | `nextjs-app-router`, `frontend-architecture` | `planner`, `test-runner` | typecheck and route/data tests if available |
| Refactor | `refactor-safely`, `code-review`, Superpowers `writing-plans` for broad work | `planner`, `reviewer`, `test-runner` | before/after behavior checks |
| Code review | `code-review`, `react-doctor` for React diffs | `reviewer`, `react-doctor-runner` | diff review, targeted diagnostics |
| PR prep | `git-pr-workflow`, `code-review`, `docs-maintainer` | `reviewer`, `test-runner`, `react-doctor-runner` | lint/type/tests as risk requires |
| Docs change | `docs-maintainer` | `docs-writer` | link/content sanity, no build unless docs app requires |
| Performance issue | `performance-audit`, `react-quality` | `planner`, `reviewer` | targeted profile/build/bundle checks only when relevant |
| Security-sensitive code | `code-review`, security sanity workflow | `security-sanity`, `reviewer` | secret scan, auth/session/data-flow review |

## Prompt Routing

Use this when deciding how to respond to the user's wording.

| User wording | MCT behavior |
| --- | --- |
| "plan", "how should we", "architecture", "approach" | Inspect repo, use `planner`, apply Superpowers `brainstorming` if requirements are ambiguous, do not edit. |
| "build", "implement", "add", "create" | If simple and clear, implement with frontend skills. If ambiguous or broad, plan first. |
| "fix", "bug", "not working", "why" | Use `debugging-loop`; do not patch until root cause is known. |
| "review", "check", "is this good" | Use `code-review`; findings first with file/line references. |
| "refactor", "cleanup", "improve architecture" | Use `refactor-safely`; avoid unrelated churn; for broad work, write a plan first. |
| "keep UI same", "only spacing", "only frontend", "vendor side only" | Treat as hard scope constraints. |
| "push", "PR", "commit" | Use `git-pr-workflow`; inspect status/diff first; run event-appropriate checks. |
| "continue", "next", "do the TODOs", "use MCT" with no specific task | Read `TODO.md`, triage unchecked items, execute in safe order. |
| "use MCT" | Apply this whole router for the task. |

## Event Routing

| Event | Automatic or Manual | Behavior |
| --- | --- | --- |
| Claude session start | Automatic Claude hook | Load `CLAUDE.md` and MCT context. |
| User prompt submitted | Automatic Claude hook | Add MCT routing hints when the prompt says `MCT`. |
| MCT prompt submitted and `package.json` exists | Required first workflow step | Run `mct opensrc --fetch-metadata`, then fill relevant library docs from official sources. |
| MCT prompt submitted and `TODO.md` exists | Automatic Claude hook | Inject `TODO.md` preview and require TODO orchestration. |
| Shell command | Automatic Claude hook | Block destructive commands unless explicitly approved. |
| File edit | Automatic Claude hook | Run lightweight secret/sanity scan. |
| React files edited | Stop hook policy | Require React Doctor status in completion receipt when meaningful React changes were made. |
| Before commit | Git hook template | Run secret scan and React Doctor diff for React projects. |
| Before push | Git hook template | Run configured stronger checks from `automation-policy.json`. |
| PR prep | Slash command | Run review, React Doctor if relevant, and draft PR text. |

## MCT CLI

Use the deterministic CLI when available:

```bash
~/.claude/bin/mct status
~/.claude/bin/mct status --md
~/.claude/bin/mct plan
~/.claude/bin/mct next --claim
~/.claude/bin/mct done "<task-id-or-slug>" --check "..."
~/.claude/bin/mct done "<task-id-or-slug>" --check "..." --commit --all
~/.claude/bin/mct commit --task "<task-id-or-slug>" --all
~/.claude/bin/mct self-update
~/.claude/bin/mct opensrc --fetch-metadata
~/.claude/bin/mct classify
~/.claude/bin/mct verify --mode pre-commit
~/.claude/bin/mct verify --mode pre-push
~/.claude/bin/mct verify --mode ci
~/.claude/bin/mct receipt --summary "..." --completed-task "..." --check "..."
```

The CLI writes state and receipts under `.mct/` in the project root.

Project bootstrap:

```bash
~/.claude/bin/mct init --project
~/.claude/bin/mct init --project --ci
```

`--project` creates `.mct/state.json`, adds `.mct/` to `.gitignore`, creates a `TODO.md` template if missing, and installs Git hooks. `--ci` also installs a GitHub Actions workflow and vendored `mct` CLI copy under `.github/mct/`.

Toolkit update:

```bash
~/.claude/bin/mct self-update
```

If the source repo is not in a standard location, set `MCT_SOURCE=/path/to/skills-hub`.

## Skill Decision Rules

- Use `frontend-architecture` whenever file ownership, boundaries, data flow, or route structure can be affected.
- Use `opensrc` at the start of MCT in projects with `package.json`, and whenever external library docs/context matter.
- Use `todo-orchestrator` whenever `TODO.md` exists and MCT is requested.
- Use `ui-system` whenever visible UI changes.
- Use `react-doctor` whenever React files changed or before committing React work.
- Use `debugging-loop` whenever something is broken or a command fails repeatedly.
- Use `code-review` before commits, PRs, and after non-trivial edits.
- Use Superpowers `brainstorming` before ambiguous creative/product/design work.
- Use Superpowers `writing-plans` before broad multi-step implementation.
- Use Superpowers verification discipline before claiming work is complete.

## Check Selection

Do not run everything by default.

| Changed Surface | Minimum Checks |
| --- | --- |
| Copy-only | diff review |
| CSS/Tailwind only | diff review, browser check if layout risk |
| React component/hook | React Doctor diff, targeted test if behavior changed |
| Shared TypeScript logic | typecheck, targeted unit test |
| Next.js route/data fetching | typecheck, route/data test if available |
| Auth/payment/security | typecheck, tests, security sanity review |
| Broad refactor | typecheck, relevant tests, review, React Doctor if React changed |
| PR-ready | risk-based lint/type/tests plus review summary |

## Completion Receipt

Every MCT task must end with:

- What changed.
- Skills/workflows used.
- TODO items completed/open/blocked when `TODO.md` exists.
- Checks run.
- Checks skipped and why.
- Risks or follow-ups.

Also write a structured receipt with `~/.claude/bin/mct receipt` when MCT was used for TODO queue execution, PR readiness, or a multi-step task.

## TODO Commit Flow

When solving tasks from `TODO.md`, prefer one descriptive commit per verified TODO item or safe independent batch.

Use this sequence:

1. Complete the TODO item.
2. Run post-task verification.
3. Run `mct done ... --check ... --commit --all`.
4. Continue to the next TODO item.

Commit rules:

- Do not commit without a verification check or explicit skipped-check reason.
- Commit messages must describe the actual completed TODO task.
- Do not mention Claude, MCT, AI, or agent tooling in commit subjects.
- Do not force commits when unrelated user changes are present unless the user explicitly wants all changes included.

## Anti-Patterns

- Do not run full builds after tiny changes unless asked.
- Do not auto-run every skill. Route by task and changed surface.
- Do not patch bugs without root cause.
- Do not redesign UI during a narrow UI request.
- Do not make global architecture changes during feature work unless required.
- Do not trust generated PR text without checking the actual diff.
