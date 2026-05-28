"""AC2: verification can no longer be satisfied by fabricated strings.

These assert the *fixed* behavior — the fakeability holes are closed — and that
legitimate evidence is still accepted (no over-blocking).
"""
import base64
import json
import struct
import tempfile
import unittest
import zlib
from pathlib import Path

from mctmod import mct

# A real, minimal 1x1 PNG — a valid image, but NOT a substantive screenshot.
PNG_BYTES = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
)


def make_png(path: Path, width: int, height: int) -> None:
    """Write a valid solid-gray RGB PNG of the given dimensions (stdlib only)."""
    def chunk(typ: bytes, data: bytes) -> bytes:
        body = typ + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)  # 8-bit RGB
    raw = b"".join(b"\x00" + b"\x7f\x7f\x7f" * width for _ in range(height))  # filter byte + pixels
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b"")
    path.write_bytes(png)


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
            mct.requirement_satisfied("negative-path-check", [], [("negative-path-check", "tested manually on staging")], [], False)
        )

    def test_single_char_attestation_is_rejected(self):
        # The audit's `--check negative-path-check=x` bypass must now fail.
        self.assertFalse(mct.requirement_satisfied("negative-path-check", [("negative-path-check", "x")], [], [], False))
        self.assertFalse(mct.requirement_satisfied("negative-path-check", [("negative-path-check", "ok")], [], [], False))

    def test_trivial_skip_reason_is_rejected(self):
        self.assertFalse(mct.requirement_satisfied("negative-path-check", [], [("negative-path-check", "lazy")], [], False))

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

    def test_image_dimensions_parsed_for_png(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "big.png"
            make_png(p, 320, 240)
            self.assertEqual(mct.image_dimensions(p), (320, 240))

    def test_substantive_rejects_tiny_accepts_real(self):
        with tempfile.TemporaryDirectory() as tmp:
            tiny = Path(tmp) / "tiny.png"
            tiny.write_bytes(PNG_BYTES)
            real = Path(tmp) / "real.png"
            make_png(real, 128, 128)
            self.assertFalse(mct.screenshot_is_substantive(tiny)[0])
            self.assertTrue(mct.screenshot_is_substantive(real)[0])


class TestBrowserArtifactOk(unittest.TestCase):
    def _evidence(self, root, rel):
        return mct.parse_browser_evidence(
            [f"tool=playwright | url=http://localhost:3000 | viewport=1440x900 | screenshot={rel} | result=pass"]
        )

    def test_real_screenshot_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_png(root / "shot.png", 200, 200)  # viewport-scale, substantive
            ok, reason = mct.browser_artifact_ok(root, self._evidence(root, "shot.png"))
            self.assertTrue(ok, reason)

    def test_tiny_1x1_screenshot_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "shot.png").write_bytes(PNG_BYTES)  # valid PNG but 1x1
            ok, reason = mct.browser_artifact_ok(root, self._evidence(root, "shot.png"))
            self.assertFalse(ok)
            self.assertIn("too small", reason)

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

    def test_forged_png_without_pixel_data_is_rejected(self):
        # 33-byte PNG: real signature + a fake 1920x1080 IHDR, but NO IDAT.
        sig = b"\x89PNG\r\n\x1a\n"
        ihdr = struct.pack(">I", 13) + b"IHDR" + struct.pack(">IIBBBBB", 1920, 1080, 8, 2, 0, 0, 0) + struct.pack(">I", 0)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "shot.png").write_bytes(sig + ihdr)
            ok, reason = mct.browser_artifact_ok(root, self._evidence(root, "shot.png"))
            self.assertFalse(ok)
            self.assertIn("IDAT", reason)

    def test_junk_jpeg_without_end_marker_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "shot.jpg").write_bytes(b"\xff\xd8\xff" + b"\x00" * 4000)  # SOI but no EOI
            ev = mct.parse_browser_evidence(
                [f"tool=playwright | url=http://x | viewport=1440x900 | screenshot=shot.jpg | result=pass"]
            )
            ok, reason = mct.browser_artifact_ok(root, ev)
            self.assertFalse(ok)

    def test_one_byte_proof_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "p.txt").write_text("x")
            ev = mct.parse_browser_evidence(["tool=playwright | url=http://x | flow=login | proof=p.txt | result=pass"])
            ok, reason = mct.browser_artifact_ok(root, ev)
            self.assertFalse(ok)
            self.assertIn("too small", reason)

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


class TestGateOnChangedFiles(unittest.TestCase):
    def _plain_task(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "TODO.md").write_text("- [ ] tidy the helper module\n")  # no files:, generic text
            _, tasks = mct.parse_todo(root, mct.DEFAULT_POLICY)
            return tasks[0], root

    def test_unannotated_tsx_change_requires_browser_proof(self):
        task, root = self._plain_task()
        required = mct.task_required_checks(task, root, ["src/Hero.tsx"])
        self.assertIn("browser-proof", required)

    def test_unannotated_ts_change_requires_typecheck_when_script_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "package.json").write_text(json.dumps({"scripts": {"typecheck": "tsc"}}))
            (root / "TODO.md").write_text("- [ ] tidy the helper module\n")
            _, tasks = mct.parse_todo(root, mct.DEFAULT_POLICY)
            required = mct.task_required_checks(tasks[0], root, ["src/util.ts"])
            self.assertIn("typecheck", required)

    def test_no_change_no_extra_requirements(self):
        task, root = self._plain_task()
        self.assertEqual(mct.task_required_checks(task, root, ["README.md"]), [])


if __name__ == "__main__":
    unittest.main()
