import unittest

from evals import (
    assert_deprecations,
    assert_endpoints_exist,
    assert_python_code_parses,
    assert_requested_version_stated,
    build_cases,
)


class AssertionTests(unittest.TestCase):
    def test_python_parser_passes_and_fails(self):
        self.assertEqual(assert_python_code_parses("```python\nx = 1\n```").status, "PASS")
        self.assertEqual(assert_python_code_parses("```python\nx =\n```").status, "FAIL")

    def test_endpoint_lookup_passes_and_fails(self):
        paths = {"/v3/responses"}
        self.assertEqual(assert_endpoints_exist("POST /v3/responses", paths).status, "PASS")
        self.assertEqual(assert_endpoints_exist("POST /v3/missing", paths).status, "FAIL")

    def test_version_statement_passes_and_fails(self):
        question = "How does this work in v3?"
        self.assertEqual(assert_requested_version_stated(question, "In v3, use create.").status, "PASS")
        self.assertEqual(assert_requested_version_stated(question, "Use create.").status, "FAIL")

    def test_deprecation_note_passes_and_fails(self):
        deprecated = {"Client.send_legacy": "Use Client.send."}
        self.assertEqual(
            assert_deprecations("Migrate from Client.send_legacy to Client.send.", deprecated).status,
            "PASS",
        )
        self.assertEqual(assert_deprecations("Call Client.send_legacy.", deprecated).status, "FAIL")

    def test_eval_set_has_25_tagged_cases(self):
        cases = build_cases()
        self.assertEqual(len(cases), 25)
        self.assertTrue(all(case["mode"] for case in cases))


if __name__ == "__main__":
    unittest.main()
