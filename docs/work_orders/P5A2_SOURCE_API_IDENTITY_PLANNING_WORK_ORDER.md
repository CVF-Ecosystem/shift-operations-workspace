# P5-A2 source API identity â€” bounded planning Work Order

Status: IMPLEMENTED_BOUNDED_PLANNING
Date: 2026-10-26. Root ORCHESTRATOR/SPEC_AUTHOR/WORK_ORDER_AUTHOR; R2.
Authority: operator roadmap continuation and current next allowed INTAKE/SPEC.
No runtime BUILD, API mounting, credential/provider or Docker effect authority.

## Product Milestone Binding

Canonical complete binding: docs/specs/P5A2_SOURCE_API_IDENTITY_SPEC.md, baseline
dcaca2c02dfdb012cc55b16907b7c6f31fecf305. Full P5-A2 operator outcome and all
G01â€“G14 acceptance/evidence/remainders/owners/P5-A2/P5-B/C/D destinations remain.
This assignment closes only contract decisions for G06/G11 and the G13 test plan;
no implementation criterion or product milestone closes. Phase5 stays0/5.
Root owns contract/metadata/commit, Luna source audit is read-only, independent
REVIEWER owns acceptance; backend/UI/operator retain their roadmap remainders.
Unknown operational coverage stays UNKNOWN; no fixture-to-production transfer.

## Exact mutation and ownership

Root may change only:
- docs/specs/P5A2_SOURCE_API_IDENTITY_SPEC.md
- docs/decisions/P5A2_SOURCE_API_IDENTITY_INTAKE_2026-10-26.md
- this planning Work Order
- SESSION/handoffs/AGENT_HANDOFF_P5A2_SOURCE_API_IDENTITY_2026-10-26.md
- SESSION/ACTIVE_SESSION_STATE.json
- SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json
- SESSION/SESSION_MEMORY.md
- CVF_SESSION/ACTIVE_SESSION_STATE.json
- IMPLEMENTATION_STATUS.json
- docs/PROJECT_INDEX.md
- docs/INDEX.md (catalog manager generated only)
- docs/catalog/ARTIFACT_REGISTRY.json (active handoff projection only)
- docs/implementation/EXECUTION_ROADMAP.md
- knowledge/PROJECT_CONTEXT.md
- knowledge/manifest.json

Independent reviewer alone owns:
docs/decisions/P5A2_SOURCE_API_IDENTITY_REVIEW_2026-10-26.md.
All application/package/test/script/config/core/hook/matrix/oracle/old evidence
paths remain read-only. No executable/file split is foreseeable. Detailed module
facts/status do not change: check the detailed generator and kit projection;
update the artifact handoff pointer and run manager -Write, then all three checks.
No private provenance, shared rule pack, Core update or unrelated merge repair.

## Finite work and acceptance

Read current canonical continuity and installed Core before each role transition;
record active new handoff acknowledgment before authorship. INTAKE audits actual
JWT/current-user/action/scope/assignment/coverage surfaces; DESIGN selects the
bounded source-read interface; SPEC freezes deny-first, fresh release, bytes,
default refusal and HTTP/native-family parity requirements. This authoring is
bounded planning work, not application BUILD. Independent REVIEW consolidates
findings before one same-scope repair packet. Round3 without an independently
new root cause stops REVIEW_COST_ESCALATION_REQUIRED. No silent self-approval.

Acceptance: source-backed intake, complete milestone reconciliation, testable
contract, honest unimplemented/operational limits, explicit future family/HTTP
binding and product-value gate before any endpoint dispatch. Review both the
unauthenticated malformed-request path and unassigned-before-coverage ordering.
Unknown production coverage cannot authorize READY or another automatic support
tranche. If a route lacks accepted scope resolver and concrete user outcome,
leave it parked under the named P5-A2 gap rather than mounting a token endpoint.

Verify installed Core, session, file-size, invariant and knowledge guards;
detailed catalog --check, kit projection check, catalog manager -Check and
git diff --check. Native pinned check_recheck explicitly applies to new intake
worker-return and legacy docs/decisions review; do not claim automatic CLI scan.
This is mechanical/source review, not live AI governance proof. No provider,
network acquisition, credential/.env use, database/container, browser/UI or
runtime source test is needed for a docs-only contract. The unchanged normal
precommit hook still runs the full test suite for each commit.

After planning REVIEW_PASS: Root normal material commit; independent terminal
review of actual exact set; dedicated five-path actual material-SHA continuity
commit; independent clean split-range closure. The five paths are SESSION state,
bootstrap, memory, new handoff and compatibility state only. Replace the sole
GC020 marker with the actual planning material SHA in that child. Synchronize
the artifact handoff pointer in the material commit so the child changes no
catalog pointer. No push or deployment. End at accepted planning only; the next
product work order must separately bound implementation and its prerequisites.

## Gate-To-Role Closeability Contract

closeabilityContractVersion: cvf.gate-role-closeability@1.0.0
closeabilityDisposition: CLOSEABLE
returnTimeRecheck: REQUIRED_BEFORE_REPAIR
implementationTopologyPolicy: EXACT_PATHS_WITH_NO_FORESEEABLE_SPLIT
foreseeableFileSplitDisposition: NOT_REQUIRED_UNDER_SIZE_BUDGET

| gateId | mustPassBy | repairOwner | repairPhase | mutationSurface | topology | commitOwner | commitPhase | dependsOn |
|---|---|---|---|---|---|---|---|---|
| authorization_review | PRE_DISPATCH | work-order-author | PRE_DISPATCH | docs/work_orders/P5A2_SOURCE_API_IDENTITY_PLANNING_WORK_ORDER.md | EXACT_PATHS | commit-steward | DISPATCH_COMMIT | NONE |
| pre_dispatch_gate | PRE_DISPATCH | orchestrator | PRE_DISPATCH | docs/specs/P5A2_SOURCE_API_IDENTITY_SPEC.md;docs/work_orders/P5A2_SOURCE_API_IDENTITY_PLANNING_WORK_ORDER.md | EXACT_PATHS | commit-steward | DISPATCH_COMMIT | authorization_review |
| dispatch_continuity | IMPLEMENTATION | session-sync-steward | IMPLEMENTATION | SESSION/handoffs/AGENT_HANDOFF_P5A2_SOURCE_API_IDENTITY_2026-10-26.md material-SHA marker | EXACT_PATHS | session-sync-steward | DISPATCH_CONTINUITY_COMMIT | pre_dispatch_gate |
| pre_implementation_autorun | IMPLEMENTATION | orchestrator | IMPLEMENTATION | SESSION/handoffs/AGENT_HANDOFF_P5A2_SOURCE_API_IDENTITY_2026-10-26.md;docs/specs/P5A2_SOURCE_API_IDENTITY_SPEC.md | EXACT_PATHS | commit-steward | MATERIAL_COMMIT | dispatch_continuity |
| focused_checker_tests | WORKER_RETURN | implementation-worker | IMPLEMENTATION | docs/specs/P5A2_SOURCE_API_IDENTITY_SPEC.md;docs/catalog/ARTIFACT_REGISTRY.json;docs/INDEX.md | EXACT_PATHS | commit-steward | MATERIAL_COMMIT | dispatch_continuity,pre_implementation_autorun |
| adif_integrity | WORKER_RETURN | implementation-worker | IMPLEMENTATION | docs/decisions/P5A2_SOURCE_API_IDENTITY_INTAKE_2026-10-26.md | EXACT_PATHS | commit-steward | MATERIAL_COMMIT | dispatch_continuity |
| worker_return_fast | WORKER_RETURN | implementation-worker | WORKER_RETURN | docs/decisions/P5A2_SOURCE_API_IDENTITY_INTAKE_2026-10-26.md | EXACT_PATHS | commit-steward | MATERIAL_COMMIT | focused_checker_tests,adif_integrity |
| reviewer_fast | REVIEW | reviewer | REVIEW | docs/decisions/P5A2_SOURCE_API_IDENTITY_REVIEW_2026-10-26.md | EXACT_PATHS | commit-steward | MATERIAL_COMMIT | worker_return_fast |
| pre_commit | PRE_MATERIAL_COMMIT | repair-worker | PRE_MATERIAL_COMMIT | docs/specs/P5A2_SOURCE_API_IDENTITY_SPEC.md;docs/work_orders/P5A2_SOURCE_API_IDENTITY_PLANNING_WORK_ORDER.md;docs/PROJECT_INDEX.md;docs/INDEX.md;docs/catalog/ARTIFACT_REGISTRY.json;IMPLEMENTATION_STATUS.json;knowledge/PROJECT_CONTEXT.md;knowledge/manifest.json;SESSION/ACTIVE_SESSION_STATE.json;SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json;SESSION/SESSION_MEMORY.md;CVF_SESSION/ACTIVE_SESSION_STATE.json;SESSION/handoffs/AGENT_HANDOFF_P5A2_SOURCE_API_IDENTITY_2026-10-26.md;docs/implementation/EXECUTION_ROADMAP.md | EXACT_PATHS | commit-steward | MATERIAL_COMMIT | reviewer_fast |
| terminal_completion_review | POST_MATERIAL | reviewer | POST_MATERIAL | docs/decisions/P5A2_SOURCE_API_IDENTITY_REVIEW_2026-10-26.md | EXACT_PATHS | commit-steward | CORRECTIVE_MATERIAL_COMMIT | pre_commit |
| continuity | CONTINUITY_COMMIT | session-sync-steward | CONTINUITY_COMMIT | SESSION/handoffs/AGENT_HANDOFF_P5A2_SOURCE_API_IDENTITY_2026-10-26.md;SESSION/ACTIVE_SESSION_STATE.json;SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json;SESSION/SESSION_MEMORY.md;CVF_SESSION/ACTIVE_SESSION_STATE.json | EXACT_PATHS | session-sync-steward | CONTINUITY_COMMIT | terminal_completion_review |
| committed_range_closure | POST_MATERIAL_CLOSURE | reviewer | POST_MATERIAL_CLOSURE | SESSION/handoffs/AGENT_HANDOFF_P5A2_SOURCE_API_IDENTITY_2026-10-26.md;docs/decisions/P5A2_SOURCE_API_IDENTITY_REVIEW_2026-10-26.md | EXACT_PATHS | session-sync-steward | CONTINUITY_COMMIT | continuity |

## Accepted planning disposition

Independent PLANNING_REVIEW_PASS_BOUNDED, API-SPEC-F1/F2 resolved/no waiver. INTAKE/DESIGN/SPEC complete; runtime/API remains NOT_IMPLEMENTED. Only normal planning material/terminal actual-range review/dedicated5actualSHAcontinuity/clean closure remain. This WO authorizes no successor endpoint, source-mode evolution or physical/provider effect.
