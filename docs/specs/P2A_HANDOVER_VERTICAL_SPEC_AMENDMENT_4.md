# SPEC Amendment 4 — P2-A Canonical Debt Digest Correction

ID: `P2A-HANDOVER-SPEC-AMENDMENT-4`
Tranche: `P2A-HANDOVER-VERTICAL-2026-07-26`
Risk: R2
Status: REVIEW_PASS
Design: `docs/decisions/ADR_2026-07-27_P2A_HANDOVER_CANONICAL_DEBT_DIGEST_CORRECTION_ADDENDUM.md`
Amends: parent SPEC and Amendments 1-3

## Scope

Parent requirements and AC-01-AC-34 remain in force. This amendment resolves
the single baseline migration defect exposed by R24.

## Added requirement

### R25 — bounded canonical baseline migration

The existing `scripts/generate_catalog.py` debt entry must contain the SHA-256
of its unchanged UTF-8 logical content under R24:

`fff6229dde57a174935b87eb8319ef7e6d1bdd882580f74e672c81054739c93b`

Only that entry's `sha256` field may change. Its path, line count, hard limit,
reason and required split remain unchanged. The other debt entry and its
digest remain unchanged.

## Acceptance criteria

- **AC-35:** the baseline diff changes exactly one JSON scalar: the
  `scripts/generate_catalog.py` `sha256`, from `a46bd98d...` to
  `fff6229d...`.
- **AC-36:** the canonical digest equals the committed Git blob digest and the
  file-size gate passes on both LF and CRLF checkout representations.
- **AC-37:** both debt entries pass canonical digest and line-count validation;
  existing mutation-negative coverage remains green.
- **AC-38:** all parent/amended gates pass and the BUILD receipt records F14,
  its proof, and the unchanged 47-path boundary.

## Claim boundary

This amendment corrects one stale metadata value. It does not modify
`scripts/generate_catalog.py`, forgive content drift, expand legacy debt or
alter application behavior.

## Disposition

`HOV-REV-F14` is accepted at SPEC without waiver. AC-35-AC-38 are approved
under the delegated independent reviewer authority.
