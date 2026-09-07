---
page_id: runs-create
sdk_version: v3
page_type: reference
---
# Runs.create

Starts an asynchronous run.

## Parameters

| name | type | default | required |
|---|---|---|---|
| assistant_id | string | none | yes |
| tool_choice | enum | auto | no |
| parallel_tool_calls | boolean | true | no |

## Example

```python
run = client.runs.create(assistant_id="asst_123", tool_choice="auto")
```
