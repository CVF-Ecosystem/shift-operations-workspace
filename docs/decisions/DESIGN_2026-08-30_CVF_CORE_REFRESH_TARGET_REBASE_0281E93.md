# DESIGN — CVF Public-Core Exact-Target Rebase 0281e93

- Tranche: `CVF-CORE-REFRESH-TARGET-REBASE-0281E93-2026-08-30`
- Phase: `DESIGN`
- Risk: `R2`
- Status: `READY_FOR_INDEPENDENT_DESIGN_REVIEW`
- Active role: `DESIGN_AUTHOR`
- Accepted INTAKE SHA-256:
  `28e1160993d2638554bdb810dd36f393eebb65db62b47b8f92b8049fc290ba53`
- INTAKE review SHA-256:
  `4c754b7cc47ef247453075e0633848534d121959aba7fb845d49f12975da1b8c`
- Old Core/pin:
  `a7a797d7111be472ef2cbd928cbeffc70ccb6bc6`
- Frozen proposed target:
  `0281e93bab4a75083973eb7242fd2bc8f65055d3`
- BUILD external-effect authority: `NOT_GRANTED`

## 1. Decision

Use a preservation-first bootstrap-native attempt against exactly
`0281e93...`. The later BUILD graph, if an exact Work Order passes independent
authorization review and external-effect authority is then explicitly
recorded, is one sanctioned reconciler, one scoped two-pin bridge and one
downstream initializer. The initializer's doctor fetch is part of that BUILD
effect graph; a later reviewer doctor is a separate REVIEW effect. Neither may
be described as read-only or zero-network.

Every network boundary rechecks the frozen target. A clone or doctor fetch
that observes any other target selects `TARGET_DRIFT`, preserves the observed
state, rolls back from frozen preimages and stops without retarget or retry.
This DESIGN neither adopts the target nor authorizes a network, Core, root,
pin, binding, fixture-repair, commit or push effect.

## 2. Preserved facts and boundaries

- Hidden Core is clean at the old full pin; existing local
  `origin/main` is the frozen target. Local ancestry is `0` ahead / `6`
  behind. The cumulative delta is `256` paths, `173` outside the accepted
  Markdown/docs-only class; it is not downstream product adoption.
- The prior `d786013...` attempt and its independent
  `REVIEW_PASS_FAILURE_ROLLED_BACK` are immutable. It failed honestly at
  `DOWNSTREAM_SYNCHRONIZATION:P3` because a disposable positive used literal
  `"x"` in six `^[0-9a-f]{64}$` fields: the repository matcher rejected it
  while a lenient secondary validator accepted it. Rollback restored the old
  Core, `17/17` roots, `2/2` pins, `9/9` shared carriers and `1/1` binding.
- The separate fixture-repair lineage remains open at
  `AUTHORIZATION_REREVIEW_CHANGES_REQUIRED` (`AR-F1`); its source harness has
  valid retained bounded evidence, but mandatory focused verification still
  has the reviewed F1/F2 test-plumbing failures. This tranche may read and
  execute exact frozen bytes as a P0 safety input, but may not edit them,
  close that tranche, suppress its failures or claim its full suite passes.
- The rejected protocol-exception DESIGN remains immutable with findings
  `DR-F1..DR-F4`. No exception is activated or needed: this design accounts
  for the doctor's real fetch/ref effect inside later explicit authority.
- P4-E remains parked at `DESIGN_REVIEW_PASS`; XR1 historical-object debt is
  unchanged. The protected operator assessment is excluded from open, read,
  hash, inventory, stage and use. Broad downstream untracked inventory is
  forbidden.

## 3. Frozen tool and policy identities

SPEC and Work Order must recompute and bind these exact identities before any
external effect:

| Surface | SHA-256 / Git object |
|---|---|
| Core reconciler raw / blob | `96ac0cce3bf9df5733ffe2c6f5a7850db0ccfdc4403daaa70fdb6981dc58196c` / `4b705c6bf7b10bda62520dca488ecb453a4f4945` |
| Core doctor raw / blob | `2410bbabf88f12581d2e34a71efe247fe9080ebb299a58eb6f9ff6a35818796b` / `2ad83efee05c738fec40aa1779929da07f3d1c8c` |
| Core new-workspace raw / blob | `7e5567c55026f3be44f11c924d44835d6fb98b1fb4268dfedf6453af89927032` / `5f311a1a1c8dc787c7b19011bf34c5a84fc773c7` |
| Core `governance/toolkit/05_OPERATION` tree | `23fe8bd39ae102d3302d34de1d80208e2ef9bbb6` |
| Downstream initializer raw | `bb37b16256a693853bddfdbcb40c2f7211e6984a90a972da83899962fae209c8` |
| Active rule-pack selector raw | `f51bacd206ec4e95b92f4f4479bc7c68ee605db3752d514ff3094bdff02dc855` |

The three Core script blobs and operation tree are identical at old pin and
target. Any byte/object/profile drift is `TOOL_OR_EFFECT_DRIFT` and requires a
fresh governed target decision, not an in-attempt amendment.

## 4. Collision-free attempt-3 evidence lifecycle

All six paths below are currently absent and must be proved absent and safely
contained again at BUILD preflight:

1. `D:\UNG DUNG AI\TOOL AI 2026\CVF-Workspace\_cvf-core-backups\CVF-CORE-REFRESH-TARGET-REBASE-0281E93-ATTEMPT-3-EVIDENCE`;
2. `docs/decisions/CVF_CORE_REFRESH_ROOT_EFFECTS_2026-08-30_0281E93_ATTEMPT_3.json`;
3. `docs/decisions/CVF_CORE_REFRESH_WORKER_RETURN_2026-08-30_0281E93_ATTEMPT_3.md`;
4. `docs/decisions/CVF_CORE_REFRESH_COMPLETION_REVIEW_2026-08-30_0281E93_ATTEMPT_3.md`;
5. `docs/decisions/CVF_CORE_REFRESH_REVIEW_TARGET_MOVEMENT_ROLLBACK_2026-08-30_0281E93_ATTEMPT_3.json`; and
6. `docs/decisions/CVF_CORE_REFRESH_REVIEW_TARGET_MOVEMENT_REREVIEW_2026-08-30_0281E93_ATTEMPT_3.md`.

Attempt-1, attempt-2, fixture-repair and protocol-exception artifacts and
contained failed states are immutable. The worker JSON is the semantic
receipt and worker Markdown is a summary; neither self-hashes nor cross-hashes.
The completion review owns their final hashes and does not self-hash. A
conditional rollback JSON does not self-hash; its terminal rereview owns all
readable prior attempt-3 hashes and does not depend on a future artifact.

## 5. P0 preflight and the fixture-state rule

Before the evidence directory, network, Core move, root write, pin edit or
binding write, the worker must prove:

1. exact resolved workspace/project/Core/backup containers with no reparse
   escape; expected public remote; clean old Core and exact old pins/binding;
2. local availability of old and target objects, exact `0/6` ancestry and
   local `origin/main == 0281e93...` without fetching;
3. all accepted phase, tool, profile, policy and future matrix/pin hashes;
   downstream staged-zero; all six attempt-3 paths absent;
4. recoverable preimages for old Core, the exact 17 roots, two pins, nine
   shared carriers and ignored binding, including `PRESENT`/`ABSENT` state;
5. exact preservation hashes for the three P4-E checkpoint artifacts and all
   allowlisted prior governance/evidence artifacts; and
6. strict P0 conformance before external effect.

Strict P0 conformance must use the repository matcher and the independently
implemented strict functions already present in the exact-hash fixture
harness. It must synthesize lower-case 64-hex witnesses, reject the retained
six-field `"x"` regression on both surfaces, require exclusive positive
matching, exact generator/oracle id equality, complete one-fact mutation
rejection and the focused temporal cross-product. The future Work Order must
pin the exact command bytes and all imported source hashes and must recompute
counts instead of copying `686` or `894` from history.

The current `cvf_core_refresh_conformance.py` top-level runner is bound to the
fixture-repair family and hard-coded count; it must not be repointed to the
attempt-3 family or edited here. SPEC must define a read-only target-family P0
adapter that calls its generic synthesis/strict-validation functions and the
repository generator/oracle under pinned hashes. No output may be accepted as
PASS unless both strict surfaces agree against matrix-owned expectations.

This use is evidence consumption, not fixture repair. The two reviewed
fixture-test defects, open authorization status and known focused-suite
baseline remain recorded. If any current fixture byte changes before BUILD,
or P0 cannot run without a repair, the attempt selects zero-effect refusal;
the target-rebase worker cannot fix it.

## 6. Ordered BUILD command graph and network accounting

After a passed P0 and complete preservation, the only initial graph is:

1. invoke the old Core's sanctioned
   `update_cvf_workspace_public_core.ps1 -WorkspaceRoot <exact-workspace>`
   exactly once;
2. immediately record transcript, exit, backup/replacement paths, root effects,
   Core remote, cleanliness, HEAD and `origin/main`; continue only when
   `HEAD == origin/main == 0281e93...`;
3. replace exactly one old full pin in `.cvf/manifest.json.cvfCoreCommit` and
   exactly one old full pin in the generated `AGENTS.md` header, then parse
   both back to the target; and
4. invoke downstream `scripts/initialize_cvf_clone.ps1` exactly once.

The successful graph contains three ordered Git network operations: reconciler
clone, initializer fetch and initializer-doctor fetch. The doctor fetch can
move `origin/main`; therefore initializer success is insufficient unless its
post-doctor checkpoint proves clean five-way equality across Core HEAD, Core
`origin/main`, manifest, AGENTS and binding at the frozen target. An executed
failure records only its actual prefix.

No manual fetch, direct checkout, custom clone, overlay,
`-UpdateProjectManifests`, pending-backup override, separate worker doctor,
alternate remote, credential helper, retry or in-attempt target rebase is
allowed.

## 7. Root, downstream and binding effects

The reconciler root ceiling is exactly the following ordered 17 paths:

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

Every path receives exactly one `CREATE`, `UPDATE`, `DELETE` or `NO_CHANGE`
observation; success and complete rollback require `17/17`. Originally absent
targets return to absence during rollback; backups, failed replacements and
failed-root deltas remain retained.

The initial worker's tracked downstream ceiling is exactly two pin carriers,
nine shared carriers and two worker artifacts:

```text
.cvf/manifest.json
AGENTS.md
knowledge/manifest.json
IMPLEMENTATION_STATUS.json
SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json
SESSION/ACTIVE_SESSION_STATE.json
CVF_SESSION/ACTIVE_SESSION_STATE.json
SESSION/SESSION_MEMORY.md
SESSION/handoffs/CVF_CORE_REFRESH_TARGET_REBASE_0281E93_2026-08-30.md
docs/INDEX.md
docs/implementation/EXECUTION_ROADMAP.md
docs/decisions/CVF_CORE_REFRESH_ROOT_EFFECTS_2026-08-30_0281E93_ATTEMPT_3.json
docs/decisions/CVF_CORE_REFRESH_WORKER_RETURN_2026-08-30_0281E93_ATTEMPT_3.md
```

Ignored `.cvf/local-binding.json` is the sole additional local effect. All
other downstream paths are byte-protected during BUILD, including fixture
source/tests/matrix/pin/receipts, protocol-exception artifacts, P4-E artifacts,
product/runtime/database/catalog files and accepted phase/review documents.

## 8. Rollback and reviewer target movement

Every post-start failure first contains and preserves the observed failure,
then restores old Core, all 17 roots, two pins, nine shared carriers and the
binding from frozen preimages. It runs at most one exact rollback-verifier
doctor, records that doctor's fetch and before/after remote ref, writes honest
failure evidence and stops. Complete and incomplete rollback are disjoint;
an incomplete restore cannot fabricate Core/pin hashes, staged-zero, P4-E
preservation or unreadable evidence hashes.

A distinct completion reviewer may run at most one exact doctor in REVIEW.
The reviewer records its command/script hash, network window, exit code and
target before/after. If that fetch moves `origin/main` away from `0281e93...`,
the reviewer writes immutable `REVIEW_TARGET_MOVEMENT` and stops; it does not
repair or retarget. A distinct `REPAIR_WORKER` may then perform rollback only
from BUILD preimages, create only the conditional rollback JSON, and never run
the reconciler. A distinct rereviewer owns the terminal review. Failed
replacement and movement evidence remain preserved in every outcome.

## 9. Roles and phase gates

- `ORCHESTRATOR` records transitions and authority; it does not implement or
  self-approve.
- `SPEC_AUTHOR` owns the exact requirements, successor matrix, registry entry
  and one-way digest pin.
- `WORK_ORDER_AUTHOR` owns exact commands, paths, hashes and stop rules; its
  document grants no external effect.
- `INDEPENDENT_AUTHORIZATION_REVIEWER` recomputes the Work Order and records
  findings/waivers. PASS still leaves BUILD authority `NOT_GRANTED`.
- Only after explicit recorded external-effect approval may a distinct
  `IMPLEMENTATION_WORKER` own P0, preservation, initial execution, worker-time
  rollback and the two worker artifacts.
- `INDEPENDENT_COMPLETION_REVIEWER`, conditional `REPAIR_WORKER`, and
  `INDEPENDENT_COMPLETION_REREVIEWER` are distinct non-overlapping roles.
- `CLOSER/SESSION_SYNC_STEWARD` acts only after an accepted terminal review.
  `COMMIT_STEWARD` remains inactive without separate authority.

DESIGN review PASS is required before SPEC; SPEC review PASS before Work Order;
authorization review PASS and explicit external-effect approval before BUILD;
independent terminal review before FREEZE. No review disposition silently
grants the next phase.

## 10. Invariant-family applicability

Applicability is `TRIGGERED`: attempt 3 has shared receipts over multiple
outcomes, outcome-controlled fields, exact counters/temporal relations,
multiple validator surfaces and an adjacent conformance failure. Before SPEC
review, register a successor such as
`CVF-CORE-REFRESH-TARGET-REBASE-0281E93-OUTCOMES-2026-08-30`, with its own
matrix path, canonical digest and static machine pin. Use
`docs/templates/INVARIANT_FAMILY_PROOF.md` in the Work Order and reviews.

The new matrix is the sole owner of attempt-3 outcome fields, relations,
counter rules, doctor before/after observations and evidence lifecycle. This
DESIGN intentionally does not copy those rules. The `d786013...` target matrix,
fixture-repair matrix and their pins remain immutable inputs, not semantic
owners for attempt 3.

## 11. Verification and closure semantics

Worker and reviewer must run applicable JSON parsing, session/mirror, Project
Knowledge, invariant-family, target-family strict P0, catalog, file-size,
scoped tracked-diff and staged-zero guards. Evidence records exact command,
working directory, ordering, exit and retained output. A failed target-family
gate cannot be waived into success.

The fixture-repair focused-suite failures are a separately reviewed inherited
baseline, not a target-rebase success. They must be reported unchanged and
must not be hidden by a broad “all tests pass” claim. If the controlling FREEZE
rule requires their closure, a successful target adoption stops at
`BUILD_SUCCESS_FREEZE_BLOCKED_BY_PARKED_FIXTURE_REPAIR` and routes the already
governed fixture lineage for fresh authorization after Core freshness; this
tranche may not repair it. Only an accepted success or accepted complete
rollback with no missing required artifact may close bounded; incomplete
rollback remains open failure.

## 12. Stop conditions and bounded claim

Stop on target, remote, ancestry, phase, tool, policy, profile, matrix, pin or
fixture-byte drift; containment/preimage failure; evidence collision; strict
surface disagreement; unexpected path/command/network effect; credential need;
protected-state contact; fixture repair need; role overlap; failed restore; or
need for product/runtime/database, installation, deployment, release, commit
or push effects. No stop condition grants wider authority, retargeting or
retry.

A later successful closure may prove only deterministic public-Core freshness
and pin reconciliation to exact `0281e93...` inside the enumerated boundary.
It does not prove CVF controls AI/agent behavior, provider behavior, downstream
runtime adoption of the 256-path Core delta, arbitrary-untracked absence,
fixture-repair closure, P4-E implementation, database behavior, deployment or
production readiness. No provider or mock output is governance proof here.

## 13. DESIGN acceptance and next move

Independent review must verify target/tool freezing, real doctor network/ref
accounting, strict P0 treatment of the prior failure, fixture-state non-repair,
collision-free attempt-3 ownership, exact root/downstream/binding ceilings,
rollback and reviewer-movement handling, roles, phase gates, invariant-family
trigger, P4-E/protected preservation, stop rules and bounded claim. Findings
and waivers must be explicit.

Next governed move: independent DESIGN review only. SPEC, Work Order, BUILD,
doctor/fetch/reconcile, Core/root/pin/binding mutation, fixture repair,
provider/credential use, installation, product/database change, deployment,
commit, push and P4-E SPEC remain unauthorized. BUILD external-effect authority
remains `NOT_GRANTED` until an exact Work Order passes independent review and
the later authority is explicitly recorded.
