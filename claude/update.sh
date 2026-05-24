#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "${ROOT_DIR}"

if [ ! -d .git ]; then
  echo "This toolkit folder is not a git repo: ${ROOT_DIR}" >&2
  exit 1
fi

echo "Updating skills-hub from git..."
git pull --ff-only

echo "Installing updated toolkit..."
"${ROOT_DIR}/claude/install.sh"

echo
echo "Update complete."
echo "Restart Claude Code sessions for fresh hook context."
echo "For each project that uses MCT hooks, refresh project automation with:"
echo "  ~/.claude/bin/mct init --project"
echo "For projects using vendored CI, run:"
echo "  ~/.claude/bin/mct init --project --ci"
