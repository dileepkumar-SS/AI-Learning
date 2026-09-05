# Week 5 Failure Taxonomy

| Failure mode | Count | Frequency | Severity | Example trace_id |
|---|---:|---:|---|---|
| states a quota or limit that is not present in the indexed docs | 4 | 20% | ships invented operational constraints | tr_0019 |
| answers with the v2 method signature for a v3 question | 3 | 15% | ships broken code to a user's repo | tr_0023 |
| gives a correct-looking answer without a resolvable citation | 3 | 15% | blocks verification and review | tr_0017 |
| quotes a code example when the parameter table contains the requested default | 1 | 5% | ships subtly wrong configuration values | tr_0003 |
| returns generic retry guidance instead of the requested exact symbol | 1 | 5% | merely annoys the reader | tr_0021 |