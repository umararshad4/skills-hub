"""Autonomous control loop (`mct run`): drain, guards, rollback, and — critically —
that it inherits the verified completion gate (cannot fake a UI task done)."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MCT = REPO / "claude" / "bin" / "mct"
FAKE_AGENT = REPO / "tests" / "fixtures" / "fake_agent.sh"
AGENT_CMD = f"bash {FAKE_AGENT}"


def git(root, *args):
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True)


def make_repo(tmp, todo):
    root = Path(tmp)
    git(root, "init", "-q")
    git(root, "config", "user.email", "t@example.com")
    git(root, "config", "user.name", "tester")
    (root / "seed.txt").write_text("seed\n")
    (root / "TODO.md").write_text(todo)
    git(root, "add", "-A")
    git(root, "commit", "-qm", "seed")  # clean tree at run start
    return root


def mct_run(root, *args):
    return subprocess.run([sys.executable, str(MCT), "run", *args], cwd=str(root), capture_output=True, text=True)


def todo_text(root):
    return (Path(root) / "TODO.md").read_text()


class TestPreconditions(unittest.TestCase):
    def test_dry_run_prints_plan_and_mutates_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(tmp, "- [ ] write the onboarding notes #docs\n")
            before = todo_text(root)
            result = mct_run(root, "--dry-run")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(json.loads(result.stdout)["dryRun"])
            self.assertEqual(todo_text(root), before)

    def test_refuses_without_yes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(tmp, "- [ ] write the onboarding notes #docs\n")
            result = mct_run(root, "--agent-cmd", AGENT_CMD)
            self.assertEqual(result.returncode, 2)
            self.assertIn("- [ ]", todo_text(root))  # untouched

    def test_requires_an_agent_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(tmp, "- [ ] write the onboarding notes #docs\n")
            result = mct_run(root, "--yes")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("work-step command", result.stderr)


class TestDrain(unittest.TestCase):
    def test_drains_completable_tasks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(tmp, "- [ ] write note one #docs\n- [ ] write note two #docs\n")
            result = mct_run(root, "--yes", "--agent-cmd", AGENT_CMD, "--max-iterations", "10")
            self.assertEqual(result.returncode, 0, result.stderr)
            out = json.loads(result.stdout)
            self.assertEqual(out["done"], 2)
            self.assertEqual(out["blocked"], 0)
            self.assertNotIn("- [ ]", todo_text(root))
            self.assertEqual(todo_text(root).count("- [x]"), 2)

    def test_max_iterations_stop_guard(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(tmp, "- [ ] write note one #docs\n- [ ] write note two #docs\n")
            result = mct_run(root, "--yes", "--agent-cmd", AGENT_CMD, "--max-iterations", "1")
            out = json.loads(result.stdout)
            self.assertEqual(out["stopReason"], "max-iterations")
            self.assertEqual(out["done"], 1)  # only one task before the guard trips


class TestInheritsGate(unittest.TestCase):
    def test_ui_task_is_blocked_not_faked_done(self):
        # The agent edits files but produces NO browser proof. The loop must NOT
        # mark the UI task done — the same gate as `mct done` applies.
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(tmp, "- [ ] polish the pricing hero #ui\n")
            result = mct_run(root, "--yes", "--agent-cmd", AGENT_CMD, "--max-iterations", "5", "--retries", "0")
            out = json.loads(result.stdout)
            self.assertEqual(out["done"], 0, "a UI task with no browser proof must not be marked done")
            self.assertEqual(out["blocked"], 1)
            self.assertNotIn("- [x]", todo_text(root))
            self.assertIn("#blocked", todo_text(root))


if __name__ == "__main__":
    unittest.main()
