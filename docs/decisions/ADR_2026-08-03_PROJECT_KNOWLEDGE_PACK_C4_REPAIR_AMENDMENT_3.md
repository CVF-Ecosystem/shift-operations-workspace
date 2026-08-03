# ADR — Project Knowledge Pack C4 Repair Amendment 3

- Tranche: `PROJECT-KNOWLEDGE-PACK-C4-REPAIR-AMENDMENT-3-2026-08-03`
- Risk: `R2`
- Status: `DESIGN_COMPLETE`

## Decision

Correct continuity in place without expanding the ten-path final candidate.
The final narrative must distinguish:

- original BUILD `bb3e336`: exactly eight BUILD paths, zero provider/network/
  POST calls, independently `FINAL_REVIEW_PASS` after F1-F4;
- parent C4 `8dd99c0`: original eight closure paths;
- Amendment 1 `c32b5c5`: final ceiling raised to ten because three required
  closure sources invalidated Project Context pins;
- Amendment 2 `ffd548e`: roadmap file-size repair and bounded git-network
  reconciliation;
- final candidate: exact ten paths, including repaired
  `knowledge/PROJECT_CONTEXT.md` and `knowledge/manifest.json`.

The roadmap's zero-call phrase must be scoped to BUILD provider/network/POST
history, not the later git-governance operations. Active next work remains
fresh P3-A Refinery INTAKE only.

After continuity/status/roadmap bytes settle, refresh exactly the two affected
Project Context pins for `IMPLEMENTATION_STATUS.json` and the roadmap. The
module-registry pin remains unchanged.

## Verification and network

Retain both prior failures and the Amendment 2 passing sequence. Permit one
final post-continuity fail-stop sequence and one independent FREEZE re-review.
After R2, only Amendment 3 authority push, one doctor/core-fetch and final
closure push may use network. No retry or other call is allowed.

