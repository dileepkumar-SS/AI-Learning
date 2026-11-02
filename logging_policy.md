# Logging and PII policy

Integrator questions are redacted before trace construction or disk writes. API-key patterns become `[REDACTED_API_KEY]`; PostgreSQL, MySQL, MongoDB, and MongoDB SRV connection strings become `[REDACTED_CONNECTION_STRING]`. Raw secrets are never placed in `capstone_traces.jsonl`, MCP arguments, span attributes, or generated reports. Tests scan the persisted trace to enforce this line.
