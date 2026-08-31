# WORK ORDER — CVF Public-Core Refresh Target Rebase

- Tranche: `CVF-CORE-REFRESH-TARGET-REBASE-2026-08-30`
- Phase: `WORK_ORDER`
- Risk: `R2`
- Status: `READY_FOR_INDEPENDENT_AUTHORIZATION_REVIEW`
- BUILD external-effect authority: `NOT_GRANTED_BY_THIS_DOCUMENT`
- Old Core/pin: `a7a797d7111be472ef2cbd928cbeffc70ccb6bc6`
- Frozen target: `d7860138350130d6d105826ce186f1beeaba3c2d`
- Accepted DESIGN SHA-256:
  `90313677f0efffcc2e5dd78b6e1efb95e2e919c1494adc9c9274128ec0865f73`
- Accepted DESIGN review SHA-256:
  `0fb6841c68093800e265784768e0feb38ccf188ad1b518d6a8bf750ed6e40bdc`
- Final accepted SPEC SHA-256:
  `f8c2de27e5aca67f53bb530cd9bbce17abc1f3b65a56ad7bfe5ba0a1fb044161`
- Final SPEC review/rereview SHA-256:
  `b9fadce65a8f40da68e82dc0a832dfede1e327ce1fc2b2656247a9dcfc182ecb`
- Final matrix raw/canonical SHA-256:
  `dc0c35298fb584d995f51ed8cf996f599f12b934617afd51e1a27b24ce47f4cc`
- Final machine-pin raw/canonical SHA-256:
  `4ce97c9823ae63447ffe158ae9b0d81ac7690a19c019b368ce00da5be8793b66`
- Accepted registry raw/canonical SHA-256:
  `e22195a46528feff89ee7f622ac1d964a0a94e9acc8b85f82a93de77c57525c5`

## 1. Authorization boundary

This Work Order translates only the accepted target-rebase DESIGN and final
SPEC into a bounded execution contract. Independent
`AUTHORIZATION_REVIEW_PASS` makes this contract eligible for a later operator
decision; it does not authorize BUILD or any external effect. After that
review, the ORCHESTRATOR must obtain and record explicit operator approval of
the external-effect boundary before assigning an `IMPLEMENTATION_WORKER`.

Without that later approval, network use, hidden-Core/workspace-root mutation,
pin or binding mutation and evidence creation remain prohibited. Credentials,
provider calls, package installation, product/runtime/database changes,
deployment, release, commit and push are outside this Work Order in every
outcome. `COMMIT_STEWARD` is inactive.

The protected operator assessment is excluded from open, read, hash, stage,
inventory and use by every role. Broad downstream untracked inventory is
forbidden. Attempt-1 artifacts, evidence directory, preserved replacement and
retained failure deltas are immutable.

## 2. Bound phase lineage and fixed locations

The accepted preceding lineage is fixed to:

| Artifact | Raw/canonical SHA-256 |
|---|---|
| `docs/decisions/INTAKE_2026-08-30_CVF_CORE_REFRESH_TARGET_REBASE.md` | `f4efd86c242132082949432f7c44e0f1304599826b0e823fdff3abd39cf77294` |
| `docs/decisions/INTAKE_REVIEW_2026-08-30_CVF_CORE_REFRESH_TARGET_REBASE.md` | `fc381ad4485a57760b029c9072cdd3aee93333b0dd6c9d026cbc1e13625df865` |
| `docs/decisions/DESIGN_2026-08-30_CVF_CORE_REFRESH_TARGET_REBASE.md` | `90313677f0efffcc2e5dd78b6e1efb95e2e919c1494adc9c9274128ec0865f73` |
| `docs/decisions/DESIGN_REVIEW_2026-08-30_CVF_CORE_REFRESH_TARGET_REBASE.md` | `0fb6841c68093800e265784768e0feb38ccf188ad1b518d6a8bf750ed6e40bdc` |
| `docs/specs/CVF_CORE_REFRESH_TARGET_REBASE_2026-08-30_SPEC.md` | `f8c2de27e5aca67f53bb530cd9bbce17abc1f3b65a56ad7bfe5ba0a1fb044161` |
| `docs/decisions/SPEC_REVIEW_2026-08-30_CVF_CORE_REFRESH_TARGET_REBASE.md` | `b9fadce65a8f40da68e82dc0a832dfede1e327ce1fc2b2656247a9dcfc182ecb` |

Fixed locations are:

- workspace root:
  `D:\UNG DUNG AI\TOOL AI 2026\CVF-Workspace`;
- downstream project root:
  `D:\UNG DUNG AI\TOOL AI 2026\CVF-Workspace\shift-operations-workspace`;
- hidden Core root:
  `D:\UNG DUNG AI\TOOL AI 2026\CVF-Workspace\.Controlled-Vibe-Framework-CVF`;
- public remote:
  `https://github.com/Blackbird081/Controlled-Vibe-Framework-CVF.git`; and
- contained attempt-2 evidence directory, required absent at preflight:
  `D:\UNG DUNG AI\TOOL AI 2026\CVF-Workspace\_cvf-core-backups\CVF-CORE-REFRESH-2026-08-30-ATTEMPT-2-EVIDENCE`.

Any different remote, old pin, target, ancestry, advertised tip, cloned target,
resolved container or accepted artifact hash stops fail-closed. No role may
adopt or rebase to a different target inside this tranche.

## 3. Exact accepted tool and profile bindings

Preflight and independent authorization review must recompute all bindings:

| Surface | Accepted binding |
|---|---|
| Core reconciler raw SHA-256 | `96ac0cce3bf9df5733ffe2c6f5a7850db0ccfdc4403daaa70fdb6981dc58196c` |
| Core reconciler Git blob | `4b705c6bf7b10bda62520dca488ecb453a4f4945` |
| Core doctor raw SHA-256 | `2410bbabf88f12581d2e34a71efe247fe9080ebb299a58eb6f9ff6a35818796b` |
| Core doctor Git blob | `2ad83efee05c738fec40aa1779929da07f3d1c8c` |
| Core new-workspace raw SHA-256 | `7e5567c55026f3be44f11c924d44835d6fb98b1fb4268dfedf6453af89927032` |
| Core new-workspace Git blob | `5f311a1a1c8dc787c7b19011bf34c5a84fc773c7` |
| Core `governance/toolkit/05_OPERATION` tree | `23fe8bd39ae102d3302d34de1d80208e2ef9bbb6` |
| Downstream initializer raw SHA-256 | `bb37b16256a693853bddfdbcb40c2f7211e6984a90a972da83899962fae209c8` |
| Active `operator-local` profile raw SHA-256 | `f51bacd206ec4e95b92f4f4479bc7c68ee605db3752d514ff3094bdff02dc855` |

The three Core script blobs and operation-tree binding must be equal at old
pin and frozen target. Any drift requires a fresh governed target rebase, not a
repair or retry under this Work Order.

## 4. Roles and non-concurrent ownership

- `ORCHESTRATOR`: records gates, operator authority and role routing; does not
  implement or self-approve.
- `WORK_ORDER_AUTHOR`: owns only this authorization contract; grants no
  external effect.
- `INDEPENDENT_AUTHORIZATION_REVIEWER`: may create only the authorization
  review named in section 13; does not execute BUILD.
- `IMPLEMENTATION_WORKER`: after later explicit operator approval only, owns
  zero-effect preflight, preimages, initial execution, worker-time rollback,
  the first two tracked evidence artifacts and worker return.
- `INDEPENDENT_COMPLETION_REVIEWER`: owns only the completion review and its
  separately authorized single doctor; never repairs.
- `REPAIR_WORKER`: only after immutable `REVIEW_TARGET_MOVEMENT`, owns
  rollback-only restoration from frozen BUILD preimages and the conditional
  rollback JSON; never reconciles, retargets or retries.
- `INDEPENDENT_COMPLETION_REREVIEWER`: owns only the conditional terminal
  Markdown and its separately authorized single rereviewer doctor.
- `CLOSER/SESSION_SYNC_STEWARD`: acts only after accepted terminal review.
- `COMMIT_STEWARD`: inactive; no commit or push authority exists.

The implementation worker, repair worker and each review role must be distinct
assignments. Reviewers cannot approve artifacts they authored. Role windows do
not overlap.

## 5. Exact command graph and checkpoints

From the downstream project root, and only after later explicit operator
approval, the initial worker may invoke exactly these two top-level commands in
this order:

```text
powershell -ExecutionPolicy Bypass -File "D:\UNG DUNG AI\TOOL AI 2026\CVF-Workspace\.Controlled-Vibe-Framework-CVF\scripts\update_cvf_workspace_public_core.ps1" -WorkspaceRoot "D:\UNG DUNG AI\TOOL AI 2026\CVF-Workspace"
powershell -ExecutionPolicy Bypass -File "D:\UNG DUNG AI\TOOL AI 2026\CVF-Workspace\shift-operations-workspace\scripts\initialize_cvf_clone.ps1"
```

The reconciler is invoked exactly once. Immediately after it returns, before
any pin edit or initializer, the worker records the full transcript, exit code,
Core/replacement/backup locations, 17 root observations and replacement state,
then proves exact remote, clean Core and
`Core HEAD == Core origin/main == d7860138350130d6d105826ce186f1beeaba3c2d`.
Any failure at this checkpoint routes worker-time rollback and stops.

Only after that checkpoint passes, the worker uses scoped `apply_patch` edits
to replace exactly one occurrence of the old full pin in
`.cvf/manifest.json.cvfCoreCommit` and exactly one occurrence in the generated
`AGENTS.md` `CVF Commit` header. It parses both and proves exact target equality
before invoking the initializer exactly once.

Successful worker network accounting is exactly three ordered top-level Git
network operations inherent in the sanctioned graph: reconciler clone,
initializer fetch, initializer-doctor fetch. An executed failure records only
its actual ordered prefix. No manual Git network command, direct checkout,
custom clone, overlay, `-UpdateProjectManifests`, pending-backup override,
separate worker doctor, alternate remote, credential helper, retry or
in-attempt target rebase is permitted.

The completion reviewer, or one separately authorized rereviewer, may invoke at
most one exact doctor in its own role window:

```text
powershell -ExecutionPolicy Bypass -File "D:\UNG DUNG AI\TOOL AI 2026\CVF-Workspace\.Controlled-Vibe-Framework-CVF\scripts\check_cvf_workspace_agent_enforcement.ps1" -ProjectPath "D:\UNG DUNG AI\TOOL AI 2026\CVF-Workspace\shift-operations-workspace"
```

A rollback worker must invoke that same command exactly once after restoration
before any complete-rollback claim. It is a rollback verifier, not a
reconciliation retry and not a worker counter. If rollback is already
incomplete, or the verifier fails, the exact stage/verifier state is governed
only by the matrix.

## 6. Zero-effect preflight and preservation

Before the first external effect, the implementation worker must record and
require all final SPEC R1-R5 predicates:

- exact contained workspace, downstream, hidden-Core, backup and evidence
  paths, with no reparse-point escape;
- expected remote; clean Core at the old full pin; locally available frozen
  target and accepted ancestry; downstream staged-zero;
- all phase, SPEC, review, matrix, pin, registry, tool and profile hashes in
  sections 2-3; exact `operator-local` profile;
- all six attempt-2 evidence paths absent and collision-free;
- recoverable preimages for old Core, all 17 roots, two pins, nine shared
  carriers and ignored binding, each recorded as `PRESENT` with raw hash/bytes
  or `ABSENT` as applicable;
- allowlisted preservation hashes for parked P4-E and current governance
  artifacts; and
- contained prior backups, failed replacements and root deltas protected from
  overwrite, rename, deletion or reinterpretation.

Any false, unreadable or mismatched predicate selects zero-effect refusal:
there is no network/Core/root/pin/binding mutation and none of the six
attempt-2 evidence paths may be created. No doctor is run for refusal.

Preservation must finish before the reconciler. It includes the old Core,
exact 17 roots, two pins, nine shared carriers, ignored binding and accepted
protected hashes. Preservation locations must be contained and recoverable.

## 7. Exact 17 workspace-root targets

The reconciler root-effect ceiling is exactly this ordered set:

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

Each target is accounted exactly once as `CREATE`, `UPDATE`, `DELETE` or
`NO_CHANGE`. Success and complete rollback require `17/17`; no other
workspace-root effect is allowed. Originally absent targets return to absence
on rollback. Backups, failed replacements and failed-root deltas are retained.

## 8. Attempt-2 evidence lifecycle and downstream ceilings

The complete six-path attempt-2 lifecycle is:

1. `D:\UNG DUNG AI\TOOL AI 2026\CVF-Workspace\_cvf-core-backups\CVF-CORE-REFRESH-2026-08-30-ATTEMPT-2-EVIDENCE`;
2. `docs/decisions/CVF_CORE_REFRESH_ROOT_EFFECTS_2026-08-30_ATTEMPT_2.json`;
3. `docs/decisions/CVF_CORE_REFRESH_WORKER_RETURN_2026-08-30_ATTEMPT_2.md`;
4. `docs/decisions/CVF_CORE_REFRESH_COMPLETION_REVIEW_2026-08-30_ATTEMPT_2.md`;
5. `docs/decisions/CVF_CORE_REFRESH_REVIEW_TARGET_MOVEMENT_ROLLBACK_2026-08-30_ATTEMPT_2.json`; and
6. `docs/decisions/CVF_CORE_REFRESH_REVIEW_TARGET_MOVEMENT_REREVIEW_2026-08-30_ATTEMPT_2.md`.

The initial worker may change at most these exact 13 tracked paths:

```text
.cvf/manifest.json
AGENTS.md
knowledge/manifest.json
IMPLEMENTATION_STATUS.json
SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json
SESSION/ACTIVE_SESSION_STATE.json
CVF_SESSION/ACTIVE_SESSION_STATE.json
SESSION/SESSION_MEMORY.md
SESSION/handoffs/CVF_CORE_REFRESH_TARGET_REBASE_2026-08-30.md
docs/INDEX.md
docs/implementation/EXECUTION_ROADMAP.md
docs/decisions/CVF_CORE_REFRESH_ROOT_EFFECTS_2026-08-30_ATTEMPT_2.json
docs/decisions/CVF_CORE_REFRESH_WORKER_RETURN_2026-08-30_ATTEMPT_2.md
```

Ignored `.cvf/local-binding.json` is the one additional local effect. The first
two tracked paths are pin carriers, the next nine are shared continuity
carriers and the final two are worker evidence. Every other downstream path is
byte-protected during BUILD, including the closed attempt-1 handoff, dedicated
P4-E/governance artifacts, product/runtime/database/catalog files and all
current SPEC, Work Order and review artifacts.

The completion reviewer has a one-artifact ceiling: it alone may create
`docs/decisions/CVF_CORE_REFRESH_COMPLETION_REVIEW_2026-08-30_ATTEMPT_2.md`.
It may not edit the worker receipt or return.

Only after immutable `REVIEW_TARGET_MOVEMENT`, the repair worker may mutate
exactly these 11 pre-existing tracked pin/shared carriers:

```text
.cvf/manifest.json
AGENTS.md
knowledge/manifest.json
IMPLEMENTATION_STATUS.json
SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json
SESSION/ACTIVE_SESSION_STATE.json
CVF_SESSION/ACTIVE_SESSION_STATE.json
SESSION/SESSION_MEMORY.md
SESSION/handoffs/CVF_CORE_REFRESH_TARGET_REBASE_2026-08-30.md
docs/INDEX.md
docs/implementation/EXECUTION_ROADMAP.md
```

It may additionally create only
`docs/decisions/CVF_CORE_REFRESH_REVIEW_TARGET_MOVEMENT_ROLLBACK_2026-08-30_ATTEMPT_2.json`
and restore/regenerate ignored `.cvf/local-binding.json`: at most 12 tracked
paths plus one ignored local effect. Worker receipt, worker return and movement
review remain immutable. The rereviewer alone may create
`docs/decisions/CVF_CORE_REFRESH_REVIEW_TARGET_MOVEMENT_REREVIEW_2026-08-30_ATTEMPT_2.md`.

The initial root-effects JSON is the worker's semantic receipt and worker
Markdown is only a summary. Neither self-hashes nor cross-hashes. Completion
review owns their final hashes and does not self-hash. Conditional rollback
JSON does not self-hash. Terminal rereview owns hashes for all readable prior
attempt-2 artifacts and does not self-hash or depend on a future artifact.

## 9. Success, failure, rollback and reviewer movement

After the two-pin bridge, initial success requires initializer exit zero,
bounded doctor PASS, clean Core and five-way frozen-target equality across Core
HEAD, Core origin/main, manifest, AGENTS and binding. The worker then writes its
two evidence artifacts and the nine shared carriers, runs all applicable gates,
leaves staged zero and returns without claiming tranche closure.

Every post-start failure is preservation-first: containment-check and preserve
the failed state; restore old Core, all 17 roots, pins, shared carriers and
binding from preimages; run at most the one matrix-authorized rollback verifier;
write truthful evidence; and stop without retry. Complete rollback and
incomplete rollback are disjoint. Incomplete rollback may not fabricate Core
or pin hashes, staged-zero, P4-E preservation or hashes for unreadable
artifacts.

If independent completion review observes public target movement after a
successful worker return, it records immutable `REVIEW_TARGET_MOVEMENT` and
stops. This is neither success nor target adoption. A distinct repair worker
may then perform rollback only from frozen BUILD preimages, with no reconciler,
retarget or retry, and create the conditional JSON. A distinct rereviewer owns
the terminal review. Only accepted success or accepted complete-rollback review
may route to bounded FREEZE; incomplete rollback remains open failure.

The registered matrix in section 10 is the sole semantic owner of per-outcome
required, forbidden and conditional fields, exact counter relations, failure-
stage/prefix pairs, rollback-stage/verifier pairs and evidence lifecycle. This
Work Order does not restate those rules. Every receipt and review projection
must match exactly one of the matrix's closed outcomes.

## 10. Invariant-family proof

- **Applicability decision:** `TRIGGERED`; registered family
  `CVF-CORE-REFRESH-TARGET-REBASE-OUTCOMES-2026-08-30`, risk `R2`, lifecycle
  `ACTIVE`.
- **Matrix id / canonical digest:** family above at
  `docs/cvf/invariants/cvf-core-refresh-target-rebase-outcomes-2026-08-30.json`,
  canonical digest
  `dc0c35298fb584d995f51ed8cf996f599f12b934617afd51e1a27b24ce47f4cc`.
- **Machine pin:**
  `docs/specs/cvf_core_refresh_target_rebase_2026_08_30_invariant_pin.py`, raw
  SHA-256
  `4ce97c9823ae63447ffe158ae9b0d81ac7690a19c019b368ce00da5be8793b66`.
- **Adapter / test paths:** matrix-declared synthetic deterministic identity
  `CVF_CORE_REFRESH_TARGET_REBASE_INLINE_ADAPTER_V3`; no tracked adapter path.
  Evidence tests are `tests/unit/test_invariant_family_contract.py` and
  `tests/integration/test_invariant_family_repository_guard.py`. Disposable
  positives live only inside the contained evidence directory and are derived
  from the pinned matrix, never worker output.
- **Mutation exclusions:** `NONE`.
- **Exact commands:**
  `python scripts/check_invariant_families.py --json` and
  `python -m pytest -q tests/unit/test_invariant_family_contract.py tests/integration/test_invariant_family_repository_guard.py`.
- **Evidence owner:** the `IMPLEMENTATION_WORKER` returns initial conformance;
  a conditional `REPAIR_WORKER` returns its bounded evidence; the independent
  completion reviewer or rereviewer owns independent recomputation and the
  terminal conformance summary in its role window.
- **Reviewer recomputation:** the independent reviewer recomputes the canonical
  digest and complete generated mutation corpus, samples at least one raw
  emitted positive for each of all seven outcomes, checks both declared
  validator surfaces and exclusivity, reruns the focused temporal cross-product
  and verifies no expectation was derived from BUILD output.

Before BUILD return, the matrix-declared adapter emits one disposable positive
per outcome. Both validator surfaces must accept all `7/7` positives
exclusively and reject the complete generated one-fact mutation corpus with no
excluded operator. The final accepted baseline is `686/686` rejected mutations
and `40/40` focused temporal judgments; fresh BUILD/review evidence must be
recomputed rather than copied from SPEC review.

## 11. Deterministic evidence and gates

Worker and reviewer run all applicable JSON parsing, session/mirror, Project
Knowledge, invariant-family, focused invariant tests, catalog, file-size,
repository/scoped-diff and staged-zero guards. The minimum repository commands
include:

```text
python scripts/check_session_state.py
python scripts/check_project_knowledge.py
python scripts/check_invariant_families.py --json
python -m pytest -q tests/unit/test_invariant_family_contract.py tests/integration/test_invariant_family_repository_guard.py
python scripts/generate_catalog.py --check
python scripts/check_file_size.py
```

Evidence must include command, working directory, start/end ordering, exit code
and unambiguous output or retained transcript. JSON artifacts must parse.
Scoped tracked effects must fit the current role's exact ceiling and the staged
set must be zero. A failed deterministic gate cannot be waived into success.

Completion review independently checks tool/phase/matrix hashes, command and
network transcripts, the exact 17-root set, role-specific tracked/local path
ceilings, recoverable preimages, preservation/rollback receipts, five-way
target or honest rollback truth, doctor ownership, all six evidence lifecycle
states, P4-E hashes, attempt-1 immutability and prohibited-effect counts.

## 12. Stop conditions and claim boundary

Stop on target movement; phase/tool/profile/hash/remote/ancestry drift;
preflight, containment or preimage failure; evidence collision or reparse-point
escape; Core/downstream dirt outside the exact role allowlist; unexpected
path/command/network effect; credential need; protected-assessment contact;
failed restore; unreadable required evidence; role overlap; or need for
provider, installation, product/runtime/database change, deployment, release,
commit or push. No stop condition authorizes widening, repair outside the
conditional ceiling, retargeting or retry.

P4-E remains parked at accepted `DESIGN_REVIEW_PASS`; this Work Order cannot
open P4-E SPEC or alter its artifacts. XR1 debt remains separate. The protected
assessment remains excluded as stated in section 1.

This tranche may prove only deterministic public-Core freshness and pin
reconciliation inside the enumerated boundary. It does not prove CVF control
of an AI/agent, provider behavior, product adoption of the 202-path Core delta,
arbitrary-untracked absence, database behavior, deployment or production
readiness. No provider or mock output is governance proof here. Any later claim
about CVF governing AI/agent behavior requires a real provider API call with a
recorded request/response under project policy.

## 13. Authorization review and next governed move

Independent authorization review may create exactly one artifact:
`docs/decisions/AUTHORIZATION_REVIEW_2026-08-30_CVF_CORE_REFRESH_TARGET_REBASE.md`.
It must recompute every bound hash and location, verify command/effect/role/
evidence ceilings, complete all invariant-family proof fields, inspect the
matrix as sole outcome-semantic owner, and record numbered findings and waivers.

Only `AUTHORIZATION_REVIEW_PASS` with findings/waivers explicitly resolved may
route to the ORCHESTRATOR for an operator decision. Even then, BUILD external-
effect authority remains `NOT_GRANTED_BY_THIS_DOCUMENT`: a later explicit
operator approval must be recorded before any implementation worker can run
the reconciler, initializer or doctor or mutate Core/root/pins/binding/evidence.
No commit or push authority is granted.
