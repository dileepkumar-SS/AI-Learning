# Week 8 Trajectory Evaluation

## Metrics over the same 10 cases

| Phase | Tool-choice accuracy | Argument validity | Steps taken / needed | Cost p50 | Cost max | Trajectory pass | Outcome−trajectory gap |
|---|---:|---:|---:|---:|---:|---:|---:|
| Before | 86.4% | 95.5% | 0.957 | $0.000108 | $0.000170 | 40.0% | 60.0 pp |
| After | 88.0% | 96.0% | 1.087 | $0.000108 | $0.000170 | 70.0% | 30.0 pp |

Outcome pass rate is 100.0% in both phases.

## Right answer, wrong path

`q01` — Migrate Client.send to v3 and show Python.

Outcome: PASS (`Client.send`). Trajectory: FAIL (`search_docs`). The agent searched docs, skipped `get_openapi_spec`, and recited the correct operation from memory.

## Exactly one mitigation

Mitigation: **Require get_openapi_spec before finish in the agent planning description.**

Top mode, `missing_required_tool`: **3 -> 0**.
Measured price: **+41.7 tokens per question** (385.3 -> 427.0).

## Regression matrix

| Failure mode | Before | After | Delta |
|---|---:|---:|---:|
| missing_required_tool | 3 | 0 | -3 |
| invalid_argument | 1 | 1 | +0 |
| wrong_tool | 1 | 1 | +0 |
| redundant_step | 1 | 1 | +0 |

No mode worsened and no new mode appeared. Checked: missing_required_tool, invalid_argument, wrong_tool, redundant_step.

## Alternate-path policy

Cases `q05`, `q06`, and `q07` explicitly name deprecated operations, so both `search -> spec -> changelog` and `search -> changelog -> spec` are accepted. All other cases require the single shortest documented path.
