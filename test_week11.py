import json
import re
import unittest

import production_drill as drill


class Week11ProductionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        drill.plant_logs()
        cls.found, cls.elapsed, cls.slice_used = drill.find_incident_from_vague_complaint()

    def test_vague_search_finds_one_deprecated_output(self):
        self.assertEqual(self.found["trace_id"], "prod_0037")
        self.assertIn("generated-output", self.slice_used)
        self.assertNotIn("prod_0037", self.slice_used)

    def test_trace_has_required_observability_fields(self):
        self.assertIn("prompt_version", self.found)
        self.assertTrue(self.found["retrieved_context_ids"])
        self.assertEqual({item["name"] for item in self.found["spans"]}, {"retrieval", "generation", "tools"})
        for item in self.found["spans"]:
            self.assertGreater(item["latency_ms"], 0)
            self.assertGreater(item["tokens"]["total"], 0)
            self.assertGreater(item["cost_usd"], 0)

    def test_span_costs_and_tokens_equal_trace_totals(self):
        self.assertAlmostEqual(sum(item["cost_usd"] for item in self.found["spans"]), self.found["total_cost_usd"])
        self.assertEqual(sum(item["tokens"]["total"] for item in self.found["spans"]), self.found["total_tokens"])

    def test_incident_case_is_red_before_and_green_after(self):
        red, red_total, _ = drill.run_suite(fixed=False)
        green, green_total, _ = drill.run_suite(fixed=True)
        self.assertEqual((red, red_total), (10, 11))
        self.assertEqual((green, green_total), (11, 11))

    def test_fix_changes_retrieval_and_prompt_version(self):
        case = drill.incident_case()
        _, before_context, before_prompt = drill.answer_case(case, fixed=False)
        _, after_context, after_prompt = drill.answer_case(case, fixed=True)
        self.assertIn("v2:client-send-legacy:example", before_context)
        self.assertNotIn("v2:client-send-legacy:example", after_context)
        self.assertEqual(before_prompt, "docs-rag-v10.0")
        self.assertEqual(after_prompt, "docs-rag-v11.0")

    def test_artifact_constraints(self):
        drill_text = (drill.ROOT / "drill.md").read_text(encoding="utf-8")
        self.assertRegex(drill_text, r"Time-to-find: \*\*\d{2}:\d{2}\*\*")
        tenx_lines = (drill.ROOT / "tenx.md").read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(tenx_lines), 1)
        self.assertIn("750", tenx_lines[0])
        plan = (drill.ROOT / "deployment_plan.md").read_text(encoding="utf-8")
        self.assertEqual(sum(line.startswith(("Canary:", "Rollback:")) for line in plan.splitlines()), 2)


if __name__ == "__main__":
    unittest.main()
