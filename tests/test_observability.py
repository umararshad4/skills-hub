"""AC6: errors are logged, not silently swallowed."""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MCT = REPO / "claude" / "bin" / "mct"


class TestNoSilentSwallow(unittest.TestCase):
    def test_every_except_block_logs(self):
        lines = MCT.read_text().splitlines()
        for i, line in enumerate(lines):
            if not line.strip().startswith("except Exception"):
                continue
            indent = len(line) - len(line.lstrip())
            body = []
            for following in lines[i + 1:]:
                if not following.strip():
                    continue
                if (len(following) - len(following.lstrip())) <= indent:
                    break  # dedented out of the except block
                body.append(following)
            blob = "\n".join(body)
            # An except block must log or re-raise somewhere — never silently swallow.
            self.assertTrue(
                "logger." in blob or "raise" in blob,
                f"silent swallow in except block near line {i + 1}: {blob!r}",
            )


class TestCorruptStateWarns(unittest.TestCase):
    def test_corrupt_state_emits_warning_under_debug(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "-C", str(root), "init", "-q"], check=True)
            (root / ".mct").mkdir()
            (root / ".mct" / "state.json").write_text("{ not valid json ")
            env = {**os.environ, "MCT_DEBUG": "1"}
            result = subprocess.run(
                [sys.executable, str(MCT), "status"],
                cwd=str(root), capture_output=True, text=True, env=env,
            )
            self.assertIn("could not parse .mct/state.json", result.stderr)


if __name__ == "__main__":
    unittest.main()
