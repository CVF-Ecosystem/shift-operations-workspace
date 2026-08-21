# INTAKE — P4-A3 Application Memory

- Tranche: `P4A3-APPLICATION-MEMORY-2026-08-21`
- Phase: `INTAKE`
- Risk: `R2`
- Author: `INTAKE_AUTHOR`
- Authority: operator delegated the next governed decision after the distinct
  P4-A2 closure commit `422661f`
- BUILD authority: `NOT GRANTED`

## Intent

Build the first bounded application-memory layer: provider-neutral
session/working memory that can retain explicitly admitted, scoped advisory
facts for a short lifetime without becoming canonical operational truth.

## Entry boundary

Each entry must bind an authenticated owner, shift and authorization-scope
digest; a closed purpose code; source/provenance digests; classification;
creation/expiry times; and immutable correction/delete lineage. Reads must
revalidate owner, scope, TTL, deletion/supersession and source validity before
returning anything.

## In scope

- pure `packages/application-memory` contracts and process-local store;
- `SESSION` and `WORKING` layers only;
- deterministic admission, lookup, correction, tombstone deletion and
  sanitized receipts;
- one no-route workspace application composition;
- exact unit/contract/integration/CVF tests and evidence runner mechanics.

## Out of scope

- episodic or semantic memory, embeddings/vector search and autonomous
  learning;
- raw chat history as truth, provider-local memory, hidden prompts or model
  output admitted without provenance;
- durable database/schema/migration, public API/UI, production adapter,
  deployment, commit or push;
- production/customer/RESTRICTED data and cross-user/cross-shift recall.

## Acceptance direction

Fail closed on missing/mismatched identity or scope, expired/deleted/
superseded entries, invalid provenance, unsupported classification/purpose,
over-budget payload and any attempt to mutate an existing entry. Positive
proof must remain bounded to synthetic/local data. A final governance claim
will require a separately authorized real-provider proof after non-consuming
review; BUILD itself receives zero provider calls.

## Initial disposition

`READY_FOR_CONSOLIDATED_INTAKE_REVIEW`; no BUILD or external effect is
authorized.
