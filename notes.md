# Week 5 Notes

## Seeded sample

Sample seed: 20260905

tr_0018, tr_0003, tr_0023, tr_0019, tr_0017, tr_0011, tr_0016, tr_0004, tr_0024, tr_0021, tr_0008, tr_0002, tr_0010, tr_0007, tr_0005, tr_0030, tr_0022, tr_0001, tr_0027, tr_0015

## Replay evidence

Replay seed: 53017
Random replay trace_id: tr_0008

Original output:

> The default embedding model is text-embedding-3-small.

Replayed output from trace fields:

> The default embedding model is text-embedding-3-small.

All replay-critical fields were present: prompt_version, retrieved chunk_ids + scores, model + params, and raw_output.

## Open coding sentences

- tr_0018: The answer matched the expected source and the cited chunk contained the claim.
- tr_0003: The answer copied the nearby code sample and missed the parameter table value that answered the question.
- tr_0023: The answer used an older Client.send reference even though the question asked for the v3 behavior.
- tr_0019: The answer gave a quota-like response even though the retrieved chunks did not contain that policy.
- tr_0017: The answer looked correct, but the output did not include a chunk_id that a reviewer could open.
- tr_0011: The answer matched the expected source and the cited chunk contained the claim.
- tr_0016: The answer used an older Client.send reference even though the question asked for the v3 behavior.
- tr_0004: The answer matched the expected source and the cited chunk contained the claim.
- tr_0024: The answer gave a quota-like response even though the retrieved chunks did not contain that policy.
- tr_0021: The answer stayed at retry guidance level and did not resolve the exact requested symbol.
- tr_0008: The answer looked correct, but the output did not include a chunk_id that a reviewer could open.
- tr_0002: The answer used an older Client.send reference even though the question asked for the v3 behavior.
- tr_0010: The answer matched the expected source and the cited chunk contained the claim.
- tr_0007: The answer matched the expected source and the cited chunk contained the claim.
- tr_0005: The answer gave a quota-like response even though the retrieved chunks did not contain that policy.
- tr_0030: The answer matched the expected source and the cited chunk contained the claim.
- tr_0022: The answer matched the expected source and the cited chunk contained the claim.
- tr_0001: The answer matched the expected source and the cited chunk contained the claim.
- tr_0027: The answer looked correct, but the output did not include a chunk_id that a reviewer could open.
- tr_0015: The answer gave a quota-like response even though the retrieved chunks did not contain that policy.


## Public benchmark note

A public benchmark would not include our old v1/v2/v3 SDK pages sitting beside each other, so it would miss the wrong-version failure mode.
It would also score final answers more than trace replayability, so missing chunk_id citations could look harmless even though they block review.
Finally, benchmark questions rarely ask private product-limit questions that are absent from the corpus, so they would not reveal our quota invention pattern.