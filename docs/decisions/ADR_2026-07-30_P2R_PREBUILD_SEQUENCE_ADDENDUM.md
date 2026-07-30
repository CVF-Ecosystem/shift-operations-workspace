# ADR Addendum — P2-R Pre-BUILD Sequence

- Tranche: `P2R-OPERATIONAL-REPORT-FREEZE-PREREQUISITE-2026-07-30`
- Phase: `DESIGN AMENDMENT`
- Risk: `R2`
- Status: `REVIEW_PASS — SEQUENCING REPAIR ONLY`

## Finding

`P2R-PREBUILD-F1 C2_G6_ORDER_CYCLE`: the reviewed Work Order requires the
pre-BUILD continuity checkpoint to record a G6 outcome, while G6 itself must
run from the clean pushed pre-BUILD checkpoint. One immutable commit cannot
both precede and contain the result of the later gate.

## Decision

The pre-BUILD continuity checkpoint records:

- operator-delegated R2 approval;
- implementation/reviewer assignment;
- authorization-parent acknowledgment;
- exact 59-path ceiling;
- G6 as the next mandatory gate;
- manual handoff/no-Claude-CLI boundary.

It does not claim a G6 result.

After that checkpoint is pushed and the worktree is clean, the assigned
implementation worker runs G6 before editing any C3 path. A passing result is
recorded in the worker return and the authorized BUILD evidence receipt.

No Report behavior, requirement, acceptance criterion, changed-set path,
protected boundary, evidence command, stop condition or claim is removed.
BUILD remains prohibited until pushed pre-BUILD continuity and passing G6.
