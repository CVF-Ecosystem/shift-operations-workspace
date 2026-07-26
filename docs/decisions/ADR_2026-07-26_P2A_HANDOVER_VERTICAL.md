# ADR — P2-A Handover Vertical

Date: 2026-07-26
Tranche: `P2A-HANDOVER-VERTICAL-2026-07-26`
Risk: R2
Status: APPROVED — BUILD GATED BY C1/C2

## 1. Intake

The incident vertical is `FREEZE / CLOSED_BOUNDED` at C3
`eac28f9edcff0ff8e85e14cb8764b603c917fe6b`. The only next roadmap move is
the remaining P2-A handover domain.

This tranche implements handovers only. It does not implement reports, UI,
channels or AI routing. It does change one existing cross-record invariant:
`open_handover_items_linked` stops being an override and becomes a real
freeze prerequisite. `report_approved` remains unimplemented and retains an
explicit audited override.

## 2. Existing truth and ambiguity resolved

The existing public contract requires:

- `handover_id`;
- `from_shift_id`;
- `to_shift_id`;
- `items`;
- `acknowledged`.

The workflow says: generate carry-over from open work, sender reviews,
receiver acknowledges and responsibility changes are audited. The freeze
policy requires `open_handover_items_linked`.

The repository has no handover migration/model/runtime today. It also has no
reliable open/resolved field for `OperationalEvent`; `DataState.CONFIRMED`
means evidentiary confirmation, not operational resolution. This tranche
must not invent the false rule that every confirmed event is still open.

## 3. Decision

### 3.1 Aggregate and lifecycle

Add migration `006_handovers.sql` with two tables:

- `handovers`;
- `handover_items`.

Canonical domain types:

- `HandoverStatus`: `DRAFT`, `REVIEWED`, `ACKNOWLEDGED`;
- `HandoverItem`;
- `Handover`.

Lifecycle:

`DRAFT -> REVIEWED -> ACKNOWLEDGED`

`ACKNOWLEDGED` is terminal. Review and acknowledgement are separate,
authenticated actions. The acknowledging receiver must differ from the
sender/reviewer.

### 3.2 Server-derived completeness

The caller supplies only `from_shift_id` and `to_shift_id`. It cannot submit,
remove or rewrite `items`, status, actor identity, version or digest.

At creation, the server snapshots the exact open work set for the source
shift:

- `Task`: every status except `DONE` and `CANCELLED`;
- `CustomerRequest`: every status except `CLOSED`;
- `Incident`: every status except `CLOSED`.

Each item stores:

- item and handover IDs;
- source record type and ID;
- server-computed source digest;
- summary, owner, due time and risk snapshot;
- source evidence persisted as `HandoverItem` evidence links.

Task and Incident retain their own risk. CustomerRequest has no risk field,
so its handover snapshot uses `R1`; this is presentation/routing metadata,
not retroactive mutation of the customer-request schema.

The digest is computed from a canonical, server-derived snapshot including
source identity, status, owner, due/promised time, summary and evidence
identities. It prevents a handover from remaining valid after the source
record changes without changing membership.

Exact digest payloads:

- Task: record type/id, shift ID, title, description, status, owner ID,
  due-at, risk class and evidence;
- CustomerRequest: record type/id, shift ID, customer ID, summary, details,
  status, source-message ID, received/promised times and owner ID;
- Incident: record type/id, shift ID, risk class, summary, description,
  status, owner ID, version, created-at and evidence.

Evidence is sorted by `(evidence_id, source_type, source_id, sha256)`. UUIDs
are lowercase strings; datetimes are UTC ISO-8601; absent values are JSON
null. Digest bytes are UTF-8 JSON with sorted keys and compact separators.
The digest is lowercase SHA-256 hex. CustomerRequest's derived `R1` handover
risk is included in its item snapshot.

`OperationalEvent` is deliberately excluded from automatic completeness
until a separately governed open/resolved semantic exists. Events may remain
evidence on Task/Incident items; this tranche makes no claim that all events
are automatically carried forward.

An empty handover is valid when the exact open-work set is empty.

### 3.3 Revalidation and recovery

Review, acknowledgement and freeze each recompute the current open-work
snapshot and require exact equality of `(record_type, record_id, digest)`.
A new, changed, closed or missing source record makes the handover stale and
the action fails with conflict.

Handover snapshots are immutable. Recovery from drift is to create a new
draft. Multiple historical handovers for one source shift are allowed; freeze
accepts only an `ACKNOWLEDGED` handover whose snapshot exactly matches current
open work.

### 3.4 Shift constraints

- source and destination shifts must both exist;
- they must differ;
- destination must be `OPEN`;
- source must not be `FROZEN`;
- handover mutation is prohibited after the source shift freezes.

Creating a handover does not silently change `Shift.status`.
Destination `OPEN` state and source-not-FROZEN state are rechecked at review,
acknowledgement and freeze; a state change invalidates readiness.

The repository has no shift-assignment/member registry. Therefore a valid
receiver acknowledgement proves a distinct authenticated supervisor accepted
the transfer; it does not prove that supervisor was assigned to the
destination shift. That stronger claim requires a later identity/assignment
model and is explicitly outside this tranche.

### 3.5 Governance chains

`handover.create` — minimum role operator:

`identity -> permission -> domain_lock(shift_handover) -> derive snapshot -> persist aggregate/items/evidence -> audit`

`handover.review` — minimum role shift supervisor:

`identity -> permission -> lifecycle -> revalidate snapshot -> persist -> audit`

`handover.acknowledge` — minimum role shift supervisor:

`identity -> permission -> distinct receiver -> lifecycle -> revalidate snapshot -> persist -> audit`

All state mutation, item/evidence persistence and audit writes share one
`Ledger.transaction()`.

### 3.6 Freeze integration

`ShiftService.freeze` continues to require:

- governed closed shift;
- explicit audited override for unimplemented `report_approved`;
- a real freeze-ready handover.

The existing request field `override_unimplemented_prerequisites` is retained
for compatibility but is narrowed to `report_approved` only. It can never
bypass missing, unacknowledged, self-acknowledged or stale handover state.
Audit text must say only `report_approved` was not checked.

The readiness check and shift freeze occur in the same unit of work. This is
atomic for the repository's tested transaction model; production concurrency/
isolation guarantees remain outside the claim.

### 3.7 API

- `POST /handovers`
- `GET /handovers/{handover_id}`
- `GET /handovers?from_shift_id=<uuid>`
- `POST /handovers/{handover_id}/review`
- `POST /handovers/{handover_id}/acknowledge`

Request models forbid extra fields. Items and server-owned lifecycle fields
are response-only.

### 3.8 Persistence and split architecture

Migration 006 owns the schema. SQLAlchemy metadata mirrors it exactly,
including:

- PostgreSQL-native `handover_status` and `risk_class`;
- shift and aggregate foreign keys;
- source-type/version CHECKs;
- unique `(handover_id, source_record_type, source_record_id)`;
- timezone-aware timestamps.

Near-limit host files remain wiring surfaces:

- `_handover_tables.py` builds both tables;
- `_handover_store.py` owns SqlLedger behavior;
- `_handover_repository.py` owns InMemoryLedger behavior;
- every touched Python file stays at or below 300 physical lines.

`tests/cvf/test_shift_close_governance.py` is legacy debt at 313 lines and
must change because its freeze assertions are affected. It must be split
below 300 into:

- the original close-governance module;
- `_shift_close_fixtures.py`;
- `test_shift_close_freeze_interaction.py`.

Its debt-baseline entry is removed. No replacement debt or exception is
allowed.

## 4. Evidence decision

Closure asserts identity/permission/lifecycle/audit/freeze governance, so it
requires:

1. InMemoryLedger and SQLite parity/atomicity;
2. disposable PostgreSQL 16 migration-created-schema round-trip;
3. real-provider evidence bound to a successful authenticated handover review,
   distinct receiver acknowledgement and freeze;
4. refusal paths with observed zero provider calls;
5. sanitized output/receipts and exact Docker cleanup;
6. reviewer-owned rollback rehearsal.

No production endpoint calls a provider. The provider call is an evidence
bridge reached only after the governed local route chain succeeds.

## 5. Rejected alternatives

- **Caller-supplied items:** rejected; omission would make freeze trivially
  bypassable.
- **Treat all confirmed events as open:** rejected; confirmation is not
  resolution.
- **Reuse the old override for handovers:** rejected; it would leave the
  policy prerequisite non-load-bearing.
- **Mutable/refreshable snapshot:** rejected for this tranche; immutable
  snapshots plus new-draft recovery are simpler and auditable.
- **One handover per shift:** rejected; a stale snapshot must be recoverable
  without destructive update.
- **Modify legacy oversized test in place:** rejected by the hard file guard.

## 6. Claim boundary

Potential closure proves an authenticated, durable, server-derived handover
for open Task/CustomerRequest/Incident records on InMemoryLedger, SQLite and
disposable local PostgreSQL 16, and makes `open_handover_items_linked` a real
freeze prerequisite.

It does not implement report approval, automatic OperationalEvent
open/resolved classification, UI, production provider routing, production/
managed PostgreSQL readiness, destination-shift personnel assignment,
concurrency/load/HA or Phase 2's full start-to-freeze exit gate.

## 7. Independent authorization review

Findings repaired before approval:

- `HOV-AUTH-F1 DIGEST_SHAPE_AMBIGUOUS`: exact per-source fields and canonical
  JSON/hash encoding are now normative.
- `HOV-AUTH-F2 DESTINATION_AUTHORITY_OVERCLAIM`: receiver evidence is bounded
  to distinct authenticated supervisor identity; no assignment claim.
- `HOV-AUTH-F3 FREEZE_DESTINATION_DRIFT`: source/destination state is
  revalidated at review, acknowledgement and freeze.

All three close without waiver. Independent authorization disposition:
`REVIEW_PASS`. Under the operator-delegated reviewer/work-order authority,
Codex approves this ADR on 2026-07-26. BUILD remains prohibited until the
matching SPEC/WORK_ORDER C1 and pre-BUILD continuity C2 are pushed.
