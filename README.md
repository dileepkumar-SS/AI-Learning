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

## Week 10 single-agent vs squad race

Run both arms on the same ten verbatim Week 6 cases and regenerate all evidence:

```bash
python3 multi_agent_race.py
```

The runner applies one shared binary judge, reports pass rate, p50/p99 latency, total tokens, and cost per question for both arms, logs every worker hand-off, calculates the context re-send multiplier, and performs a separate HTTP 500 failure-injection run.

## Week 11 production drill

Plant the production log corpus, run the timed incident search, and regenerate the complete RED → GREEN evidence:

```bash
python3 production_drill.py
```

The command finds a deprecated-method output from last week's logs, exports its full trace, records stage-level cost, adds the incident to the ten-case Week 6 suite, preserves the failing pre-fix result, applies the retrieval policy and prompt-version bump, and records the passing full-suite result plus canary, rollback, and 10× plans.
