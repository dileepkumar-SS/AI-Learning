# Own-server tool prompt and error diff

```diff
-description: "Search docs."
+description: "Find a published developer-documentation page for one API version.
+Use this before answering version-specific SDK questions. If the requested
+version is unpublished, use latest_version and migration_path to recover
+instead of guessing an endpoint."

-{"isError": true, "message": "Error 3"}
+{"isError": true, "code": "UNPUBLISHED_VERSION",
+ "message": "No docs exist for v4; latest published is v3.2.",
+ "latest_version": "v3.2",
+ "migration_path": "Read v3.2/migration for deprecated methods and retry...",
+ "retryable": true}
```
