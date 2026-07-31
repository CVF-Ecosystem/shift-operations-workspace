# ADR — P2-C Mutation and Full UI

ID: `ADR-P2C-MUTATION-FULL-UI-2026-07-31`
Tranche: `P2C-MUTATION-FULL-UI-2026-07-31`
Control-chain phase: `DESIGN`
Risk: `R2`
Status: `DESIGN_REVIEW_PASS_AFTER_REPAIR`

## 1. Context

The closed P2-C read slice proves authenticated identity-only reads and a
read-only React console. Later closed tranches added governed shift/message
admission and the Report/freeze prerequisite. P2-C still lacks resource scope,
mutation UI and complete operational closeout presentation.

The intake identified six findings. This ADR resolves them architecturally;
it does not authorize implementation.

## 2. Decision summary

P2-C will remain one roadmap tranche but use four separately authorized,
reviewed, committed and pushed BUILD checkpoints:

1. **C3a — assignment authorization foundation**;
2. **C3b — backend read/mutation contract readiness**;
3. **C3c — operator mutation UI**;
4. **C3d — supervisor closeout UI and bounded P2-C proof**.

C3b cannot begin before C3a receives independent `REVIEW_PASS` and is pushed.
C3c cannot begin before C3b receives independent `REVIEW_PASS` and is pushed.
C3d cannot begin before C3c receives independent `REVIEW_PASS` and is pushed.
No checkpoint may inherit an open changed set from its predecessor.

## 3. D1 — Single-workspace boundary; no fake tenant model

This application currently has one canonical workspace identity:
`shift-operations-workspace`. No tenant lifecycle, tenant administrator,
tenant provisioning flow, tenant-scoped encryption key or tenant retention
policy exists.

Adding a nullable/defaulted `tenant_id` to a few tables would create the
appearance of isolation without enforcing it across every aggregate, receipt,
audit, query and foreign key. That design is rejected.

P2-C therefore implements **per-shift assignment/resource scope inside one
workspace**. It makes no multi-tenant isolation claim. If multi-tenancy becomes
a product requirement, it requires a new cross-system tranche and migration.
At P2-C FREEZE the roadmap/catalog wording must distinguish the completed
assignment scope from excluded tenant isolation.

The existing `cvf_runtime.data_scope` control is also not repurposed. It
governs whether classified content may be sent to a provider placement. It is
not row-level authorization. Operational resource scope belongs to the
workspace API authorization layer and must call the ordinary identity and
permission gates in addition to its assignment check.

This resolves `P2C-MUT-INTAKE-F1` without inventing tenant or CVF semantics.

## 4. D2 — Canonical shift assignment

### 4.1 Entity

C3a adds a package-owned `ShiftAssignment` record with:

- server-generated `assignment_id`;
- `shift_id` and `user_id` foreign keys;
- `status` in `ACTIVE | REVOKED`;
- server-derived `assigned_by`, `assigned_at`, optional `revoked_by` and
  `revoked_at`;
- integer `version` starting at 1.

There may be at most one ACTIVE assignment for `(shift_id, user_id)`. Revoked
history is retained. InMemory, SQLite and PostgreSQL must enforce equivalent
behavior. Assignment mutations and actor-bound audit writes are atomic.

### 4.2 Bootstrap and management

- `ShiftService.create` atomically assigns the authenticated creator to the
  new shift together with shift creation and audit. If any write fails, none
  survive.
- `shift.assignment.manage` requires at least `shift_supervisor`.
- A supervisor may list/manage assignments for any shift as the bounded
  staffing control-plane exception; ordinary operational reads and mutations
  remain assignment-scoped.
- A dedicated staffing endpoint returns only the minimum shift identity/status
  needed to select a staffing target. It is not the operational read endpoint
  and does not return events, work, messages, handovers or Reports.
- Migration creates no inferred assignment for an existing shift because the
  repository has no truthful source for that fact. Existing shifts therefore
  fail closed for operational access until a supervisor uses the staffing
  control plane to assign users. Deployment evidence must prove a supervisor
  can discover and staff such a shift without operational-data access.
- A target user must exist and be active when assigned.
- Revoke is idempotent only for an already-revoked assignment with the exact
  identity; it cannot erase history.

Supervisor-wide staffing authority is explicit and narrow. It does not grant
the supervisor authority to mutate every operational record without an ACTIVE
assignment.

### 4.3 Resource-scope rules

- `viewer` and `operator` list/read only assigned shifts.
- Higher roles also list/read only assigned shifts for operational endpoints;
  their wider authority is available only at assignment-management endpoints.
- Every shift-bound operational read or mutation resolves its canonical
  `shift_id` server-side and requires an ACTIVE assignment before lifecycle,
  risk, approval or persistence work.
- Handover create/review requires source-shift assignment. Acknowledge requires
  destination-shift assignment, closing the prior “identity only, no receiver
  assignment claim” boundary.
- Approval creation resolves the stored target to its shift and requires the
  approver to be assigned there. Caller-supplied shift assertions are refused.
- A customer request with `shift_id = null` is outside this shift console. The
  P2-C UI creates and mutates only requests bound to the selected shift;
  unbound customer-inbox workflow remains a separate future surface.
- Cross-shift operations check each role-specific side explicitly rather than
  using either shift as a proxy for both.

Unknown/inaccessible resources use a uniform not-found response where needed
to prevent shift-id enumeration. Authentication failure remains 401; known
identity without coarse permission remains 403; stale lifecycle/version
remains 409.

## 5. D3 — Server-backed session and capabilities

C3a adds:

- `GET /auth/me`: verified `user_id`, global role and access-token expiry;
- `GET /shifts/{shift_id}/capabilities`: a server-derived advisory list of
  currently visible actions for that principal and shift.

The browser never decodes the JWT as authority and never duplicates the role
ranking. Capabilities are presentation hints only. Every mutation re-runs
identity, permission, assignment, lifecycle, risk, evidence and approval gates
on the server. A capability disappearing between render and submit therefore
produces a controlled refusal, not a bypass.

Capability output contains action names and bounded reason categories, never
secrets, approval digests, other users' credentials or raw policy internals.

This resolves `P2C-MUT-INTAKE-F4`.

## 6. D4 — Mutation concurrency and ambiguous outcomes

Existing versioned aggregate mutations exposed to the UI gain a required
`expected_version`. Services compare it inside the same transaction before
mutation. Report status-only transitions additionally carry
`expected_status`, because immutable Report content versions do not increment
when status changes. Mismatch returns controlled 409 with no partial
mutation/audit.

These required preconditions intentionally tighten the pre-release HTTP
contract. Old mutation requests that omit them fail with controlled 422; they
are never silently treated as an unconditional write. SPEC and OpenAPI tests
must enumerate every affected route and preserve unchanged routes exactly.

P2-C does not add offline replay or a generic idempotency ledger. The browser:

- permits one in-flight submission per control;
- never automatically retries a mutation;
- after an ambiguous network outcome, invalidates local detail and requires a
  fresh server read before enabling another submit;
- refreshes the affected resource/capabilities after every success or
  controlled conflict.

Durable queued commands, replay identifiers and merge/conflict policy remain
P2-D. Create endpoints without existing durable intent support must disclose
the bounded “outcome unknown—refresh before retry” state. This is not an
exactly-once claim.

## 7. D5 — Explicit vertical matrix

“Full UI” means all already-implemented Phase-2 operational lifecycle
verticals needed for a shift, not every stub folder in `workspace-web`.

### C3c operator surface

- create/select shift;
- append internal message;
- create event;
- create task intent/task and display approval-needed refusal;
- create and transition customer request;
- report and transition incident;
- create handover;
- generate/version/submit Report;
- close shift;
- deterministic refresh, validation, accessibility and controlled errors for
  every control above.

### C3d supervisor closeout surface

- list minimal staffing targets and assign/revoke shift members;
- confirm event;
- create durable approval receipts for supported stored targets;
- acknowledge incident;
- review and destination-assigned acknowledge handover;
- approve/revoke Report approval where the backend lifecycle permits;
- freeze shift;
- post-freeze event correction;
- display exact prerequisite/refusal state without a client-side bypass.

Feature folders for leadership dashboard, administration, external customer
portal, external/channel chat, notifications and export remain excluded.
P5-A owns PDF/Excel rendering/export.

This resolves `P2C-MUT-INTAKE-F2` by making every included and excluded
vertical explicit.

## 8. D6 — HTTP contracts and frontend structure

- C3b adds bounded assignment-scoped reads needed by the UI but absent today:
  internal messages, full task history, shift-bound customer-request history,
  and sanitized approval/readiness state for supported targets. Existing event,
  incident, handover and Report reads are reused rather than forked.
- Every new list has deterministic ordering and a hard maximum or explicit
  pagination contract; no silent truncation is permitted.
- FastAPI/Pydantic/OpenAPI remains the executable HTTP source.
- Small feature-owned TypeScript DTOs are allowed; generated monolithic types
  are rejected because the repository's 200-line hard limit must remain
  meaningful.
- Contract/OpenAPI tests compare every browser-used request/response field,
  enum and security declaration to the backend schema.
- The generic browser request helper gains typed JSON bodies, query handling
  and controlled response parsing. It never logs tokens, request bodies or raw
  transport objects.
- React features remain split below 200 lines. `OperationsConsole` becomes a
  coordinator, not a growing all-actions component.
- Mutation state is ephemeral React state. The inactive localStorage offline
  queue is neither imported nor populated.

This resolves `P2C-MUT-INTAKE-F3` and preserves the frontend/backend boundary.

## 9. D7 — P2-D and exit-gate separation

C3c/C3d may render offline status and refuse mutation while disconnected.
They may not enqueue, replay, synchronize in the background or subscribe to
realtime updates. Those behaviors remain P2-D.

Even after C3c, Phase 2 is not complete. P2-D must close, then a separate
full-shift exit-gate tranche must prove `start → updates → tasks → handover →
report → freeze` with AI and external channels disabled.

This resolves `P2C-MUT-INTAKE-F5` and `P2C-MUT-INTAKE-F6`.

## 10. Evidence architecture

### C3a

- focused unit/contract/integration tests;
- full non-live regression;
- InMemory/SQLite parity;
- disposable PostgreSQL 16 migrations, reapply, assignment/resource-scope,
  atomic rollback and cleanup proof;
- real HTTP/JWT refusal matrix showing zero provider calls;
- only after durable admitted assignment-scoped behavior is verified, exactly
  one real provider call with sanitized receipt;
- exact-parent rollback rehearsal and repository gates.

### C3b

- focused API/OpenAPI/contract and cross-backend tests for every browser-used
  read and required mutation precondition;
- assignment refusal on every new/readiness route;
- deterministic list limits, sanitized failures, full non-live regression,
  disposable PostgreSQL proof where persistence/query code changes, exact-
  parent rehearsal and repository gates;
- no frontend source and no UI-completion claim.

### C3c and C3d

- frozen pnpm install, typecheck, unit/component tests and production build;
- real browser E2E against built web plus real FastAPI routes, not mocked
  governance, with a disposable database where the Work Order requires it;
- mocks only for isolated layout/loading/empty-state tests;
- anonymous, wrong-role, unassigned, stale-version, frozen-parent and missing-
  approval refusals where applicable;
- no provider call unless the checkpoint makes a new CVF-governance claim. The
  final P2-C governance claim at C3d requires fresh sanitized real-provider evidence
  after the complete refusal matrix proves zero calls.

Every checkpoint records exact test counts, tool versions, changed paths,
container cleanup and claim boundaries. No secret value or raw credential may
appear in output or receipts.

## 11. Alternatives rejected

### A. UI-only mutation controls

Rejected: identity-only backend reads and absent assignment scope would remain
bypassable by non-browser clients.

### B. Placeholder tenant column

Rejected: creates a false isolation claim without a tenant lifecycle and full
foreign-key/query enforcement.

### C. Reuse `cvf_runtime.data_scope` for row authorization

Rejected: changes the meaning of a provider-placement control and would make
both claims ambiguous.

### D. One combined backend/frontend BUILD commit

Rejected: too broad to review or revert safely and would hide which layer
established authority.

### E. Activate the existing offline queue now

Rejected: crosses into P2-D replay/conflict semantics.

### F. Decode JWT and enforce roles in React

Rejected: client state is not authority and can be bypassed or stale.

## 12. Claim boundary

If all future SPEC requirements and checkpoints pass, P2-C may claim only:

> Within the single `shift-operations-workspace`, authenticated users see and
> mutate only actively assigned shift resources; the React console exposes
> the specified operator and supervisor lifecycle controls while every action
> is re-authorized and audited by the backend on the proven backends.

It may not claim multi-tenant isolation, offline/realtime behavior, exactly-
once mutation, production/managed PostgreSQL readiness, external channels,
AI functionality, report rendering/export, P2-D completion, the full-shift
exit gate or Phase-2 completion.

## 13. Next governed move

Independently review this DESIGN against intake F1-F6, current source and the
roadmap. Only `REVIEW_PASS` authorizes SPEC authoring. No WORK_ORDER or BUILD
authority exists.
