from __future__ import annotations

import json

from mcp_agent import MCPHost, ROOT


def main() -> None:
    host = MCPHost(ROOT / "capstone_mcp_config.json")
    try:
        tools = host.discover()
        response = host.call(
            "version_scoped_search",
            {
                "query": "How do I search in v3?",
                "symbol": "client.search",
                "api_version": "v3.0",
                "trace_id": "external-reviewer-demo",
            },
        )
        print(json.dumps({"discovered": tools, "response": response}, indent=2))
    finally:
        host.close()


if __name__ == "__main__":
    main()
