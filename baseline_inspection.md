# baseline_inspection.md

## How do I authenticate the SDK client?
Expected: v3.2.0:auth-guide:api-key-login
Hit: True
- 1.3229 v3.2.0:auth-guide:api-key-login
- 0.4472 v3.2.0:auth-guide:top
- 0.4170 v3.2.0:retry-guide:retry-behavior

## What is the default for retry_backoff_ms in v3.2.0?
Expected: v3.2.0:client-send-v3:parameters
Hit: False
- 3.0870 v3.2.0:changelog-v3-2:changes
- 2.5298 v3.2.0:changelog-v3-2:top
- 2.2942 v3.2.0:client-send-v3:example

## Which Client.send parameter is required?
Expected: v3.2.0:client-send-v3:parameters
Hit: False
- 1.2247 v1.9.0:client-send-v1:top
- 1.2247 v2.8.0:client-send-v2:top
- 1.2247 v3.2.0:client-send-v3:top

## Show the Client.send code sample using retry_backoff_ms.
Expected: v3.2.0:client-send-v3:example
Hit: True
- 1.3765 v3.2.0:client-send-v3:example
- 1.2247 v1.9.0:client-send-v1:top
- 1.2247 v1.9.0:client-send-v1:parameters

## What is the default event_buffer value?
Expected: v3.2.0:client-stream-v3:parameters
Hit: True
- 1.4596 v3.2.0:client-stream-v3:parameters
- 0.4082 v3.2.0:client-stream-v3:top
- 0.3780 v3.2.0:auth-guide:api-key-login

## What default purpose does Files.upload use?
Expected: v3.2.0:files-upload-v3:parameters
Hit: True
- 1.2247 v3.2.0:files-upload-v3:top
- 1.1180 v3.2.0:files-upload-v3:parameters
- 0.2085 v3.2.0:client-stream-v3:parameters

## Which embedding model is the default in v3.2.0?
Expected: v3.2.0:embeddings-create-v3:parameters
Hit: True
- 2.5298 v3.2.0:changelog-v3-2:top
- 1.3720 v3.2.0:changelog-v3-2:changes
- 0.7845 v3.2.0:embeddings-create-v3:parameters

## What is the default max_output_tokens?
Expected: v3.2.0:responses-create-v3:parameters
Hit: True
- 1.3229 v3.2.0:responses-create-v3:parameters
- 0.4170 v3.2.0:client-stream-v3:parameters
- 0.3780 v3.2.0:auth-guide:api-key-login

## What does ERR-4032 mean?
Expected: v3.2.0:responses-create-v3:errors
Hit: True
- 0.7276 v3.2.0:responses-create-v3:errors
- 0.5145 v3.2.0:changelog-v3-2:changes
- 0.0000 v3.2.0:auth-guide:top

## What is the default tool_choice on Runs.create?
Expected: v3.2.0:runs-create-v3:parameters
Hit: True
- 2.0083 v3.2.0:runs-create-v3:parameters
- 1.2247 v3.2.0:runs-create-v3:top
- 0.4851 v3.2.0:responses-create-v3:errors

## What changed in version v3.2.0 for Client.send retry behavior?
Expected: v3.2.0:changelog-v3-2:changes
Hit: True
- 2.5298 v3.2.0:changelog-v3-2:top
- 2.2295 v3.2.0:changelog-v3-2:changes
- 1.6330 v3.2.0:client-send-v3:top

## What is the monthly quota for Client.send?
Expected: NOT_IN_CORPUS
Hit: False
- 1.2247 v1.9.0:client-send-v1:top
- 1.2247 v2.8.0:client-send-v2:top
- 1.2247 v3.2.0:client-send-v3:top
