# INTAKE — CVF Public-Core Refresh

- Tranche: `CVF-CORE-REFRESH-2026-08-23`
- Control-chain phase: `INTAKE`
- Risk: `R2`
- Status: `OPEN_FOR_INDEPENDENT_INTAKE_REVIEW`
- Execution base: `0b89016df8483a4904d2c64b1a6560ccbc6b27ae`
- Frozen public-Core target:
  `3b031fec35473e6ee6a554c4c72400e7a23b06c5`
- Operator authority: `2026-08-23` response `next` to the explicit proposal to
  reconcile CVF Core and then return to P4-C
- Active role: `INTAKE_AUTHOR`

## Request boundary

Restore the mandatory workspace-doctor freshness gate before the parked P4-C
Work Order can receive its bounded authorization rereview. This authority
covers only a governed public-Core/workspace-pin reconciliation. It does not
authorize P4-C BUILD, product changes, provider calls, credentials, installs,
deployment, commit or push.

## Verified current truth

- Hidden Core path:
  `D:\UNG DUNG AI\TOOL AI 2026\CVF-Workspace\.Controlled-Vibe-Framework-CVF`.
- Remote is the expected public URL; the hidden-Core worktree is clean.
- Hidden-Core HEAD and downstream manifest pin are
  `7d9f360a3df11ac998972728000785799399c02b`.
- Fetched `origin/main` is the frozen target
  `3b031fec35473e6ee6a554c4c72400e7a23b06c5`; current HEAD is its ancestor.
- Workspace doctor returned blocking `BEHIND_PUBLIC_REMOTE` (23 passes, one
  failure, plus the retained legacy-catalog warning).
- The public delta modifies only `README.md` and
  `docs/guides/external-agent-review-guide.md`, and adds
  `docs/guides/CVF_EXTERNAL_AGENT_ROUND_TRIP_KIT.md` (293 added lines total).
  It changes no Core script or downstream product source.
- Downstream `HEAD == origin/main == 0b89016...`, staged set is empty.
- Before this INTAKE, the P4-C dirty set excluding the protected operator
  assessment contained exactly 19 paths with LF-terminated sorted-path digest
  `0dd882e328a44a9659ba289594b194adf7111d5ee729104ba500082767adc7c9`.

## Intended outcome

1. Use only the sanctioned public-Core reconciler, without
   `-UpdateProjectManifests`, to preserve the old clean clone, install a fresh
   clone at the frozen target and refresh its declared workspace-root kit.
2. Update only the exact downstream Core pin/header/local-binding and governed
   evidence/continuity surfaces later authorized by a reviewed Work Order.
3. Require full equality among Core HEAD, Core `origin/main`, manifest full
   pin, generated ignored local binding and every refreshed knowledge pin.
4. Restore workspace doctor PASS (the bounded legacy-catalog warning may
   remain), independently review the evidence, then return to the parked P4-C
   authorization rereview.

## Declared external effects

The reconciler may move the current clean hidden Core to a timestamped path
under `<workspaceRoot>/_cvf-core-backups/`, clone the frozen public repository,
rewrite `WORKSPACE_RULES.md`, and run the workspace-root wrapper installer.
The installer may write:

- `New-CVF-Governed-Project.ps1`;
- `Run-CVF-NewProject-Enforcement.ps1`;
- `Update-CVF-Workspace.ps1`;
- `Update-CVF-Workspace-Public-Profile.ps1`;
- `Test-CVF-Workspace.ps1`;
- `Repair-CVF-Workspace.ps1`;
- `Manage-CVF-Workspace.ps1`;
- `.agents/workflows/cvf-onboard.md`;
- `.agents/workflows/pre-commit-check.md`;
- `CVF_WORKSPACE_USER_GUIDE.md`;
- `CVF_WORKSPACE_HUONG_DAN_SU_DUNG.md`;
- `CVF_WORKSPACE_CLASSIFICATION_GUIDE.md`.

The installer also preserves an existing or creates a missing
`WORKSPACE_PROJECT_ENFORCEMENT_BASELINE.json`. It may remove any present
`Get-CVF-Workspace-OverlayProfiles.ps1`,
`Update-CVF-Workspace-Overlay.ps1`, or
`CVF_WORKSPACE_OVERLAY_STATUS.json`. Together with `WORKSPACE_RULES.md`, these
are the complete 17 reconciler-managed root targets. The current active
profile is `operator-local`, so public-profile synchronization must not run.
BUILD must capture existence, SHA-256 preimages/postimages and create/delete
deltas for all 17 targets and preserve sufficient preimages for rollback. No
backup deletion is authorized.

The reconciler is not atomic across those effects: its internal `catch` can
restore the original Core after replacement failure, but it does not restore
root artifacts or downstream files already written; it also provides no
automatic rollback for a later pin, initializer, gate or continuity failure.
A later DESIGN and Work Order must therefore define an executable post-clone
rollback that (1) resolves and verifies every Core/backup/preimage/failed-delta
path inside the exact workspace root, (2) moves and preserves the failed
replacement Core, (3) restores the original Core backup, (4) hash-verifies
restoration of every prior root artifact, (5) moves newly created root
artifacts that lacked preimages into a preserved failed-root-delta tree,
(6) restores downstream pin/header/continuity preimages, (7) deletes no
backup or evidence, and (8) records the trigger, moves, hashes and resulting
post-rollback doctor state before stopping.

The only contemplated network effects are unauthenticated public Git
clone/fetch operations against
`https://github.com/Blackbird081/Controlled-Vibe-Framework-CVF.git`. They are
not BUILD-authorized by INTAKE. A later reviewed Work Order must freeze their
count and require stop/rollback if either observes a different target.

## P4-C parking and protected state

P4-C remains at `WORK_ORDER_REPAIR_READY_FOR_REREVIEW`; BUILD stays blocked.
The 14 non-continuity P4-C paths within the recorded 19-path set are byte-exact
protected during reconciliation. The five shared continuity carriers may
change only to park/restore the active pointer and record Core-refresh facts.
The P4-C handoff remains read-only. After Core-refresh closure, continuity must
restore P4-C as the active tranche without changing its Work Order or review.

The pre-existing untracked operator file
`docs/decisions/ASSESSMENT_2026-07-23_OPERATIONS_WORKSPACE_REPOSITIONING.md`
must not be opened, edited, staged, hashed or used as evidence.

## Boundaries and stop conditions

- No `-UpdateProjectManifests`; its gate does not match this portable manifest
  and its output is not accepted as the exact downstream pin edit.
- No product/runtime/catalog/roadmap/database/provider/deployment action and no
  claim that CVF governs AI or agent behavior; therefore no provider call is
  needed for this maintenance tranche.
- Stop before BUILD unless INTAKE, DESIGN, SPEC and exact Work Order each pass
  their required reviews and explicit BUILD authority is recorded.
- Stop on hidden-Core dirt, remote mismatch, target movement, missing backup or
  rollback capacity, undeclared root delta, P4-C artifact drift, assessment
  access, secret exposure, staged content or any failed deterministic gate.

## Acceptance for INTAKE

Independent review must confirm operator authority, R2 classification, exact
mismatch/target/delta, full reconciler side effects and rollback need, frozen
network boundary, P4-C parking/protection and the no-governance-claim boundary.

## Next governed move

`INDEPENDENT_INTAKE_REVIEWER` returns exactly one of `INTAKE_REVIEW_PASS`,
`INTAKE_REVIEW_CHANGES_REQUIRED`, or `INTAKE_BLOCKED_SOURCE_OR_OWNER`.

## Target-rebase amendment — 2026-08-24

The first authorized BUILD attempt stopped and fully rolled back because public
`main` advanced after the earlier freeze. The operator explicitly approved the
new target `864c4e0e6139f3e32067dea41f43f240e505c0d8`. It is a descendant of
`3b031fec...`; the incremental delta is two documentation-only commits touching
three Core documentation/projection files. All R2 scope, exact scripts,
`17/12/10` ceilings, assessment exclusion, rollback, no-provider and no-commit/
push boundaries remain unchanged. Only the frozen target and dependent pins may
be rebased. A further target movement still requires stop and rollback.
