#!/usr/bin/env bash
# Lightweight supply-chain and local-safety checks with no third-party deps.
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO"

rc=0

echo "== security: Python syntax =="
if python3 -m py_compile claude/bin/mct claude/hooks/scripts/*.py; then
  echo "py-compile: PASS"
else
  echo "py-compile: FAIL"; rc=1
fi

echo
echo "== security: local-only crash reporting =="
if python3 claude/bin/mct report-issue --status | grep -q "local-only"; then
  echo "reporting-egress: PASS"
else
  echo "reporting-egress: FAIL"; rc=1
fi

echo
echo "== security: destructive-command guard smoke =="
if printf '%s' '{"tool_input":{"command":"bash -lc \"rm -rf /\""}}' \
  | python3 claude/hooks/scripts/guard-dangerous-command.py \
  | grep -q '"decision".*"block"'; then
  echo "danger-guard: PASS"
else
  echo "danger-guard: FAIL"; rc=1
fi

echo
echo "== security: GitHub Actions pinning visibility =="
python3 - <<'PY'
from pathlib import Path
import re
bad = []
paths = list(Path(".github/workflows").glob("*.yml"))
paths.extend(Path("claude/templates/ci").glob("**/*.yml"))
for path in paths:
    for no, line in enumerate(path.read_text(errors="ignore").splitlines(), 1):
        m = re.search(r"uses:\s*([^@\s]+)@([^\s#]+)", line)
        if m and not re.fullmatch(r"[0-9a-fA-F]{40}", m.group(2)):
            bad.append(f"{path}:{no}: {m.group(1)}@{m.group(2)} is tag-pinned, not SHA-pinned")
if bad:
    print("actions-pinning: WARN")
    for item in bad:
        print(f"  {item}")
else:
    print("actions-pinning: PASS")
PY

exit "$rc"
