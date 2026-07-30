# ADR Addendum — Message Admission Pre-BUILD Sequence

- Tranche: `MESSAGE-ADMISSION-TRUST-REPAIR-2026-07-30`
- Phase: `DESIGN AMENDMENT`
- Risk: R2
- Status: `REVIEW_PASS — sequencing repair only`

## Finding

`MAR-PREBUILD-F1 C2_G6_ORDER_CYCLE`: the reviewed Work Order said C2 must
record the G6 result, while G6 itself must run from the clean pushed C2 state.
Both statements cannot be true in one immutable C2 commit.

## Decision

C2 records the operator's worker assignment, C1 acknowledgment, exact ceiling
and the requirement to run G6. After C2 is pushed, the assigned worker runs G6
before editing any BUILD path and includes the exact result in its return and
BUILD receipt.

No requirement, changed-set path, acceptance criterion or evidence gate is
removed. BUILD remains prohibited until pushed C2 and passing G6.
