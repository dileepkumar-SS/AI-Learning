from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).parent


@dataclass
class ServerSession:
    name: str
    process: subprocess.Popen
    request_id: int = 0

    def request(self, method: str, params: dict | None = None) -> tuple[dict, dict]:
        self.request_id += 1
        message = {"jsonrpc": "2.0", "id": self.request_id, "method": method, "params": params or {}}
        assert self.process.stdin is not None and self.process.stdout is not None
        self.process.stdin.write(json.dumps(message) + "\n")
        self.process.stdin.flush()
        response = json.loads(self.process.stdout.readline())
        return message, response

    def close(self) -> None:
        self.process.terminate()
        self.process.wait(timeout=2)
        for stream in (self.process.stdin, self.process.stdout, self.process.stderr):
            if stream is not None:
                stream.close()


class MCPHost:
    """Configuration-driven MCP host. Tool names and schemas are never hard-coded here."""

    def __init__(self, config_path: Path):
        config = json.loads(config_path.read_text(encoding="utf-8"))
        self.sessions: list[ServerSession] = []
        self.tools: dict[str, tuple[ServerSession, dict]] = {}
        self.wire: list[dict] = []
        for name, server in config["servers"].items():
            process = subprocess.Popen(
                [server["command"], *server.get("args", [])],
                cwd=ROOT,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
            )
            self.sessions.append(ServerSession(name, process))

    def discover(self) -> list[str]:
        for session in self.sessions:
            for method in ("initialize", "tools/list"):
                request, response = session.request(method)
                self.wire.append({"server": session.name, "request": request, "response": response})
                if method == "tools/list":
                    for tool in response["result"]["tools"]:
                        self.tools[tool["name"]] = (session, tool)
        return sorted(self.tools)

    def call(self, tool_name: str, arguments: dict) -> dict:
        session, _ = self.tools[tool_name]
        request, response = session.request("tools/call", {"name": tool_name, "arguments": arguments})
        self.wire.append({"server": session.name, "request": request, "response": response})
        return response

    def close(self) -> None:
        for session in self.sessions:
            session.close()


def answer_package_query(config_path: Path, package: str) -> tuple[dict, list[dict], list[str]]:
    """The model decision belongs in this host; MCP servers only execute JSON-RPC tools."""
    host = MCPHost(config_path)
    try:
        names = host.discover()
        selected = next(
            name
            for name, (_, schema) in host.tools.items()
            if "latest published version" in schema["description"].lower()
        )
        response = host.call(selected, {"package": package})
        return response, host.wire, names
    finally:
        host.close()


if __name__ == "__main__":
    response, wire, names = answer_package_query(ROOT / "mcp_config.json", "docs-sdk")
    print(json.dumps({"discovered_tools": names, "selected_tool": wire[-1]["request"]["params"]["name"], "response": response}, indent=2))
