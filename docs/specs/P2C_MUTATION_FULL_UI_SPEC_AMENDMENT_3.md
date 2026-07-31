# SPEC Amendment 3 — P2-C C3a1 Review-Repair Test Split

- Tranche: `P2C-MUTATION-FULL-UI-2026-07-31`
- Checkpoint: `C3a1`
- Risk: `R2`
- Status: `REVIEW_PASS`

## Amendment

Add `R32 — review-repair coverage remains executable under the hard guard`:

> The accepted C3a1 F1/F2 repair MUST retain executable regression proof for
> duplicate assignment-id parity, genuine duplicate-active distinction,
> unrelated constraint passthrough, no partial write, live PostgreSQL and
> complete controlled JWT-expiry conversion. When that proof cannot fit in
> the three authorized test hosts under the 300-line hard limit, it MUST be
> split into the three exact feature-owned companion paths authorized by Work
> Order Amendment 2. Coverage MUST NOT be deleted, converted to prose, hidden
> behind a file-size exception or duplicated solely to change test counts.

Each original host and companion MUST be at most 300 lines. Companion imports
and fixtures must remain bounded to the assignment/authentication behavior
under review.

R1-R31 and AC-01..AC-35 remain unchanged. This amendment resolves only
`P2C-C3A1-BUILD-RE-REVIEW-BLOCK-F1` and grants no authority outside the
amended exact Work Order ceiling.
