# SPEC — Project Knowledge Pack C4 Repair Amendment 2

- Tranche: `PROJECT-KNOWLEDGE-PACK-C4-REPAIR-AMENDMENT-2-2026-08-03`
- Risk: `R2`
- Status: `SPEC_COMPLETE`

## Requirements

- `R1` Preserve the exact ten repair/closure paths from Amendment 1.
- `R2` Reduce the roadmap to at most 600 physical lines by condensing only the
  Project Knowledge Pack closure prose; retain all required closure truth.
- `R3` After roadmap bytes settle, change only its one SHA-256 value in the
  manifest; preserve the other two repaired pins and all other manifest data.
- `R4` Preserve all paths protected by Amendment 1 byte-identically.
- `R5` Retain both prior fail-stop results and permit exactly one replacement
  verification sequence, stopping at its first failure with no retry.
- `R6` Permit exactly three bounded git-network command invocations after R2:
  amendment-authority push, doctor/core-fetch, and final closure push.
- `R7` Make zero provider/helper/integration-rehearsal/POST/remote-ingest or
  other network calls.
- `R8` Require independent `FREEZE_REVIEW_PASS` before closure commit/push.

## Acceptance criteria

- `AC-1` Roadmap is at most 600 lines and its manifest pin equals its final
  SHA-256.
- `AC-2` Final candidate relative to the authority parent changes exactly ten
  repair/closure paths; amendment authority is a separate five-path commit.
- `AC-3` The sole replacement sequence passes knowledge, 77-test focused unit,
  session, catalog, file-size, repository, JSON/diff/residue and doctor gates.
- `AC-4` Doctor reports the truthful current result after its one authorized
  core fetch; no extra doctor or fetch is permitted.
- `AC-5` Independent reviewer returns `FREEZE_REVIEW_PASS`, no waiver.
- `AC-6` Final closure push is separate and leaves `HEAD == origin/main` clean.

## Stop conditions

Stop on missing exact R2 approval, authority not pushed, an eleventh candidate
path, protected drift, roadmap above 600 lines, pin mismatch, any replacement
gate failure, retry, extra fetch/push/network command, provider/helper/POST,
residue, broadened claim or missing independent review.

