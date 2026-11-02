# Week 7 Agent vs Workflow Race

Both systems used the same ten inputs, tools, deterministic model, and output contract.

| System | Pass rate | p50 latency | Total tokens | Cost/question |
|---|---:|---:|---:|---:|
| agent | 100.0% | 6.514 ms | 5766 | $0.000132 |
| workflow | 100.0% | 3.240 ms | 1417 | $0.000044 |

## Verdict

Ship the fixed workflow. The path varies only for deprecated-endpoint migration questions: after the OpenAPI lookup marks an operation deprecated, its replacement must be read from the changelog. However, this is a known, bounded conditional and none of the ten questions requires open-ended planning. Both systems pass, while the workflow is faster, cheaper, and uses fewer tokens. An agent would become justified only if inputs could require an unknown sequence of searches or tools that cannot be expressed as this fixed three-step pipeline.

The verdict is 72 words.
