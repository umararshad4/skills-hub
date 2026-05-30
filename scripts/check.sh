#!/usr/bin/env bash
# One-command objective status for the toolkit.
#
#   1. unit tests        (python3 -m unittest discover -s tests)
#   2. red-team probes   (scripts/redteam.sh — known bypasses must be blocked)
#   3. strict self-audit (mct audit --strict — non-zero on high-severity issues)
#   4. security smoke    (syntax, local-only reporting, guard smoke, action pinning visibility)
#
# Exits non-zero if any step fails. This is the gate the project must pass
# before it can honestly be called production-ready.
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO"
rc=0

echo "=== 1/4 unit tests ==="
if python3 -m unittest discover -s tests -q 2>&1 | tail -3; then
  echo "unit: PASS"
else
  echo "unit: FAIL"; rc=1
fi

echo
echo "=== 2/4 red-team bypass probes ==="
if bash scripts/redteam.sh; then
  echo "redteam: PASS"
else
  echo "redteam: FAIL"; rc=1
fi

echo
echo "=== 3/4 strict self-audit ==="
if python3 claude/bin/mct audit --strict >/dev/null 2>&1; then
  echo "audit: PASS"
else
  echo "audit: FAIL (run: python3 claude/bin/mct audit --strict)"; rc=1
fi

echo
echo "=== 4/4 security smoke ==="
if bash scripts/security-check.sh; then
  echo "security: PASS"
else
  echo "security: FAIL"; rc=1
fi

echo
if [ "$rc" -eq 0 ]; then
  echo "=== OVERALL: PASS ==="
else
  echo "=== OVERALL: FAIL ==="
fi
exit "$rc"
