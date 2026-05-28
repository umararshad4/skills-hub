"""Stable verification helpers: task classification and evidence parsing.

These cover behavior that should remain constant. The *fakeability* fixes
(check_satisfies hardening, real browser artifacts) are asserted in
test_verification_hardening.py once AC2 lands.
"""
import tempfile
import unittest
from pathlib import Path

from mctmod import mct


def one_task(text):
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "TODO.md").write_text(f"- [ ] {text}\n")
        _, tasks = mct.parse_todo(root, mct.DEFAULT_POLICY)
        return tasks[0]


class TestTaskClassification(unittest.TestCase):
    def test_ui_tag_is_ui_task(self):
        self.assertTrue(mct.is_ui_task(one_task("redo the hero #ui")))

    def test_tsx_file_is_ui_task(self):
        self.assertTrue(mct.is_ui_task(one_task("edit component files:src/Hero.tsx")))

    def test_plain_backend_task_is_not_ui(self):
        self.assertFalse(mct.is_ui_task(one_task("optimize the cron job files:src/cron.py")))

    def test_react_task_detection(self):
        self.assertTrue(mct.is_react_task(one_task("fix react state #react")))

    def test_security_task_detection(self):
        self.assertTrue(mct.is_security_task(one_task("rotate auth secrets")))

    def test_api_task_detection(self):
        self.assertTrue(mct.is_api_task(one_task("add pricing endpoint")))


class TestRequiredChecks(unittest.TestCase):
    def test_ui_task_requires_browser_proof(self):
        with tempfile.TemporaryDirectory() as tmp:
            required = mct.task_required_checks(one_task("polish the banner #ui"), Path(tmp))
        self.assertIn("browser-proof", required)

    def test_security_task_requires_negative_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            required = mct.task_required_checks(one_task("harden the login auth"), Path(tmp))
        self.assertIn("negative-path-check", required)

    def test_plain_task_has_no_required_checks(self):
        with tempfile.TemporaryDirectory() as tmp:
            required = mct.task_required_checks(one_task("update the changelog #docs"), Path(tmp))
        self.assertEqual(required, [])


class TestBrowserEvidenceParsing(unittest.TestCase):
    def test_pipe_delimited_fields_parsed(self):
        parsed = mct.parse_browser_evidence(
            ["tool=playwright | url=http://localhost:3000 | viewport=1440x900 | result=pass"]
        )
        self.assertEqual(parsed[0]["url"], "http://localhost:3000")
        self.assertEqual(parsed[0]["viewport"], "1440x900")
        self.assertEqual(parsed[0]["result"], "pass")

    def test_browser_check_names_filters_browser_checks(self):
        names = mct.browser_check_names(["playwright-run", "typecheck", "chrome-visual"])
        self.assertIn("playwright-run", names)
        self.assertIn("chrome-visual", names)
        self.assertNotIn("typecheck", names)


if __name__ == "__main__":
    unittest.main()
