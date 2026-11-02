import unittest

import trajectory_eval as trajectory


class TrajectoryEvalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.before = [trajectory.generate_run(case, mitigated=False) for case in trajectory.CASES]
        cls.after = [trajectory.generate_run(case, mitigated=True) for case in trajectory.CASES]

    def test_all_ten_cases_have_expected_paths(self):
        self.assertEqual(len(trajectory.CASES), 10)
        self.assertEqual(set(trajectory.EXPECTED_SEQUENCES), {case.case_id for case in trajectory.CASES})
        self.assertEqual(trajectory.ALTERNATE_PATH_CASES, {"q05", "q06", "q07"})
        for case_id in trajectory.ALTERNATE_PATH_CASES:
            self.assertEqual(len(trajectory.EXPECTED_SEQUENCES[case_id]), 2)

    def test_gap_exposes_right_answer_wrong_path(self):
        before = trajectory.metrics(self.before)
        self.assertEqual(before["outcome_pass_rate_pct"], 100.0)
        self.assertEqual(before["trajectory_pass_rate_pct"], 40.0)
        self.assertEqual(before["gap_points"], 60.0)
        q01 = self.before[0]
        self.assertTrue(trajectory.outcome_passes(q01))
        self.assertFalse(trajectory.trajectory_passes(q01))
        self.assertEqual(q01.sequence, ("search_docs",))

    def test_exactly_one_mitigation_changes_only_top_mode_cases(self):
        changed = {
            before.case_id
            for before, after in zip(self.before, self.after)
            if before.sequence != after.sequence
        }
        self.assertEqual(changed, {"q01", "q09", "q10"})
        self.assertEqual(trajectory.mode_counts(self.before)["missing_required_tool"], 3)
        self.assertEqual(trajectory.mode_counts(self.after)["missing_required_tool"], 0)

    def test_no_failure_mode_regresses(self):
        before = trajectory.mode_counts(self.before)
        after = trajectory.mode_counts(self.after)
        self.assertTrue(all(after[mode] <= before[mode] for mode in trajectory.FAILURE_MODES))

    def test_metrics_include_cost_p50_and_max(self):
        values = trajectory.metrics(self.before)
        self.assertIn("cost_p50_usd", values)
        self.assertIn("cost_max_usd", values)
        self.assertGreaterEqual(values["cost_max_usd"], values["cost_p50_usd"])


if __name__ == "__main__":
    unittest.main()
