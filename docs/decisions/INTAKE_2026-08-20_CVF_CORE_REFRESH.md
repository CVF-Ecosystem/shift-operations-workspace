# INTAKE — CVF Public-Core Refresh

- Tranche: `CVF-CORE-REFRESH-2026-08-20`
- Control-chain phase: `INTAKE`
- Risk: `R2`
- Status: `OPEN_FOR_INDEPENDENT_INTAKE_REVIEW`
- Execution base: `7d525b6681bd6b51ac89fb32ddcf57136fb95d2e`
- Operator authority: `2026-08-20` response “đồng ý” to the proposed
  `reconcile core -> consider P4-A` sequence
- Active role: `INTAKE_AUTHOR`

## Request boundary

Restore the mandatory workspace doctor freshness gate before any roadmap
tranche opens. The operator authority covers this reconciliation only. It does
not open P4-A, P4-A2, or any provider/runtime lane.

## Verified current truth

- Hidden public Core path:
  `D:\UNG DUNG AI\TOOL AI 2026\CVF-Workspace\.Controlled-Vibe-Framework-CVF`.
- Remote is the expected public URL and the hidden-Core worktree is clean.
- Hidden-Core HEAD and downstream pins are
  `2103a38fda01ee827e9fc6c3be38a824fa5d54ad`.
- Local `origin/main` is
  `7d9f360a3df11ac998972728000785799399c02b`.
- Workspace doctor result is `FAIL (23/25)`, with the sole failure
  `BEHIND_PUBLIC_REMOTE`; the legacy-catalog result is a bounded warning.
- The upstream delta is one public documentation commit touching four public
  Core documentation files. No downstream product source is involved.

## Intended outcome

1. Use the sanctioned public-Core reconciler named by `AGENTS.md` and the
   doctor to replace the clean hidden Core with the current public tip while
   preserving the prior clone in the reconciler-managed backup directory.
2. Update the exact downstream pin surfaces `.cvf/manifest.json` and the
   generated `AGENTS.md` header to the full new commit.
3. Synchronize the compact/canonical continuity carriers and create a bounded
   evidence/review record.
4. Run `scripts/initialize_cvf_clone.ps1` after the pin edit so the ignored
   `.cvf/local-binding.json.resolvedCoreCommit` is regenerated to the exact
   hidden-Core HEAD; require that value, the manifest pin, Core HEAD and
   `origin/main` to be identical.
5. Require doctor PASS, session-state/mirror PASS, JSON validity, diff hygiene,
   and independent R2 review before FREEZE.

## Declared external filesystem effects

The reconciler moves the old clean hidden Core into the timestamped
`<workspaceRoot>/_cvf-core-backups/` directory, clones the replacement, and
rewrites `WORKSPACE_RULES.md`. Its wrapper installer rewrites these workspace
root artifacts:

- `New-CVF-Governed-Project.ps1`
- `Run-CVF-NewProject-Enforcement.ps1`
- `Update-CVF-Workspace.ps1`
- `Update-CVF-Workspace-Public-Profile.ps1`
- `Test-CVF-Workspace.ps1`
- `Repair-CVF-Workspace.ps1`
- `Manage-CVF-Workspace.ps1`
- `.agents/workflows/cvf-onboard.md`
- `.agents/workflows/pre-commit-check.md`
- `CVF_WORKSPACE_USER_GUIDE.md`
- `CVF_WORKSPACE_HUONG_DAN_SU_DUNG.md`
- `CVF_WORKSPACE_CLASSIFICATION_GUIDE.md`

It preserves an existing `WORKSPACE_PROJECT_ENFORCEMENT_BASELINE.json`, and
may delete these obsolete overlay artifacts if present:
`Get-CVF-Workspace-OverlayProfiles.ps1`,
`Update-CVF-Workspace-Overlay.ps1`, and
`CVF_WORKSPACE_OVERLAY_STATUS.json`. The active profile is `operator-local`,
so public-profile synchronization will not run.

The only authorized network effects are unauthenticated public Git operations
against `https://github.com/Blackbird081/Controlled-Vibe-Framework-CVF.git`:
one `git clone` performed by the reconciler and one `git fetch origin main`
performed by `scripts/initialize_cvf_clone.ps1`. No credential, provider, or
product API/network endpoint is authorized. If either operation observes a
tip other than the frozen target `7d9f360a3df11ac998972728000785799399c02b`,
BUILD must execute the Work Order rollback and stop.

BUILD must capture existence and SHA-256 preimages for every named root file,
capture postimages, and record any create/delete delta. Rollback evidence must
identify the timestamped hidden-Core backup and preserve preimages sufficient
to restore root artifacts. No destructive cleanup of backups is authorized.

## Boundaries

- No P4-A/P4-A2, AI Gateway, RAG, provider, product API, database, runtime,
  deployment, or product-source change.
- No provider secret may be read or printed. No live-provider proof is needed
  because the tranche makes no claim that CVF governs AI/agent behavior.
- Do not use `-UpdateProjectManifests`: the reconciler's implementation uses a
  non-portable `cvfCorePath` gate and writes a short pin plus extra fields.
- Historical evidence remains historical and is not rewritten.
- `.cvf/local-binding.json` is ignored local state, not a commit surface, but
  its currently stale `resolvedCoreCommit` (`27137db4...`) must be regenerated
  and verified after the manifest/Core update.
- Do not commit or push until independent REVIEW accepts the complete changed
  set. Commit ownership is assigned later by WORK_ORDER.

## Stop conditions

Stop before BUILD if independent review rejects this boundary. During BUILD,
stop if the hidden Core is dirty, the remote changes, the target is no longer
`origin/main`, reconciliation cannot preserve/restore the old clone, project
source changes, continuity drifts, or the doctor has any new failure.

## Acceptance for INTAKE

Independent review must confirm the operator authority, R2 classification,
exact observed mismatch, reconciliation-only objective, external filesystem
effects, P4 parking, and no-governance-claim boundary.

## Next governed move

`INDEPENDENT_INTAKE_REVIEWER` returns exactly one of:
`INTAKE_REVIEW_PASS`, `INTAKE_REVIEW_CHANGES_REQUIRED`, or
`INTAKE_BLOCKED_SOURCE_OR_OWNER`.
