# SPEC Amendment 3 — P2-A Handover Rollback Portability

ID: `P2A-HANDOVER-SPEC-AMENDMENT-3`
Tranche: `P2A-HANDOVER-VERTICAL-2026-07-26`
Risk: R2
Status: REVIEW_PASS
Design: `docs/decisions/ADR_2026-07-27_P2A_HANDOVER_ROLLBACK_PORTABILITY_ADDENDUM.md`
Amends: parent SPEC and Amendments 1-2

## Scope

Parent R1-R23 and AC-01-AC-30 remain in force except AC-20's exact changed
set, superseded below.

## Added requirement

### R24 — portable debt digest

The file-size guard's debt SHA-256 must be computed over UTF-8 text with CRLF
and lone CR canonicalized to LF. LF and CRLF representations of identical
logical text must have the same digest. Any other content mutation, including
one preserving line count, must still invalidate the debt entry.

The canonicalization must not change line limits, debt membership, tracked-file
requirements, fail-closed configuration behavior or the closed allowlist.
Existing LF baseline digest values remain unchanged.

## Acceptance criteria

- **AC-20 (superseded):** C3 changes exactly 47 authorized paths; no 48th path.
- **AC-31:** a debt entry generated from LF content remains valid when the same
  logical file is represented with CRLF.
- **AC-32:** same-line-count non-EOL content mutation still fails digest
  validation.
- **AC-33:** `check_file_size.py`, its integration test and documentation agree
  on the canonical digest rule; all touched Python remains <=300 lines.
- **AC-34:** reviewer rollback rehearsal in a fresh Windows worktree at the
  committed parent returns the expected baseline and all repository gates PASS.

## Claim boundary

This amendment repairs cross-checkout determinism only. It does not relax the
debt ratchet, authorize new debt, alter application behavior or expand the
handover claim.

## Disposition

`HOV-REV-F13` is accepted at SPEC without waiver. AC-20 and AC-31-AC-34 are
approved under the delegated independent reviewer authority.
