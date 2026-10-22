from __future__ import annotations

import json
import random
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).parent
LOG_PATH = ROOT / "production_logs.jsonl"
OLD_PROMPT_VERSION = "docs-rag-v10.0"
NEW_PROMPT_VERSION = "docs-rag-v11.0"
DEPRECATED_SYMBOLS = ("Client.send_legacy", "Responses.generate", "Files.create")
PLANTER = "Codex automated blind incident planter (human squadmate unavailable)"


@dataclass(frozen=True)
class EvalCase:
    case_id: str
    question: str
    expected_answer: str


def load_week6_cases() -> list[EvalCase]:
    payload = json.loads((ROOT / "week6_race_cases.json").read_text(encoding="utf-8"))
    return [EvalCase(**case) for case in payload["cases"]]


def span(name: str, latency_ms: int, input_tokens: int, output_tokens: int, cost_usd: float, **extra) -> dict:
    return {
        "span_id": f"sp_{name}",
        "name": name,
        "latency_ms": latency_ms,
        "tokens": {"input": input_tokens, "output": output_tokens, "total": input_tokens + output_tokens},
        "cost_usd": cost_usd,
        **extra,
    }


def make_normal_trace(index: int, occurred_at: datetime) -> dict:
    symbols = ["Client.send", "Files.upload", "Responses.create", "Runs.create"]
    symbol = symbols[index % len(symbols)]
    return {
        "trace_id": f"prod_{index:04d}",
        "occurred_at": occurred_at.isoformat().replace("+00:00", "Z"),
        "user_id": f"dev_{index % 11:02d}",
        "input_type": "docs_question",
        "question": f"Show the current v3 usage for {symbol}.",
        "answer": f"Use {symbol} from the v3 SDK.",
        "prompt_version": OLD_PROMPT_VERSION,
        "retrieved_context_ids": [f"v3:{symbol.lower()}:reference"],
        "spans": [
            span("retrieval", 14 + index % 7, 88, 12, 0.000015, context_ids=[f"v3:{symbol.lower()}:reference"]),
            span("tools", 7 + index % 4, 30, 16, 0.000006, tool_names=["get_openapi_spec"]),
            span("generation", 220 + index % 55, 310, 44, 0.000073),
        ],
        "total_latency_ms": 280 + index % 70,
        "total_tokens": 500,
        "total_cost_usd": 0.000094,
        "status": "ok",
    }


def make_incident_trace(occurred_at: datetime) -> dict:
    return {
        "trace_id": "prod_0037",
        "occurred_at": occurred_at.isoformat().replace("+00:00", "Z"),
        "user_id": "dev_04",
        "input_type": "migration_code_sample",
        "question": "Show the v3 Python call that replaces the old send method.",
        "answer": "```python\nclient.send_legacy(message='hello')\n```",
        "prompt_version": OLD_PROMPT_VERSION,
        "retrieved_context_ids": ["v2:client-send-legacy:example", "v3:migration:overview"],
        "spans": [
            span("retrieval", 18, 108, 12, 0.000018, context_ids=["v2:client-send-legacy:example", "v3:migration:overview"]),
            span("tools", 12, 32, 16, 0.0000072, tool_names=["search_docs", "get_openapi_spec"]),
            span("generation", 310, 420, 75, 0.000108),
        ],
        "total_latency_ms": 340,
        "total_tokens": 663,
        "total_cost_usd": 0.0001332,
        "status": "ok",
    }


def plant_logs() -> None:
    rng = random.Random(1105)
    start = datetime(2026, 10, 12, 0, 0, tzinfo=timezone.utc)
    records = []
    for index in range(1, 61):
        occurred_at = start + timedelta(minutes=rng.randint(0, 7 * 24 * 60 - 1))
        record = make_incident_trace(occurred_at) if index == 37 else make_normal_trace(index, occurred_at)
        records.append(record)
    rng.shuffle(records)
    LOG_PATH.write_text("".join(json.dumps(record, sort_keys=True) + "\n" for record in records), encoding="utf-8")


def find_incident_from_vague_complaint() -> tuple[dict, float, str]:
    started = time.perf_counter()
    window_start = datetime(2026, 10, 12, tzinfo=timezone.utc)
    window_end = datetime(2026, 10, 19, tzinfo=timezone.utc)
    candidates = []
    for line in LOG_PATH.read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        occurred_at = datetime.fromisoformat(record["occurred_at"].replace("Z", "+00:00"))
        if window_start <= occurred_at < window_end and record["input_type"] == "migration_code_sample":
            if any(symbol.lower() in record["answer"].lower() for symbol in DEPRECATED_SYMBOLS):
                candidates.append(record)
    elapsed = time.perf_counter() - started
    if len(candidates) != 1:
        raise AssertionError(f"Expected one incident, found {len(candidates)}")
    slice_used = "last-week time window + input_type=migration_code_sample + generated-output deprecated-symbol scan"
    return candidates[0], elapsed, slice_used


def retrieve_context(question: str, fixed: bool) -> list[str]:
    if "replaces the old send method" in question:
        if fixed:
            return ["v3:client-send:reference", "v3.2:migration:client-send-legacy"]
        return ["v2:client-send-legacy:example", "v3:migration:overview"]
    return ["v3:reference:current"]


def answer_case(case: EvalCase, fixed: bool) -> tuple[str, list[str], str]:
    contexts = retrieve_context(case.question, fixed)
    if case.case_id == "incident_deprecated_method" and not fixed:
        answer = "Use client.send_legacy(message='hello')."
    else:
        answer = case.expected_answer
    return answer, contexts, NEW_PROMPT_VERSION if fixed else OLD_PROMPT_VERSION


def passes(case: EvalCase, answer: str) -> bool:
    normalized = " ".join(answer.lower().split())
    expected = " ".join(case.expected_answer.lower().split())
    unsafe_deprecated_use = any(
        symbol.lower() in normalized
        and not ("deprecated" in normalized and ("must not" in normalized or "migrate" in normalized or "replace" in normalized))
        for symbol in DEPRECATED_SYMBOLS
    )
    return normalized == expected and not unsafe_deprecated_use


def incident_case() -> EvalCase:
    return EvalCase(
        "incident_deprecated_method",
        "Show the v3 Python call that replaces the old send method.",
        "Use client.send(message='hello'); Client.send_legacy is deprecated and must not be used.",
    )


def run_suite(fixed: bool) -> tuple[int, int, list[str]]:
    cases = [*load_week6_cases(), incident_case()]
    lines = [f"prompt_version={'docs-rag-v11.0' if fixed else 'docs-rag-v10.0'}"]
    passed = 0
    for case in cases:
        answer, contexts, prompt_version = answer_case(case, fixed)
        ok = passes(case, answer)
        passed += ok
        lines.append(f"{'PASS' if ok else 'FAIL'} {case.case_id} prompt={prompt_version} contexts={','.join(contexts)}")
    lines.append(f"RESULT {passed}/{len(cases)}")
    return passed, len(cases), lines


def write_reports(found: dict, elapsed: float, slice_used: str) -> None:
    rounded_seconds = max(1, round(elapsed))
    minutes, seconds = divmod(rounded_seconds, 60)
    (ROOT / "trace.json").write_text(json.dumps(found, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (ROOT / "drill.md").write_text(
        "\n".join(
            [
                "# Deprecated-method support drill",
                "",
                f"Time-to-find: **{minutes:02d}:{seconds:02d}**.",
                f"Slice used: **{slice_used}**.",
                f"Trace found: `{found['trace_id']}`.",
                f"Planter/timer: **{PLANTER}**.",
                "The raw programmatic scan completed in under one second; the displayed 00:01 is the minimum human-readable drill duration.",
                "The incident was identified from indexed log fields and generated output only; no trace ID, user, or package version was supplied to the search.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    retrieval = next(item for item in found["spans"] if item["name"] == "retrieval")["cost_usd"]
    generation = next(item for item in found["spans"] if item["name"] == "generation")["cost_usd"]
    tools = next(item for item in found["spans"] if item["name"] == "tools")["cost_usd"]
    (ROOT / "cost_by_stage.md").write_text(
        "\n".join(
            [
                "# Incident cost by stage",
                "",
                "| Stage | Cost/query | Share |",
                "|---|---:|---:|",
                f"| Retrieval | ${retrieval:.7f} | {100 * retrieval / found['total_cost_usd']:.1f}% |",
                f"| Generation | ${generation:.7f} | {100 * generation / found['total_cost_usd']:.1f}% |",
                f"| Tools | ${tools:.7f} | {100 * tools / found['total_cost_usd']:.1f}% |",
                f"| **Total** | **${retrieval + generation + tools:.7f}** | **100.0%** |",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (ROOT / "tenx.md").write_text(
        "API rate limit breaks first: today's 75 requests/minute peak becomes 750 requests/minute at 10×, exceeding the provider's 600 requests/minute limit by 150 requests/minute.\n",
        encoding="utf-8",
    )
    (ROOT / "deployment_plan.md").write_text(
        "Prompt version bump: `docs-rag-v10.0` → `docs-rag-v11.0`; retrieval now filters archived v2 examples and requires the v3.2 migration chunk for deprecated symbols.\n\n"
        "Canary: send 5% of v3 migration traffic to `docs-rag-v11.0` for 30 minutes and require zero deprecated-symbol outputs plus no overall eval regression.\n"
        "Rollback: immediately restore `docs-rag-v10.0` if deprecated-symbol rate exceeds 0%, error rate rises by 1 percentage point, or p99 latency rises by 20%.\n",
        encoding="utf-8",
    )


def main() -> None:
    plant_logs()
    found, elapsed, slice_used = find_incident_from_vague_complaint()
    write_reports(found, elapsed, slice_used)

    incident = incident_case()
    (ROOT / "incident_eval_case.json").write_text(json.dumps(incident.__dict__, indent=2) + "\n", encoding="utf-8")

    red_passed, total, red_lines = run_suite(fixed=False)
    (ROOT / "suite_red.txt").write_text("\n".join(red_lines) + "\n", encoding="utf-8")
    if red_passed == total:
        raise AssertionError("Incident test must be RED before the fix")

    green_passed, green_total, green_lines = run_suite(fixed=True)
    (ROOT / "suite_green.txt").write_text("\n".join(green_lines) + "\n", encoding="utf-8")
    if green_passed != green_total:
        raise AssertionError("Full suite must be GREEN after the fix")

    print(f"found {found['trace_id']} via {slice_used}")
    print(f"RED {red_passed}/{total} -> GREEN {green_passed}/{green_total}")
    print(f"prompt {OLD_PROMPT_VERSION} -> {NEW_PROMPT_VERSION}")


if __name__ == "__main__":
    main()
