---
page_id: responses-create-v3
sdk_version: v3.2.0
page_type: reference
---
# Responses.create

## Parameters

| name | type | default | required |
|---|---|---|---|
| instructions | string | none | no |
| max_output_tokens | integer | 1024 | no |
| temperature | number | 0.2 | no |

## Errors

| code | meaning |
|---|---|
| ERR-4032 | unsafe tool output was blocked |
