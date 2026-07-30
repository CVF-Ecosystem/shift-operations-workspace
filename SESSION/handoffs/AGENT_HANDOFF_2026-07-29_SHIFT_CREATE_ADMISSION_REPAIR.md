# Agent Handoff — Shift Create Admission Repair

## Disposition

- Tranche: `SHIFT-CREATE-ADMISSION-REPAIR-2026-07-29`
- Control-chain phase: `WORK_ORDER`
- Risk: `R2`
- Active role: `ORCHESTRATOR / REVIEWER / COMMIT_STEWARD`
- Status: `WORK_ORDER_REVIEW_PASS — C1_THEN_C2_NEXT`

## Operator role assignment

- Codex: `ORCHESTRATOR`, `REVIEWER`, later `COMMIT_STEWARD`;
- Claude: future `IMPLEMENTATION_WORKER` or bounded `REPAIR_WORKER` only.

Codex does not perform BUILD. Claude does not review, self-approve, stage,
commit or push. This assignment keeps the reviewer independent of the future
implementation worker while preserving the provider-neutral role contract.

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

## SPEC disposition

SPEC:
`docs/specs/SHIFT_CREATE_ADMISSION_REPAIR_SPEC.md`.

The proposed specification converts the ADR into 17 requirements and 21
acceptance criteria. It pins:

- the verified-JWT/operator admission and single router-to-service path;
- exact actor-bound `shift.create` audit fields inside the create transaction;
- preserved query parameters and a bearer-security-only OpenAPI delta;
- InMemory, SQLite and disposable PostgreSQL 16 rollback/parity evidence;
- refusal zero-call and admitted exactly-one-call provider evidence;
- a protected zero-line message/Integration-Edge boundary without freezing
  anonymous message behavior as a desired regression contract.

Next move: Codex, as ORCHESTRATOR/REVIEWER, reviews the SPEC against INTAKE,
ADR, source truth and existing evidence architecture. A `REVIEW_PASS` permits
authoring a Work Order only. BUILD, provider calls, source/test/contract
changes, stage, commit and push remain unauthorized.

## SPEC review disposition

Review:
`docs/decisions/SHIFT_CREATE_ADMISSION_REPAIR_SPEC_REVIEW.md`.

- `SCR-SPEC-REV-F1 EVIDENCE_RUNNER_COUPLING_AMBIGUITY` closed without waiver:
  provider evidence now depends on admitted API/audit proof, while R7/R8
  backend/PostgreSQL evidence remains a separate mandatory closure gate.
- R1-R17 and AC-01 through AC-21: `REVIEW_PASS`.
- Focused predecessor probes: 34 passed; current OpenAPI/source/transaction
  truth reproduced; session/catalog/file-size/diff gates PASS.
- Existing PostgreSQL and provider runners are already 300 and 299 lines;
  the Work Order must explicitly authorize any split/new support path.

Next move: author a bounded Work Order with exact changed-set ceiling, G6,
evidence commands, stop conditions and commit ownership. BUILD, provider
calls, implementation edits, stage, commit and push remain unauthorized.

## WORK_ORDER authorization disposition

Work Order:
`docs/work_orders/SHIFT_CREATE_ADMISSION_REPAIR_WORK_ORDER.md`.

Authorization review:
`docs/decisions/SHIFT_CREATE_ADMISSION_REPAIR_WORK_ORDER_AUTHORIZATION_REVIEW.md`.

- exact C3 BUILD ceiling: 19 explicit paths, no conditional 20th path;
- provider evidence uses a new exact runner/support split; closed P2-C
  provider evidence remains read-only;
- PostgreSQL evidence uses one new coherent live test and a line-neutral target
  extension in the existing 300-line owned runner;
- `SCR-WO-AUTH-F1 NON_PORTABLE_FOCUSED_COMMAND` closed without waiver;
- authorization disposition: `REVIEW_PASS`.

Next move: Codex transitions to `COMMIT_STEWARD`, verifies and pushes the
zero-BUILD C1 authorization set. Codex then records a separate C2 pre-BUILD
continuity acknowledgment and pushes it. Claude may declare
`IMPLEMENTATION_WORKER` only after both commits are on `origin/main` and G6
passes. No BUILD or provider call is authorized yet.
