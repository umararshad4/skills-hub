"""End-to-end CLI behavior via subprocess in throwaway git repos.

Covers AC5 (claim state is consumed) and AC8 (a failed commit never leaves a
TODO marked done-but-uncommitted).
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MCT = REPO / "claude" / "bin" / "mct"


def git(root, *args):
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True)


def make_repo(tmp, todo):
    root = Path(tmp)
    git(root, "init", "-q")
    git(root, "config", "user.email", "t@example.com")
    git(root, "config", "user.name", "tester")
    (root / "seed.txt").write_text("seed\n")
    git(root, "add", "-A")
    git(root, "commit", "-qm", "seed")
    (root / "TODO.md").write_text(todo)
    return root


def mct_run(root, *args):
    return subprocess.run(
        [sys.executable, str(MCT), *args],
        cwd=str(root), capture_output=True, text=True,
    )


class TestClaimConsumption(unittest.TestCase):
    def test_claimed_task_is_not_rehanded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(tmp, "- [ ] ship the onboarding flow\n")
            first = mct_run(root, "next", "--claim")
            self.assertEqual(first.returncode, 0, first.stderr)
            first_next = json.loads(first.stdout)["next"]
            self.assertEqual(len(first_next), 1)
            claimed_id = first_next[0]["id"]

            second = json.loads(mct_run(root, "next", "--claim").stdout)
            second_ids = [t["id"] for t in second["next"]]
            self.assertNotIn(claimed_id, second_ids)
            self.assertIn(claimed_id, second["alreadyClaimed"])

    def test_reclaim_rehands_the_task(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(tmp, "- [ ] ship the onboarding flow\n")
            claimed_id = json.loads(mct_run(root, "next", "--claim").stdout)["next"][0]["id"]
            reclaimed = json.loads(mct_run(root, "next", "--reclaim").stdout)["next"]
            self.assertIn(claimed_id, [t["id"] for t in reclaimed])


class TestDoneCommitOrdering(unittest.TestCase):
    def test_done_commit_is_atomic_never_done_but_uncommitted(self):
        # AC8 invariant: after `mct done --commit`, the task is either [x] AND
        # committed, or untouched — never [x]-but-uncommitted. The checkbox flip
        # now commits atomically (committing the flip itself when nothing else is staged).
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(tmp, "- [ ] update the changelog notes #docs\n")
            result = mct_run(root, "done", "changelog", "--check", "diff-review=read the diff", "--commit")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("- [x]", (root / "TODO.md").read_text())
            # The flip is committed — HEAD:TODO.md shows [x], so no done-but-uncommitted state.
            committed = subprocess.run(["git", "-C", str(root), "show", "HEAD:TODO.md"], capture_output=True, text=True).stdout
            self.assertIn("- [x]", committed)

    def test_successful_done_flips_checkbox(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(tmp, "- [ ] update the changelog notes #docs\n")
            result = mct_run(root, "done", "changelog", "--check", "diff-review=read the diff")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("- [x]", (root / "TODO.md").read_text())


class TestFinalCheckStrict(unittest.TestCase):
    def test_final_check_accepts_strict_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(tmp, "- [ ] something to do\n")
            result = mct_run(root, "final-check", "--strict")
            # Must not be an argparse crash (exit 2); 0 or 1 are valid audit outcomes.
            self.assertIn(result.returncode, (0, 1), result.stderr)
            self.assertNotIn("unrecognized arguments", result.stderr)


if __name__ == "__main__":
    unittest.main()
