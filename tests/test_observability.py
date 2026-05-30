"""AC6: errors are logged, not silently swallowed."""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from mctmod import mct

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


class TestEventLog(unittest.TestCase):
    def test_append_event_writes_jsonl(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = mct.append_event(root, "unit.test", {"ok": True})
            self.assertTrue(path.exists())
            line = path.read_text().strip()
            self.assertIn('"kind": "unit.test"', line)

    def test_append_receipt_uses_unique_names_and_logs_events(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            receipt = {"at": mct.now(), "summary": "first", "completedTasks": [], "checksRun": [], "checksSkipped": [], "browserEvidence": [], "risks": []}
            first = mct.append_receipt(root, dict(receipt))
            second = mct.append_receipt(root, {**receipt, "summary": "second"})
            self.assertNotEqual(first.name, second.name)
            events = (root / ".mct" / "events.jsonl").read_text()
            self.assertEqual(events.count('"kind": "receipt.appended"'), 2)


if __name__ == "__main__":
    unittest.main()
