# Work Order — Bootstrap-Native CVF Core Refresh

- Tranche: `CVF-CORE-REFRESH-2026-08-23`
- Phase: `WORK_ORDER`
- Risk: `R2`
- Status: `READY_FOR_AUTHORIZATION_REVIEW`
- Operator direction: remove low-value over-engineering and unblock the parked
  project lane.
- BUILD/network authority: `CONDITIONAL_ON_AUTHORIZATION_REVIEW_PASS`
- DESIGN SHA-256:
  `7a6634c831013b55464d61cb32cc020b5f64eeca704dea5213e182a27aee9efa`
- SPEC SHA-256:
  `5946c55a4a50aa6626a3f39a08b2e5e04b1e9e87897a9cd1592a27594484e7fe`

## 1. Precedence

This Work Order supersedes the executable instructions in the historical
593-line Core-refresh Work Order and its 8x2 evidence-contract amendment. Those
files, the matrix, adapter and reviews remain historical evidence only. The
accepted bootstrap-native DESIGN/SPEC and this Work Order are the complete
execution contract.

## 2. Roles

- `IMPLEMENTATION_WORKER`: performs preflight, preimages, the two sanctioned
  worker commands, rollback if needed, and the concise worker return.
- `INDEPENDENT_COMPLETION_REVIEWER`: after worker success, runs one doctor and
  verifies the final state/path/evidence checklist.
- Reviewer and worker must be different agents.
- No commit or push is authorized in this Work Order.

## 3. Fixed inputs

- Old Core pin: `7d9f360a3df11ac998972728000785799399c02b`.
- Target: `3b031fec35473e6ee6a554c4c72400e7a23b06c5`.
- Remote: `https://github.com/Blackbird081/Controlled-Vibe-Framework-CVF.git`.
- Reconciler SHA-256:
  `96ac0cce3bf9df5733ffe2c6f5a7850db0ccfdc4403daaa70fdb6981dc58196c`.

Exact worker commands, in order:

```text
powershell -ExecutionPolicy Bypass -File "<core>\scripts\update_cvf_workspace_public_core.ps1" -WorkspaceRoot "<workspace-root>"
powershell -ExecutionPolicy Bypass -File scripts/initialize_cvf_clone.ps1
```

Exact independent-review/rollback-verifier command:

```text
powershell -ExecutionPolicy Bypass -File "<core>\scripts\check_cvf_workspace_agent_enforcement.ps1" -ProjectPath "<project-root>"
```

## 4. Exact ceilings

Workspace-root effects, exactly 17:

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

Downstream worker paths, exactly 12; the first ten are mutable carriers:

```text
.cvf/manifest.json
AGENTS.md
knowledge/manifest.json
IMPLEMENTATION_STATUS.json
SESSION/ACTIVE_SESSION_STATE.json
CVF_SESSION/ACTIVE_SESSION_STATE.json
SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json
SESSION/SESSION_MEMORY.md
SESSION/handoffs/CVF_CORE_REFRESH_2026-08-23.md
docs/INDEX.md
docs/decisions/CVF_CORE_REFRESH_ROOT_EFFECTS_2026-08-23.json
docs/decisions/CVF_CORE_REFRESH_WORKER_RETURN_2026-08-23.md
```

Pre-BUILD governance artifacts are not worker-path additions. Every other
workspace/project path is immutable during BUILD. The assessment path is
excluded without opening, reading, hashing, inventorying, staging or use.

## 5. Preflight and preimages

Before external effect, the worker must verify and record:

- downstream staged set empty and `HEAD == origin/main`;
- exact non-assessment porcelain path set and statuses;
- Core clean at the old pin, exact remote and target already present at
  `origin/main`;
- reconciler digest and exact DESIGN/SPEC/Work Order digests;
- containment of one fresh evidence directory directly below
  workspace-root `_cvf-core-backups`.

Inside that directory preserve the complete old Core, all 17 root targets as
existence plus byte preimages, and all ten carrier byte preimages. A preflight
failure stops zero-effect with no doctor.

## 6. BUILD

Run each exact worker command once with a plain PowerShell transcript and exit
code. Do not add flags, direct Git commands, trace2/packet instrumentation or a
separate worker doctor.

Success requires exactly the inherent three public operations: reconciler
clone, initializer fetch and initializer-owned doctor fetch. They use no
credentials, the exact remote and the frozen target.

After the commands, write only:

- `docs/decisions/CVF_CORE_REFRESH_ROOT_EFFECTS_2026-08-23.json` containing
  direct before/after root existence/hash observations; and
- `docs/decisions/CVF_CORE_REFRESH_WORKER_RETURN_2026-08-23.md` containing
  command transcripts/exits, Core/pin equality, doctor result, actual changed
  paths, backup location and explicit claim boundary.

No synthetic corpus, matrix consumer, adapter or frozen runner is executed.

## 7. Failure

After any worker mutation/external execution failure:

1. preserve the failed replacement Core under the evidence directory;
2. restore the old Core;
3. restore all 17 root targets to captured existence/bytes, moving any newly
   created target whose prestate was absent into evidence quarantine;
4. restore all ten carrier bytes;
5. verify old Core, `17/17` roots and `10/10` carriers;
6. run the verifier command exactly once, record its transcript/exit, and stop.

The reached public-operation prefix is recorded as `0..3`. Failure never
becomes success and no completion-review doctor runs for that attempt.

## 8. Authorization and completion review

Authorization review checks exact hashes, commands, ceilings, preflight,
rollback and evidence list. `AUTHORIZATION_REVIEW_PASS` activates the
operator's conditional BUILD/network authority for this Work Order only.

After worker success, the independent completion reviewer runs the exact doctor
once, then directly verifies:

- Core clean and `HEAD == origin/main == manifest == binding == AGENTS == target`;
- doctor PASS and staged set empty;
- actual root effects and downstream changes remain within `17/12`;
- non-carrier preexisting dirty paths retain their bytes;
- transcripts, exits, root observation and worker return exist and agree.

Review records findings/waivers explicitly. It does not reconstruct the retired
evidence framework or repeat unchanged tests.

## 9. Stop conditions and prohibited effects

Stop on any preflight/digest/containment mismatch, target movement, credential
request, undeclared path effect, failed command, failed restore, assessment
access, or need for provider/install/database/deployment/commit/push authority.

The only network permitted is the exact public Git activity inherent in the
two worker commands, one conditional rollback verifier on failure, and one
completion-review doctor after success. No AI-governance claim is made, so no
provider API call is required or authorized.

## 10. Review path

Authorization review is written only to:
`docs/decisions/CVF_CORE_REFRESH_BOOTSTRAP_NATIVE_WORK_ORDER_AUTHORIZATION_REVIEW_2026-08-24.md`.

## 11. Target-rebase amendment — 2026-08-24

The prior authorization is historical for the rolled-back `3b031fec...`
attempt and does not authorize a retry. For the next attempt only:

- frozen target: `864c4e0e6139f3e32067dea41f43f240e505c0d8`;
- DESIGN raw SHA-256:
  `3028a5741cd28a8f3868d267e882660704064497b32833797734a2c84552a24d`;
- SPEC raw SHA-256:
  `002f31ef8b4e922deb2c5955764e01e2e838846c023eedc3bc840de6ce85d895`.

These values supersede only the old target and dependent DESIGN/SPEC pins.
All exact commands, `17/12/10` arrays, preflight, fresh preimages, success and
failure graphs, preservation-first rollback, evidence list, assessment
exclusion and prohibited effects remain unchanged. The next attempt requires a
fresh evidence directory and independent authorization PASS. Any further
target movement stops and rolls back; no commit or push is authorized.

## 12. Pin-carrier sequencing repair — 2026-08-24

The `INITIALIZER_PIN_REFUSAL` attempt is historical and fully rolled back; its
authorization does not permit another retry. Current governing pins are:

- DESIGN raw SHA-256:
  `695565e6ab9137f6d6366a9e683d176a6225140462ca5ae3d100911681d02c35`;
- SPEC raw SHA-256:
  `01f8acb4274d4276b05bace965d8e6635fd405bb39876857a29e2a94b4cca78e`;
- target: `864c4e0e6139f3e32067dea41f43f240e505c0d8`.

For the next attempt, section 6 is amended only by this mandatory local step
between the two unchanged worker commands:

1. after command 1 exit `0`, verify Core clean and exact
   `HEAD == origin/main == target`;
2. using scoped `apply_patch` edits, replace the old full pin exactly once in
   `.cvf/manifest.json` at `cvfCoreCommit` and exactly once in `AGENTS.md` at
   the `CVF Commit` header;
3. parse the manifest and verify both carrier values equal the full target;
4. record the local step result in the plain worker transcript, then invoke
   command 2 exactly once.

Zero/multiple matches or any check/write/parse failure triggers section 7
rollback. These two files are already carrier paths with byte preimages; the
step adds no public operation and no path. The expected success graph remains
clone + initializer fetch + initializer-owned doctor fetch. All remaining
commands, `17/12/10` arrays, fresh-backup rule, failure graph, evidence,
assessment exclusion and prohibited effects remain unchanged. Fresh independent
authorization PASS is required; no commit or push is authorized.

## 13. Completion F1 acceptance amendment — 2026-08-24

The successful BUILD and the single completion doctor are fixed historical
evidence. No BUILD command, pin edit, reconciler, initializer or doctor may be
rerun for this amendment. Current governing pins are:

- DESIGN raw SHA-256:
  `0db70eb33acbfbe5e0e0a449846d370da43e8de71519b26885dfa539f6c877d8`;
- SPEC raw SHA-256:
  `427453a64940bf926f74ec0e2a09736823f3394f6492d7bdf925cc12de0683b3`.

For completion rereview, section 8's non-carrier byte predicate is superseded
only for the 33 frozen dirty paths outside the ten carriers. The reviewer must
instead verify the canonical frozen 39-path/status set and LF digest, unchanged
33-path membership/status, exact command/local-patch transcripts, actual
changed-path containment within the 12 worker paths, and no new dirty path
outside that ceiling. Ten-carrier byte proof and every other completion check
remain mandatory.

The rereview must explicitly state that 33-path byte equality is not claimed.
It may read existing evidence and perform local read-only state checks only; it
must not use network or create another doctor result. A PASS closes only F1 and
the bounded Core-refresh completion contract. No commit or push is authorized.
