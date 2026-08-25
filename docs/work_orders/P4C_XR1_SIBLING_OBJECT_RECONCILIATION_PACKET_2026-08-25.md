# XR1 sibling object reconciliation control packet

- Parent: `P4C-INTEGRATION-EDGE-2026-08-23`
- Purpose: clear `P4C-COMP-REV-F1` without weakening the full-suite gate
- Risk: `R2` (authorized GitHub fetch into an independent sibling clone)
- Operator authority: granted 2026-08-25
- P4-C product BUILD: unchanged and complete at exact 67 paths

## INTAKE

Independent review proved that the P4-C full suite is blocked by
`test_operations_authorized_contract_is_reciprocal_when_sibling_present`.
The clean, non-shallow sibling `CVF-Operations-Workspace` clone has local
`HEAD == origin/main == 3ed0fc83...`, while GitHub advertises public `main ==
f320229c...`; objects `f99b3bf...` and `a944b72e...` are absent locally. The
operator approved a separate sibling reconciliation. No Operations BUILD or
source change is requested.

## DESIGN

Run exactly one non-branch-changing fetch:

`git -C <CVF-Operations-Workspace> fetch origin main`

This may update the sibling object database and `origin/main` only. It must not
checkout, merge, rebase, reset, clean, stash, edit, stage, commit or push. The
sibling working branch/HEAD and files remain unchanged. If either required
object is still absent after fetch, stop and retain the P4-C blocker.

## SPEC

After fetch:

1. sibling worktree and staged sets remain empty;
2. sibling `HEAD` remains `3ed0fc83cc542f9c2af2c17ee9cbed60b891e74a`;
3. `origin/main` equals the fetched public tip;
4. `git cat-file -e <object>^{commit}` succeeds for both
   `f99b3bf916985572e633275311a11aef4bd3aabf` and
   `a944b72e84b22abed184a9b678c9b0b0ab3e65c3`;
5. the isolated XR1 test passes, then the complete non-live suite passes in
   `shift-operations-workspace` without deselection;
6. P4-C exact-67 scope, staged-zero, Knowledge/session/invariant/catalog/
   file-size/repository/doctor guards remain green.

No provider, credential, install, deployment, database effect, source edit,
commit or push is authorized. This fetch is environmental reconciliation, not
Operations BUILD or governance-behavior proof.

## WORK_ORDER

- Worker: separate `ENVIRONMENT_REPAIR_WORKER`.
- Allowed external effect: the exact fetch command above, once.
- Allowed filesystem effect: Git-managed sibling object database and
  `refs/remotes/origin/main` only.
- Project file edit ceiling: zero for both repositories.
- Stop on dirty sibling state, unexpected remote, fetch failure, missing
  objects after fetch, branch/HEAD movement, any file diff, test/guard failure,
  credential prompt, or request for another network action.
- Reviewer: independent from the environment worker and must recompute
  object/branch/worktree/test evidence before P4-C can resume FREEZE review.

## Disposition

`READY_FOR_INDEPENDENT_AUTHORIZATION_REVIEW`. No fetch has occurred under this
packet.
