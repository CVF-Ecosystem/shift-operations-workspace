# SPEC — CVF Public-Core Exact-Target Rebase 0281e93

- Tranche: `CVF-CORE-REFRESH-TARGET-REBASE-0281E93-2026-08-30`
- Phase: `SPEC`
- Risk: `R2`
- Status: `READY_FOR_INDEPENDENT_SPEC_REREVIEW_AFTER_F1_REPAIR`
- Active role: `REPAIR_WORKER`
- Old Core/pin: `a7a797d7111be472ef2cbd928cbeffc70ccb6bc6`
- Frozen target: `0281e93bab4a75083973eb7242fd2bc8f65055d3`
- Invariant family:
  `CVF-CORE-REFRESH-TARGET-REBASE-0281E93-OUTCOMES-2026-08-30`
- Matrix canonical digest:
  `e39de7e9ed3199ec8f9033b1c90af9eca993655470f675a0ed3ae93846dbe45c`
- BUILD external-effect authority: `NOT_GRANTED`

## R1 — Accepted phase lineage and immutable target

Only these accepted bytes authorize this SPEC:

| Artifact | SHA-256 |
|---|---|
| `docs/decisions/INTAKE_2026-08-30_CVF_CORE_REFRESH_TARGET_REBASE_0281E93.md` | `28e1160993d2638554bdb810dd36f393eebb65db62b47b8f92b8049fc290ba53` |
| `docs/decisions/INTAKE_REVIEW_2026-08-30_CVF_CORE_REFRESH_TARGET_REBASE_0281E93.md` | `4c754b7cc47ef247453075e0633848534d121959aba7fb845d49f12975da1b8c` |
| `docs/decisions/DESIGN_2026-08-30_CVF_CORE_REFRESH_TARGET_REBASE_0281E93.md` | `1fc8c00dd19bfd08a4b185f1fdc41fbe58991a7006248a593a5fc6fc371cb8b5` |
| `docs/decisions/DESIGN_REVIEW_2026-08-30_CVF_CORE_REFRESH_TARGET_REBASE_0281E93.md` | `78eaf8c9e7e01af721c877ed6aaa89b6446baea40e3ef05df85f8772d1088c56` |

The only public remote is
`https://github.com/Blackbird081/Controlled-Vibe-Framework-CVF.git`. The old
pin and target are the full hashes above. Before every later network boundary,
the worker or reviewer must compare the applicable advertised/local target to
the frozen target. Any other target selects fail-closed target drift; no role
may retarget, retry or amend this tranche in place.

## R2 — Exact tools, profile and fixture-state inputs

A Work Order must recompute these identities before granting any effect:

| Surface | Required identity |
|---|---|
| Core reconciler raw / Git blob | `96ac0cce3bf9df5733ffe2c6f5a7850db0ccfdc4403daaa70fdb6981dc58196c` / `4b705c6bf7b10bda62520dca488ecb453a4f4945` |
| Core doctor raw / Git blob | `2410bbabf88f12581d2e34a71efe247fe9080ebb299a58eb6f9ff6a35818796b` / `2ad83efee05c738fec40aa1779929da07f3d1c8c` |
| Core new-workspace raw / Git blob | `7e5567c55026f3be44f11c924d44835d6fb98b1fb4268dfedf6453af89927032` / `5f311a1a1c8dc787c7b19011bf34c5a84fc773c7` |
| Core `governance/toolkit/05_OPERATION` tree | `23fe8bd39ae102d3302d34de1d80208e2ef9bbb6` |
| Downstream initializer raw | `bb37b16256a693853bddfdbcb40c2f7211e6984a90a972da83899962fae209c8` |
| Active rule-pack selector raw | `f51bacd206ec4e95b92f4f4479bc7c68ee605db3752d514ff3094bdff02dc855` |

The Core script blobs and operation tree must be identical at old pin and
target. Drift is `TOOL_OR_EFFECT_DRIFT`, not repair authority.

The read-only P0 adapter imports only these frozen sources:

| Source | SHA-256 |
|---|---|
| `scripts/invariant_family_contract.py` | `19616ecaf9bbdb35738a1622fa790c7f0c0e24d5afdbbae154d402528aa78497` |
| `scripts/invariant_family_mutation_generator.py` | `d5f2e13328874dc41946fe73334f8c34eb55619db3b101781869d448b54a82ae` |
| `scripts/invariant_family_ownership.py` | `71ec4c547d72c9e4d3d6a8951aaf889f78e8459849106f143beb6298b523aac7` |
| `scripts/invariant_family_mutation_oracle.py` | `f9bf70a8c2adee0097c9faed7e1b2f0e554aa1fa3d6021a0ed346275de0f6cdc` |
| `scripts/cvf_core_refresh_conformance.py` | `cae96b6eef4ab9d5bd4e0a8a58c02d05c04591d68b835a1be356f140c5a4adb9` |
| `tests/unit/test_invariant_family_pattern_mutations.py` | `49dba6d885c054170fd2a48905e5ee0ebdd33b9dcb7a507b74d6c5af8b0f14a7` |
| `tests/integration/test_invariant_family_repository_guard.py` | `44cdf8451cef01bfe58239563afe3aaf162b92906812c2c5725a3925e39079e6` |

The last two are parked fixture-state preimages, not an edit scope. If any
listed byte changes, or P0 requires repair, execution selects zero-effect
refusal.

## R3 — Read-only P0 adapter contract

The adapter identity is
`CVF_CORE_REFRESH_TARGET_REBASE_0281E93_READ_ONLY_P0_ADAPTER_V1`. The Work
Order must pin the exact inline command bytes and working directory. The
adapter may read only the matrix, registry, digest pin and R2 sources; import
the generic synthesis and strict-validation functions from the frozen harness;
and import the repository matcher, generator and independent oracle. It must
not call the fixture-specific top-level `run`, whose family id and counts are
intentionally hard-coded to the parked fixture-repair family.

The adapter performs entirely in memory and emits one canonical JSON object to
stdout. It creates no directory or file, performs no network/provider/
credential/database action, and does not mutate Core, workspace root,
downstream state or fixtures. A wrapper may hold stdout in memory until the
authorized evidence lifecycle begins; it must not redirect P0 output into a
preflight-created file.

PASS requires all of the following against the matrix digest in the header:

- exactly `8/8` synthesized positives, each matching only its own shape on
  both repository and independent strict validators;
- exactly `1257/1257` unique generated/oracle mutation ids, with exact-set
  equality and both validators rejecting every mutation;
- the complete operator corpus: required deletion, forbidden insertion,
  unknown field, discriminator replacement, wrong type, const mismatch, enum
  mismatch, counter mutation, pattern mismatch and one-sided relation change;
- exactly `40/40` correct temporal cross-product judgments (`38` accepted,
  `2` rejected) over initial failure-stage/network-prefix and incomplete-
  rollback-stage/verifier pair domains; and
- exactly six lower-case 64-hex positive witnesses, with literal `"x"`
  rejected for each field on both validator surfaces.

The eight-outcome count is intentional. The new target has a distinct
`BUILD_SUCCESS_FREEZE_BLOCKED_BY_PARKED_FIXTURE_REPAIR` state, so BUILD success
cannot be conflated with FREEZE eligibility. The matrix-owned operational
predicate `fixture_freeze_gate_status` must equal `fixture_repair_status` in
both BUILD-success shapes. `SUCCESS_VALID` requires both fields to be
`AUTHORIZATION_REREVIEW_PASS`; the freeze-blocked shape requires both to be
`AUTHORIZATION_REREVIEW_CHANGES_REQUIRED`. Therefore the currently parked
authorization status selects only the freeze-blocked outcome, while the
eligible success outcome remains available only after a separately accepted
fixture authorization rereview.

## R4 — Zero-effect preflight

Before evidence-directory creation or any external effect, prove exact
contained workspace/project/Core/backup paths with no reparse escape; expected
remote; clean old Core and exact old pins/binding; local old/target objects;
local `origin/main ==` target and exact `0/6` ancestry without fetching;
accepted phase, policy, profile, tool, matrix, pin and P0-source hashes;
downstream staged-zero; all six future paths absent; recoverable
`PRESENT`/`ABSENT` preimages; exact P4-E and allowlisted prior-evidence hashes;
and R3 PASS.

The protected operator assessment is excluded from open, read, hash,
inventory, stage and use. Broad downstream untracked inventory is forbidden.
Any false, unreadable or changed predicate selects the matrix-owned
zero-effect refusal and permits no attempt-3 artifact creation.

## R5 — Collision-free six-path evidence lifecycle

The complete attempt-3 lifecycle is:

1. `D:\UNG DUNG AI\TOOL AI 2026\CVF-Workspace\_cvf-core-backups\CVF-CORE-REFRESH-TARGET-REBASE-0281E93-ATTEMPT-3-EVIDENCE`;
2. `docs/decisions/CVF_CORE_REFRESH_ROOT_EFFECTS_2026-08-30_0281E93_ATTEMPT_3.json`;
3. `docs/decisions/CVF_CORE_REFRESH_WORKER_RETURN_2026-08-30_0281E93_ATTEMPT_3.md`;
4. `docs/decisions/CVF_CORE_REFRESH_COMPLETION_REVIEW_2026-08-30_0281E93_ATTEMPT_3.md`;
5. `docs/decisions/CVF_CORE_REFRESH_REVIEW_TARGET_MOVEMENT_ROLLBACK_2026-08-30_0281E93_ATTEMPT_3.json`; and
6. `docs/decisions/CVF_CORE_REFRESH_REVIEW_TARGET_MOVEMENT_REREVIEW_2026-08-30_0281E93_ATTEMPT_3.md`.

All must initially be absent, resolve inside their accepted containers and
remain collision-free. Prior attempts, fixture repair, protocol exception and
their contained failures are immutable. The root-effects JSON is the worker's
semantic receipt and the worker Markdown is a summary; neither self-hashes nor
cross-hashes. Completion review owns their final hashes and does not self-hash.
Conditional rollback JSON does not self-hash. Terminal rereview owns all
readable prior attempt-3 hashes and never depends on a future artifact.

## R6 — Sanctioned command and network graph

After R4 PASS and complete preservation, the initial worker may execute only:

1. old Core `scripts/update_cvf_workspace_public_core.ps1 -WorkspaceRoot
   <exact-workspace>` exactly once;
2. an immediate no-network checkpoint recording transcript, exit, backup and
   replacement paths, root effects, remote, cleanliness, HEAD and
   `origin/main`, continuing only on exact target equality;
3. exactly one old-full-pin replacement in
   `.cvf/manifest.json.cvfCoreCommit` and one in the generated `AGENTS.md`
   header, both parsed back to target; then
4. downstream `scripts/initialize_cvf_clone.ps1` exactly once.

The successful worker graph has exactly three ordered Git network operations:
reconciler clone, initializer fetch, initializer-doctor fetch. The initializer
doctor is a real fetch/ref effect. Success requires exit zero and post-doctor
five-way equality across Core HEAD, Core `origin/main`, manifest, AGENTS and
binding. A failure records only its actual prefix.

No manual fetch, direct checkout, custom clone, overlay,
`-UpdateProjectManifests`, pending-backup override, separate worker doctor,
alternate remote, credential helper, retry or in-attempt target rebase is
allowed.

## R7 — Exact effect ceilings

The reconciler workspace-root ceiling is the ordered set below; every target
must have one `CREATE`, `UPDATE`, `DELETE` or `NO_CHANGE` observation. Success
and complete rollback require `17/17`.

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

The initial-worker tracked downstream ceiling is exactly 13 paths: two pin
carriers, nine shared carriers and two worker artifacts.

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

Ignored `.cvf/local-binding.json` is the sole additional local effect. Every
other downstream path is byte-protected, including this SPEC/matrix/pin,
accepted phase/review artifacts, fixture/protocol/P4-E artifacts, catalog,
product/runtime and database files. Originally absent root targets return to
absence on rollback; backups, failed replacements and failed-root deltas stay
retained.

## R8 — Terminal outcome ownership

The registered matrix is the only semantic owner of exact required,
forbidden and conditional fields; domains; counters and relations; failure-
stage/prefix pairs; rollback-stage/verifier pairs; hashes; and lifecycle rules.
Its closed outcome ids are:

1. `ZERO_EFFECT_PREFLIGHT_REFUSAL`;
2. `SUCCESS`;
3. `BUILD_SUCCESS_FREEZE_BLOCKED_BY_PARKED_FIXTURE_REPAIR`;
4. `FAILURE_ROLLED_BACK`;
5. `FAILURE_ROLLBACK_INCOMPLETE`;
6. `REVIEW_TARGET_MOVEMENT`;
7. `REVIEW_TARGET_MOVEMENT_ROLLED_BACK`; and
8. `REVIEW_TARGET_MOVEMENT_ROLLBACK_INCOMPLETE`.

This list identifies the closed grammar; it does not duplicate matrix field
rules. Adapters, fixtures, receipts and the Work Order must consume the matrix
by family id and canonical digest, never independently restate those rules.
For the two BUILD-success outcomes, the matrix alone owns the exact fixture
gate field, its status domain and equality relation. A consumer must derive
the outcome from the observed authorization-rereview status; it may not select
FREEZE eligibility by correlated relabeling of outcome/disposition fields.
`REVIEW_TARGET_MOVEMENT` closes only the first reviewer window and routes
conditional repair. Incomplete rollback remains open failure. Only an accepted
success or accepted complete rollback can route toward bounded FREEZE, and the
parked fixture rule may still select the distinct freeze-blocked outcome.

## R9 — Rollback and reviewer target movement

Every post-start worker failure first contains and preserves the observed
failure, then restores old Core, 17 roots, two pins, nine shared carriers and
binding from frozen preimages. It may run at most one exact rollback-verifier
doctor, recording that doctor's network/ref before and after state. Complete
and incomplete rollback are disjoint; incomplete restore must use observation
states and never fabricate unavailable hashes, staged-zero, P4-E preservation
or success counters.

A distinct completion reviewer may invoke at most one exact authorized doctor.
It records command/script identity, network window, exit and target before/
after. Movement away from the frozen target creates immutable
`REVIEW_TARGET_MOVEMENT` and stops without repair or retarget. A distinct
rollback-only `REPAIR_WORKER` may restore from BUILD preimages and create only
the conditional rollback JSON; it never invokes the reconciler. A distinct
terminal rereviewer owns the final Markdown and readable evidence hashes.

The conditional repair ceiling is 11 tracked pin/shared carriers plus one
conditional JSON create, at most 12 tracked paths, plus the ignored binding.
Worker artifacts and completion review stay immutable.

## R10 — Temporal ownership and role gates

Role windows do not overlap:

- `ORCHESTRATOR` records phase/authority transitions and routes roles;
- `SPEC_AUTHOR` owns only this SPEC, matrix, registry entry and pin;
- `WORK_ORDER_AUTHOR` translates an accepted SPEC into exact commands, paths,
  hashes, evidence and stop conditions but grants no external effect;
- `INDEPENDENT_AUTHORIZATION_REVIEWER` recomputes the Work Order; PASS alone
  leaves BUILD authority ungranted;
- only explicit recorded external-effect approval activates a distinct
  `IMPLEMENTATION_WORKER` for P0, preservation, initial execution, worker-time
  rollback and two worker artifacts;
- `INDEPENDENT_COMPLETION_REVIEWER`, conditional `REPAIR_WORKER` and
  `INDEPENDENT_COMPLETION_REREVIEWER` are distinct roles; and
- `CLOSER/SESSION_SYNC_STEWARD` acts only after accepted terminal review;
  `COMMIT_STEWARD` requires separate authority.

Required gates are DESIGN review PASS before SPEC, SPEC review PASS before
Work Order, authorization review PASS plus explicit external-effect approval
before BUILD, independent terminal review before FREEZE, and explicit closure
before commit. No review disposition silently grants the next phase.

## R11 — Fixture, P4-E and protected-state boundaries

Fixture repair remains parked at
`AUTHORIZATION_REREVIEW_CHANGES_REQUIRED`; this tranche may consume its exact
frozen generic functions but may not edit its source/tests/matrix/pin/receipts,
claim its focused suite passes, close its findings or suppress its baseline.
The matrix-owned FREEZE rule is exact: the observed fixture authorization-
rereview status is copied into `fixture_freeze_gate_status`; equality is
mandatory. `AUTHORIZATION_REREVIEW_CHANGES_REQUIRED` selects
`BUILD_SUCCESS_FREEZE_BLOCKED_BY_PARKED_FIXTURE_REPAIR` after successful BUILD,
and only a separately accepted `AUTHORIZATION_REREVIEW_PASS` permits
`SUCCESS`. Fixture byte drift still selects zero-effect refusal before BUILD.
Route fixture repair separately; do not repair it here.

P4-E stays exactly `DESIGN_REVIEW_PASS`; its three checkpoint artifacts must
remain byte-identical. XR1 historical-object debt remains unresolved. The
protected operator assessment receives exactly zero contacts across every
matrix outcome. No tranche outcome authorizes P4-E SPEC/BUILD, XR1 repair,
fixture repair, product/runtime/database work or broad untracked inventory.

## R12 — Invariant family, digest and verification

Applicability is `TRIGGERED`: shared receipts span terminal outcomes;
outcome-controlled presence and exact counter/temporal relations exist;
repository and independent validators share one contract; and the prior
literal-`"x"` finding exposed an adjacent invariant member.

The sole matrix is
`docs/cvf/invariants/cvf-core-refresh-target-rebase-0281e93-outcomes-2026-08-30.json`;
its canonical digest is the header digest. The one-way machine consumer is
`docs/specs/cvf_core_refresh_target_rebase_0281e93_2026_08_30_invariant_pin.py`.
Matrix and pin do not bind this SPEC and create no self/cross-hash cycle. The
predecessor target-rebase and fixture matrices remain immutable inputs, not
semantic owners for attempt 3.

Work Order and every independent review must complete
`docs/templates/INVARIANT_FAMILY_PROOF.md`, recompute the canonical digest,
run the full R3 corpus, sample one raw positive per outcome and verify the
matrix expectations predate BUILD. Required local deterministic gates include:

```text
python scripts/check_invariant_families.py --json
python -m pytest -q tests/unit/test_invariant_family_contract.py tests/integration/test_invariant_family_repository_guard.py
```

The exact target-family P0 command is additional and must be pinned in the
Work Order. Counts must be recomputed, not trusted from this prose.

The bounded `SPEC-REV-F1` repair is reconstructable from the accepted review
at SHA-256
`02a3e81791f42272a488a4a008f93b21ec2561c6cf0e9d9cfa1af97ef7a380b2`:
only the two BUILD-success shapes gained the required
`fixture_freeze_gate_status` field and one equality relation each; the eligible
shape's `fixture_repair_status` changed from the parked status to
`AUTHORIZATION_REREVIEW_PASS`. The full corpus consequently changes from
`1249` to `1257`: `SUCCESS_VALID` `156 -> 160` and the freeze-blocked shape
`161 -> 165`; all six other shape counts are unchanged. The operator delta is
exactly required deletion `+2`, wrong type `+2`, const mismatch `+2` and one-
sided relation change `+2`. No target, command, path, network, effect,
rollback, evidence, role or claim boundary changed.

## R13 — Final deterministic gates and evidence

Worker and reviewer run applicable JSON parsing, session/mirror, Project
Knowledge, invariant-family, target P0, catalog, file-size, scoped tracked-diff
and staged-zero guards. Evidence records exact commands, working directories,
ordering, exits and retained output. Completion review independently checks
the 17-root and role-specific downstream ceilings, preimages, target/pins,
hash ownership, network counts, fixture/P4-E/protected preservation and every
prohibited effect. A failed target-family gate cannot be waived into success.

The inherited fixture focused-test failures must be disclosed separately; no
result may be summarized as unrestricted “all tests pass.”

## R14 — Stop conditions and bounded claim

Stop on target, remote, ancestry, phase, policy, role, tool, profile, matrix,
pin, P0-source or fixture drift; collision/containment/preimage failure;
strict-surface or oracle disagreement; unexpected command/path/network effect;
credential need; protected-state contact; fixture repair need; failed restore;
or need for product/runtime/database, installation, deployment, release,
commit or push effects. Stop never grants retry, retarget or wider authority.

A later accepted closure may prove only deterministic public-Core freshness
and pin reconciliation to exact `0281e93...` inside the enumerated boundary.
It does not prove CVF controls AI/agent behavior, provider behavior, arbitrary-
untracked absence, downstream adoption of the 256-path Core delta, fixture
repair closure, P4-E implementation, XR1 repair, database behavior, deployment
or production readiness. No provider or mock output is governance proof here.

## Acceptance criteria

- `AC1`: R1-R4 pass before any external effect; otherwise only zero-effect
  refusal is valid.
- `AC2`: the worker remains inside R5-R7 and selects exactly one matrix shape.
- `AC3`: rollback and reviewer movement obey R8-R10 with immutable evidence
  and honest incomplete-state observations.
- `AC4`: fixture, P4-E, XR1 and protected-state boundaries in R11 hold for
  every outcome.
- `AC5`: registry ownership, digest pin, `8/8`, the full generated/oracle
  mutation corpus with exact-set equality, correlated BUILD-success outcome
  selection, `40/40` temporal judgments and all
  six SHA-pattern probes are independently recomputed under R12-R13.
- `AC6`: R14 remains true; no claim or authority expands because a gate passes.

## Next governed move

Independent SPEC review only. Work Order, BUILD, reconciler, doctor/fetch,
Core/workspace-root/pin/binding mutation, fixture repair, provider/credential
use, installation, product/database change, deployment, commit, push and P4-E
SPEC remain unauthorized. Even after SPEC review, BUILD remains locked until
an exact Work Order passes independent authorization review and explicit
external-effect authority is recorded.
