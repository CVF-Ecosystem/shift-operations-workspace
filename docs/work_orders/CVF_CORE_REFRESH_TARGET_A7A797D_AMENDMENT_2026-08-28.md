# Work Order Amendment — CVF Core Target `a7a797d`

- Tranche: `CVF-CORE-REFRESH-TARGET-A7A797D-2026-08-28`
- Parent contract: `CVF-CORE-REFRESH-2026-08-23`
- Phase: `WORK_ORDER`
- Risk: `R2`
- Role: `TARGET_AMENDMENT_AUTHOR`
- Status: `READY_FOR_INDEPENDENT_AUTHORIZATION_REVIEW`
- Target:
  `a7a797d7111be472ef2cbd928cbeffc70ccb6bc6`
- Public remote:
  `https://github.com/Blackbird081/Controlled-Vibe-Framework-CVF.git`
- Operator authority: on `2026-08-28`, the operator explicitly approved the
  exact target `a7a797d7111be472ef2cbd928cbeffc70ccb6bc6`.

## 1. Purpose and precedence

This amendment repairs the renewed Core-freshness prerequisite blocking the
P4-D final audit. It authorizes exactly one refresh execution from the current
project pin `a0ef5923d100b02c43294815ac9d01d8db20e8b8` to the exact target
above, then one independent completion review and one bounded Core-refresh
commit/push.

All authority for prior targets and attempts, including the completed
`a0ef5923...` execution, is historical and cannot be reused. This amendment
supersedes only target-dependent values, the current project base and the
seven dated evidence paths stated here. It otherwise inherits without
broadening the independently passed `a0ef` pattern at:

- prior amendment:
  `docs/work_orders/CVF_CORE_REFRESH_TARGET_A0EF5923_AMENDMENT_2026-08-27.md`
  at raw SHA-256
  `dd0d43f12f61a7c97cadc0852420e3473b874d23c4c67f18824471bf4f439e7a`;
- prior authorization review:
  `docs/decisions/CVF_CORE_REFRESH_TARGET_A0EF5923_AUTHORIZATION_REVIEW_2026-08-27.md`;
- prior completion review:
  `docs/decisions/CVF_CORE_REFRESH_TARGET_A0EF5923_COMPLETION_REVIEW_2026-08-27.md`
  with disposition `COMPLETION_REVIEW_PASS` and findings/waivers `NONE/NONE`.

The accepted target-neutral bootstrap-native architecture and acceptance
contract remain frozen:

- DESIGN:
  `docs/decisions/DESIGN_2026-08-23_CVF_CORE_REFRESH_BOOTSTRAP_NATIVE_SIMPLIFICATION.md`
  at raw SHA-256
  `0db70eb33acbfbe5e0e0a449846d370da43e8de71519b26885dfa539f6c877d8`;
- SPEC:
  `docs/specs/CVF_CORE_REFRESH_BOOTSTRAP_NATIVE_SIMPLIFICATION_SPEC.md`
  at raw SHA-256
  `427453a64940bf926f74ec0e2a09736823f3394f6492d7bdf925cc12de0683b3`;
- parent Work Order:
  `docs/work_orders/CVF_CORE_REFRESH_2026-08-24_BOOTSTRAP_NATIVE_WORK_ORDER.md`
  at raw SHA-256
  `30022a03f3ff72489a0959a72effc31b238230e2bb9c6251d70f21b95a98c81a`.

The retired evidence-contract matrix, synthetic corpus, trace ancestry and
validator-of-validator route remain non-operative. No DESIGN or SPEC rewrite
is required.

## 2. Roles and separation

- `TARGET_AMENDMENT_AUTHOR`: creates only this amendment; no execution,
  network, mutation outside this file, staging, commit or push.
- `INDEPENDENT_AUTHORIZATION_REVIEWER`: reviews this amendment and creates
  only path 4 below. It must return `AUTHORIZATION_REVIEW_PASS` before BUILD.
- `IMPLEMENTATION_WORKER`: performs preflight, preimages, the exact refresh
  sequence, rollback if needed, and creates only paths 5-6 below in addition
  to scoped edits of paths 1-2.
- `INDEPENDENT_COMPLETION_REVIEWER`: after a successful worker return, runs
  one separately owned doctor, verifies the contract and creates only path 7.
- `COMMIT_STEWARD`: acts only after `COMPLETION_REVIEW_PASS`; stages exactly
  paths 1-7, commits them once, and pushes that commit to `origin/main`.
- Authorization and completion reviewers must be independent of the worker.

## 3. Exact project changed-set ceiling

The complete project changed-set ceiling is exactly these seven paths:

1. `.cvf/manifest.json`
2. `AGENTS.md`
3. `docs/work_orders/CVF_CORE_REFRESH_TARGET_A7A797D_AMENDMENT_2026-08-28.md`
4. `docs/decisions/CVF_CORE_REFRESH_TARGET_A7A797D_AUTHORIZATION_REVIEW_2026-08-28.md`
5. `docs/decisions/CVF_CORE_REFRESH_TARGET_A7A797D_ROOT_EFFECTS_2026-08-28.json`
6. `docs/decisions/CVF_CORE_REFRESH_TARGET_A7A797D_WORKER_RETURN_2026-08-28.md`
7. `docs/decisions/CVF_CORE_REFRESH_TARGET_A7A797D_COMPLETION_REVIEW_2026-08-28.md`

Paths 1-2 are the only mutable project carriers. Paths 3-7 are governance and
evidence artifacts owned by the separated roles above. No continuity,
catalog, Knowledge, status, roadmap, product source, test or P4-D path may
change in this prerequisite commit.

The exact 54 paths numbered 1-54 in
`docs/work_orders/P4D_CHANNEL_ADAPTERS_WORK_ORDER.md` are an immutable dirty
set for this refresh. Capture their existence, status and SHA-256 preimages by
explicit pathspec without staging them; after worker and reviewer actions,
prove the same 54 paths retain identical existence, status and bytes. Never
edit, restore, stage, commit or push any member of that P4-D set in this
Core-refresh commit.

The operator assessment remains excluded: do not open, read, hash, inventory,
stage, edit or use it. Do not use broad project untracked/status inventory;
checks must use the explicit seven-path and P4-D exact-54 pathspecs.

## 4. Declared non-commit effects

The reconciler may affect only the hidden sibling Core plus these exact 17
workspace-root paths, all outside the project Git commit:

```text
WORKSPACE_RULES.md
New-CVF-Governed-Project.ps1
Run-CVF-NewProject-Enforcement.ps1
Update-CVF-Workspace.ps1
Update-CVF-Workspace-Public-Profile.ps1
Test-CVF-Workspace.ps1
Repair-CVF-Workspace.ps1
Manage-CVF-Workspace.ps1
.agents/workflows/cvf-onboard.md
.agents/workflows/pre-commit-check.md
CVF_WORKSPACE_USER_GUIDE.md
CVF_WORKSPACE_HUONG_DAN_SU_DUNG.md
CVF_WORKSPACE_CLASSIFICATION_GUIDE.md
WORKSPACE_PROJECT_ENFORCEMENT_BASELINE.json
Get-CVF-Workspace-OverlayProfiles.ps1
Update-CVF-Workspace-Overlay.ps1
CVF_WORKSPACE_OVERLAY_STATUS.json
```

The initializer may rewrite ignored `.cvf/local-binding.json`. Before
execution, preserve the binding's existence/bytes, each root target's
existence/bytes and the complete old hidden Core inside one fresh,
containment-checked directory directly under workspace-root
`_cvf-core-backups`. None is staged or committed.

Success verifies the exact root effect set, target binding and clean Core.
Failure restores and verifies the old Core, the binding's captured
existence/bytes and all `17/17` root targets before returning failure. A root
target or binding absent in prestate but created during a failed attempt is
moved into contained failure evidence, not deleted.

## 5. Frozen scripts and commands

The sanctioned scripts retain the independently passed hashes:

- reconciler SHA-256:
  `96ac0cce3bf9df5733ffe2c6f5a7850db0ccfdc4403daaa70fdb6981dc58196c`;
- initializer SHA-256:
  `bb37b16256a693853bddfdbcb40c2f7211e6984a90a972da83899962fae209c8`.

The worker runs exactly once, in order:

```text
powershell -ExecutionPolicy Bypass -File "<core>\scripts\update_cvf_workspace_public_core.ps1" -WorkspaceRoot "<workspace-root>"
<scoped patch of only .cvf/manifest.json cvfCoreCommit and AGENTS.md CVF Commit>
powershell -ExecutionPolicy Bypass -File scripts/initialize_cvf_clone.ps1
```

The reconciler command must not include `-UpdateProjectManifests`, overlay,
pending-Core override or any other flag. After command 1 exits `0`, the worker
must directly prove the replacement Core is clean and
`HEAD == origin/main == target`. It then replaces exactly once:

- `.cvf/manifest.json` `cvfCoreCommit`; and
- the `AGENTS.md` `CVF Commit` header,

from the full old pin to the full target. Zero or multiple matches, parse
failure, or any other project edit triggers rollback. Only after both values
parse and equal the target may the initializer run.

The independent completion reviewer runs exactly once after worker success:

```text
powershell -ExecutionPolicy Bypass -File "<core>\scripts\check_cvf_workspace_agent_enforcement.ps1" -ProjectPath "<project-root>"
```

## 6. Preflight

Before any mutation or network operation, require and record:

- project `HEAD == origin/main ==
  604addc93c7e971fa270d52d7ac562bfdf272ab8` and staged set empty;
- the amendment and authorization review are present within paths 3-4, and
  the review says `AUTHORIZATION_REVIEW_PASS` with `NONE/NONE`;
- Core resolves to the sibling hidden Core, its worktree/index are clean at
  `a0ef5923d100b02c43294815ac9d01d8db20e8b8`, and origin is the exact
  public remote;
- local fetched `origin/main` and the available target object equal the full
  frozen target, and the target descends from the current Core; if advertised
  `main` later differs, stop and roll back;
- DESIGN, SPEC, parent Work Order, prior pattern, reconciler and initializer
  hashes equal the frozen values above;
- the exact-seven project ceiling and exact-54 P4-D immutable preimages are
  captured through explicit pathspecs, staged set remains empty, and the
  excluded assessment was not accessed or inventoried;
- the fresh backup/evidence directory is resolved and proven contained under
  workspace-root `_cvf-core-backups` before preserving the old Core, binding
  and 17 root preimages.

A preflight mismatch is a zero-network, zero-mutation refusal. It consumes no
execution authority and runs no doctor. Any changed target requires fresh
operator authority rather than an automatic retry.

## 7. Network and external-effect ceiling

The one successful worker execution permits only the unauthenticated public
Git operations inherent in the two sanctioned scripts: reconciler clone,
initializer fetch, and initializer-owned doctor fetch. The independent
completion reviewer owns one later doctor fetch. There is no extra worker
doctor and no direct Git fetch outside those scripts.

On post-start failure, only the reached worker prefix plus one rollback-
verifier doctor after complete restoration is permitted; no completion doctor
runs. Credentials, provider/product APIs, dependency installation, database,
deployment, destructive deletion, force operations and any other network or
external effect are prohibited.

## 8. Evidence and success conditions

Path 5 records the target, timestamps, backup containment, old/new Core facts,
binding pre/post state, all 17 root pre/post existence and hashes, exact
commands/exits, reached network graph, scoped pin-patch result, exact-seven
project comparison, P4-D exact-54 preservation, staged-zero state and rollback
result when applicable. Path 6 links that receipt and records the worker
disposition and claim boundary. Plain transcripts remain in the contained
evidence directory.

Worker success requires:

- Core clean and exact public remote;
- `Core HEAD == Core origin/main == manifest cvfCoreCommit == ignored binding
  resolvedCoreCommit == AGENTS CVF Commit == target`;
- initializer-owned doctor exits `0` with PASS or the already accepted bounded
  legacy-catalog note only;
- root effects are contained within the exact 17 and project effects within
  paths 1-6; P4-D exact-54 bytes/status/existence are unchanged;
- project staged set is empty and no prohibited effect occurred.

Completion review recomputes those checks, runs its one doctor, verifies path
7 is its only project edit, and returns findings/waivers explicitly. Only
`COMPLETION_REVIEW_PASS` with `NONE/NONE` releases commit ownership.

## 9. Rollback and stop conditions

After any mutation/external execution failure, preserve the failed Core and
evidence, then restore and verify in order: old Core, all `17/17` root targets,
ignored local binding, paths 1-2 and all exact-54 P4-D preimages. Retain paths
3-6 as the bounded governance/failure record. Run exactly one rollback-
verifier doctor only after restoration; record its result and stop. Rollback
cannot convert failure into success or permit a retry.

Stop on target/remote/script/hash movement; dirty Core; nonempty staged set;
missing authorization; backup/containment failure; any path outside the exact
ceilings; any P4-D preimage drift caused during this refresh; assessment
access; unexpected root/binding effect; failed command/doctor/restore; or need
for a prohibited effect. A new target or second execution requires fresh
operator authority and a new amendment/review.

## 10. Staging, commit and push

After `COMPLETION_REVIEW_PASS`, the `COMMIT_STEWARD` must:

1. verify project `HEAD == origin/main == 604addc...`, staged set empty,
   exact-seven final changed set, P4-D exact-54 preservation, clean target Core
   and all pin equality;
2. stage the seven paths by explicit literal pathspec only and prove the staged
   set equals exactly paths 1-7; never stage P4-D or the assessment;
3. commit once with message
   `chore(cvf): refresh core to a7a797d (doctor pass)`;
4. verify the commit contains exactly paths 1-7 and the worktree still retains
   the untouched P4-D exact-54 set; and
5. push that single commit to `origin main`, then verify local
   `HEAD == origin/main`.

Any mismatch stops before commit or push. P4-D final audit resumes only after
this separate Core-refresh commit/push succeeds; this amendment does not
itself close, FREEZE or commit P4-D.

## 11. Claim boundary and disposition

PASS proves only that this workspace's public hidden Core and three pin
carriers (manifest, ignored local binding and AGENTS header) are aligned to the
exact approved public target, with bounded root/project effects and doctor
success. It does not prove CVF controls AI/agent behavior, live-provider or
vendor behavior, production readiness, deployment readiness, or P4-D closure.
No provider call is required or authorized for this maintenance claim.

Disposition: `READY_FOR_INDEPENDENT_AUTHORIZATION_REVIEW`.
No reconciliation, network, mutation outside this amendment, staging, commit
or push is authorized until the independent authorization review passes.
