# ADR Addendum — P2-C C3a2 Handover Runner Test Ceiling Repair

- Tranche: `P2C-MUTATION-FULL-UI-2026-07-31`
- Checkpoint: `C3a2`
- Phase: `DESIGN AMENDMENT`
- Risk: `R2`
- Status: `REVIEW_PASS — CLOSED_WITHOUT_WAIVER`

## Finding

`C3A2-BUILD-BLOCK-F2 HANDOVER_RUNNER_TEST_HOST_OMITTED`: after Amendment 1
resumed the unstaged partial BUILD, the full non-live suite reached `1125
passed / 2 failed / 112 skipped`. Both failures are in the same existing host,
`tests/integration/test_handover_live_evidence_runner.py`, which is outside the
exact 81-path ceiling.

The two P2-R regression tests mint test-local principals (`hov-ev-op2`,
`hov-ev-sup3`, `hov-ev-sup4`, `hov-ev-op3` and
`hov-ev-rep-approver2`) but do not persist their ACTIVE assignments. Correct
C3a2 enforcement therefore returns enumeration-safe 404 before the tests can
reach their intended handover/report assertions. No other full-suite failure
or outside-ceiling edit host was observed.

## Decision

Add exactly that one omitted test host to the C3a2 BUILD ceiling, raising it
from 81 to 82. The tests must use explicit persisted ACTIVE assignment setup
for only the principals and shifts each scenario exercises. Their original
P2-R meaning remains unchanged: an acknowledged handover without an approved
current report still refuses freeze with zero provider calls, and the helper
still produces a genuine approved current END_SHIFT report.

Do not make runner authentication implicitly assign users, weaken the
assignment guard, change production behavior, add a wildcard/reserve, or edit
another path. The host is currently 249 lines and the repository file-size
guard passes, so no split/debt/exemption is required.

## BUILD state

The partial BUILD has 58 changed paths, all within the approved 81, and zero
staged paths. No out-of-ceiling edit, provider call, commit, push, self-review
or FREEZE occurred in diagnosing this blocker. Resume requires the matching
SPEC and Work Order amendments, independent authorization review, a pushed
authorization commit and a separate pushed four-surface resume checkpoint.
