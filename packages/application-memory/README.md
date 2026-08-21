# application-memory

Pure P4-A3 session/working application memory layer (tranche
`P4A3-APPLICATION-MEMORY-2026-08-21`).

Stores explicitly admitted, scoped advisory facts for a short lifetime
without becoming canonical operational truth. Owns strict immutable
contracts, deterministic layer policy, a process-local append-only store,
correction/tombstone lifecycle, use-time scope/TTL/source revalidation and
sanitized receipts. Depends only on the standard library, Pydantic and
`retrieval-contracts` - see `pyproject.toml`. Imports no provider SDK, HTTP
client, environment, database or hidden CVF Core.

## What this package does

1. Rejects unknown fields and non-NFC strings on every strict, frozen model;
   closed enums bound layer/purpose/classification/source type/outcome.
2. Binds every entry to an authenticated owner, shift and authorization-scope
   digest; entry ids are UUIDs, every digest is lowercase SHA-256, timestamps
   are timezone-aware UTC, and content is normalized and bounded to 4096
   codepoints / 8192 UTF-8 bytes.
3. Enforces deterministic layer policy: `SESSION` max 8 hours, `WORKING` max
   24 hours, requested TTL positive and within the ceiling, `now >= expires_at`
   is expired.
4. Admits only after a positive source-revalidation result bound to source
   type/id/version/content/provenance digests - caller declarations alone are
   never trusted.
5. Writes append-only and atomically: duplicate id, cross-owner/shift/scope
   access, stale source, expired entry, unsupported purpose/classification or
   budget breach all change zero state.
6. Correction atomically appends one successor and tombstones its active
   predecessor; delete atomically appends one tombstone; races fail closed
   with no partial write.
7. Reads in a fixed order (owner -> shift/scope -> TTL -> tombstone ->
   source revalidation -> deterministic `(created_at_utc, entry_id)` order ->
   limit 1..50), omitting refused items with a sanitized reason/count.
8. Emits sanitized receipts recomputed from their own canonical body,
   containing no content/query/prompt/source body/token/credential/provider
   output.

## What this package does not do

It does not implement episodic or semantic memory, embeddings, autonomous
learning or action, durable database persistence, a public API/UI, a
production provider adapter or deployment. The store is process-local and
advisory only - never canonical operational truth.

## Claim boundary

This package proves a bounded, provider-neutral, process-local session/working
memory composition over synthetic/local evidence. It does not prove
episodic/semantic memory, durable persistence, operational-corpus recall, a
public API/UI, autonomous action, deployment or production readiness.
