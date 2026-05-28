#!/usr/bin/env bash
# Test work-step that writes a file containing a secret. Assembled at runtime so
# this fixture source carries no literal secret pattern.
set -euo pipefail
PAD=$(printf 'A%.0s' $(seq 24))
printf 'API_KEY = "sk-%s"\n' "$PAD" >> "${MCT_ROOT}/leaked-config.txt"
exit 0
