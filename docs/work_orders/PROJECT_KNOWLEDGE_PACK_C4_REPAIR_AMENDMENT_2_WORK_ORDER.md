# WORK ORDER — Project Knowledge Pack C4 Repair Amendment 2

- Tranche: `PROJECT-KNOWLEDGE-PACK-C4-REPAIR-AMENDMENT-2-2026-08-03`
- Parent amendment authority: `c32b5c51d51847dbd0fbf3bb582e9f7dd3fa1734`
- Risk: `R2`
- Status: `DRAFT_PENDING_INDEPENDENT_AUTHORIZATION_AND_HUMAN_R2_APPROVAL`

## Exact authority package

Commit and push separately exactly:

1. `docs/decisions/INTAKE_2026-08-03_PROJECT_KNOWLEDGE_PACK_C4_REPAIR_AMENDMENT_2.md`
2. `docs/decisions/ADR_2026-08-03_PROJECT_KNOWLEDGE_PACK_C4_REPAIR_AMENDMENT_2.md`
3. `docs/specs/PROJECT_KNOWLEDGE_PACK_C4_REPAIR_AMENDMENT_2_SPEC.md`
4. `docs/work_orders/PROJECT_KNOWLEDGE_PACK_C4_REPAIR_AMENDMENT_2_WORK_ORDER.md`
5. `docs/decisions/PROJECT_KNOWLEDGE_PACK_C4_REPAIR_AMENDMENT_2_AUTHORIZATION_REVIEW.md`

## Exact final candidate

The final changed-set ceiling remains exactly the ten paths listed by
Amendment 1. Amendment 2 repair edits only:

- `docs/implementation/EXECUTION_ROADMAP.md`
- the roadmap SHA-256 value in `knowledge/manifest.json`

No new candidate path is added.

## Roles and execution order

1. Independent authorization reviewer verifies retained evidence, minimal
   in-ceiling repair, replacement-run ceiling and exact network reconciliation.
2. Human explicitly approves R2 for this exact Work Order hash and its three
   bounded git-network command invocations.
3. Commit steward commits locally and pushes exactly the five authority paths,
   leaving the ten candidate paths unstaged.
4. Repair worker condenses only the roadmap closure entry to at most 600 lines,
   captures its final SHA-256 and updates only its manifest pin.
5. Run exactly one replacement fail-stop sequence: knowledge validator,
   focused unit tests, session, catalog, file-size, repository, JSON/diff/
   residue/protected-hash checks, then exactly one workspace doctor invocation.
6. Independent FREEZE reviewer checks the exact ten-path candidate and all
   retained/new evidence. Only `FREEZE_REVIEW_PASS` transfers to closer.
7. Commit steward commits exactly ten candidate paths and performs the single
   authorized final closure push. Verify clean `HEAD == origin/main` without
   another fetch.

## Network and call ceiling

After fresh R2 approval, exactly these network-bearing command invocations are
permitted: one amendment-authority push, one doctor invocation whose script
performs one CVF-core fetch, and one final closure push. Provider, helper,
integration rehearsal, POST, remote ingest and every other network action are
zero. No retry of any command is authorized.

## Next move

Independent Amendment 2 authorization review only. No repair, verification
replacement, stage, commit, push, doctor or later-roadmap action is authorized
from this draft.

