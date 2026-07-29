# ADR — Shift Create Admission Repair

- ADR id: `ADR-2026-07-29-SHIFT-CREATE-ADMISSION-REPAIR`
- Tranche: `SHIFT-CREATE-ADMISSION-REPAIR-2026-07-29`
- Phase: `DESIGN`
- Risk: `R2`
- Status: `PROPOSED — SPEC NEXT; BUILD NOT AUTHORIZED`

## Context

`POST /shifts` is the remaining shift-lifecycle mutation that bypasses the
application-service boundary. It accepts an anonymous request and calls
`Ledger.create_shift` directly, so no authenticated actor, permission decision
or atomic audit record exists.

INTAKE also found anonymous `POST /messages`. Message ingestion has a different
trust boundary: it accepts external/source semantics and a caller-supplied
sender identity. Treating that as a mechanical copy of shift creation would
prematurely decide channel identity mapping and provenance.

## Decision 1 — split the adjacent message bypass

This tranche repairs `POST /shifts` only. Anonymous message creation is parked
as the sole next security tranche after this one.

The split is architectural, not a waiver:

- shift creation is the root of an internal operational lifecycle;
- message ingestion must decide trusted sender mapping, source/channel
  provenance and whether raw input crosses Integration Edge first;
- the current tranche must never claim all mutation routes are authenticated.

## Decision 2 — one governed service entry point

Add `ShiftService.create(name, starts_at, ends_at, principal)`.

The router must:

1. require `principal = Depends(get_principal)`;
2. call `ShiftService.create`;
3. translate `CvfDenied` without calling the ledger directly.

The service must:

1. require permission action `shift.create`;
2. construct the canonical `operations_domain.models.Shift`;
3. use one `Ledger.transaction()` unit;
4. create the shift and append its audit record inside that same unit;
5. return only after both operations commit.

Audit failure must roll back shift creation on InMemoryLedger and SqlLedger.

## Decision 3 — authority

Add `shift.create` to the existing permission map at minimum role `operator`.
This matches routine `event.create`, `task.create`, `incident.report` and
`handover.create`. It does not change role ranking or lower any existing bar.

Viewer and anonymous requests are refused. Higher roles inherit operator
authority through the existing role hierarchy.

## Decision 4 — preserve the HTTP contract

Keep `name`, `starts_at` and `ends_at` as query parameters for this corrective
tranche. Moving them to a JSON body is a breaking API/OpenAPI change with no
security benefit.

The OpenAPI delta must be limited to the new bearer-security requirement on
`POST /shifts`; unrelated paths and schemas must remain byte-stable.

## Decision 5 — evidence model

Because closure will claim identity, permission and audit are load-bearing for
shift creation, BUILD evidence must include:

- anonymous, malformed-token and insufficient-role refusals;
- zero provider calls for every refusal;
- a valid operator JWT creating a shift through the real API/service chain;
- exactly one real provider call only after the admitted mutation/audit proof;
- atomic rollback tests on InMemory and SQLite;
- disposable PostgreSQL 16 create/audit/reconnect and rollback evidence;
- full regression, contract/OpenAPI, catalog, session and file-size gates.

The provider call is governance evidence. The production shift-create endpoint
does not and must not call an AI provider.

## Decision 6 — claim boundary

On successful review this tranche may claim only:

> `POST /shifts` requires a verified JWT, enforces `shift.create` permission,
> and atomically persists the shift with an actor-bound audit record.

It may not claim:

- all mutation routes are authenticated;
- message sender identity is verified;
- assignment, tenant or data-scope authorization;
- frontend mutation support;
- production/managed-PostgreSQL readiness;
- P2-C or Phase 2 completion.

## Findings disposition

- `SCR-INTAKE-F1`: resolved by `ShiftService.create` and no router-ledger call.
- `SCR-INTAKE-F2`: resolved by `shift.create` at operator minimum.
- `SCR-INTAKE-F3`: resolved by preserving query compatibility.
- `SCR-INTAKE-F4`: resolved by an explicit split; message repair is next.
- `SCR-INTAKE-F5`: resolved by refusal-zero-call/exactly-one-admitted-call
  live evidence.
- `SCR-INTAKE-F6`: resolved by InMemory, SQLite and PostgreSQL evidence.

## Next move

Author a testable SPEC. No source, test, permission, contract, stage, commit or
provider-call authority is granted by this ADR.
