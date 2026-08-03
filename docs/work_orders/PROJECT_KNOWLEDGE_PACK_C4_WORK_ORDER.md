# WORK ORDER — Project Knowledge Pack C4 Closure

- Tranche: `PROJECT-KNOWLEDGE-PACK-C4-2026-08-03`
- Parent BUILD: `bb3e33668a6d60585455bf0301ba059918a15890`
- Risk: `R2`
- Status: `DRAFT_PENDING_INDEPENDENT_AUTHORIZATION_AND_HUMAN_R2_APPROVAL`

## Exact closure changed set

Only these eight paths may change:

1. `SESSION/SESSION_MEMORY.md`
2. `SESSION/ACTIVE_SESSION_STATE.json`
3. `CVF_SESSION/ACTIVE_SESSION_STATE.json`
4. `SESSION/handoffs/AGENT_HANDOFF_2026-08-03_PROJECT_KNOWLEDGE_PACK.md`
5. `IMPLEMENTATION_STATUS.json`
6. `docs/implementation/EXECUTION_ROADMAP.md`
7. `docs/catalog/MODULE_REGISTRY.json`
8. `docs/catalog/MODULE_CATALOG.md`

Protected and byte-identical: the eight BUILD paths at `bb3e336`; these four
C4 drafts plus the independent authorization review after their pushed
five-path authority commit; `.cvf/**`; provider configuration; other handoffs;
application/runtime source; and all later-queue artifacts.

## Authority package

The C4 authority commit contains exactly:

1. `docs/decisions/INTAKE_2026-08-03_PROJECT_KNOWLEDGE_PACK_C4.md`
2. `docs/decisions/ADR_2026-08-03_PROJECT_KNOWLEDGE_PACK_C4.md`
3. `docs/specs/PROJECT_KNOWLEDGE_PACK_C4_SPEC.md`
4. `docs/work_orders/PROJECT_KNOWLEDGE_PACK_C4_WORK_ORDER.md`
5. `docs/decisions/PROJECT_KNOWLEDGE_PACK_C4_AUTHORIZATION_REVIEW.md`

Only independent `AUTHORIZATION_REVIEW_PASS`, explicit human R2 approval of
this exact Work Order, and pushed five-path authority transfer closure power to
`SESSION_SYNC_STEWARD`.

## Roles and execution order

1. `INDEPENDENT_AUTHORIZATION_REVIEWER` reviews exact authority and boundaries.
2. Human operator explicitly approves or rejects this C4 Work Order.
3. `COMMIT_STEWARD` commits/pushes exactly the five authority paths.
4. `SESSION_SYNC_STEWARD` hashes protected BUILD/authority files, edits closure
   paths 1-7, then runs `python scripts/generate_catalog.py --write` for path 8.
5. Run knowledge validator, focused tests, JSON/session/catalog/file-size/
   repository/diff/secret/residue gates and workspace doctor. Make zero
   provider/helper/network/POST calls; do not rerun integration helper.
6. `INDEPENDENT_FREEZE_REVIEWER` checks exact diff, protected hashes, source
   truth, generated catalog, evidence, next queue and claim ceiling.
7. Only `FREEZE_REVIEW_PASS` transfers unchanged eight paths to `CLOSER`, then
   `COMMIT_STEWARD` commits/pushes C4 separately.

## Required final truth

- Active phase becomes `FREEZE`; Project Knowledge Pack status is
  `CLOSED_BOUNDED`; active role routes through reviewer/closer/stewards.
- Implementation status and roadmap record BUILD `bb3e336`, reviewed evidence,
  exact local-only claim and fresh P3-A INTAKE as sole next move.
- Registry entry is exact: id `project-knowledge-pack`, path `knowledge`, kind
  `package`, status `partial`, empty `cvf_controls`, contract
  `knowledge/manifest.json`, tests the exact unit/integration hosts, and local
  structural enforcement text with explicit non-enforcement boundaries.
- Generated catalog reflects 22 modules and current computed metrics; it is not
  hand-edited.
- Later queue items remain parked; provider-call count for BUILD+C4 is zero.

## Verification

Run without executing the helper:

```powershell
python scripts/check_project_knowledge.py
python -m pytest tests/unit/test_project_knowledge_pack.py -q
python scripts/check_session_state.py
python scripts/generate_catalog.py --check
python scripts/check_file_size.py
python scripts/testing/validate_repository.py
```

Also parse changed JSON, verify exact paths/protected hashes, scan for secrets
without printing matches, assert no `_index.json`/temp/staged residue, and run
the resolved workspace doctor. The retained reviewed full-suite and integration
evidence may be recorded without rerunning the helper because closure changes
no BUILD path.

## Stop conditions

Stop on missing approval, authority not pushed, path/hash drift, failed gate,
catalog hand edit, provider/helper/network/POST/external action, residue,
broadened claim, later-queue activation beyond fresh P3-A INTAKE, self-review
or missing independent FREEZE review. No provider retry exists; allowed calls
are zero.

## Next move

Independent C4 authorization review only. No closure edit, generator write,
stage or commit is authorized from this draft.
