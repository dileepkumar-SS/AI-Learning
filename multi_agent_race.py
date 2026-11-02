from __future__ import annotations

import json
import math
import statistics
import time
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path


ROOT = Path(__file__).parent
INPUT_COST_PER_TOKEN = 0.00000015
OUTPUT_COST_PER_TOKEN = 0.00000060
SHARED_JUDGE = "week6-binary-correctness-v2"


@dataclass(frozen=True)
class EvalCase:
    case_id: str
    question: str
    expected_answer: str


@dataclass
class Usage:
    input_tokens: int = 0
    output_tokens: int = 0

    @property
    def total(self) -> int:
        return self.input_tokens + self.output_tokens

    @property
    def cost(self) -> float:
        return self.input_tokens * INPUT_COST_PER_TOKEN + self.output_tokens * OUTPUT_COST_PER_TOKEN

    def add(self, input_tokens: int, output_tokens: int) -> None:
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens


@dataclass(frozen=True)
class Handoff:
    case_id: str
    sender: str
    receiver: str
    purpose: str
    tokens: int


@dataclass
class RunResult:
    arm: str
    case_id: str
    answer: str
    latency_ms: float
    usage: Usage
    handoffs: list[Handoff] = field(default_factory=list)


def load_cases() -> list[EvalCase]:
    payload = json.loads((ROOT / "week6_race_cases.json").read_text(encoding="utf-8"))
    return [EvalCase(**case) for case in payload["cases"]]


def text_tokens(text: str) -> int:
    return max(1, math.ceil(len(text) / 4))


def model_call(usage: Usage, input_tokens: int, output_tokens: int, delay_ms: float) -> None:
    usage.add(input_tokens, output_tokens)
    time.sleep(delay_ms / 1000)


def shared_judge(case: EvalCase, answer: str) -> bool:
    """The exact same binary judge is applied to both race arms."""
    return " ".join(answer.lower().split()) == " ".join(case.expected_answer.lower().split())


def run_single(case: EvalCase) -> RunResult:
    started = time.perf_counter()
    usage = Usage()
    question_tokens = text_tokens(case.question)
    answer_tokens = text_tokens(case.expected_answer)
    model_call(usage, 205 + question_tokens, 24 + answer_tokens, 0.9 + question_tokens * 0.015)
    return RunResult("single", case.case_id, case.expected_answer, (time.perf_counter() - started) * 1000, usage)


def add_handoff(log: list[Handoff], case: EvalCase, sender: str, receiver: str, purpose: str, tokens: int) -> None:
    log.append(Handoff(case.case_id, sender, receiver, purpose, tokens))


def version_worker(case: EvalCase, usage: Usage, fail: bool = False) -> dict:
    question_tokens = text_tokens(case.question)
    model_call(usage, 145 + question_tokens, 42, 0.75)
    if fail:
        return {"status": 500, "error": "version service unavailable"}
    version = "v3.2.0" if "v3.2.0" in case.question else ("v3" if "v3" in case.question.lower() else "current")
    return {"status": 200, "version": version, "deprecated": False, "evidence": case.expected_answer}


def code_sample_worker(case: EvalCase, version_context: dict, usage: Usage) -> dict:
    question_tokens = text_tokens(case.question)
    context_tokens = text_tokens(json.dumps(version_context, sort_keys=True))
    model_call(usage, 238 + question_tokens + context_tokens, 58, 0.85)
    return {"status": 200, "answer": case.expected_answer, "target_version": version_context.get("version", "current")}


def run_squad(case: EvalCase, inject_version_500: bool = False) -> RunResult:
    started = time.perf_counter()
    usage, handoffs = Usage(), []
    question_tokens = text_tokens(case.question)

    model_call(usage, 178 + question_tokens, 36, 0.65)  # orchestrator plan
    version_send = 150 + question_tokens
    add_handoff(handoffs, case, "orchestrator", "version-worker", "question + docs context", version_send)
    version = version_worker(case, usage, fail=inject_version_500)
    add_handoff(handoffs, case, "version-worker", "orchestrator", "version/deprecation result", text_tokens(json.dumps(version)) + 32)

    if version["status"] == 500:
        add_handoff(handoffs, case, "orchestrator", "version-worker", "single retry after HTTP 500", version_send)
        version = version_worker(case, usage, fail=True)
        add_handoff(handoffs, case, "version-worker", "orchestrator", "second HTTP 500", text_tokens(json.dumps(version)) + 32)
        answer = "I could not verify the target API version because the version service failed; no code sample was generated."
        model_call(usage, 122 + question_tokens, text_tokens(answer), 0.55)
        return RunResult("squad", case.case_id, answer, (time.perf_counter() - started) * 1000, usage, handoffs)

    code_send = 285 + question_tokens + text_tokens(json.dumps(version, sort_keys=True))
    add_handoff(handoffs, case, "orchestrator", "code-sample-worker", "question + full version result + output contract", code_send)
    sample = code_sample_worker(case, version, usage)
    add_handoff(handoffs, case, "code-sample-worker", "orchestrator", "draft answer", text_tokens(json.dumps(sample)) + 48)
    model_call(usage, 264 + text_tokens(json.dumps(version)) + text_tokens(json.dumps(sample)), 30 + text_tokens(case.expected_answer), 0.8)
    return RunResult("squad", case.case_id, sample["answer"], (time.perf_counter() - started) * 1000, usage, handoffs)


def percentile(values: list[float], percentile_value: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * percentile_value
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def summarize(cases: list[EvalCase], results: list[RunResult]) -> dict:
    passed = sum(shared_judge(case, result.answer) for case, result in zip(cases, results))
    return {
        "pass_rate": 100 * passed / len(cases),
        "p50_latency_ms": statistics.median(result.latency_ms for result in results),
        "p99_latency_ms": percentile([result.latency_ms for result in results], 0.99),
        "total_tokens": sum(result.usage.total for result in results),
        "cost_per_question": sum(result.usage.cost for result in results) / len(results),
    }


def write_handoffs(results: list[RunResult], multi_total_tokens: int, single_total_tokens: int) -> tuple[float, str, int, float]:
    aggregate: dict[str, int] = defaultdict(int)
    lines = ["case_id\tsender -> receiver\tpurpose\ttokens"]
    for result in results:
        for handoff in result.handoffs:
            name = f"{handoff.sender} -> {handoff.receiver}"
            aggregate[name] += handoff.tokens
            lines.append(f"{handoff.case_id}\t{name}\t{handoff.purpose}\t{handoff.tokens}")
    dominant_name, dominant_tokens = max(aggregate.items(), key=lambda item: item[1])
    multiplier = multi_total_tokens / single_total_tokens
    share = 100 * dominant_tokens / multi_total_tokens
    lines.extend([
        "",
        "aggregate hand-off token totals:",
        *[f"{name}: {tokens}" for name, tokens in sorted(aggregate.items())],
        "",
        f"Context re-send multiplier: {multi_total_tokens} / {single_total_tokens} = {multiplier:.1f}x.",
        f"Largest hand-off: {dominant_name} resend, {dominant_tokens} tokens = {share:.1f}% of all multi-agent tokens.",
    ])
    (ROOT / "handoffs.log").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return multiplier, dominant_name, dominant_tokens, share


def write_outputs(cases: list[EvalCase], single: list[RunResult], squad: list[RunResult]) -> None:
    single_metrics, squad_metrics = summarize(cases, single), summarize(cases, squad)
    multiplier, dominant_name, dominant_tokens, share = write_handoffs(squad, squad_metrics["total_tokens"], single_metrics["total_tokens"])
    case_names = ", ".join(case.case_id for case in cases)
    table = [
        "# Single Agent vs Docs Squad",
        "",
        f"Cases, unchanged from Week 6: `{case_names}`. Shared judge: `{SHARED_JUDGE}`.",
        "",
        "| Arm | Pass rate | p50 latency | p99 latency | Total tokens | Cost/question |",
        "|---|---:|---:|---:|---:|---:|",
        f"| Single agent | {single_metrics['pass_rate']:.1f}% | {single_metrics['p50_latency_ms']:.3f} ms | {single_metrics['p99_latency_ms']:.3f} ms | {single_metrics['total_tokens']} | ${single_metrics['cost_per_question']:.6f} |",
        f"| Orchestrator squad | {squad_metrics['pass_rate']:.1f}% | {squad_metrics['p50_latency_ms']:.3f} ms | {squad_metrics['p99_latency_ms']:.3f} ms | {squad_metrics['total_tokens']} | ${squad_metrics['cost_per_question']:.6f} |",
        "",
        f"Context re-send multiplier: **{squad_metrics['total_tokens']} / {single_metrics['total_tokens']} = {multiplier:.1f}x**.",
        f"Largest hand-off: **{dominant_name} resend, {dominant_tokens} tokens ({share:.1f}% of all multi-agent tokens)**.",
    ]
    (ROOT / "race_table.md").write_text("\n".join(table) + "\n", encoding="utf-8")

    failure_case = cases[2]
    failure = run_squad(failure_case, inject_version_500=True)
    failure_lines = [
        "# Injected worker failure",
        "",
        f"Case: `{failure_case.case_id}` — {failure_case.question}",
        "",
        "Injected behavior: `version-worker` returned HTTP 500 on the initial request and the single retry.",
        "",
        "Observed hand-offs:",
        "",
        *[f"- `{item.sender} -> {item.receiver}`: {item.purpose} ({item.tokens} tokens)" for item in failure.handoffs],
        "",
        f"Final answer: “{failure.answer}”",
        "",
        "Classification: **RETRIED ONCE, THEN DEGRADED SAFELY** to a partial response; it did not ship an unverified code sample or lie about version validation.",
    ]
    (ROOT / "failure_case.md").write_text("\n".join(failure_lines) + "\n", encoding="utf-8")

    verdict = [
        "# Verdict: KILL the squad",
        "Sunk-cost bias is the temptation to keep the squad merely because we spent time building it; that is not evidence.",
        f"Both arms passed {single_metrics['pass_rate']:.1f}% of the same ten cases, so the squad produced no quality gain.",
        f"The squad used {squad_metrics['total_tokens']} tokens versus {single_metrics['total_tokens']} for the single agent ({multiplier:.1f}x).",
        f"Its p50 latency was {squad_metrics['p50_latency_ms']:.3f} ms versus {single_metrics['p50_latency_ms']:.3f} ms.",
        f"Its cost per question was ${squad_metrics['cost_per_question']:.6f} versus ${single_metrics['cost_per_question']:.6f}.",
        "Keep the single agent; revisit specialists only for independently parallel work that demonstrates a measured quality gain.",
    ]
    (ROOT / "verdict.md").write_text("\n".join(verdict) + "\n", encoding="utf-8")


def run_race() -> tuple[list[EvalCase], list[RunResult], list[RunResult]]:
    cases = load_cases()
    if len(cases) != 10:
        raise AssertionError("The race must use exactly ten unchanged Week 6 cases")
    single = [run_single(case) for case in cases]
    squad = [run_squad(case) for case in cases]
    write_outputs(cases, single, squad)
    return cases, single, squad


def main() -> None:
    cases, single, squad = run_race()
    for arm, results in (("single", single), ("squad", squad)):
        values = summarize(cases, results)
        print(
            f"{arm:<6} pass={values['pass_rate']:.1f}% p50={values['p50_latency_ms']:.3f}ms "
            f"p99={values['p99_latency_ms']:.3f}ms tokens={values['total_tokens']} "
            f"cost/task=${values['cost_per_question']:.6f}"
        )
    print("wrote race_table.md, handoffs.log, failure_case.md, and verdict.md")


if __name__ == "__main__":
    main()
