# P5-A2 same-unit recovery AM2 — source/SQL/HTTP accepted, UI failed

Self-declared worker-return artifact: yes
Status: COMPLETE_PENDING_REVIEW
Date: 2026-10-27. Risk R2. Root return/effect/commit owner;
source worker consolidated_recovery_design (Sol-Medium), native SQL test worker
stage_b_result_review (Luna-Max), independent reviewer recovery_review.

## Disposition and observable acceptance

SOURCE_SQL_HTTP_AND_FAILED_UI_EVIDENCE_READY. PHYSICAL_ACCEPTANCE_NOT_MET.
The operator-approved seeder/conditional sole timestamp repair is implemented
and actual PostgreSQL confirms exactly users1/shifts36/assignments36/reports37,
all27other tables0. The only data mismatch was this synthetic user's created_at;
the guarded transaction changed that one field, verified every other raw/native
field/security/hash and committed. Password hash, role, ID and other data stayed
unchanged. Same volume/nonce/credentials, no reset/reseed/migration/schema change.
Real JWT login200 and both frozen native source HTTP receipt digests passed.
Actual UI used one browser context and failed at LOGIN before any login/query/
screenshot. No second context, restart, recovery or smoke was attempted.
The exact browser exception was not retained. Later read-only custody inspection
found API/web PIDs absent and the new owned container stopped; the termination
cause is UNKNOWN. The intervening interruption is history, not causal proof.
Cleanup removed only that stopped exact owned container, preserved the volume,
and registered volume1/container0/API0/web0. No further app data writes occurred.

This return completes the current source/result documentation for review; it
does not accept the missing UI milestone or authorize another effect budget.
Tranche disposition: source and partial physical evidence accepted for review,
UI acceptance FAILED; only a settled evidence record can later freeze.
Milestone disposition: P5-A2 OPEN, Phase5 0/5; no whole product gap closes.

## Product Milestone Binding

Milestone P5-A2 in docs/implementation/EXECUTION_ROADMAP.md at actual AM2
dispatch044ed5c and continuitydbbabe4 plus this current result. The full user
outcome is an authorized integrated scheduled flow for signals, forecasts,
history/lineage, freshness, uncertainty and abstention, with exact human
run/version/source approval before any durable recommendation/action.
Full acceptance remains P5A2_PROACTIVE_REPORTING_SPEC: operational source
authority/retention, scheduler/recovery, cohort/method fit, signals/forecast/
drift quality, integrated application access/display, exact approval, drills
and real provider governance proof when a claim applies. Operator and an
independent reviewer own milestone acceptance. Mock output is not AI proof.
Current accepted bounded source/substrate/API/manual UI/numeric history stays
accepted. AM2 now adds actual one-field synthetic timestamp repair and SQL/JWT/
HTTP proof; actual standing-source UI acceptance remains missing. Operational
coverage is UNKNOWN. This assignment addressed only the synthetic G04/G05 route.

| Gap | Current evidence / limitation | AM2 result | Accountable owner / concrete destination |
|---|---|---|---|
| G01/A7 | Real provider401 spent; BLOCKED | None | Root/operator, P5-A A7 then P5-A2 |
| G02 | Operational RAG/context/index/citations BLOCKED | None | Backend/Root, P5-A2 context |
| G03 | Pure numeric accepted; business/cohort fit UNKNOWN | None | Backend/operator, P5-A2 method |
| G04 | Fixture/PG query/API/source accepted; operational integration UNKNOWN | Synthetic SQL/JWT/HTTP PASS, UI FAILED; gap stays open | Backend/Root, P5-A2 source |
| G05 | Fixture authority/coverage accepted; production mode/authority/coverage/retention/SQLite UNKNOWN | Exact synthetic rows/security/hash PASS, UI missing | Backend/Root/operator, P5-A2 coverage |
| G06 | Native/HTTP identity/fresh release accepted; later use-time access OPEN | None | Backend/Root, P5-A2 approval |
| G07 | Scheduler/claim/recovery OPEN | No operational runtime acceptance | Backend/Root, P5-A2 runtime |
| G08 | Pure signals accepted; operational quality OPEN | None | Backend/operator, P5-A2 signals |
| G09 | Pure forecasts accepted; operational accuracy OPEN | None | Backend/operator, P5-A2 forecasting |
| G10 | Pure drift accepted; monitoring/display OPEN | None | Backend/UI/Root, P5-A2 quality and P5-B |
| G11 | Source API/manual UI source accepted; other flows OPEN | Actual source-panel proof failed before queries | UI/Root/operator, P5-A2 application |
| G12 | Exact human approval OPEN | None | Backend/UI/operator, P5-A2 approval |
| G13 | Fixture/stale/session drills accepted; integrated drills OPEN | Synthetic failure/custody evidence only | Backend/Root, P5-A2 drills and P5-C |
| G14 | Live AI-governance proof HELD | Provider calls0; NO_AI | Root/operator, separately admitted P5-A2 REVIEW |

P5-B dashboard/search/observability: backend/UI/Root. P5-C backup/resilience/
security/performance: backend/Root/operator. P5-D deployment/Shadow Mode/release:
Root/operator. UNKNOWN remains a blocker for future bounded verification.
No support work automatically authorizes another tranche. The product return
is the unchanged P5-A2 integrated context/runtime/quality/approval/drill path;
this local UI gap remains visible and cannot be silently excluded to close it.

## Evidence and scope

Canonical evidence: P5A2_SYNTHETIC_BACKEND_RECOVERY_AM2_EVIDENCE_2026-10-27.json;
admission: P5A2_SYNTHETIC_BACKEND_RECOVERY_AM2_ADMISSION_2026-10-27.json.
Normal dispatch044ed5c exact18 and continuitydbbabe4 exact5 independently clean;
hooks3483PASS148skip4warnings220.32s/219.79s. Source independent checkpoint
SOURCE_CHECKPOINT_PASS_BOUNDED pins ten actual source/test raw/LF hashes;
worker68PASS23.76s, independent60PASS23.19s; four emitted seed-family outcomes,
complete generated mutation corpus and existing lifecycle18/full608 passed.
Native transaction13PASS includes actual SQLite SQL/rollback/schema drift with
scoped PG-type converters; it is not physical PostgreSQL proof by itself.
The actual retained-volume run supplies physical PostgreSQL16.15 RR/RO evidence.

AM2 preflight1, exclusive marker1, recover1, new container1, API/web start1each;
smoke1/realJWT1/sourceHTTP2; actualbrowsercontext1/login0/query0/screenshot0.
Native seed0, CAS changes1 field, no extra SQL inspection beyond admitted
inventory/write/postsummary/smoke paths. No new volume/nonce/credential,
migration/schema repair/reset/ACL/install/pull/provider/public/deploy/push.
All old failed packets/markers and frozen fixtures/oracles/migrations remain
byte-pinned; current AM2 marker is immutable and SPENT. Source bytes stayed
frozen throughout proof. Ten actual source/test paths are:

- apps/workspace-api/src/workspace_api/demo/seed.py
- apps/workspace-api/src/workspace_api/demo/seed_recovery.py
- apps/workspace-api/src/workspace_api/demo/seed_recovery_compare.py
- scripts/p5a2_source_demo_recover.py
- scripts/p5a2_source_demo_recovery_inventory.py
- scripts/p5a2_source_demo_recovery_custody.py
- tests/unit/test_p5a2_demo_recovery_source.py
- tests/unit/test_p5a2_demo_recovery_findings.py
- tests/unit/test_p5a2_demo_seed_recovery.py
- tests/unit/test_p5a2_demo_seed_transactions.py


The actual prewrite user timestamp was 2026-10-26T21:46:26.699812Z; frozen target
is 2025-12-31T20:00:00Z. The last native/post state digest is
d9418536c37fadc684a73ecfb2d2c67199bae29dfe5f43db5f12239b4ad8518b;
schema digest d1b13a0a45bad4c3607e5fbdb6439082df6f4b1ff3cd2f90398d4d0c228716db.
Actual owned container877cd8fc... was removed; final merged owner digest
3af5e4892aaea7bfe64422ed7f3b237a6d54f910c8e2d0dbc68e6e925b9599ab.
Last accepted SQL state is EXACT_SEEDED; cleanup retained volume and made no
app data write. No additional post-cleanup SQL query is claimed.

## Orchestration and failure limits

A target-prelude assertion initially compared the raw lifecycle/context
storage envelope digest to the merged record digest. It stopped before any
write/proof; official common.read_owner resolved the comparison and an
independent TARGET_GO verified current IDs/digest/volume. No runtime retry.
Node rejected eval code generation before a browser launched. Direct execution
of the unchanged reviewed procedure then used the sole actual context.
Its result file, not the empty immediate tool return, records the UI failure.
No screenshot or mocked replacement was manufactured.
The all-live cleanup correctly refused before effects when its live-resource
predicate was no longer established. Independent readonly reconciliation and
STATIC_CLEANUP_GO_BOUNDED admitted only a stopped exact-container/absent-PID
cleanup. That route passed: volume1/container0/API0/web0, appwrites0/restarts0.
The native frozen stop helper's reversed stopped-state check was not invoked.

## Concrete possible continuation — NOT AUTHORIZED

Current AM2 execution is SPENT. No automatic new support tranche or retry.
If the operator elects to finish this SAME acceptance unit, a fresh reviewed
runtime/browser budget is required: preserve already accepted source/data
repair; inspect retained owner/volume/fingerprint/rows read-only, refuse any
mismatch; start at most one exact owned profile using existing credentials,
verify-only with zero seed/CAS writes, then use exactly ONE browser context for TWO existing as-of panel
submissions and capture TWO real panel screenshots. Check actual
process/container liveness immediately before UI and keep execution contiguous;
no second recovery/browser attempt, reset, provider, new source feature or
production claim. Exact new custody baseline/budget must be independently
admitted before effect; never repurpose this spent marker. Source/data repair
must not be repeated. Declining leaves the safe retained-volume checkpoint.
This proposal does not itself grant source/runtime authority.

## Agent Operation Trace Block

| Field | Evidence |
|---|---|
| Actor | Root IMPLEMENTATION_WORKER for effects; REPAIR_WORKER exact cleanup; ORCHESTRATOR return |
| Provider or surface | Local repository, fixed Desktop Linux pipe, PostgreSQL16.15, cached Chromium; NO_AI |
| Working directory | downstream project root only |
| Allowed scope source | explicit operator reply and reviewed SAME-unit AM2 SPEC/WO/admission |
| Actual changed set | ten sealed source/test paths plus admitted Root/result/continuity/catalog families |
| Manifest delta | EXACT_MATCH_AUTHORIZED_FAMILY |
| Commit owner | Root COMMIT_STEWARD after independent review and normal gates |
| Claim boundary | source/data repair and local synthetic SQL/JWT/HTTP only; UI failed, milestone open |

## Epistemic Process Block

Expected: sole-created_at repair or exact seed/verify, SQL/JWT/API and both UI
views. Observed: only timestamp differed, CAS1 and SQL/HTTP passed; one UI
context failed before login/query. Afterward runtime resources were stopped/
absent; cause and exact UI exception unknown. Independent cleanup retained
volume and no other app data changed. Update claim to partial acceptance;
never infer successful UI from source tests, prior manual UI or HTTP success.

## Resolved post-proof source integration finding / dual source attribution

Existing domain-boundary/shim check initially found1failed39passed before any
commit: the comparator's direct User importer violated exact frozen E2 rules.
The bounded repair injects the identical canonical class: native ledger.models.User,
parent inventory the existing repository.User. Wrong classes refuse. Clean-child
proof establishes canonical identity with no config/ledger_factory/.env load;
no E2 allowlist, shared model, global ledger or normal config was changed.
Worker combined104PASS26.83s; independent102PASS26.53s; invariant/size passed.
POST_PROOF_REPAIR_REVIEW_PASS_PARTIAL_EVIDENCE_ONLY accepts final source.

The old ten physical execution hashes remain immutable under
AD/EVIDENCE.physicalExecutionSourceCheckpoint. Current final source hashes are
AD/EVIDENCE.sourceCheckpoint/source; exactly five differ for the injection and
caller/test wiring. Actual SQL/CAS/JWT/HTTP/UI/custody observations belong to
the OLD execution hashes. Final repaired source has inert regression evidence
only; no physical replay is claimed or authorized. The earlier frozen-through-
proof statement describes that historical execution, not the later repair.
All13transaction/refusal/race/rollback cases and boundary tests stayed intact.
The inside-authority finding is resolved; only normal full material/continuity
gates remain, never actualUI/milestone acceptance or a new runtime budget.

## Return-Time Closeability Recheck

closeabilityDisposition: CLOSEABLE
outsideAuthorityBlockers: NONE
nextRepairRoute: NONE
workerRedispatchAllowed: NO

This packet is closeable for accepted source/SQL/HTTP and truthful failed-UI
evidence, normal material/continuity only. Missing UI acceptance and any fresh
runtime/browser budget are an explicit future operator checkpoint, not hidden
current repair authority. Invoke verified pinned Core check_recheck explicitly
for this standalone legacy worker-return marker; CLI/hook does not auto-scan
this legacy docs/decisions family. No further worker/runtime redispatch.
