# ADR — P2-A Incident Vertical

Date: 2026-07-26
Tranche: `P2A-INCIDENT-VERTICAL-2026-07-26`
Risk: R2
Status: APPROVED

## 1. Intake

Phase 1 is closed. The next roadmap lane is the remaining P2-A work:
incidents and handovers. Neither domain has a migration table or runtime
vertical. They are deliberately split:

- this tranche implements **incidents only**;
- handovers remain a successor tranche because they also replace the
  `open_handover_items_linked` freeze override with a real prerequisite.

Combining both would mix two schemas, two lifecycles, two APIs and a freeze
semantic change in one BUILD. That conflicts with the repository's enforced
split-file and bounded-tranche discipline.

## 2. Decision

### 2.1 Incident record

Add migration `005_incidents.sql` and one canonical `Incident` model:

- `incident_id: UUID`
- `shift_id: UUID`
- `risk_class: RiskClass`
- `summary: str`
- `description: str | None`
- `status: IncidentStatus`
- `owner_id: str | None`
- `evidence: list[EvidenceRef]` stored through `evidence_links`
- `version: int`
- `created_at: datetime`

`IncidentStatus` values:

`REPORTED -> ACKNOWLEDGED -> MITIGATING -> RESOLVED -> CLOSED`

`ACKNOWLEDGED` may move directly to `RESOLVED`; `CLOSED` is terminal.

### 2.2 Report first, govern acknowledgement

An operator must be able to report an incident immediately. Reporting is not
the protected acceptance decision.

`incident.report`:

`identity -> permission -> domain_lock -> persist -> audit`

It creates a `REPORTED` record, persists supplied evidence atomically with the
incident and audit, and rejects any write under a frozen parent shift.

`incident.acknowledge`:

`identity -> permission -> risk -> evidence -> approval -> lifecycle -> persist -> audit`

It is the protected decision that the organization accepts the incident into
the governed operational workflow. For R2+, approval receipts are created by
authenticated approvers against the already-persisted target:

- `record_type = "Incident"`
- `action = "incident.acknowledge"`
- `record_id = incident_id`
- `target_version = current incident.version`
- risk is derived from the stored Incident
- no caller-supplied approver identity or receipt list

This reuses the durable receipt architecture. It does not create a second
creation-intent mechanism.

`incident.transition` handles only post-acknowledgement progress:

- `ACKNOWLEDGED -> MITIGATING | RESOLVED`
- `MITIGATING -> RESOLVED`
- `RESOLVED -> CLOSED`

It runs identity, permission, lifecycle, frozen-parent protection, mutation
and audit atomically. `REPORTED -> ACKNOWLEDGED` is accepted only through the
dedicated acknowledgement action.

### 2.3 Persistence

Migration 005 owns the schema. SQLAlchemy metadata must mirror it exactly:

- native PostgreSQL `risk_class` binding via the existing variant;
- shift FK;
- exact status CHECK;
- version and timestamps;
- no `metadata.create_all()` as migration evidence.

Both InMemoryLedger and SqlLedger expose:

- `add_incident`
- `get_incident`
- `list_incidents_for_shift`
- `put_incident`

They return copies/reconstructed models, block frozen-shift mutations, persist
evidence, and keep mutation plus audit atomic.

### 2.4 File-split architecture

Existing near-limit files are wiring surfaces only:

- `tables.py` delegates the incident table to `_incident_tables.py`;
- `sql_ledger.py` inherits `_IncidentStoreMixin`;
- `repository.py` inherits `_IncidentRepositoryMixin`;
- no touched Python file may exceed 300 physical lines;
- the legacy debt baseline and exception registry are read-only.

This is an architectural requirement, not a suggestion to the worker.

### 2.5 API

- `POST /incidents`
- `GET /incidents/{incident_id}`
- `GET /incidents?shift_id=<uuid>`
- `POST /incidents/{incident_id}/acknowledge`
- `POST /incidents/{incident_id}/transition`

Request models forbid extra fields. Caller-supplied approvals, approver
identity, target version, and risk-derived authority are prohibited.

### 2.6 Evidence

Because closure asserts CVF governance behavior, mock/TestClient results are
insufficient on their own. BUILD must produce:

1. SQLite/InMemory parity and atomicity tests;
2. real disposable PostgreSQL 16 migration-created-schema round-trip;
3. a real provider call bound to a successful governed R2 acknowledgement,
   with refusal paths proving zero provider calls;
4. sanitized evidence receipts with no key, Authorization header, generated
   database credential, or raw DSN.

## 3. Rejected alternatives

- **Incidents plus handovers in one tranche:** rejected as overbroad.
- **Approval before incident reporting:** rejected because reporting urgent
  facts must not wait for quorum.
- **Caller-supplied approvals:** prohibited by the closed P2B reconciliation.
- **Incident creation intents:** unnecessary because the reported Incident is
  already a durable approver-visible target.
- **Generic strings without lifecycle/CHECK parity:** rejected; it would move
  invariants out of the domain and database.
- **Adding methods directly into near-limit files:** rejected by the hard
  split guard and by design.

## 4. Claim boundary

Closure may claim one governed incident vertical on InMemoryLedger, SQLite and
disposable local PostgreSQL 16, with provider-bound governance evidence. It
does not implement handovers, reports, production deployment/load/HA,
managed-PostgreSQL parity, P2-C UI, refresh/revocation, or a production
provider call from an API endpoint.

## 5. Authorization review findings

Independent review found and repaired before approval:

- `INC-AUTH-F1 OVERBROAD_GUARD_TEST_PATHS`: migration-idempotency and
  file-size guard tests already discover new files automatically; modifying
  them was unnecessary and removed from the changed set.
- `INC-AUTH-F2 LIVE_TEST_SPLIT_CONFLICT`: the existing PostgreSQL live module
  is already 267 lines. Adding incident coverage there would violate the
  300-line ceiling. It is now protected; incident live coverage lives in a
  coherent new module, and the runner receives only a bounded test-list
  extension with a corresponding runner regression test.

Both findings close without waiver.

Independent authorization disposition: `REVIEW_PASS`. Under the operator's
delegated reviewer/approval authority, Codex approves this ADR intact on
2026-07-26. BUILD remains prohibited until the matching SPEC/WORK_ORDER C1
and pre-BUILD continuity C2 are pushed.

## 6. Authorization Amendment 1 — independent BUILD review

Date: 2026-07-26

The first independent BUILD review returns `REVIEW_CHANGES_REQUIRED`.
Five findings close only through repair and independent re-review:

- `INC-REV-F1 OPENAPI_GOLDEN_AUTHORIZATION_GAP`: the intended five-operation
  incident API changes the repository-wide OpenAPI digest, but the existing
  golden test was outside the original 37-path ceiling.
- `INC-REV-F2 LEDGER_PARITY_DIVERGENCE`: InMemory duplicate add overwrites,
  the SQL backend exposes a backend exception, missing put is not normalized,
  and deterministic list ordering lacks an incident-id tie-break.
- `INC-REV-F3 SQL_LIST_EVIDENCE_LOSS`: SQL get reconstructs evidence but SQL
  list silently returns incidents without their evidence.
- `INC-REV-F4 VERSION_INVARIANT_ABSENT`: `version >= 1` is stated by R4 but
  enforced by neither the canonical model nor migration/metadata CHECK.
- `INC-REV-F5 LIVE_EVIDENCE_SANITIZATION_GAP`: raw provider error/response
  text and a configurable raw endpoint can reach the receipt; the existing
  test passes only already-clean fixture data.

The repair keeps the split-file decision. A new
`scripts/_incident_live_evidence_support.py` owns provider HTTP,
sanitization, safe endpoint description and receipt rendering; the runner
remains a coherent orchestration facade. The existing repository-wide
OpenAPI golden test may be updated only after proving the delta is exactly
the authorized incident contract. No blind digest refresh is accepted.

This amendment adds exactly two paths to the final C3 ceiling:

1. `tests/unit/test_p2b_openapi_contract.py`
2. `scripts/_incident_live_evidence_support.py`

The final C3 changed set is therefore exactly 39 paths. No handover, report,
freeze, auth/JWT, prior migration, CVF core or continuity implementation path
is authorized. Codex independently approves this amendment under the
operator-delegated reviewer/work-order authority. Repair remains prohibited
until the matching SPEC and Work Order amendments are committed and pushed.
