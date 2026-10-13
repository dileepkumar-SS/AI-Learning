# Week 7 docs agent vs fixed workflow

Run either implementation on the same default migration case:

```bash
python3 week7.py agent
python3 week7.py workflow
```

Run the complete ten-question race and regenerate `race.csv`, `week7_report.md`, and `budget_termination.log`:

```bash
python3 week7.py race
```

Run only the forced budget example with `python3 week7.py budget-demo`. Both systems use the same deterministic local model, three tools, ten inputs, and output contract. Latency is measured wall-clock runtime; tokens use the shared serialized-text estimator and cost uses the constants declared in `week7.py`.

## Week 8 trajectory evaluation

Run the before/after trajectory experiment and regenerate its CSV and report:

```bash
python3 trajectory_eval.py
```

The evaluator asserts expected paths for the same ten documentation cases, accepts two legitimate orderings for the three explicitly deprecated-operation cases, reports trajectory and cost-distribution metrics, exposes an outcome-pass/trajectory-fail trace, applies exactly one mitigation, and checks every failure mode for regressions.

## Week 9 MCP integration

Run the configuration-driven agent against both MCP servers:

```bash
python3 mcp_agent.py
```

Regenerate the live discovery, JSON-RPC wire, zero-agent-change, config-diff, and recoverable-error evidence:

```bash
python3 week9_evidence.py
```

The host starts servers from JSON configuration, executes `initialize` and `tools/list`, and routes `tools/call` to the server that advertised the selected capability. Adding the package registry changes only `mcp_config.json`; the host does not import either server or contain a hard-coded tool list.
