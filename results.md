# Week 4 Task Set E Results

This run keeps the chunking and corpus fixed, measures dense retrieval first, then makes exactly one retrieval change: a rerank pass over the dense top-25 candidates.

## Golden set

| # | Developer question | Known-correct chunk_id |
|---|---|---|
| 1 | How do I authenticate the SDK client? | v3.2.0:auth-guide:api-key-login |
| 2 | What is the default for retry_backoff_ms in v3.2.0? | v3.2.0:client-send-v3:parameters |
| 3 | Which Client.send parameter is required? | v3.2.0:client-send-v3:parameters |
| 4 | Show the Client.send code sample using retry_backoff_ms. | v3.2.0:client-send-v3:example |
| 5 | What is the default event_buffer value? | v3.2.0:client-stream-v3:parameters |
| 6 | What default purpose does Files.upload use? | v3.2.0:files-upload-v3:parameters |
| 7 | Which embedding model is the default in v3.2.0? | v3.2.0:embeddings-create-v3:parameters |
| 8 | What is the default max_output_tokens? | v3.2.0:responses-create-v3:parameters |
| 9 | What does ERR-4032 mean? | v3.2.0:responses-create-v3:errors |
| 10 | What is the default tool_choice on Runs.create? | v3.2.0:runs-create-v3:parameters |
| 11 | What changed in version v3.2.0 for Client.send retry behavior? | v3.2.0:changelog-v3-2:changes |
| 12 | What is the monthly quota for Client.send? | NOT_IN_CORPUS |

## Before and after

| Run | Retrieval method | hit-rate@3 | p50 latency/query |
|---|---|---:|---:|
| Baseline | Dense lexical-semantic overlap | 9/12 (75.00%) | 0.255 ms |
| After | Dense top-25 + rerank | 11/12 (91.67%) | 0.556 ms |

## Failure labels from baseline inspection

Tally: R=2, G=0, Not-In-Corpus=1

| Question | Expected | Label | Evidence |
|---|---|---|---|
| What is the default for retry_backoff_ms in v3.2.0? | v3.2.0:client-send-v3:parameters | R | Expected v3.2.0:client-send-v3:parameters, but top-3 fetched v3.2.0:changelog-v3-2:changes, v3.2.0:changelog-v3-2:top, v3.2.0:client-send-v3:example. |
| Which Client.send parameter is required? | v3.2.0:client-send-v3:parameters | R | Expected v3.2.0:client-send-v3:parameters, but top-3 fetched v1.9.0:client-send-v1:top, v2.8.0:client-send-v2:top, v3.2.0:client-send-v3:top. |
| What is the monthly quota for Client.send? | NOT_IN_CORPUS | Not-In-Corpus | No known-correct chunk exists in the indexed developer docs. |

## Why this one change

The baseline failures are R failures where the right chunk is in the candidate pool but not in the top-3 because dense retrieval ranks neighboring chunks higher. That tally points to a ranking problem after recall, not a generation problem, so I chose one rerank pass over the dense top-25 as the single retrieval change.

## Per-question fixed/unfixed table

| Question | Baseline top-3 hit | After top-3 hit | Status |
|---|---:|---:|---|
| How do I authenticate the SDK client? | True | True | already passed |
| What is the default for retry_backoff_ms in v3.2.0? | False | True | fixed |
| Which Client.send parameter is required? | False | True | fixed |
| Show the Client.send code sample using retry_backoff_ms. | True | True | already passed |
| What is the default event_buffer value? | True | True | already passed |
| What default purpose does Files.upload use? | True | True | already passed |
| Which embedding model is the default in v3.2.0? | True | True | already passed |
| What is the default max_output_tokens? | True | True | already passed |
| What does ERR-4032 mean? | True | True | already passed |
| What is the default tool_choice on Runs.create? | True | True | already passed |
| What changed in version v3.2.0 for Client.send retry behavior? | True | True | already passed |
| What is the monthly quota for Client.send? | False | False | not-in-corpus, not touched |

## Fixed and untouched failures

Fixed by rerank:
- What is the default for retry_backoff_ms in v3.2.0?
- Which Client.send parameter is required?

Not fixed / not touched:
- What is the monthly quota for Client.send?

## Shipping decision

Ship the rerank pass. It raises hit-rate@3 from 9/12 to 11/12 while adding only 0.302 ms p50 latency in this local run.

## Code diff

The code change is in Main.py: the baseline retriever is dense_search; the single changed retriever is rerank_search, which reranks the dense top-25 candidates.