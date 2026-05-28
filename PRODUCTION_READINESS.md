# Production Readiness Hardening Spec

Goal: harden the MCT toolkit into a **trustworthy, tested, fail-closed engineering-discipline
toolkit** that a real team or another agent can adopt in production. This is **Target A**: make
the existing CLI/hook surface safe and honest. It does **not** add an autonomous multi-agent
runtime (that is explicitly out of scope).

Guiding principle (the whole point): **verification must be real, not self-asserted.** Every
acceptance criterion below is "done" only when its `Verify:` command actually passes. Never weaken
a test or delete a red-team case to go green.

Keep `claude/bin/mct` **Python 3 stdlib only** (zero third-party deps). Stay within the existing
architecture and code style.

---

## How progress is measured

A single command must report objective status:

```
bash scripts/check.sh
```

`scripts/check.sh` (create it) runs, in order, and exits non-zero if any step fails:
1. `python3 -m unittest discover -s tests -v`  (unit suite, >= 30 test methods)
2. `bash scripts/redteam.sh`  (every previously-working bypass must now be BLOCKED)
3. `python3 claude/bin/mct audit --strict`  (strict self-audit on this repo: non-zero on high-severity)

The Ralph loop may output `<promise>PRODUCTION READY</promise>` **only** when every box below is
checked AND `bash scripts/check.sh` exits 0, with the full output pasted as proof.

---

## Acceptance criteria

### AC1 — Test suite exists and passes
- [ ] `tests/` dir with stdlib `unittest`; runnable via `python3 -m unittest discover -s tests`.
- [ ] Covers: TODO parser (incl. malformed `- []`, `-[ ]`, empty `- [ ]`), dependency graph +
      cycle detection (bare dep tokens), `classify_files`, `recommend_checks`, `check_satisfies`,
      `valid_browser_evidence`, `missing_required_checks`, `browser_artifact_issue`, state
      load/save roundtrip + corrupt-state fallback, audit issue detection.
- [ ] >= 30 test methods, all passing.
- Verify: `python3 -m unittest discover -s tests -v` exits 0; test count >= 30.

### AC2 — Verification is no longer trivially fakeable (the core fix)
- [ ] (a) `check_satisfies`: a required check is satisfied ONLY by (i) a recorded executed check
      with a pass result, or (ii) an EXPLICIT per-check skip with a non-empty reason
      (e.g. `--skipped-check typecheck=reason`). Dumping a keyword into a free-text blob must NOT
      satisfy a required check. `mct done --check auth` must NOT satisfy a `#security` task's
      required `negative-path-check`.
- [ ] (b) Browser evidence requires a REAL artifact: when a UI task is completed with a browser
      check, evidence must reference a screenshot/proof file that EXISTS, is NON-EMPTY, and (for
      screenshots) has a valid image magic number (PNG/JPEG/WebP/GIF). A bare formatted string with
      no artifact is REJECTED.
- [ ] (c) `mct` can actually RUN a check and record the real exit code: add `mct run-check <name>`
      (or `mct done --run-check ...`) that executes typecheck/test/react-doctor and records
      `executed=true, exitCode=N, result=pass|fail`. Audit distinguishes executed vs self-reported.
- Verify: red-team cases R1 (fake browser evidence → rejected), R2 (`--check auth` for required
  negative-path → rejected), R3 (`--skipped-check 'browser skip'` blob bypass → rejected) all pass
  in `scripts/redteam.sh`; plus unit tests for each.

### AC3 — Danger guard hardened (no more security theater)
- [ ] Rewrite `claude/hooks/scripts/guard-dangerous-command.py` to detect destructive commands
      structurally (tokenize; don't just substring-match the raw text). Must BLOCK: `rm -rf /`,
      `rm -rf /*`, `rm -rf ~`, `rm -rf $HOME`, `rm -fr /<path>`, `rm --recursive --force ...`,
      `mkfs.*`, `dd ... of=/dev/...`, `find / -delete`, `git reset --hard`, `git clean -fdx`,
      `git push -f` / `--force`, `chmod -R 777`, fork bomb `:(){ :|:& };:`, `> /dev/sda`.
- [ ] Reduce false positives: do not block solely because a dangerous word appears as data/text;
      match the actual command being run.
- Verify: red-team R4..Rn — each previously-bypassing command now yields `{"decision":"block"}`;
  unit tests for both block and allow cases.

### AC4 — Fail-closed enforcement
- [ ] Git hooks (`claude/git-hooks/pre-commit`, `pre-push`): when `$MCT_BIN` is missing, FAIL
      CLOSED (non-zero) unless `MCT_ALLOW_MISSING=1` is explicitly set; print a clear message.
- [ ] Add `mct doctor` that reports whether repo git hooks are installed/active and whether the
      enforced path is wired.
- [ ] `run_package_script` returning 0 for a missing script must LOG a visible warning and record
      the check as skipped (not silently "passed").
- Verify: unit test for missing-binary path (hook exits non-zero without the env var, 0 with it);
  `mct doctor` output asserted.

### AC5 — State integrity
- [ ] `save_state` writes atomically (tempfile + `os.replace`).
- [ ] `mct next --claim` actually CONSUMES claim state: skips tasks already `in_progress`/`done`
      (with a `--reclaim` or TTL escape hatch). No write-only dead fields.
- Verify: unit tests — atomic write leaves no partial file on simulated failure; a second
  `next --claim` does not re-hand an already-claimed task.

### AC6 — Observability & error handling
- [ ] Import `logging`; add `MCT_DEBUG=1` / `-v` to surface logs.
- [ ] Replace silent `except Exception` blocks so they log at warning level (still graceful).
- Verify: `grep` shows no bare silent swallow without a log call; unit test asserts corrupt-state
  fallback emits a warning under `MCT_DEBUG=1`.

### AC7 — Parser & robustness
- [ ] Malformed TODO lines handled deterministically and documented (no silent garbage tasks).
- [ ] Cycle detection works with bare dependency tokens.
- Verify: unit tests for malformed lines and for a 2-task mutual-dependency cycle.

### AC8 — `command_done` ordering / no inconsistent state
- [ ] Do not flip the TODO checkbox + write the receipt BEFORE a commit that can fail. Either
      commit first, or roll back the checkbox/state if the commit fails.
- Verify: unit test simulating commit failure → checkbox NOT flipped, state consistent.

### AC9 — Honest docs + versioning
- [ ] README / AGENTS.md / MCT.md updated with an "Enforced vs Advisory" section that states real
      guarantees honestly; remove/qualify the unqualified "autonomous orchestration" claim.
- [ ] `CHANGELOG.md` added and kept updated per criterion.
- [ ] `VERSION` in `claude/bin/mct` bumped (>= 2.0.0).
- Verify: docs contain the "Enforced vs Advisory" section; CHANGELOG present; version bumped.

### AC10 — One-command check + CI + strict audit
- [ ] `python3 claude/bin/mct audit --strict` exists and returns non-zero on any high-severity
      issue regardless of `--warn-only`.
- [ ] `scripts/check.sh` runs unittest + redteam + strict self-audit and exits non-zero on failure.
- [ ] CI template (`claude/templates/ci/github-actions/mct.yml`) runs `scripts/check.sh`.
- Verify: `bash scripts/check.sh` exits 0 on a healthy tree.

---

## Known limitations (record here instead of faking anything)

- (Out of scope by design) No autonomous control loop / multi-agent dispatch — this is Target A.
- _Add any criterion that proves genuinely infeasible, with the reason._

---

## Progress log

_The loop appends a one-line note per iteration: which AC advanced and the verify result._
