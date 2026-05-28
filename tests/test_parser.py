"""TODO.md parsing and task-metadata extraction."""
import tempfile
import unittest
from pathlib import Path

from mctmod import mct


def parse(text):
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "TODO.md").write_text(text)
        path, tasks = mct.parse_todo(root, mct.DEFAULT_POLICY)
        return path, tasks


class TestParseTodo(unittest.TestCase):
    def test_missing_todo_returns_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            path, tasks = mct.parse_todo(Path(tmp), mct.DEFAULT_POLICY)
        self.assertIsNone(path)
        self.assertEqual(tasks, [])

    def test_open_and_done_checkboxes(self):
        _, tasks = parse("- [ ] First task\n- [x] Second task\n- [X] Third task\n")
        self.assertEqual(len(tasks), 3)
        self.assertFalse(tasks[0].done)
        self.assertTrue(tasks[1].done)
        self.assertTrue(tasks[2].done)

    def test_star_bullets_are_parsed(self):
        _, tasks = parse("* [ ] Star bullet task\n")
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].clean_text, "Star bullet task")

    def test_tags_files_and_deps_extracted(self):
        _, tasks = parse("- [ ] Build login #ui #auth files:src/a.tsx,src/b.ts depends:setup-db\n")
        task = tasks[0]
        self.assertIn("ui", task.tags)
        self.assertIn("auth", task.tags)
        self.assertEqual(task.files, ["src/a.tsx", "src/b.ts"])
        self.assertEqual(task.deps, ["setup-db"])

    def test_clean_text_strips_tags_and_meta(self):
        _, tasks = parse("- [ ] Ship feature #ui files:src/a.tsx depends:foo\n")
        self.assertEqual(tasks[0].clean_text, "Ship feature")

    def test_line_numbers_are_one_based(self):
        _, tasks = parse("intro\n\n- [ ] Real task\n")
        self.assertEqual(tasks[0].line, 3)

    def test_task_id_is_deterministic(self):
        self.assertEqual(mct.task_id("Same text"), mct.task_id("Same text"))
        self.assertNotEqual(mct.task_id("Text A"), mct.task_id("Text B"))

    def test_slug_is_kebab_and_bounded(self):
        slug = mct.slugify("Add OAuth2 + PKCE Login Flow!!!")
        self.assertRegex(slug, r"^[a-z0-9-]+$")
        self.assertLessEqual(len(slug), 48)

    def test_blocked_tag_marks_blocked(self):
        _, tasks = parse("- [ ] Waiting task #blocked\n")
        self.assertTrue(tasks[0].blocked)

    def test_indented_subtasks_are_parsed(self):
        _, tasks = parse("- [ ] Parent\n  - [ ] Child task\n")
        self.assertEqual(len(tasks), 2)

    def test_non_checkbox_lines_ignored(self):
        _, tasks = parse("# Heading\nSome prose\n- bullet without checkbox\n- [ ] Only real task\n")
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].clean_text, "Only real task")

    def test_malformed_checkboxes_are_dropped(self):
        # `- []` and `-[ ]` are malformed and must not become tasks.
        _, tasks = parse("- [] missing space\n-[ ] no space after dash\n- [ ] valid one\n")
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].clean_text, "valid one")

    def test_tag_only_task_is_not_created(self):
        # A checkbox whose text is only tags/metadata has no real task text.
        _, tasks = parse("- [ ] #ui\n- [ ] real work here\n")
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].clean_text, "real work here")


class TestParseMeta(unittest.TestCase):
    def test_comma_and_space_separated(self):
        self.assertEqual(mct.parse_meta("files:a.ts, b.ts c.ts", "files"), ["a.ts", "b.ts", "c.ts"])

    def test_absent_key_returns_empty(self):
        self.assertEqual(mct.parse_meta("no metadata here", "depends"), [])


class TestInferRisk(unittest.TestCase):
    def test_security_words_are_high_risk(self):
        self.assertEqual(mct.infer_risk("update auth flow", [], [], False), "high")

    def test_blocked_is_high_risk(self):
        self.assertEqual(mct.infer_risk("simple copy tweak", [], [], True), "high")

    def test_code_files_are_medium_risk(self):
        self.assertEqual(mct.infer_risk("edit component", ["a.tsx"], [], False), "medium")

    def test_plain_copy_is_low_risk(self):
        self.assertEqual(mct.infer_risk("fix typo in readme", ["README.md"], [], False), "low")


if __name__ == "__main__":
    unittest.main()
