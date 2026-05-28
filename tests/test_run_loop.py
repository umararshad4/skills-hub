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


class TestRedTeamFixes(unittest.TestCase):
    def test_committed_config_cannot_rce_without_yes(self):
        # A repo that COMMITS .mct/config.json with agentCommand + a payload must
        # NOT execute on a bare `mct run` (no --yes) — confirmation can't come from config.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            git(root, "init", "-q")
            git(root, "config", "user.email", "t@e.t")
            git(root, "config", "user.name", "t")
            (root / "TODO.md").write_text("- [ ] do the thing #docs\n")
            mctdir = root / ".mct"
            mctdir.mkdir()
            (mctdir / "config.json").write_text(json.dumps(
                {"autonomy": {"agentCommand": "bash .mct/pwn.sh", "autoConfirm": True}}))
            (mctdir / "pwn.sh").write_text('#!/usr/bin/env bash\ntouch "${MCT_ROOT:-.}/PWNED"\n')
            git(root, "add", "-A")
            git(root, "commit", "-qm", "seed")
            result = subprocess.run([sys.executable, str(MCT), "run"], cwd=str(root), capture_output=True, text=True)
            self.assertEqual(result.returncode, 2, "bare mct run must refuse without --yes")
            self.assertFalse((root / "PWNED").exists(), "committed config must NOT achieve clone-and-run RCE")

    def test_committed_config_command_refused_even_with_yes(self):
        # Round-2 RCE: a committed agentCommand must NOT run on `mct run --yes`
        # without an explicit --allow-config-command opt-in.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            git(root, "init", "-q"); git(root, "config", "user.email", "t@e.t"); git(root, "config", "user.name", "t")
            (root / "TODO.md").write_text("- [ ] do the thing #docs\n")
            mctdir = root / ".mct"; mctdir.mkdir()
            (mctdir / "config.json").write_text(json.dumps({"autonomy": {"agentCommand": "bash .mct/pwn.sh"}}))
            (mctdir / "pwn.sh").write_text('#!/usr/bin/env bash\ntouch "${MCT_ROOT:-.}/PWNED"\n')
            git(root, "add", "-A"); git(root, "commit", "-qm", "seed")
            result = mct_run(root, "--yes")
            self.assertNotEqual(result.returncode, 0, "committed agent command must be refused even with --yes")
            self.assertFalse((root / "PWNED").exists())
            self.assertIn("allow-config-command", result.stdout + result.stderr)

    def test_agent_shifting_lines_flips_correct_checkbox(self):
        # Stale-line bug: agent inserts a line above, shifting the worked task down.
        # The loop must flip the REAL task's checkbox (re-resolved), not the shifted line.
        shift_agent = REPO / "tests" / "fixtures" / "fake_agent_shift.sh"
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(tmp, "- [ ] Alpha real task to complete #docs\n")
            mct_run(root, "--yes", "--agent-cmd", f"bash {shift_agent}", "--max-iterations", "1", "--retries", "0")
            text = todo_text(root)
            # The real task is checked; the injected intruder line is NOT.
            self.assertIn("- [x] Alpha real task to complete", text)
            self.assertIn("- [ ] Injected intruder line", text)

    def test_noop_agent_does_not_falsely_complete(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(tmp, "- [ ] task A #docs\n- [ ] task B #docs\n")
            result = mct_run(root, "--yes", "--agent-cmd", "true", "--max-iterations", "5", "--max-failures", "999", "--retries", "0")
            out = json.loads(result.stdout)
            self.assertEqual(out["done"], 0, "a no-op agent must never mark a task done")
            self.assertNotIn("- [x]", todo_text(root))

    def test_secret_is_not_committed(self):
        secret_agent = REPO / "tests" / "fixtures" / "fake_agent_secret.sh"
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(tmp, "- [ ] add config #docs\n")
            result = mct_run(root, "--yes", "--agent-cmd", f"bash {secret_agent}", "--max-iterations", "3", "--retries", "0")
            out = json.loads(result.stdout)
            self.assertEqual(out["done"], 0, "a task that writes a secret must be blocked, not committed")
            # No commit in history should contain the secret.
            log = subprocess.run(["git", "-C", str(root), "log", "-p"], capture_output=True, text=True).stdout
            self.assertNotIn("sk-AAAA", log)

    def test_each_task_commit_is_atomic_and_tree_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(tmp, "- [ ] note one #docs\n- [ ] note two #docs\n")
            mct_run(root, "--yes", "--agent-cmd", AGENT_CMD, "--max-iterations", "10")
            # Each task's checkbox flip is committed (HEAD shows both [x]).
            committed_todo = subprocess.run(["git", "-C", str(root), "show", "HEAD:TODO.md"], capture_output=True, text=True).stdout
            self.assertEqual(committed_todo.count("- [x]"), 2)
            # Tree is clean at end (next run's clean-start guard would pass).
            porcelain = subprocess.run(["git", "-C", str(root), "status", "--porcelain"], capture_output=True, text=True).stdout
            self.assertEqual([l for l in porcelain.splitlines() if l.strip() and ".mct/" not in l], [])

    def test_no_duplicate_commit_on_rerun(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(tmp, "- [ ] note one #docs\n")
            mct_run(root, "--yes", "--agent-cmd", AGENT_CMD, "--max-iterations", "5")
            first = subprocess.run(["git", "-C", str(root), "rev-list", "--count", "HEAD"], capture_output=True, text=True).stdout.strip()
            second = mct_run(root, "--yes", "--agent-cmd", AGENT_CMD, "--max-iterations", "5")
            out = json.loads(second.stdout)
            after = subprocess.run(["git", "-C", str(root), "rev-list", "--count", "HEAD"], capture_output=True, text=True).stdout.strip()
            self.assertEqual(out["done"], 0, "an already-done task must not be re-run")
            self.assertEqual(first, after, "no new commits on re-run of a drained queue")


if __name__ == "__main__":
    unittest.main()
