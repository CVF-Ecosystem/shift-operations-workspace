# DESIGN — CVF Public-Core Refresh

- Tranche: `CVF-CORE-REFRESH-2026-08-20`
- Phase: `DESIGN`
- Risk: `R2`
- Parent: `INTAKE_REVIEW_PASS`
- Status: `AUTHORIZATION_REVIEW_PASS`
- Author role transition: `DESIGN_AUTHOR` after `INTAKE_REVIEW_PASS`

## Decision

Use the sanctioned `update_cvf_workspace_public_core.ps1` without
`-UpdateProjectManifests`, from the downstream project working directory. It
will preserve the old clean hidden Core in `_cvf-core-backups`, clone the
public tip, refresh the documented workspace-root files, and leave the
operator-local profile unchanged. Then apply exact full-hash pin edits in
`.cvf/manifest.json` and `AGENTS.md`, run the project initializer to regenerate
the ignored local binding, and synchronize project continuity.

Before reconciliation, copy every existing reconciler-managed workspace-root
file that can be overwritten or deleted into a timestamped directory under
`_cvf-core-backups/workspace-root-preimages-*`, preserving relative paths.
Record existence/SHA-256 before and after. Never remove either backup.

## Alternatives

- A plain `git pull --ff-only` has a smaller filesystem effect but does not
  execute the reconciler explicitly required by the project protocol.
- `-UpdateProjectManifests` is rejected because it does not support this
  portable manifest shape and would write a short pin/extra keys.
- Proceeding with P4 while doctor fails is rejected.

## Exact downstream scope

Authorization, evidence, and continuity may create/modify only:

- `.cvf/manifest.json`, `AGENTS.md`, `knowledge/manifest.json`,
  `IMPLEMENTATION_STATUS.json`;
- `SESSION/ACTIVE_SESSION_STATE.json`,
  `CVF_SESSION/ACTIVE_SESSION_STATE.json`,
  `SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json`,
  `SESSION/SESSION_MEMORY.md`;
- `SESSION/handoffs/CVF_CORE_REFRESH_2026-08-20.md` (create);
- `docs/decisions/INTAKE_2026-08-20_CVF_CORE_REFRESH.md` (created/repair);
- `docs/decisions/INTAKE_REVIEW_2026-08-20_CVF_CORE_REFRESH.md` (create);
- `docs/decisions/DESIGN_2026-08-20_CVF_CORE_REFRESH.md` (create/repair);
- `docs/decisions/AUTHORIZATION_REVIEW_2026-08-20_CVF_CORE_REFRESH.md`
  (create, then append final re-review disposition);
- `docs/decisions/CVF_CORE_REFRESH_ROOT_EFFECTS_2026-08-20.json` (create);
- `docs/decisions/CVF_CORE_REFRESH_WORKER_RETURN_2026-08-20.md` (create);
- `docs/decisions/CVF_CORE_REFRESH_COMPLETION_REVIEW_2026-08-20.md` (create);
- `docs/specs/CVF_CORE_REFRESH_SPEC.md` and
  `docs/work_orders/CVF_CORE_REFRESH_WORK_ORDER.md`.

No catalog or roadmap change is needed: this is governance continuity, not a
module/product milestone. P3-B remains blocked and Phase 4 remains parked.

## Rollback

On any post-reconciler failure, the IMPLEMENTATION_WORKER verifies that the
Core, backup, failed-clone and root-preimage paths resolve inside the named
workspace root; moves (does not delete) the replacement Core to
`_cvf-core-backups/.Controlled-Vibe-Framework-CVF-failed-<timestamp>`; moves
the original timestamped Core backup back to the canonical Core path; restores
overwritten root files from preimages; and moves root files that were absent
before BUILD but newly created into a timestamped failed-root-delta directory.
No clone, backup or evidence is deleted. The worker records the trigger, path
checks, moves, restored hashes and resulting doctor state before stopping.
