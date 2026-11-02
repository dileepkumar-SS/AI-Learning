# Integrated Capstone Eval

Cases: **n=30**. Pass rate: **100.0% (30/30)**.
Validated binary judge agreement against frozen labels: **93.3%** (threshold: 85%).

Deterministic assertions run before the judge: version resolution, versioned citation, Python parse, version-specific symbol existence, removed-method explanation, and write-time PII redaction.

| Mode | Passed | Total | Pass rate |
|---|---:|---:|---:|
| community_poisoning | 1 | 1 | 100.0% |
| deprecation_surface | 1 | 1 | 100.0% |
| pii_redaction | 2 | 2 | 100.0% |
| removed_symbol_migration | 1 | 1 | 100.0% |
| terminology_gap | 1 | 1 | 100.0% |
| version_scoped_code | 24 | 24 | 100.0% |

## Number that moved

Enforcing the caller-version metadata filter reduced wrong-version code samples from **3/30 (10.0%) → 0/30 (0.0%)**, n=30.

## Explicit non-coverage

The suite does not execute imports against real installed SDK wheels, measure retrieval recall over the full 9,000-user query distribution, or validate external Stack Overflow freshness beyond the named poisoning cases.
