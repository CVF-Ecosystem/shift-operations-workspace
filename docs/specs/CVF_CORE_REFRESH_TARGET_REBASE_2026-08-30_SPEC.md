# SPEC — CVF Public-Core Refresh Target Rebase

- Tranche: `CVF-CORE-REFRESH-TARGET-REBASE-2026-08-30`
- Phase: `SPEC`
- Risk: `R2`
- Status: `READY_FOR_INDEPENDENT_SPEC_REREVIEW`
- Active role: `REPAIR_WORKER`
- Old Core/pin:
  `a7a797d7111be472ef2cbd928cbeffc70ccb6bc6`
- Frozen target:
  `d7860138350130d6d105826ce186f1beeaba3c2d`
- Invariant family:
  `CVF-CORE-REFRESH-TARGET-REBASE-OUTCOMES-2026-08-30`
- Matrix canonical digest:
  `dc0c35298fb584d995f51ed8cf996f599f12b934617afd51e1a27b24ce47f4cc`

## R1 — Accepted phase chain and fixed target

The only accepted phase lineage is:

| Artifact | Raw/canonical SHA-256 |
|---|---|
| `docs/decisions/INTAKE_2026-08-30_CVF_CORE_REFRESH_TARGET_REBASE.md` | `f4efd86c242132082949432f7c44e0f1304599826b0e823fdff3abd39cf77294` |
| `docs/decisions/INTAKE_REVIEW_2026-08-30_CVF_CORE_REFRESH_TARGET_REBASE.md` | `fc381ad4485a57760b029c9072cdd3aee93333b0dd6c9d026cbc1e13625df865` |
| `docs/decisions/DESIGN_2026-08-30_CVF_CORE_REFRESH_TARGET_REBASE.md` | `90313677f0efffcc2e5dd78b6e1efb95e2e919c1494adc9c9274128ec0865f73` |
| `docs/decisions/DESIGN_REVIEW_2026-08-30_CVF_CORE_REFRESH_TARGET_REBASE.md` | `0fb6841c68093800e265784768e0feb38ccf188ad1b518d6a8bf750ed6e40bdc` |

The only public remote is
`https://github.com/Blackbird081/Controlled-Vibe-Framework-CVF.git`. The old
Core/pin and frozen target are the full hashes in the header. Any different
remote, ancestry, advertised tip, cloned target or review-time public tip is
fail-closed. No BUILD attempt may adopt or rebase to another target.

## R2 — Exact accepted tool and profile bindings

Before external effect, a later Work Order must recompute and require all of
these accepted bindings:

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

Old-to-target Git objects for the three Core scripts and the operation tree
must remain equal. Any mismatch requires a fresh governed target rebase; it is
not repair inside this tranche.

## R3 — Sanctioned command graph

The initial worker may use only the accepted bootstrap-native graph:

1. the old Core's
   `scripts/update_cvf_workspace_public_core.ps1 -WorkspaceRoot <workspace>`
   exactly once;
2. only after its immediate frozen-target checkpoint passes, replace exactly
   one old full pin in `.cvf/manifest.json.cvfCoreCommit` and exactly one old
   full pin in the generated `AGENTS.md` `CVF Commit` header; and
3. downstream `scripts/initialize_cvf_clone.ps1` exactly once.

The success graph has exactly three ordered top-level Git network operations:
reconciler clone, initializer fetch and initializer-doctor fetch. An executed
failure records only its actual ordered prefix. No manual Git network command,
direct checkout, custom clone, overlay, `-UpdateProjectManifests`, pending-
backup override, separate worker doctor, alternate remote, credential helper,
retry or in-attempt target rebase is allowed.

An independently authorized completion reviewer or rereviewer may own at most
one exact doctor invocation in its role window. A rollback worker must own the
one rollback-verifier doctor required for a complete-rollback claim; that
verifier is not a reconciliation retry and cannot satisfy worker counters.

## R4 — Zero-effect preflight

Before the first external effect, prove exact contained workspace, project,
Core, backup and evidence paths; expected remote; clean old Core; locally
available target and accepted ancestry; downstream staged-zero; R1-R2 hashes;
`operator-local`; recoverable preimages; every attempt-2 evidence path absent;
and all allowlisted P4-E/governance preservation hashes. Any false or unreadable
predicate selects the matrix's zero-effect refusal and permits no network,
Core/root/pin/binding mutation or attempt-2 artifact creation.

The protected operator assessment is excluded from open, read, hash, stage,
inventory and use. Broad downstream untracked inventory is forbidden.

## R5 — Exact attempt-2 evidence lifecycle

These six paths are the complete attempt-2 lifecycle and must all begin absent:

1. `D:\UNG DUNG AI\TOOL AI 2026\CVF-Workspace\_cvf-core-backups\CVF-CORE-REFRESH-2026-08-30-ATTEMPT-2-EVIDENCE`;
2. `docs/decisions/CVF_CORE_REFRESH_ROOT_EFFECTS_2026-08-30_ATTEMPT_2.json`;
3. `docs/decisions/CVF_CORE_REFRESH_WORKER_RETURN_2026-08-30_ATTEMPT_2.md`;
4. `docs/decisions/CVF_CORE_REFRESH_COMPLETION_REVIEW_2026-08-30_ATTEMPT_2.md`;
5. `docs/decisions/CVF_CORE_REFRESH_REVIEW_TARGET_MOVEMENT_ROLLBACK_2026-08-30_ATTEMPT_2.json`; and
6. `docs/decisions/CVF_CORE_REFRESH_REVIEW_TARGET_MOVEMENT_REREVIEW_2026-08-30_ATTEMPT_2.md`.

They must resolve inside their accepted containers without collision or
reparse-point escape. Attempt-1 receipts, review, evidence directory, preserved
replacement and all retained deltas are immutable and may never be overwritten,
deleted, renamed or reinterpreted.

The root-effects JSON is the initial worker's semantic receipt; worker Markdown
is a summary. Neither self-hashes nor cross-hashes. The completion review owns
their final hashes and does not self-hash. Conditional rollback JSON never
self-hashes; terminal rereview owns final hashes for all readable prior
attempt-2 artifacts and does not self-hash or depend on a future artifact.

## R6 — Exact 17 workspace-root targets

The reconciler root-effect ceiling is exactly this ordered set; every target
has a recoverable preimage and exactly one `CREATE`, `UPDATE`, `DELETE` or
`NO_CHANGE` post-observation:

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

Success and complete rollback require `17/17`. Originally absent targets return
to absence on rollback. Backups, failed replacements and failed-root deltas are
retained.

## R7 — Exact initial-worker downstream ceiling

The worker ceiling is exactly these 13 tracked paths:

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

The first two are pin carriers, the next nine are shared continuity carriers,
and the last two are worker evidence. Ignored `.cvf/local-binding.json` is the
one additional local effect. Every other downstream path is byte-protected,
including the closed attempt-1 handoff, dedicated P4-E/governance artifacts,
product/runtime/database/catalog files and all current SPEC/Work Order/review
artifacts.

## R8 — Preservation-first execution and worker rollback

Before the reconciler, preserve the old Core, 17 roots, two pins, nine shared
carriers, binding and accepted protected hashes. Immediately after the one
reconciler return, record transcript, exit, Core/backup locations, 17 root
observations and replacement state. Continue only if Core is clean, remote is
exact and `HEAD == origin/main ==` frozen target.

After that checkpoint only, perform the exact two-pin bridge and initializer.
Success requires initializer exit zero, bounded doctor PASS and five-way target
equality across Core HEAD, Core origin, manifest, AGENTS and binding.

Every post-start failure preserves the failed state, restores old Core/roots/
pins/shared/binding from preimages, runs at most the matrix-authorized one
rollback verifier, writes truthful evidence and stops. Complete and incomplete
rollback are disjoint. Incomplete rollback never fabricates Core/pin hashes,
staged-zero, P4-E preservation or unreadable artifact hashes.

## R9 — Closed terminal-outcome grammar

The registered matrix is the sole semantic owner of per-outcome required,
forbidden and conditional fields, exact operation/counter relations, failure-
stage/prefix pairs, rollback-stage/verifier pairs and evidence lifecycle. Its
closed outcome set is exactly:

1. `ZERO_EFFECT_PREFLIGHT_REFUSAL`;
2. `SUCCESS`;
3. `FAILURE_ROLLED_BACK`;
4. `FAILURE_ROLLBACK_INCOMPLETE`;
5. `REVIEW_TARGET_MOVEMENT`;
6. `REVIEW_TARGET_MOVEMENT_ROLLED_BACK`; and
7. `REVIEW_TARGET_MOVEMENT_ROLLBACK_INCOMPLETE`.

No prose artifact, adapter, fixture, receipt schema or Work Order may restate
or independently own those field rules. `REVIEW_TARGET_MOVEMENT` closes only
the initial reviewer window and routes conditional repair; it is not a tranche
success or target adoption. Only accepted success or complete-rollback terminal
review may route to bounded FREEZE. Incomplete rollback stays open failure.

## R10 — Reviewer movement and temporal ownership

Role windows are non-concurrent:

- `ORCHESTRATOR` records gates, authority boundaries and role routing; it does
  not implement or self-approve.
- `SPEC_AUTHOR` owns only this contract, matrix, registry entry and digest pin;
  its window ends at return for independent SPEC review.
- a later `WORK_ORDER_AUTHOR` may translate only an accepted SPEC into bounded
  commands, paths, evidence and stop rules; it grants no external effect.
- `IMPLEMENTATION_WORKER` owns preflight, initial execution, worker-time
  rollback, the first two evidence artifacts and worker return only.
- `INDEPENDENT_COMPLETION_REVIEWER` owns only the completion review and its
  separately authorized doctor; it never repairs.
- only after immutable `REVIEW_TARGET_MOVEMENT`, a distinct `REPAIR_WORKER`
  may restore two pins, nine shared carriers and binding from frozen BUILD
  preimages, perform hidden-Core/17-root rollback, and create only the
  conditional rollback JSON. It never reconciles or retries.
- a distinct `INDEPENDENT_COMPLETION_REREVIEWER` owns only the conditional
  terminal Markdown and any separately authorized rereviewer doctor.
- `CLOSER/SESSION_SYNC_STEWARD` acts only after accepted terminal review;
  `COMMIT_STEWARD` remains inactive without separate authority.

The repair ceiling is the intentional temporal intersection of 11 tracked
pin/shared carriers, one conditional JSON create and one ignored binding: at
most 12 tracked paths plus one ignored local effect. Both worker artifacts and
the completion review remain immutable. Conditional incomplete rollback uses
only the matrix's permitted stage/verifier pairs and honest observation states.

## R11 — Canonical invariant family and machine pin

Applicability is `TRIGGERED` by shared receipts across outcomes, outcome-
controlled field presence, exact counter/temporal relations, multiple validator
surfaces and the prior adjacent-family review history.

The sole matrix is
`docs/cvf/invariants/cvf-core-refresh-target-rebase-outcomes-2026-08-30.json`,
family `CVF-CORE-REFRESH-TARGET-REBASE-OUTCOMES-2026-08-30`, canonical digest
`dc0c35298fb584d995f51ed8cf996f599f12b934617afd51e1a27b24ce47f4cc`.
The machine consumer is
`docs/specs/cvf_core_refresh_target_rebase_2026_08_30_invariant_pin.py`.

The 2026-08-29 family and all attempt-1 evidence remain immutable historical
inputs, not semantic owners for attempt 2. Matrix, pin and SPEC form no self-
hash or cross-hash cycle: the matrix binds only already accepted phase sources;
SPEC and pin point one-way to the matrix digest.

## R12 — Conformance and mutation evidence

Before BUILD return, the matrix-declared deterministic adapter must emit one
disposable positive for each of seven outcomes inside the contained evidence
directory. The repository guard and an independent validator must accept each
positive exclusively and reject the complete generated one-fact mutation
corpus, with no excluded operator. Mutation coverage includes every required
deletion, forbidden-field insertion, discriminator substitution, unknown
field, illegal domain value, counter change and one-sided relation change.

Required commands are:

```text
python scripts/check_invariant_families.py --json
python -m pytest -q tests/unit/test_invariant_family_contract.py tests/integration/test_invariant_family_repository_guard.py
```

The reviewer recomputes the canonical digest and full corpus, samples one raw
positive per outcome, checks all declared validator surfaces and verifies no
expectation was derived from worker output.

## R13 — Final deterministic gates

Worker and reviewer run applicable JSON parsing, session/mirror, Project
Knowledge, invariant-family, focused invariant tests, catalog, file-size,
repository/scoped-diff and staged-zero guards. Completion review independently
checks command transcripts, exact 17-root and role-specific tracked/local path
ceilings, preimages, pins/target, hashes, P4-E preservation and prohibited
effects. A failed gate cannot be waived into success.

## R14 — Live-evidence and claim boundary

This maintenance tranche may prove only deterministic public-Core freshness/
pin reconciliation inside enumerated paths. It does not prove CVF control of an
AI/agent, provider behavior, product runtime adoption of the 202-path Core
delta, arbitrary-untracked absence, database behavior, deployment or
production readiness. Therefore no provider or mock output is governance proof
for this tranche. If a later claim asserts AI/agent governance behavior, a real
provider API call and recorded request/response are mandatory under project
policy.

Credentials, provider calls, package installation, product/database changes,
deployment, release, commit and push are outside this contract.

## Acceptance criteria

- `AC1`: R1-R5 pass before any external effect; otherwise the matrix's
  zero-effect refusal is the only valid outcome.
- `AC2`: initial execution stays inside R3 and R6-R8 and selects exactly one
  matrix outcome without claiming tranche closure.
- `AC3`: worker-time and reviewer-time rollback satisfy R8-R10 with immutable
  attempt-1 and prior attempt-2 evidence.
- `AC4`: R11 digest/ownership and R12 complete mutation corpus pass without
  exclusion, duplicate semantic owner or hash cycle.
- `AC5`: an independent reviewer recomputes R13, records findings and waivers,
  and accepts only an exact matrix shape.
- `AC6`: R14 remains true for every outcome.

## Next governed move

Independent SPEC review only. Work Order, BUILD, reconciler, doctor, network,
Core/workspace-root/pin/binding mutation, P4-E SPEC, provider/credential use,
installation, product/database change, deployment, commit and push remain
unauthorized.
