# WORK ORDER — Project Knowledge Pack C4 Repair Amendment 1

- Tranche: `PROJECT-KNOWLEDGE-PACK-C4-REPAIR-AMENDMENT-1-2026-08-03`
- Parent C4 authority: `8dd99c02ad27901f416b935a1dcf78ab6ccd4eaa`
- Parent BUILD: `bb3e33668a6d60585455bf0301ba059918a15890`
- Risk: `R2`
- Status: `DRAFT_PENDING_INDEPENDENT_AUTHORIZATION_AND_HUMAN_R2_APPROVAL`

## Exact final changed set

The current unstaged eight-path C4 candidate is retained:

1. `SESSION/SESSION_MEMORY.md`
2. `SESSION/ACTIVE_SESSION_STATE.json`
3. `CVF_SESSION/ACTIVE_SESSION_STATE.json`
4. `SESSION/handoffs/AGENT_HANDOFF_2026-08-03_PROJECT_KNOWLEDGE_PACK.md`
5. `IMPLEMENTATION_STATUS.json`
6. `docs/implementation/EXECUTION_ROADMAP.md`
7. `docs/catalog/MODULE_REGISTRY.json`
8. `docs/catalog/MODULE_CATALOG.md`

Repair adds exactly:

9. `knowledge/PROJECT_CONTEXT.md`
10. `knowledge/manifest.json`

## Authority package

Commit/push separately exactly these five authority paths before repair:

1. `docs/decisions/INTAKE_2026-08-03_PROJECT_KNOWLEDGE_PACK_C4_REPAIR_AMENDMENT_1.md`
2. `docs/decisions/ADR_2026-08-03_PROJECT_KNOWLEDGE_PACK_C4_REPAIR_AMENDMENT_1.md`
3. `docs/specs/PROJECT_KNOWLEDGE_PACK_C4_REPAIR_AMENDMENT_1_SPEC.md`
4. `docs/work_orders/PROJECT_KNOWLEDGE_PACK_C4_REPAIR_AMENDMENT_1_WORK_ORDER.md`
5. `docs/decisions/PROJECT_KNOWLEDGE_PACK_C4_REPAIR_AMENDMENT_1_AUTHORIZATION_REVIEW.md`

## Execution order

1. Independent authorization reviewer checks root cause, minimality, exact
   paths, post-repair run ceiling and zero-call boundary.
2. Human operator explicitly approves R2 for this exact Work Order hash.
3. Commit steward commits/pushes exactly the five authority paths while leaving
   the eight closure paths unstaged.
4. Repair worker verifies protected hashes, settles the three source bytes,
   updates Project Context wording, computes the three source SHA-256 values,
   and changes only those values in the manifest.
5. Run one fresh fail-stop sequence: knowledge validator, focused unit tests,
   session, catalog, file-size, repository and doctor checks. Do not run the
   integration helper.
6. Independent FREEZE reviewer checks exact ten-path diff, hashes, evidence,
   queue and bounded claim. Only `FREEZE_REVIEW_PASS` transfers to closer and
   commit steward.

## Protected set

Byte-identical throughout repair: `knowledge/README.md`,
`knowledge/OPERATIONS_GLOSSARY.md`, `knowledge/GOVERNANCE_BOUNDARIES.md`,
`scripts/check_project_knowledge.py`, both knowledge test hosts, the five
parent C4 authority paths, `.cvf/**`, provider configuration, application and
runtime source, other handoffs and all later-queue artifacts.

## Execution boundary

Zero provider/helper/network/POST/external calls. No integration helper rerun,
retry loop, schema/policy/eligibility change, remote ingest, retrieval,
automatic injection, Refinery/RAG/learning implementation or production claim.

## Next move

Independent amendment authorization review only. No repair edit, generator,
verification rerun, stage, commit or push is authorized from this draft.

