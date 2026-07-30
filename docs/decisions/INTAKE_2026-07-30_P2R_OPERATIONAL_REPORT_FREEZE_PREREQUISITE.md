# INTAKE — P2-R Operational Report and Freeze Prerequisite

- Tranche: `P2R-OPERATIONAL-REPORT-FREEZE-PREREQUISITE-2026-07-30`
- Control-chain phase: `INTAKE`
- Risk: `R2`
- Status: `INTAKE RECORDED — DESIGN NOT YET AUTHORED`
- Owner boundary: `shift-operations-workspace`

## Request and trigger

The operator selected the roadmap order:

`P2-R → P2-C mutation/full UI → P2-D offline/realtime → full-shift exit gate`.

This intake opens only P2-R: a canonical operational Report vertical and a
real `report_approved` freeze prerequisite. It does not open P2-C, P2-D,
Phase 5 reporting/export, or inherit DESIGN, SPEC, WORK_ORDER, BUILD,
provider-call, commit, or mutation authority from any closed tranche.

Settled predecessors remain closed:

- P2A incidents and handovers;
- P2B authentication and approver-identity reconciliation;
- shift-create admission;
- internal-message admission.

## Reproduced current truth

At clean `HEAD == origin/main ==
ba9917a06dc8f2ff04bd5c42fb6b59f0d94d8590`:

- migration `002_tasks_customers_reports.sql` already creates `reports` with
  `report_id`, required `shift_id`, free-text `report_type`, `version`,
  lifecycle status (`DRAFT`, `IN_REVIEW`, `APPROVED`, `FROZEN`), JSONB
  `content`, `generated_from_cutoff`, and `created_at`;
- `operations_domain` has no `Report` or `ReportStatus`;
- SQLAlchemy metadata has no reports table mapping;
- Ledger Protocol, InMemoryLedger and SqlLedger have no report methods;
- workspace-api has only a reports README stub, no router/application service,
  and `main.py` includes no reports router;
- reporting-engine and report-generation worker surfaces are README/stub only;
- `shift-report.schema.json` requires only `report_id`, `shift_id`, `version`,
  `status`, and an unconstrained `sections` array, while the migration uses
  `report_type`, `content`, and `generated_from_cutoff`;
- domain/workflow docs say a report draft uses confirmed/corrected/frozen
  records, carries cutoff/version/approval/evidence, and is reviewed then
  approved;
- freeze policy requires `shift_closed`, `report_approved`, and
  `open_handover_items_linked`;
- `open_handover_items_linked` is load-bearing, but
  `ShiftService._UNIMPLEMENTED_PREREQUISITES` still contains only
  `report_approved`;
- freeze currently requires an explicit reasoned override, writes an override
  audit saying `report_approved not checked`, and then freezes without reading
  any Report;
- approval receipt creation accepts Event confirm/correct, Task create, and
  Incident acknowledge only; no Report action exists;
- no deterministic rule selects the approved Report when multiple rows exist,
  and the migration has no uniqueness constraint preventing multiple approved
  versions for one shift/report type.

Inspection was read-only. No provider call, secret read, external service,
Docker/PostgreSQL run, production data access, source/test/schema edit, stage,
commit, or push occurred.

## Boundary conflict

P2-R is an operational record required to finish a shift and make freeze
truthful. It is not the Phase 5 reporting engine:

- P2-R owns Report lifecycle, stored content/snapshot provenance, governed
  review/approval, durable parity, and freeze readiness;
- P5-A later owns presentation/template generation and PDF/Excel export;
- P2-R must not claim PDF/Excel generation, forecasting, AI authorship,
  production analytics, or full reporting-engine completion.

The existing migration, contract and docs are not equivalent. DESIGN must
select one canonical runtime shape and explicitly reconcile the others rather
than treating their current overlap as a finished contract.

## Required DESIGN decisions

- `P2R-INTAKE-F1 CANONICAL_REPORT_SHAPE`: reconcile migration fields,
  `shift-report.schema.json`, domain docs and API shape; decide `report_type`,
  structured content/sections, version, cutoff, evidence/provenance and strict
  validation without silently breaking existing contracts.
- `P2R-INTAKE-F2 LIFECYCLE_AND_IMMUTABILITY`: define allowed transitions
  across `DRAFT → IN_REVIEW → APPROVED → FROZEN`, edit/version rules,
  post-approval mutation behavior, and post-freeze correction semantics.
- `P2R-INTAKE-F3 SNAPSHOT_PROVENANCE`: define exactly which confirmed,
  corrected and shift-bound records enter content at
  `generated_from_cutoff`, how deterministic ordering/digests are computed,
  and how stale or missing data is detected.
- `P2R-INTAKE-F4 REVIEW_AND_APPROVAL_AUTHORITY`: define verified-JWT roles,
  permission actions, self-approval policy, whether durable approval receipts
  are reused, exact target-version/payload binding, and actor-bound audits.
- `P2R-INTAKE-F5 FREEZE_BINDING`: replace the override with a real check that
  selects exactly one eligible approved Report for the shift, rejects
  missing/ambiguous/stale/wrong-shift/wrong-version reports, and shares the
  same transaction boundary as handover readiness and freeze.
- `P2R-INTAKE-F6 BACKEND_PARITY`: define report mapping and methods on
  Protocol/InMemory/SQLite/PostgreSQL, controlled duplicate/conflict behavior,
  deep-copy semantics, reconnect proof, atomic rollback, and whether migration
  002 is sufficient or a new migration is unavoidable.
- `P2R-INTAKE-F7 HTTP_AND_FAILURE_CONTRACT`: define report create/read/review/
  approve operations and controlled 401/403/404/409/422 outcomes, including
  frozen parent shift, invalid lifecycle, invalid content, stale version,
  missing approval, and ambiguous report selection.
- `P2R-INTAKE-F8 COMPATIBILITY_AND_HISTORY`: preserve historical OpenAPI/
  schema proofs, decide additive versus breaking changes, and prevent a report
  implementation from changing settled incident/handover/message semantics.
- `P2R-INTAKE-F9 EVIDENCE_AND_CLAIM`: require focused/full regression,
  cross-backend rollback/parity, disposable PostgreSQL 16 and exact cleanup;
  because closure will claim permission/approval/freeze governance is
  load-bearing, require fresh real-provider evidence with refusal zero-call
  behavior and exactly one call only after a genuine durable admitted path.

## Scope questions DESIGN must answer

- Whether `report_type` is a fixed end-shift value or a governed enum/set.
- Whether report content is generated deterministically at create time,
  submitted by a caller and server-validated, or separated into draft
  construction and review endpoints.
- Whether approval is one authenticated `report.approve` action or requires a
  risk/quorum receipt despite the existing reports table having no risk field.
- Whether an approved report becomes immutable immediately or only when the
  shift freezes.
- Whether the report row must transition to `FROZEN` atomically with the
  shift.
- Whether a database uniqueness/partial-index rule is needed to guarantee one
  active/approved report per shift/report type/version.
- How `sections` in the JSON Schema maps to migration `content` without
  claiming the current loose schema is already authoritative.

These are DESIGN decisions, not assumptions granted by this intake.

## Non-goals

- P2-C mutation/full UI;
- P2-D offline queue, sync conflict resolution, websocket/SSE or realtime;
- Phase 5 templates, PDF/Excel rendering, scheduled reports or forecasting;
- AI report generation, RAG, memory, provider-generated operational truth;
- external/channel message ingestion;
- reopening incidents, handovers, authentication, approval reconciliation,
  shift-create or internal-message closures;
- production/managed PostgreSQL, HA, load, backup/restore or deployment proof.

## Claim boundary

This intake claims only that the current report/freeze surfaces were inspected
and the missing operational Report model/persistence/API/approval plus the
override-only `report_approved` prerequisite were confirmed from source.

It does not claim Report is implemented, the override is removed, freeze is
fully prerequisite-backed, any report is approved, P2-R/Phase 2 is complete,
or a reporting engine exists.

## Acceptance boundary for INTAKE

INTAKE is complete when DESIGN can resolve `P2R-INTAKE-F1` through
`P2R-INTAKE-F9` without:

- equating the current migration, loose JSON Schema and prose model;
- letting caller-supplied content/identity become approved operational truth;
- allowing more than one ambiguous approved report to satisfy freeze;
- checking approval outside the freeze transaction;
- hiding InMemory/SQL/PostgreSQL divergence;
- folding P2-C, P2-D or P5-A into this tranche;
- inheriting BUILD authority from closed predecessors.

Next move: author DESIGN only. No production source, test, schema, migration,
contract, provider, Docker/PostgreSQL, stage, commit, or push authority is
granted by this intake.
