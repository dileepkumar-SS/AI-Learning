---
page_id: client-send
sdk_version: v3
page_type: reference
---
# Client.send

Sends one request and returns the model response.

## Parameters

| name | type | default | required |
|---|---|---|---|
| message | string | none | yes |
| retry_backoff_ms | integer | 250 | no |
| timeout_ms | integer | 30000 | no |

## Example

```python
client.send("hello", retry_backoff_ms=250, timeout_ms=30000)
```
