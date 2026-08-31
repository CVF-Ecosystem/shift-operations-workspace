# INTAKE — CVF Public-Core Refresh

- Tranche: `CVF-CORE-REFRESH-2026-08-29`
- Control-chain phase: `INTAKE`
- Risk: `R2`
- Status: `OPEN_FOR_INDEPENDENT_INTAKE_REVIEW`
- Downstream execution base:
  `a8e2ad8199d700a238d7d74bdbf85329446228de`
- Current local/pinned Core:
  `a7a797d7111be472ef2cbd928cbeffc70ccb6bc6`
- Frozen observed public target:
  `06c3d040a3dc8fa22fa27f2f9c3e40739def075e`
- Operator authority: `2026-08-29` response `tiếp tục` to the explicit request
  to open a fresh Core reconciliation INTAKE before P4-E SPEC
- Active role: `CORE_REFRESH_INTAKE_AUTHOR`

## Request boundary

Restore the mandatory workspace-doctor freshness gate, then return to the
parked P4-E DESIGN checkpoint. This authority opens only a fresh reconciliation
INTAKE. It does not authorize DESIGN, SPEC, WORK_ORDER, hidden-Core mutation,
workspace-root writes, public Git operations, installation, product/database
changes, provider calls, credentials, deployment, commit or push.

## Verified current truth

- Hidden Core resolves to
  `D:\UNG DUNG AI\TOOL AI 2026\CVF-Workspace\.Controlled-Vibe-Framework-CVF`.
- Its expected public remote is
  `https://github.com/Blackbird081/Controlled-Vibe-Framework-CVF.git`.
- Hidden-Core worktree is clean. `HEAD`, downstream manifest pin and declared
  local Core are `a7a797d7111be472ef2cbd928cbeffc70ccb6bc6`.
- The final P4-E doctor observation fetched public `origin/main` at the frozen
  target `06c3d040a3dc8fa22fa27f2f9c3e40739def075e` and returned blocking
  `BEHIND_PUBLIC_REMOTE`: 23/25 checks passed, one freshness failure and the
  retained bounded legacy-catalog warning.
- The graph is exactly `0` ahead / `1` behind; merge-base is the current local
  Core. The sole public commit is `06c3d04 sync: public surface update from
  governance@5531c5f9d`.
- The public delta changes 190 Core paths: `.github` 5, `ARCHITECTURE.md` 1,
  `docs` 11, `EXTENSIONS` 92, `governance` 80 and `README.md` 1. It includes
  runtime and governance source, so this is not a documentation-only refresh.
- The downstream workspace-kit/reconciler surface is unchanged across the
  delta: no change to `AGENTS.md`, `AGENT_HANDOFF.md`, `scripts/`,
  `governance/toolkit/05_OPERATION/` or
  `docs/reference/CVF_WORKSPACE_RULES.md`. The current reconciler SHA-256 is
  `96ac0cce3bf9df5733ffe2c6f5a7850db0ccfdc4403daaa70fdb6981dc58196c`.
- Downstream `HEAD == origin/main == a8e2ad8199d700a238d7d74bdbf85329446228de`;
  staged set is empty. Current P4-E documentation/continuity edits remain
  uncommitted and must be preserved byte-exact outside separately authorized
  continuity/pin carriers.

## Intended outcome

1. Reconcile the clean hidden Core to one independently revalidated frozen
   public target using only the sanctioned public-Core reconciler.
2. Preserve the old Core, all affected workspace-root preimages and all current
   P4-E work; do not delete backups or failed-attempt evidence.
3. Update only the exact downstream Core pin/header/local binding, Knowledge
   source pins and continuity/evidence carriers later enumerated by an approved
   Work Order.
4. Require equality among Core `HEAD`, Core `origin/main`, the manifest full
   pin, generated ignored local binding and every declared current pin.
5. Restore workspace doctor PASS, allowing only the already bounded legacy-
   catalog warning, then return continuity to P4-E at
   `DESIGN_REVIEW_PASS` before any separate DESIGN-to-SPEC transition.

## Contemplated external and root effects

A later reviewed Work Order may authorize unauthenticated public Git
fetch/clone only against the declared public remote. It must freeze operation
counts and target identity and stop with rollback on target movement, remote
mismatch or unexpected history.

The unchanged reconciler may move the current clean hidden Core to a preserved
timestamped path under `<workspaceRoot>/_cvf-core-backups/`, clone the frozen
public repository, rewrite `WORKSPACE_RULES.md` and run the workspace-root
wrapper installer. The complete known reconciler-managed root inventory is:

1. `WORKSPACE_RULES.md`
2. `New-CVF-Governed-Project.ps1`
3. `Run-CVF-NewProject-Enforcement.ps1`
4. `Update-CVF-Workspace.ps1`
5. `Update-CVF-Workspace-Public-Profile.ps1`
6. `Test-CVF-Workspace.ps1`
7. `Repair-CVF-Workspace.ps1`
8. `Manage-CVF-Workspace.ps1`
9. `.agents/workflows/cvf-onboard.md`
10. `.agents/workflows/pre-commit-check.md`
11. `CVF_WORKSPACE_USER_GUIDE.md`
12. `CVF_WORKSPACE_HUONG_DAN_SU_DUNG.md`
13. `CVF_WORKSPACE_CLASSIFICATION_GUIDE.md`
14. `WORKSPACE_PROJECT_ENFORCEMENT_BASELINE.json`
15. `Get-CVF-Workspace-OverlayProfiles.ps1`
16. `Update-CVF-Workspace-Overlay.ps1`
17. `CVF_WORKSPACE_OVERLAY_STATUS.json`

DESIGN and the Work Order must independently verify that this unchanged
inventory remains complete, record existence and SHA-256 pre/post state for
all 17 targets, distinguish create/update/delete/no-change, and forbid public-
profile synchronization while the active profile is operator-local.

## Atomicity and rollback obligation

The reconciler is not assumed atomic across hidden Core, workspace-root and
downstream carrier effects. DESIGN and the Work Order must define executable
rollback that:

- resolves and containment-checks every Core, backup, failed-delta, root and
  downstream path inside the exact workspace boundary;
- preserves the failed replacement Core and all evidence;
- restores the original clean Core and verifies its commit/remote/clean state;
- hash-verifies restoration of every prior root and downstream preimage;
- moves newly created root artifacts lacking preimages into a preserved failed-
  delta tree rather than deleting them;
- regenerates or restores the ignored local binding consistently;
- records trigger, moves, hashes, staged state and post-rollback doctor result;
- stops without deleting any backup or evidence.

## P4-E parking and protected state

P4-E remains at accepted `DESIGN_REVIEW_PASS`, findings/waivers `NONE/NONE`.
Its INTAKE, reviews, repaired DESIGN, handoff and uncommitted continuity work
must remain unchanged except for the exact active-pointer/parking carriers
later authorized. P4-E SPEC and all P4-E product work remain unauthorized.

The pre-existing operator assessment
`docs/decisions/ASSESSMENT_2026-07-23_OPERATIONS_WORKSPACE_REPOSITIONING.md`
must not be opened, read, edited, staged, hashed, inventoried or used as
evidence. Broad untracked-file inventory is forbidden.

## Risk and evidence boundary

- R2 is required because later phases may authorize public network access,
  hidden-Core replacement, workspace-root writes and governance-pin changes.
- Core source changes do not become downstream runtime behavior merely because
  the reference clone is refreshed. This tranche may claim only pin/freshness
  reconciliation and deterministic repository evidence.
- No claim that CVF governs AI or agent behavior is made. No provider call is
  required or authorized for this maintenance claim.
- No secret, credential, dependency installation, product/database mutation,
  deployment, release, commit or push is in scope.

## Stop conditions

Stop on Core dirt, unexpected ancestry, target movement, remote mismatch,
changed reconciler/root-effect surface, missing backup or rollback capacity,
undeclared root/downstream delta, P4-E byte drift outside authorized carriers,
protected-assessment access, secret exposure, staged content or any failed
deterministic gate. Any target rebase requires new explicit operator authority
and bounded rereview before external effects.

## Acceptance for INTAKE

Independent review must confirm authority, R2 classification, exact observed
refs/ancestry/delta, the non-documentation Core scope, unchanged reconciler
surface, complete contemplated root effects, rollback obligation, frozen
network boundary, P4-E parking/protection and the no-provider/no-governance-
behavior-claim boundary.

## Next governed move

`INDEPENDENT_INTAKE_REVIEWER` returns exactly one of `INTAKE_REVIEW_PASS`,
`INTAKE_REVIEW_CHANGES_REQUIRED` or `INTAKE_BLOCKED_SOURCE_OR_OWNER`.
