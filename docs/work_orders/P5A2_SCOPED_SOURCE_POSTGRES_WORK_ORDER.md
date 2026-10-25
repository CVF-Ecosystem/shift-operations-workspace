# P5-A2 Stage B PostgreSQL source harness — bounded source Work Order

Status: DISPATCH_READY
Date: 2026-10-26; R2. Root ORCHESTRATOR/SPEC_AUTHOR/WORK_ORDER_AUTHOR.
This is an authorization-review candidate, NOT a worker release by itself.
Inherit accepted source SPEC/StageA; new design/test/effect contract is the
StageB SPEC below. Independent SPEC/WO PASS, normal dispatch commit and dedicated
actual-SHA continuity precede BUILD. This source WO grants NO Docker run.

## Product Milestone Binding

Canonical full block, acceptance and current G01–G14 reconciliation/owners/
destinations: docs/specs/P5A2_SCOPED_SOURCE_POSTGRES_SPEC.md at baseline8dc39e1.
User outcome is integrated authorized forecast/history/freshness/exact human
approval; only G04/G05/G06 physical fixture source mechanics and partial G13
are selected. Prior pure/PG36/37/StageA accepted; actual new SQL query unproved.
G01/A7/G02 blocked; operational G03/G05/G06/G08–G10/G13 and G07/G11/G12 open,
G14 held. Root accountable/contracts/oracle/effect/commit, backend worker,
independent reviewer, UI roadmap owner/operator retain all named P5-A2 and
P5-B/C/D destinations; Phase5 0/5. UNKNOWN production coverage cannot authorize
production use; synthetic-only harness may proceed. Return after source review
to finite effect admission, then actual result review; no automatic support loop.

## Exact worker changed set

- scripts/run_p5a2_scoped_source_postgres.py
- tests/integration/p5a2_scoped_source_pg_fixture.py
- tests/integration/p5a2_scoped_source_pg_probes.py
- tests/integration/test_p5a2_scoped_source_postgres_live.py
- tests/unit/test_p5a2_scoped_source_postgres_runner.py
- docs/decisions/P5A2_SCOPED_SOURCE_POSTGRES_WORKER_RETURN_2026-10-26.md

Each executable <=300 lines, target<=250. Fixture helper owns native synthetic
seeding/independent expected manifests; probes helper owns real transaction
tracing/writer barriers. Live test is ONE opt-in comprehensive target; runner
owns admission/budget fencing/minimal environment and existing lifecycle reuse;
unit test owns inert prerequisite/ownership/cleanup/skip/sanitization/fence cases.
No extra path/split without consolidated Root amendment before mutation.

Root-only: StageB SPEC, this WO, DRAFT effect WO, frozen new PG oracle, admission
JSON, eventual exact attempt/evidence JSON named by admission, canonical SESSION
state/bootstrap/memory/newhandoff + mirror; IMPLEMENTATION_STATUS.json; docs/INDEX.md;
docs/implementation/EXECUTION_ROADMAP.md; docs/catalog/MODULE_REGISTRY.json and
MODULE_CATALOG.md; knowledge/PROJECT_CONTEXT.md, GOVERNANCE_BOUNDARIES.md and
manifest.json. Independent reviewer alone owns
`docs/decisions/P5A2_SCOPED_SOURCE_POSTGRES_REVIEW_2026-10-26.md`.
Old runners/source/parent/pure/old oracles/receipts/Core/hook remain READ-ONLY.

## Required implementation/proof

Follow docs/specs/P5A2_SCOPED_SOURCE_POSTGRES_SPEC.md and Root oracle rawSHA
0b69156fcb09a6b65a25c437320a5f4001f4068284d5bcf8b88438700a92f44f;
source oracle0f/bodyoracle12ad/sourcefamily9b3 stay unchanged. Use native ledger
and actual query_source; no cloned source selector or fake driver rows in live
proof. Native valid seeding, disjoint actors/windows, all six500/501 cases,
both full golden receipts/content/lineage/analysis, four physical writer races,
actual RR/read-only/newfresh identity, and refusal confidentiality are mandatory.

Inert BUILD only: py_compile, focused new runner unit tests, safe collection of
live target with NO owned context (must skip), existing source+generic corpus,
six metadata guards. No Docker daemon calls from tests/build, real DB connection,
network/package/pull/provider/credential/.env/CSV effect. Old cached readiness
observation in SPEC is not physical proof and grants no effect by itself.

Runner admission is PLANNING_NO_EFFECT while BUILD proceeds. After independent
source review Root seals exact five harness hashes + all inherited pins, switches
effect WO to active review candidate, and independently reviews finite effect
budget. Then normal SOURCE/EFFECT-ADMISSION material commit, terminal review,
dedicated actual-SHA continuity and clean closure precede the ONE real invocation.
No harness code read from an uncommitted source surface for the physical proof.

Attempt reservation O_EXCL persists exactly once, including failed run; no retry
or delete/reuse of reservation. Child live target needs owned fixed admission /
marker/context/nonce and exact loopback identity, not ambient general LIVE_URL.
Refuse stale observation and arbitrary URL/target/force/path escape. Minimal env
and all errors/tails scrub ephemeral password/full DSN. Created ID/volume identity
only authorizes cleanup of that owned resource; unknown cleanup cannot be PASS.

## Invariant-Family Proof

Follow docs/cvf/INVARIANT_FAMILY_STANDARD.md. Existing family
P5A2-SCOPED-SOURCE-OUTCOMES canonical9b3ba818e647d228e453706fac1378a69388bbae7b1a02d81732e64d939d5d4c
and registered native emitter/validator/84-mutation corpus remain owners. New SQL
experiment supplements backend evidence without changing shapes/consumers/matrix.
Applicability decision for no new family is in StageB SPEC; independent review
must accept it before dispatch. If shared outcome/schema ownership grows, stop.
Real source adapters unchanged; new test receives actual native READY/REFUSED
and matches frozen closed receipts. Recompute pin; rerun four source tests plus
tests/unit/test_invariant_family_contract.py and
tests/integration/test_invariant_family_repository_guard.py. Evidence owner worker;
independent reviewer reruns corpus/samples both native outcomes and physical result.
Flat nested exclusions remain limited; existing backend semantic tests retained.

Worker return: exact source manifest/hashes/lines, focused failures and final
results, no physical claim before effect, full gap remainders/owner destinations,
standalone marker/native return-time recheck. Independent review consolidates
findings before repair; round3 without independent new root cause stops with
REVIEW_COST_ESCALATION_REQUIRED. No self-approval/commit/push/public release.
Root owns unmodified full precommit hooks; no bypass/deselection/xfail.

## Gate-To-Role Closeability Contract

closeabilityContractVersion: cvf.gate-role-closeability@1.0.0
closeabilityDisposition: CLOSEABLE
returnTimeRecheck: REQUIRED_BEFORE_REPAIR
implementationTopologyPolicy: EXACT_PATHS_WITH_NO_FORESEEABLE_SPLIT
foreseeableFileSplitDisposition: NOT_REQUIRED_UNDER_SIZE_BUDGET

| gateId | mustPassBy | repairOwner | repairPhase | mutationSurface | topology | commitOwner | commitPhase | dependsOn |
|---|---|---|---|---|---|---|---|---|
| authorization_review | PRE_DISPATCH | work-order-author | PRE_DISPATCH | docs/work_orders/P5A2_SCOPED_SOURCE_POSTGRES_WORK_ORDER.md | EXACT_PATHS | commit-steward | DISPATCH_COMMIT | NONE |
| pre_dispatch_gate | PRE_DISPATCH | orchestrator | PRE_DISPATCH | docs/work_orders/P5A2_SCOPED_SOURCE_POSTGRES_WORK_ORDER.md;docs/specs/P5A2_SCOPED_SOURCE_POSTGRES_SPEC.md | EXACT_PATHS | commit-steward | DISPATCH_COMMIT | authorization_review |
| dispatch_continuity | IMPLEMENTATION | session-sync-steward | IMPLEMENTATION | SESSION/handoffs/AGENT_HANDOFF_P5A2_SCOPED_SOURCE_POSTGRES_2026-10-26.md material-SHA marker | EXACT_PATHS | session-sync-steward | DISPATCH_CONTINUITY_COMMIT | pre_dispatch_gate |
| pre_implementation_autorun | IMPLEMENTATION | orchestrator | IMPLEMENTATION | docs/work_orders/P5A2_SCOPED_SOURCE_POSTGRES_WORK_ORDER.md;SESSION/handoffs/AGENT_HANDOFF_P5A2_SCOPED_SOURCE_POSTGRES_2026-10-26.md | EXACT_PATHS | commit-steward | MATERIAL_COMMIT | dispatch_continuity |
| focused_checker_tests | WORKER_RETURN | implementation-worker | IMPLEMENTATION | scripts/run_p5a2_scoped_source_postgres.py;tests/integration/p5a2_scoped_source_pg_fixture.py;tests/integration/p5a2_scoped_source_pg_probes.py;tests/integration/test_p5a2_scoped_source_postgres_live.py;tests/unit/test_p5a2_scoped_source_postgres_runner.py | EXACT_PATHS | commit-steward | MATERIAL_COMMIT | dispatch_continuity,pre_implementation_autorun |
| adif_integrity | WORKER_RETURN | implementation-worker | IMPLEMENTATION | docs/decisions/P5A2_SCOPED_SOURCE_POSTGRES_WORKER_RETURN_2026-10-26.md | EXACT_PATHS | commit-steward | MATERIAL_COMMIT | dispatch_continuity |
| worker_return_fast | WORKER_RETURN | implementation-worker | WORKER_RETURN | docs/decisions/P5A2_SCOPED_SOURCE_POSTGRES_WORKER_RETURN_2026-10-26.md | EXACT_PATHS | commit-steward | MATERIAL_COMMIT | focused_checker_tests,adif_integrity |
| reviewer_fast | REVIEW | reviewer | REVIEW | docs/decisions/P5A2_SCOPED_SOURCE_POSTGRES_REVIEW_2026-10-26.md | EXACT_PATHS | commit-steward | MATERIAL_COMMIT | worker_return_fast |
| pre_commit | PRE_MATERIAL_COMMIT | repair-worker | PRE_MATERIAL_COMMIT | scripts/run_p5a2_scoped_source_postgres.py;tests/integration/p5a2_scoped_source_pg_fixture.py;tests/integration/p5a2_scoped_source_pg_probes.py;tests/integration/test_p5a2_scoped_source_postgres_live.py;tests/unit/test_p5a2_scoped_source_postgres_runner.py;docs/decisions/P5A2_SCOPED_SOURCE_POSTGRES_REVIEW_2026-10-26.md | EXACT_PATHS | commit-steward | MATERIAL_COMMIT | reviewer_fast |
| terminal_completion_review | POST_MATERIAL | reviewer | POST_MATERIAL | docs/decisions/P5A2_SCOPED_SOURCE_POSTGRES_REVIEW_2026-10-26.md | EXACT_PATHS | commit-steward | CORRECTIVE_MATERIAL_COMMIT | pre_commit |
| continuity | CONTINUITY_COMMIT | session-sync-steward | CONTINUITY_COMMIT | SESSION/handoffs/AGENT_HANDOFF_P5A2_SCOPED_SOURCE_POSTGRES_2026-10-26.md;SESSION/ACTIVE_SESSION_STATE.json;SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json;SESSION/SESSION_MEMORY.md;CVF_SESSION/ACTIVE_SESSION_STATE.json | EXACT_PATHS | session-sync-steward | CONTINUITY_COMMIT | terminal_completion_review |
| committed_range_closure | POST_MATERIAL_CLOSURE | reviewer | POST_MATERIAL_CLOSURE | SESSION/handoffs/AGENT_HANDOFF_P5A2_SCOPED_SOURCE_POSTGRES_2026-10-26.md;docs/decisions/P5A2_SCOPED_SOURCE_POSTGRES_REVIEW_2026-10-26.md | EXACT_PATHS | session-sync-steward | CONTINUITY_COMMIT | continuity |

Planning repair PG-PLAN-F1/F2: pre-harness oracle now freezes exact baseline and all auxiliary actor/scope/instance/window/asof/policy/mutation context. New runner creation must use --pull=never + exact cached imageID, with inert command proof, without mutating old base runner. Effect authority still absent. At sealing, same joint SOURCE MATERIAL / EFFECT DISPATCH commit plus dedicated actual-SHA continuity serves the two bounded orders; result pass follows its own material/continuity chain.
