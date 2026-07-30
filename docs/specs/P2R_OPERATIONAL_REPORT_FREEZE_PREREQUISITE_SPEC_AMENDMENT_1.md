# SPEC Amendment 1 — P2-R Pre-BUILD Sequence

- Tranche: `P2R-OPERATIONAL-REPORT-FREEZE-PREREQUISITE-2026-07-30`
- Risk: `R2`
- Status: `REVIEW_PASS`

## Amendment

Add `R34`:

> The immutable pre-BUILD continuity checkpoint records G6 as the next
> mandatory gate, not a result that does not yet exist. G6 runs from clean
> pushed pre-BUILD state before the first C3 edit. Its exact result belongs
> in the implementation-worker return and
> `P2R_OPERATIONAL_REPORT_FREEZE_BUILD_EVIDENCE_RECEIPT.md`.

R1-R33 and AC-01..AC-32 remain unchanged. This amendment resolves only
`P2R-PREBUILD-F1`.
