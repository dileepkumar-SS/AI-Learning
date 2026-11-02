# SDK Docs Answer Engine — one-page architecture

```mermaid
flowchart LR
    U[Integrator question + required SDK version] --> R[Write-time secret redaction]
    R --> A[Hand-built agent loop / host]
    A -->|initialize + tools/list| M[MCP client]
    M --> S[Own docs MCP server]
    A -->|symbol_exists| S
    A -->|check_deprecation| S
    A -->|version_scoped_search| S
    S --> C[(v2.4 + v3.0 corpus, migration metadata)]
    A --> G[Answer synthesis / model-call boundary]
    G --> O[Versioned citation + checked code + migration warning]
    R --> T[(Unified trace ID)]
    A --> T
    M --> T
    S --> T
    G --> T
    T --> E[Assertions → validated judge → taxonomy/trajectory reports]
```

The model-call boundary is answer synthesis in the host; MCP `initialize`, `tools/list`, and `tools/call` are local protocol operations and contain no model. Token cost is attributed to version resolution, discovery, symbol check, deprecation lookup, retrieval, and generation spans. One `trace_id` is required at every tool boundary.
