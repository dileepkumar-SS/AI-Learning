---
page_id: embeddings-create
sdk_version: v3
page_type: reference
---
# Embeddings.create

Creates vector embeddings.

## Parameters

| name | type | default | required |
|---|---|---|---|
| model | string | text-embedding-3-small | no |
| input | string or string[] | none | yes |
| dimensions | integer | 1536 | no |

## Example

```python
vectors = client.embeddings.create(input=["alpha"], dimensions=1536)
```
