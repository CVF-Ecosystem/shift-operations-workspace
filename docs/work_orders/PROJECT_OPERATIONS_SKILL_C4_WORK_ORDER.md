# Work Order — Project Operations Skill C4 Closure

- Tranche: `PROJECT-OPERATIONS-SKILL-C4-2026-08-03`
- Risk: `R2`
- Status: `DRAFT_PENDING_INDEPENDENT_AUTHORIZATION`

## Exact changed set

Only these eight paths may change:

1. `SESSION/SESSION_MEMORY.md`
2. `SESSION/ACTIVE_SESSION_STATE.json`
3. `CVF_SESSION/ACTIVE_SESSION_STATE.json`
4. `SESSION/handoffs/AGENT_HANDOFF_2026-08-02_PROJECT_OPERATIONS_SKILL.md`
5. `IMPLEMENTATION_STATUS.json`
6. `docs/implementation/EXECUTION_ROADMAP.md`
7. `docs/catalog/MODULE_REGISTRY.json`
8. `docs/catalog/MODULE_CATALOG.md`

Protected and byte-identical: BUILD `ad7e037`'s eight paths; these five C4
authority paths after their authorization commit; `.cvf/**`; provider
configuration; other continuity/handoffs; and every later-queue artifact:

1. `docs/decisions/INTAKE_2026-08-03_PROJECT_OPERATIONS_SKILL_C4.md`
2. `docs/decisions/ADR_2026-08-03_PROJECT_OPERATIONS_SKILL_C4.md`
3. `docs/specs/PROJECT_OPERATIONS_SKILL_C4_SPEC.md`
4. `docs/work_orders/PROJECT_OPERATIONS_SKILL_C4_WORK_ORDER.md`
5. `docs/decisions/PROJECT_OPERATIONS_SKILL_C4_AUTHORIZATION_REVIEW.md`

## Roles and order

1. `INDEPENDENT_AUTHORIZATION_REVIEWER` reviews this exact package.
2. `COMMIT_STEWARD` commits/pushes exactly the five named C4 authority paths
   above; no closure path enters that commit. That pushed five-path commit
   directly transfers authority to `SESSION_SYNC_STEWARD`; there is no
   intermediate checkpoint or hidden changed set.
3. `SESSION_SYNC_STEWARD` edits exactly closure paths 1-7, then runs
   `python scripts/generate_catalog.py --write` to produce path 8.
4. Run JSON/session/catalog/file-size/repository/diff/secret/doctor gates,
   focused tests and the full non-live suite. Make zero provider calls.
5. `INDEPENDENT_FREEZE_REVIEWER` compares authority, exact diff, source truth,
   generated catalog, evidence preservation, tests and claim boundary.
6. Only `FREEZE_REVIEW_PASS` transfers to `CLOSER`. `CLOSER` confirms the exact
   eight-path candidate, zero runtime/staged residue, zero open finding, the
   bounded claim and final `FREEZE / CLOSED_BOUNDED` disposition, then transfers
   those unchanged eight paths to `COMMIT_STEWARD` for a separate C4
   commit/push.

## Evidence and invariants

- Start and finish with `HEAD == origin/main` and no staged/runtime residue.
- Before edits, hash all eight BUILD paths; after edits require exact equality.
- Validate live state/receipt as final `12/8/4` without invoking the runner.
- Preserve the independent BUILD review and exact-parent rehearsal results.
- Generated catalog is accepted only when `generate_catalog.py --check` passes.

## Stop conditions

Stop on missing authorization, changed-set overflow, protected-path hash drift,
failed test/gate, continuity/mirror mismatch, false `enforced` semantics,
provider call, installation, residue, broader claim or missing independent
FREEZE review. No waiver, retry or thirteenth provider call is authorized.
