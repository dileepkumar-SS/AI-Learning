Prompt version bump: `docs-rag-v10.0` → `docs-rag-v11.0`; retrieval now filters archived v2 examples and requires the v3.2 migration chunk for deprecated symbols.

Canary: send 5% of v3 migration traffic to `docs-rag-v11.0` for 30 minutes and require zero deprecated-symbol outputs plus no overall eval regression.
Rollback: immediately restore `docs-rag-v10.0` if deprecated-symbol rate exceeds 0%, error rate rises by 1 percentage point, or p99 latency rises by 20%.
