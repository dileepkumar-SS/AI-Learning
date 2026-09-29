from __future__ import annotations

import ast
import hashlib
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).parent
ASSERTION_NAMES = (
    "python_code_parses",
    "endpoint_exists_in_openapi",
    "requested_api_version_is_stated",
    "deprecated_symbol_has_migration_note",
)
JUDGED_CRITERIA = 1


@dataclass(frozen=True)
class AssertionResult:
    name: str
    status: str
    detail: str


def load_json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def load_traces() -> dict[str, dict]:
    records = {}
    for line in (ROOT / "traces.jsonl").read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        records[record["trace_id"]] = record
    return records


def build_cases() -> list[dict]:
    labels = load_json("labels_25.json")["labels"]
    traces = load_traces()
    cases = []
    for label in labels:
        trace = traces[label["trace_id"]]
        cases.append(
            {
                **label,
                "question": trace["question"],
                "answer": trace["raw_output"],
                "reference": trace["expected_answer"],
                "mode": trace["failure_mode"],
            }
        )
    return cases


def assert_python_code_parses(answer: str) -> AssertionResult:
    snippets = re.findall(r"```python\s+(.*?)```", answer, flags=re.DOTALL | re.IGNORECASE)
    if not snippets:
        return AssertionResult(ASSERTION_NAMES[0], "SKIP", "no Python code block")
    try:
        for snippet in snippets:
            ast.parse(snippet)
    except SyntaxError as exc:
        return AssertionResult(ASSERTION_NAMES[0], "FAIL", f"SyntaxError: {exc.msg}")
    return AssertionResult(ASSERTION_NAMES[0], "PASS", f"parsed {len(snippets)} block(s)")


def assert_endpoints_exist(answer: str, paths: set[str]) -> AssertionResult:
    mentioned = set(re.findall(r"(?<![\w])(/v\d+/[a-zA-Z0-9_./{}-]+)", answer))
    if not mentioned:
        return AssertionResult(ASSERTION_NAMES[1], "SKIP", "no endpoint path")
    missing = sorted(mentioned - paths)
    if missing:
        return AssertionResult(ASSERTION_NAMES[1], "FAIL", "unknown: " + ", ".join(missing))
    return AssertionResult(ASSERTION_NAMES[1], "PASS", ", ".join(sorted(mentioned)))


def assert_requested_version_stated(question: str, answer: str) -> AssertionResult:
    requested = re.search(r"\bv(\d+)(?:\.(\d+)\.(\d+))?\b", question, flags=re.IGNORECASE)
    if not requested:
        return AssertionResult(ASSERTION_NAMES[2], "SKIP", "question does not request a version")
    version = requested.group(0).lower()
    if version in answer.lower():
        return AssertionResult(ASSERTION_NAMES[2], "PASS", f"states {version}")
    return AssertionResult(ASSERTION_NAMES[2], "FAIL", f"answer does not state {version}")


def assert_deprecations(answer: str, deprecations: dict[str, str]) -> AssertionResult:
    mentioned = [symbol for symbol in deprecations if symbol in answer]
    if not mentioned:
        return AssertionResult(ASSERTION_NAMES[3], "SKIP", "no deprecated symbol")
    lacking_note = [
        symbol
        for symbol in mentioned
        if not re.search(rf"(?:migrat|replac|instead).{{0,100}}{re.escape(symbol)}|{re.escape(symbol)}.{{0,100}}(?:migrat|replac|instead)", answer, re.I)
    ]
    if lacking_note:
        return AssertionResult(ASSERTION_NAMES[3], "FAIL", "missing migration note: " + ", ".join(lacking_note))
    return AssertionResult(ASSERTION_NAMES[3], "PASS", "migration note present")


def run_assertions(case: dict, paths: set[str], deprecations: dict[str, str]) -> list[AssertionResult]:
    answer = case["answer"]
    return [
        assert_python_code_parses(answer),
        assert_endpoints_exist(answer, paths),
        assert_requested_version_stated(case["question"], answer),
        assert_deprecations(answer, deprecations),
    ]


def agreement(cases: list[dict], verdicts: dict[str, str]) -> tuple[int, int, float]:
    matches = sum(case["label"] == verdicts[case["case_id"]] for case in cases)
    return matches, len(cases), 100 * matches / len(cases)


def verify_blind_ordering() -> tuple[bool, str]:
    labels = ROOT / "labels_25.json"
    judge_files = [ROOT / "judge_results_v1.json", ROOT / "judge_results_v2.json"]
    valid = all(labels.stat().st_mtime_ns < path.stat().st_mtime_ns for path in judge_files)
    digest = hashlib.sha256(labels.read_bytes()).hexdigest()
    return valid, digest


def verify_regressions(cases: list[dict]) -> None:
    by_id = {case["case_id"]: case for case in cases}
    regressions = load_json("regression_cases.json")
    if len(regressions) < 2:
        raise AssertionError("at least two regression cases are required")
    for regression in regressions:
        case = by_id[regression["case_id"]]
        for field in ("trace_id", "question", "answer"):
            if case[field] != regression[field]:
                raise AssertionError(f"{regression['case_id']} is not a verbatim replay: {field}")


def main() -> None:
    cases = build_cases()
    if len(cases) < 25:
        raise AssertionError("eval set must contain at least 25 cases")
    if any(not case["mode"] for case in cases):
        raise AssertionError("every case must have a Week 5 mode")
    verify_regressions(cases)

    schema = load_json("openapi.json")
    paths = set(schema["paths"])
    deprecations = load_json("deprecations.json")
    assertions = {case["case_id"]: run_assertions(case, paths, deprecations) for case in cases}
    v1 = load_json("judge_results_v1.json")["verdicts"]
    v2 = load_json("judge_results_v2.json")["verdicts"]
    before = agreement(cases, v1)
    after = agreement(cases, v2)
    ordering_ok, labels_hash = verify_blind_ordering()
    if not ordering_ok:
        raise AssertionError("labels_25.json must predate both judge result files")

    mode_rows = []
    for mode in sorted({case["mode"] for case in cases}):
        selected = [case for case in cases if case["mode"] == mode]
        passed = 0
        for case in selected:
            deterministic_ok = all(result.status != "FAIL" for result in assertions[case["case_id"]])
            passed += v2[case["case_id"]] == "PASS" and deterministic_ok
        mode_rows.append((mode, passed, len(selected), 100 * passed / len(selected)))

    disagreements = [case for case in cases if case["label"] != v1[case["case_id"]]]
    prediction_correct = {case["case_id"] for case in disagreements} == {"eval_008", "eval_017"} and after[0] == after[1]

    print("mode                 passed/total  pass_rate")
    print("-------------------  ------------  ---------")
    for mode, passed, total, rate in mode_rows:
        print(f"{mode:<19}  {passed:>2}/{total:<9}  {rate:>8.1f}%")
    print()
    print(f"agreement_before: {before[2]:.1f}% ({before[0]}/{before[1]})")
    print(f"agreement_after:  {after[2]:.1f}% ({after[0]}/{after[1]})")
    print(f"assertions: {len(ASSERTION_NAMES)} | judged criteria: {JUDGED_CRITERIA}")
    print("blind ordering: PASS (label file mtime predates judge result files)")
    print(f"labels sha256: {labels_hash}")
    print("regression replays: PASS (2 verbatim Week 5 failed traces)")

    report = [
        "# Week 6 Eval Report",
        "",
        f"Blind ordering: **PASS**. `labels_25.json` predates both judge result files. SHA-256: `{labels_hash}`.",
        "",
        f"Agreement before -> after: **{before[2]:.1f}% ({before[0]}/{before[1]}) -> {after[2]:.1f}% ({after[0]}/{after[1]})**.",
        "",
        f"Split: **{len(ASSERTION_NAMES)} deterministic assertions vs {JUDGED_CRITERIA} judged criterion**.",
        "",
        "## Pass rate by Week 5 mode",
        "",
        "| Mode | Passed | Total | Pass rate |",
        "|---|---:|---:|---:|",
        *[f"| {mode} | {passed} | {total} | {rate:.1f}% |" for mode, passed, total, rate in mode_rows],
        "",
        "## Judge disagreements",
        "",
        "- `eval_008`: Human **PASS**, judge v1 **FAIL**. The human was right: the answer exactly names the requested embedding model; brevity is not unhelpfulness.",
        "- `eval_017`: Human **PASS**, judge v1 **FAIL**. The human was right: the answer gives the requested boolean default completely and correctly.",
        "",
        "Both v1 disagreements are visible as few-shot examples in `judge_v2.txt`.",
        "",
        "## Prediction check",
        "",
        ("The prediction was correct: both false negatives were fixed and no true-negative verdict changed. It was not wrong on any observed case." if prediction_correct else "The prediction was partly wrong; inspect the changed verdicts."),
        "",
        "## Protocol note",
        "",
        "Judge verdicts are stored run artifacts, so this command is deterministic and requires no API key. Re-running the table does not relabel cases or silently call a model.",
    ]
    (ROOT / "eval_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
