"""AC4: enforcement fails closed; mct doctor reports wiring."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MCT = REPO / "claude" / "bin" / "mct"
PRE_COMMIT = REPO / "claude" / "git-hooks" / "pre-commit"
PRE_PUSH = REPO / "claude" / "git-hooks" / "pre-push"


def run_hook(hook_path, env_extra):
    env = {**os.environ, "MCT_BIN": "/nonexistent/path/to/mct", **env_extra}
    return subprocess.run(["bash", str(hook_path)], capture_output=True, text=True, env=env)


class TestFailClosed(unittest.TestCase):
    def test_pre_commit_fails_closed_when_binary_missing(self):
        result = run_hook(PRE_COMMIT, {})
        self.assertEqual(result.returncode, 1, "pre-commit should fail closed when mct is missing")
        self.assertIn("failing closed", result.stderr)

    def test_pre_commit_can_be_bypassed_explicitly(self):
        result = run_hook(PRE_COMMIT, {"MCT_ALLOW_MISSING": "1"})
        self.assertEqual(result.returncode, 0, "MCT_ALLOW_MISSING=1 should allow skipping")

    def test_pre_push_fails_closed_when_binary_missing(self):
        result = run_hook(PRE_PUSH, {})
        self.assertEqual(result.returncode, 1)

    def test_pre_push_can_be_bypassed_explicitly(self):
        result = run_hook(PRE_PUSH, {"MCT_ALLOW_MISSING": "1"})
        self.assertEqual(result.returncode, 0)


class TestDoctor(unittest.TestCase):
    def test_doctor_reports_hook_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "-C", str(root), "init", "-q"], check=True)
            result = subprocess.run(
                [sys.executable, str(MCT), "doctor"], cwd=str(root), capture_output=True, text=True
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertIn("pre-commit", report["gitHooks"])
            self.assertIn("pre-push", report["gitHooks"])
            # Freshly initialized repo has no MCT hooks installed.
            self.assertFalse(report["enforcedPathActive"])


if __name__ == "__main__":
    unittest.main()
