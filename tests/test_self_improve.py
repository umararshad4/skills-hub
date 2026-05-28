"""Self-improvement pipeline: redaction safety + off-by-default egress gates."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from mctmod import mct

REPO = Path(__file__).resolve().parents[1]
MCT = REPO / "claude" / "bin" / "mct"

# Secret-like fixtures assembled at runtime so this source file contains no
# literal secret pattern (which would trip the repo's own secret scanner).
FAKE_SK = "sk-" + "A" * 24
FAKE_AWS = "AKIA" + "IOSFODNN7" + "EXAMPLE"
FAKE_GH = "ghp_" + "0" * 26
FAKE_PW = "password = " + chr(34) + "hunter2hunter2" + chr(34)


class TestRedaction(unittest.TestCase):
    def test_scrub_removes_secrets(self):
        out = mct.scrub_text(f"here is {FAKE_SK} and more")
        self.assertNotIn(FAKE_SK, out)
        self.assertIn("<redacted-secret>", out)

    def test_scrub_removes_home_path(self):
        out = mct.scrub_text(f"failed reading {Path.home()}/projects/app/.env")
        self.assertNotIn(str(Path.home()), out)

    def test_detect_secret_is_broadened(self):
        self.assertTrue(mct.detect_secret(FAKE_AWS))
        self.assertTrue(mct.detect_secret(FAKE_GH))
        self.assertTrue(mct.detect_secret(FAKE_PW))
        self.assertFalse(mct.detect_secret("just a normal sentence"))

    def test_url_inline_credentials_redacted(self):
        url = "postgres://app:" + "Pr0dDbPass1" + "@10.0.0.5:5432/main"
        out = mct.scrub_text(f"DB connect failed for {url}")
        self.assertNotIn("Pr0dDbPass1", out)
        self.assertTrue(mct.detect_secret(url))
        self.assertFalse(mct.detect_secret(out))

    def test_pem_private_key_body_redacted(self):
        begin = "-----BEGIN " + "PRIVATE KEY-----"
        end = "-----END " + "PRIVATE KEY-----"
        body = "MIIB" + "A" * 48
        pem = f"{begin}\n{body}\n{end}"
        out = mct.scrub_text(f"failed to load key:\n{pem}")
        self.assertNotIn(body, out, "PEM key body must be redacted, not just the header")
        self.assertFalse(mct.detect_secret(out))

    def test_cloud_keys_detected(self):
        google = "AIza" + "B" * 35
        stripe = "sk_live_" + "0123456789abcdef0123"
        self.assertTrue(mct.detect_secret(google))
        self.assertTrue(mct.detect_secret(stripe))
        self.assertNotIn(google, mct.scrub_text(google))


class TestReport(unittest.TestCase):
    def test_report_is_allowlisted_and_redacted(self):
        try:
            raise ValueError(f"boom with token {FAKE_SK} in {Path.home()}/x")
        except ValueError as exc:
            import traceback as tb
            report = mct.build_crash_report(exc, tb.format_exc())
        allowed = {"signature", "mctVersion", "python", "os", "errorType", "message", "argv", "traceback", "at"}
        self.assertEqual(set(report) - allowed, set(), "report must contain only allowlisted keys")
        self.assertNotIn(FAKE_SK, json.dumps(report))
        self.assertNotIn(str(Path.home()), json.dumps(report))

    def test_signature_is_deterministic(self):
        self.assertEqual(mct.error_signature("ValueError", "x"), mct.error_signature("ValueError", "x"))
        self.assertNotEqual(mct.error_signature("ValueError", "a"), mct.error_signature("TypeError", "a"))


class TestDefaults(unittest.TestCase):
    def test_self_improve_is_off_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            config = mct.default_config(Path(tmp))
        self.assertFalse(config["selfImprove"]["enabled"])


def _repo_with_crash(tmp):
    root = Path(tmp)
    subprocess.run(["git", "-C", str(root), "init", "-q"], check=True)
    crashes = root / ".mct" / "crashes"
    crashes.mkdir(parents=True)
    (crashes / "abc123.json").write_text(json.dumps({
        "signature": "abc123", "mctVersion": "3.0.0", "errorType": "ValueError",
        "message": "boom", "argv": [], "traceback": "...", "at": "2026-01-01T00:00:00+00:00",
    }))
    return root


def _run(root, *args, mct_home=None):
    env = {**os.environ}
    if mct_home is not None:
        env["MCT_HOME"] = str(mct_home)
    return subprocess.run([sys.executable, str(MCT), "report-issue", *args], cwd=str(root), capture_output=True, text=True, env=env)


class TestInRepoConfigCannotEnableEgress(unittest.TestCase):
    def test_committed_config_does_not_grant_consent_or_redirect(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as home:
            root = _repo_with_crash(tmp)
            # A hostile committed config tries to self-enable egress + redirect upstream.
            (root / ".mct" / "config.json").write_text(json.dumps(
                {"selfImprove": {"enabled": True, "upstreamRepo": "attacker/evil"}}))
            status = json.loads(_run(root, "--status", mct_home=home).stdout)
            self.assertFalse(status["enabled"], "in-repo config must NOT grant egress consent")
            self.assertEqual(status["upstreamRepo"], "umararshad4/skills-hub", "upstream repo is pinned, not from config")
            # And an actual send attempt is refused (consent lives out-of-tree).
            result = _run(root, "--last", "--open-issue", "--yes", mct_home=home)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("OFF", result.stdout + result.stderr)


class TestEgressGates(unittest.TestCase):
    def test_open_issue_refused_when_disabled(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _repo_with_crash(tmp)
            result = _run(root, "--last", "--open-issue", "--yes")
            self.assertNotEqual(result.returncode, 0, "must refuse to send when reporting is OFF")
            self.assertIn("OFF", result.stdout + result.stderr)

    def test_print_does_not_egress(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _repo_with_crash(tmp)
            result = _run(root, "--last", "--print")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["signature"], "abc123")

    def test_status_runs_offline(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _repo_with_crash(tmp)
            result = _run(root, "--status")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(json.loads(result.stdout)["enabled"])

    def test_enable_requires_confirm(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _repo_with_crash(tmp)
            result = _run(root, "--enable")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("confirm", (result.stdout + result.stderr).lower())


if __name__ == "__main__":
    unittest.main()
