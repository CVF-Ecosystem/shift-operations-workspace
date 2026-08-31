# WORK ORDER — CVF Public-Core Exact-Target Rebase 0281e93

- Tranche: `CVF-CORE-REFRESH-TARGET-REBASE-0281E93-2026-08-30`
- Phase: `WORK_ORDER`
- Risk: `R2`
- Status: `READY_FOR_INDEPENDENT_AUTHORIZATION_REVIEW`
- Active role: `WORK_ORDER_AUTHOR`
- BUILD external-effect authority: `NOT_GRANTED_BY_THIS_DOCUMENT`
- Old Core/pin: `a7a797d7111be472ef2cbd928cbeffc70ccb6bc6`
- Frozen target: `0281e93bab4a75083973eb7242fd2bc8f65055d3`
- Public remote:
  `https://github.com/Blackbird081/Controlled-Vibe-Framework-CVF.git`
- Final accepted SPEC SHA-256:
  `7264fb1e142062be9c60cbfd486ec93e671fe384347fd98567c22346d4e527c4`
- Final SPEC review/rereview SHA-256:
  `82727d1b54acccc640a179bda09691d4f104feb968e06065d9bb6a0865884bba`
- Matrix raw/canonical SHA-256:
  `e39de7e9ed3199ec8f9033b1c90af9eca993655470f675a0ed3ae93846dbe45c`
- Machine-pin file SHA-256:
  `855b02058e1a358cb02187dd852cf8b6c0e47f6d6d4d5642b7b27a093dada852`

## 1. Authority and phase boundary

This Work Order translates only the accepted exact-target DESIGN and final SPEC into a bounded execution contract. It grants no BUILD or external-effect authority. Independent `AUTHORIZATION_REVIEW_PASS` makes the exact bytes of this document eligible for a later authority decision; it does not activate the graph below.

Before assigning an `IMPLEMENTATION_WORKER`, the ORCHESTRATOR must record an explicit approval that identifies this Work Order by path and SHA-256, repeats the exact old pin and target, and authorizes the enumerated external effects: the sanctioned reconciler, scoped two-pin bridge, initializer and their exact network/root/Core/pin/binding/evidence consequences. Approval of a different hash, target, path set, command, network graph or role assignment is invalid.

Until both independent review and that exact recorded approval exist, the following remain prohibited: doctor/fetch/reconciler/initializer execution; network/provider/credential use; evidence-directory creation; hidden-Core, workspace-root, downstream pin, binding or continuity mutation; fixture repair; installation; product/runtime/database change; deployment; release; commit; and push. `COMMIT_STEWARD` remains inactive in every outcome of this Work Order.

The protected operator assessment is excluded from open, read, hash, inventory, stage and use by every role. Broad downstream untracked inventory is forbidden.

## 2. Accepted lineage and fixed locations

Independent authorization review and BUILD preflight must recompute these
exact raw SHA-256 values from current bytes:

| Artifact | SHA-256 |
|---|---|
| `docs/decisions/INTAKE_2026-08-30_CVF_CORE_REFRESH_TARGET_REBASE_0281E93.md` | `28e1160993d2638554bdb810dd36f393eebb65db62b47b8f92b8049fc290ba53` |
| `docs/decisions/INTAKE_REVIEW_2026-08-30_CVF_CORE_REFRESH_TARGET_REBASE_0281E93.md` | `4c754b7cc47ef247453075e0633848534d121959aba7fb845d49f12975da1b8c` |
| `docs/decisions/DESIGN_2026-08-30_CVF_CORE_REFRESH_TARGET_REBASE_0281E93.md` | `1fc8c00dd19bfd08a4b185f1fdc41fbe58991a7006248a593a5fc6fc371cb8b5` |
| `docs/decisions/DESIGN_REVIEW_2026-08-30_CVF_CORE_REFRESH_TARGET_REBASE_0281E93.md` | `78eaf8c9e7e01af721c877ed6aaa89b6446baea40e3ef05df85f8772d1088c56` |
| `docs/specs/CVF_CORE_REFRESH_TARGET_REBASE_0281E93_2026-08-30_SPEC.md` | `7264fb1e142062be9c60cbfd486ec93e671fe384347fd98567c22346d4e527c4` |
| `docs/decisions/SPEC_REVIEW_2026-08-30_CVF_CORE_REFRESH_TARGET_REBASE_0281E93.md` | `82727d1b54acccc640a179bda09691d4f104feb968e06065d9bb6a0865884bba` |
| `docs/cvf/invariants/cvf-core-refresh-target-rebase-0281e93-outcomes-2026-08-30.json` | `e39de7e9ed3199ec8f9033b1c90af9eca993655470f675a0ed3ae93846dbe45c` |
| `docs/specs/cvf_core_refresh_target_rebase_0281e93_2026_08_30_invariant_pin.py` | `855b02058e1a358cb02187dd852cf8b6c0e47f6d6d4d5642b7b27a093dada852` |
| `docs/cvf/invariants/registry.json` | `3022d323782e2fd3cf18f377f4293b43e1637a1f14ccef96a1b3717a2ac9f0e2` |
| `.cvf/policy.json` | `c8a28fb11accc2ae3d21054636f6c32046e1547203be8b4044901f658ed3a863` |
| `docs/cvf/INVARIANT_FAMILY_STANDARD.md` | `c360655acb89c6fc8e412f87289d5ef990f62c5795605a95b1d4327cd6dff402` |
| `docs/cvf/invariants/invariant-family.schema.json` | `7313f9c9f631eacf160f2ce0ad2fdef5757eb10427fdb3574354f9a3564714e0` |

Fixed resolved locations are:

- workspace root:
  `D:\UNG DUNG AI\TOOL AI 2026\CVF-Workspace`;
- project root:
  `D:\UNG DUNG AI\TOOL AI 2026\CVF-Workspace\shift-operations-workspace`;
- hidden Core root:
  `D:\UNG DUNG AI\TOOL AI 2026\CVF-Workspace\.Controlled-Vibe-Framework-CVF`;
- backup container:
  `D:\UNG DUNG AI\TOOL AI 2026\CVF-Workspace\_cvf-core-backups`; and
- public remote exactly as stated in the header.

The old and target Git objects must already be local before P0. Without a fetch, preflight must prove clean Core `HEAD == a7a797d...`, local `origin/main == 0281e93...`, ancestry exactly `0` ahead / `6` behind, and both downstream pins plus ignored binding at the old full pin. Any other target, remote, ancestry, advertised/ref state or accepted hash is fail-closed. No role may retarget or amend this attempt in place.

## 3. Frozen tool, profile and P0-source identities

All identities below must be recomputed by the authorization reviewer and by
the worker before any external effect:

| Surface | Required identity |
|---|---|
| Core reconciler raw / Git blob | `96ac0cce3bf9df5733ffe2c6f5a7850db0ccfdc4403daaa70fdb6981dc58196c` / `4b705c6bf7b10bda62520dca488ecb453a4f4945` |
| Core doctor raw / Git blob | `2410bbabf88f12581d2e34a71efe247fe9080ebb299a58eb6f9ff6a35818796b` / `2ad83efee05c738fec40aa1779929da07f3d1c8c` |
| Core new-workspace raw / Git blob | `7e5567c55026f3be44f11c924d44835d6fb98b1fb4268dfedf6453af89927032` / `5f311a1a1c8dc787c7b19011bf34c5a84fc773c7` |
| Core `governance/toolkit/05_OPERATION` Git tree | `23fe8bd39ae102d3302d34de1d80208e2ef9bbb6` |
| Downstream initializer raw | `bb37b16256a693853bddfdbcb40c2f7211e6984a90a972da83899962fae209c8` |
| Active `operator-local` selector raw | `f51bacd206ec4e95b92f4f4479bc7c68ee605db3752d514ff3094bdff02dc855` |

The three Core script blobs and operation tree must be identical at the old pin and target. Any byte, object, policy or profile drift is `TOOL_OR_EFFECT_DRIFT` and requires a fresh governed target decision.

The exact read-only P0 source set is:

| Source | SHA-256 |
|---|---|
| `scripts/invariant_family_contract.py` | `19616ecaf9bbdb35738a1622fa790c7f0c0e24d5afdbbae154d402528aa78497` |
| `scripts/invariant_family_mutation_generator.py` | `d5f2e13328874dc41946fe73334f8c34eb55619db3b101781869d448b54a82ae` |
| `scripts/invariant_family_ownership.py` | `71ec4c547d72c9e4d3d6a8951aaf889f78e8459849106f143beb6298b523aac7` |
| `scripts/invariant_family_mutation_oracle.py` | `f9bf70a8c2adee0097c9faed7e1b2f0e554aa1fa3d6021a0ed346275de0f6cdc` |
| `scripts/cvf_core_refresh_conformance.py` | `cae96b6eef4ab9d5bd4e0a8a58c02d05c04591d68b835a1be356f140c5a4adb9` |
| `tests/unit/test_invariant_family_pattern_mutations.py` | `49dba6d885c054170fd2a48905e5ee0ebdd33b9dcb7a507b74d6c5af8b0f14a7` |
| `tests/integration/test_invariant_family_repository_guard.py` | `44cdf8451cef01bfe58239563afe3aaf162b92906812c2c5725a3925e39079e6` |

The last two paths are parked fixture-state preimages, not edit scope. Any change in this source set selects `ZERO_EFFECT_PREFLIGHT_REFUSAL`; the worker must not repair or suppress the inherited fixture failures.

## 4. Exact read-only P0 command and adapter

Working directory is the exact project root in section 2. Adapter identity is
`CVF_CORE_REFRESH_TARGET_REBASE_0281E93_READ_ONLY_P0_ADAPTER_V1`. The UTF-8,
LF-normalized bytes strictly between the `PYTHON-PAYLOAD-BEGIN` and
`PYTHON-PAYLOAD-END` marker lines below have SHA-256
`0cd29a56f7186a5c030aae8d365d3f778d787d27a6797eab6e12226639bdb925`. Those bytes are the only authorized P0
payload; the marker lines are excluded.

`PYTHON-PAYLOAD-BEGIN`
```python
import copy, hashlib, json, re, sys
from pathlib import Path
root = Path.cwd().resolve()
sys.path.insert(0, str(root / "scripts"))
from scripts import invariant_family_contract as contract
from scripts.cvf_core_refresh_conformance import _all_shapes, _match_sets, _shape, _temporal_cases, strict_matches_shape, synthesize_positive
from scripts.invariant_family_mutation_generator import generate_mutations
from scripts.invariant_family_mutation_oracle import required_mutation_ids

family = "CVF-CORE-REFRESH-TARGET-REBASE-0281E93-OUTCOMES-2026-08-30"
matrix_rel = "docs/cvf/invariants/cvf-core-refresh-target-rebase-0281e93-outcomes-2026-08-30.json"
matrix_path = root / matrix_rel
digest = "e39de7e9ed3199ec8f9033b1c90af9eca993655470f675a0ed3ae93846dbe45c"
source_hashes = {
    "scripts/invariant_family_contract.py": "19616ecaf9bbdb35738a1622fa790c7f0c0e24d5afdbbae154d402528aa78497",
    "scripts/invariant_family_mutation_generator.py": "d5f2e13328874dc41946fe73334f8c34eb55619db3b101781869d448b54a82ae",
    "scripts/invariant_family_ownership.py": "71ec4c547d72c9e4d3d6a8951aaf889f78e8459849106f143beb6298b523aac7",
    "scripts/invariant_family_mutation_oracle.py": "f9bf70a8c2adee0097c9faed7e1b2f0e554aa1fa3d6021a0ed346275de0f6cdc",
    "scripts/cvf_core_refresh_conformance.py": "cae96b6eef4ab9d5bd4e0a8a58c02d05c04591d68b835a1be356f140c5a4adb9",
    "tests/unit/test_invariant_family_pattern_mutations.py": "49dba6d885c054170fd2a48905e5ee0ebdd33b9dcb7a507b74d6c5af8b0f14a7",
    "tests/integration/test_invariant_family_repository_guard.py": "44cdf8451cef01bfe58239563afe3aaf162b92906812c2c5725a3925e39079e6",
}
for rel, expected in source_hashes.items():
    assert hashlib.sha256((root / rel).read_bytes()).hexdigest() == expected
matrix = contract.load_json_no_dup(matrix_path)
assert contract.canonical_digest(matrix_path) == digest
assert matrix["familyId"] == family
registry = contract.load_json_no_dup(root / "docs/cvf/invariants/registry.json")
owners = [x for x in registry["families"] if x.get("familyId") == family]
assert len(owners) == 1 and owners[0].get("matrixPath") == matrix_rel
pin_text = (root / "docs/specs/cvf_core_refresh_target_rebase_0281e93_2026_08_30_invariant_pin.py").read_text(encoding="utf-8")
assert re.search(r'MATRIX_CANONICAL_DIGEST\s*=\s*"([0-9a-f]{64})"', pin_text).group(1) == digest

positives = {}
mutation_ids = []
shape_counts = {}
operator_counts = {}
for shape in _all_shapes(matrix):
    sid = shape["shapeId"]
    positive = synthesize_positive(matrix, shape)
    positives[sid] = positive
    matches = _match_sets(matrix, positive)
    assert matches["repository"] == [sid] and matches["independent"] == [sid]
    mutations = generate_mutations(matrix, sid, positive)
    generated = [m.mutationId for m in mutations]
    oracle = required_mutation_ids(matrix, sid, positive)
    assert len(generated) == len(set(generated)) and set(generated) == oracle
    for mutation in mutations:
        assert _match_sets(matrix, mutation.payload) == {"repository": [], "independent": []}
        mutation_ids.append(mutation.mutationId)
        operator_counts[mutation.operator] = operator_counts.get(mutation.operator, 0) + 1
    shape_counts[sid] = len(mutations)
assert len(positives) == 8
assert len(mutation_ids) == len(set(mutation_ids)) == 1257

temporal = _temporal_cases(matrix, positives)
assert len(temporal) == 40 and sum(x["expected"] for x in temporal) == 38
assert sum(not x["expected"] for x in temporal) == 2 and all(x["correct"] for x in temporal)

sha_sid = "REVIEW_TARGET_MOVEMENT_ROLLED_BACK_VALID"
sha_shape = _shape(matrix, sha_sid)
sha_fields = [name for name, domain in sha_shape["fieldDomains"].items() if domain.get("pattern") == "^[0-9a-f]{64}$"]
assert len(sha_fields) == 6
for name in sha_fields:
    assert re.fullmatch(r"[0-9a-f]{64}", positives[sha_sid][name])
    probe = copy.deepcopy(positives[sha_sid])
    probe[name] = "x"
    assert _match_sets(matrix, probe) == {"repository": [], "independent": []}

eligible = copy.deepcopy(positives["SUCCESS_VALID"])
eligible["outcome"] = "BUILD_SUCCESS_FREEZE_BLOCKED_BY_PARKED_FIXTURE_REPAIR"
eligible["freeze_disposition"] = "FREEZE_BLOCKED_BY_PARKED_FIXTURE_REPAIR"
eligible["blocking_component"] = "CVF_CORE_REFRESH_CONFORMANCE_FIXTURE_REPAIR"
eligible["blocking_observation_state"] = "AUTHORIZATION_REREVIEW_CHANGES_REQUIRED"
parked = copy.deepcopy(positives["BUILD_SUCCESS_FREEZE_BLOCKED_BY_PARKED_FIXTURE_REPAIR_VALID"])
parked["outcome"] = "SUCCESS"
parked["freeze_disposition"] = "FREEZE_ELIGIBLE_IF_INDEPENDENT_REVIEW_ACCEPTS"
parked.pop("blocking_component")
parked.pop("blocking_observation_state")
correlated = [_match_sets(matrix, eligible), _match_sets(matrix, parked)]
assert correlated == [{"repository": [], "independent": []}, {"repository": [], "independent": []}]

result = {
    "adapterIdentity": "CVF_CORE_REFRESH_TARGET_REBASE_0281E93_READ_ONLY_P0_ADAPTER_V1",
    "familyId": family,
    "matrixCanonicalDigest": digest,
    "exclusivePositives": "8/8",
    "generatedOracleMutations": "1257/1257",
    "oracleExactSet": True,
    "mutationCountByShape": shape_counts,
    "mutationCountByOperator": operator_counts,
    "temporalJudgments": "40/40",
    "temporalAccepted": 38,
    "temporalRejected": 2,
    "shaPatternWitnesses": "6/6",
    "literalXProbesRejectedByBothSurfaces": "6/6",
    "correlatedOutcomeSelectionJudgments": "4/4",
    "validatorSurfaces": ["repository", "independent"],
    "terminalDisposition": "PASS",
}
print(json.dumps(result, sort_keys=True, separators=(",", ":")))
```
`PYTHON-PAYLOAD-END`

The exact invocation is the PowerShell sequence below. `$cvfP0` must contain
exactly the payload bytes above; it may be populated in memory from the Work
Order, but may not be written to a file. Replace
The invocation below pins that same literal payload digest.

```powershell
$cvfP0Bytes = [System.Text.UTF8Encoding]::new($false).GetBytes(($cvfP0 -replace "`r`n", "`n"))
$cvfP0Sha256 = [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($cvfP0Bytes)).ToLowerInvariant()
if ($cvfP0Sha256 -ne "0cd29a56f7186a5c030aae8d365d3f778d787d27a6797eab6e12226639bdb925") { throw "P0 payload hash mismatch" }
$env:PYTHONDONTWRITEBYTECODE = "1"
python -B -c $cvfP0
if ($LASTEXITCODE -ne 0) { throw "P0 adapter failed" }
```

P0 performs only allowlisted reads and in-memory computation, creates no
directory/file, emits exactly one canonical JSON object to stdout and performs
no network/provider/credential/database action. Stdout must remain in memory
until section 6 permits evidence-directory creation. PASS requires fresh
`8/8`, `1257/1257` exact generated/oracle set equality and rejection by both
validators, `40/40` temporal judgments (`38/2`), six valid lower-case 64-hex
witnesses, literal `"x"` rejected for each of the six fields by both surfaces,
and `4/4` correlated BUILD-success relabel judgments rejected. The parked
fixture-specific top-level `run` must not be called.

## 5. Zero-effect preflight and frozen preimages

Before evidence-directory creation, network, Core movement, root write, pin
edit or binding write, the implementation worker must prove and retain in
memory:

1. exact resolved containers in section 2 with no symlink/junction/reparse
   escape, expected remote and backup containment;
2. clean old Core and exact old manifest/AGENTS/binding pins; local old/target
   objects; local `origin/main ==` frozen target; exact `0/6` ancestry without
   fetch; project staged count zero;
3. all phase, policy, tool, profile, matrix, pin, registry and source hashes in
   sections 2-4; P0 PASS from the exact payload;
4. all six section-6 future paths absent and collision-free;
5. recoverable preimages for old Core, all 17 section-7 root paths, the two pin
   carriers, nine shared carriers and ignored binding; each path is recorded
   as `PRESENT` with raw bytes/SHA-256 or `ABSENT`;
6. exact byte hashes for the three parked P4-E artifacts:
   `SESSION/handoffs/P4E_IDENTITY_CONVERSATION_ROUTING_2026-08-29.md`,
   `docs/decisions/INTAKE_2026-08-29_P4E_IDENTITY_CONVERSATION_ROUTING.md` and
   `docs/decisions/DESIGN_2026-08-29_P4E_IDENTITY_CONVERSATION_ROUTING.md`;
7. allowlisted hashes for every accepted lineage artifact in section 2, all
   attempt-1/attempt-2 receipt-return-review artifacts, and the parked
   fixture-repair and rejected protocol-exception DESIGN/review artifacts; and
8. zero protected-assessment contacts and no broad untracked inventory.

The preimage manifest must bind resolved path, containment root, state,
raw SHA-256 where present, restoration source and restoration order. It must
also record immutable hashes for prior backups, failed Core replacements and
failed-root deltas without modifying, moving or reinterpreting them.

Any false, unreadable, changed or ambiguous predicate selects matrix-owned
`ZERO_EFFECT_PREFLIGHT_REFUSAL`. That outcome creates none of the six attempt-3
paths and performs no doctor, fetch, Core/root/pin/binding/continuity effect.

## 6. Collision-free attempt-3 evidence lifecycle

All six paths must be absent at preflight:

1. `D:\UNG DUNG AI\TOOL AI 2026\CVF-Workspace\_cvf-core-backups\CVF-CORE-REFRESH-TARGET-REBASE-0281E93-ATTEMPT-3-EVIDENCE`;
2. `docs/decisions/CVF_CORE_REFRESH_ROOT_EFFECTS_2026-08-30_0281E93_ATTEMPT_3.json`;
3. `docs/decisions/CVF_CORE_REFRESH_WORKER_RETURN_2026-08-30_0281E93_ATTEMPT_3.md`;
4. `docs/decisions/CVF_CORE_REFRESH_COMPLETION_REVIEW_2026-08-30_0281E93_ATTEMPT_3.md`;
5. `docs/decisions/CVF_CORE_REFRESH_REVIEW_TARGET_MOVEMENT_ROLLBACK_2026-08-30_0281E93_ATTEMPT_3.json`; and
6. `docs/decisions/CVF_CORE_REFRESH_REVIEW_TARGET_MOVEMENT_REREVIEW_2026-08-30_0281E93_ATTEMPT_3.md`.

After P0 and preservation pass, the worker may create path 1 and later paths
2-3. The root-effects JSON is the semantic receipt and worker Markdown is its
summary; neither self-hashes nor cross-hashes. The completion reviewer alone
creates path 4 and owns final hashes of paths 2-3 without self-hashing. A
conditional repair worker alone creates path 5, which does not self-hash. The
terminal rereviewer alone creates path 6 and owns hashes of every readable
prior attempt-3 artifact without self-hashing or depending on future bytes.

Attempt-1, attempt-2, fixture-repair and protocol-exception artifacts and all
retained failure states are immutable.

## 7. Exact workspace-root and downstream ceilings

The reconciler workspace-root ceiling is this ordered set of exactly 17 paths:

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

Each path receives exactly one `CREATE`, `UPDATE`, `DELETE` or `NO_CHANGE`
observation. Success and complete rollback require `17/17`. Originally absent
paths return to absence on rollback. No other workspace-root effect is
permitted; backups, failed replacements and failed-root deltas are retained.

The initial implementation worker's tracked downstream ceiling is exactly 13
paths: two pin carriers, nine shared carriers and two worker artifacts.

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

Ignored `.cvf/local-binding.json` is the sole additional local downstream
effect. Every other downstream path is byte-protected during BUILD, including
this Work Order; the accepted phase/review/SPEC/matrix/pin/registry artifacts;
fixture source/tests/matrix/pin/receipts; prior attempts; protocol-exception
artifacts; P4-E artifacts; catalog; product/runtime; and database files.

The completion reviewer has a one-path tracked ceiling: path 4 in section 6.
After immutable `REVIEW_TARGET_MOVEMENT`, the conditional repair worker may
mutate only the 11 pre-existing pin/shared paths above, create only path 5,
and restore/regenerate the ignored binding: at most 12 tracked paths plus one
ignored local effect. Paths 2-4 remain immutable. The terminal rereviewer may
create only path 6.

## 8. Ordered BUILD command graph, target checkpoints and network prefix

Only after exact recorded external-effect approval, the implementation worker
may execute from the project root:

```text
powershell -ExecutionPolicy Bypass -File "D:\UNG DUNG AI\TOOL AI 2026\CVF-Workspace\.Controlled-Vibe-Framework-CVF\scripts\update_cvf_workspace_public_core.ps1" -WorkspaceRoot "D:\UNG DUNG AI\TOOL AI 2026\CVF-Workspace"
```

The reconciler is invoked exactly once. Immediately after return and before
pin edit/initializer, record transcript, exit, backup/replacement paths, all
17 root observations, remote, cleanliness, HEAD and `origin/main`. Continue
only if exit is zero and clean
`HEAD == origin/main == 0281e93bab4a75083973eb7242fd2bc8f65055d3`.

Then use a scoped `apply_patch` to replace exactly one old full pin at
`.cvf/manifest.json.cvfCoreCommit` and exactly one old full pin in the generated
`AGENTS.md` `CVF Commit` header. Parse both back to the frozen target and
record one pin-bridge checkpoint. No other edit is allowed before invoking:

```text
powershell -ExecutionPolicy Bypass -File "D:\UNG DUNG AI\TOOL AI 2026\CVF-Workspace\shift-operations-workspace\scripts\initialize_cvf_clone.ps1"
```

The initializer is invoked exactly once. The only successful worker Git
network sequence is exactly three ordered operations:

```text
P1 = RECONCILER_CLONE
P2 = INITIALIZER_FETCH
P3 = INITIALIZER_DOCTOR_FETCH
```

Before P1, the worker rechecks local frozen target. Immediately after P1 it
checks replacement HEAD/ref as above. Before P2 it checks the target object
and both pins. The initializer's doctor may move `origin/main`; therefore
initializer exit zero is not success until the post-P3 checkpoint proves a
clean five-way equality:

```text
Core HEAD == Core origin/main == manifest pin == AGENTS pin == binding pin
          == 0281e93bab4a75083973eb7242fd2bc8f65055d3
```

The worker records only the actually executed ordered prefix on failure. No
manual fetch, direct checkout, custom clone, overlay,
`-UpdateProjectManifests`, pending-backup override, alternate remote,
credential helper, separate worker doctor, retry or in-attempt retarget is
permitted.

## 9. Failure classification and worker-time rollback

Every failure maps to the matrix's exact temporal pair and one primary class:

- `TARGET_DRIFT`: any advertised/local/cloned/doctor-observed target differs;
- `TOOL_OR_EFFECT_DRIFT`: frozen tool/blob/tree/profile/policy/source changes;
- `PREFLIGHT_REFUSAL`: containment, collision, hash, pin, ancestry, staged,
  P0, preimage, protected or fixture predicate fails before start;
- `RECONCILIATION`: reconciler/P1 or immediate replacement checkpoint fails;
- `PIN_BRIDGE`: scoped two-pin replacement or parse-back fails;
- `DOWNSTREAM_SYNCHRONIZATION`: initializer/P2/P3, five-way checkpoint,
  deterministic gate or evidence finalization fails;
- `UNAUTHORIZED_EFFECT`: any undeclared command/path/network/credential or
  protected-state contact occurs; and
- `ROLLBACK_INCOMPLETE`: any containment/preservation/restoration/verifier/
  failure-continuity step cannot be honestly completed.

After any post-start failure, the worker first contains and preserves the
observed failure and failed replacement, then restores from frozen preimages
in this order: old Core; 17 roots; two pins; nine shared carriers; ignored
binding. It may run at most one exact rollback-verifier doctor:

```text
powershell -ExecutionPolicy Bypass -File "D:\UNG DUNG AI\TOOL AI 2026\CVF-Workspace\.Controlled-Vibe-Framework-CVF\scripts\check_cvf_workspace_agent_enforcement.ps1" -ProjectPath "D:\UNG DUNG AI\TOOL AI 2026\CVF-Workspace\shift-operations-workspace"
```

The worker records that doctor's fetch and `origin/main` before/after, writes
truthful failure evidence and stops. Complete rollback requires exact
`17/17`, `2/2`, `9/9`, `1/1`, staged zero and old Core/manifest/AGENTS/binding
equality. An incomplete rollback records only observable states and never
fabricates unavailable Core/pin hashes, P4-E preservation, staged-zero or
unreadable evidence hashes. There is no retry or retarget under any class.

## 10. Reviewer doctor and conditional movement rollback

A distinct `INDEPENDENT_COMPLETION_REVIEWER` may execute the exact doctor in
section 9 at most once in REVIEW. It must record command and doctor-script
hash, network window, exit code, public/local target before/after and all ref
movement. It creates only section-6 path 4 and never repairs.

If reviewer fetch leaves `origin/main` at the frozen target, review continues
against the applicable worker outcome. If it moves away, the reviewer creates
immutable `REVIEW_TARGET_MOVEMENT`, records the observed target and stops. It
must not repair, retarget, rerun doctor or claim success.

Only after that immutable movement review may a distinct `REPAIR_WORKER`
restore old Core, 17 roots, two pins, nine shared carriers and binding from the
BUILD preimages. It must never invoke the reconciler, initializer or a new
target bridge. It may run the section-9 doctor once only as its rollback
verifier, records before/after ref movement, creates only the conditional JSON
and stops. A distinct `INDEPENDENT_COMPLETION_REREVIEWER` then owns path 6 and,
if separately authorized for its role window, at most one exact doctor. Role
ceilings and immutable hash ownership remain those in sections 6-7.

## 11. Invariant-family outcome mapping and exact counters

Applicability is `TRIGGERED`. Complete the proof fields from
`docs/templates/INVARIANT_FAMILY_PROOF.md` using:

- family id:
  `CVF-CORE-REFRESH-TARGET-REBASE-0281E93-OUTCOMES-2026-08-30`;
- sole semantic owner:
  `docs/cvf/invariants/cvf-core-refresh-target-rebase-0281e93-outcomes-2026-08-30.json`;
- canonical digest:
  `e39de7e9ed3199ec8f9033b1c90af9eca993655470f675a0ed3ae93846dbe45c`;
- machine consumer:
  `docs/specs/cvf_core_refresh_target_rebase_0281e93_2026_08_30_invariant_pin.py`;
- adapter identity: section 4; mutation exclusions: `NONE`; and
- evidence tests: `tests/unit/test_invariant_family_contract.py` and
  `tests/integration/test_invariant_family_repository_guard.py`.

The matrix alone owns required/forbidden/conditional fields, domains,
relations, exact failure-stage/network-prefix pairs, rollback-stage/verifier
pairs, evidence lifecycle and these eight outcome ids:

1. `ZERO_EFFECT_PREFLIGHT_REFUSAL`;
2. `SUCCESS`;
3. `BUILD_SUCCESS_FREEZE_BLOCKED_BY_PARKED_FIXTURE_REPAIR`;
4. `FAILURE_ROLLED_BACK`;
5. `FAILURE_ROLLBACK_INCOMPLETE`;
6. `REVIEW_TARGET_MOVEMENT`;
7. `REVIEW_TARGET_MOVEMENT_ROLLED_BACK`; and
8. `REVIEW_TARGET_MOVEMENT_ROLLBACK_INCOMPLETE`.

Consumers must not restate or weaken matrix field grammar. Each receipt/review
projection matches exactly one shape. The operational fixture status is copied
into `fixture_freeze_gate_status`; the matrix equality and status const select
the only permitted BUILD-success outcome. Current
`AUTHORIZATION_REREVIEW_CHANGES_REQUIRED` selects the freeze-blocked outcome,
not unrestricted `SUCCESS`.

Exact non-semantic execution ceilings remain: root `17`; initial worker
tracked `13`; worker evidence creates `2`; ignored binding `1`; successful
network prefix `3`; reconciler/pin bridge/initializer `1/1/1`; provider calls
`0`; reconciliation retries `0`; self/cross hashes `0/0`; protected contacts
`0`; complete rollback restores `17/2/9/1`; conditional repair mutable
carriers `11`, JSON create `1`, tracked ceiling `12`, ignored effect `1`;
reviewer doctor at most `1` in its own window. The exact matrix controls which
of these counters/fields is required or forbidden for each outcome.

Worker and reviewer must freshly recompute P0 `8/1257/40/6/4`; historical or
SPEC-review counts are not evidence. A failed matrix/P0 gate cannot be waived
into success.

## 12. Roles, deterministic gates and evidence

Role windows are non-overlapping:

- `ORCHESTRATOR` records gates/authority and routes work; does not implement or
  self-approve.
- `WORK_ORDER_AUTHOR` owns only this document and grants no effect.
- `INDEPENDENT_AUTHORIZATION_REVIEWER` owns only the authorization review.
- `IMPLEMENTATION_WORKER`, after exact approval only, owns P0, preimages,
  initial graph, worker-time rollback and worker artifacts.
- `INDEPENDENT_COMPLETION_REVIEWER`, conditional `REPAIR_WORKER`, and
  `INDEPENDENT_COMPLETION_REREVIEWER` must be distinct from one another and
  from the implementation worker.
- `CLOSER/SESSION_SYNC_STEWARD` acts only after an accepted terminal review.
- `COMMIT_STEWARD` is inactive without separate post-closure authority.

Applicable deterministic commands include:

```text
python scripts/check_session_state.py
python scripts/check_project_knowledge.py
python scripts/check_invariant_families.py --json
python -m pytest -q tests/unit/test_invariant_family_contract.py tests/integration/test_invariant_family_repository_guard.py
python scripts/generate_catalog.py --check
python scripts/check_file_size.py
```

The exact section-4 P0 command is additional. JSON must duplicate-key parse;
session/mirror, Project Knowledge, invariant family, catalog, file size,
role-scoped tracked diff and staged-zero must be checked. Evidence records
exact command, working directory, ordering, start/end, exit and retained
output. The inherited fixture focused baseline remains separately disclosed
as `28 passed, 2 skipped, 7 failed`; it is not repaired here and no result may
be called unrestricted “all tests pass.”

Completion review independently verifies the accepted hashes, P0 payload,
raw positive per outcome, generated/oracle exact set, both validators,
correlated probes, temporal pairs, SHA probes, command/network transcripts,
17-root accounting, role-specific downstream ceilings, preimages, five-way
target or honest rollback state, evidence ownership, fixture/P4-E/protected
preservation and every prohibited-effect counter.

## 13. Stop conditions, commit ownership and claim boundary

Stop on target, remote, ancestry, phase, role, policy, tool, profile, matrix,
pin, P0 payload/source or fixture drift; collision; containment/reparse or
preimage failure; strict-surface/oracle disagreement; unexpected command,
path or network effect; credential need; protected-state contact; broad
untracked inventory; fixture repair need; failed restore; unreadable evidence;
role overlap; or need for product/runtime/database, install, deployment,
release, commit or push effect. Stop never grants widening, retry or retarget.

Prohibited effects are exact zero: provider/mock calls, credential reads,
dependency installs, product changes, database actions, deployments, releases,
commits, pushes, manual Git network operations, reconciliation retries,
protected-assessment contacts and broad untracked inventories. The sanctioned
script-internal Git operations and role-owned doctors are counted separately
under sections 8-11.

No commit or push is authorized by this document, BUILD approval or terminal
review. Only a later accepted FREEZE disposition may activate a separately
named `COMMIT_STEWARD`; commit ownership, exact changed set, message and push
authority must be recorded separately. Historical commits may not be amended,
squashed, rewritten or force-pushed.

P4-E remains byte-protected at `DESIGN_REVIEW_PASS`; XR1 debt remains open;
fixture repair remains parked. A later accepted closure may prove only
deterministic public-Core freshness and pin reconciliation to exact
`0281e93...` inside this boundary. It does not prove CVF controls AI/agent or
provider behavior, arbitrary-untracked absence, downstream adoption of the
256-path Core delta, fixture closure, P4-E implementation, XR1 repair,
database behavior, deployment or production readiness. Any AI-governance
claim requires separate real-provider evidence; mock output is never proof.

## 14. Independent authorization review and next move

The independent authorization reviewer may create exactly one artifact:

`docs/decisions/AUTHORIZATION_REVIEW_2026-08-31_CVF_CORE_REFRESH_TARGET_REBASE_0281E93.md`

The reviewer must recompute this Work Order's SHA-256, all bound artifact/tool/
profile/source hashes and locations; verify the exact P0 payload and fresh
`8/1257/40/6/4` results; complete the invariant-family proof; inspect matrix
outcome ownership; and verify all commands, targets, checkpoints, preimages,
evidence paths, ceilings, rollback roles, stop rules, prohibited effects,
commit boundary and claim boundary. Findings and waivers must be explicit.

Only `AUTHORIZATION_REVIEW_PASS` with findings/waivers resolved may route to
the ORCHESTRATOR for the separate exact external-effect decision. Even then,
BUILD external-effect authority remains
`NOT_GRANTED_BY_THIS_DOCUMENT` until explicit approval of this exact Work
Order path/SHA, old pin, target and enumerated external-effect graph is
recorded. No doctor/fetch/reconcile, BUILD, commit or push is authorized now.
