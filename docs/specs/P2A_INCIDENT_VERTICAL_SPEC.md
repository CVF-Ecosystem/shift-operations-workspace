# Specification — P2-A Incident Vertical

ID: `P2A-INCIDENT-SPEC-001`
Tranche: `P2A-INCIDENT-VERTICAL-2026-07-26`
Risk: R2
Status: APPROVED

## 1. Scope and prohibitions

The tranche implements incidents only. It must not implement handovers,
reports, frontend, channel/provider routing, refresh/revocation, admin user
provisioning, or alter existing event/task/customer/shift behavior.

No migration, model, route or test may be added for handovers. The existing
freeze override remains unchanged.

## 2. Domain requirements

### R1 — canonical model

`operations_domain.models` owns `IncidentStatus` and `Incident`. The
workspace-api model shim re-exports the same objects (`is`, not an equivalent
redefinition).

Status values are exactly:

`REPORTED`, `ACKNOWLEDGED`, `MITIGATING`, `RESOLVED`, `CLOSED`.

### R2 — lifecycle

Allowed transitions:

- REPORTED -> ACKNOWLEDGED
- ACKNOWLEDGED -> MITIGATING
- ACKNOWLEDGED -> RESOLVED
- MITIGATING -> RESOLVED
- RESOLVED -> CLOSED

All others fail. CLOSED is terminal. Generic transition must not perform
REPORTED -> ACKNOWLEDGED; only the acknowledgement action may do so.

### R3 — contract

`incident.schema.json` must require the existing public fields:
`incident_id`, `shift_id`, `risk_class`, `summary`, `status`, and constrain
risk/status to canonical values. Optional runtime fields may be documented
without weakening those required fields.

## 3. Schema and persistence

### R4 — migration 005

Migration 005 creates exactly one `incidents` table with:

- UUID primary key;
- non-null shift FK;
- native `risk_class`, default R1;
- summary, optional description and owner;
- exact status CHECK, default REPORTED;
- version >= 1;
- timezone-aware created_at.

It is idempotently discoverable by the existing migration runner. Existing
migrations remain byte-identical.

### R5 — SQLAlchemy parity

The metadata table matches migration 005 two-directionally for table/columns,
PK/FK, nullability, type family, risk native enum, status CHECK and defaults.
SQLite stays portable; PostgreSQL compiles risk as native `risk_class`, not
VARCHAR. Negative tests prove the parity assertion fails on drift.

### R6 — ledger parity

Both ledgers implement add/get/list-for-shift/put. Required behavior:

- duplicate id fails consistently;
- missing id raises KeyError;
- returned records are copies/reconstructed objects;
- frozen parent blocks add and put;
- evidence round-trips;
- mutation plus audit rolls back atomically;
- list is scoped to exact shift and deterministic.

`Ledger` runtime protocol conformance remains true.

## 4. Governance behavior

### R7 — report

Minimum role: operator. Domain: `equipment_incident`.

Report must:

- reject unknown action/insufficient role/out-of-scope domain;
- store Incident, evidence and audit in one unit of work;
- audit action `incident.report`, record type `Incident`;
- never accept caller-controlled status/version/approver fields at HTTP.

### R8 — acknowledge

Minimum role: shift_supervisor. It loads the stored incident inside the unit
of work, derives current risk/version, verifies REPORTED -> ACKNOWLEDGED,
checks evidence sufficiency, server-collects exact-scope receipts, re-derives
fresh authority, enforces quorum/self-approval rules, updates version and
audits atomically.

Receipt creation accepts the exact new pair
`("Incident", "incident.acknowledge")`, derives risk/version from the stored
Incident and uses `payload_digest = NULL`.

Stale-version, wrong-action, wrong-record, wrong-risk, inactive/demoted,
fabricated and self-only receipts cannot authorize acknowledgement.

### R9 — post-ack transition

Minimum role: operator. It rejects REPORTED, checks lifecycle, blocks a frozen
parent shift, increments version and commits mutation plus audit atomically.
Audit action is `incident.transition`.

### R10 — API

All five ADR endpoints require verified JWT principal through the existing
dependency. Error mapping:

- auth 401/403;
- missing incident/shift 404;
- lifecycle/frozen/version conflict 409;
- malformed/extra payload 422.

OpenAPI must expose the canonical request/response schemas and no approvals
field on incident requests.

## 5. Split/file constraints

### R11 — hard file limits

Python <= 300; TS/TSX/JS/JSX <= 200. No exception/debt update.

Required delegation:

- incident Table builder in `_incident_tables.py`;
- SQL methods in `_incident_store.py` mixin;
- in-memory methods in `_incident_repository.py` mixin.

`tables.py`, `sql_ledger.py`, and `repository.py` receive wiring only. Any
implementation that moves bulk incident logic into those files fails review
even if the numeric guard happens to pass.

### R12 — coherent tests

New test modules are split by concern: vertical governance, schema parity,
ledger persistence, OpenAPI, live-evidence runner. No catch-all test file.

## 6. Live evidence

### R13 — PostgreSQL

Run the official disposable PostgreSQL runner after migration 005. Evidence
must prove:

- PostgreSQL 16 identity;
- 001-005 apply and idempotent reapply;
- incidents pg_catalog/type/CHECK/FK parity;
- incident/evidence/audit round-trip across reconnect;
- constraint refusal leaves connection usable;
- exact container and captured anonymous volume absent.

Incident live cases live in
`tests/integration/test_incident_postgres_live.py`. The existing
`test_sql_ledger_postgres_live.py` remains byte-identical. The runner may
change only its pytest target list so both coherent modules execute inside the
same owned container; runner tests pin that target list and all existing
redaction/cleanup behavior.

### R14 — provider-bound governance

The live runner invokes a real configured provider exactly once only after a
real R2 incident acknowledgement succeeds through the real FastAPI/JWT route
chain (TestClient transport is acceptable for the local API process; the
provider response itself must be real and non-mocked). Both approver and
confirmer principals come from valid signed bearer tokens, not constructed
caller-supplied Principal objects.
Before that:

- insufficient evidence must refuse with zero provider calls;
- missing/fabricated/stale or self-only approval must refuse with zero calls;
- genuine authenticated durable receipt plus distinct confirmer must pass.

The expected provider token is deterministic. The receipt records endpoint
family/model/status/token only, never secret values or Authorization headers.
Missing credentials returns a truthful prerequisite/block status, never PASS.

### R15 — no secret leakage

Provider key and PostgreSQL credential are environment/process-local only.
Failure stdout/stderr, JSON summaries and receipts are sanitized.

## 7. Acceptance criteria

- **AC-01:** exact Incident model/status identity and serialization pass.
- **AC-02:** lifecycle positive/negative/terminal matrix passes.
- **AC-03:** migration discovery/idempotency and exact schema pass.
- **AC-04:** native PostgreSQL risk enum parity positive/negative pass.
- **AC-05:** Ledger protocol and both backend semantics pass.
- **AC-06:** frozen-parent and reference constraints match across backends.
- **AC-07:** report persistence/evidence/audit atomicity pass.
- **AC-08:** acknowledgement risk/evidence/approval/version binding pass.
- **AC-09:** fabricated/stale/self/inactive/demoted receipts fail.
- **AC-10:** transition lifecycle/freeze/audit atomicity pass.
- **AC-11:** HTTP auth/errors/extra-field refusal pass.
- **AC-12:** OpenAPI and incident JSON Schema contracts pass.
- **AC-13:** full non-live suite has zero failure/error.
- **AC-14:** real PostgreSQL 16 incident suite has zero skip/failure/error.
- **AC-15:** provider-bound evidence PASS with refusal call-count zero and
  success call-count one.
- **AC-16:** file-size, catalog, session, validator, diff and doctor gates pass.
- **AC-17:** exact authorized BUILD changed set; protected paths untouched.
- **AC-18:** rollback rehearsal restores the C2 parent and its baseline gates.
- **AC-19:** handover/report/freeze semantics remain byte-identical.
- **AC-20:** receipt claim remains bounded and sanitized.

Any production/schema/approval/security defect or any secret-bearing output is
a STOP condition requiring independent review before repair.

Independent authorization disposition: `REVIEW_PASS`; requirements AC-01
through AC-20 are approved without waiver on 2026-07-26. BUILD remains gated
by the Work Order and C2 continuity push.

## 8. Amendment 1 — repair requirements

Status: APPROVED

The original requirements remain intact and gain the following executable
clarifications:

- **R4-A:** `Incident.version` rejects values below 1. Migration 005 and the
  SQLAlchemy incidents table carry equivalent named `version >= 1` CHECK
  constraints. Positive and negative model, SQLite and live PostgreSQL tests
  prove the invariant and schema-parity tests fail when either side drifts.
- **R6-A:** both ledgers reject duplicate add with the same controlled
  exception type/message and reject put of a missing incident with
  `KeyError`. List reconstructs evidence on both backends and orders by
  `(created_at, incident_id)` so equal timestamps are deterministic. Tests
  exercise both backends rather than accepting a generic SQL exception.
- **R10-A:** the repository-wide OpenAPI golden changes only for the five
  authorized incident operations:
  `POST /incidents`, `GET /incidents`,
  `GET /incidents/{incident_id}`,
  `POST /incidents/{incident_id}/acknowledge`, and
  `POST /incidents/{incident_id}/transition`, plus their reachable canonical
  schemas. The old golden path is authorized for this reviewed delta only.
- **R15-A:** all provider-derived error/response strings are sanitized before
  return, print or receipt rendering. The exact configured key, bearer/JWT
  material, URL userinfo, query and fragment are removed. Receipts store only
  a safe provider endpoint family/host description. Tests inject exact
  sentinel secrets into an HTTP error body, exception text and endpoint and
  prove absence from returned summaries, stdout/stderr and the receipt.
- **R15-B:** provider-call accounting resets for each runner invocation and
  records actual calls; refusal-path claims are not hard-coded substitutes
  for an observed counter. A repair invalidates the prior live receipt as
  closure evidence: fresh PostgreSQL and real-provider runs must replace it
  before re-review can pass.

The sanitization/provider/receipt implementation is split into
`scripts/_incident_live_evidence_support.py`; the existing runner remains
under 300 physical lines without compression. AC-01 through AC-20 remain the
acceptance criteria, now evaluated with these clarifications.

Independent amendment disposition: `REVIEW_PASS`. No waiver is granted for
`INC-REV-F1` through `INC-REV-F5`.
