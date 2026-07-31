# SPEC Amendment 4 — P2-C C3a2 Ceiling Repair

- Tranche: `P2C-MUTATION-FULL-UI-2026-07-31`
- Checkpoint: `C3a2`
- Risk: `R2`
- Status: `REVIEW_PASS`

## Amendment

Add `R31 — C3a2 omitted-host repair`:

> C3a2 SHALL migrate the representative real-route contract proof and the
> existing message-admission live runner to explicit persisted ACTIVE
> assignment setup. The contract proof retains its schema-validation purpose.
> Both separate fresh-ledger message branches SHALL persist and ACTIVE-assign
> authenticated `msg-ev-op`. Frozen refusal retains 409, zero message/audit
> writes and zero provider calls; genuine admission retains exactly one message, exact
> actor-bound audit and the later exactly-one real provider call. No production
> bypass, implicit/default assignment or additional path is permitted.

AC-30 and AC-32 apply to the amended exact 81-path ceiling. R1-R30 and
AC-01..AC-35 remain unchanged and mandatory. This amendment grants no BUILD
authority by itself.
