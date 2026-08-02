# Agent Handoff — Phase 2 Full-Shift Exit Gate

## Disposition

- Tranche: `P2-FULL-SHIFT-EXIT-2026-08-02`
- Risk: `R2`
- Control-chain phase: `BUILD` repair after independent `REVIEW_FAIL`
- Active role: `REPAIR_WORKER`
- Status: `REPAIR AUTHORIZED — PROVIDER PROHIBITED PENDING PRE-CALL REVIEW_PASS`
- Authorization commit: `def5ec0188f0bdfb6045e5ebbc156147115b89c9`
- Repair amendment commit: `22d6bd7cc28a623bcaf05654724d53dca83405a8`

## Settled predecessor

P2-D is `FREEZE / CLOSED_BOUNDED`: BUILD `6fc4359` and C4 `e1ac14b` are
pushed. P2-D authority does not carry forward. Phase 2 remains `IN PROGRESS`
for this full-shift exit gate only.

## Control chain

- INTAKE: `docs/decisions/INTAKE_2026-08-02_PHASE2_FULL_SHIFT_EXIT.md`
- DESIGN: `docs/decisions/ADR_2026-08-02_PHASE2_FULL_SHIFT_EXIT.md`
- SPEC: `docs/specs/PHASE2_FULL_SHIFT_EXIT_SPEC.md`
- WORK_ORDER: `docs/work_orders/PHASE2_FULL_SHIFT_EXIT_WORK_ORDER.md`
- AUTHORIZATION REVIEW:
  `docs/decisions/PHASE2_FULL_SHIFT_EXIT_WORK_ORDER_AUTHORIZATION_REVIEW.md`
- REPAIR AMENDMENT:
  `docs/work_orders/PHASE2_FULL_SHIFT_EXIT_WORK_ORDER_AMENDMENT_1.md`
- AMENDMENT AUTHORIZATION REVIEW:
  `docs/decisions/PHASE2_FULL_SHIFT_EXIT_AMENDMENT_1_AUTHORIZATION_REVIEW.md`

Independent authorization review closed `P2-EXIT-AUTH-F1` through `F5` and
re-review findings `F6`/`F7` without waiver. Final disposition is
`REVIEW_PASS / APPROVED`: exactly 15 unique BUILD paths (11 NEW, 4 existing).

## Authorized boundary

This is an evidence-only composition tranche. It proves one persisted
scheduled 12-hour lineage through real UI/FastAPI/JWT, bounded offline replay,
polling, handover snapshot, Report approval and atomic freeze; PostgreSQL
reconnect verifies records/receipts/audits. It adds no product/API/schema/
dependency/CI behavior. Twelve hours means scheduled interval, not wall-clock
soak. No production, push/exactly-once/full-offline, Phase 3 or post-Phase-2
claim is authorized.

## BUILD review disposition and provider accounting

Independent BUILD review returned `REVIEW_FAIL` with four accepted findings,
all carried without waiver into Amendment 1: whole-ledger refusal immutability
and isolated prerequisites; producer-bound browser evidence; complete durable
handover/receipt/action-actor binding; and exact committed-task fresh GET
before rendered `IN_PROGRESS` state.

One physical provider call already occurred. It remains immutable evidence but
its admission claim is `INVALIDATED_BY_REVIEW_FAIL`. The amended tranche budget
is exactly two physical calls: the invalidated first call and exactly one
replacement. A third call is forbidden.

## Next governed move

`REPAIR_WORKER` may modify only Amendment 1's 13 finding hosts within the same
final exact 15-path BUILD ceiling. Rerun the complete ordered evidence and a
fresh exact-parent detached rehearsal, then stop for independent repaired-
candidate pre-call review. Provider use remains prohibited until that review
returns `REVIEW_PASS`. Only then may exactly one replacement call occur,
followed by final independent BUILD review. No BUILD commit/push, C4 or Phase 2
closure is authorized before final `REVIEW_PASS`.

## Parked checkpoint

The automatic post-Phase-2 queue remains `PARKED_ONLY_NO_BUILD_AUTHORITY`.
It activates only after this BUILD receives independent review/push and a
separate C4 marks the exit gate and Phase 2 `CLOSED_BOUNDED`.
