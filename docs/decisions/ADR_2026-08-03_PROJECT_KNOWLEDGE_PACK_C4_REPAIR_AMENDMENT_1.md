# ADR — Project Knowledge Pack C4 Repair Amendment 1

- Tranche: `PROJECT-KNOWLEDGE-PACK-C4-REPAIR-AMENDMENT-1-2026-08-03`
- Risk: `R2`
- Status: `DESIGN_COMPLETE`

## Decision

Repair the fail-closed C4 candidate by extending its final changed-set ceiling
from eight to exactly ten paths: the original eight closure paths plus
`knowledge/PROJECT_CONTEXT.md` and `knowledge/manifest.json`.

Settle the final bytes of the three pinned closure sources first. Then update
the Project Context advisory sentence from the active Knowledge Pack tranche
to the truthful `CLOSED_BOUNDED` state with fresh P3-A Refinery INTAKE next.
Finally replace only the three `project-context` SHA-256 values in the manifest
with hashes of the settled source bytes.

## Determinism and ordering

The catalog generator may run only if the registry/catalog candidate needs
regeneration before hashes are captured. It must not run after the manifest
pins are written. The knowledge module has zero counted code files, so changing
the two Markdown/JSON repair paths must not alter generated catalog metrics.
Any source-byte change after pin capture is a stop condition.

## Preserved boundaries

The repair does not change pack schema, disposition, consumers, policy,
classification, owner, helper behavior or eligibility rules. It makes stale
source pins current and synchronizes advisory text only. Six other BUILD paths,
five C4 authority paths, application/runtime code, CVF core/configuration and
later-queue artifacts remain protected.

No provider/helper/network/POST/external call is allowed. The existing failed
gate is retained as evidence; the amendment permits one fresh post-repair
fail-stop verification sequence, not an unbounded retry loop.

