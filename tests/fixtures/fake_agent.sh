#!/usr/bin/env bash
# Test work-step for `mct run`: makes a real, attributable change so the working
# tree is non-empty (lets the loop proceed to verification). It does NOT produce
# browser proof, so a UI task must still be BLOCKED by the gate, not faked done.
set -euo pipefail
printf 'work for %s (attempt %s)\n' "${MCT_TASK_ID:-?}" "${MCT_ATTEMPT:-?}" >> "${MCT_ROOT}/work-${MCT_TASK_ID}.txt"
exit 0
