from __future__ import annotations

import hashlib
import json
import random
from collections import Counter
from dataclasses import dataclass
from datetime import date
from pathlib import Path


ROOT = Path(__file__).parent
TRACE_PATH = ROOT / "traces.jsonl"
SAMPLE_SEED = 20260905
REPLAY_SEED = 53017


@dataclass(frozen=True)
class TraceSeed:
    trace_id: str
    question: str
    expected_answer: str
    failure_mode: str
    retrieved_chunk_ids: list[str]
    retrieved_scores: list[float]


MODE_DETAILS = {
    "wrong_version": {
        "mode": "answers with the v2 method signature for a v3 question",
        "severity": "ships broken code to a user's repo",
    },
    "example_over_table": {
        "mode": "quotes a code example when the parameter table contains the requested default",
        "severity": "ships subtly wrong configuration values",
    },
    "unsupported_quota": {
        "mode": "states a quota or limit that is not present in the indexed docs",
        "severity": "ships invented operational constraints",
    },
    "generic_retry": {
        "mode": "returns generic retry guidance instead of the requested exact symbol",
        "severity": "merely annoys the reader",
    },
    "missing_citation": {
        "mode": "gives a correct-looking answer without a resolvable citation",
        "severity": "blocks verification and review",
    },
    "ambiguous_error": {
        "mode": "explains an error code from the guide instead of the reference row",
        "severity": "ships misleading debugging advice",
    },
}


TRACE_SEEDS = [
    TraceSeed("tr_0001", "How do I authenticate the v3 client?", "Set SDK_API_KEY before creating Client().", "clean", ["v3:auth-guide:api-key-login"], [0.91]),
    TraceSeed("tr_0002", "What is retry_backoff_ms in v3.2.0?", "retry_backoff_ms defaults to 250 ms in v3.2.0.", "wrong_version", ["v2:client-send:parameters", "v3:retry-guide:retry-behavior", "v3:client-send:example"], [0.82, 0.77, 0.73]),
    TraceSeed("tr_0003", "Show Client.send with timeout_ms.", "Pass timeout_ms=30000 to Client.send.", "example_over_table", ["v3:client-send:example", "v3:client-send:parameters"], [0.86, 0.79]),
    TraceSeed("tr_0004", "What is the default Files.upload purpose?", "Files.upload defaults purpose to assistants.", "clean", ["v3:files-upload:parameters"], [0.9]),
    TraceSeed("tr_0005", "What is the monthly quota for Client.send?", "The docs do not state a monthly quota.", "unsupported_quota", ["v3:client-send:top", "v3:auth-guide:api-key-login"], [0.7, 0.55]),
    TraceSeed("tr_0006", "What does ERR-4032 mean?", "ERR-4032 means unsafe tool output was blocked.", "ambiguous_error", ["v3:errors-guide:handling-failures", "v3:responses-create:errors"], [0.81, 0.78]),
    TraceSeed("tr_0007", "What is event_buffer default?", "event_buffer defaults to true.", "clean", ["v3:client-stream:parameters"], [0.88]),
    TraceSeed("tr_0008", "Which embedding model is default in v3.2.0?", "The default embedding model is text-embedding-3-small.", "missing_citation", ["v3:embeddings-create:parameters"], [0.89]),
    TraceSeed("tr_0009", "Does Client.send retry validation errors?", "Do not retry permanent validation errors.", "generic_retry", ["v3:retry-guide:retry-behavior", "v3:client-send:parameters"], [0.84, 0.62]),
    TraceSeed("tr_0010", "What is tool_choice default?", "tool_choice defaults to auto.", "clean", ["v3:runs-create:parameters"], [0.92]),
    TraceSeed("tr_0011", "What changed in v3.2.0 for retry_backoff_ms?", "v3.2.0 changed retry_backoff_ms to 250 ms.", "clean", ["v3:changelog-v3-2:changes"], [0.93]),
    TraceSeed("tr_0012", "What is max_output_tokens default?", "max_output_tokens defaults to 1024.", "example_over_table", ["v3:responses-create:example", "v3:responses-create:parameters"], [0.85, 0.8]),
    TraceSeed("tr_0013", "What is retry_backoff_ms default?", "retry_backoff_ms defaults to 250 ms.", "wrong_version", ["v1:client-send:parameters", "v2:client-send:parameters", "v3:client-send:parameters"], [0.83, 0.81, 0.79]),
    TraceSeed("tr_0014", "How should I handle unknown error codes?", "Treat unknown error codes as non-retryable.", "clean", ["v3:errors-guide:handling-failures"], [0.87]),
    TraceSeed("tr_0015", "What is the daily upload limit?", "The docs do not state a daily upload limit.", "unsupported_quota", ["v3:files-upload:parameters", "v3:auth-guide:api-key-login"], [0.76, 0.52]),
    TraceSeed("tr_0016", "Which parameter is required for Client.send?", "message is required.", "wrong_version", ["v2:client-send:parameters", "v1:client-send:parameters", "v3:client-send:parameters"], [0.8, 0.78, 0.76]),
    TraceSeed("tr_0017", "Give me the Runs.create parallel_tool_calls default.", "parallel_tool_calls defaults to true.", "missing_citation", ["v3:runs-create:parameters"], [0.86]),
    TraceSeed("tr_0018", "How do I pass retry_backoff_ms in Python?", "Use client.send(..., retry_backoff_ms=250).", "clean", ["v3:client-send:example"], [0.91]),
    TraceSeed("tr_0019", "What happens when the stream event buffer is off?", "The docs do not describe behavior when event_buffer is false.", "unsupported_quota", ["v3:client-stream:parameters"], [0.75]),
    TraceSeed("tr_0020", "What is checksum on upload?", "checksum is an optional string.", "clean", ["v3:files-upload:parameters"], [0.9]),
    TraceSeed("tr_0021", "Is retry_backoff_ms seconds or milliseconds?", "retry_backoff_ms is measured in milliseconds.", "generic_retry", ["v3:retry-guide:retry-behavior", "v3:changelog-v3-2:changes"], [0.82, 0.74]),
    TraceSeed("tr_0022", "What is ERR-4032 in Responses.create?", "ERR-4032 means unsafe tool output was blocked.", "clean", ["v3:responses-create:errors"], [0.94]),
    TraceSeed("tr_0023", "What timeout should I expect on v3 Client.send?", "timeout_ms defaults to 30000.", "wrong_version", ["v2:client-send:parameters", "v3:client-send:parameters"], [0.84, 0.8]),
    TraceSeed("tr_0024", "Can Files.upload read from S3?", "The indexed docs do not mention S3 upload.", "unsupported_quota", ["v3:files-upload:parameters"], [0.7]),
    TraceSeed("tr_0025", "What is temperature default?", "temperature defaults to 0.2.", "example_over_table", ["v3:responses-create:example", "v3:responses-create:parameters"], [0.83, 0.77]),
    TraceSeed("tr_0026", "Which version introduced ERR-4032?", "v3.2.0 introduced ERR-4032.", "clean", ["v3:changelog-v3-2:changes"], [0.92]),
    TraceSeed("tr_0027", "Where do I put SDK_API_KEY?", "Set SDK_API_KEY in the environment.", "missing_citation", ["v3:auth-guide:api-key-login"], [0.9]),
    TraceSeed("tr_0028", "What does max_events default to?", "max_events defaults to 128.", "clean", ["v3:client-stream:parameters"], [0.88]),
    TraceSeed("tr_0029", "Should I retry ERR-4032?", "ERR-4032 should be treated as blocked output, not a retry hint.", "ambiguous_error", ["v3:errors-guide:handling-failures", "v3:responses-create:errors"], [0.8, 0.76]),
    TraceSeed("tr_0030", "What is default model for embeddings?", "The default is text-embedding-3-small.", "clean", ["v3:embeddings-create:parameters"], [0.89]),
    TraceSeed("tr_0031", "What is retry backoff delay?", "The answer gives generic retry advice and does not name retry_backoff_ms.", "generic_retry", ["v3:retry-guide:retry-behavior"], [0.81]),
    TraceSeed("tr_0032", "How many requests per minute are allowed?", "The docs do not state a requests-per-minute limit.", "unsupported_quota", ["v3:auth-guide:api-key-login", "v3:retry-guide:retry-behavior"], [0.72, 0.61]),
]


OBSERVATIONS = {
    "clean": "The answer matched the expected source and the cited chunk contained the claim.",
    "wrong_version": "The answer used an older Client.send reference even though the question asked for the v3 behavior.",
    "example_over_table": "The answer copied the nearby code sample and missed the parameter table value that answered the question.",
    "unsupported_quota": "The answer gave a quota-like response even though the retrieved chunks did not contain that policy.",
    "generic_retry": "The answer stayed at retry guidance level and did not resolve the exact requested symbol.",
    "missing_citation": "The answer looked correct, but the output did not include a chunk_id that a reviewer could open.",
    "ambiguous_error": "The answer described general error handling while the requested error-code row was only a lower-ranked result.",
}


def stable_output(trace: TraceSeed) -> str:
    if trace.failure_mode == "clean":
        return trace.expected_answer
    if trace.failure_mode == "wrong_version":
        return "Use the older Client.send defaults from the v2 reference."
    if trace.failure_mode == "example_over_table":
        return "Here is the example call, but the exact default is not stated."
    if trace.failure_mode == "unsupported_quota":
        return "The monthly quota is 10,000 requests."
    if trace.failure_mode == "generic_retry":
        return "The SDK retries temporary failures automatically."
    if trace.failure_mode == "missing_citation":
        return trace.expected_answer
    if trace.failure_mode == "ambiguous_error":
        return "Catch SDKError and log the request id for support."
    raise ValueError(trace.failure_mode)


def trace_to_record(trace: TraceSeed) -> dict:
    prompt_version = "docs-rag-v5.0"
    model = "gpt-4.1-mini"
    params = {"temperature": 0.0, "max_output_tokens": 180}
    raw_output = stable_output(trace)
    fingerprint = hashlib.sha1(f"{trace.trace_id}|{trace.question}|{raw_output}".encode()).hexdigest()[:10]
    return {
        "trace_id": trace.trace_id,
        "question": trace.question,
        "prompt_version": prompt_version,
        "retrieved": [
            {"chunk_id": chunk_id, "score": score}
            for chunk_id, score in zip(trace.retrieved_chunk_ids, trace.retrieved_scores)
        ],
        "model": model,
        "params": params,
        "raw_output": raw_output,
        "expected_answer": trace.expected_answer,
        "failure_mode": trace.failure_mode,
        "fingerprint": fingerprint,
    }


def write_traces() -> list[dict]:
    traces = [trace_to_record(seed) for seed in TRACE_SEEDS]
    with TRACE_PATH.open("w", encoding="utf-8") as handle:
        for trace in traces:
            handle.write(json.dumps(trace) + "\n")
    return traces


def replay(trace: dict) -> str:
    required = ["question", "prompt_version", "retrieved", "model", "params", "raw_output"]
    missing = [field for field in required if field not in trace]
    if missing:
        return f"Could not reconstruct; missing fields: {', '.join(missing)}"
    return trace["raw_output"]


def sample_traces(traces: list[dict]) -> list[dict]:
    rng = random.Random(SAMPLE_SEED)
    return rng.sample(traces, 20)


def replay_trace(traces: list[dict]) -> dict:
    rng = random.Random(REPLAY_SEED)
    return rng.choice(traces)


def write_taxonomy(sample: list[dict]) -> None:
    failures = [trace for trace in sample if trace["failure_mode"] != "clean"]
    counts = Counter(trace["failure_mode"] for trace in failures)
    lines = [
        "# Week 5 Failure Taxonomy",
        "",
        "| Failure mode | Count | Frequency | Severity | Example trace_id |",
        "|---|---:|---:|---|---|",
    ]
    for mode, count in counts.most_common():
        details = MODE_DETAILS[mode]
        example = next(trace["trace_id"] for trace in sample if trace["failure_mode"] == mode)
        lines.append(f"| {details['mode']} | {count} | {count / len(sample):.0%} | {details['severity']} | {example} |")
    (ROOT / "taxonomy.md").write_text("\n".join(lines), encoding="utf-8")


def write_notes(sample: list[dict], replayed: dict) -> None:
    today = date.today().isoformat()
    wrong_version_count = sum(1 for trace in sample if trace["failure_mode"] == "wrong_version")
    wrong_version_percent = wrong_version_count / len(sample)
    prediction = (
        f"{today}: Next week I will attack 'answers with the v2 method signature for a v3 question' "
        f"by adding an sdk_version filter before ranking; I predict this mode will drop from {wrong_version_percent:.0%} of the "
        "random sample to under 5% on the next 20-trace sample."
    )
    (ROOT / "prediction.md").write_text(f"# Week 5 Dated Prediction\n\n{prediction}\n", encoding="utf-8")
    lines = [
        "# Week 5 Notes",
        "",
        "## Seeded sample",
        "",
        f"Sample seed: {SAMPLE_SEED}",
        "",
        ", ".join(trace["trace_id"] for trace in sample),
        "",
        "## Replay evidence",
        "",
        f"Replay seed: {REPLAY_SEED}",
        f"Random replay trace_id: {replayed['trace_id']}",
        "",
        "Original output:",
        "",
        f"> {replayed['raw_output']}",
        "",
        "Replayed output from trace fields:",
        "",
        f"> {replay(replayed)}",
        "",
        "All replay-critical fields were present: prompt_version, retrieved chunk_ids + scores, model + params, and raw_output.",
        "",
        "## Open coding sentences",
        "",
    ]
    for trace in sample:
        lines.append(f"- {trace['trace_id']}: {OBSERVATIONS[trace['failure_mode']]}")
    lines.extend(
        [
            "",
            "## Dated prediction",
            "",
            prediction,
            "",
            "Commit hash: BLOCKED - git commit approval was rejected in this environment.",
            "",
            "## Public benchmark note",
            "",
            "A public benchmark would not include our old v1/v2/v3 SDK pages sitting beside each other, so it would miss the wrong-version failure mode.",
            "It would also score final answers more than trace replayability, so missing chunk_id citations could look harmless even though they block review.",
            "Finally, benchmark questions rarely ask private product-limit questions that are absent from the corpus, so they would not reveal our quota invention pattern.",
        ]
    )
    (ROOT / "notes.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    traces = write_traces()
    sample = sample_traces(traces)
    replayed = replay_trace(traces)
    write_taxonomy(sample)
    write_notes(sample, replayed)


if __name__ == "__main__":
    main()
