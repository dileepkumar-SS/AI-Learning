# Same failing docs lookup: before and after

## Before

Tool description: `Search docs.`

```text
Model -> search_docs(query='Responses.create', api_version='v4')
Tool  -> Error 3
Model -> I could not find the documentation, but `/v4/responses` is probably the endpoint.
```

The opaque error gives the model no safe recovery path, so it guesses.

## After

Tool description: `Find a published developer-documentation page for one API version. Use this before answering version-specific SDK questions. If unpublished, use latest_version and migration_path to recover instead of guessing.`

```text
Model -> search_docs(query='Responses.create', api_version='v4')
Tool  -> {"code": "UNPUBLISHED_VERSION", "isError": true, "latest_version": "v3.2", "message": "No docs exist for v4; latest published is v3.2.", "migration_path": "Read v3.2/migration for deprecated methods and retry with api_version=v3.2.", "retryable": true}
Model -> v4 is unpublished; retrying with v3.2 and reading its migration page.
Tool  -> {"api_version": "v3.2", "isError": false, "page": "/v3.2/docs/responses.create-migration"}
Model -> The latest published documentation is v3.2; I will answer from that version and flag the mismatch.
```

The second transcript is backed by the live JSON-RPC calls made while generating this artifact.
