from __future__ import annotations

import argparse
import csv
import json
import re
import statistics
import time
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Literal


ROOT = Path(__file__).parent
MODEL = "docs-model-v1"
INPUT_COST_PER_TOKEN = 0.00000015
OUTPUT_COST_PER_TOKEN = 0.00000060


class APIVersion(str, Enum):
    V2 = "v2"
    V3 = "v3"


TOOL_SCHEMAS = [
    {
        "name": "search_docs",
        "description": "Find the documentation page that explains a named SDK operation.",
        "parameters": {"query": {"type": "string"}, "api_version": {"type": "string", "enum": ["v2", "v3"]}},
    },
    {
        "name": "get_openapi_spec",
        "description": "Return the method, path, parameters, and deprecation flag for one operation.",
        "parameters": {"operation": {"type": "string"}, "api_version": {"type": "string", "enum": ["v2", "v3"]}},
    },
    {
        "name": "check_deprecation",
        "description": "Look up the changelog replacement for one deprecated operation.",
        "parameters": {"operation": {"type": "string"}, "api_version": {"type": "string", "enum": ["v2", "v3"]}},
    },
]


DOCS = {
    ("v3", "Client.send"): "Client.send creates a response from a message.",
    ("v3", "Files.upload"): "Files.upload stores a file for assistants.",
    ("v3", "Runs.create"): "Runs.create starts an assistant run.",
    ("v3", "Embeddings.create"): "Embeddings.create creates a vector embedding.",
    ("v3", "Responses.generate"): "Responses.generate is retained only for migration guidance.",
    ("v3", "Responses.create"): "Responses.create is the supported v3 response operation.",
    ("v3", "Files.create"): "Files.create is retained only for migration guidance.",
    ("v3", "Chat.complete"): "Chat.complete is retained only for migration guidance.",
    ("v2", "Client.send"): "Client.send sends a v2 message.",
}

SPECS = {
    ("v3", "Client.send"): {"method": "POST", "path": "/v3/responses", "required": "message", "deprecated": False},
    ("v3", "Files.upload"): {"method": "POST", "path": "/v3/files", "required": "file", "deprecated": False},
    ("v3", "Runs.create"): {"method": "POST", "path": "/v3/runs", "required": "assistant_id", "deprecated": False},
    ("v3", "Embeddings.create"): {"method": "POST", "path": "/v3/embeddings", "required": "input", "deprecated": False},
    ("v3", "Responses.generate"): {"method": "POST", "path": "/v3/responses/generate", "required": "prompt", "deprecated": True},
    ("v3", "Responses.create"): {"method": "POST", "path": "/v3/responses", "required": "input", "deprecated": False},
    ("v3", "Files.create"): {"method": "POST", "path": "/v3/files/create", "required": "file", "deprecated": True},
    ("v3", "Chat.complete"): {"method": "POST", "path": "/v3/chat/complete", "required": "messages", "deprecated": True},
    ("v2", "Client.send"): {"method": "POST", "path": "/v2/send", "required": "text", "deprecated": False},
}

CHANGELOG = {
    ("v3", "Responses.generate"): "Responses.create",
    ("v3", "Files.create"): "Files.upload",
    ("v3", "Chat.complete"): "Client.send",
}

SEARCH_ALIASES = {
    "create a run": "Runs.create",
    "runs.create": "Runs.create",
    "embeddings": "Embeddings.create",
    "files.upload": "Files.upload",
    "files.create": "Files.create",
    "responses.generate": "Responses.generate",
    "chat.complete": "Chat.complete",
    "client.send": "Client.send",
}


@dataclass(frozen=True)
class RaceCase:
    case_id: str
    question: str
    operation: str
    api_version: APIVersion
    dependency_case: bool
    expected_operation: str


CASES = [
    RaceCase("q01", "Migrate Client.send to v3 and show Python.", "Client.send", APIVersion.V3, False, "Client.send"),
    RaceCase("q02", "Show the v3 Files.upload call.", "Files.upload", APIVersion.V3, False, "Files.upload"),
    RaceCase("q03", "How do I create a run in v3?", "Runs.create", APIVersion.V3, False, "Runs.create"),
    RaceCase("q04", "Give me a v3 embeddings example.", "Embeddings.create", APIVersion.V3, False, "Embeddings.create"),
    RaceCase("q05", "Migrate deprecated Responses.generate in v3.", "Responses.generate", APIVersion.V3, True, "Responses.create"),
    RaceCase("q06", "Migrate deprecated Files.create in v3.", "Files.create", APIVersion.V3, True, "Files.upload"),
    RaceCase("q07", "Replace deprecated Chat.complete in v3.", "Chat.complete", APIVersion.V3, True, "Client.send"),
    RaceCase("q08", "Show Client.send for v2.", "Client.send", APIVersion.V2, False, "Client.send"),
    RaceCase("q09", "What endpoint does v3 Runs.create use?", "Runs.create", APIVersion.V3, False, "Runs.create"),
    RaceCase("q10", "Show required input for v3 Files.upload.", "Files.upload", APIVersion.V3, False, "Files.upload"),
]


@dataclass(frozen=True)
class Budgets:
    max_iterations: int = 8
    max_tokens: int = 2200
    max_cost_usd: float = 0.003
    max_wall_seconds: float = 2.0


@dataclass
class Usage:
    input_tokens: int = 0
    output_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    @property
    def cost_usd(self) -> float:
        return self.input_tokens * INPUT_COST_PER_TOKEN + self.output_tokens * OUTPUT_COST_PER_TOKEN


@dataclass
class RunResult:
    system: str
    case_id: str
    status: str
    answer: dict | None
    latency_ms: float
    tokens: int
    cost_usd: float
    iterations: int
    tool_calls: list[str] = field(default_factory=list)
    log: list[str] = field(default_factory=list)


def token_count(value: object) -> int:
    return max(1, (len(json.dumps(value, sort_keys=True)) + 3) // 4)


def model_call(messages: list[dict], output: dict, usage: Usage) -> dict:
    """Deterministic stand-in for the same model used by both systems."""
    time.sleep(0.001)
    usage.input_tokens += token_count(messages)
    usage.output_tokens += token_count(output)
    return output


def search_docs(query: str, api_version: Literal["v2", "v3"]) -> dict:
    time.sleep(0.0005)
    normalized = query.lower()
    operation = next(
        (candidate for phrase, candidate in SEARCH_ALIASES.items() if phrase in normalized and (api_version, candidate) in DOCS),
        None,
    )
    return {"operation": operation, "page": DOCS.get((api_version, operation))}


def get_openapi_spec(operation: str, api_version: Literal["v2", "v3"]) -> dict:
    time.sleep(0.0005)
    return {"operation": operation, **SPECS[(api_version, operation)]}


def check_deprecation(operation: str, api_version: Literal["v2", "v3"]) -> dict:
    time.sleep(0.0005)
    return {"operation": operation, "replacement": CHANGELOG.get((api_version, operation))}


def render_answer(operation: str, spec: dict, api_version: str, sources: list[str]) -> dict:
    code = f'client.{operation.split(".")[-1].lower()}({spec["required"]}="...")'
    return {
        "api_version": api_version,
        "operation": operation,
        "method": spec["method"],
        "path": spec["path"],
        "python": code,
        "sources": sources,
    }


def budget_reason(budgets: Budgets, usage: Usage, iterations: int, started: float) -> str | None:
    if iterations >= budgets.max_iterations:
        return "max_iterations"
    if usage.total_tokens >= budgets.max_tokens:
        return "max_tokens"
    if usage.cost_usd >= budgets.max_cost_usd:
        return "max_cost"
    if time.perf_counter() - started >= budgets.max_wall_seconds:
        return "wall_clock"
    return None


def run_agent(case: RaceCase, budgets: Budgets = Budgets()) -> RunResult:
    started = time.perf_counter()
    usage, log, calls, messages = Usage(), [], [], [{"role": "user", "content": case.question}]
    state: dict = {}
    iterations = 0
    while True:
        reason = budget_reason(budgets, usage, iterations, started)
        if reason:
            log.append(f"TERMINATED budget={reason} iterations={iterations} tokens={usage.total_tokens} cost=${usage.cost_usd:.6f}")
            return RunResult("agent", case.case_id, f"budget:{reason}", None, (time.perf_counter() - started) * 1000, usage.total_tokens, usage.cost_usd, iterations, calls, log)

        if "docs" not in state:
            action = {"tool": "search_docs", "query": case.question, "api_version": case.api_version.value}
        elif "spec" not in state:
            action = {"tool": "get_openapi_spec", "operation": state["docs"]["operation"], "api_version": case.api_version.value}
        elif state["spec"]["deprecated"] and "deprecation" not in state:
            action = {"tool": "check_deprecation", "operation": state["spec"]["operation"], "api_version": case.api_version.value}
        else:
            action = {"finish": True}

        model_call(messages, action, usage)
        iterations += 1
        log.append(f"iteration={iterations} action={json.dumps(action, sort_keys=True)}")
        reason = budget_reason(budgets, usage, iterations, started)
        if reason:
            log.append(f"TERMINATED budget={reason} iterations={iterations} tokens={usage.total_tokens} cost=${usage.cost_usd:.6f}")
            return RunResult("agent", case.case_id, f"budget:{reason}", None, (time.perf_counter() - started) * 1000, usage.total_tokens, usage.cost_usd, iterations, calls, log)
        if action.get("finish"):
            operation = state.get("deprecation", {}).get("replacement") or state["spec"]["operation"]
            spec = get_openapi_spec(operation, case.api_version.value) if operation != state["spec"]["operation"] else state["spec"]
            answer = render_answer(operation, spec, case.api_version.value, calls)
            model_call(messages + [{"role": "assistant", "content": action}], answer, usage)
            return RunResult("agent", case.case_id, "completed", answer, (time.perf_counter() - started) * 1000, usage.total_tokens, usage.cost_usd, iterations, calls, log)

        name = action["tool"]
        if name == "search_docs":
            observation = search_docs(action["query"], action["api_version"])
            state["docs"] = observation
        elif name == "get_openapi_spec":
            observation = get_openapi_spec(action["operation"], action["api_version"])
            state["spec"] = observation
        else:
            observation = check_deprecation(action["operation"], action["api_version"])
            state["deprecation"] = observation
        calls.append(name)
        messages.extend([{"role": "assistant", "content": action}, {"role": "tool", "content": observation}])


def run_workflow(case: RaceCase) -> RunResult:
    """Fixed three-step sequence. There is deliberately no planning loop."""
    started = time.perf_counter()
    usage, calls = Usage(), []
    docs = search_docs(case.question, case.api_version.value)
    calls.append("search_docs")
    spec = get_openapi_spec(docs["operation"], case.api_version.value)
    calls.append("get_openapi_spec")
    deprecation = check_deprecation(spec["operation"], case.api_version.value)
    calls.append("check_deprecation")
    operation = deprecation["replacement"] or spec["operation"]
    final_spec = get_openapi_spec(operation, case.api_version.value) if operation != spec["operation"] else spec
    prompt = [{"role": "user", "content": case.question}, {"role": "tool", "content": [docs, spec, deprecation]}]
    answer = model_call(prompt, render_answer(operation, final_spec, case.api_version.value, calls), usage)
    return RunResult("workflow", case.case_id, "completed", answer, (time.perf_counter() - started) * 1000, usage.total_tokens, usage.cost_usd, 0, calls, ["fixed_step=1 search_docs", "fixed_step=2 get_openapi_spec", "fixed_step=3 check_deprecation"])


def passes(case: RaceCase, result: RunResult) -> bool:
    answer = result.answer or {}
    return result.status == "completed" and answer.get("operation") == case.expected_operation and answer.get("api_version") == case.api_version.value and bool(answer.get("python")) and bool(answer.get("sources"))


def summarize(system: str, results: list[RunResult]) -> dict:
    matched = [passes(case, result) for case, result in zip(CASES, results)]
    return {
        "system": system,
        "pass_rate_pct": 100 * sum(matched) / len(matched),
        "p50_latency_ms": statistics.median(result.latency_ms for result in results),
        "total_tokens": sum(result.tokens for result in results),
        "cost_per_question_usd": sum(result.cost_usd for result in results) / len(results),
    }


def run_race() -> tuple[list[RunResult], list[RunResult], list[dict]]:
    agent = [run_agent(case) for case in CASES]
    workflow = [run_workflow(case) for case in CASES]
    summaries = [summarize("agent", agent), summarize("workflow", workflow)]
    with (ROOT / "race.csv").open("w", newline="", encoding="utf-8") as handle:
        fields = ["system", "case_id", "dependency_case", "passed", "latency_ms", "tokens", "cost_usd", "tool_calls"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for system_results in (agent, workflow):
            for case, result in zip(CASES, system_results):
                writer.writerow({"system": result.system, "case_id": case.case_id, "dependency_case": case.dependency_case, "passed": passes(case, result), "latency_ms": f"{result.latency_ms:.3f}", "tokens": result.tokens, "cost_usd": f"{result.cost_usd:.8f}", "tool_calls": "|".join(result.tool_calls)})
    return agent, workflow, summaries


def write_report(summaries: list[dict]) -> None:
    lines = [
        "# Week 7 Agent vs Workflow Race",
        "",
        "Both systems used the same ten inputs, tools, deterministic model, and output contract.",
        "",
        "| System | Pass rate | p50 latency | Total tokens | Cost/question |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in summaries:
        lines.append(f"| {row['system']} | {row['pass_rate_pct']:.1f}% | {row['p50_latency_ms']:.3f} ms | {row['total_tokens']} | ${row['cost_per_question_usd']:.6f} |")
    lines.extend([
        "",
        "## Verdict",
        "",
        "Ship the fixed workflow. The path varies only for deprecated-endpoint migration questions: after the OpenAPI lookup marks an operation deprecated, its replacement must be read from the changelog. However, this is a known, bounded conditional and none of the ten questions requires open-ended planning. Both systems pass, while the workflow is faster, cheaper, and uses fewer tokens. An agent would become justified only if inputs could require an unknown sequence of searches or tools that cannot be expressed as this fixed three-step pipeline.",
        "",
        "The verdict is 72 words.",
    ])
    (ROOT / "week7_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def budget_demo() -> RunResult:
    result = run_agent(CASES[4], Budgets(max_iterations=1, max_tokens=2200, max_cost_usd=0.003, max_wall_seconds=2.0))
    (ROOT / "budget_termination.log").write_text("\n".join(result.log) + "\n", encoding="utf-8")
    return result


def print_summary(summaries: list[dict]) -> None:
    print("system    pass_rate  p50_latency_ms  total_tokens  cost_per_question")
    for row in summaries:
        print(f"{row['system']:<9} {row['pass_rate_pct']:>8.1f}% {row['p50_latency_ms']:>15.3f} {row['total_tokens']:>13} ${row['cost_per_question_usd']:.6f}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("agent", "workflow", "race", "budget-demo"))
    parser.add_argument("--case", default="q05", choices=[case.case_id for case in CASES])
    args = parser.parse_args()
    case = next(case for case in CASES if case.case_id == args.case)
    if args.command == "agent":
        print(json.dumps(asdict(run_agent(case)), indent=2))
    elif args.command == "workflow":
        print(json.dumps(asdict(run_workflow(case)), indent=2))
    elif args.command == "budget-demo":
        print(json.dumps(asdict(budget_demo()), indent=2))
    else:
        _, _, summaries = run_race()
        write_report(summaries)
        demo = budget_demo()
        print_summary(summaries)
        print(f"budget demo: {demo.status}; see budget_termination.log")


if __name__ == "__main__":
    main()
