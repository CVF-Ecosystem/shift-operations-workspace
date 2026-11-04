# PR #5 CI repair — 2026-11-05

docType: work_order
Status: DISPATCH_READY
Risk: R2

## INTAKE / DESIGN / SPEC

Operator authorized fixing both failing PR checks and merging PR #5. The
observed `validate` job stops at editable package metadata: setuptools sees
multiple unrelated top-level directories. The `catalog-kit` job compares
LF-checked-out generated views with CRLF strings rendered by the project kit.
The local CRLF checkout masks that drift. The intended behavior is a metadata
only editable install for this monorepo and generated catalog bytes matching
the repository's `.gitattributes` LF policy on every host. This packet grants
no product runtime, database, browser, provider, deployment or Core mutation.

### Repair amendment 1 — hosted Ubuntu projection

After commit `9f93aa4`, hosted `catalog-kit` and `web` passed. Hosted
`validate` passed editable install and detailed catalog check but failed at
`python scripts/sync_cvf_catalog_kit.py`. The projection's fallback source
selection sorts `Path` objects; Windows compares case insensitively while
Linux compares case sensitively. Four stub modules therefore select a nested
README on Windows and the root README on Linux. The committed registry is
Windows-derived. This amendment adds only
`scripts/sync_cvf_catalog_kit.py` to the allowed implementation paths, to
sort normalized relative path strings case insensitively with a deterministic
tie break. Preserve the registry's existing evidence values and statuses.
Stop if hosted rerun exposes a further root cause. Independent authorization
re-review is required before this repair round's BUILD.

### Repair amendment 2 — clean hosted test environment

The operator explicitly authorized expanding the CI work to install the
declared public Core and other public test dependencies on a clean runner,
repair test portability and merge only when all checks pass. Run
`41903721108` passed install, both catalog checks, repository validation,
`catalog-kit` and `web`; the full pytest step reported 20 failures and
8 setup errors. Consolidated causes: Ubuntu lacks the pinned sibling Core,
workspace root rules, Windows `powershell`, local `.venv/Scripts/python.exe`
and application node_modules; it also lacks the skill creator validator.
Four knowledge source pins were generated from CRLF local bytes while the
repository enforces LF on clean checkout. These are CI environment and
artifact-byte failures, not product behavior failures.

Authorized implementation paths now additionally include
`.github/workflows/ci.yml` and `knowledge/manifest.json`, plus necessary
project-owned continuity/review/index records. Configure `validate` on a
Windows runner with the exact supported Python, local `.venv`, dependencies
and node_modules; invoke the existing explicit Core clone initializer, which
checks origin/pin and installs workspace rules from the pinned Core. Download
the public OpenAI skill creator validator at a fixed source commit with a
SHA-256 check, expose `SKILL_CREATOR_ROOT`, then run the unchanged full pytest
gate. Refresh only the four LF knowledge source hashes and verify the pack
on LF bytes. Do not skip/xfail/remove tests, mock provider governance, fetch
private provenance or copy secrets. Continue dependent same-scope CI repairs
under this authority; re-admit only a changed path family, risk or effect boundary.
Independent authorization re-review is required before amendment 2 BUILD.

Amendment 2 admission choreography: existing dispatch commits `8f4ecfb` and
`07b4011` remain the tranche anchors. Independent acceptance and current
continuity acknowledgment are recorded before BUILD; their changed records
land with the amendment material commit through the normal hook. A fresh
dispatch commit per amendment is not an inherited Core requirement. The
graph's dispatch-continuity row retains its existing committed anchor; the
amendment admission rows use MATERIAL_COMMIT. After material, preserve
independent terminal review, a dedicated actual-SHA continuity commit and
clean split-range closure review.

Dependent amendment 2 test-portability repair: run `41907009464` passed all
environment/catalog setup and reported 3 failures/8 setup errors, isolated
to two fixtures. Add exact paths
`tests/integration/test_project_knowledge_ingest_rehearsal.py` and
`tests/unit/test_p5a2_demo_recovery_findings.py`. Canonicalize helper SHA input
to LF, matching the existing normalized Git-blob integrity comparison and
unchanged expected hash. Explicitly set the ACL fixture owner to the current
user before the existing private/OWNER RIGHTS/Everyone assertions; hosted
admin-created files can default to the Administrators owner. Keep runtime
ACL verifier and all tamper/refusal assertions unchanged. Existing G01–G14
binding and operator CI authority apply; independent review gates repair.

Dependent test deadline repair adds exact
`tests/unit/test_report_export_limits.py`: two full-hook attempts failed
because the Windows spawned test worker had not reached its partial-output
marker within the test-only3s deadline, while isolated25tests PASS. The
product's unchanged `DEADLINE_SECONDS` is10s. Bind this real-child test and
its elapsed bound to that actual product deadline, keeping partial-write,
termination and no-return assertions; change no runtime deadline or guard.
This is a separately evidenced test portability cause under the same CI
milestone binding and requires independent review before repair.

## Product Milestone Binding

- **Milestone:** P5-A2, `docs/implementation/EXECUTION_ROADMAP.md`, assessed at
  `f5c5fc1` and PR #5 merge candidate `db75213`; still OPEN.
- **User outcome:** authorized users ultimately receive source-linked proactive
  reporting across SQL/API/UI with human approval before durable action.
- **Acceptance:** full reporting, source, quality, scheduler, approval,
  integration and live provider governance evidence under P5-A2; independent
  review and operator acceptance. This CI repair cannot close that outcome.
- **Current truth:** AM4 exact read-only SQL and JWT login accepted, first UI
  submit failed before source GET or screenshot; attempt SPENT and physical
  cause UNKNOWN. Phase 5 remains 0/5.
- **This assignment:** restore PR CI as a prerequisite to reviewed G04/G05
  diagnosis. Owner Root, paths limited to `pyproject.toml`, project catalog
  renderer and projection, CI workflow, knowledge manifest LF pins, generated catalog views if needed, this packet, review and
  project-owned continuity/catalog artifacts required for closure. Stop when
  fresh-checkout catalog and editable-install probes pass, local gates pass,
  independent review accepts, PR checks pass and PR #5 merges without a
  product-completion claim. No new AM4 physical attempt.
- **Product return:** return to bounded G04/G05 UI readiness diagnosis/planning
  under a separate assignment. This support work does not authorize source UI
  repair, runtime, provider or replay.

| Gap | Current evidence / limitation | In assignment | Owner / destination |
|---|---|---|---|
| G01/A7 | Provider 401, BLOCKED | NO | Root/operator, P5-A A7 then P5-A2 |
| G02 | Operational RAG/context/citations BLOCKED | NO | Backend/Root, P5-A2 context |
| G03 | Business/cohort fit UNKNOWN | NO | Backend/operator, P5-A2 method |
| G04 | Synthetic SQL/JWT accepted; UI failed; operational integration UNKNOWN | CI support only | Backend/Root, P5-A2 source |
| G05 | Synthetic authority accepted; production/coverage/retention/SQLite UNKNOWN; UI missing | CI support only | Backend/Root/operator, P5-A2 coverage |
| G06 | Later use-time access OPEN | NO | Backend/Root, P5-A2 approval |
| G07 | Scheduler/claim/recovery OPEN | NO | Backend/Root, P5-A2 runtime |
| G08 | Signal quality OPEN | NO | Backend/operator, P5-A2 signals |
| G09 | Forecast accuracy OPEN | NO | Backend/operator, P5-A2 forecasting |
| G10 | Drift display OPEN | NO | Backend/UI/Root, P5-A2 quality and P5-B |
| G11 | Source panel UI proof failed; other flows OPEN | NO | UI/Root/operator, P5-A2 application |
| G12 | Human approval OPEN | NO | Backend/UI/operator, P5-A2 approval |
| G13 | Integrated drills OPEN | NO | Backend/Root, P5-A2 drills and P5-C |
| G14 | Live AI governance proof HELD | NO | Root/operator, separately admitted P5-A2 REVIEW |

## WORK_ORDER / BUILD / REVIEW

ORCHESTRATOR → SPEC_AUTHOR → WORK_ORDER_AUTHOR: this packet bounds the repair.
IMPLEMENTATION_WORKER changes only the two original CI causes and the
amended hosted projection and clean-runner causes. REVIEWER independently
checks the exact source/checkout comparison, packaging metadata, merged PR
coverage, negative findings and claim boundaries. COMMIT_STEWARD uses the normal
hook and exact changed-path review. SESSION_SYNC_STEWARD records the actual
material commit and keeps canonical project continuity aligned. CLOSER may
merge only after green hosted checks and no unresolved independent findings.

Independent authorization review PASS after continuity synchronization:
Product Milestone Binding G01–G14 complete for this support assignment,
pinned Core preflight COMPLIANT/0, work-order graph 0 violations, and
canonical state/bootstrap/mirror/memory/handoff aligned. The initial BUILD
started after its dispatch commit. Amendment 2 follows the admission
choreography above after independent review and current acknowledgment.

## Gate-To-Role Closeability Contract

closeabilityContractVersion: cvf.gate-role-closeability@1.0.0
closeabilityDisposition: CLOSEABLE
returnTimeRecheck: REQUIRED_BEFORE_REPAIR
implementationTopologyPolicy: BOUNDED_PATH_FAMILIES
foreseeableFileSplitDisposition: COVERED_BY_BOUNDED_PATH_FAMILY

| gateId | mustPassBy | repairOwner | repairPhase | mutationSurface | topology | commitOwner | commitPhase | dependsOn |
|---|---|---|---|---|---|---|---|---|
| authorization_review | PRE_DISPATCH | work-order-author | PRE_DISPATCH | docs/work_orders/CI_PR5_REPAIR_2026-11-05.md | EXACT_PATHS | commit-steward | MATERIAL_COMMIT | NONE |
| pre_dispatch_gate | PRE_DISPATCH | orchestrator | PRE_DISPATCH | docs/work_orders/CI_PR5_REPAIR_2026-11-05.md;SESSION/handoffs/AGENT_HANDOFF_CI_PR5_REPAIR_2026-11-05.md;SESSION/ACTIVE_SESSION_STATE.json;SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json;CVF_SESSION/ACTIVE_SESSION_STATE.json;SESSION/SESSION_MEMORY.md;docs/catalog/ARTIFACT_REGISTRY.json;docs/INDEX.md | BOUNDED_PATH_FAMILY | commit-steward | MATERIAL_COMMIT | authorization_review |
| dispatch_continuity | IMPLEMENTATION | session-sync-steward | IMPLEMENTATION | SESSION/handoffs/AGENT_HANDOFF_CI_PR5_REPAIR_2026-11-05.md material-SHA marker | EXACT_PATHS | session-sync-steward | DISPATCH_CONTINUITY_COMMIT | pre_dispatch_gate |
| pre_implementation_autorun | IMPLEMENTATION | orchestrator | IMPLEMENTATION | docs/work_orders/CI_PR5_REPAIR_2026-11-05.md;SESSION/handoffs/AGENT_HANDOFF_CI_PR5_REPAIR_2026-11-05.md | EXACT_PATHS | commit-steward | MATERIAL_COMMIT | dispatch_continuity |
| focused_checker_tests | WORKER_RETURN | implementation-worker | IMPLEMENTATION | pyproject.toml;scripts/lib/downstream_catalog/CvfDownstreamCatalogLib.ps1;scripts/sync_cvf_catalog_kit.py;.github/workflows/ci.yml;knowledge/manifest.json;tests/integration/test_project_knowledge_ingest_rehearsal.py;tests/unit/test_p5a2_demo_recovery_findings.py;tests/unit/test_report_export_limits.py;docs/INDEX.md;docs/catalog/MODULE_CATALOG.md | EXACT_PATHS | commit-steward | MATERIAL_COMMIT | dispatch_continuity,pre_implementation_autorun |
| adif_integrity | WORKER_RETURN | orchestrator | WORKER_RETURN | docs/work_orders/CI_PR5_REPAIR_2026-11-05.md | EXACT_PATHS | commit-steward | MATERIAL_COMMIT | focused_checker_tests |
| worker_return_fast | WORKER_RETURN | orchestrator | WORKER_RETURN | docs/reviews/CI_PR5_REPAIR_REVIEW_2026-11-05.md | EXACT_PATHS | commit-steward | MATERIAL_COMMIT | adif_integrity |
| reviewer_fast | REVIEW | reviewer | REVIEW | docs/reviews/CI_PR5_REPAIR_REVIEW_2026-11-05.md | EXACT_PATHS | commit-steward | MATERIAL_COMMIT | worker_return_fast |
| pre_commit | PRE_MATERIAL_COMMIT | repair-worker | PRE_MATERIAL_COMMIT | pyproject.toml;scripts/lib/downstream_catalog/CvfDownstreamCatalogLib.ps1;scripts/sync_cvf_catalog_kit.py;.github/workflows/ci.yml;knowledge/manifest.json;tests/integration/test_project_knowledge_ingest_rehearsal.py;tests/unit/test_p5a2_demo_recovery_findings.py;tests/unit/test_report_export_limits.py;docs/INDEX.md;docs/catalog/MODULE_CATALOG.md;docs/work_orders/CI_PR5_REPAIR_2026-11-05.md;docs/reviews/CI_PR5_REPAIR_REVIEW_2026-11-05.md;SESSION/handoffs/AGENT_HANDOFF_CI_PR5_REPAIR_2026-11-05.md;SESSION/ACTIVE_SESSION_STATE.json;SESSION/SESSION_MEMORY.md;SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json;CVF_SESSION/ACTIVE_SESSION_STATE.json;docs/catalog/ARTIFACT_REGISTRY.json;docs/PROJECT_INDEX.md | BOUNDED_PATH_FAMILY | commit-steward | MATERIAL_COMMIT | reviewer_fast |
| terminal_completion_review | POST_MATERIAL | reviewer | POST_MATERIAL | docs/reviews/CI_PR5_REPAIR_REVIEW_2026-11-05.md | EXACT_PATHS | commit-steward | CORRECTIVE_MATERIAL_COMMIT | pre_commit |
| continuity | CONTINUITY_COMMIT | session-sync-steward | CONTINUITY_COMMIT | SESSION/handoffs/AGENT_HANDOFF_CI_PR5_REPAIR_2026-11-05.md;SESSION/ACTIVE_SESSION_STATE.json;SESSION/SESSION_MEMORY.md;SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json;CVF_SESSION/ACTIVE_SESSION_STATE.json | EXACT_PATHS | session-sync-steward | CONTINUITY_COMMIT | terminal_completion_review |
| committed_range_closure | POST_MATERIAL_CLOSURE | reviewer | POST_MATERIAL_CLOSURE | SESSION/handoffs/AGENT_HANDOFF_CI_PR5_REPAIR_2026-11-05.md;docs/reviews/CI_PR5_REPAIR_REVIEW_2026-11-05.md | EXACT_PATHS | session-sync-steward | CONTINUITY_COMMIT | continuity |
