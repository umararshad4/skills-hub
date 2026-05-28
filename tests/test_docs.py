"""AC9: docs honestly state guarantees; versioning is bumped."""
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


class TestDocs(unittest.TestCase):
    def test_readme_has_enforced_vs_advisory_section(self):
        readme = (REPO / "README.md").read_text()
        self.assertIn("What Is Enforced vs Advisory", readme)
        self.assertIn("not a self-driving", readme)

    def test_changelog_exists(self):
        self.assertTrue((REPO / "CHANGELOG.md").exists())

    def test_version_is_bumped(self):
        text = (REPO / "claude" / "bin" / "mct").read_text()
        match = re.search(r'VERSION\s*=\s*"(\d+)\.(\d+)\.(\d+)"', text)
        self.assertIsNotNone(match, "VERSION not found")
        major = int(match.group(1))
        self.assertGreaterEqual(major, 2, "VERSION should be >= 2.0.0")


if __name__ == "__main__":
    unittest.main()
