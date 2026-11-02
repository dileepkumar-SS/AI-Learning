# Single Agent vs Docs Squad

Cases, unchanged from Week 6: `tr_0001, tr_0002, tr_0003, tr_0004, tr_0005, tr_0006, tr_0007, tr_0008, tr_0009, tr_0010`. Shared judge: `week6-binary-correctness-v2`.

| Arm | Pass rate | p50 latency | p99 latency | Total tokens | Cost/question |
|---|---:|---:|---:|---:|---:|
| Single agent | 100.0% | 1.317 ms | 1.351 ms | 2489 | $0.000053 |
| Orchestrator squad | 100.0% | 3.923 ms | 3.932 ms | 11114 | $0.000246 |

Context re-send multiplier: **11114 / 2489 = 4.5x**.
Largest hand-off: **orchestrator -> code-sample-worker resend, 3229 tokens (29.1% of all multi-agent tokens)**.
