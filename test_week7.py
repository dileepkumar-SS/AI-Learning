import ast
import inspect
import unittest

import week7


class Week7Tests(unittest.TestCase):
    def test_three_distinct_typed_tools(self):
        self.assertEqual(len(week7.TOOL_SCHEMAS), 3)
        descriptions = [schema["description"] for schema in week7.TOOL_SCHEMAS]
        self.assertEqual(len(set(descriptions)), 3)
        for schema in week7.TOOL_SCHEMAS:
            self.assertEqual(schema["parameters"]["api_version"]["enum"], ["v2", "v3"])

    def test_same_ten_inputs_include_three_dependency_cases(self):
        self.assertEqual(len(week7.CASES), 10)
        self.assertGreaterEqual(sum(case.dependency_case for case in week7.CASES), 3)

    def test_agent_and_workflow_share_output_contract(self):
        case = week7.CASES[4]
        agent = week7.run_agent(case)
        workflow = week7.run_workflow(case)
        self.assertEqual(set(agent.answer), set(workflow.answer))
        self.assertTrue(week7.passes(case, agent))
        self.assertTrue(week7.passes(case, workflow))

    def test_workflow_has_no_loop(self):
        tree = ast.parse(inspect.getsource(week7.run_workflow))
        self.assertFalse(any(isinstance(node, (ast.For, ast.While)) for node in ast.walk(tree)))

    def test_each_budget_terminates_cleanly(self):
        case = week7.CASES[4]
        settings = {
            "max_iterations": week7.Budgets(max_iterations=1),
            "max_tokens": week7.Budgets(max_iterations=99, max_tokens=1),
            "max_cost": week7.Budgets(max_iterations=99, max_tokens=99999, max_cost_usd=0.000001),
            "wall_clock": week7.Budgets(max_iterations=99, max_tokens=99999, max_cost_usd=1, max_wall_seconds=0),
        }
        for reason, budgets in settings.items():
            with self.subTest(reason=reason):
                result = week7.run_agent(case, budgets)
                self.assertEqual(result.status, f"budget:{reason}")
                self.assertIsNone(result.answer)
                self.assertIn(f"budget={reason}", result.log[-1])


if __name__ == "__main__":
    unittest.main()
