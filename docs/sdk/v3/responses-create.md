---
page_id: responses-create
sdk_version: v3
page_type: reference
---
# Responses.create

Creates a response.

## Parameters

| name | type | default | required |
|---|---|---|---|
| instructions | string | none | no |
| max_output_tokens | integer | 1024 | no |
| temperature | number | 0.2 | no |

## Example

```python
answer = client.responses.create(instructions="cite sources", max_output_tokens=1024)
```
