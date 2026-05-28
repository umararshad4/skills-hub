"""Dependency analysis, task planning, and file classification."""
import tempfile
import unittest
from pathlib import Path

from mctmod import mct


def parse(text):
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "TODO.md").write_text(text)
        _, tasks = mct.parse_todo(root, mct.DEFAULT_POLICY)
        return tasks


class TestDependencyAnalysis(unittest.TestCase):
    def test_resolvable_deps_build_graph(self):
        tasks = parse("- [ ] alpha\n- [ ] beta depends:alpha\n")
        result = mct.dependency_analysis(tasks)
        beta = next(t for t in tasks if t.slug == "beta")
        alpha = next(t for t in tasks if t.slug == "alpha")
        self.assertIn(alpha.id, result["graph"][beta.id])

    def test_mutual_cycle_is_detected(self):
        tasks = parse("- [ ] alpha depends:beta\n- [ ] beta depends:alpha\n")
        result = mct.dependency_analysis(tasks)
        self.assertTrue(result["cycles"], "expected a cycle to be detected for mutually dependent tasks")

    def test_unresolvable_dep_is_reported_missing(self):
        tasks = parse("- [ ] alpha depends:does-not-exist\n")
        result = mct.dependency_analysis(tasks)
        alpha = tasks[0]
        self.assertIn("does-not-exist", result["missing"].get(alpha.id, []))


class TestTaskPlan(unittest.TestCase):
    def test_single_open_task_is_sequential(self):
        tasks = parse("- [ ] only task\n")
        plan = mct.task_plan(tasks)
        self.assertEqual(plan["mode"], "sequential")
        self.assertEqual(len(plan["next"]), 1)

    def test_independent_low_risk_tasks_are_parallel_candidates(self):
        tasks = parse(
            "- [ ] write docs page one #docs files:docs/one.md\n"
            "- [ ] write docs page two #docs files:docs/two.md\n"
        )
        plan = mct.task_plan(tasks)
        self.assertEqual(plan["mode"], "parallel-candidates")
        self.assertGreaterEqual(len(plan["independent"]), 2)

    def test_overlapping_files_prevent_parallel(self):
        tasks = parse(
            "- [ ] edit shared doc a #docs files:docs/shared.md\n"
            "- [ ] edit shared doc b #docs files:docs/shared.md\n"
        )
        plan = mct.task_plan(tasks)
        self.assertIn("docs/shared.md", plan["overlappingFiles"])
        self.assertEqual(plan["mode"], "sequential")

    def test_high_risk_tasks_are_not_independent(self):
        tasks = parse(
            "- [ ] update auth tokens files:src/auth.ts\n"
            "- [ ] write changelog #docs files:docs/log.md\n"
        )
        plan = mct.task_plan(tasks)
        independent_ids = {t["slug"] for t in plan["independent"]}
        self.assertNotIn("update-auth-tokens", independent_ids)

    def test_blocked_task_is_listed_blocked(self):
        tasks = parse("- [ ] do later #blocked files:src/x.ts\n")
        plan = mct.task_plan(tasks)
        self.assertEqual(len(plan["blocked"]), 1)


class TestClassifyFiles(unittest.TestCase):
    def test_surfaces_are_classified(self):
        surfaces = mct.classify_files(
            ["a.tsx", "b.css", "c.ts", "d.md", "package.json", "x.test.ts", "random.bin"]
        )
        self.assertIn("a.tsx", surfaces["react"])
        self.assertIn("b.css", surfaces["ui"])
        self.assertIn("c.ts", surfaces["typescript"])
        self.assertIn("d.md", surfaces["docs"])
        self.assertIn("package.json", surfaces["config"])
        self.assertIn("x.test.ts", surfaces["tests"])
        self.assertIn("random.bin", surfaces["other"])

    def test_empty_input_yields_no_surfaces(self):
        self.assertEqual(mct.classify_files([]), {})


class TestRecommendChecks(unittest.TestCase):
    def test_react_surface_recommends_react_doctor(self):
        with tempfile.TemporaryDirectory() as tmp:
            checks = mct.recommend_checks(Path(tmp), {"react": ["a.tsx"]})
        self.assertIn("react-doctor-diff", checks)

    def test_diff_review_always_present(self):
        with tempfile.TemporaryDirectory() as tmp:
            checks = mct.recommend_checks(Path(tmp), {})
        self.assertIn("diff-review", checks)


if __name__ == "__main__":
    unittest.main()
