# Week 9 MCP discovery evidence

Tool count: **2 before -> 4 after**.

Before names from live `tools/list`: `get_openapi_spec, search_docs`.
After names from live `tools/list`: `get_openapi_spec, registry_get_deprecation, registry_get_version, search_docs`.

## Package-registry query trace

```text
User: What is the latest published version of docs-sdk?
Discovered: get_openapi_spec, registry_get_deprecation, registry_get_version, search_docs
Tool selected: registry_get_version
Tool result: {"isError": false, "package": "docs-sdk", "released": "2026-08-18", "version": "3.2.0"}
Assistant: docs-sdk 3.2.0 was released on 2026-08-18.
```

The selected tool is supplied only by the package-registry server.
