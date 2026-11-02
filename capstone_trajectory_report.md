# Integrated Trajectory Eval

Cases: **n=12**.
Tool-choice accuracy: **100.0%**.
Outcome pass rate: **100.0%**.
Trajectory pass rate: **91.7%**.
Outcome-vs-trajectory gap: **8.3 percentage points**.

`cap_eval_08` passed its outcome after an MCP retrieval retry, but failed trajectory efficiency because `version_scoped_search` ran twice. The honest gap is retained rather than treating the retry as an ideal path.
