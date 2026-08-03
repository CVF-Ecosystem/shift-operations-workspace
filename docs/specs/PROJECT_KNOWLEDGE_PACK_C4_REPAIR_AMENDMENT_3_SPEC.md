# SPEC — Project Knowledge Pack C4 Repair Amendment 3

- Tranche: `PROJECT-KNOWLEDGE-PACK-C4-REPAIR-AMENDMENT-3-2026-08-03`
- Risk: `R2`
- Status: `SPEC_COMPLETE`

## Requirements

- `R1` Preserve the exact ten-path final candidate; add no candidate path.
- `R2` Correct memory, canonical/mirror state, handoff, implementation status
  and roadmap to record ten paths, both repair authorities, two repaired
  BUILD-owned knowledge paths and bounded git-network history.
- `R3` Preserve the original BUILD claim of exactly eight paths and zero
  provider/network/POST calls by scoping it explicitly to BUILD.
- `R4` Keep fresh P3-A Refinery INTAKE as the sole next move; later work parked.
- `R5` Refresh only the implementation-status and roadmap hashes in the
  `project-context` manifest entry after their final bytes settle.
- `R6` Preserve registry/catalog bytes, Project Context bytes and all protected
  paths from Amendments 1–2.
- `R7` Permit one final post-continuity fail-stop verification sequence and one
  independent FREEZE re-review, no waiver or retry.
- `R8` After fresh R2, permit exactly three new git-network invocations:
  authority push, doctor/core-fetch and final closure push; all provider/helper/
  integration/POST/remote-ingest/other-network calls remain zero.

## Acceptance criteria

- `AC-1` Independent reviewer confirms no stale eight-path/all-BUILD-protected/
  zero-network closure wording remains.
- `AC-2` Final diff contains exactly ten candidate paths and no staged/residue.
- `AC-3` Both refreshed hashes equal final source bytes; the registry pin and
  every other manifest field remain unchanged.
- `AC-4` Knowledge, focused unit, session, catalog, file-size, repository,
  JSON/diff/residue/protected-hash/secret and doctor gates PASS once.
- `AC-5` Roadmap and memory remain within 600 lines; catalog remains 22 modules.
- `AC-6` Independent `FREEZE_REVIEW_PASS`, then exact ten-path commit and final
  push leave clean `HEAD == origin/main` without another fetch.

## Stop conditions

Stop on missing exact R2, unpushed authority, eleventh candidate path,
protected drift, stale continuity, pin mismatch, gate/re-review failure,
retry, extra network/provider/helper/POST call, residue or broadened claim.

