# P5-A2 G04/G05 synthetic backend — Stage A Work Order

Status: DISPATCH_READY
Date: 2026-10-26; baseline `674d98e35f0fbafa868c34d3c3adbdd215ef3aa5`; R2.
Root WORK_ORDER_AUTHOR, ORCHESTRATOR, effect/commit owner. This Work Order grants Stage A code only after independent admission, normal
dispatch, actual-SHA continuity and clean-range gate. No physical execution.
Admission requires the three
independent frozen inputs, the source-family plan and a complete registered
STATIC_CONTRACT_ONLY resource-lifecycle family, complete metadata
patch, exact ownership and independent admission are recorded and reviewed.

## Product Milestone Binding

Canonical current P5-A2 acceptance and complete G01–G14 reconciliation,
owners and P5-A2/B/C/D destinations are in
`docs/specs/P5A2_SYNTHETIC_BACKEND_SPEC.md`, derived from current
`docs/decisions/P5A2_SOURCE_COVERAGE_INTAKE_DESIGN_2026-10-26.md` at the
baseline above. The complete user outcome is integrated authorized scheduled
signals, forecasts, history, lineage, freshness, uncertainty and abstention,
then exact human run/version/source approval before a durable recommendation
or action. Operator owns business acceptance; Root owns contracts/effects/
commit, backend worker future code, independent reviewer acceptance.

This Stage A assignment covers only G04/G05 synthetic development source:
an exact fixed local PostgreSQL dataset/authority contract, isolated API
composition and inert lifecycle tools with tests. It must preserve normal
coverage `None` and accepted API/UI behavior. It does not prove a physical
container, production coverage, operational history, quality, forecast
accuracy, AI governance or milestone completion. G01/A7 and G02 remain
BLOCKED; G03 fit, G04 operational integration and G05 production mode,
authority, coverage, retention and positive SQLite remain UNKNOWN. G06 later
use, G07 scheduler, G08–G10 operational quality, G11 remaining flows, G12
approval and G13 integrated drills remain OPEN; G14 live proof is HELD.
Backend/Root own source/runtime/context/drills, backend/operator fit/quality,
UI/Root/operator application, backend/UI/operator approval. P5-B dashboard/
search/observability stays backend/UI/Root; P5-C resilience/security/
performance backend/Root/operator; P5-D deployment/Shadow Mode/release
Root/operator. Phase 5 stays 0/5.

Finite product return: independently accepted Stage A code and in-process
contract proof, then a separate Stage B effect Work Order for one owned
persistent PostgreSQL profile and two exact real HTTP/UI contexts. The later
product move after that bounded proof is integrated runtime, quality,
context and approval work. Repeated source-support work cannot authorize
another tranche automatically.

## Stage A exact implementation ownership and topology

The future IMPLEMENTATION_WORKER may modify only these exact 23 paths plus
`docs/decisions/P5A2_SYNTHETIC_BACKEND_WORKER_RETURN_2026-10-26.md` after GO:

| Path | Purpose |
|---|---|
| `apps/workspace-api/src/workspace_api/config.py` | isolated marker and dotenv-disabled settings seam; normal path unchanged |
| `apps/workspace-api/src/workspace_api/demo/__init__.py` | package marker |
| `apps/workspace-api/src/workspace_api/demo/source_bundle_v1.json` | deployable exact synthetic records, byte/digest checked against frozen input |
| `apps/workspace-api/src/workspace_api/demo/authority_v1.json` | metadata-only deployable authority, fixed pin; no bodies, passwords or expected HTTP receipts |
| `apps/workspace-api/src/workspace_api/demo/bundle.py` | fixed bundle and metadata integrity loader |
| `apps/workspace-api/src/workspace_api/demo/coverage.py` | exact metadata-only `CoverageVerifier` |
| `apps/workspace-api/src/workspace_api/demo/seed.py` | owned idempotent PostgreSQL seed with real password hash |
| `apps/workspace-api/src/workspace_api/demo/app.py` | separate limited FastAPI app, real auth/source, owned ledger |
| `apps/workspace-api/src/workspace_api/demo/read_routes.py` | exact top-level console GET allowlist and router composition |
| `apps/workspace-api/src/workspace_api/demo/read_routes_shift.py` | selected-shift read-only GETs, split upfront under 300 lines |
| `apps/workspace-web/vite.source-demo.config.ts` | profile-only build: `envDir: false`, explicit loopback API URL, ignored `.venv/` output; normal Vite unchanged |
| `infrastructure/demo/p5a2-source-postgres.compose.yml` | one loopback PostgreSQL-only service and named volume; never the full compose |
| `scripts/p5a2_source_demo_common.py` | exact ownership record/port/ID helpers, no ambient effects |
| `scripts/p5a2_source_demo_preflight.py` | read-only local image/port/ownership checks |
| `scripts/p5a2_source_demo_start.py` | code for later one-owned-resource launch; not run in Stage A |
| `scripts/p5a2_source_demo_stop.py` | exact owner-only stop, retain volume; not run in Stage A |
| `scripts/p5a2_source_demo_smoke.py` | later exact two-context SQL/JWT/HTTP evidence code; not run in Stage A |
| `tests/unit/test_p5a2_demo_bundle.py` | independent dataset/authority pins and corruption refusals |
| `tests/unit/test_p5a2_demo_coverage.py` | exact metadata, count, actor/window/policy and mismatch outcomes |
| `tests/unit/test_p5a2_demo_profile.py` | dotenv/ambient-secret, missing DB and normal-default isolation |
| `tests/unit/test_p5a2_demo_lifecycle.py` | inert ownership state/port/image/stop refusal matrix, no Docker CLI |
| `tests/unit/test_p5a2_demo_routes.py` | exact path/method set, auth/read-only/403 and no mutation routes |
| `tests/integration/test_p5a2_demo_source_http.py` | in-process real auth/source HTTP against both frozen full receipts |

These files are an upfront bounded split: every `.py` <=300 lines and `.ts`
<=200 lines; no extra
helper, runtime test import, package manifest/lock, normal `main.py`, generic
UI/API source module, original oracle or full-stack compose edit. A necessary
split outside these paths is a Work Order amendment and independent review
before the new file is written. No worker-created credential, database,
container, server, browser, package install or network effect in Stage A.
The proposed lifecycle matrix uses only domains supported by the installed
generic mutation generator: 64-lowercase-hex owner nonce/container/image/
fingerprint/digest IDs, fixed named volume
`shiftops-p5a2-source-demo-data-v1`, and INTEGER PID fields. Image ID is
normalized after verifying the Docker `sha256:` prefix. Tests additionally
reject nonpositive, boolean and fractional PIDs and foreign/swapped/stale
resource ownership through contextual checks. Flat resource counters denote
currently still-owned resources after bounded reverse cleanup, never cumulative
created counts. Contextual evidence preserves creation/cleanup trail with exact
IDs and proves each still-owned identity; SEED_FAILED plus volume-only is valid
after verified container cleanup. Matrix shape alone does not
prove actual OS ownership or liveness. No generic guard/schema change is
authorized.

Root alone owns this SPEC/WO, the three frozen JSON inputs, admission/review,
`docs/cvf/invariants/p5a2-scoped-source-outcomes.json`, the proposed distinct
resource lifecycle family registry/matrix and real
`docs/specs/p5a2_demo_lifecycle_invariant_pin.py` docpin, four source-family consumer literal
pins (`docs/specs/p5a2_scoped_source_invariant_pin.py`,
`apps/workspace-api/src/workspace_api/application/proactive_source_receipt.py`,
`apps/workspace-api/src/workspace_api/api/proactive/response.py`,
`apps/workspace-web/src/features/proactive-source/sourceReceipt.ts`), catalog,
knowledge and SESSION continuity. The worker must not edit those paths.
Original source API/UI/PG/body oracles and Core are immutable. Reviewer alone
owns `docs/decisions/P5A2_SYNTHETIC_BACKEND_REVIEW_2026-10-26.md`.

## Pre-dispatch immutable contract and independent admission

Before status changes from DRAFT, Root records exact raw SHA-256, derivation
recipe and independent review for:
`fixtures/p5a2_source_demo_v1.json`,
`fixtures/p5a2_source_demo_authority_v1.json`, and
`tests/fixtures/p5a2_source_demo_oracle.json`. The first has complete 36/36/37
synthetic rows; the second has fixed instance/actor/policies and two approved
contexts with exact cohort/candidate digest metadata; the third has two
complete new-scope HTTP receipts. No generated expectation may come from the
new loader/verifier. Pin old API/body oracle hashes and show why a new scope
requires complete new receipts. Current independent raw hashes are data
`5a7f1dbc61fbdc40b4c201763c18c463902ea8d928ad105eddeff7b16a617cae`,
metadata authority
`3ed09877a15b7bbd9ae1178392e6262688607e73a678a95c86e0132e213baecb`,
and full new-scope oracle
`b43b5aa27cd593ba560cc48e534d7c7c12f2299d084d8c45dcbfb40a5c1a6aca`.
They require the fixed actor `PUBLIC_ACTOR`, viewer login
`source-demo-viewer`, instance `P5A2-SOURCE-DEMO-LOCAL-1`, fixture
`P5A2-SOURCE-DEMO-1`, new self-scope
`P5A2-SELF-77b89304823a5d39f60ff3872317a3d2de8403b72b740f33140cfc61aca03311`,
and exactly `initial_asof36` (36/36) plus `later_asof38` (36/37).
Freeze the complete recoverable metadata-only source-family patch and
prospective LF digest with four future consumer pins;
old registered source family `cb0fb2427848d58aaf44a3c675f3a4d9d4d59cc38214993684eb5cd4dc492243`
remains active through dispatch. Register the distinct
`P5A2-SOURCE-DEMO-RESOURCE-LIFECYCLE` family with a complete matrix, real
Root-owned docpin and existing generic family tests as STATIC_CONTRACT_ONLY
before dispatch because start/stop tools share persistent owner-state and
terminal outcomes. Its normative pre-code outcome/transition source is the
SPEC. Root freezes a full prospective metadata extension/final digest for
the future real adapter and tests, but does not activate those paths before
files exist. The source-family shapes,
domains, relations and mutation semantics may not change under metadata work.

Independent admission checks this complete contract, exact 23 worker paths,
root/reviewer ownership, 300-line split budget, Stage A zero effects, and the
full milestone gap table. Normal dispatch commit follows; an independent
actual review, dedicated five-path actual-SHA continuity commit, then clean
split-range gate precede worker GO. The active handoff successor is SESSION/handoffs/AGENT_HANDOFF_P5A2_SYNTHETIC_BACKEND_2026-10-26.md. No historical handoff SHA may be reused.

The native checker requires the literal handoff `material-SHA marker` label;
in this dispatch row its value is the actual dispatch SHA.
Dispatch continuity records the actual dispatch commit SHA in the exact five
paths declared in the graph. Later material continuity records the actual
implementation material SHA in a separate five-path child. No prior marker is
reused. Root-owned pre-commit surface is fully expanded below; no placeholder
confers authority.

## Stage A build sequence and tests

1. Worker rehydrates canonical project continuity and pinned Core, declares
   IMPLEMENTATION_WORKER in BUILD/R2/live-YES-for-AI-claims, and implements
   exact files. Normal default source coverage, auth, main app and other
   endpoints remain unchanged. The demo marker must disable `.env` before
   auth/router imports and reject missing owned PG, invalid bundle/authority,
   ambient forbidden settings or unsafe bind before listener startup. The
   profile-only Vite config disables env files, sets
   `VITE_API_URL=http://127.0.0.1:8001`, and writes only ignored `.venv/`
   output; normal UI/Vite remain unchanged.
2. The deployable bundle and authority are separately owned byte-exact
   runtime copies of the Root-frozen inputs, outside `tests/` and checked
   against their raw SHA-256 pins. Seeder validates
   exact owned DB/schema/36/36/37 immutable data and refuses partial/mismatch
   without cleanup/reset. Viewer password/JWT key are generated only by
   later Stage B launcher and supplied in a clean child environment. Stage A
   tests use nonsecret test values; no real local credential is created.
3. Coverage compares fixed actor/instance/two UTC contexts, dataset identity,
   policy and every native bounded metadata item. Normal `None` refusal and
   native access/freshness/caps stay load-bearing. Limited app mounts real
   login/me/source and the SPEC's exact GET allowlist only; no mutation verb
   or full normal router. In-process HTTP tests issue/verify a real test JWT
   through actual handlers, not a principal bypass. A test-only ledger
   injection may prove HTTP composition but must be labeled nonphysical.
4. After real files exist, worker performs only inert syntax/type checks and
   stops at `FILES_READY_FOR_BINDING` **before focused tests**. Root applies
   only its frozen source-family metadata patch/four literal pins and the
   independently registered lifecycle family's exact real adapter/test
   metadata extension and runtime consumer pins. Independent materialization
   review checks complete bytes, digest, real consumers/tests and file set.
   Only explicit Root test GO releases focused tests/repairs.
5. Focused tests compare both complete new receipts byte-for-byte and exercise
   default refusal; absent/bad/mismatched descriptor, scope, actor, window,
   policy, cohort, candidate, digest, assignment changes, bad JWT, path and
   method negatives; no secret/SQL detail; no memory fallback. Inert
   lifecycle tests cover owner-match/conflict/stop decisions without Docker
   invocation. Run the required full normal project hook, detailed catalog
   generator/kit/manager checks, knowledge/session/file-size/invariant guards
   through their respective owners. No optional physical test or browser in
   Stage A. Independent source reviewer checks exact pins, all remaining
   milestone gaps and no unapproved effects.

The Stage A worker return must list every file hash/line count, retained
failures, all G01–G14 remainders/owners/destinations, zero physical effects,
real-file family binding, and the standalone native Return-Time Closeability
Recheck for this project's legacy `docs/decisions/` path. Root owns normal
pre-commit, material commit, independent actual terminal review, dedicated
five-path material-SHA continuity and clean split-range closure. A bounded
tranche result is not P5-A2 or Phase 5 closure.

## Stage B effect boundary — separate Work Order required

This Stage A Work Order does not authorize running the start/smoke/stop tools,
Docker, PostgreSQL writes, API/web listener or browser. A later Stage B Work
Order must bind the same complete P5-A2 gap set and state an exact new budget:
one already-local inspected PostgreSQL 16 image, one newly owned persistent
container and named volume, one API and one static web child process, one
bounded seed, two fixed UTC query contexts, and a browser only if separately
selected. Dedicated PostgreSQL compose must use `network_mode: bridge` on
Docker's existing default bridge, with no `networks` declaration or new
Compose project network. It must define preflight refusal for missing image, port collision,
unowned prior state, missing installed project Python/psycopg/SQLAlchemy,
cached exact Node `22.14.0`/frontend modules, missing migration files and
profile mismatch before effects; exact loopback binds PostgreSQL
`127.0.0.1:5433`, API `127.0.0.1:8001`, static web `127.0.0.1:5174`;
fresh generated secrets in sanitized child env; exact owner record and
secret-free evidence; no pull/install, provider, `.env`, production data,
public bind, unrelated process stop, destructive volume reset or deletion.
On success retain `OWNED_RUNNING` with exact handles and stop instructions;
only an explicit later `stop` invocation may stop owned processes/container
while retaining the volume. On failure record what was started and exactly
owned cleanup. Old disposable
PG attempt budgets are spent. Independent Stage B admission, normal dispatch,
actual-SHA continuity, clean gate and source acceptance are prerequisites.

## Invariant-Family Proof

Applicability: existing registered `P5A2-SCOPED-SOURCE-OUTCOMES` at native LF
digest `cb0fb2427848d58aaf44a3c675f3a4d9d4d59cc38214993684eb5cd4dc492243`
for current native/HTTP/UI receipts; Root freezes metadata-only patch and new
digest before BUILD. Distinct persistent resource lifecycle family is required
for the new owner/start/stop state contract. Proposed ID is
`P5A2-SOURCE-DEMO-RESOURCE-LIFECYCLE`; Root must independently materialize
its complete matrix, docpin, pre-code digest and mutation corpus before
dispatch. Real adapter/test binding remains staged until real files exist.
No unregistered shared startup receipt is authoritative.
The accepted matrix owns outcome/field rules; this Work Order points to
`docs/cvf/INVARIANT_FAMILY_STANDARD.md` and does not copy its rules.
Exclusions: none proposed; any exclusion requires matrix reason and reviewer
acknowledgment. Evidence owner: implementation worker returns source/lifecycle
corpus; independent reviewer recomputes both matrix digests, runs full corpus,
samples raw positive/refusal outcomes and verifies oracle independence.
Commands after binding include `python scripts/check_invariant_families.py`
and exact focused unit/in-process HTTP tests; Stage B physical invocation is
separate. Invariant-family structural PASS does not prove operational source
completeness or AI governance.

## Gate-To-Role Closeability Contract

closeabilityContractVersion: cvf.gate-role-closeability@1.0.0
closeabilityDisposition: CLOSEABLE
returnTimeRecheck: REQUIRED_BEFORE_REPAIR
implementationTopologyPolicy: BOUNDED_PATH_FAMILIES
foreseeableFileSplitDisposition: COVERED_BY_BOUNDED_PATH_FAMILY

`DEMO_SOURCE` is the exact ten `apps/workspace-api/...` paths plus the one
exact `apps/workspace-web/vite.source-demo.config.ts` profile path above;
`DEMO_LIFECYCLE` is the exact compose plus five `scripts/...` paths;
`DEMO_TESTS` is the exact six `tests/...` paths. These families name a closed
list and allow the listed upfront splits only. Authority-bearing `config.py`,
bundle, compose, source-family matrix/pins and resource-family registry/matrix
retain exact-path ownership. The graph below is the planned Stage A topology;
The successor is SESSION/handoffs/AGENT_HANDOFF_P5A2_SYNTHETIC_BACKEND_2026-10-26.md; admission JSON carries complete recoverable source/lifecycle metadata patches, exact pins and ownership.

| gateId | mustPassBy | repairOwner | repairPhase | mutationSurface | topology | commitOwner | commitPhase | dependsOn |
|---|---|---|---|---|---|---|---|---|
| authorization_review | PRE_DISPATCH | work-order-author | PRE_DISPATCH | docs/work_orders/P5A2_SYNTHETIC_BACKEND_BUILD_WORK_ORDER.md | EXACT_PATHS | commit-steward | DISPATCH_COMMIT | NONE |
| pre_dispatch_gate | PRE_DISPATCH | orchestrator | PRE_DISPATCH | docs/specs/P5A2_SYNTHETIC_BACKEND_SPEC.md;docs/work_orders/P5A2_SYNTHETIC_BACKEND_BUILD_WORK_ORDER.md;fixtures/p5a2_source_demo_v1.json;fixtures/p5a2_source_demo_authority_v1.json;tests/fixtures/p5a2_source_demo_oracle.json;docs/cvf/invariants/registry.json;docs/cvf/invariants/p5a2-demo-resource-lifecycle.json;docs/specs/p5a2_demo_lifecycle_invariant_pin.py;docs/decisions/P5A2_SYNTHETIC_BACKEND_ADMISSION_2026-10-26.json | EXACT_PATHS | commit-steward | DISPATCH_COMMIT | authorization_review |
| dispatch_continuity | IMPLEMENTATION | session-sync-steward | IMPLEMENTATION | SESSION/handoffs/AGENT_HANDOFF_P5A2_SYNTHETIC_BACKEND_2026-10-26.md material-SHA marker;SESSION/ACTIVE_SESSION_STATE.json;SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json;SESSION/SESSION_MEMORY.md;CVF_SESSION/ACTIVE_SESSION_STATE.json | EXACT_PATHS | session-sync-steward | DISPATCH_CONTINUITY_COMMIT | pre_dispatch_gate |
| pre_implementation_autorun | IMPLEMENTATION | orchestrator | IMPLEMENTATION | SESSION/handoffs/AGENT_HANDOFF_P5A2_SYNTHETIC_BACKEND_2026-10-26.md;docs/work_orders/P5A2_SYNTHETIC_BACKEND_BUILD_WORK_ORDER.md | EXACT_PATHS | commit-steward | MATERIAL_COMMIT | dispatch_continuity |
| family_materialization | IMPLEMENTATION | orchestrator | IMPLEMENTATION | docs/cvf/invariants/p5a2-scoped-source-outcomes.json;docs/cvf/invariants/p5a2-demo-resource-lifecycle.json;docs/specs/p5a2_scoped_source_invariant_pin.py;docs/specs/p5a2_demo_lifecycle_invariant_pin.py;apps/workspace-api/src/workspace_api/application/proactive_source_receipt.py;apps/workspace-api/src/workspace_api/api/proactive/response.py;apps/workspace-web/src/features/proactive-source/sourceReceipt.ts | EXACT_PATHS | commit-steward | MATERIAL_COMMIT | pre_implementation_autorun |
| focused_checker_tests | WORKER_RETURN | implementation-worker | IMPLEMENTATION | DEMO_SOURCE;DEMO_LIFECYCLE;DEMO_TESTS | BOUNDED_PATH_FAMILY | commit-steward | MATERIAL_COMMIT | dispatch_continuity,pre_implementation_autorun,family_materialization |
| adif_integrity | WORKER_RETURN | implementation-worker | IMPLEMENTATION | docs/decisions/P5A2_SYNTHETIC_BACKEND_WORKER_RETURN_2026-10-26.md | EXACT_PATHS | commit-steward | MATERIAL_COMMIT | dispatch_continuity |
| worker_return_fast | WORKER_RETURN | implementation-worker | WORKER_RETURN | docs/decisions/P5A2_SYNTHETIC_BACKEND_WORKER_RETURN_2026-10-26.md | EXACT_PATHS | commit-steward | MATERIAL_COMMIT | focused_checker_tests,adif_integrity |
| reviewer_fast | REVIEW | reviewer | REVIEW | docs/decisions/P5A2_SYNTHETIC_BACKEND_REVIEW_2026-10-26.md | EXACT_PATHS | commit-steward | MATERIAL_COMMIT | worker_return_fast |
| pre_commit | PRE_MATERIAL_COMMIT | repair-worker | PRE_MATERIAL_COMMIT | DEMO_SOURCE;DEMO_LIFECYCLE;DEMO_TESTS;docs/decisions/P5A2_SYNTHETIC_BACKEND_WORKER_RETURN_2026-10-26.md;docs/decisions/P5A2_SYNTHETIC_BACKEND_REVIEW_2026-10-26.md;docs/specs/P5A2_SYNTHETIC_BACKEND_SPEC.md;docs/work_orders/P5A2_SYNTHETIC_BACKEND_BUILD_WORK_ORDER.md;docs/decisions/P5A2_SYNTHETIC_BACKEND_ADMISSION_2026-10-26.json;fixtures/p5a2_source_demo_v1.json;fixtures/p5a2_source_demo_authority_v1.json;tests/fixtures/p5a2_source_demo_oracle.json;tests/fixtures/p5a2_source_demo_lifecycle_oracle.json;docs/cvf/invariants/p5a2-scoped-source-outcomes.json;docs/cvf/invariants/p5a2-demo-resource-lifecycle.json;docs/specs/p5a2_demo_lifecycle_invariant_pin.py;docs/cvf/invariants/registry.json;docs/specs/p5a2_scoped_source_invariant_pin.py;apps/workspace-api/src/workspace_api/application/proactive_source_receipt.py;apps/workspace-api/src/workspace_api/api/proactive/response.py;apps/workspace-web/src/features/proactive-source/sourceReceipt.ts;SESSION/handoffs/AGENT_HANDOFF_P5A2_SYNTHETIC_BACKEND_2026-10-26.md;SESSION/ACTIVE_SESSION_STATE.json;SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json;SESSION/SESSION_MEMORY.md;CVF_SESSION/ACTIVE_SESSION_STATE.json;IMPLEMENTATION_STATUS.json;docs/PROJECT_INDEX.md;docs/implementation/EXECUTION_ROADMAP.md;knowledge/PROJECT_CONTEXT.md;knowledge/manifest.json;docs/catalog/ARTIFACT_REGISTRY.json;docs/catalog/MODULE_REGISTRY_DETAIL.json;docs/catalog/MODULE_CATALOG_DETAIL.md;docs/catalog/MODULE_REGISTRY.json;docs/catalog/MODULE_CATALOG.md;docs/INDEX.md;docs/decisions/P5A2_SOURCE_COVERAGE_INTAKE_DESIGN_2026-10-26.md;SESSION/handoffs/AGENT_HANDOFF_P5A2_SOURCE_COVERAGE_DESIGN_2026-10-26.md | BOUNDED_PATH_FAMILY | commit-steward | MATERIAL_COMMIT | reviewer_fast |
| terminal_completion_review | POST_MATERIAL | reviewer | POST_MATERIAL | docs/decisions/P5A2_SYNTHETIC_BACKEND_REVIEW_2026-10-26.md | EXACT_PATHS | commit-steward | CORRECTIVE_MATERIAL_COMMIT | pre_commit |
| continuity | CONTINUITY_COMMIT | session-sync-steward | CONTINUITY_COMMIT | SESSION/handoffs/AGENT_HANDOFF_P5A2_SYNTHETIC_BACKEND_2026-10-26.md;SESSION/ACTIVE_SESSION_STATE.json;SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json;SESSION/SESSION_MEMORY.md;CVF_SESSION/ACTIVE_SESSION_STATE.json | EXACT_PATHS | session-sync-steward | CONTINUITY_COMMIT | terminal_completion_review |
| committed_range_closure | POST_MATERIAL_CLOSURE | reviewer | POST_MATERIAL_CLOSURE | SESSION/handoffs/AGENT_HANDOFF_P5A2_SYNTHETIC_BACKEND_2026-10-26.md;docs/decisions/P5A2_SYNTHETIC_BACKEND_REVIEW_2026-10-26.md | EXACT_PATHS | session-sync-steward | CONTINUITY_COMMIT | continuity |

The pre-commit mutation row enumerates the complete exact Root-owned set.
Stage B's effect gates are absent here intentionally
and must be declared in its own Work Order. Any worker return or completion
review under this legacy `docs/decisions/` family must carry the exact
standalone self-declared marker and Return-Time Closeability Recheck; invoke
the verified pinned Core `check_recheck` directly. The normal CLI/hook does
not auto-scan this legacy family.

## Frozen registration and staged consumer pins

Admission: docs/decisions/P5A2_SYNTHETIC_BACKEND_ADMISSION_2026-10-26.json. Static lifecycle LF 97a307e0c190d5073c07cdaec20ea453fb93d9fdafa6ceea2ca043d3f1185459; planned runtime LF f323ef1062e791c1c8fa4bff880b765a79547b571b0cfca9083286d680dcef2c. Source old LF cb0fb2427848d58aaf44a3c675f3a4d9d4d59cc38214993684eb5cd4dc492243; planned final LF 6fec188950fe752ac438e2952ec3d4e2ffd3b4156efa0b9a2e06e1048c568754.
Frozen lifecycle sample corpus tests/fixtures/p5a2_source_demo_lifecycle_oracle.json contains eight independently prepared positives; all608 generated mutations reject before code. Exact symbols required: P5A2_DEMO_BUNDLE_SHA256 in demo/bundle.py, P5A2_DEMO_AUTHORITY_SHA256 in demo/coverage.py, and P5A2_DEMO_LIFECYCLE_MATRIX_CANONICAL_DIGEST in scripts/p5a2_source_demo_common.py, each a module-level bare literal assignment. Frozen three-input raw hashes and all metadata patch bytes are in admission. Existing four source consumers stay unchanged through dispatch.
