import ast
import json
import unittest

import capstone
from capstone_mcp_server import DOCS
from mcp_agent import MCPHost
from versioned_rag import version_scoped_search


class CapstoneTests(unittest.TestCase):
    def test_rag_filters_version_before_ranking(self):
        v2 = version_scoped_search(DOCS, "search records", "client.query", "v2.4")
        v3 = version_scoped_search(DOCS, "search records", "client.search", "v3.0")
        self.assertEqual(v2.sdk_version, "v2.4")
        self.assertEqual(v3.sdk_version, "v3.0")
        self.assertNotEqual(v2.code, v3.code)

    def test_three_tools_are_discovered_at_runtime(self):
        host = MCPHost(capstone.ROOT / "capstone_mcp_config.json")
        try:
            self.assertEqual(host.discover(), ["check_deprecation", "symbol_exists", "version_scoped_search"])
        finally:
            host.close()

    def test_v2_answer_has_versioned_citation_and_unasked_deprecation(self):
        trace = capstone.answer_question("How do I use client.query?", "v2.4", persist_trace=False)
        answer = trace["answer"]
        self.assertEqual(answer["citation"]["version"], "v2.4")
        self.assertIn("SDK v2.4", answer["citation_markdown"])
        self.assertIn("removed in v3.0", answer["answer"])
        ast.parse(answer["code"])

    def test_removed_v3_method_is_plainly_migrated(self):
        trace = capstone.answer_question("How do I use client.query?", "v3.0", persist_trace=False)
        answer = trace["answer"]
        self.assertIn("no longer exists in v3.0", answer["answer"])
        self.assertEqual(answer["symbol"], "client.search")
        self.assertIn("timeout=30", answer["code"])
        self.assertEqual(answer["citation"]["version"], "v3.0")

    def test_trace_id_survives_all_agent_and_mcp_hops(self):
        trace = capstone.answer_question("Show upload code.", "v3.0", persist_trace=False)
        trace_id = trace["trace_id"]
        self.assertEqual(trace["answer"]["trace_id"], trace_id)
        for item in trace["spans"]:
            if item["name"] in {"mcp_discovery", "symbol_check", "deprecation", "retrieval"}:
                self.assertEqual(item["trace_id"], trace_id)
        self.assertEqual(trace["mcp_wire_methods"], ["initialize", "tools/list", "tools/call", "tools/call", "tools/call"])

    def test_secrets_are_redacted_before_persistence(self):
        secret = "sk-super-secret-123456789"
        connection = "postgres://admin:password@db/prod"
        trace = capstone.answer_question(f"Use {secret} and {connection} to show upload.", "v3.0", persist_trace=True)
        serialized = json.dumps(trace)
        self.assertNotIn(secret, serialized)
        self.assertNotIn(connection, serialized)
        self.assertTrue(trace["pii_redacted_on_write"])
        persisted = capstone.TRACE_PATH.read_text(encoding="utf-8")
        self.assertNotIn(secret, persisted)
        self.assertNotIn(connection, persisted)

    def test_integrated_eval_and_judge_threshold(self):
        records, summary = capstone.run_integrated_eval()
        self.assertEqual(summary["total"], 30)
        self.assertEqual(summary["passed"], 30)
        self.assertGreaterEqual(summary["judge_agreement"], 85.0)
        self.assertTrue(all(all(record["assertions"].values()) for record in records))

    def test_failure_loop_taxonomy_and_required_artifacts(self):
        red = (capstone.ROOT / "capstone_loop_red.txt").read_text(encoding="utf-8")
        green = (capstone.ROOT / "capstone_loop_green.txt").read_text(encoding="utf-8")
        taxonomy = (capstone.ROOT / "integrated_taxonomy.md").read_text(encoding="utf-8")
        self.assertIn("29/30", red)
        self.assertIn("30/30", green)
        self.assertIn("NEW integration-created mode", taxonomy)
        for name in ("seam_list.md", "architecture.md", "top_3_weaknesses.md", "demo_script.md", "fresh_eyes.md"):
            self.assertTrue((capstone.ROOT / name).exists(), name)


if __name__ == "__main__":
    unittest.main()
