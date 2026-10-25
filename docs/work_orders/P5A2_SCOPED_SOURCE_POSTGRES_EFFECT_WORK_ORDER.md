# P5-A2 Stage B — ONE physical scoped PostgreSQL effect Work Order

Status: DRAFT
Date: 2026-10-26; R2. NO effect authority until separate source/effect review,
sealed admission and normal committed source/admission + dedicated continuity.

## Product Milestone Binding

Canonical complete P5-A2 outcome/acceptance/current G01–G14 evidence/remainder/
owner/destination block: docs/specs/P5A2_SCOPED_SOURCE_POSTGRES_SPEC.md. Only
physical fixture G04–G06 and partial G13 source proof is selected; production
coverage/retention, API/use-time auth, scheduler/context/UI/approval/operational
quality remain OPEN/UNKNOWN; G01/A7/G02 blocked/G14held, Phase5 0/5. Root owns
finite effect/evidence/commit; backend harness is independently reviewed;
independent reviewer owns result/cleanup acceptance, UI/operator and all P5-A2/
P5-B/C/D owners/destinations retained. No milestone closure from this experiment.

## Admission and execution boundary

Exact sealed budget/pins/marker/observation paths are in
`docs/decisions/P5A2_SCOPED_SOURCE_POSTGRES_ADMISSION_2026-10-26.json`.
Current status PLANNING_NO_EFFECT with empty harnessPins is NONDISPATCHABLE.
Root may activate this WO only after source review and exact pins sealed;
independent reviewer must accept both source and effect packet before normal
source/admission commit. Dedicated actual-SHA continuity/clean range then
permits Root exactly one invocation of the fixed new runner. No other command
may create a database/container under this authority. No direct pytest live URL.

ONE wrapper/ONE target/ONE newly owned disposable PG container. Cached exact
image/driver only; dynamic loopback port and random ephemeral local password.
No install/pull/provider/realcredential/.env/CSV/production/network acquisition.
Reuse existing migration/readiness/cleanup methods without mutating old code.
All physical cases and stop/cleanup conditions are frozen in StageB SPEC/oracle.
If failure/uncertain ownership/cleanup occurs: record partial evidence, preserve
spent attempt; no automatic retry. Only confirmed owned container/captured
anonymous volumes may be removed; no prune/pre-existing-resource deletion.

Root execution writes only exact immutable attempt marker and ignored observation
from admission, plus exact evidence JSON and metadata/return/review artifacts
already authorized by source WO. Harness/source/oracle/matrix stay READ-ONLY
through effect. Any exposed product/source defect returns to a new reviewed
repair/effect decision; no silent fix/rehearsal rerun. Result material/terminal
review/dedicated actual-SHA continuity and clean range close only this experiment.
Independent result review explicitly verifies named container/volumes absent.

## Invariant-Family Proof

Same unchanged P5A2-SCOPED-SOURCE-OUTCOMES9b3 and native emitters/validators/
registered mutation corpus as source WO. Physical observations are evidence,
not new product representation/lifecycle grammar. Source/retention/API/AI claim
limits and flat nested exclusions remain. Independently sample actual ready/
refused outputs, recompute source/oracle pins and compare all intended cases.
Legacy experiment summary retained; immutable attempt is not a mutable state
machine. No new schema/family without prior contract review.

Worker/effect return and independent completion review use standalone marker/
return-time recheck; docs/decisions selector limit requires verified native
check_recheck explicitly. Full source WO ownership/no-push/normal-hook rules apply.

## Gate-To-Role Closeability Contract

closeabilityContractVersion: cvf.gate-role-closeability@1.0.0
closeabilityDisposition: CLOSEABLE
returnTimeRecheck: REQUIRED_BEFORE_REPAIR
implementationTopologyPolicy: EXACT_PATHS_WITH_NO_FORESEEABLE_SPLIT
foreseeableFileSplitDisposition: NOT_REQUIRED_UNDER_SIZE_BUDGET

| gateId | mustPassBy | repairOwner | repairPhase | mutationSurface | topology | commitOwner | commitPhase | dependsOn |
|---|---|---|---|---|---|---|---|---|
| authorization_review | PRE_DISPATCH | work-order-author | PRE_DISPATCH | docs/work_orders/P5A2_SCOPED_SOURCE_POSTGRES_EFFECT_WORK_ORDER.md | EXACT_PATHS | commit-steward | DISPATCH_COMMIT | NONE |
| pre_dispatch_gate | PRE_DISPATCH | orchestrator | PRE_DISPATCH | docs/work_orders/P5A2_SCOPED_SOURCE_POSTGRES_EFFECT_WORK_ORDER.md;docs/specs/P5A2_SCOPED_SOURCE_POSTGRES_SPEC.md | EXACT_PATHS | commit-steward | DISPATCH_COMMIT | authorization_review |
| dispatch_continuity | IMPLEMENTATION | session-sync-steward | IMPLEMENTATION | SESSION/handoffs/AGENT_HANDOFF_P5A2_SCOPED_SOURCE_POSTGRES_2026-10-26.md material-SHA marker | EXACT_PATHS | session-sync-steward | DISPATCH_CONTINUITY_COMMIT | pre_dispatch_gate |
| pre_implementation_autorun | IMPLEMENTATION | orchestrator | IMPLEMENTATION | docs/work_orders/P5A2_SCOPED_SOURCE_POSTGRES_EFFECT_WORK_ORDER.md;SESSION/handoffs/AGENT_HANDOFF_P5A2_SCOPED_SOURCE_POSTGRES_2026-10-26.md | EXACT_PATHS | commit-steward | MATERIAL_COMMIT | dispatch_continuity |
| focused_checker_tests | WORKER_RETURN | implementation-worker | IMPLEMENTATION | docs/decisions/P5A2_SCOPED_SOURCE_POSTGRES_ATTEMPT_2026-10-26.json;docs/decisions/P5A2_SCOPED_SOURCE_POSTGRES_EVIDENCE_2026-10-26.json;docs/decisions/P5A2_SCOPED_SOURCE_POSTGRES_WORKER_RETURN_2026-10-26.md | EXACT_PATHS | commit-steward | MATERIAL_COMMIT | dispatch_continuity,pre_implementation_autorun |
| adif_integrity | WORKER_RETURN | implementation-worker | IMPLEMENTATION | docs/decisions/P5A2_SCOPED_SOURCE_POSTGRES_WORKER_RETURN_2026-10-26.md | EXACT_PATHS | commit-steward | MATERIAL_COMMIT | dispatch_continuity |
| worker_return_fast | WORKER_RETURN | implementation-worker | WORKER_RETURN | docs/decisions/P5A2_SCOPED_SOURCE_POSTGRES_WORKER_RETURN_2026-10-26.md | EXACT_PATHS | commit-steward | MATERIAL_COMMIT | focused_checker_tests,adif_integrity |
| reviewer_fast | REVIEW | reviewer | REVIEW | docs/decisions/P5A2_SCOPED_SOURCE_POSTGRES_REVIEW_2026-10-26.md | EXACT_PATHS | commit-steward | MATERIAL_COMMIT | worker_return_fast |
| pre_commit | PRE_MATERIAL_COMMIT | repair-worker | PRE_MATERIAL_COMMIT | docs/decisions/P5A2_SCOPED_SOURCE_POSTGRES_ATTEMPT_2026-10-26.json;docs/decisions/P5A2_SCOPED_SOURCE_POSTGRES_EVIDENCE_2026-10-26.json;docs/decisions/P5A2_SCOPED_SOURCE_POSTGRES_WORKER_RETURN_2026-10-26.md;docs/decisions/P5A2_SCOPED_SOURCE_POSTGRES_REVIEW_2026-10-26.md | EXACT_PATHS | commit-steward | MATERIAL_COMMIT | reviewer_fast |
| terminal_completion_review | POST_MATERIAL | reviewer | POST_MATERIAL | docs/decisions/P5A2_SCOPED_SOURCE_POSTGRES_REVIEW_2026-10-26.md | EXACT_PATHS | commit-steward | CORRECTIVE_MATERIAL_COMMIT | pre_commit |
| continuity | CONTINUITY_COMMIT | session-sync-steward | CONTINUITY_COMMIT | SESSION/handoffs/AGENT_HANDOFF_P5A2_SCOPED_SOURCE_POSTGRES_2026-10-26.md;SESSION/ACTIVE_SESSION_STATE.json;SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json;SESSION/SESSION_MEMORY.md;CVF_SESSION/ACTIVE_SESSION_STATE.json | EXACT_PATHS | session-sync-steward | CONTINUITY_COMMIT | terminal_completion_review |
| committed_range_closure | POST_MATERIAL_CLOSURE | reviewer | POST_MATERIAL_CLOSURE | SESSION/handoffs/AGENT_HANDOFF_P5A2_SCOPED_SOURCE_POSTGRES_2026-10-26.md;docs/decisions/P5A2_SCOPED_SOURCE_POSTGRES_REVIEW_2026-10-26.md | EXACT_PATHS | session-sync-steward | CONTINUITY_COMMIT | continuity |
