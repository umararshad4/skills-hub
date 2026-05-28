"""State and config load/save behavior, including corruption fallback."""
import json
import tempfile
import unittest
from pathlib import Path

from mctmod import mct


class TestState(unittest.TestCase):
    def test_default_state_shape(self):
        state = mct.default_state()
        self.assertEqual(state["tasks"], {})
        self.assertEqual(state["runs"], [])
        self.assertEqual(state["checkHistory"], [])

    def test_load_state_missing_returns_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = mct.load_state(Path(tmp))
        self.assertEqual(state["tasks"], {})

    def test_corrupt_state_falls_back_to_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".mct").mkdir()
            mct.state_path(root).write_text("{ this is not valid json ")
            state = mct.load_state(root)
        self.assertEqual(state["tasks"], {})
        self.assertIn("runs", state)

    def test_save_then_load_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            payload = mct.default_state()
            payload["tasks"]["abc"] = {"status": "done"}
            mct.save_state(root, payload)
            reloaded = mct.load_state(root)
        self.assertEqual(reloaded["tasks"]["abc"]["status"], "done")

    def test_non_dict_state_falls_back_to_default(self):
        # state.json = "null" / a list must not crash later commands.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".mct").mkdir()
            for junk in ("null", "[1, 2, 3]", '"a string"'):
                mct.state_path(root).write_text(junk)
                state = mct.load_state(root)
                self.assertIsInstance(state, dict)
                self.assertIn("tasks", state)

    def test_load_state_backfills_missing_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".mct").mkdir()
            mct.state_path(root).write_text(json.dumps({"tasks": {"x": {}}}))
            state = mct.load_state(root)
        self.assertIn("runs", state)
        self.assertIn("checkHistory", state)


class TestAtomicSave(unittest.TestCase):
    def test_serialization_error_does_not_corrupt_existing_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            good = mct.default_state()
            good["tasks"]["keep"] = {"status": "done"}
            mct.save_state(root, good)
            # A non-serializable value must raise WITHOUT truncating the live file.
            with self.assertRaises(TypeError):
                mct.save_state(root, {"tasks": {1, 2, 3}})
            reloaded = mct.load_state(root)
            self.assertEqual(reloaded["tasks"]["keep"]["status"], "done")

    def test_no_temp_file_left_behind(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mct.save_state(root, mct.default_state())
            leftovers = list((root / ".mct").glob("state.json.tmp*"))
            self.assertEqual(leftovers, [])


class TestConfig(unittest.TestCase):
    def test_default_config_has_verification_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            config = mct.default_config(Path(tmp))
        self.assertIn("verification", config)
        self.assertIn("autonomy", config)

    def test_corrupt_config_falls_back_to_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".mct").mkdir()
            mct.config_path(root).write_text("not json")
            config = mct.load_config(root)
        self.assertIn("verification", config)

    def test_non_dict_config_falls_back_to_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".mct").mkdir()
            mct.config_path(root).write_text("[1, 2, 3]")
            config = mct.load_config(root)
            self.assertIsInstance(config, dict)
            self.assertIn("verification", config)

    def test_load_config_merges_defaults(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".mct").mkdir()
            mct.config_path(root).write_text(json.dumps({"custom": True}))
            config = mct.load_config(root)
        self.assertTrue(config["custom"])
        self.assertIn("verification", config)


class TestPolicy(unittest.TestCase):
    def test_default_policy_has_todo_queue(self):
        self.assertIn("todoQueue", mct.DEFAULT_POLICY)
        self.assertEqual(mct.DEFAULT_POLICY["todoQueue"]["fileName"], "TODO.md")


if __name__ == "__main__":
    unittest.main()
