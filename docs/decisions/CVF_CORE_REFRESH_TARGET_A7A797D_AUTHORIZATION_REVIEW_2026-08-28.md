# Independent Authorization Review — CVF Core Target `a7a797d`

- Review date: `2026-08-28`
- Tranche: `CVF-CORE-REFRESH-TARGET-A7A797D-2026-08-28`
- Phase: `WORK_ORDER`
- Role: `INDEPENDENT_AUTHORIZATION_REVIEWER`
- Risk: `R2`
- Reviewed amendment raw SHA-256:
  `6f4d252519a34517b369f44b1eaef82c98da43869831bc99caae53db62a291ec`
- Disposition: `AUTHORIZATION_REVIEW_PASS`

## Authority, target and predecessor

The operator explicitly approved the full target
`a7a797d7111be472ef2cbd928cbeffc70ccb6bc6` on `2026-08-28`. This authority
permits exactly one execution for that target. The completed `a0ef5923...`
execution is predecessor evidence only; its authority is consumed and cannot
authorize a retry or later target.

Local read-only Git checks confirm:

- project `HEAD == origin/main ==
  604addc93c7e971fa270d52d7ac562bfdf272ab8`;
- hidden Core is clean at
  `a0ef5923d100b02c43294815ac9d01d8db20e8b8`;
- Core origin is exactly
  `https://github.com/Blackbird081/Controlled-Vibe-Framework-CVF.git`;
- local Core `origin/main` and the available target object both equal the full
  frozen `a7a797d...` target; and
- `a7a797d...` descends from `a0ef5923...`.

The predecessor amendment has the frozen raw SHA-256 `dd0d43f...`; its
authorization review exists, and its completion review records
`COMPLETION_REVIEW_PASS` with findings/waivers `NONE/NONE`.

## Frozen contracts and commands

The target-neutral inputs match their frozen SHA-256 values:

- DESIGN: `0db70eb33acbfbe5e0e0a449846d370da43e8de71519b26885dfa539f6c877d8`;
- SPEC: `427453a64940bf926f74ec0e2a09736823f3394f6492d7bdf925cc12de0683b3`;
- parent Work Order:
  `30022a03f3ff72489a0959a72effc31b238230e2bb9c6251d70f21b95a98c81a`;
- reconciler:
  `96ac0cce3bf9df5733ffe2c6f5a7850db0ccfdc4403daaa70fdb6981dc58196c`;
- initializer:
  `bb37b16256a693853bddfdbcb40c2f7211e6984a90a972da83899962fae209c8`.

The authorized sequence is exact and feasible: reconciler once, scoped
exactly-once replacement of only the manifest and AGENTS pin carriers, then
initializer once. The reconciler command excludes `-UpdateProjectManifests`,
overlay, pending-Core override and every other optional flag. The initializer
owns the worker doctor; the independent completion reviewer owns one later
doctor. No additional worker doctor or direct Git fetch is authorized.

## Exact scope and preservation

The project ceiling is unique and exactly seven paths. Only
`.cvf/manifest.json` and `AGENTS.md` are mutable project carriers; paths 3–7
are role-separated governance/evidence artifacts. The ignored
`.cvf/local-binding.json` is correctly declared as a non-commit initializer
effect. The project staged set is empty.

The P4-D Work Order still identifies exactly `54/54` unique, existing paths.
Their scoped staged set is empty. Capturing their existence, porcelain status
and SHA-256 bytes through explicit pathspecs before BUILD makes the required
post-worker and post-review equality check feasible. No role in this refresh
may edit, restore, stage, commit or push any of those paths.

The target-pinned workspace installer retains the declared effect surface:
14 public-safe root artifacts are written or preserved, and only the three
declared orphaned overlay artifacts may be removed. This equals the exact
17-path root ceiling. The active workspace profile is `operator-local`, so the
reconciler's conditional public-profile synchronization branch is not reached.

Before external execution, the worker must preserve the complete old Core,
ignored binding existence/bytes and all 17 root existence/byte preimages in a
fresh directory proven contained under workspace-root `_cvf-core-backups`.
The ordered rollback restores and verifies the old Core, `17/17` roots,
binding, the two project carriers and all exact-54 preimages; newly created
prestate-absent artifacts are quarantined rather than destructively deleted.
A preflight mismatch remains zero-network and zero-mutation, while a
post-start failure cannot become success or permit a retry.

The protected operator assessment is outside both ceilings and was not
opened, read, hashed, inventoried, staged, edited or used in this review.

## Evidence, network, commit and claim boundaries

The root-effects receipt and worker return require the exact command exits,
Core/pin/binding/root observations, exact-seven comparison, exact-54
preservation, staged-zero proof, reached network graph and rollback result when
applicable. The completion reviewer must recompute the contract and run its
one doctor before releasing commit ownership.

Successful worker network is limited to unauthenticated public Git operations
in the two sanctioned scripts: reconciler clone, initializer fetch and the
initializer-owned doctor fetch. Credentials, provider/product APIs, dependency
installation, database, deployment, destructive deletion, force operations
and all other external effects remain prohibited.

Only `COMPLETION_REVIEW_PASS` with findings/waivers `NONE/NONE` releases the
`COMMIT_STEWARD` to stage and commit exactly paths 1–7 and push that single
commit to project `origin/main`. The separate commit does not close or commit
P4-D.

PASS proves only exact public-Core/pin alignment, bounded workspace/project
effects and doctor success. It is not proof of CVF control over AI/agents,
provider/vendor behavior, P4-D completion, production readiness or deployment
readiness. Therefore no live provider call is required or authorized.

## Findings, waivers and disposition

- Findings: `NONE`.
- Waivers: `NONE`.
- Review external effects: `NONE` — local read-only checks only; no network,
  reconciliation, Core/root/source/continuity mutation, staging, commit or
  push.
- Disposition: `AUTHORIZATION_REVIEW_PASS`.

The separate `IMPLEMENTATION_WORKER` may now perform exactly one execution
under the amendment. Any target, script hash, path ceiling, external-effect
class or commit-ownership movement stops and requires fresh authority.
