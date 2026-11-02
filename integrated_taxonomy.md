# Integrated Error Taxonomy

Re-scored over the 30-case integrated pre-fix seam run; status records the measured post-fix result.

| Failure mode | Count | Frequency | Severity | Trace ID | Status |
|---|---:|---:|---|---|---|
| wrong-version code sample | 3 | 10.0% | critical | `cap_c0ae3fd68644` | inherited; 3 -> 0 after metadata filter |
| missing removal-version warning | 2 | 6.7% | high | `cap_3b6e9649e0fa` | inherited; 2 -> 0 after deprecation tool |
| community answer poisoning | 1 | 3.3% | high | `cap_9fbb596187af` | inherited; 1 -> 0 after current-doc priority |
| terminology not mapped to symbol | 1 | 3.3% | medium | `cap_370f45c29ea6` | accepted: asks user for exact method |
| MCP trace context lost at hop | 2 | 6.7% | critical | `cap_ff7b91f0e86d` | NEW integration-created mode; 2 -> 0 after trace_id echo assertion |

The integration-created mode is **MCP trace context lost at hop**; it did not exist before the agent called a subprocess server.
