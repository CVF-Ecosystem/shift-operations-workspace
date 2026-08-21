# SPEC — P4-A3 Application Memory

- Tranche: `P4A3-APPLICATION-MEMORY-2026-08-21`
- Version: `1.0`
- Risk: `R2`

## Requirements

R1. All public Pydantic models use strict fields, forbid extras and are frozen.
Enums are closed; every schema/subschema rejects unsupported keywords.

R2. Entry ids are UUIDs; every digest is lowercase SHA-256; timestamps are
timezone-aware UTC. Content is normalized deterministically and bounded to
4096 codepoints/8192 UTF-8 bytes. Empty content is rejected.

R3. Layer is exactly `SESSION` or `WORKING`; maximum TTL is respectively 8 or
24 hours. Requested TTL must be positive and within the layer ceiling.
Expiry uses `now >= expires_at`.

R4. Purpose is a closed enum: `ACTIVE_TASK_CONTEXT`, `HANDOVER_CONTEXT`,
`OPERATOR_WORKING_NOTE`. Classification is `PUBLIC|INTERNAL`; `RESTRICTED`
and unknown strings fail closed.

R5. Admission requires authenticated owner id, existing assigned shift, exact
authorization-scope digest, and a positive source-revalidation result bound to
source type/id/version/content/provenance digests. Caller declarations alone
are insufficient.

R6. Store writes are append-only and deep-copy isolated. Duplicate id,
cross-owner/shift/scope access, stale source, expired entry, unsupported
purpose/classification or budget breach changes zero state.

R7. Correction atomically appends one successor and tombstones its active
predecessor. Delete atomically appends one tombstone. Double/cyclic/cross-scope
correction and delete/correct races fail closed with no partial write.

R8. Read order is fixed: owner, shift/scope, TTL, tombstone/supersession,
source revalidation, then deterministic `(created_at_utc, entry_id)` ordering.
Limit is 1..50. A refused item is omitted with a sanitized reason/count; no
fail-open partial object may escape validation.

R9. Receipt hashes are recomputed from their own canonical body. Receipts
contain no content/query/prompt/source body/token/credential/provider output.
Positive receipt grammar must match the actual store result; negative writes
must report zero mutations.

R10. Package imports no workspace application, provider SDK, HTTP client,
environment, database or hidden Core. Application composition opens no route,
persists nothing and never recalls memory implicitly into P4-A2.

R11. Tests must reconstruct untrusted nested models from primitive dumps and
cover `model_construct`/hash-recompute adversaries, UTC/TTL edges, Unicode
byte limits, aliasing, concurrency, stale source and all scope mismatches.

R12. BUILD provider/network/install/database/commit/push/deployment counts are
zero. Any final governance-behavior claim requires a separate post-review
real-provider authority and sanitized receipt.

## Acceptance criteria

AC1 strict models/schema and dependency boundary tests pass. AC2 every
negative write is zero mutation. AC3 TTL/scope/source filters fail closed.
AC4 correction/delete concurrency has one winner and coherent lineage. AC5
receipt recomputation and secret scan pass. AC6 focused parent regressions and
full suite pass. AC7 catalog/session/knowledge/file-size/repository/JSON/diff/
doctor gates pass. AC8 exact changed set, staged zero and HEAD base preserved.

## Exclusions

No episodic/semantic memory, embeddings, autonomous learning/action, durable
database, public API/UI, production data/provider adapter or deployment.
