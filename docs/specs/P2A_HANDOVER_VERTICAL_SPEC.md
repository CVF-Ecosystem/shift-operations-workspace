# Specification — P2-A Handover Vertical

ID: `P2A-HANDOVER-SPEC-001`
Tranche: `P2A-HANDOVER-VERTICAL-2026-07-26`
Risk: R2
Status: APPROVED — BUILD GATED BY C1/C2

## 1. Scope

Implement handovers and the real `open_handover_items_linked` freeze
prerequisite. Do not implement reports, frontend, channels, AI routing,
refresh/revocation, admin provisioning or OperationalEvent resolution.

Existing migrations 001-005 remain byte-identical.

## 2. Domain requirements

### R1 — canonical types

`operations_domain.models` owns:

- `HandoverStatus`: exactly `DRAFT`, `REVIEWED`, `ACKNOWLEDGED`;
- `HandoverItem`;
- `Handover`.

Workspace API shims re-export the same objects by identity.

Required public aggregate fields retain the contract names:
`handover_id`, `from_shift_id`, `to_shift_id`, `items`, `acknowledged`.
`acknowledged` is derived from status and cannot contradict it.

### R2 — lifecycle

Only:

- DRAFT -> REVIEWED;
- REVIEWED -> ACKNOWLEDGED.

ACKNOWLEDGED is terminal. Generic or caller-controlled status mutation is
prohibited.

### R3 — source snapshot

The exact mandatory source set is:

- Task status not in `{DONE, CANCELLED}`;
- CustomerRequest status not `CLOSED` and `shift_id == from_shift_id`;
- Incident status not `CLOSED`.

OperationalEvent is not in the mandatory set because no open/resolved field
exists. Empty source sets are valid.

Each item contains a canonical SHA-256 digest of its server-derived source
snapshot. Digest construction is deterministic, order-independent for
evidence identities and identical across backends.

Exact payload:

- Task: `record_type`, `record_id`, `shift_id`, `title`, `description`,
  `status`, `owner_id`, `due_at`, `risk_class`, `evidence`;
- CustomerRequest: `record_type`, `record_id`, `shift_id`, `customer_id`,
  `summary`, `details`, `status`, `source_message_id`, `received_at`,
  `promised_at`, `owner_id`, derived handover `risk_class="R1"`;
- Incident: `record_type`, `record_id`, `shift_id`, `risk_class`, `summary`,
  `description`, `status`, `owner_id`, `version`, `created_at`, `evidence`.

Evidence entries contain `evidence_id`, `source_type`, `source_id`, `sha256`
and sort by that tuple. UUIDs are lowercase strings; datetimes normalize to
UTC ISO-8601; absent values are null. Serialize UTF-8 JSON with
`sort_keys=True` and separators `(",", ":")`; store lowercase SHA-256 hex.

### R4 — shift and actor invariants

- source/destination shifts exist and differ;
- destination status is OPEN;
- source is not FROZEN;
- source/destination state is rechecked at create, review, acknowledge and
  freeze;
- review and acknowledgement require shift_supervisor or higher;
- reviewer and receiver IDs differ;
- stored actor IDs come only from verified JWT principals;
- stale snapshot, invalid lifecycle or frozen source fails with conflict.

No assignment registry exists. Acceptance proves only that the receiver is a
distinct authenticated supervisor; it must not claim destination-shift staff
assignment.

## 3. Schema and persistence

### R5 — migration 006

Migration 006 contains CREATE-only, idempotently re-applicable statements for:

- native PostgreSQL enum `handover_status`;
- `handovers`;
- `handover_items`.

`handovers` includes UUID PK, from/to shift FKs, status, creator/reviewer/
receiver IDs, review/ack timestamps, version >=1 and created timestamp.

`handover_items` includes UUID PK, handover FK, exact source-type CHECK
(`Task`, `CustomerRequest`, `Incident`), source UUID/digest, snapshot fields,
native risk_class, and uniqueness per handover/source.

### R6 — metadata parity

SQLAlchemy matches migration 006 two-directionally for tables, columns,
PK/FK, nullability, defaults, enum names/values, CHECKs and uniqueness.
SQLite stays portable; PostgreSQL compiles both enums as native types with
`create_type=False`. Negative tests prove drift detection.

### R7 — ledger parity

Both backends implement:

- add/get/list handover;
- put handover;
- derive current open-work snapshot for a shift.

Required behavior:

- duplicate aggregate/item fails in the same controlled shape;
- missing ID raises KeyError;
- returns are copies/reconstructed objects;
- items and evidence round-trip;
- list order is deterministic;
- source/destination/FK rules match;
- mutation plus audit rolls back atomically;
- source snapshot comparison is backend-identical.

List order is exactly `(created_at, handover_id)`. Actor ID columns are text,
not user FKs: they preserve the verified JWT subject/audit identity without
inventing an assignment or provisioning constraint. Polymorphic source IDs
are not database FKs; service-side source derivation/revalidation is the
load-bearing reference check.

Ledger runtime protocol conformance remains true.

## 4. Application behavior

### R8 — create

Minimum role operator. Request accepts only from/to shift IDs. The service
validates shifts, derives items, persists aggregate/items/evidence and audit
atomically. Audit action: `handover.create`, record type `Handover`.

### R9 — review

Minimum role shift_supervisor. Load and revalidate inside the unit of work,
require DRAFT, set REVIEWED/reviewer/time/version and append
`handover.review` audit atomically.

### R10 — acknowledge

Minimum role shift_supervisor. Load and revalidate inside the unit of work,
require REVIEWED, reject reviewer self-acknowledgement, set
ACKNOWLEDGED/receiver/time/version and append `handover.acknowledge` audit
atomically.

### R11 — freeze

Freeze requires:

1. shift CLOSED;
2. explicit reasoned override for `report_approved`;
3. at least one ACKNOWLEDGED handover from that shift whose source snapshot
   exactly matches current mandatory open work.

The report override cannot bypass handover readiness. Readiness check, freeze
mutation, freeze audit and report-override audit share one transaction.
Override audit text no longer says handover was unchecked.

### R12 — HTTP

All five handover endpoints require verified JWT. Error mapping:

- auth/permission: 401/403;
- missing handover/shift: 404;
- lifecycle, actor, stale snapshot, destination state or freeze conflict: 409;
- malformed/extra/caller-owned fields: 422.

OpenAPI exposes exact canonical request/response schemas. Repository-wide
golden change is only the five handover operations and reachable schemas.

## 5. Split and guard requirements

### R13 — executable limits

Python <=300; TS/TSX/JS/JSX <=200. Host modules named in the ADR receive
wiring only.

The 313-line legacy `test_shift_close_governance.py` must be split into the
original module, `_shift_close_fixtures.py` and
`test_shift_close_freeze_interaction.py`; all three finish <=300. Remove its
exact debt entry from `FILE_SPLIT_DEBT_BASELINE.json`. Do not edit the guard,
approved allowlist, exception registry or remaining three debt entries.

### R14 — coherent tests

Separate modules own vertical/API behavior, SQL persistence, schema parity,
PostgreSQL live behavior and live-evidence runner behavior. No catch-all file
or readability compression is accepted.

## 6. Live evidence

### R15 — PostgreSQL

The official disposable PostgreSQL runner executes the existing core,
incident and new handover live modules in one owned container.

Evidence proves PostgreSQL 16, migration 001-006 first/reapply counts, native
enum/CHECK/FK/unique parity, aggregate/items/evidence/audit reconnect,
snapshot refusal, rollback and exact cleanup.

### R16 — provider-bound governance

Before the one real provider call:

- missing handover freeze fails with observed zero calls;
- DRAFT/REVIEWED-only handover fails with zero calls;
- self-acknowledgement fails with zero calls;
- stale/omitted source snapshot fails with zero calls;
- genuine sender review plus distinct receiver acknowledgement plus report
  override succeeds through valid JWT HTTP routes.

Only then call the configured provider exactly once and require the
deterministic expected token.

### R17 — sanitization

Provider key, JWT, PostgreSQL credential and URL credentials remain process/
environment local. Exact secret, Bearer/JWT patterns, URL userinfo/query/
fragment, raw DSN and generated DB password cannot appear in returned
summaries, stdout/stderr or receipts. Failure-path sentinel tests are
mandatory.

## 7. Acceptance criteria

- **AC-01:** exact model/status/shim identity and serialization.
- **AC-02:** lifecycle matrix and terminal behavior.
- **AC-03:** contract required fields and caller-owned-field prohibition.
- **AC-04:** migration discovery/idempotency and exact two-table schema.
- **AC-05:** native enum/CHECK/FK/unique two-directional parity.
- **AC-06:** both ledger backends have identical CRUD/error/copy/order behavior.
- **AC-07:** exact open-work membership and digest parity.
- **AC-08:** item evidence persistence and atomic create/audit.
- **AC-09:** authenticated review and distinct receiver acknowledgement.
- **AC-10:** stale/new/closed/mutated source invalidates prior snapshot.
- **AC-11:** freeze cannot bypass handover with report override.
- **AC-12:** freeze/readiness/audits are atomic.
- **AC-13:** HTTP auth/error/extra-field behavior.
- **AC-14:** OpenAPI and JSON Schema exact contract.
- **AC-15:** legacy oversized test split and debt entry removed.
- **AC-16:** full non-live suite has zero failure/error.
- **AC-17:** PostgreSQL 16 live suite has zero skip/failure/error.
- **AC-18:** real provider evidence has refusal zero calls and success one.
- **AC-19:** file-size/catalog/session/validator/diff/doctor gates pass.
- **AC-20:** exact authorized changed set and protected-path zero diff.
- **AC-21:** reviewer rollback rehearsal restores C2 baseline and gates.
- **AC-22:** report/UI/channel/event-resolution claim boundaries remain intact.
- **AC-23:** no destination personnel-assignment claim is made without an
  assignment registry.

Any production/schema/freeze/identity/security defect, secret-bearing output,
required extra path, Docker ownership uncertainty or existing regression is a
STOP requiring independent review before repair.

## 8. Independent authorization disposition

`HOV-AUTH-F1 DIGEST_SHAPE_AMBIGUOUS`,
`HOV-AUTH-F2 DESTINATION_AUTHORITY_OVERCLAIM` and
`HOV-AUTH-F3 FREEZE_DESTINATION_DRIFT` were repaired without waiver.

Disposition: `REVIEW_PASS`; AC-01 through AC-23 are approved on 2026-07-26.
BUILD remains gated by the Work Order and pushed C1/C2 commits.
