# SPEC Amendment 1 — Pre-BUILD Sequence

- Tranche: `MESSAGE-ADMISSION-TRUST-REPAIR-2026-07-30`
- Status: `REVIEW_PASS`

## Amendment

Add `R20`:

> C2 records G6 as the next mandatory gate, not a result that does not yet
> exist. G6 runs from clean pushed C2 before the first BUILD edit. Its exact
> result belongs in the worker return and BUILD evidence receipt.

AC-01..AC-23 and R1-R19 remain unchanged. This amendment resolves only
`MAR-PREBUILD-F1`.
