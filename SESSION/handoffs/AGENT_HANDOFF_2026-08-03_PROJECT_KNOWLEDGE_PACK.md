# Agent Handoff — Project Knowledge Pack

## Disposition

- Tranche: `PROJECT-KNOWLEDGE-PACK-2026-08-03`
- Risk: `R2`
- Control-chain phase: `WORK_ORDER` authorized, BUILD pending G6
- Active role: `IMPLEMENTATION_WORKER`
- Status: `AUTHORIZED_PENDING_G6`
- Governance baseline: `c50474f`

## Authority chain

INTAKE, DESIGN and SPEC findings closed without waiver. Independent Work Order
review returned `AUTHORIZATION_REVIEW_PASS`. The human operator then explicitly
approved R2 for Work Order
`docs/work_orders/PROJECT_KNOWLEDGE_PACK_WORK_ORDER.md`, SHA-256
`dc08fa3ffaeae36a009012ded12c47446b54ce8cfa111711d2b565b7ef140371`,
with exactly eight BUILD paths, zero provider calls and no remote ingest.

The exact seven-path governance package is committed and pushed at `c50474f`.
This separate exact four-path checkpoint records the transfer; it does not
contain any BUILD edit.

## Exact BUILD boundary

After this checkpoint is pushed and G6 passes, BUILD may change only:

1. `knowledge/README.md`
2. `knowledge/PROJECT_CONTEXT.md`
3. `knowledge/OPERATIONS_GLOSSARY.md`
4. `knowledge/GOVERNANCE_BOUNDARIES.md`
5. `knowledge/manifest.json`
6. `scripts/check_project_knowledge.py`
7. `tests/unit/test_project_knowledge_pack.py`
8. `tests/integration/test_project_knowledge_ingest_rehearsal.py`

All governance, continuity, implementation-status, roadmap, catalog,
application/runtime, provider-configuration and CVF-core paths are protected
during BUILD. C4 is separate and unauthorized.

## G6 and execution constraints

G6 must confirm clean `HEAD == origin/main`, exact pushed authority and SPEC
hashes, the eight-path baseline (tracked README plus seven absent paths), clean
pinned core/helper hashes, no staged/runtime `_index.json` residue, passing
session/repository/doctor gates and the parked later queue.

Only G6 PASS permits implementation. The public-core helper may run only from
the authorized integration test after exact hash and file-only token
inspection, against an exact disposable three-file input with cleanup in
`finally`. No provider call, provider-secret/config read, POST, remote
collection, external write, repository `_index.json`, Refinery, retrieval,
RAG, learning or later-queue work is authorized.

## Review and commit boundary

Leave the exact eight BUILD paths unstaged for an independent reviewer. Only
`REVIEW_PASS` may transfer the unchanged candidate to `COMMIT_STEWARD` for a
separate BUILD commit/push. A later C4 requires fresh governance.

## Next governed move

Commit/push this exact four-path continuity checkpoint, rehydrate, and run G6.
Stop before edit on any mismatch. No provider retry exists because the allowed
provider-call count is exactly zero.

