# SPEC — Project Knowledge Pack C4 Repair Amendment 1

- Tranche: `PROJECT-KNOWLEDGE-PACK-C4-REPAIR-AMENDMENT-1-2026-08-03`
- Risk: `R2`
- Status: `SPEC_COMPLETE`

## Requirements

- `R1` Preserve the original eight closure candidate paths and add exactly
  `knowledge/PROJECT_CONTEXT.md` and `knowledge/manifest.json`.
- `R2` Project Context must state Knowledge Pack `CLOSED_BOUNDED`, fresh P3-A
  Refinery INTAKE next, and keep later retrieval/RAG/learning work bounded.
- `R3` Change only the three `project-context` source-pin SHA-256 values in the
  manifest; every other manifest field remains byte-semantically unchanged.
- `R4` Each replacement pin must equal the SHA-256 of the final on-disk source
  named by that pin.
- `R5` Protect the other six BUILD paths and all five C4 authority paths
  byte-identically.
- `R6` Make zero provider/helper/network/POST/external calls and do not execute
  the integration helper rehearsal.
- `R7` Retain the first failed validator result and run at most one fresh
  post-repair fail-stop verification sequence.
- `R8` Obtain independent `FREEZE_REVIEW_PASS` before stage/commit/push.

## Acceptance criteria

- `AC-1` Final diff relative to `8dd99c0` contains exactly ten repair/closure
  paths and the amendment authority is committed separately.
- `AC-2` `python scripts/check_project_knowledge.py` returns PASS on the fresh
  post-repair run.
- `AC-3` Focused unit, session, catalog, file-size and repository gates PASS in
  the same fail-stop sequence.
- `AC-4` All three source hashes match and protected hashes do not drift.
- `AC-5` Catalog remains generated at 22 modules; no `_index.json`, temporary,
  staged, provider or network residue exists.
- `AC-6` Independent reviewer returns `FREEZE_REVIEW_PASS`, no waiver.

## Stop conditions

Stop on missing exact human R2 approval, authority not pushed, an eleventh
changed closure/repair path, protected-byte drift, source changes after pin
capture, failed gate, second post-repair verification attempt, broadened claim,
helper/provider/network/POST action, residue or missing independent review.

