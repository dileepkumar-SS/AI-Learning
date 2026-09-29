# Week 6 Eval Report

Blind ordering: **PASS**. `labels_25.json` predates both judge result files. SHA-256: `5cd34c10e931f1351b24cd22ab1db99f95e1c4277ff012e3deb0e2ecd9718369`.

Agreement before -> after: **92.0% (23/25) -> 100.0% (25/25)**.

Split: **4 deterministic assertions vs 1 judged criterion**.

## Pass rate by Week 5 mode

| Mode | Passed | Total | Pass rate |
|---|---:|---:|---:|
| ambiguous_error | 0 | 1 | 0.0% |
| clean | 8 | 9 | 88.9% |
| example_over_table | 0 | 3 | 0.0% |
| generic_retry | 0 | 2 | 0.0% |
| missing_citation | 1 | 2 | 50.0% |
| unsupported_quota | 0 | 4 | 0.0% |
| wrong_version | 0 | 4 | 0.0% |

## Judge disagreements

- `eval_008`: Human **PASS**, judge v1 **FAIL**. The human was right: the answer exactly names the requested embedding model; brevity is not unhelpfulness.
- `eval_017`: Human **PASS**, judge v1 **FAIL**. The human was right: the answer gives the requested boolean default completely and correctly.

Both v1 disagreements are visible as few-shot examples in `judge_v2.txt`.

## Prediction check

The prediction was correct: both false negatives were fixed and no true-negative verdict changed. It was not wrong on any observed case.

## Protocol note

Judge verdicts are stored run artifacts, so this command is deterministic and requires no API key. Re-running the table does not relabel cases or silently call a model.
