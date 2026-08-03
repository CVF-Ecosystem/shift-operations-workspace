# Work Order — Project Operations Skill C4 Status Repair

- Risk: `R2`
- Status: `DRAFT_PENDING_INDEPENDENT_AUTHORIZATION`

## Authorization package

Commit/push exactly these five paths after independent authorization PASS:

1. `docs/decisions/INTAKE_2026-08-03_PROJECT_OPERATIONS_SKILL_C4_STATUS_REPAIR.md`
2. `docs/decisions/ADR_2026-08-03_PROJECT_OPERATIONS_SKILL_C4_STATUS_REPAIR.md`
3. `docs/specs/PROJECT_OPERATIONS_SKILL_C4_STATUS_REPAIR_SPEC.md`
4. `docs/work_orders/PROJECT_OPERATIONS_SKILL_C4_STATUS_REPAIR_WORK_ORDER.md`
5. `docs/decisions/PROJECT_OPERATIONS_SKILL_C4_STATUS_REPAIR_AUTHORIZATION_REVIEW.md`

## Exact BUILD

Change only `IMPLEMENTATION_STATUS.json`, and within it only the top-level
`status` scalar to the exact ADR value. All other paths and all other parsed
fields are protected. The two untracked Knowledge Pack drafts remain untouched
and unstaged.

## Order and roles

1. `INDEPENDENT_AUTHORIZATION_REVIEWER` reviews the package.
2. `COMMIT_STEWARD` pushes exactly the five authorization paths.
3. `CONTINUITY_REPAIR_WORKER` applies the one-scalar repair.
4. Run the SPEC gates and independent BUILD review, zero provider calls.
5. Only REVIEW_PASS transfers the one path to `COMMIT_STEWARD` for a separate
   commit/push; verify clean tracked worktree while retaining the two expected
   untracked Knowledge Pack drafts.

Stop on extra field/path change, Knowledge Pack draft mutation/staging, failed
gate, provider/network call, hidden runtime artifact, missing review or broader
claim.

