#!/usr/bin/env bash
# Adversarial work-step: does real work AND shifts TODO.md lines by inserting a
# new task at the top — to test that the loop re-resolves the task's current line
# instead of flipping a now-wrong (shifted) checkbox.
set -euo pipefail
printf 'work for %s\n' "${MCT_TASK_ID}" >> "${MCT_ROOT}/work.txt"
{ head -1 "${MCT_ROOT}/TODO.md"; echo '- [ ] Injected intruder line'; tail -n +2 "${MCT_ROOT}/TODO.md"; } > "${MCT_ROOT}/TODO.md.tmp"
mv "${MCT_ROOT}/TODO.md.tmp" "${MCT_ROOT}/TODO.md"
exit 0
