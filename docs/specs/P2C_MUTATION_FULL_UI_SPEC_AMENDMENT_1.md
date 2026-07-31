# SPEC Amendment 1 — P2-C C3a Fan-out Repair

- Tranche: `P2C-MUTATION-FULL-UI-2026-07-31`
- Risk: `R2`
- Status: `REVIEW_PASS`

## Amendment

Add `R30 — C3a sub-checkpoint separation`:

> C3a SHALL execute as C3a1 then C3a2, each with an exact-path Work Order,
> independent review, commit and push. C3a1 implements and proves R1-R5 and
> the `/auth/me` plus capability contracts of R9, but MUST NOT claim R6/R7
> route-wide enforcement. C3a2 implements and proves R6-R8, the
> server-authority/non-authority behavior of R9, and the route/fixture portion
> of R10. C3a2 MUST consume the reviewed C3a1 assignment contract without
> silently changing it. C3b cannot begin until C3a2 is reviewed and pushed.

Acceptance allocation is clarified without renumbering:

- C3a1 owns AC-01..AC-03, AC-07's endpoint shape and capability secrecy,
  AC-08, and the applicable migration/PostgreSQL/rollback/gate evidence in
  AC-09, AC-29..AC-33.
- C3a2 owns AC-04..AC-06, AC-07's backend re-authorization proof, AC-09's
  enforcement parity, AC-10, and its applicable AC-29..AC-33 evidence.
- AC-32 applies separately to each exact sub-checkpoint ceiling.

R1-R29 and AC-01..AC-35 remain unchanged and mandatory. Final C3a completion
means both C3a1 and C3a2 have independent `REVIEW_PASS` and are pushed.

This amendment resolves only `P2C-WO-FEAS-F1`; it grants no BUILD authority.
