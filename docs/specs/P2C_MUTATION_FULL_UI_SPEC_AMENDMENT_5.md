# SPEC Amendment 5 — P2-C C3a2 Handover Runner Test Ceiling Repair

- Tranche: `P2C-MUTATION-FULL-UI-2026-07-31`
- Checkpoint: `C3a2`
- Risk: `R2`
- Status: `REVIEW_PASS`

## Amendment

Add `R32 — C3a2 handover-runner regression-host migration`:

> C3a2 SHALL migrate the two P2-R regression scenarios in
> `tests/integration/test_handover_live_evidence_runner.py` to explicit
> persisted ACTIVE assignment setup for their test-local authenticated
> principals. The no-report scenario SHALL still reach freeze and return 409
> with an unchanged provider-call counter. The ready-report scenario SHALL
> still produce an APPROVED, current END_SHIFT report. The repair SHALL NOT
> introduce implicit assignment in the runner, weaken enumeration-safe scope
> enforcement, alter production behavior, or require another edit host.

AC-30 and AC-32 apply to the amended exact 82-path ceiling. R1-R31 and
AC-01..AC-35 remain unchanged and mandatory. This amendment grants no BUILD
authority by itself.
