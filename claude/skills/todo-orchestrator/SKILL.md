---
name: todo-orchestrator
description: Use when MCT is requested and a project TODO.md exists, or when the user asks to continue, execute, triage, or complete TODO items. Converts TODO.md into a safe sequential or parallel execution queue.
---

# TODO Orchestrator

Use `TODO.md` as the task queue when present.

## Workflow

1. Read root `TODO.md`.
2. Parse unchecked items and nearby notes.
3. Classify each item:
   - independent
   - dependent
   - blocked
   - risky
   - needs clarification
4. Choose execution mode:
   - sequential for dependent, risky, or overlapping work;
   - parallel only for independent work with separate files and separate checks.
5. Execute or dispatch tasks using the relevant skills for each item.
6. Run post-task verification after every completed item.
7. Review combined changes after each batch.
8. Update `TODO.md` checkboxes only through `mct done` when possible.
9. Create a descriptive commit after each verified TODO item when using the TODO queue workflow.
10. Report completed, blocked, skipped, checks, commits, and risks.

## Rules

- User prompt beats `TODO.md` when they conflict.
- Do not delete TODO items unless explicitly requested.
- Do not mark an item complete unless the repo state and verification support it.
- For UI/browser TODOs, run Playwright MCP when validating local flows/screenshots/responsiveness; use Chrome MCP when validation needs the user's real Chrome profile, auth state, extensions, or remote/profile-dependent pages.
- For non-UI TODOs, run the most relevant targeted test/check and record it.
- `mct done` must include at least one `--check` or `--skipped-check` reason.
- Use `mct done <task> --check <check> --commit --all` to check off and commit a verified TODO item.
- Commit one TODO item at a time unless a batch was explicitly classified as independent and safe.
- If a task is ambiguous and a wrong choice is costly, ask before editing.
- If a task can be split into safe smaller items, split it in the plan before implementation.
- Keep parallel work conservative; merging conflicting subagent outputs costs more than it saves.

## Output

End with:

- completed TODO items;
- TODO items still open;
- blocked items and blocker reason;
- checks run;
- checks skipped and why.
