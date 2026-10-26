# P5-A2 synthetic backend consolidated source and retained-volume recovery

docType: work_order
Status: DISPATCH_READY
Date: 2026-10-27
Baseline: `08c62dad7b956faf7e1d1dd6cb56ee79e10cbead`
Risk: R2
Phase: WORK_ORDER reviewed-dispatch candidate; independent authorization and committed dispatch/continuity remain prerequisites.
Role transition: SPEC_AUTHOR → WORK_ORDER_AUTHOR for this candidate.
Root is ORCHESTRATOR, effect/artifact owner and COMMIT_STEWARD. A later named
backend IMPLEMENTATION_WORKER changes source only after gates. An independent
REVIEWER owns authorization, actual-source checkpoint and result review.

## Product Milestone Binding

Milestone P5-A2, Phase 5 of `docs/implementation/EXECUTION_ROADMAP.md`, is
reconciled at `08c62da` plus the current 2026-10-27 recovery intake/design
acknowledgment in the active Stage B handoff. The full user outcome is an
authorized integrated scheduled flow for signals, forecasts, source history,
lineage, freshness, uncertainty and abstention, with exact human
run/version/source approval before durable recommendation or action.
Acceptance requires operational source authority/retention, scheduler and
recovery, method/cohort fit, signal/forecast/drift quality, application
access, exact approval, integrated drills and applicable real-provider
governance proof; operator and independent reviewer own final milestone
acceptance. The canonical business contract is
`docs/specs/P5A2_PROACTIVE_REPORTING_SPEC.md`; the current complete gap
reconciliation is in `docs/specs/P5A2_SYNTHETIC_BACKEND_RECOVERY_SPEC.md`
and is repeated here for dispatch review. Mock UI checks cannot support a
CVF AI-governance claim.

Accepted bounded source/substrate/UI evidence is named in the baseline
`docs/specs/P5A2_SYNTHETIC_BACKEND_SPEC.md` and prior Stage B Work Order.
The Stage B failure return and independent review establish one spent start,
only a retained labeled volume, no API/web/smoke/UI, and a confirmed
standalone import blocker; failed-result material `555119e` and continuity
`08c62da` closed clean 15+5. Database contents and migration progress remain
UNKNOWN. This assignment closes only the known local synthetic G04/G05
physical proof route; no whole gap or milestone closes. Phase 5 remains 0/5.

| Gap | Current evidence and status | This assignment | Owner and concrete remainder destination |
|---|---|---|---|
| G01/A7 | Real provider 401 spent; BLOCKED | No | Root/operator, P5-A A7 then P5-A2 |
| G02 | Operational RAG/context/index/citations BLOCKED | No | Backend/Root, P5-A2 context |
| G03 | Pure numeric accepted; business/cohort fit UNKNOWN | No | Backend/operator, P5-A2 method |
| G04 | Scoped fixture/PG query/API accepted; standing synthetic backend failed; operational integration UNKNOWN | Synthetic recovery only | Backend/Root, P5-A2 source |
| G05 | Fixture coverage accepted; production mode/authority/coverage/retention and positive SQLite UNKNOWN | Exact synthetic authority only | Backend/Root/operator, P5-A2 coverage |
| G06 | Native/HTTP identity/fresh release accepted; later use-time access OPEN | No | Backend/Root, P5-A2 approval |
| G07 | Scheduler/claim/recovery OPEN | No | Backend/Root, P5-A2 runtime |
| G08 | Pure signals accepted; operational quality OPEN | No | Backend/operator, P5-A2 signals |
| G09 | Pure forecasts accepted; operational accuracy OPEN | No | Backend/operator, P5-A2 forecasting |
| G10 | Pure residual/drift accepted; monitoring/display OPEN | No | Backend/UI/Root, P5-A2 quality and P5-B |
| G11 | Source API/manual UI accepted; other flows OPEN | Existing source panel only | UI/Root/operator, P5-A2 application |
| G12 | Exact human approval OPEN | No | Backend/UI/operator, P5-A2 approval |
| G13 | Native failure/stale/session drills accepted; integrated drills OPEN | No | Backend/Root, P5-A2 drills and P5-C |
| G14 | Live AI-governance proof HELD | No | Root/operator, separately admitted P5-A2 REVIEW |

P5-B dashboard/search/observability stays with backend/UI/Root; P5-C
backup/resilience/security/performance stays with backend/Root/operator;
P5-D deployment/Shadow Mode/release stays with Root/operator. UNKNOWN is
neither omitted nor treated as accepted. The finite product return is one
physical synthetic SQL/JWT/API/UI proof or one safe refusal, then P5-A2
integrated runtime/context/quality/approval work. This support path is
necessary because the selected local source demonstration cannot run from
the standalone launcher and its volume must be preserved.

## Allowed source, artifacts and owners

The worker's bounded implementation family is exact existing
`scripts/p5a2_source_demo_start.py` (import roots only), new
`scripts/p5a2_source_demo_bootstrap.py`, new
`scripts/p5a2_source_demo_recover.py`, and only necessary bounded
`scripts/p5a2_source_demo_recovery_*.py` splits under the 300-line guard.
Focused tests may be new `tests/unit/test_p5a2_demo_bootstrap.py`,
`tests/unit/test_p5a2_demo_recovery_*.py` and the existing
`tests/unit/test_p5a2_demo_lifecycle.py` only if needed for the existing
adapter. The worker cannot edit normal API/UI, fixtures, oracles, migrations,
`scripts/p5a2_source_demo_common.py`, stop, smoke, compose, existing family
matrix/registry or accepted source logic. An unforeseen source path requires
Root's consolidated reviewed amendment before mutation.

Root owns the exact new decision family:
`docs/decisions/P5A2_SYNTHETIC_BACKEND_RECOVERY_ADMISSION_2026-10-27.json`,
`..._ATTEMPT_2026-10-27.json`, `..._EVIDENCE_2026-10-27.json`, and
`..._RETURN_2026-10-27.md`; the independent reviewer owns
`docs/decisions/P5A2_SYNTHETIC_BACKEND_RECOVERY_REVIEW_2026-10-27.md`.
The optional successful browser screenshots are exactly
`docs/reviews/evidence/p5a2-source-demo-recovery-initial-20261027.png` and
`docs/reviews/evidence/p5a2-source-demo-recovery-later-20261027.png`.
Root's metadata/continuity/catalog/knowledge path family is the same exact
family listed in the Stage B admission, with this SPEC and Work Order added.
Before READY, Root seals its full actual path manifest, all current hashes,
roles and budgets in the new admission; the shorthand above is not an
unbounded path authorization. The existing active Stage B handoff and exact
five session/mirror paths are the dispatch and terminal continuity carriers.

## One integrated BUILD and physical stop rules

1. Root obtains independent SPEC/authorization review, runs the ordinary
   pre-dispatch gates, commits the normal dispatch, records its actual SHA in
   the active handoff through a dedicated exact-five continuity commit, then
   obtains independent clean split-range review. Only then does BUILD start.
2. Worker changes only the bounded source/tests and runs clean standalone
   child seed import and full demo app composition probes under the actual
   child environment, plus focused source/refusal/lifecycle tests. The probes
   make no DB, listener, browser, provider, install or network call. Pytest
   alone is insufficient. Root and independent reviewer then check and pin
   the ACTUAL changed source hashes/lines, the remaining 22 frozen Stage A
   source pins, all frozen fixtures/oracles/migrations, and both invariant
   family digests. The reviewer records SOURCE_CHECKPOINT_PASS or refusal.
   Changed source may still be uncommitted in this same BUILD, but is frozen
   byte-for-byte after checkpoint through physical result. Any later source
   change invalidates admission and stops the effect budget.
3. After checkpoint and a fresh pinned-Core preflight, Root verifies the
   registered partial owner/volume-only state, exact nonce/labels, cached
   image, mount target, local generated credential reference and custody,
   absent container/API/web, and free fixed loopback ports 5433/8001/5174.
   Every Docker command uses the exact local CLI
   `C:/Users/DELL/AppData/Local/Programs/DockerDesktop/resources/bin/docker.exe`
   with `--host npipe:////./pipe/dockerDesktopLinuxEngine`, never ambient or
   remote Docker routing. The only image ID is the admitted cached pin; no
   tag operation or pull occurs.
   This is not the existing fresh-profile preflight. Refuse on ambiguity.
   Root writes exactly one exclusive immutable recovery reservation before
   any new container effect. The prior Stage B START reservation remains
   spent and untouched.
4. Root invokes the new recovery tool at most once. It reuses the same volume,
   nonce and local generated credentials, with no new volume/secret and no
   pull. At most one exact owned PostgreSQL container is created. Revalidate
   image, labels and mounted volume. Before seed writes, collect a
   single-connection repeatable-read read-only inventory of database name, PostgreSQL 16
   identity/system identifier, source-compatible schema including expected
   migration tables and native required columns, and counts for ALL tables.
   Continue only with all rows empty, or exact target counts in four tables
   and zero other rows. No migration replay, DDL, reset or delete is allowed.
   Native seed once or exact verification must reject partial/foreign data
   and mismatched record/body hashes. Repeat identity and counts afterward.
5. Only after SQL acceptance, start at most one API and one web child.
   Run one native smoke: real JWT login, two frozen HTTP source contexts with
   receipt digests `5523c755204ea4ee3e960394306c61d32d75d926806276748f99be481f6b0e64`
   and `874e8e5693e1efeea30f92ab26ef48dacb00f0b0efa109f977fd3e8beba6f554`.
   Verify SQL users=1/shifts=36/shift_assignments=36/reports=37. One
   isolated browser context may submit each accepted UTC query once and save
   two screenshots: visible synthetic label, 36/36/36 then 36/36/37.
6. On any failure, retain old evidence, owner trail, volume and credentials.
   Stop only newly created exact owned children/container after fresh identity
   verification, record the new trail and remaining resource counts, then
   stop this tranche's physical work. Success retains one owned container,
   existing volume, API and web process. A future stop needs a separate
   reviewed decision retaining the volume. No automatic retry.

Total NEW recovery budget: one read-only preflight, one exclusive reservation,
one recovery call,
one container over the existing volume, zero new volumes, zero new secrets,
zero migrations, at most one native seed or exact verification, one API and
one web child, one smoke, one read-only inventory connection and one read-only
SQL summary, two smoke HTTP contexts and two UI submits, one smoke JWT login
and one browser login, one browser context/two screenshots. Bounded readiness
probes have maxima 40 each for DB, API and web, with no second startup.
Provider calls, package installs,
pulls, external/public network effects, `.env` reads, operator secrets,
volume delete/reset, deployment and push are zero. This sealed candidate releases
none of this budget. No prior spent effect count is reset.

## Evidence and claim boundary

The new admission records exact source/baseline/frozen hashes, owner/effect
boundaries and reservation protocol. Attempt and evidence record resource
IDs, label/nonce match, image and mount identity, secret-reference presence
without value, prewrite schema/count verdict and fingerprint, postwrite
counts, physical SQL/JWT/HTTP/UI results, canonical body and screenshot
digests, cleanup trail and actual remaining resources. No passwords, DSN,
JWT, bearer token, report bodies or local secret bytes enter Git, logs or
review. Retain the prior failure receipt and any new refusal as observed.
The result review reconciles all G01-G14, actual source manifest, tests,
effect counts and claim limits. A successful local synthetic profile proves
only this exact authority and two query contexts, never operational coverage,
retention, business fit, forecasting quality, scheduler, approval, provider
governance, production or milestone readiness.

Reference `docs/cvf/INVARIANT_FAMILY_STANDARD.md` and registered
P5A2-SOURCE-DEMO-RESOURCE-LIFECYCLE digest
`f323ef1062e791c1c8fa4bff880b765a79547b571b0cfca9083286d680dcef2c`.
The source family digest remains
`6fec188950fe752ac438e2952ec3d4e2ffd3b4156efa0b9a2e06e1048c568754`.
Reuse the existing adapter, do not copy matrix rules or
create a second grammar. If a family surface changes, run
`python scripts/check_invariant_families.py` before REVIEW/FREEZE.
Legacy `docs/decisions/` return and completion review must carry exact
standalone self-declared markers and Return-Time Closeability Rechecks;
reviewer invokes pinned Core `check_recheck` explicitly and records result.
The normal CLI/hook does not automatically scan that legacy family.

## Gate-To-Role Closeability Contract

closeabilityContractVersion: cvf.gate-role-closeability@1.0.0
closeabilityDisposition: CLOSEABLE
returnTimeRecheck: REQUIRED_BEFORE_REPAIR
implementationTopologyPolicy: BOUNDED_PATH_FAMILIES
foreseeableFileSplitDisposition: COVERED_BY_BOUNDED_PATH_FAMILY

In the graph, `SOURCE` means only the exact worker source/test family above,
including bounded recovery helper/test splits; `ROOT_RECORDS` means the
exact Root-owned recovery decision and metadata families sealed in admission;
`REVIEW` is the exact independent recovery review; and `FIVE` is the current
active handoff plus four session/mirror paths. Root expands all abbreviations
into a sealed manifest before READY. No protected or authority-bearing path
is authorized by an abbreviation. The current sealed candidate awaits
independent authorization; no BUILD or physical budget is released.

| gateId | mustPassBy | repairOwner | repairPhase | mutationSurface | topology | commitOwner | commitPhase | dependsOn |
|---|---|---|---|---|---|---|---|---|
| authorization_review | PRE_DISPATCH | work-order-author | PRE_DISPATCH | docs/work_orders/P5A2_SYNTHETIC_BACKEND_RECOVERY_WORK_ORDER.md;docs/specs/P5A2_SYNTHETIC_BACKEND_RECOVERY_SPEC.md | EXACT_PATHS | commit-steward | DISPATCH_COMMIT | NONE |
| pre_dispatch_gate | PRE_DISPATCH | orchestrator | PRE_DISPATCH | CVF_SESSION/ACTIVE_SESSION_STATE.json;IMPLEMENTATION_STATUS.json;SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json;SESSION/ACTIVE_SESSION_STATE.json;SESSION/SESSION_MEMORY.md;SESSION/handoffs/AGENT_HANDOFF_P5A2_SYNTHETIC_BACKEND_STAGE_B_2026-10-26.md;docs/INDEX.md;docs/PROJECT_INDEX.md;docs/catalog/ARTIFACT_REGISTRY.json;docs/catalog/MODULE_CATALOG.md;docs/catalog/MODULE_CATALOG_DETAIL.md;docs/catalog/MODULE_REGISTRY.json;docs/catalog/MODULE_REGISTRY_DETAIL.json;docs/decisions/P5A2_SYNTHETIC_BACKEND_RECOVERY_ADMISSION_2026-10-27.json;docs/decisions/P5A2_SYNTHETIC_BACKEND_RECOVERY_ATTEMPT_2026-10-27.json;docs/decisions/P5A2_SYNTHETIC_BACKEND_RECOVERY_EVIDENCE_2026-10-27.json;docs/decisions/P5A2_SYNTHETIC_BACKEND_RECOVERY_RETURN_2026-10-27.md;docs/implementation/EXECUTION_ROADMAP.md;docs/reviews/evidence/p5a2-source-demo-recovery-initial-20261027.png;docs/reviews/evidence/p5a2-source-demo-recovery-later-20261027.png;docs/specs/P5A2_SYNTHETIC_BACKEND_RECOVERY_SPEC.md;docs/work_orders/P5A2_SYNTHETIC_BACKEND_RECOVERY_WORK_ORDER.md;knowledge/PROJECT_CONTEXT.md;knowledge/manifest.json;docs/work_orders/P5A2_SYNTHETIC_BACKEND_RECOVERY_WORK_ORDER.md;docs/specs/P5A2_SYNTHETIC_BACKEND_RECOVERY_SPEC.md;SESSION/handoffs/AGENT_HANDOFF_P5A2_SYNTHETIC_BACKEND_STAGE_B_2026-10-26.md;SESSION/ACTIVE_SESSION_STATE.json;SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json;SESSION/SESSION_MEMORY.md;CVF_SESSION/ACTIVE_SESSION_STATE.json | BOUNDED_PATH_FAMILY | commit-steward | DISPATCH_COMMIT | authorization_review |
| dispatch_continuity | IMPLEMENTATION | session-sync-steward | IMPLEMENTATION | SESSION/handoffs/AGENT_HANDOFF_P5A2_SYNTHETIC_BACKEND_STAGE_B_2026-10-26.md material-SHA marker;SESSION/ACTIVE_SESSION_STATE.json;SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json;SESSION/SESSION_MEMORY.md;CVF_SESSION/ACTIVE_SESSION_STATE.json | EXACT_PATHS | session-sync-steward | DISPATCH_CONTINUITY_COMMIT | pre_dispatch_gate |
| pre_implementation_autorun | IMPLEMENTATION | orchestrator | IMPLEMENTATION | CVF_SESSION/ACTIVE_SESSION_STATE.json;IMPLEMENTATION_STATUS.json;SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json;SESSION/ACTIVE_SESSION_STATE.json;SESSION/SESSION_MEMORY.md;SESSION/handoffs/AGENT_HANDOFF_P5A2_SYNTHETIC_BACKEND_STAGE_B_2026-10-26.md;docs/INDEX.md;docs/PROJECT_INDEX.md;docs/catalog/ARTIFACT_REGISTRY.json;docs/catalog/MODULE_CATALOG.md;docs/catalog/MODULE_CATALOG_DETAIL.md;docs/catalog/MODULE_REGISTRY.json;docs/catalog/MODULE_REGISTRY_DETAIL.json;docs/decisions/P5A2_SYNTHETIC_BACKEND_RECOVERY_ADMISSION_2026-10-27.json;docs/decisions/P5A2_SYNTHETIC_BACKEND_RECOVERY_ATTEMPT_2026-10-27.json;docs/decisions/P5A2_SYNTHETIC_BACKEND_RECOVERY_EVIDENCE_2026-10-27.json;docs/decisions/P5A2_SYNTHETIC_BACKEND_RECOVERY_RETURN_2026-10-27.md;docs/implementation/EXECUTION_ROADMAP.md;docs/reviews/evidence/p5a2-source-demo-recovery-initial-20261027.png;docs/reviews/evidence/p5a2-source-demo-recovery-later-20261027.png;docs/specs/P5A2_SYNTHETIC_BACKEND_RECOVERY_SPEC.md;docs/work_orders/P5A2_SYNTHETIC_BACKEND_RECOVERY_WORK_ORDER.md;knowledge/PROJECT_CONTEXT.md;knowledge/manifest.json;SESSION/handoffs/AGENT_HANDOFF_P5A2_SYNTHETIC_BACKEND_STAGE_B_2026-10-26.md;SESSION/ACTIVE_SESSION_STATE.json;SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json;SESSION/SESSION_MEMORY.md;CVF_SESSION/ACTIVE_SESSION_STATE.json | BOUNDED_PATH_FAMILY | commit-steward | MATERIAL_COMMIT | dispatch_continuity |
| source_build | IMPLEMENTATION | implementation-worker | IMPLEMENTATION | scripts/p5a2_source_demo_start.py;scripts/p5a2_source_demo_bootstrap.py;scripts/p5a2_source_demo_recover.py;scripts/p5a2_source_demo_recovery_*.py;tests/unit/test_p5a2_demo_recovery_*.py;tests/unit/test_p5a2_demo_bootstrap.py;tests/unit/test_p5a2_demo_lifecycle.py | BOUNDED_PATH_FAMILY | commit-steward | MATERIAL_COMMIT | dispatch_continuity,pre_implementation_autorun |
| focused_checker_tests | WORKER_RETURN | implementation-worker | IMPLEMENTATION | scripts/p5a2_source_demo_start.py;scripts/p5a2_source_demo_bootstrap.py;scripts/p5a2_source_demo_recover.py;scripts/p5a2_source_demo_recovery_*.py;tests/unit/test_p5a2_demo_recovery_*.py;tests/unit/test_p5a2_demo_bootstrap.py;tests/unit/test_p5a2_demo_lifecycle.py;CVF_SESSION/ACTIVE_SESSION_STATE.json;IMPLEMENTATION_STATUS.json;SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json;SESSION/ACTIVE_SESSION_STATE.json;SESSION/SESSION_MEMORY.md;SESSION/handoffs/AGENT_HANDOFF_P5A2_SYNTHETIC_BACKEND_STAGE_B_2026-10-26.md;docs/INDEX.md;docs/PROJECT_INDEX.md;docs/catalog/ARTIFACT_REGISTRY.json;docs/catalog/MODULE_CATALOG.md;docs/catalog/MODULE_CATALOG_DETAIL.md;docs/catalog/MODULE_REGISTRY.json;docs/catalog/MODULE_REGISTRY_DETAIL.json;docs/decisions/P5A2_SYNTHETIC_BACKEND_RECOVERY_ADMISSION_2026-10-27.json;docs/decisions/P5A2_SYNTHETIC_BACKEND_RECOVERY_ATTEMPT_2026-10-27.json;docs/decisions/P5A2_SYNTHETIC_BACKEND_RECOVERY_EVIDENCE_2026-10-27.json;docs/decisions/P5A2_SYNTHETIC_BACKEND_RECOVERY_RETURN_2026-10-27.md;docs/implementation/EXECUTION_ROADMAP.md;docs/reviews/evidence/p5a2-source-demo-recovery-initial-20261027.png;docs/reviews/evidence/p5a2-source-demo-recovery-later-20261027.png;docs/specs/P5A2_SYNTHETIC_BACKEND_RECOVERY_SPEC.md;docs/work_orders/P5A2_SYNTHETIC_BACKEND_RECOVERY_WORK_ORDER.md;knowledge/PROJECT_CONTEXT.md;knowledge/manifest.json | BOUNDED_PATH_FAMILY | commit-steward | MATERIAL_COMMIT | dispatch_continuity,source_build |
| source_checkpoint | IMPLEMENTATION | reviewer | IMPLEMENTATION | CVF_SESSION/ACTIVE_SESSION_STATE.json;IMPLEMENTATION_STATUS.json;SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json;SESSION/ACTIVE_SESSION_STATE.json;SESSION/SESSION_MEMORY.md;SESSION/handoffs/AGENT_HANDOFF_P5A2_SYNTHETIC_BACKEND_STAGE_B_2026-10-26.md;docs/INDEX.md;docs/PROJECT_INDEX.md;docs/catalog/ARTIFACT_REGISTRY.json;docs/catalog/MODULE_CATALOG.md;docs/catalog/MODULE_CATALOG_DETAIL.md;docs/catalog/MODULE_REGISTRY.json;docs/catalog/MODULE_REGISTRY_DETAIL.json;docs/decisions/P5A2_SYNTHETIC_BACKEND_RECOVERY_ADMISSION_2026-10-27.json;docs/decisions/P5A2_SYNTHETIC_BACKEND_RECOVERY_ATTEMPT_2026-10-27.json;docs/decisions/P5A2_SYNTHETIC_BACKEND_RECOVERY_EVIDENCE_2026-10-27.json;docs/decisions/P5A2_SYNTHETIC_BACKEND_RECOVERY_RETURN_2026-10-27.md;docs/implementation/EXECUTION_ROADMAP.md;docs/reviews/evidence/p5a2-source-demo-recovery-initial-20261027.png;docs/reviews/evidence/p5a2-source-demo-recovery-later-20261027.png;docs/specs/P5A2_SYNTHETIC_BACKEND_RECOVERY_SPEC.md;docs/work_orders/P5A2_SYNTHETIC_BACKEND_RECOVERY_WORK_ORDER.md;knowledge/PROJECT_CONTEXT.md;knowledge/manifest.json;docs/decisions/P5A2_SYNTHETIC_BACKEND_RECOVERY_REVIEW_2026-10-27.md | BOUNDED_PATH_FAMILY | commit-steward | MATERIAL_COMMIT | focused_checker_tests |
| read_only_preflight | IMPLEMENTATION | orchestrator | IMPLEMENTATION | CVF_SESSION/ACTIVE_SESSION_STATE.json;IMPLEMENTATION_STATUS.json;SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json;SESSION/ACTIVE_SESSION_STATE.json;SESSION/SESSION_MEMORY.md;SESSION/handoffs/AGENT_HANDOFF_P5A2_SYNTHETIC_BACKEND_STAGE_B_2026-10-26.md;docs/INDEX.md;docs/PROJECT_INDEX.md;docs/catalog/ARTIFACT_REGISTRY.json;docs/catalog/MODULE_CATALOG.md;docs/catalog/MODULE_CATALOG_DETAIL.md;docs/catalog/MODULE_REGISTRY.json;docs/catalog/MODULE_REGISTRY_DETAIL.json;docs/decisions/P5A2_SYNTHETIC_BACKEND_RECOVERY_ADMISSION_2026-10-27.json;docs/decisions/P5A2_SYNTHETIC_BACKEND_RECOVERY_ATTEMPT_2026-10-27.json;docs/decisions/P5A2_SYNTHETIC_BACKEND_RECOVERY_EVIDENCE_2026-10-27.json;docs/decisions/P5A2_SYNTHETIC_BACKEND_RECOVERY_RETURN_2026-10-27.md;docs/implementation/EXECUTION_ROADMAP.md;docs/reviews/evidence/p5a2-source-demo-recovery-initial-20261027.png;docs/reviews/evidence/p5a2-source-demo-recovery-later-20261027.png;docs/specs/P5A2_SYNTHETIC_BACKEND_RECOVERY_SPEC.md;docs/work_orders/P5A2_SYNTHETIC_BACKEND_RECOVERY_WORK_ORDER.md;knowledge/PROJECT_CONTEXT.md;knowledge/manifest.json | BOUNDED_PATH_FAMILY | commit-steward | MATERIAL_COMMIT | source_checkpoint |
| effect_reservation | IMPLEMENTATION | orchestrator | IMPLEMENTATION | docs/decisions/P5A2_SYNTHETIC_BACKEND_RECOVERY_ATTEMPT_2026-10-27.json | EXACT_PATHS | commit-steward | MATERIAL_COMMIT | read_only_preflight |
| physical_start | IMPLEMENTATION | orchestrator | IMPLEMENTATION | CVF_SESSION/ACTIVE_SESSION_STATE.json;IMPLEMENTATION_STATUS.json;SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json;SESSION/ACTIVE_SESSION_STATE.json;SESSION/SESSION_MEMORY.md;SESSION/handoffs/AGENT_HANDOFF_P5A2_SYNTHETIC_BACKEND_STAGE_B_2026-10-26.md;docs/INDEX.md;docs/PROJECT_INDEX.md;docs/catalog/ARTIFACT_REGISTRY.json;docs/catalog/MODULE_CATALOG.md;docs/catalog/MODULE_CATALOG_DETAIL.md;docs/catalog/MODULE_REGISTRY.json;docs/catalog/MODULE_REGISTRY_DETAIL.json;docs/decisions/P5A2_SYNTHETIC_BACKEND_RECOVERY_ADMISSION_2026-10-27.json;docs/decisions/P5A2_SYNTHETIC_BACKEND_RECOVERY_ATTEMPT_2026-10-27.json;docs/decisions/P5A2_SYNTHETIC_BACKEND_RECOVERY_EVIDENCE_2026-10-27.json;docs/decisions/P5A2_SYNTHETIC_BACKEND_RECOVERY_RETURN_2026-10-27.md;docs/implementation/EXECUTION_ROADMAP.md;docs/reviews/evidence/p5a2-source-demo-recovery-initial-20261027.png;docs/reviews/evidence/p5a2-source-demo-recovery-later-20261027.png;docs/specs/P5A2_SYNTHETIC_BACKEND_RECOVERY_SPEC.md;docs/work_orders/P5A2_SYNTHETIC_BACKEND_RECOVERY_WORK_ORDER.md;knowledge/PROJECT_CONTEXT.md;knowledge/manifest.json;C:/Users/DELL/AppData/Local/shiftops-p5a2-source-demo;shiftops-p5a2-source-demo-db-v1;shiftops-p5a2-source-demo-data-v1;owned-api-pid;owned-web-pid | BOUNDED_PATH_FAMILY | commit-steward | MATERIAL_COMMIT | effect_reservation |
| physical_result | WORKER_RETURN | orchestrator | IMPLEMENTATION | CVF_SESSION/ACTIVE_SESSION_STATE.json;IMPLEMENTATION_STATUS.json;SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json;SESSION/ACTIVE_SESSION_STATE.json;SESSION/SESSION_MEMORY.md;SESSION/handoffs/AGENT_HANDOFF_P5A2_SYNTHETIC_BACKEND_STAGE_B_2026-10-26.md;docs/INDEX.md;docs/PROJECT_INDEX.md;docs/catalog/ARTIFACT_REGISTRY.json;docs/catalog/MODULE_CATALOG.md;docs/catalog/MODULE_CATALOG_DETAIL.md;docs/catalog/MODULE_REGISTRY.json;docs/catalog/MODULE_REGISTRY_DETAIL.json;docs/decisions/P5A2_SYNTHETIC_BACKEND_RECOVERY_ADMISSION_2026-10-27.json;docs/decisions/P5A2_SYNTHETIC_BACKEND_RECOVERY_ATTEMPT_2026-10-27.json;docs/decisions/P5A2_SYNTHETIC_BACKEND_RECOVERY_EVIDENCE_2026-10-27.json;docs/decisions/P5A2_SYNTHETIC_BACKEND_RECOVERY_RETURN_2026-10-27.md;docs/implementation/EXECUTION_ROADMAP.md;docs/reviews/evidence/p5a2-source-demo-recovery-initial-20261027.png;docs/reviews/evidence/p5a2-source-demo-recovery-later-20261027.png;docs/specs/P5A2_SYNTHETIC_BACKEND_RECOVERY_SPEC.md;docs/work_orders/P5A2_SYNTHETIC_BACKEND_RECOVERY_WORK_ORDER.md;knowledge/PROJECT_CONTEXT.md;knowledge/manifest.json;docs/reviews/evidence/p5a2-source-demo-recovery-initial-20261027.png;docs/reviews/evidence/p5a2-source-demo-recovery-later-20261027.png | BOUNDED_PATH_FAMILY | commit-steward | MATERIAL_COMMIT | physical_start |
| adif_integrity | WORKER_RETURN | orchestrator | WORKER_RETURN | docs/decisions/P5A2_SYNTHETIC_BACKEND_RECOVERY_RETURN_2026-10-27.md | EXACT_PATHS | commit-steward | MATERIAL_COMMIT | focused_checker_tests,physical_result |
| worker_return_fast | WORKER_RETURN | orchestrator | WORKER_RETURN | docs/decisions/P5A2_SYNTHETIC_BACKEND_RECOVERY_RETURN_2026-10-27.md | EXACT_PATHS | commit-steward | MATERIAL_COMMIT | adif_integrity |
| reviewer_fast | REVIEW | reviewer | REVIEW | docs/decisions/P5A2_SYNTHETIC_BACKEND_RECOVERY_REVIEW_2026-10-27.md | EXACT_PATHS | commit-steward | MATERIAL_COMMIT | worker_return_fast |
| pre_commit | PRE_MATERIAL_COMMIT | repair-worker | PRE_MATERIAL_COMMIT | scripts/p5a2_source_demo_start.py;scripts/p5a2_source_demo_bootstrap.py;scripts/p5a2_source_demo_recover.py;scripts/p5a2_source_demo_recovery_*.py;tests/unit/test_p5a2_demo_recovery_*.py;tests/unit/test_p5a2_demo_bootstrap.py;tests/unit/test_p5a2_demo_lifecycle.py;CVF_SESSION/ACTIVE_SESSION_STATE.json;IMPLEMENTATION_STATUS.json;SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json;SESSION/ACTIVE_SESSION_STATE.json;SESSION/SESSION_MEMORY.md;SESSION/handoffs/AGENT_HANDOFF_P5A2_SYNTHETIC_BACKEND_STAGE_B_2026-10-26.md;docs/INDEX.md;docs/PROJECT_INDEX.md;docs/catalog/ARTIFACT_REGISTRY.json;docs/catalog/MODULE_CATALOG.md;docs/catalog/MODULE_CATALOG_DETAIL.md;docs/catalog/MODULE_REGISTRY.json;docs/catalog/MODULE_REGISTRY_DETAIL.json;docs/decisions/P5A2_SYNTHETIC_BACKEND_RECOVERY_ADMISSION_2026-10-27.json;docs/decisions/P5A2_SYNTHETIC_BACKEND_RECOVERY_ATTEMPT_2026-10-27.json;docs/decisions/P5A2_SYNTHETIC_BACKEND_RECOVERY_EVIDENCE_2026-10-27.json;docs/decisions/P5A2_SYNTHETIC_BACKEND_RECOVERY_RETURN_2026-10-27.md;docs/implementation/EXECUTION_ROADMAP.md;docs/reviews/evidence/p5a2-source-demo-recovery-initial-20261027.png;docs/reviews/evidence/p5a2-source-demo-recovery-later-20261027.png;docs/specs/P5A2_SYNTHETIC_BACKEND_RECOVERY_SPEC.md;docs/work_orders/P5A2_SYNTHETIC_BACKEND_RECOVERY_WORK_ORDER.md;knowledge/PROJECT_CONTEXT.md;knowledge/manifest.json;docs/decisions/P5A2_SYNTHETIC_BACKEND_RECOVERY_REVIEW_2026-10-27.md;SESSION/handoffs/AGENT_HANDOFF_P5A2_SYNTHETIC_BACKEND_STAGE_B_2026-10-26.md;SESSION/ACTIVE_SESSION_STATE.json;SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json;SESSION/SESSION_MEMORY.md;CVF_SESSION/ACTIVE_SESSION_STATE.json | BOUNDED_PATH_FAMILY | commit-steward | MATERIAL_COMMIT | reviewer_fast |
| terminal_completion_review | POST_MATERIAL | reviewer | POST_MATERIAL | docs/decisions/P5A2_SYNTHETIC_BACKEND_RECOVERY_REVIEW_2026-10-27.md | EXACT_PATHS | commit-steward | CORRECTIVE_MATERIAL_COMMIT | pre_commit |
| continuity | CONTINUITY_COMMIT | session-sync-steward | CONTINUITY_COMMIT | SESSION/handoffs/AGENT_HANDOFF_P5A2_SYNTHETIC_BACKEND_STAGE_B_2026-10-26.md;SESSION/ACTIVE_SESSION_STATE.json;SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json;SESSION/SESSION_MEMORY.md;CVF_SESSION/ACTIVE_SESSION_STATE.json | EXACT_PATHS | session-sync-steward | CONTINUITY_COMMIT | terminal_completion_review |
| committed_range_closure | POST_MATERIAL_CLOSURE | reviewer | POST_MATERIAL_CLOSURE | SESSION/handoffs/AGENT_HANDOFF_P5A2_SYNTHETIC_BACKEND_STAGE_B_2026-10-26.md;docs/decisions/P5A2_SYNTHETIC_BACKEND_RECOVERY_REVIEW_2026-10-27.md | EXACT_PATHS | session-sync-steward | CONTINUITY_COMMIT | continuity |

Root expanded every graph path group from the exact admission and verifies
active graph closeability before independent authorization. The candidate
remains held until the independent authorization and normal dispatch gates pass. Any material
objective, acceptance, risk, path, secret, network, effect, budget or commit
owner change requires a reviewed consolidated amendment before execution.
