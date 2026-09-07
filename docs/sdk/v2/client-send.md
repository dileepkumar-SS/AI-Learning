---
page_id: client-send
sdk_version: v2
page_type: reference
---
# Client.send

## Parameters

| name | type | default | required |
|---|---|---|---|
| retry_backoff_ms | number | 100 | no |
| timeout_ms | number | 10000 | no |

## Example

```python
client.send("ping", retry_backoff_ms=100)
```
