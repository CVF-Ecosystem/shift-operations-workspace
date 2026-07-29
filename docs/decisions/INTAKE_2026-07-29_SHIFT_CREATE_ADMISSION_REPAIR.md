# INTAKE — Shift Create Admission Repair

- Tranche: `SHIFT-CREATE-ADMISSION-REPAIR-2026-07-29`
- Control-chain phase: `INTAKE`
- Risk: `R2`
- Status: `INTAKE RECORDED — DESIGN NOT YET AUTHORED`
- Owner boundary: `shift-operations-workspace`

## Request and trigger

After the first P2-C read-only console slice reached `FREEZE /
CLOSED_BOUNDED`, its recorded next move was to repair the parked
unauthenticated `POST /shifts` mutation before any mutation UI is added.

This intake authorizes analysis and design only. It does not authorize BUILD.

## Reproduced current truth

At `HEAD == origin/main ==
49b4d815d8e3492ba7d5fae3e8a2ebc3addf9641`:

- `POST /shifts` has no `Depends(get_principal)`;
- the router accepts `name`, `starts_at` and `ends_at` as query parameters;
- it calls `ledger.create_shift(...)` directly;
- no permission action is defined for `shift.create`;
- no application service owns shift creation;
- no audit record is appended with the mutation;
- an independent ephemeral `TestClient` probe returned
  `ANONYMOUS_SHIFT_CREATE status=200`.

The probe used an in-memory application instance only and persisted no
production data.

## Adjacent finding discovered during intake

`POST /messages` is also unauthenticated, accepts a caller-supplied
`sender_id`, and calls `ledger.add_message(...)` directly. The same ephemeral
probe returned `ANONYMOUS_MESSAGE_CREATE status=200`.

This adjacent finding is not silently absorbed into the shift-create scope.
DESIGN must explicitly choose one of these bounded dispositions:

1. keep this tranche shift-create-only and park message admission as the sole
   next security tranche; or
2. justify a combined mutation-admission repair with separate service,
   permission, audit and evidence requirements for both aggregates.

No claim that “all mutation routes are authenticated” is allowed while either
surface remains open.

## Required DESIGN decisions

- `SCR-INTAKE-F1 DIRECT_LEDGER_MUTATION`: decide the single application-service
  entry point for shift creation and the atomic mutation-plus-audit boundary.
- `SCR-INTAKE-F2 AUTHORITY_UNDEFINED`: define the minimum role and the new
  `shift.create` permission action without changing existing role hierarchy.
- `SCR-INTAKE-F3 INPUT_CONTRACT`: decide whether to preserve query parameters
  for compatibility or introduce a body model with an explicit compatibility
  plan and OpenAPI proof.
- `SCR-INTAKE-F4 ADJACENT_MESSAGE_BYPASS`: explicitly split or include
  unauthenticated message creation; no silent omission or scope expansion.
- `SCR-INTAKE-F5 GOVERNANCE_EVIDENCE`: define refusal-zero-call and admitted
  exactly-one-call live-provider evidence if the tranche claims CVF identity,
  permission or audit is load-bearing.
- `SCR-INTAKE-F6 BACKEND_PARITY`: require InMemory, SQLite and disposable
  PostgreSQL behavior where the accepted design changes persistence/audit
  semantics.

## Non-goals

- frontend mutation controls;
- offline queue or realtime transport;
- user provisioning, refresh/revocation or role-hierarchy redesign;
- per-shift assignment, tenant isolation or new `data_scope` semantics;
- report approval, reporting, AI/RAG/memory/forecasting;
- production or managed-PostgreSQL readiness;
- reopening the closed P2-C read slice.

## Acceptance boundary for INTAKE

INTAKE is complete when DESIGN can resolve F1-F6 without hiding the adjacent
message bypass, weakening existing tests, or inheriting BUILD authority from
the predecessor tranche.

Next move: author DESIGN only. No source, test, contract or catalog change is
authorized by this intake.
