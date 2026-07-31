# INTAKE — P2-C Mutation and Full UI

ID: `P2C-MUTATION-FULL-UI-2026-07-31`  
Roadmap lane: `P2-C`  
Control-chain phase: `INTAKE`  
Risk: `R2`  
Status: `INTAKE_COMPLETE — DESIGN_NOT_STARTED`

## 1. Intent and authority

Continue Phase 2 after P2-R by addressing the remainder of P2-C: governed
mutation UI, full operational vertical presentation, and the roadmap's
assignment/tenant/data-scope authorization boundary.

This intake authorizes inspection and continuity only. It does not authorize
DESIGN conclusions, SPEC, WORK_ORDER, BUILD, provider calls, source changes,
staging, commit ownership for a future BUILD, or Phase-2 closure.

## 2. Settled baseline

- P2-C read-only slice is `FREEZE / CLOSED_BOUNDED` at C3a `fe2f312` and C3b
  `e24905f`; it must not be reopened or expanded retroactively.
- Shift-create admission, internal-message admission and P2-R Report/freeze
  are separately closed bounded at `3f9e456`, `ab92f51` and `18e24e5`.
- P2-R C4 closure is pushed at `c738193`; `HEAD == origin/main` and the
  worktree was clean when this intake began.
- Workspace doctor remains `PASS WITH NOTE (24 passed, 1 warning(s))`; the
  sole warning is the accepted bounded legacy catalog-kit note.

## 3. Current source truth

- `workspace-web` authenticates with a short-lived bearer token kept in
  `sessionStorage`, then reads shifts, events, open work, incidents and
  handovers. It has no mutation controls.
- Its shared request helper is GET-only. The only browser POST is login.
- Frontend DTOs cover the read slice but not mutation inputs, messages,
  approval receipts, corrections or operational Reports.
- The end-shift-report, quick-actions, customer-inbox, operations-chat,
  administration and leadership-dashboard feature folders remain stubs.
- Backend mutation routes already exist for shifts, messages, events, tasks,
  customer requests, incidents, handovers, approvals, Reports, corrections,
  close and freeze. Their permissions, lifecycle rules, evidence and approval
  prerequisites differ materially.
- JWT carries `sub` and `role`, but the frontend has no server-backed current-
  principal/capability response and must not become an authority engine.
- No shift assignment or tenant registry exists. `owner_id` fields are record
  data, not proof that a caller may view or mutate a shift. `data_scope` has a
  tested runtime gate but is not load-bearing on these operational routes.
- The offline queue exists as a minimal localStorage helper but remains P2-D
  and is not active authority for this tranche.

## 4. Intake findings

### P2C-MUT-INTAKE-F1 — AUTHORIZATION_FOUNDATION_ABSENT

The roadmap asks for assignment/tenant/data-scope authorization, but the
repository has no assignment/tenant source of truth or server capability
surface. UI hiding cannot close this gap. DESIGN must define the server-owned
authorization model and migration implications, or explicitly split it into
an independently reviewed prerequisite before mutation UI.

### P2C-MUT-INTAKE-F2 — MUTATION_BREADTH_UNBOUNDED

“Full UI” currently spans many distinct governed mutations with different
risk, approval, evidence, version and lifecycle behavior. Authorizing them as
one undifferentiated BUILD would make exact-path review and rollback unsafe.
DESIGN must define an explicit vertical matrix and independently revertible
checkpoints; omission must remain visible rather than represented by fake or
disabled controls.

### P2C-MUT-INTAKE-F3 — CLIENT_CONTRACT_INCOMPLETE

The current hand-written browser DTO and GET-only client cannot express the
existing mutation contracts or their controlled failures. DESIGN must select
a canonical contract strategy, concurrency/version behavior, idempotency
boundary and sanitized error mapping without moving governance into React.

### P2C-MUT-INTAKE-F4 — PRINCIPAL_CAPABILITY_VIEW_ABSENT

The browser only knows that a token exists. Decoding an untrusted token or
duplicating role rules client-side cannot establish authority. DESIGN must
decide whether a server-backed principal/capability response is required and
how controls remain correct when capabilities become stale.

### P2C-MUT-INTAKE-F5 — PHASE_BOUNDARY_COLLISION

The existing localStorage offline queue belongs to P2-D. Mutation retry,
realtime, background sync and offline conflict resolution must not leak into
P2-C. P2-C may show a controlled offline refusal, but durable queued mutation
is excluded.

### P2C-MUT-INTAKE-F6 — END_TO_END_EXIT_PROOF_IS_LATER

P2-C closure cannot itself claim the Phase-2 exit gate. P2-D must close next,
then a separate full-shift run must prove `start → updates → tasks → handover
→ report → freeze` with AI and external channels disabled.

## 5. Boundary carried into DESIGN

DESIGN may cover:

- a server-owned principal/capability and assignment/data-scope foundation;
- explicit mutation UI verticals over already-governed backend services;
- Report review/approval and close/freeze presentation without P5-A export;
- browser contracts, version/conflict handling, controlled refusals,
  accessibility, responsive layout and deterministic refresh after writes;
- locked frontend/Python/PostgreSQL evidence and checkpoint separation.

DESIGN must split the work into separate governed tranches or BUILD
checkpoints if authorization foundation, backend contract expansion and UI
cannot be reviewed and reverted safely together.

## 6. Explicit exclusions

- P2-D offline queue activation, background sync and realtime;
- the full-shift Phase-2 exit run;
- P5-A PDF/Excel rendering/export;
- AI Gateway, Refinery, retrieval/RAG, memory or forecasting;
- external/channel ingestion and outbound delivery;
- refresh/revocation, password reset and real admin user provisioning;
- production/managed PostgreSQL readiness;
- writes to the CVF core or sibling repositories.

## 7. Evidence and claim rules

- UI layout tests may use mocks, but mutation and authorization claims must
  exercise real backend routes and proven persistence paths.
- Any claim that CVF governs an admitted AI/agent action requires fresh real-
  provider evidence after all refusal cases prove zero calls.
- Secrets, bearer tokens and raw transport objects must never enter receipts,
  logs or rendered failures.
- Frontend files remain at or below 200 lines; Python remains at or below 300.
- No assignment, tenant, data-scope, “full UI”, P2-C completion or Phase-2
  completion claim is allowed until a later reviewed SPEC defines and proves
  it exactly.

## 8. DESIGN questions

1. What is the canonical assignment/tenant model, and is tenant separation
   genuinely required for this single workspace or a future contract only?
2. Which mutations form the minimum complete operator/supervisor verticals?
3. Which backend read/capability/contract additions are prerequisites?
4. How are optimistic concurrency, duplicate submit and stale capability
   responses handled without P2-D queuing?
5. Which checkpoints keep authorization foundation, backend APIs and React UI
   independently reviewable and revertible?
6. What exact evidence is required for each checkpoint and final P2-C claim?

## 9. Next governed move

Author and independently review DESIGN resolving F1-F6. No SPEC, WORK_ORDER
or BUILD authority exists. No authority from P2-R or the prior read slice
carries forward.
