# Top three known weaknesses — recorded 2026-11-02 before external review

1. **Real import execution is missing.** Python syntax and version-specific symbol tables are checked, but emitted snippets are not executed against pinned v2.4/v3.0 wheels. Estimated next step: 1 engineering day for isolated test environments.
2. **Terminology mapping is deliberately narrow.** Unknown aliases produce a clarification request rather than a guess; this protects correctness but reduces answer rate. Estimated next step: 0.5 day to mine failed queries and add measured aliases.
3. **Corpus realism is bounded.** The local corpus represents the two live versions and migration seam but not all 200 samples, 50 Stack Overflow pages, or open issues. Estimated next step: 2 days for ingestion plus recall measurement.
