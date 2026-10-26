# P5-A2 Core-only binding corrective Work Order

Status: IMPLEMENTED_BOUNDED
Date: 2026-10-26
Risk: R2
Root ORCHESTRATOR/WORK_ORDER_AUTHOR; IMPLEMENTATION_WORKER independent from
REVIEWER. Root COMMIT_STEWARD/SESSION_SYNC_STEWARD.

## Checker Source Read-Ahead Block

Read installed public Core closeability checker status grammar, gate constants,
check_work_order/check_recheck; exact pin aa672d1 and two native controls in SPEC.
Use active projection before authorization. No private projected checker source
is authority for the corrected route.

## Product Milestone Binding

Canonical complete G01–G14 current evidence/remainder/owner/destination table,
acceptance/user outcome and bounded support necessity/return are in
../decisions/P5A2_CORE_ONLY_BINDING_DESIGN_SPEC_2026-10-26.md at source7fd67f5
plus carried SQL receipt SHA1c2eefad2bfae0ab2e77a4bdf2bc0e7115b189a1440d8e37ee58e4d2e41d5a6f.
Reconciled all14: selected unblock G04/G05/G13 SQL result only; G01/A7/G02
blocked, G06/auth/query/caps/cohort/retention unknown/open, operationalG03/
G08-G10/G13 open, G07/G11/G12 open, G14held. Root accountable, Sol backend/
controls, Luna independentreview/UI, operatorbusiness acceptance; each canonical
P5-A2 gate/P5-B/C/D destination retained. Phase5 0/5. Stop after bounded core
adapter/instruction repair, normal carriedSQL resultclosure, RETURN G04–G06
productSPEC. No dependent sourcequery BUILD granted by this support assignment.

## Allowed surfaces and execution

Worker: scripts/check_cvf_core_machine_inheritance.py,
scripts/_cvf_core_binding*.py, scripts/initialize_cvf_clone.ps1,
tests/unit/test_cvf_core_machine_inheritance.py, tests/unit/test_cvf_core_binding*.py,
`tests/integration/test_project_knowledge_ingest_rehearsal.py` (AM1 only).
Worker return: docs/decisions/P5A2_CORE_ONLY_BINDING_WORKER_RETURN_2026-10-26.md.
Root only: .cvf/manifest.json, .cvf/policy.json, AGENTS.md, active canonical
SESSION/mirror/handoff, IMPLEMENTATION_STATUS.json, docs/INDEX.md,
docs/implementation/EXECUTION_ROADMAP.md, knowledge governance/context/manifest,
current Docker WO/review metadata and this SPEC/WO. Preserve prior physical SQL
receipt bytes/source, original failed acquisition and spent ceilings. Independent
review: docs/decisions/P5A2_CORE_ONLY_BINDING_REVIEW_2026-10-26.md.
No .githooks changes, no CVF repo writes, no provider/credential/.env/network/
package/image/container/release/push. Python<=300; existing domain/SQL/pure/
fixtures and invariant registry/matrices remain unchanged.

Implement R1–R4 from accepted SPEC together. Root edits declared config/docs,
worker edits script/tests only, independent reviewer evaluates complete set.
Relevant focused tests/CLI/probes plus session/knowledge/size/invariant/catalog;
full pytest only unmodified normal commit hook. Native public Core CLI direct
read-only pre-repair packet check is the migration admission; fixed local
adapter must pass before material commit. Current inherited dispatch/continuity
anchors and corrective ordering are explicitly defined in SPEC, no false new
committed-dispatch claim or hook bypass.

## Return-Time Closeability Recheck

Worker return must self-declare exact standalone marker and return canonical
recheck/status. COMPLETE_PENDING_REVIEW only CLOSEABLE/NONE. Outside-scope
blocker stops/no redispatch, consolidated orchestrator route; round3 without
independent new root cause stops with REVIEW_COST_ESCALATION_REQUIRED.

## Gate-To-Role Closeability Contract

closeabilityContractVersion: cvf.gate-role-closeability@1.0.0
closeabilityDisposition: CLOSEABLE
returnTimeRecheck: REQUIRED_BEFORE_REPAIR
implementationTopologyPolicy: BOUNDED_PATH_FAMILIES
foreseeableFileSplitDisposition: COVERED_BY_BOUNDED_PATH_FAMILY

| gateId | mustPassBy | repairOwner | repairPhase | mutationSurface | topology | commitOwner | commitPhase | dependsOn |
|---|---|---|---|---|---|---|---|---|
| authorization_review | PRE_DISPATCH | orchestrator | PRE_DISPATCH | docs/work_orders/P5A2_CORE_ONLY_BINDING_WORK_ORDER.md | EXACT_PATHS | commit-steward | DISPATCH_COMMIT | NONE |
| pre_dispatch_gate | PRE_DISPATCH | work-order-author | PRE_DISPATCH | docs/decisions/P5A2_CORE_ONLY_BINDING_DESIGN_SPEC_2026-10-26.md;docs/work_orders/P5A2_CORE_ONLY_BINDING_WORK_ORDER.md | EXACT_PATHS | commit-steward | DISPATCH_COMMIT | authorization_review |
| dispatch_continuity | IMPLEMENTATION | session-sync-steward | IMPLEMENTATION | SESSION/handoffs/AGENT_HANDOFF_P5A2_CORE_BINDING_2026-10-26.md material-SHA marker | EXACT_PATHS | session-sync-steward | DISPATCH_CONTINUITY_COMMIT | pre_dispatch_gate |
| pre_implementation_autorun | IMPLEMENTATION | orchestrator | IMPLEMENTATION | docs/work_orders/P5A2_CORE_ONLY_BINDING_WORK_ORDER.md;SESSION/handoffs/AGENT_HANDOFF_P5A2_CORE_BINDING_2026-10-26.md | EXACT_PATHS | commit-steward | CORRECTIVE_MATERIAL_COMMIT | dispatch_continuity |
| focused_checker_tests | WORKER_RETURN | implementation-worker | IMPLEMENTATION | scripts/check_cvf_core_machine_inheritance.py;scripts/_cvf_core_binding*.py;scripts/initialize_cvf_clone.ps1;tests/unit/test_cvf_core_machine_inheritance.py;tests/unit/test_cvf_core_binding*.py;tests/integration/test_project_knowledge_ingest_rehearsal.py;.cvf/manifest.json;.cvf/policy.json;AGENTS.md | BOUNDED_PATH_FAMILIES | commit-steward | MATERIAL_COMMIT | dispatch_continuity,pre_implementation_autorun |
| adif_integrity | WORKER_RETURN | implementation-worker | IMPLEMENTATION | docs/decisions/P5A2_CORE_ONLY_BINDING_WORKER_RETURN_2026-10-26.md | EXACT_PATHS | commit-steward | MATERIAL_COMMIT | dispatch_continuity |
| worker_return_fast | WORKER_RETURN | implementation-worker | WORKER_RETURN | docs/decisions/P5A2_CORE_ONLY_BINDING_WORKER_RETURN_2026-10-26.md;docs/decisions/P5A2_CORE_ONLY_BINDING_WORKER_RETURN_2026-10-26.md | EXACT_PATHS | commit-steward | MATERIAL_COMMIT | focused_checker_tests,adif_integrity,pre_implementation_autorun |
| reviewer_fast | REVIEW | reviewer | REVIEW | docs/decisions/P5A2_CORE_ONLY_BINDING_REVIEW_2026-10-26.md | EXACT_PATHS | commit-steward | MATERIAL_COMMIT | worker_return_fast |
| pre_commit | PRE_MATERIAL_COMMIT | repair-worker | PRE_MATERIAL_COMMIT | scripts/check_cvf_core_machine_inheritance.py;scripts/_cvf_core_binding*.py;scripts/initialize_cvf_clone.ps1;tests/unit/test_cvf_core_machine_inheritance.py;tests/unit/test_cvf_core_binding*.py;tests/integration/test_project_knowledge_ingest_rehearsal.py;.cvf/manifest.json;.cvf/policy.json;AGENTS.md;docs/decisions/P5A2_CORE_ONLY_BINDING_REVIEW_2026-10-26.md | BOUNDED_PATH_FAMILIES | commit-steward | MATERIAL_COMMIT | reviewer_fast |
| terminal_completion_review | POST_MATERIAL | reviewer | POST_MATERIAL | docs/decisions/P5A2_CORE_ONLY_BINDING_REVIEW_2026-10-26.md | EXACT_PATHS | commit-steward | CORRECTIVE_MATERIAL_COMMIT | pre_commit |
| continuity | CONTINUITY_COMMIT | session-sync-steward | CONTINUITY_COMMIT | SESSION/handoffs/AGENT_HANDOFF_P5A2_CORE_BINDING_2026-10-26.md;SESSION/ACTIVE_SESSION_STATE.json;SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json;SESSION/SESSION_MEMORY.md;CVF_SESSION/ACTIVE_SESSION_STATE.json | EXACT_PATHS | session-sync-steward | CONTINUITY_COMMIT | terminal_completion_review |
| committed_range_closure | POST_MATERIAL_CLOSURE | reviewer | POST_MATERIAL_CLOSURE | SESSION/handoffs/AGENT_HANDOFF_P5A2_CORE_BINDING_2026-10-26.md;docs/decisions/P5A2_CORE_ONLY_BINDING_REVIEW_2026-10-26.md | EXACT_PATHS | session-sync-steward | CONTINUITY_COMMIT | continuity |


DISPATCH_READY is the active-grammar authorization-review candidate. Worker
BUILD still requires independent SPEC/authorization PASS and Root explicit
activation/acknowledgment; this status alone grants no execution.

Root activation: independent SPEC_AUTHORIZATION_PASS_BOUNDED, no findings/waivers;
current source/continuity/nativeCore packet reacknowledged before BUILD. Worker
source scope and Root config scope only; wholechangedset independent review and
fixed normaladapter/fullhook remain required before corrective material commit.

## Implementation acceptance / authority exhaustion

Independent REVIEW_PASS_BOUNDED after repairround1, CORE-BUILD-F1/F2 resolved,
no open finding/waiver. Source/config implementation complete; no more worker
BUILD grant. Static21focusedPASS, fixedordinaryadapter/native0, metadataPASS.
No CVF source/checkout changed, provider/Docker/SQL rerun or new package effect.
Normal material/fullhook then terminalreview/dedicatedactualSHAcontinuity/
cleanrange gate boundedclosure; currentactivehandoff records actual receipts.
Return product work to G04–G06SPEC after carriedSQL resultclosure, not another
support survey. All14gap owners/operational limits/Phase5 0/5/providerhold retained.

## AM1 — full-hook same-cause test-helper correction

Candidate AM1 pending independent authorization. Normal material hook stopped,
no commit:1failed/3244passed/147skipped/4warnings/8errors in206.99s, retained
.venv/p5a2-core-only-material-20261026.log. All9 failed/error cases share the
same existing tests/integration/test_project_knowledge_ingest_rehearsal.py
_pinned_helper assertion HEAD==origin/main==pin. That directly contradicts
accepted R1 installed-pin independence. A targeted active tests/scripts search
found this remaining equality; no other same-pattern current dependency.

Add this ONE exact integration test path to worker repair scope (same test
artifactclass, objective/R2/effectsNONE/Rootcommitowner), plus ownreturn. Replace
latestremote equality with reuse of corrected installedCore binding and exact
selected helper pin/hash integrity. Preserve HELPER_SHA256/networktokenguard/
actualnativePowerShell ingestion/index assertions/allnegativecases and cleanup.
Do not skip/deselect/xfail/weaken tests or change Core/helper source/hash to
force success. Root verifies original pin/hash stillmatchesinstalledhelper.
Run the9 implicated integrationcases plus21Corefocused cases once, retain
originalfailedfullhook then independentreview before reattempting normalhook.
This is pre-material same-objective repairround2 with independent newlyfound
source rootcause, not a new effect or support survey. Full14gap/boundedreturn
unchanged. Stop on new outside-authority finding; do not auto-expand paths.

Root AM1 activation: independent AM1_AUTHORIZATION_PASS_BOUNDED, no blocker/waiver.
Fresh pre-material repair acknowledgment and ordinaryadapter0 precede worker
round2 on the ONE added test path and ownreturn. No other source grant.

AM1 independent REPAIR_REVIEW_PASS_BOUNDED: exact test helper corrected,30focused
PASS19.74s, all negative/index/cleanup/hash proofs preserved, no new source/effects.
Root reattempts unmodifiednormal material hook; original failedfull log retained.
