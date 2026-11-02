from __future__ import annotations

import json
import sys

from versioned_rag import version_scoped_search


DOCS = {
    "v2.4": {
        "client.query": {
            "exists": True,
            "summary": "Search records with client.query(text); timeout is optional.",
            "code": "client.query(text='shoes')",
            "url": "https://docs.example.test/sdk/v2.4/client-query",
        },
        "client.search": {"exists": False},
        "files.upload": {
            "exists": True,
            "summary": "Upload a file with files.upload(file).",
            "code": "files.upload(file='guide.pdf')",
            "url": "https://docs.example.test/sdk/v2.4/files-upload",
        },
        "client.paginate": {
            "exists": True,
            "summary": "Paginate with client.paginate(cursor=cursor).",
            "code": "client.paginate(cursor='next')",
            "url": "https://docs.example.test/sdk/v2.4/pagination",
        },
    },
    "v3.0": {
        "client.query": {"exists": False},
        "client.search": {
            "exists": True,
            "summary": "Search records with client.search(text, timeout); timeout is mandatory.",
            "code": "client.search(text='shoes', timeout=30)",
            "url": "https://docs.example.test/sdk/v3.0/client-search",
        },
        "files.upload": {
            "exists": True,
            "summary": "Upload a file with files.upload(file, timeout).",
            "code": "files.upload(file='guide.pdf', timeout=30)",
            "url": "https://docs.example.test/sdk/v3.0/files-upload",
        },
        "client.paginate": {
            "exists": True,
            "summary": "Paginate with client.paginate(cursor, timeout).",
            "code": "client.paginate(cursor='next', timeout=30)",
            "url": "https://docs.example.test/sdk/v3.0/pagination",
        },
    },
}

DEPRECATIONS = {
    ("v2.4", "client.query"): {
        "deprecated": True,
        "replacement": "client.search",
        "removed_in": "v3.0",
        "notice": "client.query is deprecated in v2.4 and removed in v3.0; migrate to client.search when upgrading.",
    },
    ("v3.0", "client.query"): {
        "deprecated": True,
        "replacement": "client.search",
        "removed_in": "v3.0",
        "notice": "client.query no longer exists in v3.0; use client.search with mandatory timeout.",
    },
}

TOOLS = [
    {
        "name": "version_scoped_search",
        "description": "Search only the live SDK documentation matching the caller's resolved version and return version-labelled citations.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "symbol": {"type": "string"},
                "api_version": {"type": "string", "enum": ["v2.4", "v3.0"]},
                "trace_id": {"type": "string"},
            },
            "required": ["query", "symbol", "api_version", "trace_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "check_deprecation",
        "description": "Return deprecation, replacement, and removal-version metadata for one SDK symbol.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "symbol": {"type": "string"},
                "api_version": {"type": "string", "enum": ["v2.4", "v3.0"]},
                "trace_id": {"type": "string"},
            },
            "required": ["symbol", "api_version", "trace_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "symbol_exists",
        "description": "Check whether one exact SDK symbol exists in the caller's resolved version.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "symbol": {"type": "string"},
                "api_version": {"type": "string", "enum": ["v2.4", "v3.0"]},
                "trace_id": {"type": "string"},
            },
            "required": ["symbol", "api_version", "trace_id"],
            "additionalProperties": False,
        },
    },
]


def call_tool(name: str, arguments: dict) -> dict:
    version = arguments.get("api_version")
    symbol = arguments.get("symbol")
    trace_id = arguments.get("trace_id")
    if version not in DOCS:
        return {"isError": True, "code": "UNKNOWN_VERSION", "message": "Supported live versions are v2.4 and v3.0.", "trace_id": trace_id}
    if name == "version_scoped_search":
        chunk = version_scoped_search(DOCS, arguments.get("query", ""), symbol, version)
        if chunk is None:
            return {"isError": False, "found": False, "symbol": symbol, "api_version": version, "context_ids": [], "trace_id": trace_id}
        return {
            "isError": False,
            "found": True,
            "symbol": symbol,
            "api_version": version,
            "summary": chunk.text,
            "code": chunk.code,
            "citation": {"url": chunk.url, "version": chunk.sdk_version},
            "context_ids": [chunk.chunk_id],
            "trace_id": trace_id,
        }
    if name == "check_deprecation":
        record = DEPRECATIONS.get((version, symbol))
        return {
            "isError": False,
            "symbol": symbol,
            "api_version": version,
            "deprecated": bool(record),
            **(record or {}),
            "trace_id": trace_id,
        }
    if name == "symbol_exists":
        exists = DOCS[version].get(symbol, {}).get("exists", False)
        return {"isError": False, "symbol": symbol, "api_version": version, "exists": exists, "trace_id": trace_id}
    return {"isError": True, "code": "UNKNOWN_TOOL", "message": name, "trace_id": trace_id}


def respond(request: dict) -> dict:
    method = request.get("method")
    if method == "initialize":
        result = {"protocolVersion": "2025-06-18", "capabilities": {"tools": {}}, "serverInfo": {"name": "sdk-docs-capstone", "version": "1.0.0"}}
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
