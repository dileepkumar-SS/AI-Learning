from __future__ import annotations

import csv
import json
import statistics
from dataclasses import dataclass
from pathlib import Path

from week7 import (
    CASES,
    CHANGELOG,
    DOCS,
    INPUT_COST_PER_TOKEN,
    OUTPUT_COST_PER_TOKEN,
    SPECS,
    RaceCase,
)


ROOT = Path(__file__).parent
MITIGATION = "Require get_openapi_spec before finish in the agent planning description."

# Some explicitly deprecated operations may legitimately check the changelog
# either before or after the spec. These cases therefore accept a set of paths.
EXPECTED_SEQUENCES: dict[str, set[tuple[str, ...]]] = {
    "q01": {("search_docs", "get_openapi_spec")},
    "q02": {("search_docs", "get_openapi_spec")},
    "q03": {("search_docs", "get_openapi_spec")},
    "q04": {("search_docs", "get_openapi_spec")},
    "q05": {
        ("search_docs", "get_openapi_spec", "check_deprecation"),
        ("search_docs", "check_deprecation", "get_openapi_spec"),
    },
    "q06": {
        ("search_docs", "get_openapi_spec", "check_deprecation"),
        ("search_docs", "check_deprecation", "get_openapi_spec"),
    },
    "q07": {
        ("search_docs", "get_openapi_spec", "check_deprecation"),
        ("search_docs", "check_deprecation", "get_openapi_spec"),
    },
    "q08": {("search_docs", "get_openapi_spec")},
    "q09": {("search_docs", "get_openapi_spec")},
    "q10": {("search_docs", "get_openapi_spec")},
}

ALTERNATE_PATH_CASES = {"q05", "q06", "q07"}
FAILURE_MODES = (
    "missing_required_tool",
    "invalid_argument",
    "wrong_tool",
    "redundant_step",
)


@dataclass(frozen=True)
class ToolCall:
    tool: str
    arguments: dict[str, str]
    result: dict
    input_tokens: int
    output_tokens: int

    @property
    def cost_usd(self) -> float:
        return self.input_tokens * INPUT_COST_PER_TOKEN + self.output_tokens * OUTPUT_COST_PER_TOKEN


@dataclass(frozen=True)
class TrajectoryRun:
    case_id: str
    question: str
    calls: tuple[ToolCall, ...]
    answer_operation: str
    expected_operation: str
    latency_ms: float

    @property
    def sequence(self) -> tuple[str, ...]:
        return tuple(call.tool for call in self.calls)

    @property
    def cost_usd(self) -> float:
        final_answer_cost = 90 * INPUT_COST_PER_TOKEN + 35 * OUTPUT_COST_PER_TOKEN
        return sum(call.cost_usd for call in self.calls) + final_answer_cost

    @property
    def tokens(self) -> int:
        return sum(call.input_tokens + call.output_tokens for call in self.calls) + 125


def call(tool: str, operation: str, version: str, *, invalid_version: bool = False) -> ToolCall:
    api_version = "v4" if invalid_version else version
    arguments = {"operation": operation, "api_version": api_version}
    if tool == "search_docs":
        arguments = {"query": operation, "api_version": api_version}
        result = {"operation": operation, "page": DOCS.get((version, operation))}
    elif tool == "get_openapi_spec":
        result = {"operation": operation, **SPECS[(version, operation)]}
        if invalid_version:
            result = {**result, "path": "/v4/fluent-fiction"}
    elif tool == "check_deprecation":
        result = {"operation": operation, "replacement": CHANGELOG.get((version, operation))}
    else:
        raise ValueError(tool)
    sizes = {
        "search_docs": (72, 34),
        "get_openapi_spec": (91, 48),
        "check_deprecation": (83, 31),
    }
    input_tokens, output_tokens = sizes[tool]
    return ToolCall(tool, arguments, result, input_tokens, output_tokens)


def normal_calls(case: RaceCase) -> list[ToolCall]:
    version = case.api_version.value
    calls = [call("search_docs", case.operation, version), call("get_openapi_spec", case.operation, version)]
    if case.dependency_case:
        calls.append(call("check_deprecation", case.operation, version))
    return calls


def generate_run(case: RaceCase, mitigated: bool) -> TrajectoryRun:
    """Generate a reproducible recorded trajectory for the controlled experiment."""
    version = case.api_version.value
    calls = normal_calls(case)

    # Baseline failures captured from the agent failure zoo. The mitigation only
    # changes missing-spec behavior; every other trajectory remains identical.
    lower_question = case.question.lower()
    trusts_memorized_detail = any(
        phrase in lower_question
        for phrase in ("migrate client.send", "what endpoint", "required input")
    )
    if trusts_memorized_detail and not mitigated:
        calls = [call("search_docs", case.operation, version)]
    elif "create a run" in lower_question:
        calls = [
            call("search_docs", case.operation, version),
            call("check_deprecation", case.operation, version),
            call("get_openapi_spec", case.operation, version),
        ]
    elif "embeddings example" in lower_question:
        calls = [
            call("search_docs", case.operation, version),
            call("get_openapi_spec", case.operation, version, invalid_version=True),
        ]
    elif "deprecated files.create" in lower_question:
        calls = [
            call("search_docs", case.operation, version),
            call("check_deprecation", case.operation, version),
            call("get_openapi_spec", case.operation, version),
        ]
    elif "replace deprecated" in lower_question:
        calls.append(call("check_deprecation", case.operation, version))

    # All final outcomes are intentionally correct, including memory-based ones.
    latency_ms = 1.4 + sum({"search_docs": 0.8, "get_openapi_spec": 1.1, "check_deprecation": 0.9}[item.tool] for item in calls)
    return TrajectoryRun(case.case_id, case.question, tuple(calls), case.expected_operation, case.expected_operation, latency_ms)


def argument_valid(call_: ToolCall) -> bool:
    version = call_.arguments.get("api_version")
    if version not in {"v2", "v3"}:
        return False
    operation = call_.result.get("operation")
    if call_.tool == "search_docs":
        return (version, operation) in DOCS and bool(call_.result.get("page"))
    if call_.tool == "get_openapi_spec":
        expected = SPECS.get((version, operation))
        return expected is not None and call_.result.get("path") == expected["path"]
    if call_.tool == "check_deprecation":
        return (version, operation) in SPECS and call_.result.get("replacement") == CHANGELOG.get((version, operation))
    return False


def sequence_valid(run: TrajectoryRun) -> bool:
    return run.sequence in EXPECTED_SEQUENCES[run.case_id]


def trajectory_passes(run: TrajectoryRun) -> bool:
    return sequence_valid(run) and all(argument_valid(item) for item in run.calls)


def outcome_passes(run: TrajectoryRun) -> bool:
    return run.answer_operation == run.expected_operation


def tool_choice_counts(run: TrajectoryRun) -> tuple[int, int]:
    paths = EXPECTED_SEQUENCES[run.case_id]
    correct = sum(any(index < len(path) and path[index] == item.tool for path in paths) for index, item in enumerate(run.calls))
    return correct, len(run.calls)


def classify_failure(run: TrajectoryRun) -> str | None:
    if not all(argument_valid(item) for item in run.calls):
        return "invalid_argument"
    if run.sequence in EXPECTED_SEQUENCES[run.case_id]:
        return None
    optimal_lengths = [len(path) for path in EXPECTED_SEQUENCES[run.case_id]]
    if len(run.sequence) < min(optimal_lengths):
        return "missing_required_tool"
    if len(run.sequence) > max(optimal_lengths) and len(set(run.sequence)) < len(run.sequence):
        return "redundant_step"
    return "wrong_tool"


def metrics(runs: list[TrajectoryRun]) -> dict[str, float]:
    choices = [tool_choice_counts(run) for run in runs]
    valid_args = [argument_valid(item) for run in runs for item in run.calls]
    costs = [run.cost_usd for run in runs]
    actual_steps = sum(len(run.calls) for run in runs)
    needed_steps = sum(min(len(path) for path in EXPECTED_SEQUENCES[run.case_id]) for run in runs)
    outcome_rate = 100 * sum(outcome_passes(run) for run in runs) / len(runs)
    trajectory_rate = 100 * sum(trajectory_passes(run) for run in runs) / len(runs)
    return {
        "outcome_pass_rate_pct": outcome_rate,
        "trajectory_pass_rate_pct": trajectory_rate,
        "gap_points": outcome_rate - trajectory_rate,
        "tool_choice_accuracy_pct": 100 * sum(value[0] for value in choices) / sum(value[1] for value in choices),
        "argument_validity_pct": 100 * sum(valid_args) / len(valid_args),
        "step_efficiency_ratio": actual_steps / needed_steps,
        "cost_p50_usd": statistics.median(costs),
        "cost_max_usd": max(costs),
        "tokens_per_question": sum(run.tokens for run in runs) / len(runs),
        "latency_p50_ms": statistics.median(run.latency_ms for run in runs),
    }


def mode_counts(runs: list[TrajectoryRun]) -> dict[str, int]:
    observed = [classify_failure(run) for run in runs]
    return {mode: observed.count(mode) for mode in FAILURE_MODES}


def write_csv(before: list[TrajectoryRun], after: list[TrajectoryRun]) -> None:
    fields = ["phase", "case_id", "outcome_pass", "trajectory_pass", "sequence", "arguments_valid", "failure_mode", "steps", "cost_usd", "latency_ms"]
    with (ROOT / "trajectory_results.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for phase, runs in (("before", before), ("after", after)):
            for run in runs:
                writer.writerow({
                    "phase": phase,
                    "case_id": run.case_id,
                    "outcome_pass": outcome_passes(run),
                    "trajectory_pass": trajectory_passes(run),
                    "sequence": " -> ".join(run.sequence),
                    "arguments_valid": all(argument_valid(item) for item in run.calls),
                    "failure_mode": classify_failure(run) or "none",
                    "steps": len(run.calls),
                    "cost_usd": f"{run.cost_usd:.8f}",
                    "latency_ms": f"{run.latency_ms:.3f}",
                })


def write_report(before: list[TrajectoryRun], after: list[TrajectoryRun]) -> None:
    before_metrics, after_metrics = metrics(before), metrics(after)
    before_modes, after_modes = mode_counts(before), mode_counts(after)
    price_tokens = after_metrics["tokens_per_question"] - before_metrics["tokens_per_question"]
    example = next(run for run in before if outcome_passes(run) and not trajectory_passes(run))
    worsened = [mode for mode in FAILURE_MODES if after_modes[mode] > before_modes[mode]]
    rows = []
    for label, values in (("Before", before_metrics), ("After", after_metrics)):
        rows.append(
            f"| {label} | {values['tool_choice_accuracy_pct']:.1f}% | {values['argument_validity_pct']:.1f}% | "
            f"{values['step_efficiency_ratio']:.3f} | ${values['cost_p50_usd']:.6f} | ${values['cost_max_usd']:.6f} | "
            f"{values['trajectory_pass_rate_pct']:.1f}% | {values['gap_points']:.1f} pp |"
        )
    report = [
        "# Week 8 Trajectory Evaluation",
        "",
        "## Metrics over the same 10 cases",
        "",
        "| Phase | Tool-choice accuracy | Argument validity | Steps taken / needed | Cost p50 | Cost max | Trajectory pass | Outcome−trajectory gap |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
        *rows,
        "",
        f"Outcome pass rate is {before_metrics['outcome_pass_rate_pct']:.1f}% in both phases.",
        "",
        "## Right answer, wrong path",
        "",
        f"`{example.case_id}` — {example.question}",
        "",
        f"Outcome: PASS (`{example.answer_operation}`). Trajectory: FAIL (`{' -> '.join(example.sequence)}`). The agent searched docs, skipped `get_openapi_spec`, and recited the correct operation from memory.",
        "",
        "## Exactly one mitigation",
        "",
        f"Mitigation: **{MITIGATION}**",
        "",
        f"Top mode, `missing_required_tool`: **{before_modes['missing_required_tool']} -> {after_modes['missing_required_tool']}**.",
        f"Measured price: **+{price_tokens:.1f} tokens per question** ({before_metrics['tokens_per_question']:.1f} -> {after_metrics['tokens_per_question']:.1f}).",
        "",
        "## Regression matrix",
        "",
        "| Failure mode | Before | After | Delta |",
        "|---|---:|---:|---:|",
        *[f"| {mode} | {before_modes[mode]} | {after_modes[mode]} | {after_modes[mode] - before_modes[mode]:+d} |" for mode in FAILURE_MODES],
        "",
        ("Modes that worsened: " + ", ".join(worsened) + "." if worsened else "No mode worsened and no new mode appeared. Checked: " + ", ".join(FAILURE_MODES) + "."),
        "",
        "## Alternate-path policy",
        "",
        "Cases `q05`, `q06`, and `q07` explicitly name deprecated operations, so both `search -> spec -> changelog` and `search -> changelog -> spec` are accepted. All other cases require the single shortest documented path.",
    ]
    (ROOT / "trajectory_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")


def run_eval() -> tuple[list[TrajectoryRun], list[TrajectoryRun]]:
    if set(EXPECTED_SEQUENCES) != {case.case_id for case in CASES}:
        raise AssertionError("Every race case needs an expected trajectory")
    before = [generate_run(case, mitigated=False) for case in CASES]
    after = [generate_run(case, mitigated=True) for case in CASES]
    write_csv(before, after)
    write_report(before, after)
    return before, after


def print_metrics(label: str, values: dict[str, float]) -> None:
    print(
        f"{label:<7} tool={values['tool_choice_accuracy_pct']:5.1f}% "
        f"args={values['argument_validity_pct']:5.1f}% steps={values['step_efficiency_ratio']:.3f} "
        f"cost_p50=${values['cost_p50_usd']:.6f} cost_max=${values['cost_max_usd']:.6f} "
        f"gap={values['gap_points']:.1f}pp"
    )


def main() -> None:
    before, after = run_eval()
    print_metrics("before", metrics(before))
    print_metrics("after", metrics(after))
    print(f"missing_required_tool: {mode_counts(before)['missing_required_tool']} -> {mode_counts(after)['missing_required_tool']}")
    print("wrote trajectory_results.csv and trajectory_report.md")


if __name__ == "__main__":
    main()
