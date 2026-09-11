---
page_id: auth-guide
sdk_version: v3.2.0
page_type: guide
---
# Authentication guide

## API key login

Set SDK_API_KEY before creating the client. The SDK reads the environment
variable automatically when no explicit api_key is passed.

```python
client = Client()
```
