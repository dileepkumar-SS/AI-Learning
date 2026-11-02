# Third tool description diff

```diff
 search_docs(query: string, api_version: enum[v2, v3])
   Find the documentation page that explains a named SDK operation.

 get_openapi_spec(operation: string, api_version: enum[v2, v3])
   Return the method, path, parameters, and deprecation flag for one operation.

+check_deprecation(operation: string, api_version: enum[v2, v3])
+  Look up the changelog replacement for one deprecated operation.
```

Each description names one distinct job: page discovery, schema inspection, or changelog replacement lookup. All three constrain `api_version` to the same `v2 | v3` enum.
