import hashlib
import json
import unittest

from mcp_agent import MCPHost, ROOT, answer_package_query
from week9_evidence import annotations


class Week9MCPTests(unittest.TestCase):
    def discover(self, config: str):
        host = MCPHost(ROOT / config)
        try:
            return host.discover(), host.wire.copy()
        finally:
            host.close()

    def test_live_tool_discovery_before_and_after(self):
        before, _ = self.discover("mcp_config.before.json")
        after, _ = self.discover("mcp_config.json")
        self.assertEqual(before, ["get_openapi_spec", "search_docs"])
        self.assertEqual(after, ["get_openapi_spec", "registry_get_deprecation", "registry_get_version", "search_docs"])

    def test_registry_tool_is_discovered_and_called(self):
        response, wire, names = answer_package_query(ROOT / "mcp_config.json", "docs-sdk")
        self.assertIn("registry_get_version", names)
        self.assertEqual(wire[-1]["server"], "package-registry")
        self.assertEqual(wire[-1]["request"]["method"], "tools/call")
        self.assertEqual(wire[-1]["request"]["params"]["name"], "registry_get_version")
        payload = json.loads(response["result"]["content"][0]["text"])
        self.assertEqual(payload["version"], "3.2.0")

    def test_registry_wire_has_three_phases_and_all_fields_annotated(self):
        artifact = json.loads((ROOT / "wire.json").read_text(encoding="utf-8"))
        self.assertEqual([item["phase"] for item in artifact["exchange"]], ["initialize", "tools/list", "tools/call"])
        for item in artifact["exchange"]:
            self.assertEqual(set(item["request_raw"]), set(item["request_top_level_annotations"]))
            self.assertEqual(set(item["response_raw"]), set(item["response_top_level_annotations"]))
        self.assertIn("host", artifact["architecture_boundary"])
        self.assertIn("no model call", artifact["architecture_boundary"])

    def test_recoverable_unknown_version(self):
        host = MCPHost(ROOT / "mcp_config.before.json")
        try:
            host.discover()
            failed = host.call("search_docs", {"query": "Responses.create", "api_version": "v4"})
            payload = json.loads(failed["result"]["content"][0]["text"])
            self.assertTrue(payload["retryable"])
            self.assertEqual(payload["latest_version"], "v3.2")
            recovered = host.call("search_docs", {"query": "Responses.create migration", "api_version": payload["latest_version"]})
            self.assertFalse(recovered["result"]["isError"])
        finally:
            host.close()

    def test_agent_zero_change_proof_and_risk_line_count(self):
        digest = hashlib.sha256((ROOT / "mcp_agent.py").read_bytes()).hexdigest()
        proof = (ROOT / "agent_diff.txt").read_text(encoding="utf-8")
        self.assertEqual(proof.count(digest), 2)
        self.assertIn("Changed agent lines: 0", proof)
        self.assertEqual(len((ROOT / "risk_note.md").read_text(encoding="utf-8").splitlines()), 5)


if __name__ == "__main__":
    unittest.main()
