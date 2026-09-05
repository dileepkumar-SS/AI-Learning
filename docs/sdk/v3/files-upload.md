---
page_id: files-upload
sdk_version: v3
page_type: reference
---
# Files.upload

Uploads a document for later retrieval.

## Parameters

| name | type | default | required |
|---|---|---|---|
| path | string | none | yes |
| purpose | enum | assistants | no |
| checksum | string | none | no |

## Example

```python
file = client.files.upload(path="manual.pdf", purpose="assistants")
```
