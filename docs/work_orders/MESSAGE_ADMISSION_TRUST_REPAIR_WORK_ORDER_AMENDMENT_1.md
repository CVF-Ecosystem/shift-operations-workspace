# Work Order Amendment 1 — Pre-BUILD Sequence

- Tranche: `MESSAGE-ADMISSION-TRUST-REPAIR-2026-07-30`
- Status: `REVIEW_PASS — C2 THEN G6`

Section 5 C2 is corrected as follows:

- C2 records implementation/reviewer identities, pushed C1 acknowledgment,
  exact 29-path ceiling and G6 as the next mandatory gate.
- C2 does not claim a G6 result.
- From clean pushed C2, the assigned implementation worker runs G6.
- A passing G6 result is recorded in the worker return and
  `MESSAGE_ADMISSION_TRUST_REPAIR_BUILD_EVIDENCE_RECEIPT.md`.
- No BUILD path may be edited before that passing result.

All 29 C3 paths, protected boundaries, commands, stop conditions, commit
ownership and evidence requirements remain unchanged.
