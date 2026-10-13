from __future__ import annotations

import json
import sys


TOOLS = [
    {
        "name": "registry_get_version",
        "description": "Get the latest published version and release date for one package.",
        "inputSchema": {
            "type": "object",
            "properties": {"package": {"type": "string"}},
            "required": ["package"],
            "additionalProperties": False,
        },
    },
    {
        "name": "registry_get_deprecation",
        "description": "Get the published deprecation notice for one package version.",
        "inputSchema": {
            "type": "object",
            "properties": {"package": {"type": "string"}, "version": {"type": "string"}},
            "required": ["package", "version"],
            "additionalProperties": False,
        },
    },
]

PACKAGES = {
    "docs-sdk": {"version": "3.2.0", "released": "2026-08-18", "deprecated": {"2.8.0": "Migrate Client.send_legacy to Client.send."}},
    "openapi-client": {"version": "5.1.0", "released": "2026-07-04", "deprecated": {}},
}


def call_tool(name: str, arguments: dict) -> dict:
    package = arguments.get("package")
    if package not in PACKAGES:
        return {"isError": True, "code": "PACKAGE_NOT_FOUND", "message": f"Package {package!r} is not published.", "retryable": False}
    record = PACKAGES[package]
    if name == "registry_get_version":
        return {"isError": False, "package": package, "version": record["version"], "released": record["released"]}
    if name == "registry_get_deprecation":
        version = arguments.get("version")
        return {"isError": False, "package": package, "version": version, "notice": record["deprecated"].get(version, "No deprecation notice.")}
    return {"isError": True, "code": "UNKNOWN_TOOL", "message": f"Unknown tool: {name}", "retryable": False}


def respond(request: dict) -> dict:
    method = request.get("method")
    if method == "initialize":
        result = {"protocolVersion": "2025-06-18", "capabilities": {"tools": {}}, "serverInfo": {"name": "package-registry", "version": "1.0.0"}}
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
