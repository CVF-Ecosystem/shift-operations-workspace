# WORK ORDER — CVF Public-Core Refresh

- Tranche: `CVF-CORE-REFRESH-2026-08-29`
- Phase: `WORK_ORDER`
- Risk: `R2`
- Status: `READY_FOR_INDEPENDENT_AUTHORIZATION_REVIEW`
- BUILD external-effect authority: `NOT_GRANTED_BY_THIS_DOCUMENT`
- Old Core/pin: `a7a797d7111be472ef2cbd928cbeffc70ccb6bc6`
- Frozen target: `06c3d040a3dc8fa22fa27f2f9c3e40739def075e`
- Accepted DESIGN SHA-256:
  `2e383c0918a77d3262b9a065e8cbeca5a4e5798dfd7e4771c311f4f0af049443`
- Accepted DESIGN amendment SHA-256:
  `2f250e98914f671b19f7be3a820f2b216c277e8f8900e2f77ceaab69255a44e0`
- Accepted SPEC SHA-256:
  `03932a375516ff100e452a40c92fa4886e5e4b1bb10488d446dc8faa162b4f01`
- Final SPEC review SHA-256:
  `5b77e40c103cdab1a648a06d60595cc0a07aaeb65e856688c36d664e265b5890`

## 1. Authorization boundary

This Work Order translates the accepted DESIGN, amendment and SPEC into one
bounded execution contract. An independent `AUTHORIZATION_REVIEW_PASS` makes
the contract eligible for a later BUILD boundary decision; it does not itself
authorize network use, hidden-Core/workspace-root mutation, credentials,
provider calls, installation, database/product changes, deployment, commit or
push. The ORCHESTRATOR must stop after authorization review until that external
effect boundary is explicitly recorded.

The protected operator assessment remains wholly excluded: no role may open,
read, hash, inventory, stage or use it. Broad untracked inventory is forbidden.

## 2. Fixed locations and roles

- Workspace root:
  `D:\UNG DUNG AI\TOOL AI 2026\CVF-Workspace`
- Project root:
  `D:\UNG DUNG AI\TOOL AI 2026\CVF-Workspace\shift-operations-workspace`
- Current Core root:
  `D:\UNG DUNG AI\TOOL AI 2026\CVF-Workspace\.Controlled-Vibe-Framework-CVF`
- Public remote:
  `https://github.com/Blackbird081/Controlled-Vibe-Framework-CVF.git`
- Fresh evidence directory, required absent at preflight:
  `D:\UNG DUNG AI\TOOL AI 2026\CVF-Workspace\_cvf-core-backups\CVF-CORE-REFRESH-2026-08-29-ATTEMPT-1-EVIDENCE`

Roles are temporally exclusive:

- `IMPLEMENTATION_WORKER`: preflight, preimages, initial execution, rollback
  if needed, worker evidence and return.
- `INDEPENDENT_COMPLETION_REVIEWER`: one post-success doctor and completion
  review only; never repairs.
- `REPAIR_WORKER`: only after completion review records
  `REVIEW_TARGET_MOVEMENT`, executes rollback from frozen BUILD preimages and
  creates the conditional rollback JSON; never retries reconciliation.
- `INDEPENDENT_COMPLETION_REREVIEWER`: reviews the conditional rollback and
  creates its separate Markdown receipt.
- `CLOSER/SESSION_SYNC_STEWARD`: only after final review PASS, returns shared
  continuity to parked P4-E without opening P4-E SPEC.
- `COMMIT_STEWARD`: inactive; no commit or push is authorized.

The implementation worker, repair worker and each reviewer must be distinct
role assignments. A reviewer cannot approve an artifact it authored.

## 3. Exact commands and operation graph

From the project root, the initial worker may invoke exactly:

```text
powershell -ExecutionPolicy Bypass -File "D:\UNG DUNG AI\TOOL AI 2026\CVF-Workspace\.Controlled-Vibe-Framework-CVF\scripts\update_cvf_workspace_public_core.ps1" -WorkspaceRoot "D:\UNG DUNG AI\TOOL AI 2026\CVF-Workspace"
powershell -ExecutionPolicy Bypass -File "D:\UNG DUNG AI\TOOL AI 2026\CVF-Workspace\shift-operations-workspace\scripts\initialize_cvf_clone.ps1"
```

Between them, and only after the reconciler checkpoint proves clean
`Core HEAD == Core origin/main == target`, the worker uses scoped
`apply_patch` edits to replace the old full pin exactly once in
`.cvf/manifest.json.cvfCoreCommit` and exactly once in the generated `AGENTS.md`
`CVF Commit` header. It parses/verifies both target values before initializer.

Successful worker network accounting is exactly the three ordered top-level
Git operations inherent in those commands: reconciler clone, initializer
fetch, initializer-doctor fetch. No direct Git network command, extra worker
doctor, flag, alternate remote, credential helper or retry is permitted.

The completion reviewer or one separately authorized rereviewer may invoke at
most one exact doctor each:

```text
powershell -ExecutionPolicy Bypass -File "D:\UNG DUNG AI\TOOL AI 2026\CVF-Workspace\.Controlled-Vibe-Framework-CVF\scripts\check_cvf_workspace_agent_enforcement.ps1" -ProjectPath "D:\UNG DUNG AI\TOOL AI 2026\CVF-Workspace\shift-operations-workspace"
```

A rollback worker must use this same command exactly once after restoration to
claim any complete rollback. If rollback becomes incomplete before the
verifier, it records `NOT_RUN`; if the verifier itself fails, it records the
closed incomplete verifier state from the matrix. Its expected stale-Core
result is never success.

## 4. Preflight and preservation

Before any external effect, record and require all SPEC R1-R5 predicates. In
particular:

- Core clean at old pin, exact remote, locally observed target object and
  ancestry; downstream `HEAD == origin/main == a8e2ad8199d700a238d7d74bdbf85329446228de`
  and staged zero;
- reconciler SHA-256
  `96ac0cce3bf9df5733ffe2c6f5a7850db0ccfdc4403daaa70fdb6981dc58196c`,
  accepted contract hashes above, matrix digest in section 8, sanctioned
  command paths and active `operator-local` profile unchanged;
- evidence directory and all four future evidence paths absent, with no path
  or reparse-point collision;
- contained resolved paths and recoverable byte preimages for the old Core,
  exact 17 root targets, two pins, nine shared carriers and ignored binding;
- explicit `PRESENT` plus raw hash/bytes or `ABSENT` for every carrier, plus
  allowlisted raw hashes for parked P4-E and current governance artifacts; and
- contained inventory of prior Core backups/failed replacement deltas without
  deleting or overwriting them.

Any mismatch stops zero-effect. The worker does not create an evidence artifact
or run a doctor for a preflight refusal.

## 5. Exact root-effect ceiling

The reconciler may affect only these 17 workspace-root targets, each accounted
once as `CREATE`, `UPDATE`, `DELETE` or `NO_CHANGE`:

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

Success and complete rollback both require `17/17`; no other root effect is
allowed. Backups, failed replacements and failed-root deltas are retained.

## 6. Exact downstream ceilings

The initial worker may change at most these 13 tracked paths:

```text
.cvf/manifest.json
AGENTS.md
knowledge/manifest.json
IMPLEMENTATION_STATUS.json
SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json
SESSION/ACTIVE_SESSION_STATE.json
CVF_SESSION/ACTIVE_SESSION_STATE.json
SESSION/SESSION_MEMORY.md
SESSION/handoffs/CVF_CORE_REFRESH_2026-08-29.md
docs/INDEX.md
docs/implementation/EXECUTION_ROADMAP.md
docs/decisions/CVF_CORE_REFRESH_ROOT_EFFECTS_2026-08-29.json
docs/decisions/CVF_CORE_REFRESH_WORKER_RETURN_2026-08-29.md
```

Ignored `.cvf/local-binding.json` is one declared local effect. The first two
paths are pins, the next nine shared continuity and the final two worker
evidence. Every other downstream path, including P4-E/governance artifacts and
product/runtime/database/catalog files, is byte-protected during BUILD.

The completion reviewer alone may create
`docs/decisions/CVF_CORE_REFRESH_COMPLETION_REVIEW_2026-08-29.md`.

On reviewer target movement only, the repair worker may restore/update the two
pins plus nine shared carriers, restore/regenerate the binding and create
`docs/decisions/CVF_CORE_REFRESH_REVIEW_TARGET_MOVEMENT_ROLLBACK_2026-08-29.json`:
at most 12 tracked paths plus one ignored local effect. The three earlier
evidence artifacts remain immutable. The rereviewer alone may create
`docs/decisions/CVF_CORE_REFRESH_REVIEW_TARGET_MOVEMENT_REREVIEW_2026-08-29.md`.

## 7. Success, failure and rollback

Initial success requires reconciler checkpoint, exact two-pin bridge,
initializer exit zero, bounded doctor PASS, Core clean and five-way target
equality across Core HEAD/origin, manifest, AGENTS and binding. Then write the
canonical root-effects JSON, Markdown summary and nine shared carriers; run
the deterministic gates; leave staged zero; return for independent review.

After any post-start failure, containment-check and preserve the failed state;
quarantine the replacement Core/new root targets; restore old Core, 17 roots,
pins/shared carriers/binding from frozen preimages; run exactly one rollback
verifier before any complete-rollback claim; then record either
`FAILURE_ROLLED_BACK` or honest `FAILURE_ROLLBACK_INCOMPLETE`. A pre-verifier
incomplete rollback stops with `NOT_RUN`; no retry follows.

After successful worker return, reviewer target movement produces immutable
`REVIEW_TARGET_MOVEMENT`. The repair worker performs rollback only and records
`REVIEW_TARGET_MOVEMENT_ROLLED_BACK` or honest incomplete rollback in its
separate JSON. Its only post-verifier write-stage token is the shared-
continuity write failure defined by SPEC; the JSON may not describe failure to
write itself. Any new target requires fresh governed authority.

## 8. Invariant-family proof fields

- Applicability: `CVF-CORE-REFRESH-OUTCOMES-2026-08-29` (`R2`, registered).
- Matrix path: `docs/cvf/invariants/cvf-core-refresh-outcomes-2026-08-29.json`.
- Canonical digest:
  `5f6e477d8d76e11965c91c0034f0ff4f7d82e1beab5d41c2266526957a5a8025`.
- Adapter: matrix-declared inline identity
  `CVF_CORE_REFRESH_WORKER_AND_MOVEMENT_ROLLBACK_INLINE_ADAPTER_V2`; no tracked
  adapter path is created. Disposable positives live only inside the contained
  evidence directory and are derived from the pinned matrix, never worker
  output.
- Evidence tests: `tests/unit/test_invariant_family_contract.py` and
  `tests/integration/test_invariant_family_repository_guard.py`.
- Mutation exclusions: `NONE`.
- Exact repository commands:
  `python scripts/check_invariant_families.py --json` and
  `python -m pytest -q tests/unit/test_invariant_family_contract.py tests/integration/test_invariant_family_repository_guard.py`.
- Evidence owner: initial `IMPLEMENTATION_WORKER` or conditional
  `REPAIR_WORKER`; reviewer recomputes digest, five positives, full generated
  mutation corpus and the focused stage/verifier cross-product independently.

Per-outcome rules remain only in the matrix and are not duplicated here.

## 9. Evidence, gates and claim boundary

The root-effects JSON is the sole initial-worker semantic receipt; the worker
Markdown is only a summary. Neither self-hashes or cross-hashes. Independent
review owns their final hashes. Conditional rollback follows the separate
non-overwriting lifecycle in sections 6-7.

Worker/reviewer applicable gates are JSON parsing, session/mirror, Project
Knowledge, invariant-family, focused invariant tests, catalog, file-size,
repository/scoped diff and staged-zero. Completion review independently checks
commands/transcripts, 17-root/13-path ceilings, backups, target/pins, doctor,
P4-E preservation, invariant proof and prohibited effects.

The claim is only deterministic public-Core pin/freshness reconciliation. It
does not prove AI/agent governance, Core runtime adoption, product behavior,
arbitrary-untracked absence, production readiness or deployment. No provider
call belongs to this claim.

## 10. Stop conditions and review path

Stop on target movement, preflight/hash/containment/profile mismatch, Core or
downstream dirt outside allowlists, unexpected path/command/network effect,
credential need, failed restore, evidence collision, protected-assessment
contact, or need for provider/install/database/product/deployment/commit/push.

Authorization review may create only:
`docs/decisions/AUTHORIZATION_REVIEW_2026-08-29_CVF_CORE_REFRESH.md`.
It must recompute all contract hashes and complete the shared invariant-family
proof fields. `AUTHORIZATION_REVIEW_PASS` does not waive section 1's external-
effect stop. BUILD remains unauthorized until a later explicit boundary record.
