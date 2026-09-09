# Work Order - P4-E Amendment 2 Closure Ordering

Memory class: governed-work-order

docType: work_order

Batch ID: P4E-AMENDMENT2-CLOSURE-ORDERING-2026-09-10

Status: DRAFT_PENDING_INDEPENDENT_AUTHORIZATION_REVIEW

Risk ceiling: R2

Commit mode: WORKER_MUST_NOT_COMMIT; COMMIT_STEWARD_ONLY_AFTER_REVIEW

## Review Dispatch Convergence And Invocation Budget Control

Review-Dispatch Convergence Control: REQUIRED

dispatchKind: REWORK
dispatchSurface: INTERNAL_AGENT
parentAssignmentId: P4E-AMENDMENT2-CLOSURE-ORDERING-2026-09-10
reviewRoundCount: 1
priorFindingSetDigest: 7b3c183745f2d62c871a308e763c4a723e8a24256c861596894b460f8e177bed
dependencyAuditDisposition: COMPLETE_BEFORE_FIRST_REPAIR
reworkFindingDisposition: CONSOLIDATED_ALL_DEPENDENT_FINDINGS
newIndependentCriticalEvidence: P4E-AM2-AUTH-F1,P4E-AM2-AUTH-F2
regressionGuardDisposition: REQUIRED_TWO_PHASE_GATE_SEQUENCE
cumulativeExternalInvocationCount: 0
externalInvocationCeiling: 0
usageAvailability: NOT_APPLICABLE_INTERNAL_AGENT
quotaAdmissionDisposition: NOT_APPLICABLE_INTERNAL_AGENT
nextDispatchDisposition: ONE_CONSOLIDATED_REWORK
rootCauseClusterId: P4E-AM2-CLOSEABILITY-ORDERING
reworkGeneration: 1
consolidatedDefectClassSweep: COMPLETE_BEFORE_REWORK_DISPATCH
successorTrancheOpened: NO
implementationAutonomyDisposition: CONTRACT_AUTHORITY_EVIDENCE_OUTCOME_ONLY
preExecutionReviewAdmission: REQUIRED_TRIGGERED
preExecutionReviewTrigger: SOURCE_AUTHORITY_CONTRADICTION
nextRoutineReviewBoundary: PRE_EXECUTION_REVIEW
reviewerWorkBoundary: EVALUATE_RETURNED_EVIDENCE_NOT_RECREATE_IMPLEMENTATION

## Semantic Convergence Outcome

```json
{
  "schemaVersion": "cvf.semanticConvergenceControl.v1",
  "problemKey": "p4e-amendment2-closure-ordering",
  "chainMode": "INITIAL",
  "chainOrdinal": 0,
  "predecessor": null,
  "blockerDelta": {
    "prior": [],
    "resolved": [],
    "retained": [],
    "new": ["P4E-AM2-CLOSEABILITY-F1", "P4E-AM2-AUTH-F1", "P4E-AM2-AUTH-F2"],
    "reopened": [],
    "current": ["P4E-AM2-CLOSEABILITY-F1", "P4E-AM2-AUTH-F1", "P4E-AM2-AUTH-F2"]
  },
  "resolutionEvidence": {},
  "counters": {
    "partialReadyClosures": 0,
    "reviewerScopeExpansions": 0,
    "sameClaimCorrections": 1,
    "nonDecreasingBlockerTransitions": 0
  },
  "claims": [{
    "claimId": "P4E-AM2-ORDERING-CONTRACT",
    "claimClass": "DOCUMENTATION_ONLY",
    "proofClass": "PROPOSAL_ONLY_NO_RUNTIME_READINESS",
    "evidenceRef": "docs/decisions/P4E_IDENTITY_CONVERSATION_ROUTING_AMENDMENT_2_AUTHORIZATION_REVIEW_2026-09-10.md"
  }],
  "requiredDisposition": "CONTINUE_BOUNDED",
  "successorScope": "INTEGRATED_ROOT_CONTRACT"
}
```

## Checker Source Read-Ahead Block

| Field | Value |
| --- | --- |
| applicableCheckersRead | `governance/compat/check_work_order_dispatch_quality.py`; `governance/compat/check_semantic_convergence_control.py`; work-order template and guard-orientation index |
| literalTokensReviewed | Review-Dispatch Convergence Control; Semantic Convergence Outcome; Checker Source Read-Ahead Block; Source Verification Block; Agent Handoff Contract Control Block; Dual Agent Surface Matrix; Agent Operation Trace Block; Delta Execution Claim Boundary Control Block |
| gateRunPurpose | Confirm the corrected packet's forward-required machine shape before redispatch; not evidence of closure correctness. |
| claimBoundary | Structural read-ahead only; independent authorization and executed gates remain required. |

## Source Verification Block

| Claimed item | Source fact type | Source file | Verified line/section | Verified path or symbol | Owning interface/function/schema | Disposition |
| --- | --- | --- | --- | --- | --- | --- |
| Catalog must precede final suite | normative phase order | `docs/work_orders/CVF_AGENT_WORK_ORDER_P4E_IDENTITY_CONVERSATION_ROUTING_AMENDMENT_1_2026-09-10.md` | Gate-To-Role Closeability Matrix | catalog then final suite | Amendment 1 closure choreography | ACCEPT |
| Session sync was scheduled after material commit | normative phase order | `docs/work_orders/CVF_AGENT_WORK_ORDER_P4E_IDENTITY_CONVERSATION_ROUTING_AMENDMENT_1_2026-09-10.md` | Gate-To-Role Closeability Matrix | paths 83-92 timing | Amendment 1 closure choreography | ACCEPT |
| Catalog changed a Project Knowledge source pin | current configuration fact | `knowledge/manifest.json` | project-context sourcePins | `docs/catalog/MODULE_REGISTRY.json` | Project Knowledge Pack | ACCEPT |
| Machine reproduction | executed diagnostic evidence | `scripts/check_project_knowledge.py` | latest local command result | `KPK_SOURCE_PIN_DRIFT:PROJECT_CONTEXT.md` | Project Knowledge validator | ACCEPT |

## Agent Handoff Contract Control Block

| Field | Value |
| --- | --- |
| route | MULTI_AGENT_MULTI_ROLE |
| rolePattern | WORK_ORDER_AUTHOR -> INDEPENDENT_AUTHORIZATION_REVIEWER -> CLOSER -> SESSION_SYNC_STEWARD -> INDEPENDENT_COMPLETION_REVIEWER -> COMMIT_STEWARD -> SESSION_SYNC_STEWARD |
| phase | AMENDMENT_AUTHORIZATION_REVIEW; execution locked until PASS and activation commit |
| baseHeadFor(phase) | activationBaseHead=`0bb8eca3d468574c3133c9093873ce4af657212f`; material and continuity heads captured when created |
| changedSetScope(phase) | paths 110-112 for activation; 93-94 catalog; 83-92 continuity; existing path 82 review |
| traceScope(phase, actor) | each role records exact paths, commands, HEAD, staging, external effects, and lane release |
| commitOwner(phase) | COMMIT_STEWARD only; exact control-plane, material, then continuity commits |
| crossBatchIsolation | one active P4-E closure lane; unrelated changes preserved |
| nextMoveSurfaces | independent authorization review path 112 only |
| sharedWorktreeCoordinationMode | EXPLICIT_LANE_HANDOFF |
| activeLaneOwner | INDEPENDENT_AUTHORIZATION_REVIEWER |
| laneOwnedPaths | path 112 only during authorization review |
| dispatcherMutationBoundary | NO_MUTATION_WHILE_LANE_ACTIVE |
| laneReleaseEvidence | verdict, exact changed path, HEAD, staging, and no-commit statement |

## Dual Agent Surface Matrix

| Consumer class | Interface or owner surface | Authority and risk boundary | Evidence | Adapter boundary | Disposition |
| --- | --- | --- | --- | --- | --- |
| `INTERNAL_AGENT` | repository-local closure roles and paths 82-94, 110-112 | R2; exact role/path limits; no product repair | machine gates, Git evidence, independent reviews | local repository operations only | CONTRACT_ONLY |
| `EXTERNAL_AGENT_CLI_MCP` | none | no dispatch, provider, credential, mutation, or review authority | explicit operator instruction not to use Claude plus external ceiling zero | adapter absent and not inferred | N/A_WITH_REASON |

## Epistemic Process Block

Epistemic Process Applicability: HIGH_EVIDENCE

### Expected Result / Prediction

Early continuity sync removes catalog source-pin drift; post-material
finalization supplies the real material SHA; both complete suites pass.

### Evidence Comparison

Both gate cycles must compare actual results with this prediction.

### Contradiction Or Gap Disposition

Any other failure requires an explicit disposition and blocks closure.

### Claim Update

Final review records whether the prediction was confirmed, revised, narrowed,
or invalidated.

## Objective

Close `P4E-AM2-CLOSEABILITY-F1` by executing the minimal acyclic sequence
defined by the paired exact-manifest amendment. Do not reopen accepted product
repair or broaden P4-E scope.

## Source Authority

- `docs/implementation/P4E_IDENTITY_CONVERSATION_ROUTING_EXACT_MANIFEST_AMENDMENT_2_2026-09-10.md`
- Amendment 1 manifest, Work Order, and authorization review
- Existing independent completion review path 82
- Machine evidence: catalog PASS after regeneration; Project Knowledge fails
  only with `KPK_ELIGIBILITY_MISMATCH:PROJECT_CONTEXT.md` and
  `KPK_SOURCE_PIN_DRIFT:PROJECT_CONTEXT.md`; the full suite consequently
  reports two failures and eight setup errors in only Project Knowledge Pack
  tests.

## Role And Write Matrix

| Role | Authorized write surface | Required outcome |
| --- | --- | --- |
| INDEPENDENT_AUTHORIZATION_REVIEWER | path 112 only | PASS before activation |
| CLOSER | paths 93-94; evidence only otherwise | catalog/repository gates PASS |
| SESSION_SYNC_STEWARD | existing paths 83-92 only | current closure-candidate state and exact source pins before final suite |
| INDEPENDENT_COMPLETION_REVIEWER (pre-material) | existing path 82 only | conditional material-commit authorization after candidate gates |
| INDEPENDENT_COMPLETION_REVIEWER (post-material) | existing path 82 only | terminal acceptance after actual-SHA finalization and final gates |
| COMMIT_STEWARD | staging/commit only | material commit, exact path-82 terminal-review commit, then continuity commit |

## Required Sequence

1. Independently review paths 110-111.
2. Commit only paths 110-112 as the Amendment 2 activation commit.
3. Confirm catalog paths 93-94 are canonical and repository validation passes.
4. Synchronize paths 83-92 to the accepted P4-E closure candidate, including
   current source hashes in `knowledge/manifest.json`.
5. Run, in order:

```powershell
python scripts/check_project_knowledge.py
python scripts/check_session_state.py
python scripts/check_file_size.py
python scripts/check_invariant_families.py --json
python scripts/generate_catalog.py --check
python scripts/testing/validate_repository.py
python -m pytest -q
git diff --check
git status --short -uall
git diff --cached --stat
```

6. Route pre-material evidence to the independent completion reviewer. Only a
   `MATERIAL_COMMIT_AUTHORIZED_PENDING_POST_COMMIT_CONTINUITY_FINALIZATION`
   verdict authorizes the exact material commit excluding paths 83-92.
7. After material commit, finalize only paths 83-92 with its actual SHA and
   rerun the entire command sequence above, including the complete suite.
8. Route post-material evidence to the independent completion reviewer for
   terminal acceptance on path 82, rerun knowledge/file/catalog/repository and
   diff checks after that evidence-only update, then commit exactly path 82 as
   a terminal-review-evidence commit.
9. Commit only paths 83-92 as the continuity commit.
10. Verify clean staging/worktree, material, terminal-review-evidence, and continuity commit identities,
   and park P4-E at `FREEZE / CLOSED_BOUNDED`.

## Evidence And Claim Rules

- The known pre-sync Project Knowledge failures are phase-order evidence, not
  product-test waivers.
- Final suite must pass after synchronization; no failure is accepted.
- No Alibaba/provider call is required or authorized because this closure step
  asserts no AI-governance behavior.
- No Docker rerun is required absent a contradiction; the independently
  accepted disposable PostgreSQL 12-test evidence remains valid.
- No push, deployment, install, external network, shared database, or public
  export is authorized.

## Commit Boundary

The activation commit contains only paths 110-112. After final acceptance,
the pre-material review may authorize the material commit conditionally on
post-commit finalization. That material commit contains accepted P4-E product/
evidence/catalog paths and excludes 83-92. After the actual material SHA is
written and the final gates/review pass, an evidence-only commit records exact
path 82; the continuity commit then follows and contains only 83-92. Never use
broad staging commands.

## Agent Operation Trace Block

| Field | Evidence |
| --- | --- |
| Actor | ORCHESTRATOR / WORK_ORDER_AUTHOR |
| Provider or surface | local first-party project workspace |
| Session or invocation | Amendment 2 authoring and F1-F2 repair, 2026-09-10 |
| Working directory | project repository root |
| Command or tool surface | governed reads, machine diagnostics, apply-patch, Git read-only inspection |
| Target paths | paths 110-111; path 112 reserved for independent reviewer |
| Allowed scope source | operator instruction to finish P4-E and then return to CVF Core |
| Before status evidence | HEAD `0bb8eca3d468574c3133c9093873ce4af657212f`; product packet unstaged |
| After status evidence | corrected paths 110-111 pending independent rereview; no activation commit yet |
| Diff evidence | exact new paths 110-112; no product mutation in this amendment repair |
| Approval boundary | authoring only; author cannot approve own amendment |
| Claim boundary | ordering contract only; no runtime/provider/deployment/production claim |
| Deletion or rename disposition | N/A with reason - no deletion or rename |
| Agent type | WORK_ORDER_AUTHOR |
| Invocation ID | `p4e-amendment2-authoring-2026-09-10` |
| Expected manifest | paths 110-111 authored; path 112 independently reviewed |
| Actual changed set | exact paths 110-112 pending activation review |
| Manifest delta | NONE |

## Delta Execution Claim Boundary Control Block

| Field | Value |
| --- | --- |
| claimScope | Minimal P4-E closure-order correction with two explicit gate cycles. |
| claimDisposition | CLAIM_REJECTED for closure until independent authorization and executed post-material gates pass. |
| receiptEvidence | Machine-reproduced catalog-to-knowledge pin drift and authorization findings only. |
| actionEvidence | ACTION_EVIDENCE_PRESENT: paths 110-111 authored; path 112 independently reviewed. |
| invocationBoundary | Local governed document work only; zero provider/network/credential/database/deployment action. |
| interceptionBoundary | No runtime interception, wrapper, dispatcher, or universal agent enforcement is claimed. |
| claimLanguage | DRAFT means reviewable proposal only; it is not execution authority. |
| forbiddenExpansion | No product edit, provider/live/public/deploy action, broad staging, or path outside 82-94 and 110-112. |

## Stop Conditions

Stop on independent authorization failure, any product finding, any final
suite failure after sync, any needed path outside the effective 112-path
packet, or inability to preserve the exact material/path-82/continuity commit
split.

## Public Export Disposition

DEFERRED_PRIVATE_ONLY

Reason: private project closure only; no public export is authorized.

## Claim Boundary

This Work Order authorizes only the closeability-order correction and final
private P4-E closure choreography. It does not authorize product changes,
provider/runtime claims, deployment, production readiness, or public action.
