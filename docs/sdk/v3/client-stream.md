---
page_id: client-stream
sdk_version: v3
page_type: reference
---
# Client.stream

Opens a streaming response.

## Parameters

| name | type | default | required |
|---|---|---|---|
| event_buffer | boolean | true | no |
| max_events | integer | 128 | no |

## Example

```python
for event in client.stream("status", event_buffer=True):
    print(event.delta)
```
