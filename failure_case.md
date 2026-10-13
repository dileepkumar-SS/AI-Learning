# Injected worker failure

Case: `tr_0003` — Show Client.send with timeout_ms.

Injected behavior: `version-worker` returned HTTP 500 on the initial request and the single retry.

Observed hand-offs:

- `orchestrator -> version-worker`: question + docs context (159 tokens)
- `version-worker -> orchestrator`: version/deprecation result (46 tokens)
- `orchestrator -> version-worker`: single retry after HTTP 500 (159 tokens)
- `version-worker -> orchestrator`: second HTTP 500 (46 tokens)

Final answer: “I could not verify the target API version because the version service failed; no code sample was generated.”

Classification: **RETRIED ONCE, THEN DEGRADED SAFELY** to a partial response; it did not ship an unverified code sample or lie about version validation.
