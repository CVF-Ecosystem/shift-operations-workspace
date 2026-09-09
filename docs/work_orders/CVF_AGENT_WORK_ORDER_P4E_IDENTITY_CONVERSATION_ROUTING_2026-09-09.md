# CVF Agent Work Order - P4-E Identity Mapping And Conversation Routing
Memory class: governed-worker-dispatch
docType: work_order
Status: APPROVED_FOR_EXECUTION
Batch ID: P4E-IDENTITY-CONVERSATION-ROUTING
Risk ceiling: R2
Dispatch base head: e367bc996e6fceaff08d23af34c2d5d8dada0ded
dispatchBaseHead: e367bc996e6fceaff08d23af34c2d5d8dada0ded
Commit mode: WORKER_MUST_NOT_COMMIT
BUILD authority: GRANTED_BY_EXPLICIT_OPERATOR_DECISION_2026-09-09

## Dispatch Prompt Envelope

Role: IMPLEMENTATION_WORKER for `P4E-IDENTITY-CONVERSATION-ROUTING` under the
explicit operator authorization recorded after mechanical citation repair.

Canonical packet: `docs/work_orders/CVF_AGENT_WORK_ORDER_P4E_IDENTITY_CONVERSATION_ROUTING_2026-09-09.md`

Paired baseline: `docs/baselines/CVF_GC018_BASELINE_P4E_IDENTITY_CONVERSATION_ROUTING_2026-09-09.md`

Commit mode: WORKER_MUST_NOT_COMMIT.

executionBaseHead: WORKER_MUST_CAPTURE_AT_START.

Current-time note: artifact date is 2026-09-09; the worker must resolve current
HEAD, branch, origin, continuity, and source hashes again at execution start.

Do-not-misread note: APPROVED_FOR_EXECUTION authorizes only exact paths 15-80.
It does not authorize install, provider/live/network use,
database mutation outside disposable tests, deployment, staging, commit, push,
self-review, closure, Phase 5, XR1 repair, catalog migration, or repository
absorption.

Required first actions after authorization: read `WORKSPACE_RULES.md`,
`.cvf/manifest.json`, `.cvf/policy.json`, `AGENTS.md`, the active rule pack,
canonical continuity, this Work Order, its baseline, accepted SPEC/rereview,
all three matrices/pins, invariant proof template, and checker sources listed
below; capture `executionBaseHead`; verify empty staging; run the pre-
implementation gate; stop on any contradiction.

Return contract: create the exact worker return, run the ordered evidence, leave
all changes unstaged and uncommitted, release the explicit lane, and return
`COMPLETE_PENDING_REVIEW` or `BLOCKED_WITH_REASON`.

## Purpose

Implement the accepted P4-E v1 capability: durable provider-neutral external
identity linkage, two-human mapping confirmation, authorized route bindings,
and deterministic conversation placement for actor-neutral P4-C proposals.
The implementation must satisfy SPEC R1-R21 and AC-01-AC-16 without expanding
to customer/vessel authority, operational record creation, provider behavior,
deployment, or production-readiness claims.

## Scaffold Provenance Block

| Field | Value |
| --- | --- |
| scaffoldHelperCommand | `python governance/compat/build_dispatch_packet_scaffold.py --packet-kind generic-worker-dispatch --batch-id P4E-IDENTITY-CONVERSATION-ROUTING --title "P4-E Identity Mapping And Conversation Routing" --date 2026-09-09 --base e367bc996e6fceaff08d23af34c2d5d8dada0ded --commit-mode WORKER_MUST_NOT_COMMIT --stdout` |
| generatedProfile | generic-worker-dispatch plus WORKER_MUST_NOT_COMMIT no-commit worker profile |
| generatedSkeletonStatus | USED_AS_STARTING_POINT |
| manualEditsAfterScaffold | Replaced all placeholders; added exact 94-path ownership, accepted-source pins, ordered BUILD plan, invariant proof, R2 review gate, scaffold exclusions, executable AC-16 probe, and explicit secret-authority record ownership. |
| checkerReadAheadConfirmation | Work Order quality main/core/range/source/artifacts/lifecycle/tables; agent handoff; review cost; ADIF disclosure checkers were inspected before authoring. |
| docOnlyNewFields | `Carry-Forward Resolution`; `Secret-Authority Ownership`; these describe project requirements and do not create machine claims. |
| claimBoundary | Work Order authoring only; no implementation or runtime behavior is claimed. |

## Review Dispatch Convergence And Invocation Budget Control

Review-Dispatch Convergence Control: REQUIRED

dispatchKind: INITIAL
dispatchSurface: INTERNAL_AGENT
parentAssignmentId: P4E-IDENTITY-CONVERSATION-ROUTING
reviewRoundCount: 0
priorFindingSetDigest: NOT_APPLICABLE_INITIAL_DISPATCH
dependencyAuditDisposition: COMPLETE_INITIAL_ACCEPTANCE_MATRIX
reworkFindingDisposition: NOT_APPLICABLE_INITIAL_DISPATCH
newIndependentCriticalEvidence: NONE
regressionGuardDisposition: BASELINE_NEGATIVE_TESTS_PLANNED
cumulativeExternalInvocationCount: 0
externalInvocationCeiling: 0
usageAvailability: NOT_APPLICABLE_INTERNAL_AGENT
quotaAdmissionDisposition: NOT_APPLICABLE_INTERNAL_AGENT
nextDispatchDisposition: INITIAL_DISPATCH
rootCauseClusterId: NOT_APPLICABLE_INITIAL_DISPATCH
reworkGeneration: 0
consolidatedDefectClassSweep: COMPLETE_INITIAL_ACCEPTANCE_MATRIX
successorTrancheOpened: NO
implementationAutonomyDisposition: CONTRACT_AUTHORITY_EVIDENCE_OUTCOME_ONLY
preExecutionReviewAdmission: REQUIRED_TRIGGERED
preExecutionReviewTrigger: AUTHORITY_SCOPE_EXPANSION
nextRoutineReviewBoundary: PRE_EXECUTION_REVIEW
reviewerWorkBoundary: EVALUATE_RETURNED_EVIDENCE_NOT_RECREATE_IMPLEMENTATION

The trigger is the transition from accepted documentation to an R2 product
changed set spanning security, identity, persistence, and composition. The
independent reviewer evaluates this packet and its sources; the reviewer must
not recreate the implementation.

## Semantic Convergence Outcome

Standard: `docs/reference/semantic_convergence_control/CVF_SEMANTIC_CONVERGENCE_AND_ESCALATION_CONTROL_STANDARD.md` (private-provenance reference only; not present in this project working tree)

```json
{
  "schemaVersion": "cvf.semanticConvergenceControl.v1",
  "problemKey": "p4e-identity-conversation-routing-problem",
  "chainMode": "INITIAL",
  "chainOrdinal": 0,
  "predecessor": null,
  "blockerDelta": {
    "prior": ["SPEC_REVIEW_F1", "SPEC_REVIEW_F2", "SPEC_REVIEW_F3", "SPEC_REVIEW_F4", "SPEC_REVIEW_F5", "SPEC_REVIEW_F6", "SPEC_REVIEW_F7"],
    "resolved": ["SPEC_REVIEW_F1", "SPEC_REVIEW_F2", "SPEC_REVIEW_F3", "SPEC_REVIEW_F4", "SPEC_REVIEW_F5", "SPEC_REVIEW_F6", "SPEC_REVIEW_F7"],
    "retained": [],
    "new": [],
    "reopened": [],
    "current": []
  },
  "resolutionEvidence": {
    "SPEC_REVIEW_F1-F7": "docs/decisions/SPEC_REREVIEW_2026-09-09_P4E_IDENTITY_CONVERSATION_ROUTING.md#final-finding-matrix"
  },
  "counters": {
    "partialReadyClosures": 0,
    "reviewerScopeExpansions": 0,
    "sameClaimCorrections": 1,
    "nonDecreasingBlockerTransitions": 0
  },
  "claims": ["SPEC_REVIEW_PASS", "7_OF_7_FINDINGS_CLOSED", "WORK_ORDER_AUTHORING_ELIGIBLE"],
  "requiredDisposition": "CONTINUE_BOUNDED",
  "successorScope": "EXECUTABLE_IMPLEMENTATION"
}
```

## Worker Autonomy / No-Question Rule

After authorization, the worker shall repair allowed-scope checker or test
failures directly by reading the relevant source and preserving SPEC semantics.
Return to the ORCHESTRATOR only for a source contradiction, required path not
in the exact manifest, need for a dependency/install/external effect, matrix
drift, unresolved SQL atomicity, or another missing authority that makes safe
completion impossible. Do not request step-by-step implementation choices.

## ADIF Defect Registry Disclosure

Resolver query: taskClass=`implementation`, role=`IMPLEMENTATION_WORKER`, lifecyclePhase=`BUILD`

Returned defects: NONE_RETURNED

| Field | Value |
| --- | --- |
| Resolver command | `python governance/compat/run_adif_defect_resolver.py --task-class implementation --role IMPLEMENTATION_WORKER --lifecycle-phase BUILD --risk-ceiling HIGH --json` |
| Returned defect count | 0 |
| Returned defects | NONE_RETURNED |
| Disclosed defectIds | NONE |
| Dispatch impact | No matching defect packet was returned. Current direct controls remain mandatory. |

## Checker Source Read-Ahead Block

| Field | Value |
| --- | --- |
| applicableCheckersRead | `governance/compat/check_work_order_dispatch_quality.py`; its core, range, source, artifacts, lifecycle and tables modules; `governance/compat/check_agent_handoff_boundary.py`; `governance/compat/check_review_cost_control.py`; `governance/compat/check_adif_defect_registry_disclosure.py` |
| literalTokensReviewed | Dispatch Prompt Envelope; Source Verification Block; Negative Search And Collision Discipline; Intake Role Routing Decision; Reviewer Closure Conversion; Worker Return Packet Shape Contract; Agent Operation Trace Block; Delta Execution Claim Boundary Control Block; WORKER_MUST_NOT_COMMIT; EXPLICIT_LANE_HANDOFF; REQUIRED_TRIGGERED; PRE_EXECUTION_REVIEW |
| gateRunPurpose | Confirmation of a source-designed packet and exact literal shape, not first discovery. |
| claimBoundary | Structural read-ahead only; it does not prove SPEC fulfillment or application behavior. |

## Source Verification Block

| Claimed item | Claim type | Source file | Verified line/section | Verified path or symbol | Owning interface/function/schema | Disposition |
| --- | --- | --- | --- | --- | --- | --- |
| P4-E requirements and acceptance | normative contract | `docs/specs/P4E_IDENTITY_CONVERSATION_ROUTING_SPEC.md` | R1-R21; AC-01-AC-16 | SHA-256 `de3af4a90425ee70f8e285fc31e12774497f7a190b776beab3ed3d32fdc90618` | P4-E SPEC | ACCEPT |
| Independent SPEC pass | phase authority | `docs/decisions/SPEC_REREVIEW_2026-09-09_P4E_IDENTITY_CONVERSATION_ROUTING.md` | Disposition; final finding matrix | SHA-256 `e9c21bd7c5627a0529b4d15d5a1533bd834ec886d13002c77ecdaa2a8094c3cc` | independent SPEC rereviewer | ACCEPT |
| Accepted architecture | design authority | `docs/decisions/DESIGN_2026-08-29_P4E_IDENTITY_CONVERSATION_ROUTING.md` | complete file | SHA-256 `2d0975a301a15c7b8a85eba121410391ddca2f067b16d9c5089d79edb9c397b9` | P4-E DESIGN | ACCEPT |
| Mapping outcome grammar | invariant authority | `docs/cvf/invariants/p4e-mapping-action-outcomes.json` | complete file | SHA-256 `ea2af8122016a7b8ee10d9a8aa097f1b692a168a4914425172c555cd4d003e1a` | P4E-MAPPING-ACTION-OUTCOMES | ACCEPT |
| Identity outcome grammar | invariant authority | `docs/cvf/invariants/p4e-identity-resolution-outcomes.json` | complete file | SHA-256 `4ef64cf1f53633974b0e585018148a8f6bbe7a16ce4683329aa29d51c0000bdc` | P4E-IDENTITY-RESOLUTION-OUTCOMES | ACCEPT |
| Placement outcome grammar | invariant authority | `docs/cvf/invariants/p4e-placement-outcomes.json` | complete file | SHA-256 `fd351b6670292e82835b4ec34c270768174758a6d8a3f1558e4e4b3a8ec8cc56` | P4E-CONVERSATION-PLACEMENT-OUTCOMES | ACCEPT |
| Current proposal store to retire from production | implementation source | canonical project source: `apps/workspace-api/src/workspace_api/external_ingress/repository.py` | line 13 | `InMemoryExternalIngressRepository` | existing process-local repository | ACCEPT |
| Current ingress composition | implementation source | canonical project source: `apps/workspace-api/src/workspace_api/main.py` | line 41 | `include_router(external_ingress_router)` | Workspace API composition root | ACCEPT |
| Current sender verification seam | implementation source | canonical project source: `apps/integration-edge/src/integration_edge/verification/hmac.py` | line 86 | `verify_hmac` | Integration Edge HMAC verifier | ACCEPT |
| Current Edge handoff seam | implementation source | canonical project source: `apps/integration-edge/src/integration_edge/routing/service.py` | line 7 | `RoutingService` | Integration Edge proposal producer | ACCEPT |
| Current permission owner | implementation source | canonical project source: `packages/cvf-runtime/src/cvf_runtime/permission.py` | line 28 | `_ACTION_MIN_ROLE` | canonical role/action registry | ACCEPT |

## Negative Search And Collision Discipline

| Check | Evidence | Disposition |
| --- | --- | --- |
| Work Order path | exact `Test-Path` returned false before authoring | CREATE_NEW_EXACT_PATH |
| Baseline path | exact `Test-Path` returned false before authoring | CREATE_NEW_EXACT_PATH |
| P4-E token search | `rg --files docs` found the already accepted P4-E DESIGN/SPEC/review/matrix family | REUSE_NO_DUPLICATE_AUTHORITY |
| Runtime source search | targeted `rg` located Integration Edge HMAC/routing, Workspace external ingress, permission registry, and Operations Ledger owners | AMEND_NAMED_OWNERS_ONLY |
| Customer/vessel collision | only the two documented scaffold README paths exist under their directories | PROTECTED_UNCHANGED |

## Evidence Reuse And Encoding Plan

verificationMode: REVIEWER_RECOMPUTE_ONLY
priorVerificationArtifact: docs/decisions/SPEC_REREVIEW_2026-09-09_P4E_IDENTITY_CONVERSATION_ROUTING.md
priorVerificationAnchor: e9c21bd7c5627a0529b4d15d5a1533bd834ec886d13002c77ecdaa2a8094c3cc
recomputeReason: Independent authorization reviewer must recompute source hashes and path identity before granting BUILD.
unicodePathHandling: Use literal PowerShell paths and UTF-8-safe readers; changed governed Markdown and code remain ASCII unless a source contract requires otherwise.
extractedTextAuthority: N/A with reason
freshRecomputeRequired: YES_BY_REVIEWER

## Intake Role Routing Decision

| Field | Decision |
| --- | --- |
| intake summary | Operator accepted the independently recomputed SPEC rereview and requested continued P4-E progress. |
| scope classification | Bounded R2 product implementation across exact paths; no hidden reserve. |
| risk sensitivity | Identity, secret-adjacent selectors, authorization, durable SQL state, privacy deletion, and composition require independent review. |
| selected role route | MULTI_AGENT_MULTI_ROLE |
| role separation basis | ORCHESTRATOR accepted SPEC review; WORK_ORDER_AUTHOR wrote this packet; an independent authorization reviewer gates a separate IMPLEMENTATION_WORKER; an independent completion reviewer gates CLOSER. |
| escalation condition | Stop for source contradiction, path expansion, install, external effect, matrix drift, SQL atomicity ambiguity, or three same-root rework rounds. |

## Single-Agent Multi-Role Control Block

This block is present because the literal prohibition on self-review activates
the conservative structural guard; the selected execution route remains
MULTI_AGENT_MULTI_ROLE.

- Role separation ledger: WORK_ORDER_AUTHOR, authorization reviewer,
  implementation worker, completion reviewer, closer, and commit/session
  stewards are explicit phases and may not silently absorb one another.
- Evidence basis: each transition uses current source hashes, exact diff, tests,
  and gate outputs, never provider memory or an actor's recollection.
- Self-review boundary: author review is not independent review; no role may
  approve its own authored Work Order or implementation.
- Escalation conditions: stop and return to the operator/orchestrator for scope,
  authority, source, external-effect, or third-round conflicts.
- Gate sequence: pre-dispatch, independent authorization review,
  pre-implementation, worker-return fast gate, pre-closure, and pre-push.

## Legacy Absorption Coverage Index Disposition

NOT_APPLICABLE_WITH_REASON: P4-E modifies current first-party product owners and
retires one current process-local composition. It is not a legacy foundation,
external-repository absorption, or workflow-chain coverage-index tranche.

## Agent Handoff Contract Control Block

Contract source: `docs/reference/CVF_AHB_T2_AGENT_HANDOFF_CONTRACT_RATIFICATION_2026-06-16.md` (private-provenance reference only; not present in this project working tree)

| Field | Value |
| --- | --- |
| route | MULTI_AGENT_MULTI_ROLE |
| rolePattern | ORCHESTRATOR -> WORK_ORDER_AUTHOR -> INDEPENDENT_AUTHORIZATION_REVIEWER -> IMPLEMENTATION_WORKER -> INDEPENDENT_COMPLETION_REVIEWER -> CLOSER -> SESSION_SYNC_STEWARD |
| phase | WORK_ORDER pending PRE_EXECUTION_REVIEW; BUILD is locked |
| baseHeadFor(phase) | dispatchBaseHead=e367bc996e6fceaff08d23af34c2d5d8dada0ded; executionBaseHead=WORKER_MUST_CAPTURE_AT_START; closureBaseHead=REVIEWER_TO_SET |
| changedSetScope(phase) | exact 94-path ceiling in the pinned manifest; worker owns paths 15-80 only |
| traceScope(phase, actor) | each actor records base, status, commands, exact diff, external-effect counters, and lane evidence for its phase |
| commitOwner(phase) | WORKER_MUST_NOT_COMMIT; COMMIT_STEWARD only after independent completion review |
| crossBatchIsolation | one active P4-E lane; staged set empty; unrelated user changes preserved; no other mutation while lane is active |
| nextMoveSurfaces | independent authorization review only; after PASS, IMPLEMENTATION_WORKER may use worker-owned paths; reviewer and closer paths remain role-owned |
| sharedWorktreeCoordinationMode | EXPLICIT_LANE_HANDOFF |
| activeLaneOwner | INDEPENDENT_AUTHORIZATION_REVIEWER until authorization disposition; then explicitly released to IMPLEMENTATION_WORKER |
| laneOwnedPaths | current review lane owns only `docs/decisions/P4E_IDENTITY_CONVERSATION_ROUTING_WORK_ORDER_AUTHORIZATION_REVIEW_2026-09-09.md`; future worker lane owns exact paths 15-80 |
| dispatcherMutationBoundary | NO_MUTATION_WHILE_LANE_ACTIVE |
| laneReleaseEvidence | actor records final HEAD, `git status --short`, empty staging, exact changed set, and explicit lane release in its return |

## Reviewer Closure Conversion

| Field | Value |
| --- | --- |
| completionReviewPath | `docs/reviews/CVF_P4E_IDENTITY_CONVERSATION_ROUTING_COMPLETION_2026-09-09.md` |
| reviewerOwnedClosurePaths | paths 81-82 only; the worker may not create or edit either review artifact |
| closureOwner | INDEPENDENT_COMPLETION_REVIEWER, then CLOSER and SESSION_SYNC_STEWARD for paths 83-94 |
| workerCommitPermission | FORBIDDEN |

## Carry-Forward Resolution

| Rereview carry-forward | Binding Work Order resolution | Required evidence |
| --- | --- | --- |
| Exclude customer/vessel scaffolds | `packages/conversation-routing/customer-router/README.md` and `packages/conversation-routing/vessel-router/README.md` are protected; no file may be created in either directory. | exact diff/path scan and dependency-import negative test |
| AC-16 needs a real probe | path 76 must import the real Workspace API composition root, instantiate the production composition with injected stores, inspect the bound proposal/placement repository types, and fail if the process-local repository is reachable from production composition. A source-comment assertion is forbidden. | execution of `tests/integration/test_p4e_workspace_composition.py`, plus negative import test at path 79 |
| Own retirement failure | `apps/integration-edge/src/integration_edge/verification/sender_keys.py` is the sole owner of `TokenKeyRetirementReadinessV1` and `SenderTokenKeyAuthority.retire_previous`; it emits sanitized `TOKEN_KEY_RETIREMENT_BLOCKED` readiness/audit evidence. Mapping services, management APIs, and all three P4-E invariant matrices must not emit it. | unit test at path 71, receipt negative scan, import-boundary test, reviewer source inspection |

## Exact Final Changed-Set Ceiling - 94 Paths

The exact path and owner map is frozen in
`docs/implementation/P4E_IDENTITY_CONVERSATION_ROUTING_EXACT_MANIFEST_2026-09-09.md`.
Its SHA-256 is recorded below after deterministic generation. The manifest is
an indivisible part of this Work Order: the implementation worker owns paths
15-80 only; the independent reviewers own paths 81-82; the closer and session
sync steward own paths 83-94. Paths 1-14 are settled governance. An unneeded
worker path remains absent or unchanged and is reported rather than filled with
scaffolding. Any path outside the exact manifest, deletion, rename, owner-class
change, or manifest hash drift stops work and requires independent amendment
review.

exactManifestSha256: edb56012d87e7c4e9b3c715feba6d32a65a90b70064c9fa7d0d3b2abdc03a846

## Protected And Forbidden Scope

- `packages/conversation-routing/customer-router/README.md` is protected and
  unchanged; no file may be created under `customer-router/`.
- `packages/conversation-routing/vessel-router/README.md` is protected and
  unchanged; no file may be created under `vessel-router/`.
- P4-D channel adapter behavior, internal message admission, operational
  Message/Event/Task/CustomerRequest/Incident/Report/Approval creation, Phase
  5, XR1, catalog migration, and external-repository absorption are excluded.
- No new dependency, lockfile, credential file, environment file, provider SDK,
  daemon, watcher, queue service, deployment file, or public endpoint.
- No raw sender or sender token may enter log, telemetry, audit, receipt,
  management response, candidate content, exception detail, or committed test
  fixture.
- No worker edit to paths 1-14 or 81-94; no staging, commit, push, stash,
  checkout, reset, merge, rebase, or worktree operation.

## Secret-Authority Ownership

`apps/integration-edge/src/integration_edge/verification/sender_keys.py` is the
sole runtime owner of sender-token key activation, dual-read window, cache
purge, wrapping-key deletion request, and sanitized retirement readiness. It
shall define `TokenKeyRetirementReadinessV1` and
`SenderTokenKeyAuthority.retire_previous`.

The blocked record has only non-secret key id/version, attempted-at, closed
reason, and opaque correlation id. The exact outcome is
`TOKEN_KEY_RETIREMENT_BLOCKED`. It is neither a mapping action nor a Workspace
management API receipt and must not be imported by identity-mapping or
conversation-routing. Actual external secret-store deletion is represented by
an injected port in deterministic BUILD; no real secret store or credential is
used.

## Work-Order Fulfillment Manifest

Work Order Fulfillment Manifest: REQUIRED

| Required artifact group | Exact paths | Worker action | Required at handoff |
| --- | --- | --- | --- |
| package and root wiring | 15-33 | implement closed models, ports, matrix consumers, cryptographic helpers, and dependency direction | YES |
| Integration Edge sender seam | 34-42 | implement v2 authenticated sender evidence, token derivation, key authority, and handoff | YES |
| Operations Ledger | 43-49 | implement records, tables, migration, InMemory/SQLite/PostgreSQL parity and unit-of-work semantics | YES |
| Workspace API and permission | 50-64 | implement fresh-role commands, private routers, durable composition, two-transaction placement | YES |
| contract schemas | 65-66 | implement closed representation-parity schemas | YES |
| tests | 67-79 | implement deterministic positive, negative, mutation, concurrency, privacy, composition, and backend evidence | YES |
| worker return | 80 | record actual evidence and lane release without authoring completion review | YES |

Expected worker manifest: paths 15-80 only. Existing files in this range must
be changed only when necessary. New-path noncreation is allowed only when the
worker proves it is unnecessary and all R/AC evidence still passes; creating a
placeholder solely to satisfy the list is forbidden.

## Ordered BUILD Plan

1. Recompute all source hashes and matrix pins, capture execution anchor, and
   pass pre-implementation gates before any edit.
2. Implement matrix consumers and provider-neutral package contracts at paths
   15-32. Keep every new/changed Python owner below the 300-line hard limit.
3. Implement durable Operations Ledger records, migration, constraints,
   idempotency, CAS, stale-claim recovery, and backend parity at paths 43-49.
4. Implement the P4-C sender-aware signature/evidence/key-authority seam at
   paths 34-42 without importing either P4-E package.
5. Implement Workspace API fresh-role authorization, two-human lifecycle,
   private APIs, durable ingress composition, placement transaction B, retry,
   retention, and privacy deletion at paths 50-64.
6. Implement schemas and tests at paths 65-79. Run focused tests first, then
   invariant/repository/full non-live gates in the exact order below.
7. Author only the worker return at path 80, leave staging empty, and release
   the lane to the independent completion reviewer.

## Acceptance And Failure Semantics

- Every SPEC R1-R21 maps to its listed AC-01-AC-16 and must have positive plus
  fail-closed evidence. No partial acceptance or waiver is available to the
  worker.
- Same idempotency key and digest returns the sanitized prior receipt; same key
  with changed digest conflicts with zero partial mutation.
- Permission, scope, separation of duty, fresh actor/user/assignment/target
  state, expected version, and unique-current constraints are rechecked inside
  the mutation unit of work.
- Transaction A commits immutable proposal/observation/work once. Transaction B
  commits one terminal decision or rolls back and preserves bounded retry.
- Ambiguity, corruption, stale version, unavailable authority, lineage mismatch,
  and unknown claim state never degrade to a privileged route.
- Failure of key erasure or cache purge emits only the secret-authority blocked
  readiness record and prevents retirement; it never becomes a mapping receipt.
- A failed required test or gate, unexpected product regression, external
  effect, path delta, or matrix drift yields `BLOCKED_WITH_REASON`; evidence is
  retained and no commit occurs.

## Shared Invariant-Family Proof

- Applicability: APPLICABLE for all three registered P4-E families.
- Canonical digests: mapping `ea2af812...003e1a`; resolution
  `4ef64cf1...00bdc`; placement `fd351b66...8ec8cc56`.
- Emitters: `identity_mapping.invariants` and
  `conversation_routing.invariants`; each consumes the pinned matrices and does
  not restate outcome grammar.
- Evidence: path 67 plus the existing generic invariant family contract and
  repository-guard tests.
- Mutation: deterministic one-fact mutation for every field and closed outcome;
  no new exclusion or waiver.
- Reviewer recomputation: recompute all digests; run full mutation corpus;
  sample at least one raw positive for every matrix outcome; prove expected
  values came from canonical matrices rather than BUILD output.

Exact invariant commands:

```powershell
python scripts/check_invariant_families.py --json
python -m pytest -q tests/unit/test_invariant_family_contract.py tests/integration/test_invariant_family_repository_guard.py tests/unit/test_p4e_invariants.py
```

## Dual Agent Surface Matrix

| Consumer class | Interface or owner surface | Authority and risk boundary | Evidence | Adapter boundary | Disposition |
| --- | --- | --- | --- | --- | --- |
| `INTERNAL_AGENT` | exact project paths 15-80 | R2; no external effect; worker cannot commit/approve | accepted SPEC, deterministic tests, disposable databases, independent review | internal project composition only; service assertion is application ingress, not an agent adapter | CONTRACT_ONLY |
| `EXTERNAL_AGENT_CLI_MCP` | no CLI/MCP adapter in exact scope | no ingress, auth, approval, receipt, raw-data, mutation, provider, or public authority | explicit exclusion and dependency scan | external-agent adapter is absent by design and cannot be inferred from internal contracts | N/A_WITH_REASON |

## Pre-BUILD Gate

The implementation worker shall not edit source until all conditions below
pass under the recorded operator authorization:

1. continuity rehydrated; role declared as IMPLEMENTATION_WORKER;
2. authorization review path 81 exists; its only F1-F3 citation findings were
   repaired at `64cf02c`, and the operator explicitly waived rereview;
3. current HEAD equals local `origin/docs/p4e-spec`, staging is empty, and the
   only pre-existing unstaged/untracked paths are explicitly accepted or none;
4. SPEC, rereview, DESIGN, matrices, pins, and baseline hashes match;
5. Python is 3.13.12 and Pydantic is 2.10.6 without installing anything;
6. workspace doctor, session, Project Knowledge, invariant, catalog, file-size,
   and repository guards pass with only the already accepted bounded legacy-
   catalog warning;
7. providerCallCount, externalNetworkCallCount, credentialReadCount,
   dependencyInstallCount, deploymentCount, stageCount, commitCount, and
   pushCount are initialized to zero.

## Verification Commands

Substitute the captured worker value for `<executionBaseHead>`; never replace it
with the older dispatch anchor.

```powershell
powershell -ExecutionPolicy Bypass -File "../.Controlled-Vibe-Framework-CVF/scripts/check_cvf_workspace_agent_enforcement.ps1" -ProjectPath (Get-Location).Path
# Private-provenance reference only; this project has no executable local copy of governance/compat/run_agent_autorun_workflow_gate.py.
python -m pytest -q tests/unit/test_p4e_invariants.py tests/unit/test_p4e_identity_models.py tests/unit/test_p4e_identity_service.py tests/unit/test_p4e_conversation_routing.py tests/unit/test_p4e_sender_key_retirement.py tests/security/test_p4e_sender_evidence.py tests/security/test_p4e_privacy_disclosure.py tests/contract/test_p4e_contract_schemas.py tests/integration/test_p4e_backend_parity.py tests/integration/test_p4e_workspace_composition.py tests/integration/test_p4e_transaction_protocol.py tests/unit/test_p4e_dependency_boundary.py
python -m pytest -q tests/integration/test_p4e_postgres_live.py
python scripts/check_invariant_families.py --json
python -m pytest -q tests/unit/test_invariant_family_contract.py tests/integration/test_invariant_family_repository_guard.py
python scripts/check_project_knowledge.py
python scripts/check_session_state.py
python scripts/generate_catalog.py --check
python scripts/check_file_size.py
python scripts/testing/validate_repository.py
python -m pytest -q
# Shape reference only; governance/compat/run_worker_return_fast_gate.py is not copied into the project.
git diff --check
git status --short
```

The PostgreSQL test may use only an already configured disposable local test
database. If unavailable, record an honest environment blocker; do not install,
connect to a shared/production database, or replace it with a mock while
claiming AC-05/AC-10 complete.

The AC-16 command is the real import/composition probe:

```powershell
python -m pytest -q tests/integration/test_p4e_workspace_composition.py tests/unit/test_p4e_dependency_boundary.py
```

Path 75 must import the actual composition root and assert concrete bound
repository/store module ownership. Merely scanning comments, checking a string,
or asserting that a constructor exists does not satisfy AC-16.

## Required Proof Manifest

| Requirement | Required literal | Evidence owner | Required at handoff |
| --- | --- | --- | --- |
| source identity | `de3af4a90425ee70f8e285fc31e12774497f7a190b776beab3ed3d32fdc90618` | worker, reviewer recomputes | YES |
| SPEC review identity | `e9c21bd7c5627a0529b4d15d5a1533bd834ec886d13002c77ecdaa2a8094c3cc` | worker, reviewer recomputes | YES |
| mapping matrix | `ea2af8122016a7b8ee10d9a8aa097f1b692a168a4914425172c555cd4d003e1a` | worker, reviewer recomputes | YES |
| resolution matrix | `4ef64cf1f53633974b0e585018148a8f6bbe7a16ce4683329aa29d51c0000bdc` | worker, reviewer recomputes | YES |
| placement matrix | `fd351b6670292e82835b4ec34c270768174758a6d8a3f1558e4e4b3a8ec8cc56` | worker, reviewer recomputes | YES |
| key retirement failure | `TOKEN_KEY_RETIREMENT_BLOCKED` | Integration Edge secret-authority test | YES |
| composition retirement | `InMemoryExternalIngressRepository` | real composition/import probe | YES |
| worker disposition | `COMPLETE_PENDING_REVIEW` | worker return | YES |

## Worker Output Checker Read-Ahead Mandate

Before writing path 80, read checker source for its docType, path family, and
conditional content class. The return must use actual sections rather than
mentioning heading syntax in a checklist.

## Worker Return Packet Shape Contract

workerReturnPath: `docs/reviews/CVF_P4E_IDENTITY_CONVERSATION_ROUTING_WORKER_RETURN_2026-09-09.md`
contractProfile: WORKER_RETURN_FULL_GATE_V1
requiredGate: project workspace doctor plus the exact focused, invariant, repository, full-suite, diff, and status commands above; `python governance/compat/run_worker_return_fast_gate.py` remains the private-provenance shape reference only
individualCheckerSubstitution: FORBIDDEN
workerReturnSkeleton: CHECKER_SAFE_SKELETON_REQUIRED

Required terms: Purpose; Scope / Methodology; Findings / Position; Risk /
Corrective Action; Claim Boundary; Agent Operation Trace Block; Delta Execution
Claim Boundary Control Block; Public Export Disposition; executionBaseHead;
git status --short.

Conditional terms: External Knowledge Intake Routing; Rescan Intelligence
Hardening; Corpus Completeness And Report Integrity; Finding-To-Governance
Learning Disposition; Epistemic Process Block; Machine Closure Package.

Use `N/A with reason` for each non-applicable conditional block. Record:

- exact before/after status and staging;
- expected versus actual paths and manifest delta;
- test commands, exit codes, counts, and PostgreSQL availability;
- provider/network/credential/install/deploy/stage/commit/push counters;
- matrix digests and mutation summary;
- AC-16 real composition evidence;
- `TOKEN_KEY_RETIREMENT_BLOCKED` owner/negative receipt evidence;
- raw sender/token negative scans;
- explicit lane release.

## Review Gate

The independent authorization review verified source hashes, all 94 paths,
package/import direction, SQL ownership/atomicity, carry-forward resolutions,
commands, failure semantics, and the zero-external-effect boundary. Its only
F1-F3 citation findings were repaired at `64cf02c`; on 2026-09-09 the operator
accepted those mechanical repairs, waived rereview, and authorized exact BUILD.

The independent completion reviewer then evaluates returned evidence without
recreating implementation. Focused reruns need a named contradiction,
information-gain expectation, and cost reason. Completion requires exact diff,
all R/AC coverage, deterministic matrices/mutations, real AC-16 composition
probe, backend parity including disposable PostgreSQL, negative disclosure
scans, full non-live regression, zero forbidden effects, and clean staging.

## Stop Conditions And Rollback

Stop before further edits on source contradiction, changed source pin, a needed
path outside 15-80, an unnecessary destructive edit, dependency/install need,
secret or external network need, customer/vessel scope, matrix drift, inability
to prove SQLite/PostgreSQL atomicity, unexpected product regression, unsafe
evidence, or third same-root repair round.

Rollback is path-bounded: restore only worker-owned P4-E changes to their exact
`executionBaseHead` bytes or remove only new worker-created P4-E paths after the
reviewer records the failure. Preserve all unrelated user changes and all
failed evidence. The worker may not perform destructive Git rollback commands.

## Commit Prompt Readiness

- Worker staging, commit, and push: FORBIDDEN.
- Reviewer/closer may not commit before `COMPLETION_REVIEW_PASS`.
- After PASS, COMMIT_STEWARD creates one material commit for reviewed source,
  tests, worker return, and completion review.
- SESSION_SYNC_STEWARD then updates paths 83-94 in a separate continuity commit
  because the future material SHA cannot be known before commit.
- Before each push, verify repository boundary and `git remote -v`; push only
  the project branch named by current continuity. Private provenance and public
  CVF Core remain read-only.

## Agent Operation Trace Block

| Field | Evidence |
| --- | --- |
| Actor | ORCHESTRATOR -> WORK_ORDER_AUTHOR |
| Provider or surface | local first-party project workspace |
| Session or invocation | P4-E Work Order authoring, 2026-09-09 |
| Working directory | project repository root |
| Command or tool surface | governed reads, source/hash/path discovery, scaffold helper, ADIF resolver, apply-patch, focused structural checks |
| Target paths | rereview, paired GC-018 baseline, Work Order; continuity follows in separate sync |
| Allowed scope source | operator acceptance flow, accepted P4-E DESIGN/SPEC, independent SPEC_REVIEW_PASS |
| Before status evidence | clean worktree at the prior material commit; at authoring start branch `docs/p4e-spec`, HEAD `e367bc996e6fceaff08d23af34c2d5d8dada0ded`, staging empty, and only the independently supplied rereview untracked |
| After status evidence | paired baseline and Work Order authored for review; BUILD remains locked |
| Diff evidence | `git diff --name-status` and untracked inventory before material commit |
| Approval boundary | Work Order authoring and independent authorization review only |
| Claim boundary | no application/runtime/provider/live/deploy/production behavior implemented or claimed |
| Agent type | WORK_ORDER_AUTHOR |
| Invocation ID | `p4e-identity-conversation-routing-work-order-2026-09-09` |
| Expected manifest | rereview plus baseline plus Work Order for this authoring transition |
| Actual changed set | reviewer to verify before authoring commit |
| Manifest delta | pending deterministic pre-commit check |

## Delta Execution Claim Boundary Control Block

| Field | Value |
| --- | --- |
| claimScope | A bounded R2 Work Order proposal was authored from accepted DESIGN/SPEC/review evidence. |
| claimDisposition | CLAIM_REJECTED: no implementation, execution-control, runtime-enforcement, direct-interception, production, or provider-governance behavior is claimed. |
| receiptEvidence | SPEC rereview hash and local dispatch-authoring gate results only. |
| actionEvidence | Read-only discovery plus creation of the paired baseline and Work Order. |
| invocationBoundary | Zero provider, external network, credential, database, installation, deployment, or external-agent invocation. |
| interceptionBoundary | No direct interception, wrapper/proxy enforcement, runtime gate, or agent coding control is implemented by this document. |
| claimLanguage | READY_FOR_REVIEW means only eligible for independent authorization review; BUILD is not granted. |
| forbiddenExpansion | No runtime/provider/live/public/package/Web/MCP/model-router claim and no path outside the exact reviewed authority. |

## Claim Boundary

This Work Order defines proposed BUILD authority but does not grant it. It does
not prove that any P4-E code exists or works. It makes no live provider, agent-
governance, production, deployment, exact-once, external queue, customer,
vessel, operational-truth, or public-catalog claim.

## Public Export Disposition
DEFERRED_PRIVATE_ONLY

Reason: this first-party project packet may be pushed to its project remote,
but it does not claim or perform a CVF public-catalog export.
