# WORK ORDER — Project Knowledge Pack C4 Repair Amendment 3

- Tranche: `PROJECT-KNOWLEDGE-PACK-C4-REPAIR-AMENDMENT-3-2026-08-03`
- Parent authority: `ffd548e93a7fec26e5ad7263fe3671c70d810423`
- Risk: `R2`
- Status: `DRAFT_PENDING_INDEPENDENT_AUTHORIZATION_AND_HUMAN_R2_APPROVAL`

## Exact authority package

Commit/push separately exactly:

1. `docs/decisions/INTAKE_2026-08-03_PROJECT_KNOWLEDGE_PACK_C4_REPAIR_AMENDMENT_3.md`
2. `docs/decisions/ADR_2026-08-03_PROJECT_KNOWLEDGE_PACK_C4_REPAIR_AMENDMENT_3.md`
3. `docs/specs/PROJECT_KNOWLEDGE_PACK_C4_REPAIR_AMENDMENT_3_SPEC.md`
4. `docs/work_orders/PROJECT_KNOWLEDGE_PACK_C4_REPAIR_AMENDMENT_3_WORK_ORDER.md`
5. `docs/decisions/PROJECT_KNOWLEDGE_PACK_C4_REPAIR_AMENDMENT_3_AUTHORIZATION_REVIEW.md`

## Exact final candidate

The final ceiling remains the same ten paths authorized by Amendment 1.
Amendment 3 may repair only these seven already-present candidate paths:

1. `SESSION/SESSION_MEMORY.md`
2. `SESSION/ACTIVE_SESSION_STATE.json`
3. `CVF_SESSION/ACTIVE_SESSION_STATE.json`
4. `SESSION/handoffs/AGENT_HANDOFF_2026-08-03_PROJECT_KNOWLEDGE_PACK.md`
5. `IMPLEMENTATION_STATUS.json`
6. `docs/implementation/EXECUTION_ROADMAP.md`
7. `knowledge/manifest.json` — only the implementation-status and roadmap pins

The other three candidate paths and all protected paths remain byte-identical.

## Execution order

1. Independent authorization review checks accepted finding, exact in-ceiling
   repair, source-pin ordering, final verification and network ceilings.
2. Human explicitly approves exact R2 Work Order/hash and three new bounded
   git-network command invocations.
3. Commit/push exact five authority paths; leave ten candidate paths unstaged.
4. Repair continuity/status/roadmap truth, settle final bytes, then refresh only
   the two affected manifest pins.
5. Run once, fail-stop: knowledge validator; focused unit; session; catalog;
   file-size; repository; JSON/exact-diff/residue/protected-hash/secret; doctor.
6. Independent FREEZE reviewer re-reviews unchanged exact ten-path candidate.
7. Only `FREEZE_REVIEW_PASS` transfers to closer/commit steward for exact
   ten-path commit and the single final closure push. Verify local/ref equality
   without another fetch.

## Call ceiling

After fresh R2, exactly three new network-bearing invocations: Amendment 3
authority push, one doctor invocation containing one core fetch, final closure
push. Zero provider/helper/integration/POST/remote-ingest/other-network calls.
No command retry.

## Next move

Independent Amendment 3 authorization review only. No candidate repair,
verification, stage, commit, push, doctor or roadmap activation from this draft.

