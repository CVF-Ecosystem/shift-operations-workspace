# ADR Addendum — P2-C C3a1 Legacy Runner Ceiling Repair

- Tranche: `P2C-MUTATION-FULL-UI-2026-07-31`
- Checkpoint: `C3a1`
- Phase: `DESIGN AMENDMENT`
- Risk: `R2`
- Status: `REVIEW_PASS — CLOSED_WITHOUT_WAIVER`

## Finding

`P2C-C3A1-BUILD-BLOCK-F1 LEGACY_SHIFT_CREATE_RUNNERS_OUTSIDE_CEILING`:
the C3a1 BUILD correctly stopped with `BLOCKED_WORK_ORDER_CEILING` after
`ShiftService.create` began requiring a persisted active creator.

Source inspection proves two existing live-governance runners call that
service directly and would fail outside their monkeypatched unit-test context:

- `scripts/run_shift_create_live_governance_evidence.py`;
- `scripts/run_message_admission_live_governance_evidence.py`.

The first blocked draft added an autouse monkeypatch only to
`test_shift_create_live_evidence_runner.py`. That makes the test instantiate a
seeded ledger while leaving the real CLI runner broken. It is not acceptable
regression proof and must be removed.

File-size inspection also found four already-authorized test hosts over the
hard 300-line limit: message admission 310, shift-create admission 315,
shift-create live-runner test 308 and P2B OpenAPI 347. These do not require new
paths: fixtures can be compacted line-neutrally, and assignment OpenAPI
constants/strip logic belong in the already-authorized new
`test_assignment_openapi_contract.py` rather than being duplicated.

## Decision

Add exactly the two live-runner paths above to the C3a1 ceiling, increasing it
from 48 to 50 unique paths. Each runner seeds only the exact persisted active
user identities it already authenticates before calling ShiftService.create.
No permission, JWT, assignment or provider ordering is weakened.

The four overflowing test hosts must return to <=300 lines using only their
already-authorized paths. No split file, exemption or debt entry is allowed.

No requirement, claim, checkpoint boundary or other path changes. C3a1 remains
blocked until this amendment and its authorization review are pushed.
