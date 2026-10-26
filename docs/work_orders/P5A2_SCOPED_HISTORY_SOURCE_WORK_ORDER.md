# P5-A2 scoped history source — Stage A Work Order

Status: IMPLEMENTED_BOUNDED
Date: 2026-10-26; risk R2; Root ORCHESTRATOR/WORK_ORDER_AUTHOR.
Worker activation requires independent authorization PASS, normal dispatch commit,
dedicated actual-dispatch-SHA continuity and fresh acknowledgment before BUILD.
Status alone grants no execution; Stage B remains HELD.

## Product Milestone Binding

Milestone P5-A2, docs/implementation/EXECUTION_ROADMAP.md Phase 5, assessed source
814d32ba6cff65b9ea4afd499540758eec5559ee. User outcome/full acceptance: integrated
authorized scheduled signals/forecast/history/lineage/freshness/uncertainty/abstention
and human approval of exact run/version/source digest before durable action.
Canonical complete G01–G14 evidence/owner/destination reconciliation is the accepted
source SPEC docs/specs/P5A2_SCOPED_HISTORY_SOURCE_SPEC.md, SHA256
db1d218083bfadac149f1c4415cfe0bc13213f41f33311a107447cad24abe7bf, accepted bc25/814d.
Current truth: pure numeric/history and one synthetic PG36/37 proof accepted;
no native source query/emitter. Production enrollment/retention UNKNOWN.

This assignment selects only G04–G06 fixture-scoped native admission and partial
G13 source-failure drills, NOT whole gaps or milestone. Backendworker owns code;
Root owns oracle/contracts/metadata/commit; independent REVIEWER checks; operator
owns business acceptance; UI owner per roadmap. Full current reconciliation:

| Gap | Evidence/remainder | In scope | Owner and concrete destination |
|---|---|---|---|
| G01/A7 | provider401 BLOCKED | NO | Root/operator; P5-A A7 then P5-A2 |
| G02 | operational RAG UNKNOWN/BLOCKED | NO | Root/backend; P5-A2 context |
| G03 | pure metric accepted; business/cohort fit OPEN | NO | backend/operator; P5-A2 metric |
| G04 | pure/priorSQL accepted; scoped query OPEN | fixture mechanics | backend/Root; P5-A2 source |
| G05 | pure/PG aware fixture accepted; operational coverage/retention/SQLite readiness UNKNOWN | fixture time/coverage only | backend/Root/operator; P5-A2 coverage |
| G06 | current assignment primitives; bounded snapshot/recheck OPEN; API auth/use-time access OPEN | internal source mechanics only | backend/Root; P5-A2 security/API |
| G07 | scheduler/claim/recovery OPEN | NO | backend/Root; P5-A2 runtime |
| G08 | pure signals accepted; operational false positives OPEN | NO | backend/operator; P5-A2 signals |
| G09 | pure forecast accepted; operational accuracy OPEN | NO | backend/operator; P5-A2 forecast |
| G10 | pure calibration/drift accepted; monitoring/display OPEN | NO | backend/UI/Root; P5-A2 quality/P5-B |
| G11 | API/UI/history/freshness OPEN | NO | backend/UI/Root; P5-A2 application |
| G12 | exact human approval OPEN | NO | backend/UI/operator; P5-A2 approval |
| G13 | pure/priorSQL fixture accepted; integrated runtime drills OPEN | source failure only | backend/Root; P5-A2 drills |
| G14 | real-provider governance HELD | NO | Root/operator; separately admitted P5-A2 REVIEW |

All remainders retain canonical SPEC destinations. P5-B dashboard/search/observability:
backend/UI/Root; P5-C backup/resilience/security/performance: backend/Root/operator;
P5-D deployment/Shadow Mode/release: Root/operator. Phase5 0/5. Unknown production
coverage is not a fixture-BUILD dependency: default operational resolver must refuse.
Product return: internal fixture-admissible HistoryInput or closed refusal; independent
Stage A source review, then separately reviewed Stage B admission. No automatic effect.

## Exact paths and roles

Each executable <=300 lines, target <=250. Foreseeable helpers already named; no globs
or extra splits. Existing hosts add only tiny imports/delegates. Need another path or
budget change: stop for consolidated WO amendment before mutation.

Worker source paths:
- packages/operations-ledger/src/operations_ledger/_proactive_source_types.py
- packages/operations-ledger/src/operations_ledger/_proactive_source_sql.py
- packages/operations-ledger/src/operations_ledger/_proactive_source_sql_content.py
- packages/operations-ledger/src/operations_ledger/ledger.py
- packages/operations-ledger/src/operations_ledger/sql_ledger.py
- apps/workspace-api/src/workspace_api/infrastructure/repository.py
- apps/workspace-api/src/workspace_api/infrastructure/_proactive_source_memory.py
- apps/workspace-api/src/workspace_api/application/proactive_source.py
- apps/workspace-api/src/workspace_api/application/proactive_source_receipt.py

Worker test paths:
- tests/unit/p5a2_scoped_source_helpers.py
- tests/unit/test_p5a2_scoped_source.py
- tests/unit/test_p5a2_scoped_source_caps.py
- tests/unit/test_p5a2_scoped_source_family.py
- tests/integration/test_p5a2_scoped_source_sql.py

Worker return: docs/decisions/P5A2_SCOPED_HISTORY_SOURCE_WORKER_RETURN_2026-10-26.md.
Independent reviewer owns docs/decisions/P5A2_SCOPED_HISTORY_SOURCE_BUILD_REVIEW_2026-10-26.md.
Root-only: this WO; tests/fixtures/p5a2_scoped_source_oracle.json (frozen, never change
expectations to fit loader); docs/cvf/invariants/p5a2-scoped-source-outcomes.json and
docs/specs/p5a2_scoped_source_invariant_pin.py (binding only); canonical SESSION
state/bootstrap/memory/activehandoff and compatibility mirror; IMPLEMENTATION_STATUS.json;
docs/INDEX.md; docs/implementation/EXECUTION_ROADMAP.md; docs/catalog/MODULE_REGISTRY.json
and MODULE_CATALOG.md; knowledge/PROJECT_CONTEXT.md, GOVERNANCE_BOUNDARIES.md, manifest.json.

## Native unit, coverage and preflight contract

Reuse native Shift/ACTIVE assignment/Report/pure owners. Ledger gains exactly two ports:
scoped_source_read(user_id,start,end,as_of), context manager yielding package-owned
ScopedSourceUnit; fresh_scoped_cohort(user_id,start,end,prior_shift_ids), returning
FreshCohort (full capped current cohort AND current active membership of all priorIDs,
even outside new window). CohortKey/CandidateKey metadata and scoped exception belong
to _proactive_source_types.py. SQL/memory helpers implement; host delegates only.
No reverse import from operations-ledger to workspace_api; app never scans engine/lock.

Deny-first trusted existing Principal + server-composed scope mapping before storage;
scope string is not permission. Validate aware start<end<=asof and accepted versionpair.
One read unit: ordered eligible Shift+ACTIVE assignment ends_at[start,end) LIMIT501,
including reportless; ordered total END_SHIFT version metadata created<=asof LIMIT501,
regardless of status/is_current. Preflight Incident source refs AND incident-section
record lengths for every candidate using metadata/scalar JSONB count before transferring,
copying or constructing ANY Report body. All501 refuse; no partial success. Only then
load capped bodies on same unit and reconstruct with native _row_to_report. Check exact
metadata/count/body identity; unchanged parent validation checks immutable whole content
and every candidate, including superseded in-window versions, before final selection.

SQL: one PostgreSQL connection, explicit REPEATABLE READ and SET TRANSACTION READ ONLY
before reads. Seal/close first unit; NEW coherent read-only transaction for whole fresh
cohort plus prior-ID active membership. Same old RR snapshot is not fresh. Revoke maps
ACCESS_DENIED; additions/version/enrollment-time change SCOPE_INCOMPLETE. Missing coherent
or fresh capability SNAPSHOT_UNAVAILABLE. All resources close/rollback, no retries/writes.
Memory: native shared lock covers metadata/preflight then capped deepcopy; release then
fresh reacquire. Never transaction() full-store copy before caps. SQLite diagnostic
metadata reads may detect native naive timestamps -> TIME_AMBIGUOUS, no inferred UTC,
no Report body load/READY; unsupported snapshot refuses safely. No SQLite parity claim.

CoverageVerifier is a trusted server-composed port. Default production authority absent
-> COVERAGE_UNKNOWN. HARNESS-only attestor compares independently seeded exact fixture
instance/actor/scope/window/asof/versionpair/cohort/candidate sets; no caller boolean or
production override. Python trusted context is an internal caller precondition, not API
JWT authentication proof. Fresh failure discards payload and every data-bearing field;
later run/use/approval must recheck independently.

## Pre-loader independent oracle and required evidence

Root-frozen tests/fixtures/p5a2_scoped_source_oracle.json raw SHA256
0f79676b627aceebd5e83a4b8143d29feda8deaad9392ad52cdd7204b593a044.
Stdlib-only projection of old immutable PG36 oracle raw12ad36cb at HEAD814d32b,
before any loader/emitter; recipe retained .venv/prepare_p5a2_source_oracle.py and
provenance in JSON. Shift.ends_at=cutoff; UUID5 DNS assignment name
p5a2-source-assignment-{shift_id}. Two full ready receipts, selected lineage and pure
analysis; source digests a27bdcd3 /57c64e0e. Coverage seed digest hashes exact canonical
seed in each case. No new implementation generated expected results.

Compare full exact outputs. Exercise all22 frozen refusal cases; exact receipt/payloadNone.
Construct valid native500/501 each dimension (eligible/candidate versions/refs), spies
fail if body fetched/copied/constructed before caps. Reportless, late correction,
superseded versions, immutable corruption, naive/causal time, deny with bad data,
unknown coverage, missing coherent/fresh view, sanitized storage failure, post-seal
revoke/add/assignment-version/Shift-time enrollment and returned-copy isolation.
Inert SQL corpus checks metadata-only LIMIT501, JSONB scalar caps, RR/read-only single
source connection then new fresh connection sequencing; temporary SQLite negative.
Fakes prove deterministic mechanics only. Actual PostgreSQL transaction proof Stage B.

## Invariant-Family Proof

Follow docs/cvf/INVARIANT_FAMILY_STANDARD.md; matrix owns shapes, not this WO.
Family P5A2-SCOPED-SOURCE-OUTCOMES current canonical digest
bca9bb9d5d201a6daeb05c58eb850dc53f27c3235a99cb71e15954bd1702273b.
Actual emitter: proactive_source_receipt.py emit_source_ready/emit_source_refused;
SourceQueryResult carries internal payload. Evidence: four exact tests above plus
existing generic contract/repository corpus. Root adds real emitter CANONICAL_DIGEST
consumer, symbol P5A2_SCOPED_SOURCE_MATRIX_CANONICAL_DIGEST, retaining staticpin.
Only ownership/evidence/emitter identity/boundedclaim changes after paths exist and
before acceptance; preserve contractSource/shapes/domains/relations/exclusions.
Independent reviewer recomputes matrix/static/runtime pins, reruns full corpus,
samples raw emitted positive for BOTH outcomes and verifies expectations predate BUILD.
Nested-object exclusions apply only flat receipt; explicitly corrupt parsed manifest,
counts/header/digest/lineage/sourcebytes in backend tests. Reviewer acknowledges exclusions.
Evidence owner backendworker. No runtime proof before tests actually pass.

SOURCE-WO-F1 correction before dispatch: proactive_source_receipt.py also owns
validate_source_receipt(receipt), the native closed receipt validator/consumer.
Both emit_source_ready and emit_source_refused must use it. The family test must
capture BOTH real native emitted outcomes, generate the matrix-declared complete
mutation basis from each raw sample and reject EVERY mutation through this native
validator/consumer, separately from generic matrix validation. Register all four
actual source evidence test paths in the matrix during Root binding promotion.
Retain counts of samples/mutations/rejections and any exclusions; independent
REVIEWER reruns this same native corpus, recomputes pins and samples raw outcomes.
Manifest/header/count/digest/lineage corruptions additionally exercise native semantic
validation (not only matrix shape). No matrix expectation may be derived in BUILD.

Exact test command: .venv/Scripts/python.exe -m pytest -q tests/unit/test_p5a2_scoped_source.py tests/unit/test_p5a2_scoped_source_caps.py tests/unit/test_p5a2_scoped_source_family.py tests/integration/test_p5a2_scoped_source_sql.py
Generic corpus: tests/unit/test_invariant_family_contract.py and tests/integration/test_invariant_family_repository_guard.py.
Required guards: check_cvf_core_machine_inheritance.py --enforce, check_session_state.py,
check_project_knowledge.py, check_file_size.py, check_invariant_families.py,
generate_catalog.py --check. Full suite only normal unmodified commit hook; no bypass.

## Effects, stop and return

Stage A local code/tests/temporarySQLite only. NO provider/network/Docker/image/package
installation/realcredential/.env/CSV/schema/routes/UI/scheduler/approval/production writes.
CVF repos/hook/frozen parent SPEC/matrix/pure/oldoracle/SQLrunner/receipt unchanged.
Root owns local commits; no push/publicrelease. Stage B HELD: needs independentStageA
PASS, new finite effect packet, committed source/admission plus continuity. Old Docker
ceilings spent, no reset/retry/install/pull. Stop outside exact authority; one consolidated
Root amendment. Before repair consolidate predictable findings; round3 without independent
new root cause records REVIEW_COST_ESCALATION_REQUIRED. Worker return declares standalone
marker, full actual manifest/failures/limits and reconciled milestone remainders. Native
Core CLI docs/decisions selector limit requires explicit verified check_recheck + marker.

## Gate-To-Role Closeability Contract

closeabilityContractVersion: cvf.gate-role-closeability@1.0.0
closeabilityDisposition: CLOSEABLE
returnTimeRecheck: REQUIRED_BEFORE_REPAIR
implementationTopologyPolicy: EXACT_PATHS_WITH_NO_FORESEEABLE_SPLIT
foreseeableFileSplitDisposition: NOT_REQUIRED_UNDER_SIZE_BUDGET

| gateId | mustPassBy | repairOwner | repairPhase | mutationSurface | topology | commitOwner | commitPhase | dependsOn |
|---|---|---|---|---|---|---|---|---|
| authorization_review | PRE_DISPATCH | work-order-author | PRE_DISPATCH | docs/work_orders/P5A2_SCOPED_HISTORY_SOURCE_WORK_ORDER.md;tests/fixtures/p5a2_scoped_source_oracle.json | EXACT_PATHS | commit-steward | DISPATCH_COMMIT | NONE |
| pre_dispatch_gate | PRE_DISPATCH | orchestrator | PRE_DISPATCH | docs/work_orders/P5A2_SCOPED_HISTORY_SOURCE_WORK_ORDER.md;SESSION/handoffs/AGENT_HANDOFF_P5A2_SCOPED_SOURCE_QUERY_2026-10-26.md | EXACT_PATHS | commit-steward | DISPATCH_COMMIT | authorization_review |
| dispatch_continuity | IMPLEMENTATION | session-sync-steward | IMPLEMENTATION | SESSION/handoffs/AGENT_HANDOFF_P5A2_SCOPED_SOURCE_QUERY_2026-10-26.md material-SHA marker | EXACT_PATHS | session-sync-steward | DISPATCH_CONTINUITY_COMMIT | pre_dispatch_gate |
| pre_implementation_autorun | IMPLEMENTATION | orchestrator | IMPLEMENTATION | docs/work_orders/P5A2_SCOPED_HISTORY_SOURCE_WORK_ORDER.md;SESSION/handoffs/AGENT_HANDOFF_P5A2_SCOPED_SOURCE_QUERY_2026-10-26.md | EXACT_PATHS | commit-steward | MATERIAL_COMMIT | dispatch_continuity |
| focused_checker_tests | WORKER_RETURN | implementation-worker | IMPLEMENTATION | Exact worker source/test paths listed above | EXACT_PATHS | commit-steward | MATERIAL_COMMIT | dispatch_continuity,pre_implementation_autorun |
| adif_integrity | WORKER_RETURN | implementation-worker | IMPLEMENTATION | docs/decisions/P5A2_SCOPED_HISTORY_SOURCE_WORKER_RETURN_2026-10-26.md | EXACT_PATHS | commit-steward | MATERIAL_COMMIT | dispatch_continuity |
| worker_return_fast | WORKER_RETURN | implementation-worker | WORKER_RETURN | docs/decisions/P5A2_SCOPED_HISTORY_SOURCE_WORKER_RETURN_2026-10-26.md | EXACT_PATHS | commit-steward | MATERIAL_COMMIT | focused_checker_tests,adif_integrity |
| reviewer_fast | REVIEW | reviewer | REVIEW | docs/decisions/P5A2_SCOPED_HISTORY_SOURCE_BUILD_REVIEW_2026-10-26.md | EXACT_PATHS | commit-steward | MATERIAL_COMMIT | worker_return_fast |
| pre_commit | PRE_MATERIAL_COMMIT | repair-worker | PRE_MATERIAL_COMMIT | Exact worker paths and Root-only metadata/family paths listed above | EXACT_PATHS | commit-steward | MATERIAL_COMMIT | reviewer_fast |
| terminal_completion_review | POST_MATERIAL | reviewer | POST_MATERIAL | docs/decisions/P5A2_SCOPED_HISTORY_SOURCE_BUILD_REVIEW_2026-10-26.md | EXACT_PATHS | commit-steward | CORRECTIVE_MATERIAL_COMMIT | pre_commit |
| continuity | CONTINUITY_COMMIT | session-sync-steward | CONTINUITY_COMMIT | SESSION/handoffs/AGENT_HANDOFF_P5A2_SCOPED_SOURCE_QUERY_2026-10-26.md;SESSION/ACTIVE_SESSION_STATE.json;SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json;SESSION/SESSION_MEMORY.md;CVF_SESSION/ACTIVE_SESSION_STATE.json | EXACT_PATHS | session-sync-steward | CONTINUITY_COMMIT | terminal_completion_review |
| committed_range_closure | POST_MATERIAL_CLOSURE | reviewer | POST_MATERIAL_CLOSURE | SESSION/handoffs/AGENT_HANDOFF_P5A2_SCOPED_SOURCE_QUERY_2026-10-26.md | EXACT_PATHS | session-sync-steward | CONTINUITY_COMMIT | continuity |


## AM1 — finite pre-dispatch helper isolation repair

Normal dispatch hook stopped with no commit: 1failed/3244passed/147skipped/
4warnings/8errors in200.47s; retained .venv/p5a2-scoped-source-dispatch-20261026.log.
All9 cases share _pinned_helper's global Core `git status --porcelain` assertion
at tests/integration/test_project_knowledge_ingest_rehearsal.py:47. Unrelated
model-gateway tracked edits in installed Core trigger it; selected bound controls,
Core HEAD/public origin and pinned ingestion helper remain intact. No Core writes.
This single compatibility defect blocks the G04–G06 product dispatch above.

Add ONLY tests/integration/test_project_knowledge_ingest_rehearsal.py to worker
pre-dispatch repair scope (same test artifact class/R2/no effects/Rootcommitowner).
Replace whole-Core cleanliness dependency with existing exact installed-control
verification and helper Git-blob/hash integrity. Preserve HELPER_SHA256,
public origin/exact HEAD pin, network-token scan, actual native PowerShell
rehearsal, all negative index cases and cleanup. No skipping/weakened controls.
Add disposable local Git fixture regression showing unrelated dirty tracked Core
file tolerated, but changed/missing helper and bound control, wrong origin/pin
still fail. Fixture uses copied installed control/helper bytes and local temporary
Git only; never modifies actual Core or contacts remote. Keep file <=300 lines.

Independent AM1 authorization precedes this finite pre-dispatch repair activation;
it does not activate main Stage A BUILD. Backend worker owns this ONE test path
and own worker-return path; Root WO/handoff records failure/repair, independent
REVIEWER checks diff/regressions then normal dispatch retry. Full14gap binding/
remainder/owners/destinations/Phase5 0/5 above unchanged; stop once dispatch is
unblocked and RETURN source Stage A after its committed dispatch/continuity.
No follow-on support survey, global Core cleanup, source/HEAD/hash changes,
Docker/provider/package/credentials effect or hook bypass. Graph focused/precommit
mutation surfaces include this exact AM1 path; pre-dispatch failure repair is
owned by work-order-author with backendworker implementation and independent
review, before authorization_review/pre_dispatch_gate can pass again.

AM1 independent REPAIR_REVIEW_PASS_BOUNDED,37focusedPASS18.24s and independent37PASS19.03s; one-testpath repair complete. Root retries normal dispatch; original failed log retained. Main source activation still requires actual dispatch/dedicated continuity.


## Stage A acceptance and execution authority exhaustion

Independent STAGE_A_REVIEW_PASS_BOUNDED after consolidated repair1/repair2;
SOURCE-A-F1–F4 and adjacent F2-R1/F3-R1 resolved, openfindingsNONE/waiversNONE.
Source+generic91PASS2skip5.71s; independent91PASS2skip5.25s. Both frozen full
oracle receipts/lineage/analysis, native500/501x3zero-bodycopy, exactfixtureseed,
foreign exclusion/denial precedence, realreceipt metadata and native84mutation
rejections accepted. Runtimefamily binding9b3 and frozenoracle0f unchanged.
Only fixture-internal Stage A is accepted; actualPGquery/snapshot behavior,
APIauth/productionretention/quality/approval/AI proof remain unaccepted.
No continuing worker BUILD/effect grant. Root normalmaterial/terminalreview/
dedicatedactualSHAcontinuity/cleanrange still required for boundedclosure.
Stage B remains HELD until separately reviewed finite effect admission and
committed source/admission/continuity; oldphysicalceilings never reset.
Full14gap/owners/P5-B/C/D destinations above and Phase5 0/5 remain unchanged.
