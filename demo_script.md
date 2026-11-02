# Ten-minute capstone demo script

## 0:00–2:30 — real run

Run `python3 capstone.py ask --version v2.4 "How do I use client.query?"`. Point out version resolution before retrieval, the v2.4-labelled clickable citation, runnable `client.query` sample, and unasked warning that it is removed in v3.0. Then run the same question on v3.0 and show the plain “no longer exists” migration to `client.search(..., timeout=30)`.

## 2:30–5:00 — failures found

Show `integrated_taxonomy.md`, the three wrong-version samples in the pre-fix seam run, and the new MCP trace-context-loss mode. Open `capstone_loop_red.txt`. State the three known weaknesses before questions are invited.

## 5:00–7:30 — number that moved

Show wrong-version code rate **3/30 → 0/30**, n=30; integrated pass rate and judge agreement from `capstone_eval_report.md`; then read the explicit non-coverage sentence. Show the trajectory gap rather than hiding the retry.

## 7:30–10:00 — next and scale

Open `capstone_loop_green.txt`, then `capstone_cost_scale.md`. State mean cost/question and the 10× bottleneck: 750 RPM exceeds the 600 RPM limit by 150. Finish with the ranked weaknesses and the external-review status.
