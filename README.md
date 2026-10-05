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
