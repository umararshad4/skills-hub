# Changelog

All notable changes to the MCT toolkit are documented here.

## [3.0.0] - unreleased (autonomy: the `mct run` control loop)

Adds a genuine in-code control loop. Previously `mct` was a one-shot dispatcher
and the "loop" lived only in advisory markdown; now it lives in code.

### Added
- **`mct run`** — an autonomous loop that drains the runnable TODO queue: for each
  task it claims the task, dispatches a pluggable work-step command, runs the
  required deterministic checks, and on success completes the task through the
  **same verified `complete_task` gate as `mct done`** (commit, then flip the
  checkbox). On failure it rolls back the attempt non-destructively (`git stash`,
  never `reset --hard`), retries, then marks the task `#blocked` and moves on.
  - Work step is pluggable: `--agent-cmd`, `MCT_AGENT_CMD`, or
    `autonomy.agentCommand` (mct owns the loop; the agent only edits the repo).
  - Safety: requires `--yes` to mutate the repo, requires a clean tree at start
    (unless `autonomy.allowDirtyStart`), and refuses with no work command.
  - Hard stop guards: `--max-iterations`, `--max-failures`, `--max-seconds`, a
    per-task timeout, and a `.mct/STOP` kill-switch (`mct run --stop`).
  - Resumable run-state under `.mct/runs/<runId>.json`; `--dry-run` previews.
- **Crucially, the loop cannot fake completion**: a UI task with no real browser
  proof is blocked, not marked done (regression-tested as AC-RUN).

### Fixed — loop bugs found by an adversarial red-team (before shipping)
- **Clone-and-run RCE closed**: a committed `.mct/config.json` can no longer waive
  confirmation — `--yes`/`MCT_RUN_YES` is required from the caller regardless of
  config, and a config-sourced agent command warns loudly. A bare `mct run` in a
  hostile repo no longer executes committed code.
- **No false completion**: the no-op guard now measures the *agent's own delta*
  (not absolute tree dirtiness), so a leftover `#blocked` edit can't make an
  unedited task get marked done.
- **No swallowed bookkeeping / duplicate commits**: the checkbox flip is committed
  atomically with its task (flip-before-commit, revert-on-failure), `.mct/` is
  gitignored so the rollback stash can't capture MCT state, and `#blocked` markers
  are committed (durable across rollbacks). The run ends with a clean tree.
- **No secret commits**: the autonomous commit path runs the secret scanner and
  blocks the task instead of committing a detected secret.
- **Scoped commits**: when a task declares `files:`, only those (plus `TODO.md`)
  are staged, instead of `git add -A` sweeping unrelated/stray files.
- **No orphaned processes**: the agent runs in its own process group and the whole
  group is killed on timeout. The `.mct/STOP` kill-switch can't crash the loop.

### Added — self-improvement (local crash capture + opt-in upstream issue)
- **Local crash capture**: an unexpected `mct` error writes a REDACTED, LOCAL-ONLY
  report to `.mct/crashes/<sig>.json` and re-raises (the error still surfaces).
  Allowlisted fields only — never an env dump, cwd, repo name, or file contents.
  Secrets and home/user paths are scrubbed. `MCT_NO_CRASH_CAPTURE=1` opts out.
  Intentional `SystemExit`s are never captured.
- **`mct report-issue`**: view (`--last --print`), `--status`, and — strictly
  OPT-IN — open a redacted issue upstream (`--open-issue`). Egress is **OFF by
  default** and fails closed: it requires `mct report-issue --enable --confirm`,
  `--yes`, an authenticated `gh` (ambient `GITHUB_TOKEN`/`GH_TOKEN` are ignored),
  passes a residual-secret tripwire on the final payload, is deduped by error
  signature, and is hard-disabled by `MCT_NO_NETWORK=1`/`MCT_AUTOREPORT=0`. The
  upstream repo is a pinned constant (anti-SSRF); contribute-back is ISSUE-ONLY
  (auto-fix PRs are intentionally not implemented).
- Broadened the secret scanner (AWS/GitHub/GitLab/Slack/JWT/`password=` in
  addition to `sk-`/PEM), shared by the staged-diff scan and report redaction.

### Notes
- `VERSION` → `3.0.0` (the marketed "no autonomous control loop" invariant is
  reversed).

## [2.1.0] - unreleased (second-order hardening from adversarial re-audit)

An independent adversarial audit reproduced bypasses that the 2.0.0 hardening
missed (first-order only). All are now closed with regression tests:

### Security
- **Dangerous-command guard** rewritten to handle attacks it previously allowed:
  bundled interpreter flags (`bash -lc`/`-cx`/`-xc`, `sh -ec`, `zsh -lc "rm -rf /"`)
  now recurse into the payload; `git` global options (`git --no-pager`/`-c`/`-C`
  before the subcommand) are stripped before classifying `reset --hard`/`clean -fd`;
  `tee`/`>|`/raw devices (`/dev/rdisk0`), `wipefs`/`shred`/`blkdiscard` on a device,
  `chown -R` of a system root, `xargs rm -rf`, and writes to protected files
  (`/etc/passwd`) are now blocked. A non-string command no longer crashes the guard.
- **Browser proof realism**: a forged PNG header with no `IDAT` pixel data, a JPEG
  without an end-of-image marker, a WEBP with a mismatched RIFF size, and a 1-byte
  `proof=` file are all rejected (previously accepted as evidence).
- **Attestation realism**: a single-character/keyword attestation or skip reason
  (e.g. `--check negative-path-check=x`) no longer satisfies a required check; a
  substantive multi-word reason is required. (Non-executable attestations remain
  honor-based — this rejects degenerate detail, it does not verify truth.)

### Reliability
- `load_state`/`load_config`/`load_policy`/`read_package_json` no longer crash on
  non-dict JSON (`state.json = "null"`, `package.json = "[1,2]"`) — they fall back
  to defaults with a warning.
- Pathologically deep `depends:` chains no longer crash dependency analysis
  (RecursionError is caught and reported).

### Install safety
- `install.sh` now syncs with `--backup-dir`, so `--delete` can never destroy a
  user's own `~/.claude/skills`/`commands`/`agents` content without a recoverable
  copy (verified across GNU rsync and openrsync).

### Internal
- Extracted the verified completion gate into `complete_task` (+ `CompletionBlocked`);
  `mct done` is now a thin caller (behavior preserved). Prepares the gate for reuse
  by the forthcoming autonomous `mct run` loop.

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

- Closed bypasses surfaced by an adversarial re-audit:
  - The dangerous-command guard now recurses into interpreter payloads, so
    `bash -c "rm -rf /"`, `sh -c '...'`, and `eval "..."` are analyzed (benign
    payloads like `bash -c "ls"` still pass).
  - `mct final-check --strict` is now a registered flag (was an argparse crash,
    exit 2) and propagates to the audit.
  - `browser-proof` rejects degenerate screenshots: a screenshot must be a
    substantive image (>= 64px per side, or >= 1KB when dimensions are
    unparseable), so a 1x1 painted PNG no longer counts as proof.
  - `install.sh` backs up an existing global `CLAUDE.md`/`MCT.md`/`settings.json`
    to a timestamped `.bak` before overwriting, instead of clobbering silently.

### Notes
- `VERSION` bumped to `2.0.0`.
