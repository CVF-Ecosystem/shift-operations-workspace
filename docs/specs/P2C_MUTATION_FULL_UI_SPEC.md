# SPEC — P2-C Mutation and Full UI

SPEC ID: `SPEC-P2C-MUTATION-FULL-UI-2026-07-31`
Tranche: `P2C-MUTATION-FULL-UI-2026-07-31`
Risk: `R2`
Status: `SPEC_REVIEW_PASS_AFTER_REPAIR`

## 1. Normative sources and claim

This SPEC implements the reviewed parent ADR, DESIGN review and CustomerRequest
concurrency addendum. `MUST`, `MUST NOT`, `SHALL` and `SHALL NOT` are
normative.

The maximum final claim is:

> Within the single `shift-operations-workspace`, authenticated users see and
> mutate only actively assigned shift resources; the React console exposes
> the specified operator and supervisor lifecycle controls while every action
> is re-authorized and audited by the backend on the proven backends.

No multi-tenant, provider-placement `data_scope`, offline/realtime, exactly-
once, production PostgreSQL, external-channel, AI, P5-A export, P2-D,
full-shift-exit or Phase-2 completion claim is permitted.

## 2. Checkpoint contract

- **C3a:** assignment authorization foundation.
- **C3b:** backend read/mutation contract readiness.
- **C3c:** operator mutation UI.
- **C3d:** supervisor closeout UI and bounded P2-C proof.

Each checkpoint MUST receive independent `REVIEW_PASS`, commit and push before
the next begins. Changed sets MUST NOT overlap as pending work. A failure or
scope defect stops that checkpoint; it never borrows a later checkpoint path.

## 3. C3a requirements — assignment foundation

### R1 — Canonical model

`ShiftAssignment` MUST be package-owned and contain exactly the semantic
fields selected by DESIGN: server UUID, shift/user foreign identities,
ACTIVE/REVOKED status, assigned/revoked actor and timestamps, and version >=1.
No tenant field or provider `data_scope` field may be added.

### R2 — Migration and parity

The next migration MUST create assignment storage with foreign keys, status/
version checks and at most one ACTIVE `(shift_id,user_id)` assignment. It MUST
retain revoked history and be idempotently re-applicable. InMemory, SQLite and
PostgreSQL behavior and schema parity MUST match.

Existing shifts MUST receive no inferred assignment. The staffing control
plane MUST be able to discover their minimum identity/status and staff them.

### R3 — Ledger contract

The Ledger Protocol and both backends MUST support add/get/list/revoke/current-
membership queries. Returned models MUST be deep-copy isolated where existing
InMemory conventions require it. Duplicate-active, missing user/shift, stale
version and invalid lifecycle failures MUST use controlled equivalent errors
with no partial write.

### R4 — Atomic shift bootstrap

`ShiftService.create` MUST atomically persist: canonical Shift, creator ACTIVE
assignment and actor-bound audit. Creator identity is server-derived. The
creator MUST exist as a persisted active user. Failure of any write MUST roll
back all three.

### R5 — Staffing authority

`shift.assignment.manage` MUST require `shift_supervisor` or higher. Staffing
routes MUST be:

- `GET /staffing/shifts` — minimal id/name/status only;
- `GET /staffing/users` — active user id/username/global role only;
- `GET /shifts/{shift_id}/assignments`;
- `POST /shifts/{shift_id}/assignments` with target `user_id` only;
- `POST /shifts/{shift_id}/assignments/{assignment_id}/revoke` with required
  `expected_version`.

Target user MUST exist and be active. Actor/timestamps/status are server-
derived. Add/revoke plus audit MUST be atomic. Below-supervisor access is 403.
Successful revoke increments version once. A repeat with the current revoked
version returns the stored assignment unchanged and writes no second audit; a
repeat carrying the pre-revoke version is stale 409.

### R6 — Operational scope

Every shift-bound operational route MUST resolve canonical shift identity
from stored/input data and require current ACTIVE assignment before reading or
mutating. Caller-supplied scope assertions MUST NOT be authority.

The rule applies to:

- shift list/open-work/close/freeze;
- message create and future shift list;
- event create/list/confirm/correct;
- task intent create/get, task create/transition and future lists;
- shift-bound customer-request create/transition and future lists;
- incident report/get/list/acknowledge/transition;
- handover create/get/list/review/acknowledge;
- Report generate/get/list/version/submit/approve;
- approval receipt creation for supported targets.

`POST /shifts` is the bootstrap exception governed by R4. Health/login and
staffing control-plane routes are not operational-resource reads.

### R7 — Cross-shift and nullable rules

Handover create/review MUST require source assignment; acknowledge MUST
require destination assignment. Approval MUST derive its target shift from
the stored target. Customer requests with null `shift_id` MUST remain outside
the shift console and MUST receive no assignment-scope/full-UI claim.

### R8 — Enumeration-safe refusal

Unauthenticated remains 401; coarse permission denial remains 403; missing or
inaccessible operational resource MUST share the same 404 shape; stale
version/lifecycle remains 409; malformed input remains sanitized 422. Scope
refusal MUST occur before mutation/audit/provider call.

### R9 — Session and advisory capabilities

`GET /auth/me` MUST return only verified user id, JWT role and expiry.
`GET /shifts/{shift_id}/capabilities` MUST require assignment and return
advisory allowed action names plus bounded reason categories. It MUST expose no
digest, credential or policy internals. Every mutation MUST re-run all server
gates; capabilities never authorize.

Fixed token TTL/no early revocation remains an explicit limitation. This SPEC
does not claim database deactivation immediately invalidates an issued token.

### R10 — C3a evidence

C3a MUST prove focused/full tests, cross-backend parity, disposable PostgreSQL
16 migration/reapply/rollback/cleanup, legacy-shift staffing recovery, exact-
parent rehearsal, repository gates, and fresh sanitized live governance
evidence: every refusal at zero provider calls, then exactly one call only
after durable admitted assignment-scoped behavior is verified.

## 4. C3b requirements — backend contract readiness

### R11 — Browser-required reads

Add authenticated assignment-scoped deterministic reads:

- `GET /messages?shift_id=...`;
- `GET /tasks?shift_id=...` including terminal history;
- `GET /customer-requests?shift_id=...` for bound requests including terminal
  history;
- `GET /approvals/readiness?record_type=...&record_id=...&action=...` for
  exactly Event/event.confirm, TaskCreationIntent/task.create,
  Incident/incident.acknowledge and Report/report.approve. Response fields are
  record type/id, action, target version, risk class, ready boolean,
  required-role names and satisfied-role names; it MUST exclude payload digest
  and credentials.

Each list MUST use deterministic ordering and a hard maximum of 500. A 501st
matching record MUST fail with controlled 422; silent truncation and pagination
invented during BUILD are forbidden. Existing event/incident/handover/Report
reads MUST be reused.

### R12 — CustomerRequest version

Migration/model/table/ledger/contracts MUST add integer non-null version,
default/backfill 1 and check >=1. Create MUST persist/return 1. Successful
transition MUST compare expected version in-transaction and increment exactly
once. Missing precondition is 422; mismatch is 409; both leave mutation/audit
unchanged. Two-direction parity and PostgreSQL reapply are mandatory.

### R13 — Mutation precondition matrix

The following existing-aggregate actions exposed by C3c/C3d MUST require
`expected_version`: shift close/freeze; event confirm/correct; task transition;
customer-request transition; incident acknowledge/transition; handover review/
acknowledge. Report submit/approve/revoke/version-successor actions MUST
require immutable content `expected_version` plus `expected_status` where the
status changes without increasing content version.

Create/append actions, task-intent creation and idempotent approval-receipt
creation MUST remain outside this version precondition matrix. SPEC review
MUST reject any accidental precondition added to an unchanged route.

Preconditions MUST be JSON body fields, not query parameters or headers:

- close and freeze: `expected_version` (freeze retains the two deprecated
  override fields only at their refused/default-compatible contract);
- event confirm and correction: `expected_version`;
- task/customer-request/incident transition: `target_status` plus
  `expected_version`;
- incident acknowledge, handover review and acknowledge: `expected_version`;
- Report submit/approve: `expected_version` plus `expected_status`;
- Report successor version: existing optional `reason` plus
  `expected_version` and `expected_status`.

### R14 — Atomic stale refusal

Each precondition MUST be checked inside the same application transaction as
mutation and audit. Stale/missing failures MUST produce no domain write, audit,
receipt or provider call. Successful existing-aggregate mutations MUST keep
their established version/lifecycle semantics; Report content history remains
immutable.

### R15 — Contract truth

Pydantic/OpenAPI and small feature-owned TypeScript DTOs MUST agree on every
browser-used required field, enum, security declaration, response and
controlled error. Omitted newly-required preconditions intentionally return
422. Generated monolithic TypeScript files or file-size exemptions are
forbidden.

### R16 — Browser request primitive

The frontend request layer contract MUST support typed JSON body/query,
bearer header and abort signal without logging token/body/raw transport data.
401 clears session; 403/404/409/422 map to controlled categories; ambiguous
network failure maps to outcome-unknown and never auto-retries.

### R17 — C3b evidence

C3b MUST prove route/OpenAPI/contract tests, full regression, InMemory/SQLite
parity, disposable PostgreSQL for changed persistence/query behavior,
assignment refusal on every new route, stale/rollback matrices, exact-parent
rehearsal and repository gates. It MUST change no React mutation feature and
make no UI-completion claim.

## 5. C3c requirements — operator UI

### R18 — Operator verticals

The authenticated selected-shift UI MUST expose: create/select shift; append
internal message; create event; create task intent/task; create/transition
bound customer request; report/transition incident; create handover; generate/
version/submit Report; close shift.

No control may appear as implemented unless it calls the real API. Approval-
needed responses MUST identify the safe next action without exposing digest or
allowing caller-declared approval.

### R19 — State management

One in-flight submit per control. Success and controlled conflict MUST refresh
affected reads/capabilities. Ambiguous network outcome MUST disable repeat
until fresh read. No automatic retry, localStorage queue, background sync or
realtime subscription is allowed.

### R20 — Presentation quality

All controls MUST provide accessible labels, keyboard operation, focus/error
association, pending/disabled state and responsive layout. Empty/loading/
offline/forbidden/not-found/conflict/invalid/server states MUST be distinct but
must not render raw transport or secret-bearing content.

### R21 — C3c evidence

Frozen pnpm install, typecheck, component tests, production build, static HTTP
smoke and real browser E2E against real FastAPI routes are mandatory. Mocks are
allowed only for isolated layout/state tests. Python regression and repository
gates remain mandatory. No supervisor/P2-C-completion claim is allowed.

## 6. C3d requirements — supervisor closeout UI

### R22 — Supervisor verticals

The UI MUST expose: staffing target/list/add/revoke; event confirm; supported
approval receipt creation; incident acknowledge; handover review and
destination-assigned acknowledge; Report approve/revoke; shift freeze; and
post-freeze event correction.

### R23 — Server authority reflection

Controls may be hidden/disabled using advisory capabilities, but direct API
refusal MUST remain authoritative. The UI MUST refresh after assignment,
approval, lifecycle and freeze changes. It MUST display prerequisites without
offering override fields retired by P2-R.

### R24 — P2-C final evidence

C3d MUST run the complete C3a-d regression/e2e/refusal matrix on the authorized
backends, prove no offline queue use, run exact-parent rehearsal and all
repository/doctor gates, and collect fresh sanitized live-provider evidence:
zero calls for every refusal, exactly one call only after the final durable
assigned authorized closeout path is verified.

### R25 — Closure boundary

P2-C may reach `CLOSED_BOUNDED` only after C3a-d independent review/push and C4
truth sync. P2-D remains next. Phase 2 remains open until P2-D and the separate
full-shift exit gate close.

## 7. Cross-cutting requirements

### R26 — File and dependency boundaries

Python <=300 physical lines; TS/TSX/JS/JSX <=200; no new debt/exemption.
Frontend imports no Python/domain/ledger/database code. Backend imports no
React. CVF core and sibling repositories remain read-only.

### R27 — Security and sanitization

No raw key, bearer token, password, DSN credential, URL userinfo/query/
fragment, provider body or raw exception may enter logs, UI, receipts or test
failure output. Refusal evidence MUST prove zero provider call before admitted
proof.

### R28 — Truth surfaces

Each checkpoint updates only status/catalog/control-mapping surfaces whose
source truth changed, using the canonical catalog generator. No roadmap item
is ticked complete before C3d review; C4 remains separate.

### R29 — Worker and commit separation

External IMPLEMENTATION_WORKER receives prompts manually from the operator and
MUST NOT stage, commit, push, self-review or FREEZE. No Claude CLI/control call
is allowed from this session. Codex remains independent REVIEWER and later
COMMIT_STEWARD. Each checkpoint has an exact-path Work Order ceiling.

## 8. Acceptance criteria

- **AC-01:** R1-R3 model/schema/ledger parity passes on both backends.
- **AC-02:** R4 atomic shift+assignment+audit success and rollback pass.
- **AC-03:** R5 staffing role/active-user/version/audit matrix passes.
- **AC-04:** R6 route-scope matrix proves assigned allow/unassigned deny.
- **AC-05:** R7 handover source/destination and nullable-request boundaries pass.
- **AC-06:** R8 enumeration-safe status/body matrix passes.
- **AC-07:** R9 `/auth/me` and advisory capability non-authority probes pass.
- **AC-08:** existing-shift no-backfill plus supervisor recovery passes.
- **AC-09:** C3a PostgreSQL/migration/reapply/cleanup passes with zero skips.
- **AC-10:** C3a provider receipt proves refusal zero-call then exactly one call.
- **AC-11:** R11 new reads are complete, ordered, bounded and assignment-scoped.
- **AC-12:** R12 CustomerRequest backfill/version/stale parity passes.
- **AC-13:** every R13 affected route rejects missing/stale precondition.
- **AC-14:** every route excluded by R13 preserves its prior request contract.
- **AC-15:** R14 stale refusals leave zero domain/audit/receipt mutation.
- **AC-16:** R15 OpenAPI/DTO/contract agreement passes.
- **AC-17:** R16 error/sanitization/no-auto-retry tests pass.
- **AC-18:** C3b PostgreSQL and full regression pass where required.
- **AC-19:** every R18 operator control reaches a real API route.
- **AC-20:** R19 ambiguous outcome requires refresh and never queues/retries.
- **AC-21:** R20 accessibility/responsive/error-state tests pass.
- **AC-22:** C3c real-browser E2E and production build/smoke pass.
- **AC-23:** every R22 supervisor control reaches a real API route.
- **AC-24:** unassigned/wrong-role/stale/frozen/missing-approval UI/API refusals pass.
- **AC-25:** destination assignment is required for handover acknowledge.
- **AC-26:** P2-R override fields are never rendered or accepted as UI authority.
- **AC-27:** offline queue import/storage remains zero in C3c/C3d.
- **AC-28:** C3d fresh provider evidence meets R24 ordering/call-count rules.
- **AC-29:** each checkpoint exact-parent rehearsal restores its true baseline.
- **AC-30:** full Python/frontend suites and all repository gates pass.
- **AC-31:** doctor has no new failure/warning beyond bounded legacy 24/1.
- **AC-32:** exact changed set equals the reviewed Work Order ceiling.
- **AC-33:** `HEAD == origin/main`, clean start/end and zero container residue.
- **AC-34:** final claim matches section 1 and every excluded claim remains absent.
- **AC-35:** C4 is separate; P2-D/full-shift exit/Phase-2 remain open.

## 9. Stop conditions

STOP on continuity drift, dirty/unexpected baseline, unavailable required
Docker/browser/provider evidence, secret exposure, path-ceiling conflict,
file-size overflow, schema/OpenAPI drift, nonzero refusal provider call,
partial rollback, unexplained test regression or pressure to combine
checkpoints. Repair requires reviewed amendment before BUILD resumes.

## 10. Next governed move

Independently review this SPEC against DESIGN, source feasibility and route/
contract completeness. Only SPEC `REVIEW_PASS` authorizes exact-path Work Order
authoring. BUILD remains unauthorized.
