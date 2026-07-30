# Specification — P2-R Operational Report and Freeze Prerequisite

- ID: `P2R-OPERATIONAL-REPORT-FREEZE-PREREQUISITE-SPEC-001`
- Tranche: `P2R-OPERATIONAL-REPORT-FREEZE-PREREQUISITE-2026-07-30`
- Risk: `R2`
- Status: `PROPOSED — SPEC REVIEW NEXT; BUILD NOT AUTHORIZED`

## 1. Scope

Implement the operational `END_SHIFT` Report vertical and replace the
`report_approved` freeze override with a real, current, immutable,
receipt-approved Report prerequisite.

Do not implement P2-C mutation/full UI, P2-D offline/realtime, the full-shift
exit gate, P5-A templates/rendering/PDF/Excel, AI report generation,
assignment/tenant/data-scope, external channels, production deployment, or
managed-PostgreSQL readiness.

Existing migrations 001-006 remain byte-identical.

## 2. Canonical domain and public contract

### R1 — canonical types

`operations_domain.models` owns:

- `ReportStatus`: exactly `DRAFT`, `IN_REVIEW`, `APPROVED`, `FROZEN`;
- `ReportType`: exactly `END_SHIFT`;
- `ReportSourceRef`;
- `ReportSection`;
- `ReportContent`;
- `Report`.

`workspace_api.domain.models` re-exports the same class objects by identity.
No duplicate/subclass model is allowed.

`Report.version` is at least one. `Report.report_type` is `END_SHIFT`.
`Report.is_current` is server-owned.

### R2 — strict content

`ReportContent` contains exactly:

- `schema_version = "1.0"`;
- `sections: list[ReportSection]`;
- `source_manifest: list[ReportSourceRef]`;
- `snapshot_digest: str`.

Every model forbids extra fields. Digests match lowercase
`^[0-9a-f]{64}$`.

The public Report response contains exactly:

- `report_id: UUID`;
- `shift_id: UUID`;
- `report_type: "END_SHIFT"`;
- `version: integer >= 1`;
- `status: ReportStatus`;
- `is_current: boolean`;
- `sections`;
- `source_manifest`;
- `snapshot_digest`;
- `generated_from_cutoff: date-time`;
- `created_at: date-time`.

The public content fields are unpacked losslessly from the database `content`
JSON object. The API does not expose a second nested `content` property.

### R3 — exact sections

`sections` contains exactly six entries in this order:
`operational_events`, `corrections`, `tasks`, `customer_requests`,
`incidents`, `handovers`.

Each entry contains exactly:

- `section_type`, one of the six values above;
- `records`, a list of the canonical JSON serialization for that source type.

Section/type mismatch is invalid. Records contain the complete persisted
canonical domain fields for that type; no caller-defined narrative or
arbitrary extension object is accepted.

### R4 — source manifest

Each included record has exactly one manifest entry:

- `record_type`: `OperationalEvent`, `Correction`, `Task`,
  `CustomerRequest`, `Incident`, or `Handover`;
- `record_id: UUID`;
- `source_version: integer >= 1 | null`;
- `source_digest: lowercase SHA-256`.

`source_version` is the model's persisted `version` for OperationalEvent,
Task, Incident and Handover. It is null for Correction and CustomerRequest,
which have no independent version field.

The manifest order matches section order and record order. Duplicate
`(record_type, record_id)` entries are invalid.

## 3. Snapshot generation and digest

### R5 — generation eligibility

Generation requires:

- verified JWT;
- `report.generate` permission;
- existing parent shift;
- parent status exactly `CLOSED`;
- no existing current Report for initial generation.

The request supplies only `shift_id`. The server owns report id/type/version,
status, current flag, cutoff, content, digests and creation time.

Unknown shift is 404. Non-CLOSED or FROZEN shift is 409. Existing current
Report on initial generation is 409 and points the client to successor
generation.

### R6 — exact source membership

At one server-owned UTC cutoff, include:

- OperationalEvent where `shift_id` matches and state is one of
  `CONFIRMED`, `CORRECTED`, `FROZEN`;
- every Correction whose `record_id` is an included OperationalEvent id;
- every Task whose `shift_id` matches;
- every CustomerRequest whose non-null `shift_id` matches;
- every Incident whose `shift_id` matches;
- every Handover whose `from_shift_id` matches.

Exclude RAW/NORMALIZED/PROPOSED/REJECTED OperationalEvents, all Messages,
approval receipts, audits, users and destination-only handovers.

An empty section is valid. Missing one eligible source or including one
ineligible source is a defect.

### R7 — canonical encoding

Normalize before hashing:

- UUID: lowercase hyphenated string;
- enum: string value;
- datetime: UTC ISO-8601 with `Z`, preserving microseconds when nonzero;
- absent value: JSON null;
- object keys: lexicographic;
- list order: normative order below;
- evidence: `(evidence_id, source_type, source_id, sha256)`;
- JSON bytes: UTF-8, sorted keys, compact separators `(",", ":")`,
  `ensure_ascii=False`.

Record order is:

- events: `(starts_at is null, starts_at, event_id)`;
- corrections: `(created_at, correction_id)`;
- tasks: `(created_at, task_id)`;
- customer requests: `(received_at, request_id)`;
- incidents: `(created_at, incident_id)`;
- handovers: `(created_at, handover_id)`.

Timezone-equivalent datetimes must hash identically. Backend row order must
not affect output.

`source_digest = sha256(canonical source-record JSON)`.

`snapshot_digest = sha256(canonical JSON of schema_version, shift_id,
report_type, sections, source_manifest)`.

Snapshot hash input excludes report id, Report version/status/current flag,
cutoff, Report creation time and lifecycle actors.

### R8 — limits

Each section allows at most 500 records. The complete canonical serialized
`ReportContent` allows at most 2,097,152 UTF-8 bytes.

Any overflow fails with 422 before Report/audit persistence. No truncation,
partial Report, pagination token, or "first 500" success is allowed.

### R9 — revalidation

Submit-review, approval and freeze recompute R6-R8 from current persisted
truth and require:

- exact section membership and order;
- exact manifest membership/version/digests;
- exact overall snapshot digest.

Any difference is stale conflict 409 with no lifecycle or audit mutation.
Recovery is successor generation, which intentionally derives new content
from changed truth rather than requiring the predecessor digest to match.

## 4. Lifecycle, versioning and history

### R10 — forward lifecycle

Only:

- `DRAFT -> IN_REVIEW`;
- `IN_REVIEW -> APPROVED`;
- `APPROVED -> FROZEN`.

Only a current Report may transition. `FROZEN` is terminal. Direct generic
status mutation and backward transition are prohibited.

### R11 — immutable snapshots

After insert, these fields are immutable:

- report id;
- shift id;
- type;
- version;
- content;
- cutoff;
- creation time.

Lifecycle writes may change only `status`. Successor creation may change only
the predecessor's `is_current` from true to false while inserting a new row.
A non-current Report can never become current again.

Both ledger backends reject an attempted immutable-field update before
partial mutation.

### R12 — successor generation

`POST /reports/{report_id}/versions` targets the current Report:

- DRAFT or IN_REVIEW: operator or higher may generate the successor;
- APPROVED: shift supervisor or higher must supply a non-empty, trimmed
  `reason` of 1-1000 characters;
- FROZEN/non-current/frozen parent: 409.

The transaction:

1. revalidates target identity/current/lifecycle/parent state and derives a
   fresh R6-R8 snapshot without requiring predecessor-digest equality;
2. computes `new_version = previous.version + 1`;
3. marks previous `is_current = false`;
4. inserts a new current DRAFT with a fresh id/cutoff/content;
5. appends `report.regenerate` or `report.revoke_approval` audit.

All five results commit or roll back together. Older rows and receipts remain
unchanged history.

### R13 — history reads

`GET /reports?shift_id=<uuid>&include_history=false` returns a list containing
zero or one current Report.

With `include_history=true`, it returns all versions ordered by
`(version DESC, report_id)`, with a hard maximum of 100 rows. More than 100
fails with 422; no silent truncation.

`GET /reports/{report_id}` reads current or historical rows. All Report reads
require a valid JWT but make no assignment/data-scope claim.

## 5. Approval and governed application behavior

### R14 — permissions

Add exactly:

- `report.generate: operator`;
- `report.submit_review: operator`;
- `report.approve: shift_supervisor`;
- `report.revoke_approval: shift_supervisor`.

Do not change role ranking or any existing action.

### R15 — submit review

The service requires current DRAFT, R9 revalidation and
`report.submit_review`, then changes status to IN_REVIEW and appends one
actor-bound `report.submit_review` audit in the same transaction.

### R16 — receipt creation

Existing `POST /approvals` accepts the additional exact pair:

`("Report", "report.approve")`

The server loads the current stored Report and derives:

- `risk_class = "R2"`;
- `record_id = report_id`;
- `target_version = report.version`;
- `payload_digest = report.snapshot_digest`.

Non-current, DRAFT, APPROVED, FROZEN, stale or missing Reports cannot receive
a new approval receipt; only a current `IN_REVIEW` Report can. Receipt
creation retains existing authenticated-user/current-authority,
idempotency, copy, uniqueness, audit and sanitization behavior.

### R17 — approval transition

Approval requires:

- current IN_REVIEW Report;
- `report.approve` permission;
- R9 revalidation;
- receipts auto-collected only for exact
  `(Report, report_id, report.approve, target_version, R2, snapshot_digest)`;
- `assert_approval_satisfied` using fresh current user authority.

The R2 shift-supervisor seat must be filled. The approving transition actor
cannot be the sole receipt approver. Receipts for another report/version/
digest/action/risk, inactive users, downgraded users or the confirmer alone
do not count.

Status APPROVED and one actor-bound `report.approve` audit commit atomically.

### R18 — exact audits

Report audits use `record_type="Report"` and `record_id=str(report_id)`.
Required action/control-chain pairs are:

- `report.generate`: `identity, permission, snapshot, create, audit`;
- `report.regenerate`: `identity, permission, snapshot, version, audit`;
- `report.revoke_approval`: `identity, permission, approval, snapshot,
  version, audit`;
- `report.submit_review`: `identity, permission, lifecycle, snapshot, audit`;
- `report.approve`: `identity, permission, lifecycle, snapshot, approval,
  audit`;
- `report.freeze`: `identity, permission, freeze, audit`.

Before/after state contains only bounded lifecycle/version/current summaries,
not full report content, secrets, JWTs or provider/database values.

## 6. Freeze contract

### R19 — retired override

`FreezeInput` temporarily retains:

- `override_unimplemented_prerequisites: bool = false`;
- `override_reason: str | null = null`.

Extra fields are forbidden. `true` or any non-null reason (including an empty
string) returns 422 with no reads beyond admission and no mutation/audit.
OpenAPI marks both fields deprecated.

No `shift.freeze_override_unimplemented_prerequisites` audit is written after
P2-R.

### R20 — atomic freeze

After verified identity and `shift.freeze` permission, one transaction:

1. re-reads the shift and requires CLOSED;
2. runs real `open_handover_items_linked` readiness;
3. loads the one current END_SHIFT Report by shift/type;
4. rejects zero/multiple current candidates;
5. requires Report APPROVED;
6. applies R9 revalidation;
7. changes Report to FROZEN;
8. changes Shift to FROZEN;
9. writes exact `report.freeze` and `shift.freeze` audits.

Any failure rolls back all four writes. Wrong-shift or historical approved
Reports never qualify.

### R21 — idempotent frozen read

An already-FROZEN shift returns idempotent success only if exactly one current
END_SHIFT Report exists for it and that Report is FROZEN. The call creates no
new audit.

Missing, multiple, non-current-only, or non-FROZEN paired report state returns
409 as integrity drift.

### R22 — concurrent source mutation boundary

Required tested behavior:

- InMemory report generation/revalidation/freeze holds its repository
  transaction lock across source reads and writes;
- SQLite uses a write-reserving transaction equivalent to `BEGIN IMMEDIATE`
  for report mutation/freeze;
- PostgreSQL report freeze runs at SERIALIZABLE isolation and treats a
  serialization/deadlock abort as a controlled 409 after at most three
  bounded retries.

A concurrent child mutation that races final report revalidation/freeze must
not commit together with a stale Report+Shift freeze. Exactly one transaction
wins or the freeze refuses.

This does not claim production load, HA or universal serializability.

## 7. Migration and persistence

### R23 — migration 007

Add only `database/migrations/007_report_history_constraints.sql`.

It:

- adds `reports.is_current boolean`;
- validates existing `(shift_id, report_type, version)` history before adding
  uniqueness and fails on duplicate versions;
- marks only the highest version current for each shift/type;
- sets `is_current` NOT NULL with default true;
- adds CHECK `version >= 1`;
- adds unique `(shift_id, report_type, version)`;
- adds a partial unique index on `(shift_id, report_type)` where
  `is_current = true`;
- is idempotently re-applicable through the repository migration runner;
- does not delete or rewrite existing report content/status/history.

The migration must handle an empty reports table and valid multi-version
history. Ambiguous duplicate versions fail rather than choosing silently.

### R24 — metadata parity

SQLAlchemy metadata matches migrations 002+007 two-directionally for Report
columns, PK/FK, nullability, defaults, status CHECK, version CHECK, composite
unique and current partial index.

SQLite stays portable. PostgreSQL compiles JSONB/UUID/timestamptz and the
partial index correctly. Negative tests prove drift detection.

### R25 — ledger surface

Ledger Protocol, InMemoryLedger and SqlLedger implement:

- `add_report`;
- `get_report`;
- `get_current_report`;
- `list_reports_for_shift`;
- lifecycle-only `put_report`;
- atomic `create_report_successor`.

Every method accepts `unit=None` in the established pattern.

Required parity:

- controlled missing/duplicate/version/current conflicts;
- deterministic list order R13;
- deep-copy isolation for input, returned and read InMemory objects;
- lossless JSON content and timezone-aware timestamp round-trip;
- SQLite/PostgreSQL reconnect proof;
- parent FK/frozen-state behavior;
- immutable-field rejection;
- mutation/audit and successor rollback;
- runtime Protocol conformance.

Report-specific table/store/repository modules are used as needed to keep
each Python file at or below 300 physical lines. No new debt/exception is
allowed.

## 8. HTTP and OpenAPI

### R26 — endpoints

All require verified JWT:

- `POST /reports`, body exactly `{"shift_id": UUID}`, returns 201;
- `GET /reports/{report_id}`, returns 200;
- `GET /reports?shift_id=<uuid>&include_history=<bool>`, returns 200;
- `POST /reports/{report_id}/versions`, body with optional
  `{"reason"?: string|null}`, returns 201;
- `POST /reports/{report_id}/submit-review`, no body, returns 200;
- `POST /reports/{report_id}/approve`, no body, returns 200.

Caller-owned content/lifecycle/version/type/current/cutoff/digest/actor fields
are 422. The router never constructs snapshots, calls ledger mutations,
opens transactions or appends audits directly.

### R27 — controlled failures

Status classes are 401 for invalid authentication; 403 for insufficient
permission/current approval authority; 404 for a missing target; 409 for
lifecycle/current/stale/quorum/duplicate/frozen/integrity/transaction
conflict; and 422 for invalid input, limits, reason/value, or override use.

No raw `IntegrityError`, driver exception, DSN, SQL, stack trace, provider
body, credential or internal host detail escapes through HTTP or evidence
summaries.

### R28 — contract compatibility

Tighten `packages/workspace-contracts/reports/shift-report.schema.json` to R1-
R4 with `additionalProperties: false`.

The old required names `report_id`, `shift_id`, `version`, `status`,
`sections` remain. Add the other R2 fields. UUID/date-time/digest formats,
enums, minimum version, exact section order/types and strict nested shapes
are machine-tested.

Preserve a historical fixture of the pre-P2-R loose schema and prove the five
old required names remain. OpenAPI golden review permits only Report
operations/reachable schemas, the additional Report approval target, and the
deprecated freeze-input behavior. Every unrelated operation/schema is stable.

## 9. Evidence requirements

### R29 — focused and full regression

Focused suites cover domain/lifecycle/digests, ledger parity, service/API,
approval receipts, freeze, migration/schema parity, OpenAPI/JSON Schema,
rollback, concurrency boundary and evidence-runner behavior.

The full non-live suite has zero failure/error. Repository validator, catalog,
session/mirror, file-size, JSON/YAML, secret, diff and workspace doctor gates
pass with no new warning.

### R30 — disposable PostgreSQL 16

The owned runner applies migrations 001-007 and reapplies them. It proves:

- migration/metadata parity and constraints;
- generate/read/history/reconnect;
- lifecycle and exact content/digest round-trip;
- Report receipt binding and approval;
- stale/duplicate/current/version refusals;
- report/audit rollback;
- atomic Report+Shift freeze with handover readiness;
- concurrent mutation/freeze conflict;
- connection remains usable;
- owned container and captured anonymous volumes are absent after cleanup.

No production/managed-PostgreSQL claim is allowed.

### R31 — live provider governance

The evidence runner exercises real JWT/FastAPI paths and observes provider-call
delta zero for at least: missing bearer, viewer generation, non-CLOSED
generation, stale submit/approve, missing/wrong-version/wrong-digest receipt,
ambiguous/non-current Report, and attempted legacy override.

It then proves a real closed shift, ready handover, generated Report,
independent R2 receipt, approved exact version/digest, durable Report+Shift
freeze and both audits. Only after those facts are read back may exactly one
real provider call occur and return the expected deterministic marker.

Production Report endpoints never call a provider. PostgreSQL proof and
provider proof are separately mandatory.

### R32 — sanitization and cleanup

No provider key, JWT secret/token, Authorization value, database credential/
URL, raw provider body or machine-local secret is printed or stored.
Adversarial failure sentinels prove exception sanitization.

Docker ownership is captured before execution. Cleanup occurs on success,
failure, skip and interruption; pre-existing resources are never removed.

## 10. Acceptance criteria

- **AC-01/02:** R1 identity/serialization and R2-R4 public/content shapes pass.
- **AC-03/04:** R6 membership and R7 stable canonical digests are exact.
- **AC-05/06:** R8 limits fail closed; R10 lifecycle/current guards pass.
- **AC-07/08:** R11 immutability and R12 atomic preserved history pass.
- **AC-09/10:** R13 read order/bounds and only the four R14 actions pass.
- **AC-11/12:** R15 atomic review and exact R16 receipt scope pass.
- **AC-13/14:** R17 quorum separation and R18 bounded audits are load-bearing.
- **AC-15/16:** R19 override retirement and atomic R20 success pass.
- **AC-17/18:** R20 rollback and R21 frozen-integrity behavior pass.
- **AC-19/20:** R22 race exclusion and migration-007 cases pass.
- **AC-21/22:** R24 parity and R25 cross-backend behavior pass.
- **AC-23/24:** R26-R28 HTTP, schema, OpenAPI and unrelated stability pass.
- **AC-25/26:** non-live regression and PostgreSQL R30 proof pass.
- **AC-27/28:** all refusal calls are zero; one call follows durable proof.
- **AC-29/30:** sanitization/gates and exact changed-set ceiling pass.
- **AC-31/32:** reviewer rehearsal cleans up; closure uses only R33.

Any bypass, caller-authored snapshot, mutable history, stale approval,
ambiguous current Report, partial freeze/audit, raw backend exception, secret
exposure, Docker ownership uncertainty, required extra path or unrelated
regression is a STOP condition.

## 11. Claim boundary

### R33 — permitted closure statement

Only after independent BUILD review may this tranche claim:

> A closed shift can be frozen only with a current, immutable, server-derived
> `END_SHIFT` Report whose exact version and snapshot digest have a valid R2
> approval; Report freeze, Shift freeze, handover readiness, and actor-bound
> audits are atomic on the proven backends.

It may not claim report rendering/export, AI-generated operational truth,
production provider routing, managed/production PostgreSQL, assignment/
tenant/data-scope, P2-C, P2-D, the full-shift exit gate, Phase 2 completion,
production concurrency/load/HA, or report types beyond `END_SHIFT`.

## 12. Next gate

An authorization reviewer must compare this SPEC to the intake, ADR, current
source/migrations/contracts and existing evidence architecture.

`REVIEW_PASS` permits WORK_ORDER authoring only. It does not authorize BUILD,
implementation edits, provider calls, Docker/PostgreSQL, stage, commit or
push.
