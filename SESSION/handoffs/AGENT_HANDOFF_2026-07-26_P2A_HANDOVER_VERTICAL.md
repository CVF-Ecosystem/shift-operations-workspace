# Agent Handoff — P2-A Handover Vertical

## Disposition

- Tranche: `P2A-HANDOVER-VERTICAL-2026-07-26`
- Control-chain phase: approved `WORK_ORDER`, before BUILD
- Roadmap target: P2-A handovers only
- Risk: R2
- Implementation worker: Claude
- Independent reviewer / commit steward / closer: Codex
- Status: `AUTHORIZED_PENDING_G6_BUILD`

## Prior closure

P2A Incident is settled history:

- C3 `eac28f9edcff0ff8e85e14cb8764b603c917fe6b`;
- C4 `db488e0dd0130bdccc38263ea649b75982b6199b`;
- `FREEZE / CLOSED_BOUNDED`.

Do not reopen or batch incident work into this tranche.

## Authorization

- C1: `2134cd88b06db1ee30394e6f65513d0472b8bf40`
- ADR: `docs/decisions/ADR_2026-07-26_P2A_HANDOVER_VERTICAL.md`
- SPEC: `docs/specs/P2A_HANDOVER_VERTICAL_SPEC.md`
- Work Order: `docs/work_orders/P2A_HANDOVER_VERTICAL_WORK_ORDER.md`
- Independent disposition: `REVIEW_PASS`
- Findings closed without waiver:
  - `HOV-AUTH-F1 DIGEST_SHAPE_AMBIGUOUS`
  - `HOV-AUTH-F2 DESTINATION_AUTHORITY_OVERCLAIM`
  - `HOV-AUTH-F3 FREEZE_DESTINATION_DRIFT`

## Exact BUILD boundary

The final C3 ceiling is exactly 39 paths in Work Order section 3. No 40th
path is conditional.

Key invariants:

- handover items are server-derived, never caller-supplied;
- mandatory open sources are Task, CustomerRequest and Incident only;
- exact canonical digest fields/encoding are normative;
- reviewer and receiver are distinct authenticated supervisors;
- no destination-shift personnel-assignment claim;
- destination OPEN/source not-FROZEN and snapshot equality are rechecked at
  review, acknowledgement and freeze;
- report override never bypasses handover;
- OperationalEvent completeness is out of scope because it lacks an
  open/resolved semantic;
- all Python remains <=300;
- legacy `test_shift_close_governance.py` is split through the required shared
  fixture module and its debt entry is removed, not rehashed.

## Mandatory evidence

- focused model/lifecycle/API/ledger/parity/freeze/split tests;
- full non-live suite;
- disposable PostgreSQL 16 migration 001-006 round-trip;
- exact Docker cleanup;
- real provider response after valid JWT sender review, distinct receiver
  acknowledgement and freeze;
- refusal paths observed at zero provider calls;
- sanitized live/build receipts;
- protected report/incident/auth/CVF-core zero diff;
- reviewer-owned rollback rehearsal after BUILD.

## G6 and return

After this C2 push, Claude rehydrates this handoff plus ADR/SPEC/WORK_ORDER,
declares `IMPLEMENTATION_WORKER`, runs every Work Order section 2
precondition, then implements exactly the 39 paths.

Claude performs no stage/commit/push and stops at:

`READY_FOR_INDEPENDENT_HANDOVER_BUILD_REVIEW`

Any stop-condition defect is reported without repair until Codex reviews and
authorizes the next move.

## Claim boundary

Potential closure proves a server-derived, authenticated handover and real
`open_handover_items_linked` freeze prerequisite for open Task,
CustomerRequest and Incident records on InMemoryLedger, SQLite and disposable
local PostgreSQL 16, plus bounded real-provider governance evidence.

It does not implement report approval, OperationalEvent resolution,
destination personnel assignment, UI, production provider routing,
production/managed PostgreSQL readiness, concurrency/load/HA or the complete
Phase 2 exit gate.
