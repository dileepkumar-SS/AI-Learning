# Week 3 Task Set E Results

Only the 6 new v3 reference pages were indexed for the chunking comparison; the single v2 Client.send page is used only for the sdk_version filter demonstration.

## Known-answer questions

| # | Question | Known-correct page | Section | Current top-5 hit | Structure-aware top-5 hit |
|---|---|---|---|---|---|
| 1 | What is the default value and type of retry_backoff_ms on Client.send()? | client-send | Parameters | no | yes |
| 2 | Which Client.send() parameter is required? | client-send | Parameters | no | yes |
| 3 | How do you pass retry_backoff_ms in the Client.send() code sample? | client-send | Example | no | yes |
| 4 | What is the default value of event_buffer on Client.stream()? | client-stream | Parameters | no | yes |
| 5 | What is the default purpose for Files.upload()? | files-upload | Parameters | no | yes |
| 6 | Which model is the default for Embeddings.create()? | embeddings-create | Parameters | no | yes |
| 7 | What is the default max_output_tokens for Responses.create()? | responses-create | Parameters | no | yes |
| 8 | What is the default tool_choice for Runs.create()? | runs-create | Parameters | no | yes |

## Hit-in-top-5

| Strategy | Hit-in-top-5 |
|---|---:|
| Current fixed-word chunker | 0/8 |
| Structure-aware markdown chunker | 8/8 |

## sdk_version filter demonstration

Query: What is the default retry_backoff_ms for Client.send?

Unfiltered results:
- 2.6879 v2:client-send:structure:3 docs/sdk/v2/client-send.md#example
- 2.6833 v2:client-send:structure:1 docs/sdk/v2/client-send.md#top
- 2.4537 v3:client-send:structure:3 docs/sdk/v3/client-send.md#example
- 2.3750 v2:client-send:structure:2 docs/sdk/v2/client-send.md#parameters
- 2.1243 v3:client-send:structure:2 docs/sdk/v3/client-send.md#parameters

Filtered to sdk_version=v3:
- 2.4537 v3:client-send:structure:3 docs/sdk/v3/client-send.md#example
- 2.1243 v3:client-send:structure:2 docs/sdk/v3/client-send.md#parameters
- 1.9415 v3:client-send:structure:1 docs/sdk/v3/client-send.md#top
- 1.0000 v3:client-stream:structure:1 docs/sdk/v3/client-stream.md#top
- 1.0000 v3:client-stream:structure:2 docs/sdk/v3/client-stream.md#parameters

## Cited generated answers
- Q: What is the default value and type of retry_backoff_ms on Client.send()?
  A: retry_backoff_ms is an integer with default 250. [v3:client-send:structure:2](docs/sdk/v3/client-send.md#parameters)
- Q: What is the default purpose for Files.upload()?
  A: Files.upload() defaults purpose to assistants. [v3:files-upload:structure:2](docs/sdk/v3/files-upload.md#parameters)
- Q: What is the default tool_choice for Runs.create()?
  A: Runs.create() defaults tool_choice to auto. [v3:runs-create:structure:2](docs/sdk/v3/runs-create.md#parameters)

## Refusal transcripts
- Q: What is the endpoint rate limit?
  A: I cannot answer from the indexed v3 reference pages because no chunk documents an endpoint rate limit.
- Q: What is the regional data residency policy?
  A: I cannot answer from the indexed v3 reference pages because no chunk documents regional data residency.
- Q: What is the invoice retention period?
  A: I cannot answer from the indexed v3 reference pages because no chunk documents invoice retention.

## Decision

I am keeping the structure-aware chunker because it preserves markdown tables and code fences as atomic evidence, which is exactly where SDK reference answers live. The embarrassing retrieval was the unfiltered retry_backoff_ms query: the v2 Client.send chunk can outrank v3 when sdk_version is not constrained, so version filtering must be part of the retriever contract rather than a UI afterthought.

## Code diff

See Main.py for the metadata fields, current chunker, structure-aware chunker, search-only evaluation, citation generation, and forced refusals.

## Search-only dump

See search_dump.md for all 8 questions under both strategies.