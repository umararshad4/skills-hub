# Ralph Loop Protocol — MCT Production Hardening

You are hardening the skills_hub / MCT toolkit at `/Users/m1pro/My_Tech_House/skills_hub` into a
trustworthy, production-usable engineering-discipline toolkit.

**Scope: Target A** — make the existing CLI/hook surface safe, tested, fail-closed, and honest.
Do **not** build an autonomous multi-agent runtime (explicitly out of scope).

You are on branch `harden/production-readiness`. Commit there. **Never push.**

`PRODUCTION_READINESS.md` (repo root) is the authoritative spec + progress checklist.

## Each iteration

1. Run `bash scripts/check.sh` (create it on the first iteration per the spec) to see objective
   status: unit tests + red-team bypass tests + strict self-audit.
2. Pick the **first unchecked** acceptance criterion in `PRODUCTION_READINESS.md`.
3. Implement it fully in the repo source (`claude/bin/mct`, `claude/hooks/scripts/*`,
   `claude/git-hooks/*`, docs). Keep `claude/bin/mct` **Python 3 stdlib only** (zero deps) and stay
   in the existing architecture/style.
4. Add or extend tests in `tests/` (stdlib `unittest`) **and** red-team regression cases in
   `scripts/redteam.sh` that PROVE the hole is closed — a previously-working bypass must now be
   rejected/blocked.
5. Run the tests + redteam and fix until green. Do **not** tick a box unless its `Verify:` command
   actually passes — paste the real command output in your message.
6. Tick the box in `PRODUCTION_READINESS.md`, append a one-line note to its Progress log, update
   `CHANGELOG.md`, and commit with a descriptive message (one criterion per commit when practical).

## Hard rules

- **Verification must be real, not self-asserted** — this is the entire point of the project.
  Never weaken a test or delete a red-team case to go green.
- Do **not** reinstall into `~/.claude` and do **not** modify files outside the repo.
- Test the danger guard ONLY by piping JSON to the hook script, e.g.
  `echo '{"tool_input":{"command":"rm -rf /"}}' | python3 claude/hooks/scripts/guard-dangerous-command.py`
  — NEVER by actually running a destructive command.
- Tests/redteam must target the **repo** binary (`python3 .../claude/bin/mct`, with `MCT_HOME`/
  `MCT_BIN` pointed at repo paths) inside a **throwaway temp git repo** — never against this repo's
  real git history or `~/.claude`.
- If a criterion is genuinely infeasible, record it under "Known limitations" in the spec with the
  reason and move to the next — do not fake it.
- Commit messages must not mention Claude, MCT-as-AI-tooling, or agents; describe the engineering
  change. Author commits as `umar arshad <areeb.virgo12@gmail.com>`.

## Completion

ONLY when **every** acceptance-criterion box in `PRODUCTION_READINESS.md` is checked AND
`bash scripts/check.sh` exits 0: paste the full `check.sh` output as proof, then output exactly:

```
<promise>PRODUCTION READY</promise>
```

Otherwise keep working. If you cannot progress the current criterion, switch to the next one and
note the blocker in the Progress log.
