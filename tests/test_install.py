"""install.sh must never destroy a user's own ~/.claude content without a backup."""
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
INSTALL = REPO / "claude" / "install.sh"


@unittest.skipUnless(shutil.which("rsync"), "rsync not available")
class TestInstallPreservesUserContent(unittest.TestCase):
    def test_user_authored_skill_is_backed_up_not_lost(self):
        with tempfile.TemporaryDirectory() as home:
            user_skill = Path(home) / ".claude" / "skills" / "my-private-skill"
            user_skill.mkdir(parents=True)
            (user_skill / "SKILL.md").write_text("my private skill\n")

            env = {**os.environ, "HOME": home}
            result = subprocess.run(["bash", str(INSTALL)], capture_output=True, text=True, env=env)
            self.assertEqual(result.returncode, 0, result.stderr)

            # Safety property (rsync-flavor independent): the user's content must be
            # RECOVERABLE — preserved in place (openrsync) or moved to a backup
            # (GNU rsync --delete --backup-dir) — never silently destroyed.
            target = Path(home) / ".claude"
            live = user_skill / "SKILL.md"
            backups_dir = target / ".mct-backups"
            backups = list(backups_dir.rglob("my-private-skill/SKILL.md")) if backups_dir.exists() else []
            survivors = ([live] if live.exists() else []) + backups
            self.assertTrue(survivors, "user-authored skill must be preserved in place or backed up, never lost")
            self.assertEqual(survivors[0].read_text(), "my private skill\n")

    def test_custom_global_claude_md_is_backed_up(self):
        with tempfile.TemporaryDirectory() as home:
            target = Path(home) / ".claude"
            target.mkdir(parents=True)
            (target / "CLAUDE.md").write_text("MY CUSTOM GLOBAL GUIDE\n")

            env = {**os.environ, "HOME": home}
            result = subprocess.run(["bash", str(INSTALL)], capture_output=True, text=True, env=env)
            self.assertEqual(result.returncode, 0, result.stderr)

            backups = list(target.glob("CLAUDE.md.bak-*"))
            self.assertTrue(backups, "an existing custom global CLAUDE.md must be backed up before overwrite")
            self.assertEqual(backups[0].read_text(), "MY CUSTOM GLOBAL GUIDE\n")


if __name__ == "__main__":
    unittest.main()
