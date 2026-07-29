# Agent Handoff — Shift Create Admission Repair

## Disposition

- Tranche: `SHIFT-CREATE-ADMISSION-REPAIR-2026-07-29`
- Control-chain phase: `DESIGN`
- Risk: `R2`
- Active role: `SPEC_AUTHOR`
- Status: `DESIGN_RECORDED — SPEC_NEXT`

## Settled predecessor

`P2C-OPERATIONS-CONSOLE-READ-SLICE-2026-07-28` is `FREEZE /
CLOSED_BOUNDED`:

- C3a `fe2f31236bec1e1e3bcaddbe15463633b0696ab3`;
- C3b `e24905f3519af50866071fdbf08f1ed57fb06307`;
- C4 `49b4d815d8e3492ba7d5fae3e8a2ebc3addf9641`.

Do not reopen or batch predecessor work into this tranche.

## Intake evidence

Source inspection and an ephemeral `TestClient` probe independently confirmed:

- anonymous `POST /shifts` returns HTTP 200 and calls the ledger directly;
- anonymous `POST /messages` also returns HTTP 200 and trusts a caller-supplied
  sender id;
- neither route currently has a governed create service/permission/audit
  chain.

No provider call was made because INTAKE records current behavior and makes no
new governance-enforcement claim.

## Required DESIGN findings

- `SCR-INTAKE-F1 DIRECT_LEDGER_MUTATION`;
- `SCR-INTAKE-F2 AUTHORITY_UNDEFINED`;
- `SCR-INTAKE-F3 INPUT_CONTRACT`;
- `SCR-INTAKE-F4 ADJACENT_MESSAGE_BYPASS`;
- `SCR-INTAKE-F5 GOVERNANCE_EVIDENCE`;
- `SCR-INTAKE-F6 BACKEND_PARITY`.

Canonical intake:
`docs/decisions/INTAKE_2026-07-29_SHIFT_CREATE_ADMISSION_REPAIR.md`.

## Next governed move

Author and independently review DESIGN. DESIGN must explicitly split or
include the adjacent message bypass. No BUILD, source edit, permission change,
provider call, stage, commit or push authority exists from this handoff.

## DESIGN disposition

ADR: `docs/decisions/ADR_2026-07-29_SHIFT_CREATE_ADMISSION_REPAIR.md`.

- Shift creation and message ingestion are split. Message admission is the
  sole next security tranche, not waived or silently fixed here.
- `POST /shifts` keeps its query contract but must require JWT and route only
  through a new atomic `ShiftService.create`.
- `shift.create` uses the existing role hierarchy with minimum `operator`.
- Create plus actor-bound audit must share one ledger transaction.
- BUILD must prove refusal zero-call behavior, exactly one admitted live
  provider call, InMemory/SQLite rollback and disposable PostgreSQL parity.

Next move: author SPEC. BUILD remains unauthorized.
