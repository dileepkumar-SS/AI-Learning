---
page_id: errors-guide
sdk_version: v3.2.0
page_type: guide
---
# Error handling guide

## Handling failures

Catch SDKError for recoverable client exceptions and log the request id for
support. Unknown error codes should be treated as non-retryable.
