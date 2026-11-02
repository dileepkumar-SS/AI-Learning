# Integration seam list — frozen 2026-11-02 before the integrated run

This list records the initial seams without deleting resolved items.

| Seam found | Initial risk | Status |
|---|---|---|
| Week 6 eval artifacts lived on a separate branch from the Week 7–11 agent lineage | Integrated suite could silently use a new ruler | **Fixed** — 30 cases now live behind the capstone entry point with frozen labels |
| Caller version existed as text rather than an enforced retrieval filter | v2.4 caller could receive runnable-looking v3 code | **Fixed** — version is a required enum passed to every MCP tool |
| Agent trace ID was not part of MCP tool schemas | Trace broke at the subprocess boundary | **Fixed** — required and echoed by every tool, with assertions |
| Deprecated symbol lookup and code retrieval could disagree on target symbol | Removed method could produce a plausible signature | **Fixed** — existence/deprecation precede replacement retrieval |
| Unknown natural-language aliases are not mapped to SDK symbols | Engine may ask for clarification instead of answering | **Accepted** — safer than inventing a method; listed as a known weakness |
| Real SDK wheel execution environment is absent | Parser and symbol-table checks do not prove imports install | **Ran out of time** — explicit eval non-coverage |
| External peer review is not available inside this coding session | Fresh-eyes requirement cannot be truthfully claimed | **Ran out of time** — runnable client and note template supplied |
