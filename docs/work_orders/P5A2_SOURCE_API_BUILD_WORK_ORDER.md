# P5-A2 source API — bounded implementation Work Order

Status: DISPATCH_READY
Date: 2026-10-26; Root ORCHESTRATOR/SPEC_AUTHOR/WORK_ORDER_AUTHOR; R2.
Baseline59d63c66ce170ede7259c67a4f770d96e623f921. Operator requests continued
roadmap execution without routine tranche approvals. This packet requires
independent admission, normal dispatch and actual-SHA continuity before BUILD.

## Product Milestone Binding

Canonical complete current binding, acceptance and G01–G14 reconciliation:
docs/specs/P5A2_SOURCE_API_BUILD_SPEC.md. Full outcome is integrated authorized
scheduled forecasts/history/freshness/uncertainty/lineage/exact human approval;
this slice implements only bounded source-read G06/G11 and HTTP G13 cases.
G01/A7/G02 blocked, G03 business fit/G04 operational integration/G05 production
coverage/mode/retention/SQLite positive UNKNOWN; scheduler, operational signals/
accuracy/monitoring, UI, exact approval and integrated drills remain open;
G14 provider HELD. All Root/backend/UI/operator and P5-A2/P5-B/C/D owners and
destinations remain in the canonical table; Phase5 stays0/5.
Concrete caller outcome: authenticated, assigned source-read inspection or exact
nonleaking readiness refusal over real HTTP, unblocking the G11 UI caller.
Normal composition has no operational authority; fixture positives are explicit
test-only injection. Do not rename a refusal diagnostic as integrated reporting.
Finite stop: independently accepted source closure, then return directly to G11
caller/UI work under its own bounded contract; no repeat support audit loop.

## Exact worker paths and size budget

IMPLEMENTATION_WORKER / REPAIR_WORKER may change only:
- apps/workspace-api/src/workspace_api/application/proactive_source_access.py
- apps/workspace-api/src/workspace_api/application/proactive_source_preview.py
- apps/workspace-api/src/workspace_api/api/proactive/__init__.py
- apps/workspace-api/src/workspace_api/api/proactive/router.py
- apps/workspace-api/src/workspace_api/api/proactive/response.py
- apps/workspace-api/src/workspace_api/main.py
- apps/workspace-api/src/workspace_api/config.py
- apps/workspace-api/src/workspace_api/dependencies.py
- packages/cvf-runtime/src/cvf_runtime/permission.py
- tests/unit/p5a2_source_api_helpers.py
- tests/integration/test_p5a2_source_api_identity.py
- tests/integration/test_p5a2_source_api_receipts.py
- tests/integration/test_p5a2_source_api_release.py
- tests/unit/test_p5a2_source_api_transport.py
- docs/decisions/P5A2_SOURCE_API_BUILD_WORKER_RETURN_2026-10-26.md

Every executable <=300 lines, target<=250. Access/preview split is foreseeable
and already covered; router/response and four test surfaces are separate.
No extra helper/file split, broad refactor or other path without a consolidated
Root amendment and independent review BEFORE mutation. Permission change is
only canonical proactive.source.read at viewer bar; config only the server
instance identity; main/dependencies only new router/context/clock composition.
Global JWT/login, source selection, native snapshot algorithms and pure numeric
code remain unchanged. Preserve existing tests; no xfail/skip/deselection bypass.

## Root / independent ownership

Root owns this WO, P5A2_SOURCE_API_BUILD_SPEC.md, the exact admission JSON and
frozen tests/fixtures/p5a2_source_api_oracle.json; new active handoff
SESSION/handoffs/AGENT_HANDOFF_P5A2_SOURCE_API_BUILD_2026-10-26.md and canonical
SESSION state/bootstrap/memory + compatibility mirror; IMPLEMENTATION_STATUS;
docs/PROJECT_INDEX.md; docs/implementation/EXECUTION_ROADMAP.md; knowledge
PROJECT_CONTEXT/manifest; catalog ARTIFACT_REGISTRY, MODULE_REGISTRY_DETAIL,
MODULE_CATALOG_DETAIL and generated INDEX/MODULE_REGISTRY/MODULE_CATALOG.
When detailed module facts change, Root runs detailed generator --write, kit
projection --write, manager -Write in order, then all three checks. Handoff
artifact pointer must match the mirror before manager generation.

Root alone materializes the preapproved family patch at
docs/cvf/invariants/p5a2-scoped-source-outcomes.json and the digest constant in
docs/specs/p5a2_scoped_source_invariant_pin.py and
apps/workspace-api/src/workspace_api/application/proactive_source_receipt.py.
The latter two edits are digest literals only, not validator behavior changes.
Independent reviewer alone owns
docs/decisions/P5A2_SOURCE_API_BUILD_REVIEW_2026-10-26.md.
Old oracles/evidence/attempts, public Core, hook, parent/source identity SPEC,
auth tokens and unlisted source remain read-only. No push/deployment.

## Frozen contract and staged binding gate

Follow accepted P5A2_SOURCE_API_IDENTITY_SPEC and new BUILD_SPEC exactly.
Admission docs/decisions/P5A2_SOURCE_API_BUILD_ADMISSION_2026-10-26.json stores
the baseline and immutable source/oracle pins, complete metadata-only family
patch, deterministic rendering recipe and expected final LF-normalized canonical
digest. Reconstruct and review the entire proposed matrix before BUILD; a digest
or path list alone is not enough. All original outcome/shape/domain/relation/
mutation rules remain identical. The family stays the semantic owner.

Current registered matrix9b3 and existing consumers remain active for dispatch.
After committed dispatch + actual-SHA continuity/clean range, worker writes the
authorized real source and test implementations, compiles inertly, then STOPS
before first focused tests and notifies Root FILES_READY_FOR_BINDING.
No placeholder tests and no claim that the HTTP binding is already active.
Root applies only the exact preapproved patch and two old pin literals; worker
HTTP response consumer already contains the admitted final digest symbol.
Root refreshes actual catalog facts. Independent reviewer verifies actual final
matrix bytes/digest, real consumer/evidence paths, native source and HTTP mutation
binding, ownership symbol, source/oracle pins and guard compliance. After that
bounded materialization PASS, Root may release focused tests and repairs under
the same WO. Any deviation in patch, semantics or paths returns to review.

## Required evidence / scope limits

Exact complete new oracle rawSHA5cc32b1a0484460c7eafb8d23d7112f19ae713699dfd560bb98c4b00411e49fe;
Root independently verified both new scope/coverage/source receipts before
implementation. Do not regenerate expectations from new code. Real JWT signing
and verification/current stored users, real native memory fixture adapters and
HTTP TestClient required. No principal-dependency bypass or fabricated source
result. Positive synthetic authority is test-only, never runtime fixture import.
Run new focused tests plus four old source paths and both generic invariant
tests; preserve all failures and native84 mutations. Source/auth/release/byte/
OpenAPI/cache/write-zero cases are enumerated in BUILD_SPEC. Collect raw HTTP
positive/refused bodies and complete native/HTTP mutation totals in return.
No physical PG, Docker, provider, package installation, real credential, .env,
model/CSV, production data, browser or release effect. No AI governance claim.
Old physical/provider ceilings remain spent; no operational READY mode evolution.

Return exact file hashes/lines, positive/negative/mutation evidence, failures,
full milestone remainders/owners and standalone native return-time recheck.
Independent source review consolidates predictable findings before repair;
same-scope repairs continue without routine operator approvals. At repair round3
without an independent new root cause: REVIEW_COST_ESCALATION_REQUIRED.
Root owns normal precommit full tests and all commits. After source PASS:
normal exact material commit, independent terminal actual review, dedicated
five-path actual-SHA continuity, independent clean split-range closure. Keep
the actual material SHA in the sole GC020 handoff marker; never a planned hash.

## Invariant-Family Proof

## Amendment 1 — exact OpenAPI regression-chain integration

The first normal material hook refused the commit: 15 historical OpenAPI
assertions failed, 3370 passed, 148 existing skips, 4 warnings in437.50s.
Retain `.venv/p5a2-api-source-material-20261026.log`; HEAD remains7f3c63d.
The new endpoint and two structural schemas must be verified and removed before
the historical exact-delta chain. No historical golden SHA may be refreshed.
This is one consolidated same-outcome/R2/no-effect repair, not new product scope.
The Product Milestone Binding above and frozen BUILD SPEC's full G01–G14 table
apply: only G06/G11/HTTP G13 source acceptance; all remainders/owners unchanged,
Phase5 0/5. Finite stop: green unchanged normal hook, normal source closure,
then directly G11 UI under its own contract.

Additional exact REPAIR_WORKER paths:
- tests/unit/test_report_export_openapi.py — call the verified newer source
  delta helper before its existing export-only verification/removal.
- tests/unit/test_p5a2_source_openapi_contract.py — real exact source path/two
  schema checks, structural assertions and closed negative regression corpus.
- Existing worker-return path above — append Amendment1 evidence, original
  failure and role continuity; preserve historical evidence and recheck.

Root alone freezes tests/fixtures/p5a2_source_openapi_delta.json from the reviewed
structural contract before repair code, records its hash/full content admission
and independently proves removal returns exactly to the prior OpenAPI golden.
Reviewer must inspect the complete fixture and independent structural facts;
a digest alone is insufficient. No old golden, application code, source oracle,
family semantics or private/control path changes. Helpers may not delete broad
prefixes, prune arbitrary unused schemas, swallow mismatches or hide unrelated
paths/old operation changes. Missing/changed source operation, security, query,
response, each schema and extra method must refuse before any deletion. Unknown
schema/path and changed old operations remain for the historical hash to reject.
Avoid circular test imports; all executable files remain <=300 lines.

WORK_ORDER_AUTHOR first records this consolidated amendment and proposed frozen
delta in admission; independent reviewer authorization and native return-time
recheck must pass before REPAIR_WORKER mutation. The existing focused test gate
now additionally runs all ten historical OpenAPI modules plus the new module,
then the unchanged normal full precommit. Root owns staging/commit. No new
dispatch effect or standalone support tranche is opened; existing committed
dispatch remains authority for this dependent repair after amendment admission.
The pre_commit and focused_checker_tests rows below include the two exact
additional test paths; pre_commit also names the Root fixture. The existing
worker_return_fast row continues to bind the return artifact. Repair owner,
phase and commit owner remain as declared.

## Invariant-Family Proof (continued)

Follow docs/cvf/INVARIANT_FAMILY_STANDARD.md and registered
P5A2-SCOPED-SOURCE-OUTCOMES. Admission contains the recoverable pre-BUILD exact
extension and final pin; no second matrix authority. HTTP bare receipt uses
native validator/emitter, with structural OpenAPI parity only. Native/HTTP
consumers must reject full mutations for both outcomes, no added payload field.
API-only1MiB SCOPE_INCOMPLETE condition is an accepted source contract binding;
no operational-mode outcome or shape field changes. Independent reviewer samples
raw emitted positives/refusals, recomputes final native LF pin and reruns corpus.

## Gate-To-Role Closeability Contract

closeabilityContractVersion: cvf.gate-role-closeability@1.0.0
closeabilityDisposition: CLOSEABLE
returnTimeRecheck: REQUIRED_BEFORE_REPAIR
implementationTopologyPolicy: EXACT_PATHS_WITH_NO_FORESEEABLE_SPLIT
foreseeableFileSplitDisposition: NOT_REQUIRED_UNDER_SIZE_BUDGET

| gateId | mustPassBy | repairOwner | repairPhase | mutationSurface | topology | commitOwner | commitPhase | dependsOn |
|---|---|---|---|---|---|---|---|---|
| authorization_review | PRE_DISPATCH | work-order-author | PRE_DISPATCH | docs/work_orders/P5A2_SOURCE_API_BUILD_WORK_ORDER.md | EXACT_PATHS | commit-steward | DISPATCH_COMMIT | NONE |
| pre_dispatch_gate | PRE_DISPATCH | orchestrator | PRE_DISPATCH | docs/specs/P5A2_SOURCE_API_BUILD_SPEC.md;docs/work_orders/P5A2_SOURCE_API_BUILD_WORK_ORDER.md;docs/decisions/P5A2_SOURCE_API_BUILD_ADMISSION_2026-10-26.json;tests/fixtures/p5a2_source_api_oracle.json | EXACT_PATHS | commit-steward | DISPATCH_COMMIT | authorization_review |
| dispatch_continuity | IMPLEMENTATION | session-sync-steward | IMPLEMENTATION | SESSION/handoffs/AGENT_HANDOFF_P5A2_SOURCE_API_BUILD_2026-10-26.md material-SHA marker | EXACT_PATHS | session-sync-steward | DISPATCH_CONTINUITY_COMMIT | pre_dispatch_gate |
| pre_implementation_autorun | IMPLEMENTATION | orchestrator | IMPLEMENTATION | SESSION/handoffs/AGENT_HANDOFF_P5A2_SOURCE_API_BUILD_2026-10-26.md;docs/work_orders/P5A2_SOURCE_API_BUILD_WORK_ORDER.md | EXACT_PATHS | commit-steward | MATERIAL_COMMIT | dispatch_continuity |
| family_materialization | IMPLEMENTATION | orchestrator | IMPLEMENTATION | docs/cvf/invariants/p5a2-scoped-source-outcomes.json;docs/specs/p5a2_scoped_source_invariant_pin.py;apps/workspace-api/src/workspace_api/application/proactive_source_receipt.py | EXACT_PATHS | commit-steward | MATERIAL_COMMIT | pre_implementation_autorun |
| am1_authorization | IMPLEMENTATION | work-order-author | IMPLEMENTATION | docs/work_orders/P5A2_SOURCE_API_BUILD_WORK_ORDER.md;docs/decisions/P5A2_SOURCE_API_BUILD_ADMISSION_2026-10-26.json;tests/fixtures/p5a2_source_openapi_delta.json | EXACT_PATHS | commit-steward | MATERIAL_COMMIT | family_materialization |
| focused_checker_tests | WORKER_RETURN | implementation-worker | IMPLEMENTATION | apps/workspace-api/src/workspace_api/application/proactive_source_access.py;apps/workspace-api/src/workspace_api/application/proactive_source_preview.py;apps/workspace-api/src/workspace_api/api/proactive/router.py;apps/workspace-api/src/workspace_api/api/proactive/response.py;tests/integration/test_p5a2_source_api_identity.py;tests/integration/test_p5a2_source_api_receipts.py;tests/integration/test_p5a2_source_api_release.py;tests/unit/test_p5a2_source_api_transport.py;tests/unit/test_report_export_openapi.py;tests/unit/test_p5a2_source_openapi_contract.py | EXACT_PATHS | commit-steward | MATERIAL_COMMIT | dispatch_continuity,pre_implementation_autorun,family_materialization,am1_authorization |
| adif_integrity | WORKER_RETURN | implementation-worker | IMPLEMENTATION | docs/decisions/P5A2_SOURCE_API_BUILD_WORKER_RETURN_2026-10-26.md | EXACT_PATHS | commit-steward | MATERIAL_COMMIT | dispatch_continuity |
| worker_return_fast | WORKER_RETURN | implementation-worker | WORKER_RETURN | docs/decisions/P5A2_SOURCE_API_BUILD_WORKER_RETURN_2026-10-26.md | EXACT_PATHS | commit-steward | MATERIAL_COMMIT | focused_checker_tests,adif_integrity |
| reviewer_fast | REVIEW | reviewer | REVIEW | docs/decisions/P5A2_SOURCE_API_BUILD_REVIEW_2026-10-26.md | EXACT_PATHS | commit-steward | MATERIAL_COMMIT | worker_return_fast |
| pre_commit | PRE_MATERIAL_COMMIT | repair-worker | PRE_MATERIAL_COMMIT | apps/workspace-api/src/workspace_api/application/proactive_source_access.py;apps/workspace-api/src/workspace_api/application/proactive_source_preview.py;apps/workspace-api/src/workspace_api/api/proactive/__init__.py;apps/workspace-api/src/workspace_api/api/proactive/router.py;apps/workspace-api/src/workspace_api/api/proactive/response.py;apps/workspace-api/src/workspace_api/main.py;apps/workspace-api/src/workspace_api/config.py;apps/workspace-api/src/workspace_api/dependencies.py;packages/cvf-runtime/src/cvf_runtime/permission.py;tests/unit/p5a2_source_api_helpers.py;tests/integration/test_p5a2_source_api_identity.py;tests/integration/test_p5a2_source_api_receipts.py;tests/integration/test_p5a2_source_api_release.py;tests/unit/test_p5a2_source_api_transport.py;docs/decisions/P5A2_SOURCE_API_BUILD_WORKER_RETURN_2026-10-26.md;docs/decisions/P5A2_SOURCE_API_BUILD_REVIEW_2026-10-26.md;docs/cvf/invariants/p5a2-scoped-source-outcomes.json;docs/specs/p5a2_scoped_source_invariant_pin.py;apps/workspace-api/src/workspace_api/application/proactive_source_receipt.py;docs/catalog/MODULE_REGISTRY_DETAIL.json;docs/catalog/MODULE_CATALOG_DETAIL.md;docs/catalog/MODULE_REGISTRY.json;docs/catalog/MODULE_CATALOG.md;docs/INDEX.md;docs/PROJECT_INDEX.md;docs/catalog/ARTIFACT_REGISTRY.json;IMPLEMENTATION_STATUS.json;knowledge/PROJECT_CONTEXT.md;knowledge/manifest.json;SESSION/ACTIVE_SESSION_STATE.json;SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json;SESSION/SESSION_MEMORY.md;CVF_SESSION/ACTIVE_SESSION_STATE.json;SESSION/handoffs/AGENT_HANDOFF_P5A2_SOURCE_API_BUILD_2026-10-26.md;docs/implementation/EXECUTION_ROADMAP.md;tests/unit/test_report_export_openapi.py;tests/unit/test_p5a2_source_openapi_contract.py;tests/fixtures/p5a2_source_openapi_delta.json | EXACT_PATHS | commit-steward | MATERIAL_COMMIT | reviewer_fast |
| terminal_completion_review | POST_MATERIAL | reviewer | POST_MATERIAL | docs/decisions/P5A2_SOURCE_API_BUILD_REVIEW_2026-10-26.md | EXACT_PATHS | commit-steward | CORRECTIVE_MATERIAL_COMMIT | pre_commit |
| continuity | CONTINUITY_COMMIT | session-sync-steward | CONTINUITY_COMMIT | SESSION/handoffs/AGENT_HANDOFF_P5A2_SOURCE_API_BUILD_2026-10-26.md;SESSION/ACTIVE_SESSION_STATE.json;SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json;SESSION/SESSION_MEMORY.md;CVF_SESSION/ACTIVE_SESSION_STATE.json | EXACT_PATHS | session-sync-steward | CONTINUITY_COMMIT | terminal_completion_review |
| committed_range_closure | POST_MATERIAL_CLOSURE | reviewer | POST_MATERIAL_CLOSURE | SESSION/handoffs/AGENT_HANDOFF_P5A2_SOURCE_API_BUILD_2026-10-26.md;docs/decisions/P5A2_SOURCE_API_BUILD_REVIEW_2026-10-26.md | EXACT_PATHS | session-sync-steward | CONTINUITY_COMMIT | continuity |
