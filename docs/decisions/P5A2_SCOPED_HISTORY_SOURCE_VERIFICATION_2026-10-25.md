# P5-A2 G04–G06 scoped-history source verification — finite INTAKE draft

Date 2026-10-25. Role INTERNAL_AGENT source-verification author; risk R2; project revision `552612603bb35fd97a9f688787948542dc59e86e`. Root independently reviews this direction before SPEC/Work Order. This is static source inspection, not BUILD authorization, a live governance proof, or a complete repository survey. Public core `b69e1088978e8c90ac58a2243fcf8f90d0f857ed` and operator-local provenance `6d5c4a5de4b23e4ec5cb5a54fb8f0c8e6a71fd2c` are read-only. Doctor 24 PASS/2 legacy warnings; inheritance 0 violations. No test, database, provider, network, key, model, CSV, or commit action was run here.

## Product Milestone Binding

**Milestone/revision:** [Phase 5, P5-A2](../implementation/EXECUTION_ROADMAP.md#phase-5--reporting-hardening-and-freeze--in-progress-05), project revision above; full accepted 14-gap acceptance and owners in [INTAKE/DESIGN](P5A2_PROACTIVE_REPORTING_INTAKE_DESIGN_2026-10-24.md#product-milestone-binding), [SPEC](../specs/P5A2_PROACTIVE_REPORTING_SPEC.md), and [pure H1–P2 source review](P5A2_PROACTIVE_HISTORY_NUMERIC_REVIEW_2026-10-24.md). Phase 5 remains 0/5.

**User outcome/acceptance:** an authorized operator inspects integrated scheduled signals and one-shift-ahead forecasts with scope, lineage, cutoff, freshness, uncertainty, abstention and prior runs; a human approves the exact run/version/source digest before a durable recommendation or action. All G01–G14 requirements must pass with source, integration, quality, drill and owner review evidence. Root is accountable and independent reviewer; Sol owns backend/contracts/analytics/scheduler, Luna UI, operator final business acceptance. Any CVF AI-governance claim requires real-provider request/response evidence. P5-C parent-exit drills remain separately owned.

**Current truth:** P5-A A0/A1–A6 accepted locally, A7 blocked after one 401; H1–P2 pure supplied-input history/numeric portions of G03–G05/G08–G10/G13 accepted at material `9c72de4` and continuity `5526126`, normal hooks 3224 pass/146 skip/4 warnings. That proves neither actual ledger scope/retention nor integrated forecasting. Live/key/model/CSV action is held by the operator. This assignment verifies G04–G06 source capabilities and writes only this file; it closes no gap and has no BUILD, test, DB, external-effect, or commit grant. Stop at a coherent contract direction or a named unresolved dependency; return to Root for independent source review, SPEC and bounded Work Order before product implementation.

| Gap | Current evidence / remaining acceptance | In this assignment | Owner and concrete destination |
|---|---|---|---|
| G01 | P5-A A7 blocked; real 401, no accepted response | No | Root/operator: P5-A A7 decision and closure; then P5-A2 gate |
| G02 | Operational RAG corpus/index/auth/citations/application path unproved | No | Root/Sol: P5-A2 integrated-context gate |
| G03 | Pure metric/horizon and supplied-scope contract accepted; operational cohort and fit open | No | Root/Sol/operator: P5-A2 metric acceptance |
| G04 | Pure as-of/version/digest validation accepted; actual ledger series unknown | **Verify only** | Sol/Root: P5-A2 source contract and integrated history evidence |
| G05 | Pure aware-time/completeness refusal accepted; SQL timezone/retention/coverage unknown | **Verify only** | Sol/Root: P5-A2 operational time and retention evidence |
| G06 | Current assignment exists; exhaustive bounded query and revocation-safe run unknown | **Verify only** | Sol/Root: P5-A2 API/security integration |
| G07 | Scheduler/run/idempotency/recovery open | No | Sol/Root: P5-A2 runtime and drills |
| G08 | Pure trend/anomaly accepted; operational false-positive review open | No | Sol/Root/operator: P5-A2 signal acceptance |
| G09 | Pure baseline/forecast accepted; operational accuracy/business fit open | No | Sol/Root/operator: P5-A2 forecast acceptance |
| G10 | Pure calibration/drift accepted; operational monitoring/display open | No | Sol/Luna/Root: P5-A2 quality evidence; P5-B observability |
| G11 | Forecast API/UI, current/history/freshness flow open | No | Sol/Luna/Root: P5-A2 integrated application |
| G12 | Exact recommendation/run/version/digest human approval open | No | Sol/Luna/Root/operator: P5-A2 approval gate |
| G13 | Pure time-ordered evidence accepted; actual scheduler/failure/recovery drills open | No | Sol/Root: P5-A2 evaluation/drills |
| G14 | Applicable real-provider CVF governance proof parked | No | Root/operator: fresh admission and P5-A2 REVIEW if claim applies |

P5-B dashboard/search/observability remains with Sol/Luna/Root at the [P5-B roadmap item](../implementation/EXECUTION_ROADMAP.md); P5-C backup/restore/resilience/security/performance with Root/backend and operator review at P5-C; P5-D deployment/Shadow Mode/release with Root/operator at P5-D. None is accepted by this verification.

## Bounded source ledger

Exactly 20 relevant source files inspected/hashed; 0 existing test/contract files counted against the optional 10-file cap. Mandatory governance/continuity/SPEC/roadmap documents are outside the source cap. SHA-256 values are file bytes at inspection. Line references below are local to these pins; scoped inspection does not establish absence elsewhere.

| Source path | SHA-256 | Relevant lines |
|---|---|---|
| `apps/workspace-api/src/workspace_api/application/assignment_scope.py` | `0598284ccea77c63122620c55745e7c0a9b05412c1affd48963cf18fb65af000` | 23–49 |
| `apps/workspace-api/src/workspace_api/infrastructure/repository.py` | `b4ed64c6be7a16765c1a979c145e7ced6875ab399d07da2482ce535ff644eba0` | 43, 63–73, 150–151 |
| `apps/workspace-api/src/workspace_api/infrastructure/_assignment_repository.py` | `8a97573914c76a1c537f715077ffa4e35b9dda716932c973d039a2e5b1742a7d` | 95–126 |
| `apps/workspace-api/src/workspace_api/infrastructure/_report_repository.py` | `c4d3090e1c43c5575de50d4812432dce6abd8fedb96993dabd02e2e9f53f324e` | 89–126, 126–195 |
| `packages/operations-ledger/src/operations_ledger/ledger.py` | `aba08b9f9e34911ff718eb3be591e8734fe7959dca63cd15dc74746c67ba13af` | 28–44, 132–172 |
| `packages/operations-ledger/src/operations_ledger/sql_ledger.py` | `6d6164d3857659a624634d41460326afa810291489a56f16b010db85ca6b44ef` | 34–53, 76–82, 131–165 |
| `packages/operations-ledger/src/operations_ledger/_shift_queries.py` | `142fb0abb2304a12bd54ec24cbb4aa45effdd8eee036a2ad4424bfec610372ac` | 21–24 |
| `packages/operations-ledger/src/operations_ledger/_report_store.py` | `9b1c56f684bacd1b21d049323554455ab4108e9291e5d7c1e01ccf23e070fd09` | 34–59, 152–200, 200–285 |
| `packages/operations-ledger/src/operations_ledger/_rows.py` | `2abb492a51e30d578636c9de8ec97ff30b2786cd0a6a1d5bc02f336d54643999` | 12–22 |
| `packages/operations-ledger/src/operations_ledger/_assignment_store.py` | `2a81586738ede1f8269c26ba1707ca3542242d0a34238c11bd841314b5d78a6f` | 179–197, 199–242 |
| `packages/operations-ledger/src/operations_ledger/_report_tables.py` | `455005b974aaa9fe7394034a48adc50948867d5839393d03312dfcabe5a09d75` | 34–69 |
| `packages/operations-domain/src/operations_domain/report_models.py` | `67ce6c73fc9a42e752690b786c24e9282c93acb9aa05c5069cfe47cbe6864093` | 239–300 |
| `apps/workspace-api/src/workspace_api/api/shifts/router.py` | `fc0122fabee8dd3ab990e04169942d400ac75f04136fd7ea0f1c610df4faa385` | 88–103 |
| `apps/workspace-api/src/workspace_api/api/reports/router.py` | `6a5d64cb93041db2c785523fb2c4b03e4c7905a32687e0661dc67a25569c3654` | 36, 183–207 |
| `apps/workspace-api/src/workspace_api/dependencies.py` | `86e04852b2a10e87c2b4fc3af68bdeb79eee95fa219359dd75d3e2dd1b7d31f1` | 58–91 |
| `apps/workspace-api/src/workspace_api/auth/tokens.py` | `2c6b4ed636b74fb005d5d1e911358206030107834a642c6fb060c1da0c34a4b5` | 33–60, 65–113 |
| `packages/operations-ledger/src/operations_ledger/_assignment_tables.py` | `3eb40949f9d96694269508334010eaf086fff9d155bf77e4f455dbe360aac936` | 31–55 |
| `packages/operations-ledger/src/operations_ledger/tables.py` | `81ec3aab2ce00a5fd233682bbc410f058288b311fa0c219db25fbf5537457b2a` | 70–84, 213–226, 282–289 |
| `packages/reporting-engine/src/reporting_engine/proactive_history.py` | `cad9546dcc46d137ecbea2cfab24d656b7990f6075a72875b012b5196c044c9f` | 15–43, 56–96, 97–154 |
| `packages/reporting-engine/src/reporting_engine/proactive_models.py` | `f61fbbfc141b872294e6a1cccf1a389ecc05eea34e61b3025c1183f289172004` | 23–32, 67–77 |

## Verified native capability and missing connection

1. **G04, reuse:** `Ledger.list_reports_for_shift(shift_id, report_type, unit=)` returns every version; SQL orders version descending, in-memory deep-copies content. SQL unique `(shift_id,report_type,version)`, partial unique current index, report model source manifest and digest, and lifecycle-only `put_report`/successor are already present. Pure `proactive_history` validates supplied immutable content/manifest and selects one visible version per shift as-of. Reuse these owners; neither today's `status` nor `is_current` proves historical approval. There is no native cross-shift point-in-time candidate query in these inspected interfaces.
2. **G05, boundedness/time:** `SqlLedger.list_shifts()` delegates to `_shift_queries.list_shifts`, which executes unfiltered `select(shifts).mappings().all()` on a fresh engine connection and has no `unit=`. In-memory `list_shifts()` returns a list of live Shift objects without a lock or copies (repository lines 150–151). Each SQL per-shift report-history call executes `.all()` and creates full Report objects; `/reports?include_history` checks its 100-row maximum only after that. `/shifts` similarly filters already materialized shifts and checks 500 afterward. Thus existing limits do **not** prove cap-before-materialization, exhaustive page boundaries, or an atomic shift/report/assignment snapshot. `DateTime(timezone=True)` and SQLite `BEGIN` do not prove returned SQLite timestamps are aware. Reject naive persisted values as `TIMEZONE_UNSPECIFIED`/`TIME_AMBIGUOUS`; do not attach UTC. No retention/coverage attestation or late/corrected-report window proof is exposed by these inspected methods. `complete=true` and `retention_complete=true` in pure `HistoryInput` are assertions supplied by a caller, not database facts.
3. **G06, current access:** verified bearer token builds `Principal(user_id,role)`; `AssignmentScope.require_shift` queries `get_active_assignment` and masks missing/inaccessible shift. `assigned_shifts` loops all `list_shifts()` results and performs a separate assignment lookup for each, without a single unit. SQL active assignment query filters ACTIVE, and revoke is version-checked; in-memory uses the shared lock per call. `/reports` checks assignment before returning one shift's history, but it lacks a run-wide scope/cutoff/retention contract. Current token role alone is not assignment access. No inspected query joins active membership, time window, eligible shifts and report versions with server-side count bounds or stable pagination. A revoke between separately issued reads can invalidate a previously authorized source set.

**Unresolved cohort dependency:** the accepted SPEC puts observations in `[start,end)` by *selected Report cutoff* while also requiring an exhaustive eligible-shift manifest that detects shifts **without** reports. A reportless shift has no Report cutoff. The inspected Shift table has `starts_at`/`ends_at`, but neither source nor SPEC declares which shift-time rule enrolls it, how noncontiguous assignment tenure affects enrollment, or an authoritative retention/coverage owner. Deriving eligible IDs only from Report rows would erase missing shifts and falsely assert completeness. Root SPEC_AUTHOR must choose and review a server-owned cohort rule tied to Shift time/window and current assignment, with a clear treatment of reportless shifts, late-created versions, and historical query boundaries; operator accepts metric population/business fit. Until that decision and retention authority are evidenced, `BLOCKED_COHORT_DEFINITION` plus `BLOCKED_RETENTION_ATTESTATION` bar an actual `complete=true` claim and require `SCOPE_INCOMPLETE`. No UTC repair is inferred.

**Smallest proposed integrated source contract (for Root SPEC/WO, not this assignment):** one backend query/adapter owned by Sol over existing Ledger/Report/assignment and pure HistoryInput, **after** Root resolves the cohort dependency. Authenticate current principal; take a consistent backend read snapshot or explicitly fail closed if it cannot be guaranteed; count *all* enrolled assignment-scoped shift IDs including reportless ones, all candidate END_SHIFT versions (including past versions available by `run_as_of`), and selected snapshot incident refs before constructing Report objects. Enforce the SPEC's 500/500/500 bounds, `[start,end)`, `created_at <= run_as_of`, cutoff, retention/coverage and complete-manifest assertions from proven backend facts; no first-page success. Supply immutable full report bytes and ordered IDs to the accepted pure validator, which performs digest/as-of selection. Revalidate active assignment at read, run and approval/use; if revocation or concurrent source mutation prevents a coherent snapshot, return scoped refusal and no durable recommendation. SQLite-aware timestamp origin/retention policy and actual transaction isolation for both SQLite and PostgreSQL need explicit negative evidence before acceptance. Invariant-family [standard](../cvf/INVARIANT_FAMILY_STANDARD.md) applies when a shared receipt/outcome contract is materially authored; no matrix changes here.

**Product return:** G04–G06 remain UNKNOWN/OPEN for runtime. Root checks these pinned claims and resolves the retention/time/snapshot dependency in a reviewed SPEC and bounded Work Order; only then may a worker implement the missing native adapter/query connection. G01/G02 and G07–G14, P5-B/C/D and Phase 5 remain at their named gates. No automatic support survey follows this draft.

## Root independent source review — 2026-10-25

Disposition SOURCE_VERIFICATION_ACCEPTED_BOUNDED. Root ORCHESTRATOR to REVIEWER
(separate from source author), then SPEC_AUTHOR for the companion proposal.
All20source SHA pins independently recomputed MATCH; targeted source reads confirm
unbounded listing, separate SQL connection, timezone limitation and the
reportless-cohort/retention unknowns. No extra runtime test or database call.
User asks for a clearer audit/proposal and whether mock data can be used.
That is not authority to replace provider proof or assert operational coverage.
Real operational data is not needed for a fixture-scoped source-adapter contract.
The accepted pure subset and native harness can be reused with explicit
synthetic provenance; current operational G04-G06 remains UNKNOWN/OPEN.

Root inspected relevant excerpts of four existing test surfaces (not a claim
of full-file or repository completeness). These count4/10 optional test files;
no new source file was added to the worker20source inventory. Existing accepted
3224/146/4 evidence is retained, not recreated for this static audit:

| Test surface | SHA-256 bytes | Inspected relevance |
|---|---|---|
| `tests/unit/proactive_helpers.py` | `72aaef3653e9b4886d3cb8cf322a2b3596983813d6b7e5b75dea45cf4598de25` | PUBLIC synthetic canonical Report generator and explicit HistoryInput |
| `tests/integration/test_proactive_supplied_contract.py` | `88746f7c8c98ea938d98370d490b244b1e22110eaf29ee458a88b2b99af3ddac` | Digest/version/naive-time/cap refusals over supplied fixtures |
| `tests/integration/test_report_ledger_parity.py` | `ce1d18b5d3db43a20e4eabd983a2dc7886936f96bf246da6d59966b1234d4113` | Actual InMemory and disposable SQLite Report parity harness |
| `tests/cvf/test_assignment_scope_routes.py` | `7e513aec7418fc605171920cbdc974fc943af4501ecaf136c44ad1e825b064eb` | Actual FastAPI/auth-header/assignment harness; no new AI-governance proof |

Tranche source-verification outcome: bounded inspection accepted. Product
position: no G01-G14 criterion or Phase5 milestone closes; owners/destinations
above remain. Companion synthetic-data proposal needs independent review
before accepted direction; future SPEC/WO remains prerequisite to BUILD.
