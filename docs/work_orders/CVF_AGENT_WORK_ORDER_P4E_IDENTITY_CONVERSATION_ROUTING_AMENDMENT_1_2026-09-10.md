# CVF Work Order Amendment 1 - P4-E Final Consolidated Repair

Status: PENDING_INDEPENDENT_AUTHORIZATION_REVIEW

Date: 2026-09-10

Risk ceiling: R2

Commit mode: WORKER_MUST_NOT_COMMIT

## Review Dispatch Convergence And Invocation Budget Control

Review-Dispatch Convergence Control: REQUIRED

dispatchKind: REWORK
dispatchSurface: EXTERNAL_AGENT_CLI_MCP
parentAssignmentId: P4E-AMENDMENT1-CONSOLIDATED-REPAIR-2026-09-10
reviewRoundCount: 1
priorFindingSetDigest: 4ba551a174d696613f476e9f0c5682984409c0667386765f0f1c2182d640de18
dependencyAuditDisposition: COMPLETE_BEFORE_FIRST_REPAIR
reworkFindingDisposition: CONSOLIDATED_ALL_DEPENDENT_FINDINGS
newIndependentCriticalEvidence: P4E-COMP-REREV2-F1,P4E-COMP-REREV2-F2
regressionGuardDisposition: REQUIRED_AND_PLANNED_FOR_EACH_TARGETED_DEFECT
cumulativeExternalInvocationCount: 0
externalInvocationCeiling: 1
usageAvailability: KNOWN_FOR_ADMISSION
quotaAdmissionDisposition: ADMITTED_WITHIN_CUMULATIVE_CEILING
nextDispatchDisposition: ONE_CONSOLIDATED_REWORK
rootCauseClusterId: P4E-AMENDMENT1-CONSOLIDATED-F1-THROUGH-F4-2026-09-10
reworkGeneration: 1
consolidatedDefectClassSweep: COMPLETE_BEFORE_REWORK_DISPATCH
successorTrancheOpened: NO
implementationAutonomyDisposition: CONTRACT_AUTHORITY_EVIDENCE_OUTCOME_ONLY
preExecutionReviewAdmission: REQUIRED_TRIGGERED
preExecutionReviewTrigger: AUTHORITY_SCOPE_EXPANSION
nextRoutineReviewBoundary: PRE_EXECUTION_REVIEW
reviewerWorkBoundary: EVALUATE_RETURNED_EVIDENCE_NOT_RECREATE_IMPLEMENTATION

The external invocation ceiling authorizes one Claude repair dispatch only
after the independent amendment authorization review passes. It does not
authorize a provider API call from product code, any Alibaba call, or a second
automatic external dispatch.

## Semantic Convergence Outcome

The predecessor Work Order carries a legacy SCEC shape that cannot lawfully be
made the hash predecessor of a new current-schema block without rewriting the
settled artifact. This operator-authorized successor assignment therefore
opens a new, explicit problem chain for the newly established critical
security/authority evidence. The predecessor remains pinned by its SHA-256 and
by `priorFindingSetDigest` above; its review telemetry is not reset.

```json
{
  "schemaVersion": "cvf.semanticConvergenceControl.v1",
  "problemKey": "p4e-amendment1-consolidated-repair",
  "chainMode": "INITIAL",
  "chainOrdinal": 0,
  "predecessor": null,
  "blockerDelta": {
    "prior": [],
    "resolved": [],
    "retained": [],
    "new": [
      "P4E-COMP-REREV2-F1",
      "P4E-COMP-REREV2-F2",
      "P4E-COMP-REREV2-F3",
      "P4E-COMP-REREV2-F4"
    ],
    "reopened": [],
    "current": [
      "P4E-COMP-REREV2-F1",
      "P4E-COMP-REREV2-F2",
      "P4E-COMP-REREV2-F3",
      "P4E-COMP-REREV2-F4"
    ]
  },
  "resolutionEvidence": {},
  "counters": {
    "partialReadyClosures": 0,
    "reviewerScopeExpansions": 0,
    "sameClaimCorrections": 0,
    "nonDecreasingBlockerTransitions": 0
  },
  "claims": [
    {
      "claimId": "P4E-AMENDMENT1-F1-F4-REPAIR-CONTRACT",
      "claimClass": "DOCUMENTATION_ONLY",
      "proofClass": "PROPOSAL_ONLY_NO_RUNTIME_READINESS",
      "evidenceRef": "docs/reviews/CVF_P4E_IDENTITY_CONVERSATION_ROUTING_COMPLETION_2026-09-09.md#repair-generation-2-rereview"
    }
  ],
  "requiredDisposition": "CONTINUE_BOUNDED",
  "successorScope": "INTEGRATED_ROOT_CONTRACT"
}
```

## Purpose

Amend only the uncloseable authority and gate sequencing in the 2026-09-09
P4-E Work Order, then define one final consolidated repair for completion-review
round-3 findings `P4E-COMP-REREV2-F1` through `P4E-COMP-REREV2-F4`.

The accepted SPEC R1-R21 and AC-01-AC-16 remain unchanged. The agent chooses
the internal repair design inside those invariants; this amendment does not
prescribe private reasoning or unnecessary implementation structure.

## Controlling Authority

1. `docs/specs/P4E_IDENTITY_CONVERSATION_ROUTING_SPEC.md`, SHA-256
   `de3af4a90425ee70f8e285fc31e12774497f7a190b776beab3ed3d32fdc90618`.
2. `docs/reviews/CVF_P4E_IDENTITY_CONVERSATION_ROUTING_COMPLETION_2026-09-09.md`,
   SHA-256 `4ba551a174d696613f476e9f0c5682984409c0667386765f0f1c2182d640de18`.
3. `docs/implementation/P4E_IDENTITY_CONVERSATION_ROUTING_EXACT_MANIFEST_AMENDMENT_1_2026-09-10.md`.
4. CVF ADIF-0057 and return-time closeability learning at private-provenance
   material commit `3fcd426dc7c2c6d03fc915b884711df118a0563f`.
5. The operator's 2026-09-10 approval to learn first, synchronize, amend,
   independently review, and then perform the project repair.

## Superseded Clauses

This amendment supersedes only these clauses of the original Work Order:

- the exact changed-set ceiling becomes original paths 1-94 plus additive
  amendment paths 95-109;
- every reference to worker paths 15-80 means original paths 15-80 plus
  additive worker paths 95-109;
- original line 462's stale `Path 75` label is corrected to original path 76,
  `tests/integration/test_p4e_workspace_composition.py`;
- catalog PASS is no longer a worker-return prerequisite when the only drift is
  caused by this P4-E changed set and only closer-owned paths 93-94 can repair
  it; and
- the closer regenerates catalog paths 93-94 before the final full-suite and
  closure claim.

Every other original requirement, forbidden action, secret boundary, commit
mode, reviewer independence rule, and claim ceiling remains in force.

## Repair Scope

The REPAIR_WORKER may modify only original paths 15-80 and amendment paths
95-109. It must preserve valid earlier repairs and resolve these root causes:

### R3-F1 - One authoritative authentication context

- Use one authoritative signature and timestamp location for sender-aware
  ingress.
- Freshness and HMAC verification must consume the same signed timestamp and
  signature.
- Reject outer/inner mismatch, stale signed timestamp, arbitrary non-empty
  substitute signature, malformed evidence, and key-state mismatch.
- Positive webhook proof must traverse the actual route through durable
  proposal/observation persistence; a recording fake plus manual ledger insert
  cannot be called end-to-end.

### R3-F2 - Exact authority and evidence accounting

- Retain the fifteen amendment paths; do not delete useful work to match the
  obsolete ceiling.
- Reconcile worker-return expected/actual paths against the effective 109-path
  manifest and report reviewer-owned path 82 separately.
- Correct the trace-heading collision by ensuring the first actual trace
  heading is the real Agent Operation Trace section, not quoted read-ahead
  text.
- Reconcile network/install counters with cache/offline evidence or truthful
  nonzero values; never infer zero from intent.

### R3-F3 - Complete write-time CAS

- `ProposeInput` and `P4eMappingCommandService.propose` require the expected
  aggregate version mandated by SPEC R8/R9.
- Binding replacement must carry an expected binding version into the store
  and enforce it in the write predicate, on InMemory and SQL backends.
- Stale-claim recovery and rollback must require and CAS the exact proposal-
  lineage digest as required by R12, in addition to state/version/token fields
  applicable to that transition.
- Add positive, stale-version, wrong-lineage, wrong-token, wrong-state,
  duplicate, rollback, and backend-parity tests for the actual public/service
  signatures.

### R3-F4 - Honest completion evidence

- Path 80 must distinguish focused/integration/PostgreSQL evidence from a full
  end-to-end path and must not overclaim a fake-router test.
- Record exact command, exit code, counts, environment and disposable
  PostgreSQL cleanup.
- Path 102 must fail closed when the local `postgres:16-alpine` image is
  absent. It must not call or inherit a helper that performs `docker pull`;
  missing local image returns `BLOCKED_WITH_REASON` before starting a
  container or making network access.
- Return no `COMPLETE_PENDING_REVIEW` while a mandatory gate fails. Under the
  catalog-only condition defined by the manifest amendment, retain terminal
  verdict `BLOCKED_WITH_REASON` and add the non-terminal supplemental field
  `technicalRepairDisposition: COMPLETE_PENDING_CATALOG_AND_REVIEW`.

## Required Verification

Run the narrowest relevant tests while repairing, then before return execute
these exact commands from the project root, in order:

```powershell
python -m pytest -q tests/unit/test_p4e_invariants.py tests/unit/test_p4e_identity_models.py tests/unit/test_p4e_identity_service.py tests/unit/test_p4e_conversation_routing.py tests/unit/test_p4e_sender_key_retirement.py tests/security/test_p4e_sender_evidence.py tests/security/test_p4e_privacy_disclosure.py tests/contract/test_p4e_contract_schemas.py tests/integration/test_p4e_backend_parity.py tests/integration/test_p4e_workspace_composition.py tests/integration/test_p4e_transaction_protocol.py tests/unit/test_p4e_dependency_boundary.py tests/integration/test_p4e_claim_owner_cas.py tests/integration/test_p4e_command_audit_and_idempotency.py tests/integration/test_p4e_inmemory_parity.py tests/integration/test_p4e_webhook_sender_aware_ingress.py tests/integration/test_p4e_webhook_sender_aware_negative.py
docker image inspect postgres:16-alpine
python scripts/run_p4e_postgres_live_roundtrip.py --json
python -m pytest -q tests/integration/test_p4e_workspace_composition.py
python scripts/check_invariant_families.py --json
python -m pytest -q tests/unit/test_invariant_family_contract.py tests/integration/test_invariant_family_repository_guard.py
python scripts/check_project_knowledge.py
python scripts/check_session_state.py
python scripts/check_file_size.py
python scripts/testing/validate_repository.py
python scripts/generate_catalog.py --check
python -m pytest -q
git diff --check
git status --short
```

If the catalog check, repository validation, and full suite fail only because
catalog paths 93-94 need canonical regeneration,
record the exact single cause, keep terminal verdict `BLOCKED_WITH_REASON`, and
use only the supplemental pending-catalog disposition defined above. Any other
failure is blocking. Do not run an Alibaba/provider API call: this repair
asserts no AI-governance behavior and requires no provider output. Local
PostgreSQL Docker proof is required.

## Gate-To-Role Closeability Matrix

| Gate or mutation | Owner now | Timing | Result required from worker |
|---|---|---|---|
| Source/security/CAS repair | REPAIR_WORKER | BUILD | PASS |
| Worker return | REPAIR_WORKER | BUILD return | Truthful pending-review evidence |
| Independent successor completion review | INDEPENDENT_COMPLETION_REVIEWER | REVIEW | Start at round 1 for the explicitly authorized successor cluster; apply normal review-cost stop rules |
| Catalog canonical generation | CLOSER | after technical acceptance | PASS before final full suite/commit |
| Final full suite | CLOSER | after catalog generation | PASS before closure |
| Commit | COMMIT_STEWARD | after reviewer/closer acceptance | Exact accepted set only |
| Session/status synchronization | SESSION_SYNC_STEWARD | after material commit | Current state only |

## Successor Repair Assignment And Review-Cost Lineage

This amendment does not silently reset or extend the predecessor review chain.
The predecessor completion review remains immutable evidence with
`reviewRoundCount: 3`, `workerRepairTurnCount: 2`, and
`stopDisposition: CONTINUE_NEW_CRITICAL_EVIDENCE`. Its newly established
security and exact-authority root causes required operator/orchestrator action,
which the operator supplied on 2026-09-10.

The canonical dispatch block above opens the separately authorized successor
assignment as REWORK generation/round 1, bound to the predecessor review hash
and the new successor root-cause cluster. Its semantic-convergence disposition
is `OPERATOR_AUTHORIZED_SUCCESSOR_FOR_NEW_CRITICAL_EVIDENCE`; its authority
link is the operator approval plus independently accepted Amendment 1; and its
scope is the exact F1-F4 set above. Apply the current Review Cost standard
within this successor cluster and never label its first completion review as
predecessor round 4.

## Stop Conditions

Stop and return to the orchestrator if repair requires any implementation path
outside the effective worker ceiling, a protected or later-role path,
dependency installation, provider/network access, secret
use, shared database, destructive action, SPEC/design change, risk escalation,
Phase 5, XR1, catalog schema migration, public action, deployment, or commit.

The independent successor review starts at its recorded round 1 and follows the
current Review Cost standard. It must preserve predecessor telemetry and must
not describe itself as predecessor round 4. Any later escalation or repair is
governed by the successor cluster's own recorded telemetry and stop rules.

## Worker Return Requirements

Update original path 80 rather than creating another worker-return artifact.
Include exact changed paths, manifest reconciliation, tests and counts,
PostgreSQL container/cleanup evidence, catalog/full-suite disposition, external
effect counters, no-commit statement, and a claim boundary. Leave staging empty.

## Reviewer And Commit Boundary

This amendment must receive independent authorization review before repair.
The repair worker cannot self-review, edit reviewer path 82, regenerate catalog
paths 93-94, change continuity/status paths 83-92, stage, commit, push, deploy,
or declare closure.

## Public Export Disposition

DEFERRED_PRIVATE_ONLY

Reason: private project repair packet; no public-sync or catalog publication.

## Claim Boundary

This is a pending amendment, not repair authority until independently accepted.
It changes no SPEC behavior, proves no implementation result, makes no provider
or production claim, and authorizes no commit or deployment.
