# Docs-assistant eval

Run the complete Week 6 evaluation with one command:

```bash
python3 evals.py
```

The command validates 25 mode-tagged cases, checks two verbatim Week 5 regression replays, runs four deterministic assertion types, compares the stored v1/v2 judge verdicts with the frozen blind labels, prints pass rates by mode, and regenerates `eval_report.md`.

The stored judge outputs keep the exercise reproducible without an API key. `labels_25.json` was created first; its filesystem timestamp and SHA-256 are checked and reported as ordering evidence.
