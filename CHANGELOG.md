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

### Notes
- `VERSION` bumped to `2.0.0`.
