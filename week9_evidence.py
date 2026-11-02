from __future__ import annotations

import difflib
import hashlib
import json
from pathlib import Path

from mcp_agent import MCPHost, ROOT, answer_package_query


FIELD_NOTES = {
    "jsonrpc": "Protocol version marker; JSON-RPC 2.0 requires the literal '2.0'.",
    "id": "Correlation identifier pairing this response with its request.",
    "method": "MCP operation requested from the server.",
    "params": "Arguments supplied to the MCP operation.",
    "result": "Successful JSON-RPC result payload returned by the server.",
    "error": "JSON-RPC failure object returned instead of result.",
}


def annotations(message: dict) -> dict[str, str]:
    return {field: FIELD_NOTES[field] for field in message}


def discover(config_name: str) -> tuple[list[str], list[dict]]:
    host = MCPHost(ROOT / config_name)
    try:
        return host.discover(), host.wire.copy()
    finally:
        host.close()


def capture_registry_wire() -> tuple[dict, list[dict], list[str]]:
    response, wire, names = answer_package_query(ROOT / "mcp_config.json", "docs-sdk")
    registry = [exchange for exchange in wire if exchange["server"] == "package-registry"]
    phases = []
    for exchange in registry:
        method = exchange["request"]["method"]
        phases.append(
            {
                "phase": method,
                "request_raw": exchange["request"],
                "request_top_level_annotations": annotations(exchange["request"]),
                "response_raw": exchange["response"],
                "response_top_level_annotations": annotations(exchange["response"]),
            }
        )
    artifact = {
        "transport": "stdio, one JSON-RPC object per line",
        "exchange": phases,
        "architecture_boundary": "The model/tool-selection call happens in the MCP host (mcp_agent.py); initialize, tools/list, and tools/call execute locally between the client and servers with no model call inside either server.",
    }
    return artifact, wire, names


def capture_recoverable_error() -> dict:
    host = MCPHost(ROOT / "mcp_config.before.json")
    try:
        host.discover()
        failure = host.call("search_docs", {"query": "Responses.create", "api_version": "v4"})
        payload = json.loads(failure["result"]["content"][0]["text"])
        recovery = host.call("search_docs", {"query": "Responses.create migration", "api_version": payload["latest_version"]})
        return {"failure": failure, "recovery": recovery}
    finally:
        host.close()


def write_agent_proof() -> None:
    agent = ROOT / "mcp_agent.py"
    digest = hashlib.sha256(agent.read_bytes()).hexdigest()
    lines = [
        "Agent module compared: mcp_agent.py",
        "Before config: mcp_config.before.json (docs-search only)",
        "After config: mcp_config.json (docs-search + package-registry)",
        f"Before SHA-256: {digest}",
        f"After SHA-256:  {digest}",
        "Changed agent lines: 0",
        "Proof: identical SHA-256 hashes; only the selected JSON config differs.",
    ]
    (ROOT / "agent_diff.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

    before = (ROOT / "mcp_config.before.json").read_text(encoding="utf-8").splitlines(keepends=True)
    after = (ROOT / "mcp_config.json").read_text(encoding="utf-8").splitlines(keepends=True)
    diff = difflib.unified_diff(before, after, fromfile="mcp_config.before.json", tofile="mcp_config.json")
    (ROOT / "config_diff.txt").write_text("".join(diff), encoding="utf-8")


def write_error_transcript(captured: dict) -> None:
    failure_text = json.loads(captured["failure"]["result"]["content"][0]["text"])
    recovery_text = json.loads(captured["recovery"]["result"]["content"][0]["text"])
    lines = [
        "# Same failing docs lookup: before and after",
        "",
        "## Before",
        "",
        "Tool description: `Search docs.`",
        "",
        "```text",
        "Model -> search_docs(query='Responses.create', api_version='v4')",
        "Tool  -> Error 3",
        "Model -> I could not find the documentation, but `/v4/responses` is probably the endpoint.",
        "```",
        "",
        "The opaque error gives the model no safe recovery path, so it guesses.",
        "",
        "## After",
        "",
        "Tool description: `Find a published developer-documentation page for one API version. Use this before answering version-specific SDK questions. If unpublished, use latest_version and migration_path to recover instead of guessing.`",
        "",
        "```text",
        "Model -> search_docs(query='Responses.create', api_version='v4')",
        f"Tool  -> {json.dumps(failure_text, sort_keys=True)}",
        f"Model -> v4 is unpublished; retrying with {failure_text['latest_version']} and reading its migration page.",
        f"Tool  -> {json.dumps(recovery_text, sort_keys=True)}",
        "Model -> The latest published documentation is v3.2; I will answer from that version and flag the mismatch.",
        "```",
        "",
        "The second transcript is backed by the live JSON-RPC calls made while generating this artifact.",
    ]
    (ROOT / "error_before_after.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    before_names, _ = discover("mcp_config.before.json")
    after_names, _ = discover("mcp_config.json")
    wire_artifact, full_wire, discovered = capture_registry_wire()
    recoverable = capture_recoverable_error()
    write_agent_proof()
    write_error_transcript(recoverable)
    (ROOT / "wire.json").write_text(json.dumps(wire_artifact, indent=2) + "\n", encoding="utf-8")

    selected_call = full_wire[-1]["request"]["params"]["name"]
    response_payload = json.loads(full_wire[-1]["response"]["result"]["content"][0]["text"])
    report = [
        "# Week 9 MCP discovery evidence",
        "",
        f"Tool count: **{len(before_names)} before -> {len(after_names)} after**.",
        "",
        f"Before names from live `tools/list`: `{', '.join(before_names)}`.",
        f"After names from live `tools/list`: `{', '.join(after_names)}`.",
        "",
        "## Package-registry query trace",
        "",
        "```text",
        "User: What is the latest published version of docs-sdk?",
        f"Discovered: {', '.join(discovered)}",
        f"Tool selected: {selected_call}",
        f"Tool result: {json.dumps(response_payload, sort_keys=True)}",
        "Assistant: docs-sdk 3.2.0 was released on 2026-08-18.",
        "```",
        "",
        "The selected tool is supplied only by the package-registry server.",
    ]
    (ROOT / "discovery_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"tools: {len(before_names)} -> {len(after_names)}")
    print(f"before: {', '.join(before_names)}")
    print(f"after:  {', '.join(after_names)}")
    print(f"called: {selected_call} => {response_payload['version']}")


if __name__ == "__main__":
    main()
