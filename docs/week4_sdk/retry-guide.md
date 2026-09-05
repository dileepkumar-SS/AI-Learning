---
page_id: retry-guide
sdk_version: v3.2.0
page_type: guide
---
# Retry guide

## Retry behavior

The SDK retries temporary network failures automatically. Prefer idempotent
requests and avoid retrying permanent validation errors.
