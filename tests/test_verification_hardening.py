"""AC2: verification can no longer be satisfied by fabricated strings.

These assert the *fixed* behavior — the fakeability holes are closed — and that
legitimate evidence is still accepted (no over-blocking).
"""
import base64
import tempfile
import unittest
from pathlib import Path

from mctmod import mct

# A real, minimal 1x1 PNG.
PNG_BYTES = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
)


class TestCheckTokenParsing(unittest.TestCase):
    def test_bare_token_canonicalizes(self):
        self.assertEqual(mct.parse_check_token("typecheck"), ("typecheck", ""))
        self.assertEqual(mct.parse_check_token("tsc"), ("typecheck", ""))

    def test_name_equals_detail(self):
        name, detail = mct.parse_check_token("negative-path-check=invalid token returns 401")
        self.assertEqual(name, "negative-path-check")
        self.assertEqual(detail, "invalid token returns 401")

    def test_unrelated_keyword_does_not_canonicalize_to_required(self):
        # "auth" must NOT resolve to negative-path-check (the old substring bug).
        self.assertEqual(mct.canonical_check_name("auth"), "auth")

    def test_skip_requires_name_and_reason(self):
        self.assertEqual(mct.parse_skip_token("browser skip"), ("browser skip", ""))
        self.assertEqual(
            mct.parse_skip_token("browser-proof=no browser in CI"),
            ("browser-proof", "no browser in CI"),
        )


class TestRequirementSatisfied(unittest.TestCase):
    def test_executed_pass_satisfies(self):
        self.assertTrue(
            mct.requirement_satisfied("typecheck", [], [], [{"name": "typecheck", "result": "pass"}], False)
        )

    def test_executed_fail_does_not_satisfy(self):
        self.assertFalse(
            mct.requirement_satisfied("typecheck", [], [], [{"name": "typecheck", "result": "fail"}], False)
        )

    def test_named_skip_with_reason_satisfies(self):
        self.assertTrue(
            mct.requirement_satisfied("negative-path-check", [], [("negative-path-check", "tested")], [], False)
        )

    def test_auto_executable_not_satisfied_by_self_report(self):
        # A bare claim of "typecheck" must NOT satisfy — it must be executed.
        self.assertFalse(
            mct.requirement_satisfied("typecheck", [("typecheck", "I ran it")], [], [], False)
        )

    def test_browser_proof_requires_artifact_not_string(self):
        self.assertFalse(mct.requirement_satisfied("browser-proof", [("browser-proof", "looked")], [], [], False))
        self.assertTrue(mct.requirement_satisfied("browser-proof", [], [], [], True))

    def test_unrelated_keyword_does_not_satisfy_negative_path(self):
        self.assertFalse(mct.requirement_satisfied("negative-path-check", [("auth", "")], [], [], False))

    def test_named_attestation_with_detail_satisfies_negative_path(self):
        self.assertTrue(
            mct.requirement_satisfied("negative-path-check", [("negative-path-check", "401 on bad token")], [], [], False)
        )

    def test_named_attestation_without_detail_is_insufficient(self):
        self.assertFalse(mct.requirement_satisfied("negative-path-check", [("negative-path-check", "")], [], [], False))


class TestImageValidation(unittest.TestCase):
    def test_real_png_is_valid_image(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "shot.png"
            p.write_bytes(PNG_BYTES)
            self.assertTrue(mct.is_valid_image(p))

    def test_text_file_is_not_image(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "fake.png"
            p.write_text("not an image")
            self.assertFalse(mct.is_valid_image(p))


class TestBrowserArtifactOk(unittest.TestCase):
    def _evidence(self, root, rel):
        return mct.parse_browser_evidence(
            [f"tool=playwright | url=http://localhost:3000 | viewport=1440x900 | screenshot={rel} | result=pass"]
        )

    def test_real_screenshot_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "shot.png").write_bytes(PNG_BYTES)
            ok, _ = mct.browser_artifact_ok(root, self._evidence(root, "shot.png"))
            self.assertTrue(ok)

    def test_missing_screenshot_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ok, reason = mct.browser_artifact_ok(root, self._evidence(root, "shot.png"))
            self.assertFalse(ok)
            self.assertIn("missing", reason)

    def test_empty_screenshot_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "shot.png").write_bytes(b"")
            ok, reason = mct.browser_artifact_ok(root, self._evidence(root, "shot.png"))
            self.assertFalse(ok)
            self.assertIn("empty", reason)

    def test_non_image_screenshot_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "shot.png").write_text("totally not an image")
            ok, reason = mct.browser_artifact_ok(root, self._evidence(root, "shot.png"))
            self.assertFalse(ok)
            self.assertIn("not a valid image", reason)

    def test_string_only_evidence_has_no_artifact(self):
        evidence = mct.parse_browser_evidence(
            ["tool=playwright | url=http://localhost:3000/pricing | viewport=1440x900 | result=pass"]
        )
        with tempfile.TemporaryDirectory() as tmp:
            ok, reason = mct.browser_artifact_ok(Path(tmp), evidence)
        self.assertFalse(ok)
        self.assertIn("no real artifact", reason)


class TestUnmetRequiredChecks(unittest.TestCase):
    def _ui_task(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "TODO.md").write_text("- [ ] polish the hero #ui\n")
            _, tasks = mct.parse_todo(root, mct.DEFAULT_POLICY)
            return tasks[0], root

    def test_ui_task_unmet_without_artifact(self):
        task, root = self._ui_task()
        self.assertIn("browser-proof", mct.unmet_required_checks(task, root, ["playwright"], [], [], False))

    def test_ui_task_met_with_artifact(self):
        task, root = self._ui_task()
        self.assertEqual(mct.unmet_required_checks(task, root, ["playwright"], [], [], True), [])


if __name__ == "__main__":
    unittest.main()
