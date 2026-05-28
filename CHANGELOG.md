# Changelog

All notable changes to the MCT toolkit are documented here.

## [2.0.0] - unreleased (production-hardening)

Hardening pass that makes verification real instead of self-asserted, with a
test suite and red-team regression probes proving the gates cannot be faked.

### Added
- `tests/` — stdlib `unittest` suite (70+ tests) covering the TODO parser,
  dependency/planning logic, file classification, state/config load-save, and
  the verification helpers.
- `scripts/redteam.sh` — red-team regression probes; every previously-working
  bypass must be blocked, plus allow-cases proving legitimate evidence is
  accepted.
- `scripts/check.sh` — one-command status: unit tests + red-team + strict audit.
- `mct run-check <name>` and `mct done --run-check <name>` — execute a check
  (typecheck/test/react-doctor) for real and record its actual exit code.
- Structured logging on stderr; `MCT_DEBUG=1` enables debug output.

### Changed (security)
- Completion verification is no longer satisfiable by fabricated strings:
  - Required checks now match by canonical name equality, not loose substring
    matching over a free-text blob. `--check auth` no longer satisfies a
    security task's required `negative-path-check`.
  - Skips must be explicit `name=reason` with a non-empty reason; a vague
    `--skipped-check 'browser skip'` no longer satisfies anything.
  - `browser-proof` requires a real artifact (a screenshot/proof file that
    exists, is non-empty, and has a valid image magic number) — a formatted
    evidence string alone is rejected.
  - Deterministically runnable checks (typecheck/test/react-doctor) must be
    executed via `--run-check`, not merely claimed.
- `mct done` now commits **before** flipping the TODO checkbox, so a failed
  commit never leaves a task marked done-but-uncommitted.
- `mct browser-proof` rejects empty or non-image screenshot files.
- The dangerous-command guard (`guard-dangerous-command.py`) now tokenizes the
  command with `shlex` and inspects the real command name + args instead of
  substring-matching raw text. It blocks recursive-force deletes of absolute /
  home / root paths (any flag order, incl. behind `sudo`/`xargs`), `mkfs`, `dd`
  to a device, `find / -delete`, `chmod -R 777`, destructive `git`
  (`reset --hard`, `clean -fd`, `push --force`/`-f`), fork bombs, and redirects
  to raw block devices — while no longer false-positiving on dangerous words
  used as data (e.g. `echo "rm -rf /"`) or relative deletes (`rm -rf dist`).

- `save_state` now writes atomically (serialize, write temp file, `os.replace`),
  so a crash or serialization error never leaves a truncated `state.json`.
- `mct next --claim` now consumes the claim record: an already-claimed
  (`in_progress`) task is not handed out again unless `--reclaim` is passed.

- Git hooks (`pre-commit`/`pre-push`) now FAIL CLOSED when the `mct` binary is
  missing (exit non-zero) instead of silently passing; set `MCT_ALLOW_MISSING=1`
  to bypass intentionally.
- New `mct doctor` reports whether the repo's git hooks are installed and wired
  to the enforced path.
- `run_package_script` logs a visible warning and records a skipped check when a
  requested npm script is absent, instead of silently reporting success.

- Every `except Exception` fallback now logs (warnings for MCT's own
  state/config/policy corruption, debug for optional files) instead of swallowing
  errors silently.

- TODO parsing now warns on malformed checkbox lines and skips tag-only items
  with no real task text, instead of silently dropping or creating empty tasks.
- Dependency resolution matches unambiguous bare tokens (slug words / tags), so
  mutually dependent tasks form a real, cycle-detectable edge.

- README documents a "What Is Enforced vs Advisory" section that states real
  (code-enforced) guarantees vs advisory guidance, and clarifies that MCT is
  human-in-the-loop discipline tooling, not a self-driving autonomous agent.
  AGENTS.md and MCT.md point to it.

### Notes
- `VERSION` bumped to `2.0.0`.
