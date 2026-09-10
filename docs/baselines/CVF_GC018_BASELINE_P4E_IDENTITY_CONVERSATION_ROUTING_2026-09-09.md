# CVF GC-018 Baseline - P4-E Identity Mapping And Conversation Routing

Memory class: governed-dispatch-baseline

Status: READY_FOR_REVIEW

Batch ID: P4E-IDENTITY-CONVERSATION-ROUTING

Dispatch base head: e367bc996e6fceaff08d23af34c2d5d8dada0ded

Commit mode: WORKER_MUST_NOT_COMMIT

Decision owner: ORCHESTRATOR

Reviewer owner: INDEPENDENT_AUTHORIZATION_REVIEWER

Worker target: IMPLEMENTATION_WORKER

## Purpose

Freeze the source, risk, dependency, role, external-effect, and changed-set
boundary used to author the P4-E Work Order. This baseline permits independent
authorization review of that packet. It grants no BUILD authority.

## Scaffold Provenance Block

| Field | Value |
| --- | --- |
| scaffoldHelperCommand | `python governance/compat/build_dispatch_packet_scaffold.py --packet-kind generic-worker-dispatch --batch-id P4E-IDENTITY-CONVERSATION-ROUTING --title "P4-E Identity Mapping And Conversation Routing" --date 2026-09-09 --base e367bc996e6fceaff08d23af34c2d5d8dada0ded --commit-mode WORKER_MUST_NOT_COMMIT --stdout` |
| generatedProfile | generic-worker-dispatch plus WORKER_MUST_NOT_COMMIT no-commit worker profile |
| generatedSkeletonStatus | USED_AS_STARTING_POINT |
| manualEditsAfterScaffold | Replaced placeholders with the accepted P4-E SPEC identity, exact project paths, dependency findings, R2 separation, zero-external-effect limits, and the three rereview carry-forward controls. |
| checkerReadAheadConfirmation | `check_work_order_dispatch_quality.py`; its core, range, source, artifacts, lifecycle and tables modules; `check_agent_handoff_boundary.py`; `check_review_cost_control.py`; `check_adif_defect_registry_disclosure.py` |
| docOnlyNewFields | None; project-specific facts use existing headings and tables. |
| claimBoundary | Dispatch authoring evidence only; no application, runtime, provider, live, deployment, production, public-catalog, Web, or external CLI/MCP capability claim. |

## ADIF Defect Registry Disclosure

Resolver query: taskClass=`implementation`, role=`IMPLEMENTATION_WORKER`, lifecyclePhase=`BUILD`

Returned defects: NONE_RETURNED

| Field | Value |
| --- | --- |
| Resolver command | `python governance/compat/run_adif_defect_resolver.py --task-class implementation --role IMPLEMENTATION_WORKER --lifecycle-phase BUILD --risk-ceiling HIGH --json` |
| Returned defect count | 0 |
| Returned defects | NONE_RETURNED |
| Disclosed defectIds | NONE |
| Dispatch impact | No matching defect packet was returned. The Work Order still carries current literal-shape, no-commit, shared-worktree, source, review-cost, and handoff controls directly. |

## Checker Source Read-Ahead Block

| Field | Value |
| --- | --- |
| applicableCheckersRead | `governance/compat/check_work_order_dispatch_quality.py`; `check_work_order_dispatch_quality_core.py`; `check_work_order_dispatch_quality_range.py`; `check_work_order_dispatch_quality_source.py`; `check_work_order_dispatch_quality_artifacts.py`; `check_work_order_dispatch_quality_lifecycle.py`; `check_work_order_dispatch_quality_tables.py`; `check_agent_handoff_boundary.py`; `check_review_cost_control.py`; `check_adif_defect_registry_disclosure.py` |
| literalTokensReviewed | Dispatch Prompt Envelope; Source Verification Block; Intake Role Routing Decision; Reviewer Closure Conversion; Worker Return Packet Shape Contract; WORKER_MUST_NOT_COMMIT; REQUIRED_TRIGGERED; AUTHORITY_SCOPE_EXPANSION; PRE_EXECUTION_REVIEW; EXPLICIT_LANE_HANDOFF; COMPLETE_INITIAL_ACCEPTANCE_MATRIX |
| gateRunPurpose | Confirm the authored packet against known machine shapes; gates are not used for first discovery. |
| claimBoundary | Read-ahead covers dispatch artifact structure only, not implementation correctness or runtime behavior. |

## Source Verification Block

| Claimed item | Claim type | Source file | Verified line/section | Verified path or symbol | Owning interface/function/schema | Disposition |
| --- | --- | --- | --- | --- | --- | --- |
| Accepted P4-E behavior | normative contract | `docs/specs/P4E_IDENTITY_CONVERSATION_ROUTING_SPEC.md` | R1-R21 and AC-01-AC-16 | SHA-256 `de3af4a90425ee70f8e285fc31e12774497f7a190b776beab3ed3d32fdc90618` | P4-E SPEC | ACCEPT |
| Independent SPEC acceptance | review authority | `docs/decisions/SPEC_REREVIEW_2026-09-09_P4E_IDENTITY_CONVERSATION_ROUTING.md` | Disposition and final matrix | SHA-256 `e9c21bd7c5627a0529b4d15d5a1533bd834ec886d13002c77ecdaa2a8094c3cc` | independent SPEC rereviewer | ACCEPT |
| Mapping outcomes | invariant authority | `docs/cvf/invariants/p4e-mapping-action-outcomes.json` | complete file | SHA-256 `ea2af8122016a7b8ee10d9a8aa097f1b692a168a4914425172c555cd4d003e1a` | P4E-MAPPING-ACTION-OUTCOMES | ACCEPT |
| Identity outcomes | invariant authority | `docs/cvf/invariants/p4e-identity-resolution-outcomes.json` | complete file | SHA-256 `4ef64cf1f53633974b0e585018148a8f6bbe7a16ce4683329aa29d51c0000bdc` | P4E-IDENTITY-RESOLUTION-OUTCOMES | ACCEPT |
| Placement outcomes | invariant authority | `docs/cvf/invariants/p4e-placement-outcomes.json` | complete file | SHA-256 `fd351b6670292e82835b4ec34c270768174758a6d8a3f1558e4e4b3a8ec8cc56` | P4E-CONVERSATION-PLACEMENT-OUTCOMES | ACCEPT |
| Current process-local proposal store | implementation source | canonical project source: `apps/workspace-api/src/workspace_api/external_ingress/repository.py` | line 13 | `InMemoryExternalIngressRepository` | existing P4-C test/local store | ACCEPT |
| Current production composition | implementation source | canonical project source: `apps/workspace-api/src/workspace_api/main.py` | line 41 | `include_router(external_ingress_router)` | Workspace API composition root | ACCEPT |
| Current permission registry | implementation source | canonical project source: `packages/cvf-runtime/src/cvf_runtime/permission.py` | line 28 | `_ACTION_MIN_ROLE` | canonical action minimum-role map | ACCEPT |

## Negative Search And Collision Discipline

| Check | Evidence | Disposition |
| --- | --- | --- |
| Work Order path | `Test-Path docs/work_orders/CVF_AGENT_WORK_ORDER_P4E_IDENTITY_CONVERSATION_ROUTING_2026-09-09.md` returned false before authoring. | CREATE_NEW_EXACT_PATH |
| Baseline path | `Test-Path docs/baselines/CVF_GC018_BASELINE_P4E_IDENTITY_CONVERSATION_ROUTING_2026-09-09.md` returned false before authoring. | CREATE_NEW_EXACT_PATH |
| Existing P4-E authority | `rg --files docs` found accepted DESIGN, SPEC, matrices, review, and rereview surfaces; these are reused and not duplicated. | REUSE_CANONICAL_SURFACES |
| Runtime collision | Source search found the current process-local ingress repository, Workspace API composition root, Integration Edge sender seam, Operations Ledger, and permission registry. | AMEND_EXISTING_OWNERS_NO_SECOND_LIVE_OWNER |

## Dependency Release Evidence

| Dependency | Evidence | Disposition |
| --- | --- | --- |
| DESIGN | canonical digest `2d0975a301a15c7b8a85eba121410391ddca2f067b16d9c5089d79edb9c397b9` and independent DESIGN_REVIEW_PASS | RELEASED |
| SPEC | canonical digest `de3af4a90425ee70f8e285fc31e12774497f7a190b776beab3ed3d32fdc90618` | RELEASED |
| SPEC rereview | `SPEC_REVIEW_PASS`; 7/7 findings closed; zero open/new/waiver | RELEASED |
| Work Order authorization | not yet independently reviewed | HELD_PRE_EXECUTION_REVIEW |

## Dual Agent Surface Matrix

| Consumer class | Interface or owner surface | Authority and risk boundary | Evidence | Adapter boundary | Disposition |
| --- | --- | --- | --- | --- | --- |
| `INTERNAL_AGENT` | project repository exact paths in the paired Work Order | R2; no external effect; worker cannot commit or approve | accepted SPEC, source pins, deterministic and disposable-database tests | internal project code only; Integration Edge service assertion is an application boundary, not an agent adapter | CONTRACT_ONLY |
| `EXTERNAL_AGENT_CLI_MCP` | no CLI/MCP adapter is in P4-E scope | no ingress, credential, approval, mutation, receipt, raw-data, provider, or public authority | explicit exclusion in the Work Order | no external-agent adapter may be created or inferred | N/A_WITH_REASON |

## Claim Boundary

This baseline authorizes only a bounded Work Order proposal and its independent
authorization review. BUILD, dependency installation, credentials, provider
calls, external network, deployment, production use, commit by the worker,
self-review, and FREEZE remain unauthorized.

## Public Export Disposition

DEFERRED_PRIVATE_ONLY

Reason: this baseline makes no CVF public-catalog export claim. A normal push of
the first-party project repository does not turn this packet into a CVF public
catalog release.
