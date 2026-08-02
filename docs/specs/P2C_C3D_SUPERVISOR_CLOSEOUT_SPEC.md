# SPEC — P2-C C3d Supervisor Closeout

- ID: `SPEC-P2C-C3D-SUPERVISOR-CLOSEOUT-2026-08-02`
- Parent SPEC: `SPEC-P2C-MUTATION-FULL-UI-2026-07-31`
- Checkpoint: `C3d`
- Risk: `R2`
- Status: `SPEC_REVIEWED`

`MUST`, `MUST NOT`, `SHALL` and `SHALL NOT` are normative. This checkpoint
inherits parent R22-R29 and AC-23..AC-35 without weakening them.

## 1. Requirements

### R1 — No backend contract change

C3d MUST change no backend/domain/ledger/database/migration/OpenAPI source.
Every rendered action MUST call an existing real route through the existing
authenticated, sanitized, no-retry request primitive.

### R2 — Staffing control plane

The UI MUST load the existing minimal staffing shifts and active users without
using client role ranking. A 403 MUST hide/disable staffing authority without
changing operational state. For a chosen staffing shift it MUST list current
assignment history, assign only a selected active `user_id`, and revoke only
with the stored assignment id/version. It MUST display ACTIVE/REVOKED history
without inventing delete or edit semantics.

Staffing success MUST refresh staffing targets/users/assignments and the
ordinary assignment-scoped shift list. Operational records MUST NOT be fetched
through the staffing exception. If the refreshed ordinary list no longer
contains the selected shift, selection and all retained operational records
MUST be cleared before the UI can present that shift again.

### R3 — Complete event state

Operational state MUST retain all returned events. The existing timeline MUST
continue showing confirmed events only. Supervisor confirm/correction target
selection MUST use the complete selected-shift event collection and current
stored version.

### R4 — Approval target matrix

Approval receipt creation MUST support exactly the five pairs accepted by the
existing POST route:

- `OperationalEvent` + `event.confirm` from a visible selected-shift Event;
- `OperationalEvent` + `event.correct` from a visible selected-shift Event;
- `Task` + `task.create` from an explicitly entered stored intent id;
- `Incident` + `incident.acknowledge` from a visible selected-shift Incident;
- `Report` + `report.approve` from the current selected-shift Report.

The payload MUST contain only `record_type`, `record_id`, and `action`. The UI
MUST NOT render or retain an approval payload digest, approver identity,
receipt id as authority, approval target version/risk/satisfied role or
caller-declared shift. Existing Report snapshot/source digests remain part of
the read DTO and are not approval authority. A successful or idempotent
response is followed by a fresh operational read and, for the four pairs the
existing readiness endpoint supports, a sanitized readiness read.

Capabilities are advisory only. The absence of `approval.create` from the
current capability action list MUST NOT suppress all receipt controls or be
treated as a client-side refusal; POST `/approvals` remains authoritative.

### R5 — Supervisor lifecycle matrix

The UI MUST expose only these legal candidates, with the backend authoritative:

- confirm Event when state is not already `CONFIRMED`/`FROZEN`;
- acknowledge Incident when status is `REPORTED`;
- review Handover when `DRAFT`; acknowledge when `REVIEWED`;
- approve current Report when `IN_REVIEW`;
- create a successor with required reason to revoke approval only when current
  Report is `APPROVED`;
- freeze Shift only when current status is `CLOSED`;
- correct an Event only after the selected Shift is `FROZEN`.

Every versioned/status transition MUST send the exact stored precondition.
Handover acknowledge MUST be proven refused without destination assignment and
allowed only after a real destination assignment. No incoming-handover list
claim is permitted.

### R6 — Freeze prerequisites

Freeze MUST send only `expected_version`. The retired override fields MUST be
absent from TypeScript DTOs, rendered controls, request bodies and browser
traffic. The UI MUST present controlled prerequisite conflict text without
claiming success or offering a bypass.

### R7 — Mutation and refresh semantics

Every control MUST reuse or exactly preserve C3c one-in-flight, success/
conflict refresh, stale-response suppression and outcome-unknown lockout.
There MUST be no automatic mutation retry, persistent queue, service worker,
background sync, polling or realtime subscription. Selection changes MUST
reset ephemeral supervisor form and mutation state.

### R8 — Accessibility and sanitization

All controls MUST be keyboard operable and labelled; help/error text MUST be
associated; pending/result states MUST be announced; focus MUST reach bounded
failure feedback. UI/log/receipt/test output MUST contain no token, password,
DSN credential, URL userinfo/query/fragment, provider body, raw exception,
payload digest or raw policy internal.

### R9 — Real-browser proof

Pinned Playwright Chromium MUST exercise every R2-R7 action against built Vite
and real FastAPI routes on an owned disposable SQLite database. Browser proof
MUST include wrong-role, unassigned, stale, missing-approval, wrong-destination
assignment, frozen-parent and retired-override cases, plus storage/queue/retry
absence and static asset HTTP 200 checks. Browser unavailability is a blocker,
not a skip.

### R10 — Fresh live governance proof

A dedicated sanitized runner MUST observe a call counter at zero for every
refusal, then verify the final durable assigned supervisor closeout state and
actor-bound audit records before exactly one real provider call. The receipt
MUST identify model/endpoint class/status/call count without key, bearer,
request body, raw response, secret URL component or raw exception.

### R11 — Regression and repository proof

Frozen frontend install, typecheck, all frontend tests, production build, full
Python non-live tests, focused runner tests, a fresh disposable PostgreSQL 16
migration/reapply/live matrix over the runner's current pinned backend targets
through C3b2, exact-parent rehearsal, session, catalog, file-size, repository,
JSON, diff, doctor and cleanup gates MUST pass. C3c/C3d add no backend target;
the PostgreSQL runner and protected backend remain byte-identical. The exact
changed set MUST equal the approved Work Order ceiling. PostgreSQL evidence
remains local/disposable, not production.

### R12 — Closure boundary

C3d BUILD MUST NOT edit roadmap/status/continuity to claim closure. Only after
independent `REVIEW_PASS` and push may a separate C4 sync mark P2-C
`CLOSED_BOUNDED`. P2-D and full-shift exit remain open; Phase 2 remains
`IN PROGRESS`.

## 2. Acceptance criteria

- **AC-01:** R1 protected backend/OpenAPI boundary has zero diff.
- **AC-02:** staffing discovery works for an unassigned supervisor while
  operational reads remain assignment-scoped.
- **AC-03:** assign/revoke uses server-derived history/version, refreshes both
  staffing and ordinary shift views, and self-revoke clears selected-shift
  operational state rather than retaining stale disclosure.
- **AC-04:** all events are retained for supervisor targets while the timeline
  remains confirmed-only.
- **AC-05:** all five R4 approval pairs hit the real API with the exact
  three-field payload and no digest/authority leakage.
- **AC-06:** Event/Incident/Handover/Report/Shift/Correction success paths hit
  the real routes with exact preconditions.
- **AC-07:** destination assignment is mandatory for acknowledge.
- **AC-08:** Report revocation uses successor creation with reason; no fake
  endpoint or client status mutation exists.
- **AC-09:** freeze traffic contains only expected version and no override.
- **AC-10:** refusal matrix leaves domain/audit/receipt/provider effects zero.
- **AC-11:** one-in-flight, refresh, selection reset, stale suppression and
  outcome-unknown lockout pass without retry/queue/storage/realtime.
- **AC-12:** accessibility and sanitized controlled-state proof passes.
- **AC-13:** real Chromium/static-smoke C3a-d matrix passes with no mock API.
- **AC-14:** fresh provider evidence satisfies R10 ordering and call counts.
- **AC-15:** full regression, exact-parent rehearsal, repository gates,
  changed-set equality and cleanup pass.
- **AC-16:** no P2-D/full-shift-exit/Phase-2 or excluded claim appears.

## 3. Stop conditions

STOP on continuity/parent drift, dirty baseline, missing browser/provider,
outside or unnecessary path, file-size overflow, backend change, fake or
unwired control, client authority, retired override, digest/secret leak,
nonzero refusal provider call, ambiguous repeat without fresh read, mocked
governance route, incomplete cleanup or unexplained regression. Repair needs a
reviewed DESIGN->SPEC->WORK_ORDER amendment before BUILD resumes.
