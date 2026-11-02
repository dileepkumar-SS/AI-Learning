# Cost per question and 10× plan

Mean cost per integrated question: **$0.000260**, n=30.
Median end-to-end latency: **20.828 ms** in the local deterministic harness.

| Stage | Mean cost/question |
|---|---:|
| deprecation | $0.000035 |
| generation | $0.000096 |
| mcp_discovery | $0.000032 |
| retrieval | $0.000064 |
| symbol_check | $0.000027 |
| version_resolution | $0.000006 |

At 9,000 integrators, the observed 75 requests/minute peak becomes **750 requests/minute at 10×**, exceeding the configured provider limit of **600 requests/minute by 150**; the rate limit breaks before the measured cost or latency budget.

Plan: request a 1,000 RPM quota, add bounded exponential backoff, cache version/symbol checks for 15 minutes, and alert at 480 RPM (80% of the present limit).
