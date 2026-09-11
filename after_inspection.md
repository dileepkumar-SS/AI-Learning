# after_inspection.md

## How do I authenticate the SDK client?
Expected: v3.2.0:auth-guide:api-key-login
Hit: True
- 5.3229 v3.2.0:auth-guide:api-key-login
- 4.3714 v3.2.0:errors-guide:handling-failures
- 2.4170 v3.2.0:retry-guide:retry-behavior

## What is the default for retry_backoff_ms in v3.2.0?
Expected: v3.2.0:client-send-v3:parameters
Hit: True
- 9.5788 v3.2.0:client-send-v3:parameters
- 8.5412 v1.9.0:client-send-v1:parameters
- 8.5412 v2.8.0:client-send-v2:parameters

## Which Client.send parameter is required?
Expected: v3.2.0:client-send-v3:parameters
Hit: True
- 9.3165 v1.9.0:client-send-v1:parameters
- 9.3165 v2.8.0:client-send-v2:parameters
- 9.2559 v3.2.0:client-send-v3:parameters

## Show the Client.send code sample using retry_backoff_ms.
Expected: v3.2.0:client-send-v3:example
Hit: True
- 5.8765 v3.2.0:client-send-v3:example
- 3.2247 v1.9.0:client-send-v1:top
- 3.2247 v1.9.0:client-send-v1:parameters

## What is the default event_buffer value?
Expected: v3.2.0:client-stream-v3:parameters
Hit: True
- 7.9596 v3.2.0:client-stream-v3:parameters
- 4.7236 v3.2.0:files-upload-v3:parameters
- 4.7041 v1.9.0:client-send-v1:parameters

## What default purpose does Files.upload use?
Expected: v3.2.0:files-upload-v3:parameters
Hit: True
- 9.6180 v3.2.0:files-upload-v3:parameters
- 4.7085 v3.2.0:client-stream-v3:parameters
- 4.7041 v1.9.0:client-send-v1:parameters

## Which embedding model is the default in v3.2.0?
Expected: v3.2.0:embeddings-create-v3:parameters
Hit: True
- 10.2845 v3.2.0:embeddings-create-v3:parameters
- 6.2559 v3.2.0:responses-create-v3:parameters
- 5.9472 v3.2.0:files-upload-v3:parameters

## What is the default max_output_tokens?
Expected: v3.2.0:responses-create-v3:parameters
Hit: True
- 7.8229 v3.2.0:responses-create-v3:parameters
- 4.9170 v3.2.0:client-stream-v3:parameters
- 4.7236 v3.2.0:files-upload-v3:parameters

## What does ERR-4032 mean?
Expected: v3.2.0:responses-create-v3:errors
Hit: True
- 7.2276 v3.2.0:responses-create-v3:errors
- 2.5145 v3.2.0:changelog-v3-2:changes
- 0.0000 v3.2.0:auth-guide:top

## What is the default tool_choice on Runs.create?
Expected: v3.2.0:runs-create-v3:parameters
Hit: True
- 10.5083 v3.2.0:runs-create-v3:parameters
- 4.8922 v3.2.0:embeddings-create-v3:parameters
- 4.8780 v3.2.0:responses-create-v3:parameters

## What changed in version v3.2.0 for Client.send retry behavior?
Expected: v3.2.0:changelog-v3-2:changes
Hit: True
- 11.2295 v3.2.0:changelog-v3-2:changes
- 6.1471 v3.2.0:client-send-v3:example
- 5.9449 v3.2.0:client-send-v3:parameters

## What is the monthly quota for Client.send?
Expected: NOT_IN_CORPUS
Hit: False
- 3.2247 v1.9.0:client-send-v1:top
- 3.2247 v2.8.0:client-send-v2:top
- 3.2247 v3.2.0:client-send-v3:top
