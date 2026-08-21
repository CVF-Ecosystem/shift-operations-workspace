# DESIGN — P4-A3 Bounded Application Memory

- Tranche: `P4A3-APPLICATION-MEMORY-2026-08-21`
- Phase: `DESIGN`
- Risk: `R2`
- Author: `DESIGN_AUTHOR`
- Execution base: `422661f`

## Decision

Create pure package `application-memory` plus one no-route application
composition. The package owns contracts/policy/store/receipts; the
application boundary supplies authenticated principal, assignment scope,
clock and source-revalidation callback. It performs no network, environment,
database or provider I/O.

## Model

`MemoryEntryV1` is immutable and contains only:

- UUID entry id; layer `SESSION|WORKING`; closed purpose code;
- owner principal id, shift id and authorization-scope SHA-256;
- classification `PUBLIC|INTERNAL` (RESTRICTED rejected in this tranche);
- canonical source type/id/version/content digest and provenance digest;
- bounded normalized advisory content plus its digest;
- created/expires UTC, policy version and predecessor id when corrected.

Raw prompts, hidden instructions, credentials, provider identifiers and
provider-local conversation state are forbidden fields.

## Admission and lifecycle

Order is fixed: validate request → authenticate/authorize owner+shift → verify
purpose/classification → verify source/provenance → normalize and enforce
size limits → compute expiry → append entry → emit sanitized receipt.

Entries never mutate. Correction appends a successor bound to the predecessor
and tombstones the predecessor atomically. Delete appends a tombstone; it does
not erase audit lineage from the process-local store. Reads apply: owner →
shift/scope → active TTL → not tombstoned/superseded → source revalidation →
deterministic order `(created_at, entry_id)` and result limit.

## Layer policy

- `SESSION`: maximum TTL 8 hours, session-scoped advisory context.
- `WORKING`: maximum TTL 24 hours, active-shift work context.
- caller may request a shorter TTL only;
- `now >= expires_at` is expired;
- no background retention job is claimed; expiry is enforced at every read.

## Store and concurrency

`InMemoryApplicationMemoryStore` uses one lock and append-only entry/tombstone
maps. Admission/correction/delete plus receipt facts are atomic in-process.
Duplicate ids, aliasing, predecessor races and double correction/delete fail
closed without partial state. No durability or multi-process claim.

## Receipts

Receipts contain safe ids, enums, versions, timestamps, counts and SHA-256
digests only. They bind request, entry/source/provenance, scope, lifecycle and
outcome. No content body, token, credential or provider response is retained.

## Application composition

`workspace_api.application.application_memory` constructs a verified scope
from the existing authenticated principal/assignment boundary and injects the
store/clock/revalidator. It opens no HTTP route and does not feed memory into
P4-A2 automatically. A later explicit caller may request already-revalidated
entries; chat history is never implicitly recalled.

## Evidence

Tests must cover strict schema, every refusal zero mutation, TTL boundaries,
cross-owner/shift/scope isolation, stale source, correction/delete races,
hash recomputation, no-secret receipts and dependency boundaries. BUILD has
zero provider calls. After independent non-consuming review, one separate
operator checkpoint may authorize a synthetic P4-A2 call proving rejected
memory reaches the provider zero times and admitted memory at most once.

## Claim boundary

Session/working memory only, process-local and advisory. No episodic/semantic
learning, durable store, operational-corpus recall, public API/UI, autonomous
action, deployment or production readiness.
