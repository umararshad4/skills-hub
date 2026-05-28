#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${HOME}/.claude"

mkdir -p "${TARGET_DIR}"

copy_dir() {
  local name="$1"
  mkdir -p "${TARGET_DIR}/${name}"
  rsync -a --delete "${ROOT_DIR}/${name}/" "${TARGET_DIR}/${name}/"
}

STAMP="$(date +%Y%m%d%H%M%S)"

# User-owned files: back up before overwriting so a reinstall never silently
# clobbers a customized global CLAUDE.md or settings.json.
backup_then_copy() {
  local src="$1" dst="$2"
  if [ -f "${dst}" ] && ! cmp -s "${src}" "${dst}"; then
    cp "${dst}" "${dst}.bak-${STAMP}"
    echo "Backed up existing ${dst} -> ${dst}.bak-${STAMP}" >&2
  fi
  cp "${src}" "${dst}"
}

backup_then_copy "${ROOT_DIR}/CLAUDE.md" "${TARGET_DIR}/CLAUDE.md"
backup_then_copy "${ROOT_DIR}/MCT.md" "${TARGET_DIR}/MCT.md"
backup_then_copy "${ROOT_DIR}/settings.json" "${TARGET_DIR}/settings.json"
cp "${ROOT_DIR}/install.sh" "${TARGET_DIR}/install.sh"
cp "${ROOT_DIR}/update.sh" "${TARGET_DIR}/update.sh"

copy_dir "skills"
copy_dir "agents"
copy_dir "commands"
copy_dir "hooks"
copy_dir "git-hooks"
copy_dir "bin"
copy_dir "lib"
copy_dir "policies"
copy_dir "templates"

find "${TARGET_DIR}/hooks/scripts" -type f -name "*.py" -exec chmod +x {} \;
find "${TARGET_DIR}/bin" -type f -exec chmod +x {} \;
find "${TARGET_DIR}/git-hooks" -type f -exec chmod +x {} \;
chmod +x "${TARGET_DIR}/install.sh" "${TARGET_DIR}/update.sh"

echo "Installed Claude engineering toolkit to ${TARGET_DIR}"
echo "Restart Claude Code sessions for SessionStart hooks to load fresh context."
