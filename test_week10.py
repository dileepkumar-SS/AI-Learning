import json
import unittest

import multi_agent_race as race


class Week10RaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = race.load_cases()
        cls.single = [race.run_single(case) for case in cls.cases]
        cls.squad = [race.run_squad(case) for case in cls.cases]

    def test_uses_exact_ten_week6_case_ids(self):
        self.assertEqual([case.case_id for case in self.cases], [f"tr_{number:04d}" for number in range(1, 11)])
        payload = json.loads((race.ROOT / "week6_race_cases.json").read_text(encoding="utf-8"))
        self.assertIn("Verbatim", payload["provenance"])

    def test_same_judge_and_output_contract_for_both_arms(self):
        for case, single, squad in zip(self.cases, self.single, self.squad):
            self.assertTrue(race.shared_judge(case, single.answer))
            self.assertTrue(race.shared_judge(case, squad.answer))
            self.assertEqual(type(single.answer), type(squad.answer))

    def test_all_required_metrics_exist_for_both_arms(self):
        keys = {"pass_rate", "p50_latency_ms", "p99_latency_ms", "total_tokens", "cost_per_question"}
        for results in (self.single, self.squad):
            values = race.summarize(self.cases, results)
            self.assertEqual(set(values), keys)
            self.assertGreaterEqual(values["p99_latency_ms"], values["p50_latency_ms"])

    def test_multiplier_and_handoffs_are_accounted(self):
        single = race.summarize(self.cases, self.single)
        squad = race.summarize(self.cases, self.squad)
        multiplier = squad["total_tokens"] / single["total_tokens"]
        self.assertEqual(round(multiplier, 1), 4.5)
        self.assertTrue(all(len(result.handoffs) == 4 for result in self.squad))
        self.assertTrue(all(item.tokens > 0 for result in self.squad for item in result.handoffs))

    def test_injected_500_retries_then_degrades_without_code(self):
        result = race.run_squad(self.cases[2], inject_version_500=True)
        retries = [item for item in result.handoffs if "retry" in item.purpose]
        self.assertEqual(len(retries), 1)
        self.assertIn("could not verify", result.answer)
        self.assertIn("no code sample", result.answer)
        self.assertFalse(race.shared_judge(self.cases[2], result.answer))

    def test_verdict_is_at_most_ten_lines_and_names_bias(self):
        lines = (race.ROOT / "verdict.md").read_text(encoding="utf-8").splitlines()
        self.assertLessEqual(len(lines), 10)
        self.assertIn("sunk-cost bias", " ".join(lines).lower())


if __name__ == "__main__":
    unittest.main()
