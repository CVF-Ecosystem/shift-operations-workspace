# Work Order — CVF Public-Core Refresh

- Tranche: `CVF-CORE-REFRESH-2026-08-20`
- Phase: `WORK_ORDER`
- Risk ceiling: `R2`
- Status: `AUTHORIZED_FOR_BUILD`
- Parent/role ancestry: `INTAKE_REVIEW_PASS` → `DESIGN_AUTHOR` →
  `SPEC_AUTHOR` → `WORK_ORDER_AUTHOR`; independent authorization re-review is
  completed with `AUTHORIZATION_REVIEW_PASS`
- Execution base: `7d525b6681bd6b51ac89fb32ddcf57136fb95d2e`
- Target public Core: `7d9f360a3df11ac998972728000785799399c02b`

## Authority and roles

Operator authority covers public-Core/workspace-pin reconciliation only.
`IMPLEMENTATION_WORKER` may perform the exact BUILD below but must not commit,
push, open P4, or widen paths. `INDEPENDENT_REVIEWER` must be a separate agent.
`COMMIT_STEWARD` may commit only after `REVIEW_PASS`; push is not authorized by
this work order.

## BUILD sequence

1. Reconfirm project HEAD, staged-zero state, clean Core, expected remote,
   target origin/main, and operator-local profile.
2. Create a timestamped workspace-root preimage directory under
   `_cvf-core-backups`; copy every existing root target named in INTAKE while
   preserving relative paths; record existence and SHA-256 for present files.
3. Run the sanctioned reconciler from the project root without
   `-UpdateProjectManifests`.
4. Reconfirm Core remote/HEAD/origin/main/cleanliness and identify the Core
   backup path created by the reconciler.
5. Patch only the two exact downstream pin values.
6. Run `scripts/initialize_cvf_clone.ps1` to regenerate local binding and run
   the doctor; verify four-way commit equality.
7. Synchronize canonical state, mirror, bootstrap, memory, active handoff,
   implementation truth, and exactly the affected Project Knowledge pins.
8. Write a worker-return evidence artifact, run all SPEC gates, and hand off
   with staged zero.

Only the public GitHub clone in step 3 and public GitHub fetch in step 6 are
authorized network calls. Recheck the exact frozen tip after each. Any moved
tip is a failure even if it is a newer public commit.

## Mandatory post-success rollback procedure

If any check after reconciler success fails, `IMPLEMENTATION_WORKER` must:

1. resolve and verify the canonical Core, Core backup, failed-clone target,
   root-preimage and failed-root-delta paths are all inside the exact workspace
   root and outside downstream repositories;
2. move the replacement Core to the timestamped failed-clone target;
3. move the preserved original Core backup to the canonical Core path;
4. restore each previously existing root artifact from its preimage and verify
   its SHA-256; move each newly created root artifact that lacked a preimage to
   the failed-root-delta directory while preserving relative paths;
5. preserve all clones, backups, failed deltas and evidence; delete nothing;
6. record trigger, paths, containment checks, moves, hashes, Core state and
   post-rollback doctor result, then stop with no commit.

## Exact downstream write set

The files named in DESIGN's Downstream scope are the ceiling. Existing
historical handoffs and evidence are read-only. `docs/catalog/**`, roadmap,
tests, source, packages and apps are forbidden.

The exact worker-handoff set is these 17 paths:

1. `.cvf/manifest.json`
2. `AGENTS.md`
3. `knowledge/manifest.json`
4. `IMPLEMENTATION_STATUS.json`
5. `SESSION/ACTIVE_SESSION_STATE.json`
6. `CVF_SESSION/ACTIVE_SESSION_STATE.json`
7. `SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json`
8. `SESSION/SESSION_MEMORY.md`
9. `SESSION/handoffs/CVF_CORE_REFRESH_2026-08-20.md`
10. `docs/decisions/INTAKE_2026-08-20_CVF_CORE_REFRESH.md`
11. `docs/decisions/INTAKE_REVIEW_2026-08-20_CVF_CORE_REFRESH.md`
12. `docs/decisions/DESIGN_2026-08-20_CVF_CORE_REFRESH.md`
13. `docs/decisions/AUTHORIZATION_REVIEW_2026-08-20_CVF_CORE_REFRESH.md`
14. `docs/decisions/CVF_CORE_REFRESH_ROOT_EFFECTS_2026-08-20.json`
15. `docs/decisions/CVF_CORE_REFRESH_WORKER_RETURN_2026-08-20.md`
16. `docs/specs/CVF_CORE_REFRESH_SPEC.md`
17. `docs/work_orders/CVF_CORE_REFRESH_WORK_ORDER.md`

The worker must compare actual status exactly to those 17 paths. The worker
must not create `docs/decisions/CVF_CORE_REFRESH_COMPLETION_REVIEW_2026-08-20.md`.
After independent REVIEW, the reviewer/closer creates that single eighteenth
path and recomputes the final exact 18-path pre-commit set. The worker-owned
root-effects JSON remains immutable during REVIEW; final changed-set evidence
is recorded in the completion review.

## Stop conditions

Stop on changed Core remote, dirty/diverged Core, unexpected target movement,
failed backup, reconciler rollback/failure, root delta outside the enumerated
installer behavior, project source/catalog/roadmap drift, any unapproved
deletion, any failed gate, staged content, or required scope expansion.

## Acceptance

All `R1`–`R12` pass with exact evidence and no waiver. Reviewer returns exactly
`REVIEW_PASS`, `REVIEW_CHANGES_REQUIRED`, or `REVIEW_BLOCKED`. Only PASS
transfers to `CLOSER`/`COMMIT_STEWARD`.

## Reproducible evidence checks

Capture doctor command and exit code, every R8 command and exit code, pre/post
root manifest, four-way pin equality, `git check-ignore
.cvf/local-binding.json`, `git status --short`, `git diff --name-only`,
`git diff --cached --name-only`, and a sorted exact comparison between actual
worker-stage paths and the 17-path list above in the root-effects JSON. The
independent completion review owns the later 18-path pre-commit comparison.
