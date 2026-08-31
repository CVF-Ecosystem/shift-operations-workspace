# DESIGN — CVF Public-Core Exact-Target Rebase 0281e93 — Attempt 4

- Tranche: `CVF-CORE-REFRESH-TARGET-REBASE-0281E93-ATTEMPT-4-2026-08-31`
- Phase: `DESIGN`
- Risk: `R2`
- Status: `READY_FOR_INDEPENDENT_DESIGN_REREVIEW`
- Active role: `REPAIR_WORKER`
- Repaired review findings: `DR4-F1`, `DR4-F2`, `DR4-F3`, `DR4-F4`
- Accepted INTAKE SHA-256:
  `83261bd4186e2aac0b16962332c3f8691c2ef9777b4493ff831ba856bd9dba2f`
- INTAKE review SHA-256:
  `d4f6c530db95f1d8d19c3c867107157cc3f0a62b12a31bb31613801b427a6293`
- Old Core/pin:
  `a7a797d7111be472ef2cbd928cbeffc70ccb6bc6`
- Frozen proposed target:
  `0281e93bab4a75083973eb7242fd2bc8f65055d3`
- Public remote:
  `https://github.com/Blackbird081/Controlled-Vibe-Framework-CVF.git`
- BUILD external-effect authority: `NOT_GRANTED`

## 1-4. Controlling repair for DR4-F1 through DR4-F4

This section replaces the original sections 1-4 rejected by independent
review. Those rejected contracts have been removed. If any later sentence
conflicts with this section, this section controls and the conflict is a
DESIGN-review failure rather than permission to choose the broader reading.

### 1. Separate phase-valid carrier prerequisite (DR4-F1)

Attempt 4 does not author executable carrier bytes. A separate
zero-external-effect carrier tranche,
`CVF-CORE-REFRESH-ATTEMPT-4-CARRIER-2026-08-31`, must traverse its own full
`INTAKE -> DESIGN -> SPEC -> WORK_ORDER -> BUILD -> REVIEW -> FREEZE` chain.
Its implementation BUILD ceiling is exactly:

```text
scripts/cvf_core_refresh_target_rebase_0281e93_attempt_4_carrier.ps1
tests/cvf/test_cvf_core_refresh_target_rebase_0281e93_attempt_4_carrier.py
```

The `.ps1` is implementation source and the `.py` is its static, dispatcher,
call-graph, mutation-corpus and no-effect contract test. The carrier
`WORK_ORDER_AUTHOR` owns only its Work Order. A distinct
`IMPLEMENTATION_WORKER` may create the two implementation paths only after
that exact Work Order passes independent authorization review. Carrier BUILD
has no Core, workspace-root, downstream-pin, binding, continuity, attempt-4
rebase lifecycle, network, provider, fixture, product/runtime/database,
install, deployment, release, commit or push authority.

The carrier tranche's governance changed-set is separately phase-owned and
limited to these exact artifact classes: one INTAKE and review; one DESIGN
and review; one SPEC, invariant matrix, static pin, registry entry and review;
one Work Order and authorization review; the two BUILD paths plus one worker
return; one completion review; and one carrier handoff plus only the bounded
canonical continuity/index/status records required at FREEZE. Its future Work
Order must turn those classes into exact paths before carrier BUILD. No phase
author may modify an artifact owned by another phase.

The carrier is not eligible for rebase use until independent completion
review passes and carrier FREEZE publishes the exact raw path/hash of both
BUILD files. Attempt 4 remains parked until that exact prerequisite is
reviewed and frozen. Only a later explicit attempt-4 phase transition may
bind the frozen carrier at:

`scripts/cvf_core_refresh_target_rebase_0281e93_attempt_4_carrier.ps1`

The rebase Work Order may authorize activation of those frozen bytes but may
not create, patch, copy, translate, regenerate or reinterpret them. Its BUILD
ceiling remains section 8's exact 17 workspace-root observations, 13
downstream paths and ignored binding. The frozen carrier and test are
protected preimages, never rebase changed-set members.

The carrier prerequisite itself cannot open from this repair. Independent
attempt-4 DESIGN rereview must first accept this exact DESIGN hash; the
ORCHESTRATOR may then separately record authority to open the carrier INTAKE.

### 2. Acyclic mode-specific artifact/hash graph (DR4-F2)

The controlling graph is:

```text
frozen carrier + frozen carrier completion review
  -> final rebase SPEC/matrix/pin/review
  -> final rebase Work Order
  -> ParseOnly/DryRun authorization review
  -> separate external-authority decision
  -> Execute invocation/worker receipt
  -> completion review
```

The frozen carrier contains no rebase Work Order, authorization-review or
external-authority hash. The final rebase Work Order contains the carrier
path/hash and all accepted pre-authorization lineage hashes. `ParseOnly` and
`DryRun` bind only artifacts already finalized before the authorization
review: frozen carrier path/hash; final Work Order path/hash; accepted SPEC,
matrix, pin and SPEC-review path/hash; old pin; target; public remote; exact
roots; and execution id. Their canonical output marks
`AuthorizationReviewPath`, `AuthorizationReviewSha256`,
`ExternalAuthorityPath` and `ExternalAuthoritySha256` as
`DEFERRED_EXECUTE_ONLY`. Rehearsal therefore does not claim to validate
future bytes.

The finalized authorization review contains carrier and Work Order hashes,
accepted pre-authorization hashes, exact ParseOnly/DryRun tuples and their
results. A later external-authority decision is a separate immutable path;
its bytes contain carrier, Work Order and authorization-review path/hash plus
the exact Execute tuple, effect ceilings, P1/P2/P3 network prefix and assigned
worker. It does not contain its own hash. Execute receives both the finalized
authorization-review path/hash and external-authority path/hash. The worker
externally recomputes the raw hashes of carrier, Work Order, authorization
review and external-authority decision before invocation; the carrier
recomputes all four before effect. No path-only identity, self-hash or
future-byte dependency is permitted.

### 3. Raw-token dispatcher and exact tuples (DR4-F3)

The frozen carrier has no PowerShell `param(...)` block, parameter aliases,
pipeline binding or positional binder. Its first executable operation copies
the unbound `$args` string array into an in-process raw-token dispatcher.
Native PowerShell semantic parameter binding therefore never receives the
carrier options; original option spellings are observed before abbreviation,
alias, positional or coercion behavior can occur. The only host form is:

```text
pwsh.exe -NoLogo -NoProfile -NonInteractive -File <exact-carrier-path> <exact-token-tuple>
```

The full case-sensitive option surface, in canonical order, is exactly:

```text
--Mode
--ProjectRoot
--WorkspaceRoot
--CoreRoot
--BackupRoot
--OldPin
--TargetPin
--PublicRemote
--CarrierSha256
--WorkOrderPath
--WorkOrderSha256
--SpecPath
--SpecSha256
--MatrixPath
--MatrixSha256
--PinPath
--PinSha256
--SpecReviewPath
--SpecReviewSha256
--AuthorizationReviewPath
--AuthorizationReviewSha256
--ExternalAuthorityPath
--ExternalAuthoritySha256
--ExecutionId
```

Every option is followed by exactly one string token. Flags, combined tokens
and implicit booleans do not exist. `--Mode` accepts exactly one case-
sensitive value: `ParseOnly`, `DryRun` or `Execute`. Exact tuples are:

- `ParseOnly`: the canonical prefix `--Mode` through `--CarrierSha256`, and
  no later option;
- `DryRun`: `--Mode` through `--SpecReviewSha256`, followed by
  `--ExecutionId`, in the displayed relative order; and
- `Execute`: all displayed options in exact order.

Before any mode logic, the dispatcher rejects missing values, odd token
count, duplicate names, reordered names, unknown names, prefix/abbreviated or
case-folded names, aliases, positional tokens, `name=value`, switch syntax,
arrays, expression/scriptblock-shaped tokens, coercible non-canonical values
and any extra token. P0-B owns a frozen adversarial corpus with, for every
option, missing-name, missing-value, duplicate, reorder, abbreviation,
case mutation, alias-like, positional, `name=value`, extra-token and coercion-
shaped cases; it also covers every invalid Mode and every cross-mode missing
or forbidden option. The carrier test and attempt-4 matrix freeze corpus ids,
expected refusal codes, count and digest.

Value semantics are exact: `OldPin`, `TargetPin` and every SHA are lowercase
full hex; public remote and execution id equal frozen literals; every path is
absolute, normalized, contained and reparse-safe; no value comes from a
profile, alias, interpolation, ambient branch, temporary file, credential
store or authority-bearing environment variable.

### 4. Exact callable allowlists, call graph and zero-network contract (DR4-F4)

`ParseOnly` returns canonical JSON for dispatcher/schema/parse results and
the four deferred Execute-only fields. `DryRun` performs every pre-effect
decision possible from its pre-authorization tuple and returns the same
explicit deferrals; it stops before evidence creation or any mutating/network
boundary.

Per-mode callable allowlists are closed:

- **ParseOnly in-process:** raw dispatcher; `System.IO.Path` normalization/
  containment; `System.IO.File.ReadAllBytes`; `System.Security.Cryptography.
  SHA256`; PowerShell `Language.Parser.ParseFile`; ordered dictionary/list/
  string primitives; and `System.Text.Json` canonical serialization. Reads
  are limited to the carrier and explicitly supplied roots. No child process
  is reachable.
- **DryRun in-process:** ParseOnly set plus `File.Exists`,
  `Directory.Exists`, `File.GetAttributes`, `File.ReadAllText`, reparse-point
  checks and exact allowlisted snapshot comparison. Its sole child executable
  is resolved, hash-pinned `git.exe`, invoked only through
  `Invoke-AllowlistedChild` with one of the literal argv forms below. Python
  and PowerShell children are not reachable.
- **Execute in-process:** DryRun set plus SPEC-named preimage, evidence-
  directory, atomic replacement and rollback functions. Child allowlist adds
  resolved hash-pinned `python.exe` for exact P0 commands and resolved hash-
  pinned `pwsh.exe` for exactly one reconciler and one initializer tuple; a
  conditional rollback-verifier doctor is a separately authorized exact
  `pwsh.exe` tuple. Section 9 remains the sole Execute network authority.

Every filesystem write/create/delete/move/copy API is forbidden in ParseOnly
and DryRun. Every mode forbids `Invoke-Expression`, `ScriptBlock.Create`,
dot-sourcing, module import, jobs, remoting, WMI/CIM, web cmdlets, sockets,
HTTP clients, package managers, credential APIs and broad environment reads.
Execute may read only non-secret environment keys individually named by SPEC;
none may supply an authority, path or hash.

The static verifier constructs a directed graph from every function AST and
the three literal mode-entry nodes. It fails on dynamic function names,
unresolved calls, invocation operator outside `Invoke-AllowlistedChild`,
dot-source, scriptblock creation/invocation, alias command, unqualified
external command or an edge absent from the mode matrix. Transitive closure
is computed separately by mode and every reachable .NET method, cmdlet and
native child must be in that mode's allowlist. The carrier test applies the
same rule to the retained AST. P0-B mutations inject one forbidden edge, API,
child or argv at a time and require deterministic refusal.

DryRun's complete native argv allowlist is:

```text
git --no-optional-locks -C <CoreRoot> remote get-url origin
git --no-optional-locks -C <CoreRoot> rev-parse --verify HEAD^{commit}
git --no-optional-locks -C <CoreRoot> rev-parse --verify origin/main^{commit}
git --no-optional-locks -C <CoreRoot> cat-file -t <OldPin-or-TargetPin>
git --no-optional-locks -C <CoreRoot> merge-base --is-ancestor <OldPin> <TargetPin>
git --no-optional-locks -C <CoreRoot> status --porcelain=v1 --untracked-files=no
git --no-optional-locks -C <ProjectRoot> diff --cached --name-only
```

No operand may begin with `-`, contain a URI scheme, UNC prefix, remote-helper
syntax or leave its declared root. The gateway denies every other executable
and Git verb/argument, including `fetch`, `pull`, `push`, `clone`,
`ls-remote`, `submodule`, `remote update`, `checkout`, `switch`, `reset`,
`clean`, `commit`, `merge`, `rebase`, `gc`, `maintenance`, `config`,
credential helpers, `--exec-path`, `-c`, URLs, proxies and transports. It uses
a closed child environment with `GIT_TERMINAL_PROMPT=0`,
`GIT_CONFIG_NOSYSTEM=1`, `GIT_OPTIONAL_LOCKS=0`, `GCM_INTERACTIVE=Never`,
empty askpass/proxy values and no credential variables.

Zero-network proof is deterministic: AST closure proves all child launches
pass the one gateway; canonical telemetry records every allowed child/argv;
the gateway increments and refuses `network_attempt_count` before launch for
anything outside the exact local-query set; direct network APIs are forbidden
by AST; and ParseOnly/DryRun must report `network_attempt_count=0`,
`network_child_count=0` and the exact local-child ledger. Any nonzero counter,
transport/credential-prompt marker, unclassified call or undeclared child is
a hard no-effect failure. This proof is required on the frozen carrier bytes
in carrier REVIEW and again in rebase authorization review.

## 5. Fresh local gates and P0

Authorization review and BUILD independently recompute, without fetch, the
current remote, clean Core state, old/target object types, local
`origin/main`, `0/6` ancestry, two downstream pins, ignored binding, staged
count, accepted lineage hashes, policy, selector and these tool identities:

| Surface | Required identity |
|---|---|
| Core reconciler raw / blob | `96ac0cce3bf9df5733ffe2c6f5a7850db0ccfdc4403daaa70fdb6981dc58196c` / `4b705c6bf7b10bda62520dca488ecb453a4f4945` |
| Core doctor raw / blob | `2410bbabf88f12581d2e34a71efe247fe9080ebb299a58eb6f9ff6a35818796b` / `2ad83efee05c738fec40aa1779929da07f3d1c8c` |
| Core new-workspace raw / blob | `7e5567c55026f3be44f11c924d44835d6fb98b1fb4268dfedf6453af89927032` / `5f311a1a1c8dc787c7b19011bf34c5a84fc773c7` |
| Core operation tree | `23fe8bd39ae102d3302d34de1d80208e2ef9bbb6` |
| Downstream initializer raw | `bb37b16256a693853bddfdbcb40c2f7211e6984a90a972da83899962fae209c8` |
| Active selector raw | `f51bacd206ec4e95b92f4f4479bc7c68ee605db3752d514ff3094bdff02dc855` |

The worker also freshly re-hashes the carrier before and after `ParseOnly`,
`DryRun`, P0 and every effect boundary. A target, ancestry, remote, tool,
policy, selector, carrier, Work Order, authority, parameter or effect-graph
change is fail-closed `TARGET_DRIFT` or `TOOL_OR_EFFECT_DRIFT`; no role may
refresh a hash, hotfix the carrier, retarget or retry in place.

P0 has two explicit layers before evidence-directory creation or effect:

- `P0-A` reruns the accepted exact-target conformance baseline on the
  immutable attempt-3 outcome matrix and pinned sources, requiring fresh
  `8/8`, `1257/1257`, `40/40`, `6/6` and `4/4` results on both validator
  surfaces; and
- `P0-B` validates the new attempt-4 family, exact carrier contract and all
  carrier-specific mutations against counts and digests frozen by the future
  SPEC and independently reviewed Work Order.

Neither layer calls the fixture-specific top-level `run`. A failed or
unavailable P0 layer is a zero-effect refusal, not permission to repair the
fixture or wrapper.

## 6. Preimages and preservation boundary

Before any external effect, the worker builds a complete in-memory preimage
manifest and only after P0 may persist it under the attempt-4 evidence
directory. Every item records resolved path, containment root, `PRESENT` plus
raw SHA-256 or `ABSENT`, restoration source, role owner and deterministic
restoration order. The manifest covers:

- old hidden Core, its remote/ref/cleanliness and recoverable backup;
- all 17 workspace-root targets in section 8;
- the two pin carriers and nine shared downstream carriers;
- ignored `.cvf/local-binding.json`;
- the retained carrier, Work Order, authorization review and accepted phase/
  matrix/pin artifacts;
- every attempt-4 future lifecycle path;
- all prior-attempt, fixture-repair and protocol-exception artifacts; and
- the three parked P4-E artifacts in section 12.

The carrier and protected artifacts are immutable during normal BUILD. Their
preimages exist to detect and, only if an authorized script unexpectedly
touches them, restore the exact prior bytes during containment. Such contact
is still `UNAUTHORIZED_EFFECT`, never success. Failure handling first
contains and preserves the observed failed replacement/transcripts/deltas,
then restores old Core, 17 roots, two pins, nine shared carriers, binding and
any actually moved protected carrier from the accepted preimages. Missing or
unreadable preimages cause zero-effect refusal before start; incomplete
restoration is reported honestly and never filled with invented values.

## 7. Collision-free attempt-4 lifecycle

The exact Work Order must prove all six execution/review paths absent and
contained before BUILD:

1. `D:\UNG DUNG AI\TOOL AI 2026\CVF-Workspace\_cvf-core-backups\CVF-CORE-REFRESH-TARGET-REBASE-0281E93-ATTEMPT-4-EVIDENCE`;
2. `docs/decisions/CVF_CORE_REFRESH_ROOT_EFFECTS_2026-08-31_0281E93_ATTEMPT_4.json`;
3. `docs/decisions/CVF_CORE_REFRESH_WORKER_RETURN_2026-08-31_0281E93_ATTEMPT_4.md`;
4. `docs/decisions/CVF_CORE_REFRESH_COMPLETION_REVIEW_2026-08-31_0281E93_ATTEMPT_4.md`;
5. `docs/decisions/CVF_CORE_REFRESH_REVIEW_TARGET_MOVEMENT_ROLLBACK_2026-08-31_0281E93_ATTEMPT_4.json`; and
6. `docs/decisions/CVF_CORE_REFRESH_REVIEW_TARGET_MOVEMENT_REREVIEW_2026-08-31_0281E93_ATTEMPT_4.md`.

After the separate carrier tranche has frozen, the exact rebase pre-BUILD
governance lifecycle must be collision-free:

- frozen carrier prerequisite:
  `scripts/cvf_core_refresh_target_rebase_0281e93_attempt_4_carrier.ps1`;
- frozen carrier test prerequisite:
  `tests/cvf/test_cvf_core_refresh_target_rebase_0281e93_attempt_4_carrier.py`;
- SPEC: `docs/specs/CVF_CORE_REFRESH_TARGET_REBASE_0281E93_ATTEMPT_4_2026-08-31_SPEC.md`;
- SPEC review: `docs/decisions/SPEC_REVIEW_2026-08-31_CVF_CORE_REFRESH_TARGET_REBASE_0281E93_ATTEMPT_4.md`;
- Work Order: `docs/work_orders/CVF_CORE_REFRESH_TARGET_REBASE_0281E93_ATTEMPT_4_2026-08-31_WORK_ORDER.md`;
- authorization review: `docs/decisions/AUTHORIZATION_REVIEW_2026-08-31_CVF_CORE_REFRESH_TARGET_REBASE_0281E93_ATTEMPT_4.md`; and
- DESIGN review: `docs/decisions/DESIGN_REVIEW_2026-08-31_CVF_CORE_REFRESH_TARGET_REBASE_0281E93_ATTEMPT_4.md`.

Worker JSON is the semantic receipt and worker Markdown its summary; neither
self-hashes nor cross-hashes. Completion review owns their final hashes and
does not self-hash. Conditional rollback JSON does not self-hash. Terminal
rereview owns all readable earlier hashes without depending on future bytes.
Attempt-1/2/3 paths remain immutable and are never scratch space.

## 8. Root and downstream ceilings

The reconciler workspace-root ceiling remains exactly these ordered 17 paths:

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

Each gets exactly one `CREATE`, `UPDATE`, `DELETE` or `NO_CHANGE`
observation; success and complete rollback require `17/17`. The initial
worker tracked downstream ceiling is exactly 13 paths: two pins, nine shared
carriers and two worker artifacts:

```text
.cvf/manifest.json
AGENTS.md
knowledge/manifest.json
IMPLEMENTATION_STATUS.json
SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json
SESSION/ACTIVE_SESSION_STATE.json
CVF_SESSION/ACTIVE_SESSION_STATE.json
SESSION/SESSION_MEMORY.md
SESSION/handoffs/CVF_CORE_REFRESH_TARGET_REBASE_0281E93_ATTEMPT_4_2026-08-31.md
docs/INDEX.md
docs/implementation/EXECUTION_ROADMAP.md
docs/decisions/CVF_CORE_REFRESH_ROOT_EFFECTS_2026-08-31_0281E93_ATTEMPT_4.json
docs/decisions/CVF_CORE_REFRESH_WORKER_RETURN_2026-08-31_0281E93_ATTEMPT_4.md
```

Ignored binding is the sole additional normal local downstream effect. The
carrier, Work Order, reviews, SPEC, matrix/pin/registry, fixture, prior
attempts, P4-E, catalog, product/runtime/database and unrelated governed
files are byte-protected. The completion reviewer creates only lifecycle path
4. After immutable reviewer target movement, a distinct repair worker may
restore the 11 pre-existing pin/shared carriers, binding and any specifically
recorded protected carrier unexpectedly moved by the authorized graph, and
create only path 5. The exact Work Order must enumerate this conditional
emergency ceiling; it cannot become ordinary edit scope. The rereviewer
creates only path 6.

## 9. Ordered BUILD and network graph

Only exact later authority may activate `Execute`. Its internal graph is:

1. revalidate target/tool/carrier/Work Order/authority/P0/preimages and freeze
   the pre-effect snapshot;
2. invoke the sanctioned old-Core reconciler exactly once;
3. capture its transcript and all 17 root observations, and continue only on
   zero exit plus clean `HEAD == origin/main == 0281e93...`;
4. apply one scoped replacement to `.cvf/manifest.json.cvfCoreCommit` and one
   to the generated `AGENTS.md` pin header, parse both back and record one pin
   bridge; and
5. invoke downstream `scripts/initialize_cvf_clone.ps1` exactly once, then
   require clean five-way equality among Core HEAD, Core `origin/main`,
   manifest, AGENTS and binding at the target.

The sole successful Git network prefix is ordered exactly:

```text
P1 = RECONCILER_CLONE
P2 = INITIALIZER_FETCH
P3 = INITIALIZER_DOCTOR_FETCH
```

Fresh target/tool/carrier checks occur immediately before P1, after P1,
before P2 and after P3. The actually executed prefix is recorded on failure.
No manual fetch, direct checkout, custom clone, overlay,
`-UpdateProjectManifests`, pending-backup override, alternate remote,
credential helper, separate worker doctor, retry, alternate carrier or
in-attempt retarget is permitted.

## 10. Failure, rollback and reviewer movement

Failure classes remain disjoint: `TARGET_DRIFT`, `TOOL_OR_EFFECT_DRIFT`,
`PREFLIGHT_REFUSAL`, `RECONCILIATION`, `PIN_BRIDGE`,
`DOWNSTREAM_SYNCHRONIZATION`, `UNAUTHORIZED_EFFECT` and
`ROLLBACK_INCOMPLETE`. The new attempt-4 matrix owns exact outcome shapes,
field presence, temporal/network-prefix pairs, carrier validation state and
rollback/verifier relations; prose consumers may not restate its grammar.

Every post-start failure preserves the failed state before restoration. The
worker may run at most one exact rollback-verifier doctor and records its
network/ref movement. Complete rollback requires exact old Core, `17/17`
roots, `2/2` pins, `9/9` shared carriers, `1/1` binding, unchanged carrier and
parked protection, and staged zero. There is one attempt only: no preflight
rerun after failure, reconcile retry, carrier hotfix, retarget or in-attempt
repair.

A distinct completion reviewer may run at most one exact doctor in REVIEW.
If it moves `origin/main`, the reviewer writes immutable
`REVIEW_TARGET_MOVEMENT` and stops without repair. A distinct
`REPAIR_WORKER` may restore only from BUILD preimages, never invoke the
reconciler/initializer or bridge a new target, and creates only path 5. A
distinct terminal rereviewer owns path 6. Each doctor window requires its own
explicit effect authority and exact before/after accounting.

## 11. Invariant-family applicability

Applicability is `TRIGGERED`: R2 attempt 4 couples retained carrier bytes,
mode-dependent required/forbidden effects, outcome-controlled receipt fields,
exact counters/temporal relations, two validator surfaces and the adjacent
attempt-3 wrapper failure.

SPEC must register a new collision-free family:

- family id:
  `CVF-CORE-REFRESH-TARGET-REBASE-0281E93-ATTEMPT-4-OUTCOMES-2026-08-31`;
- matrix path:
  `docs/cvf/invariants/cvf-core-refresh-target-rebase-0281e93-attempt-4-outcomes-2026-08-31.json`; and
- machine pin path:
  `docs/specs/cvf_core_refresh_target_rebase_0281e93_attempt_4_2026_08_31_invariant_pin.py`.

The matrix is the sole semantic owner of attempt-4 outcomes, carrier-mode
facts, evidence lifecycle, field grammar, counters and relations. SPEC review
freezes its canonical digest and P0-B counts. Work Order and reviews use
`docs/templates/INVARIANT_FAMILY_PROOF.md` by id/digest, without copying matrix
rules. The attempt-3 matrix remains immutable and independently supplies only
the P0-A regression baseline.

## 12. Fixture, P4-E and protected state

The inherited fixture baseline remains exactly `28 passed, 2 skipped, 7
failed`, status `AUTHORIZATION_REREVIEW_CHANGES_REQUIRED`. Attempt 4 may not
invoke its fixture-specific top-level run, repair or suppress it, alter its
source/tests/matrix/pin/receipts, or call BUILD success unrestricted
`SUCCESS`. The new matrix must preserve the freeze-blocked distinction while
that status remains open.

P4-E remains parked at `DESIGN_REVIEW_PASS`; its exact protected hashes are:

| Artifact | SHA-256 |
|---|---|
| `SESSION/handoffs/P4E_IDENTITY_CONVERSATION_ROUTING_2026-08-29.md` | `23ce2ae4c71e0db29c1d673baef0c1d269791524776f987466d7ad177514fe61` |
| `docs/decisions/INTAKE_2026-08-29_P4E_IDENTITY_CONVERSATION_ROUTING.md` | `a48e6f3a5fb2c1137608fb1c99a15f28cb6cbc98032bf9ac99fdf62b0aad9ac7` |
| `docs/decisions/DESIGN_2026-08-29_P4E_IDENTITY_CONVERSATION_ROUTING.md` | `2d0975a301a15c7b8a85eba121410391ddca2f067b16d9c5089d79edb9c397b9` |

XR1 historical-object debt stays unresolved. The protected operator
assessment remains excluded from open, read, hash, name, inventory, stage and
use. Broad downstream untracked inventory is prohibited. Product/runtime/
database, installation, deployment, release and unrelated catalog work remain
outside scope.

## 13. Roles and phase gates

- `ORCHESTRATOR` records authority and routes roles; it does not implement or
  self-approve.
- `DESIGN_AUTHOR` owns only this DESIGN.
- `INDEPENDENT_DESIGN_REVIEWER` owns only the DESIGN review.
- `SPEC_AUTHOR` owns requirements, the new matrix, registry entry and static
  pin only after an explicit DESIGN-to-SPEC transition.
- The separate carrier-tranche `WORK_ORDER_AUTHOR` owns only its Work Order;
  its distinct `IMPLEMENTATION_WORKER` owns exactly the two section-1 BUILD
  paths after authorization review, and its independent reviewer/closer owns
  carrier REVIEW/FREEZE.
- The rebase `WORK_ORDER_AUTHOR` owns only the rebase Work Order after SPEC
  review PASS. It references the exact frozen carrier path/hash and may not
  create or modify carrier implementation or test bytes.
- `INDEPENDENT_AUTHORIZATION_REVIEWER` owns parse/static/no-effect rehearsal
  and one review artifact; PASS does not itself grant BUILD.
- A distinct `IMPLEMENTATION_WORKER` acts only after exact external-effect
  approval and owns P0, preimages, execution, worker rollback and paths 1-3.
- `INDEPENDENT_COMPLETION_REVIEWER`, conditional `REPAIR_WORKER`, terminal
  `INDEPENDENT_COMPLETION_REREVIEWER`, `CLOSER`,
  `SESSION_SYNC_STEWARD` and any later `COMMIT_STEWARD` have non-overlapping
  windows. No commit steward is activated by this DESIGN.

DESIGN review PASS is required before SPEC; SPEC review PASS before Work
Order; authorization review PASS plus explicit exact external-effect approval
before BUILD; independent terminal review before FREEZE. No role or review
silently grants the next phase.

## 14. Verification, stop rules and claim boundary

Authorization review, worker and applicable reviewers run duplicate-key JSON,
session/mirror, Project Knowledge, invariant-family, P0-A/P0-B, catalog,
file-size, role-scoped tracked-diff and staged-zero gates. Every retained
result records exact command, directory, ordering, start/end, exit, stdout and
stderr. A historical result is not fresh evidence.

Stop on phase/role drift; any target, remote, ancestry, tool, selector,
policy, carrier, Work Order, authority, matrix, pin, P0 source or fixture
drift; parse/static/rehearsal failure; path collision; containment/reparse or
preimage failure; unexpected command/path/network effect; credential need;
protected-state contact; broad inventory; fixture repair need; unreadable
evidence; failed restore; or need for product/runtime/database, install,
deployment, release, commit or push. Stop does not grant widening, retry,
repair or retarget.

A later accepted closure may prove only deterministic public-Core freshness
and pin reconciliation to exact `0281e93...` within the enumerated boundary,
or an honestly reviewed refusal/rollback outcome. It cannot prove arbitrary
untracked absence, downstream adoption of the 256-path Core delta, fixture
closure, P4-E implementation, XR1 repair, AI/agent or provider governance,
database behavior, deployment or production readiness. No provider call is
required for this repository-maintenance DESIGN; mock output is not
governance proof.

## 15. DESIGN acceptance and next move

Independent DESIGN rereview must verify the separate phase-valid carrier
prerequisite and its exact two-path BUILD ceiling; the acyclic, mode-specific
hash graph; the raw-token dispatcher and exact three tuples; the per-mode
callable/child/argument allowlists, deterministic AST graph and zero-network
contract; authoring/activation separation; target/tool/P0 gates; preimages,
attempt-4 lifecycle paths, 17-root and downstream ceilings, P1/P2/P3 network
graph, rollback/reviewer movement, role gates, invariant-family trigger,
fixture/P4-E/protected preservation, stop rules and bounded claims. Findings
and waivers must be explicit.

Next governed move: independent DESIGN rereview only. The carrier prerequisite
cannot open until that rereview accepts this exact DESIGN hash and the
ORCHESTRATOR records a separate carrier-INTAKE transition. Attempt-4 SPEC,
Work Order, carrier authoring or execution, BUILD, doctor/fetch/reconcile,
Core/root/pin/binding/
continuity mutation, evidence-directory creation, fixture repair,
provider/credential use, installation, product/database change, deployment,
release, commit, push and P4-E SPEC remain unauthorized.
