from __future__ import annotations

import json
import sys


LATEST_VERSION = "v3.2"
TOOLS = [
    {
        "name": "search_docs",
        "description": (
            "Find a published developer-documentation page for one API version. "
            "Use this before answering version-specific SDK questions. If the requested "
            "version is unpublished, use the returned latest_version and migration_path "
            "to recover instead of guessing an endpoint."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "api_version": {"type": "string", "enum": ["v2", "v3.2", "v4"]},
            },
            "required": ["query", "api_version"],
            "additionalProperties": False,
        },
    },
    {
        "name": "get_openapi_spec",
        "description": "Return the published method and endpoint path for one documented operation.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "operation": {"type": "string", "enum": ["Responses.create", "Files.upload"]},
                "api_version": {"type": "string", "enum": ["v2", "v3.2"]},
            },
            "required": ["operation", "api_version"],
            "additionalProperties": False,
        },
    },
]


def call_tool(name: str, arguments: dict) -> dict:
    if name == "search_docs":
        version = arguments["api_version"]
        if version == "v4":
            return {
                "isError": True,
                "code": "UNPUBLISHED_VERSION",
                "message": "No docs exist for v4; latest published is v3.2.",
                "latest_version": LATEST_VERSION,
                "migration_path": "Read v3.2/migration for deprecated methods and retry with api_version=v3.2.",
                "retryable": True,
            }
        return {"isError": False, "page": f"/{version}/docs/{arguments['query'].lower().replace(' ', '-')}", "api_version": version}
    if name == "get_openapi_spec":
        paths = {"Responses.create": "/v3/responses", "Files.upload": "/v3/files"}
        return {"isError": False, "method": "POST", "path": paths[arguments["operation"]], "api_version": arguments["api_version"]}
    return {"isError": True, "code": "UNKNOWN_TOOL", "message": f"Unknown tool: {name}", "retryable": False}


def respond(request: dict) -> dict:
    method = request.get("method")
    if method == "initialize":
        result = {"protocolVersion": "2025-06-18", "capabilities": {"tools": {}}, "serverInfo": {"name": "docs-search", "version": "1.0.0"}}
    elif method == "tools/list":
        result = {"tools": TOOLS}
    elif method == "tools/call":
        params = request.get("params", {})
        payload = call_tool(params.get("name", ""), params.get("arguments", {}))
        result = {"content": [{"type": "text", "text": json.dumps(payload)}], "isError": payload.get("isError", False)}
    else:
        return {"jsonrpc": "2.0", "id": request.get("id"), "error": {"code": -32601, "message": "Method not found"}}
    return {"jsonrpc": "2.0", "id": request.get("id"), "result": result}


def main() -> None:
    for line in sys.stdin:
        try:
            print(json.dumps(respond(json.loads(line))), flush=True)
        except Exception as exc:
            print(json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32603, "message": str(exc)}}), flush=True)


if __name__ == "__main__":
    main()
