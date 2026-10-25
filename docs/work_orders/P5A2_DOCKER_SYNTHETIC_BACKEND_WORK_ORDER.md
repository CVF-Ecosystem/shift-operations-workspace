# P5-A2 Docker PostgreSQL synthetic-backend rehearsal

Status: IMPLEMENTED_BOUNDED
Date: 2026-10-25
Risk: R2
Execution owner: INTERNAL_AGENT IMPLEMENTATION_WORKER (Sol/medium)
Independent source/effect acceptance: Root REVIEWER
Commit/continuity owner: Root COMMIT_STEWARD / SESSION_SYNC_STEWARD

## Checker Source Read-Ahead Block

Read materialized `governance/compat/check_gate_to_role_closeability.py`:
ACTIVE_STATUSES/status grammar, REQUIRED_GATE_IDS, phase/topology constants and
`check_work_order`. Read its canonical closeability standard and the project
invariant-family standard/template. Root checks an active-status projection
before authorization; DRAFT status alone is not executable-contract proof.

## Product Milestone Binding

Milestone P5-A2, Phase5 in `docs/implementation/EXECUTION_ROADMAP.md`, source
`29c0ef7c953d5df6419d9542030acdd2b5d9197e` plus this contract packet.
Full acceptance/current truth/owned G01–G14 remainders: canonical parent
INTAKE/DESIGN, scoped-history audit/synthetic-first proposal/review and accepted
`docs/specs/P5A2_DOCKER_SYNTHETIC_BACKEND_SPEC.md` (its complete gap table).
User outcome remains integrated scoped scheduled forecast/history/lineage
with exact human approval before durable recommendations/actions.

G01/A7 and G02 operational RAG BLOCKED; pure G03–G05/G08–G10/G13 portions
accepted, operational portions OPEN/UNKNOWN; G06 actual query/auth/completeness,
G07 scheduler, G11 API/UI and G12 exact approval OPEN; G14 provider proof HELD.
This assignment serves only actual PostgreSQL persistence/time/lineage and
fixture-analysis portions G04/G05/G13. It closes no whole criterion. Root
accountable, Sol backend/contracts, Luna UI, independent reviewer, operator
business acceptance; every remainder retains its exact parent P5-A2 gate.
P5-B/C/D retain roadmap owners/destinations; Phase5 0/5. Necessity: prove the
native SQL substrate before building the missing scoped-history query adapter.
Finite stop: one reviewed source set and one admitted disposable PG rehearsal;
return directly to G04–G06 cohort/query/coverage/snapshot/cap SPEC/WO.

## Frozen requirements and oracle

Accepted SPEC SHA-256 `c97cad4967840e53f41909968a31f61920da754315d78dc3ea004f5a0745a830`;
independent acceptance `docs/decisions/P5A2_DOCKER_BACKEND_SPEC_REVIEW_2026-10-25.md`.
Implement R1–R4 together. Root's pre-BUILD oracle is copied byte-identically to
`tests/fixtures/p5a2_docker_backend_oracle.json`, SHA-256
`12ad36cbd335a8def5e7ac9a6ade6f0bf542cb45af4cec1760a7291a8f6973c0`.
It is read-only contract data committed before BUILD; do not regenerate expected
results from the new loader or change accepted helper/numeric algorithms.

## Allowed implementation paths and topology

Bounded new wrapper/helper family: `scripts/run_p5a2_docker_backend.py` and
`scripts/_p5a2_docker_backend_*.py`. New test family:
`tests/integration/test_p5a2_docker_backend.py`,
`tests/integration/_p5a2_docker_*.py`,
`tests/unit/test_p5a2_docker_backend*.py`.
Prefer one thin wrapper, one fixture/helper and one opt-in SQL target; split
within these families only if necessary, with every Python file <=300 lines.

Worker return/evidence:
`docs/decisions/P5A2_DOCKER_BACKEND_WORKER_RETURN_2026-10-25.md` and
`docs/decisions/P5A2_DOCKER_BACKEND_EVIDENCE_2026-10-25.json`.
Root review: `docs/decisions/P5A2_DOCKER_BACKEND_BUILD_REVIEW_2026-10-25.md`.
Root alone owns status/index/roadmap/catalog/knowledge/current handoff/state and
authority/artifact changes. Existing base/P4-E PostgreSQL runners, migrations,
SqlLedger/domain/pure code, parent SPEC/matrix and golden oracle are read-only.
No generic infrastructure framework, production source/query/API/UI/schema,
dependency manifest or existing guard changes are authorized.

## Effect admission and ceilings

Operator authority: roadmap continuation plus Docker backend request and
“làm đi”. It admits local disposable synthetic PostgreSQL when this WO is
independently accepted and dispatch/continuity committed. It does not release
the AI provider live/key/model/CSV hold.

Stage A is source BUILD and focused inert/unit tests only. Worker returns
before any pip, image pull or container effect. Root reviews the complete source
and existing focused evidence, then records Stage B admission in active handoff.
No new permission request is needed within these exact bounds.

Stage B permits one official PostgreSQL16-alpine image acquisition if missing
and one project `.venv`-only `psycopg[binary]==3.3.4` installation from official
PyPI (resolved versions/check evidence retained). No host/global install,
production connection, real operator credential, .env read, provider SDK call
or paid service. A failed acquisition is retained and stops; no automatic retry.
Record actual image ID and actual container image identity to detect tag change.

At most one actual uniquely named PostgreSQL container creation/rehearsal;
native dynamic loopback port, ephemeral generated DB password, no bind/named
volume. Only the exact new test target runs against its process-local URL.
Native bounded readiness polls are allowed; no second physical rehearsal.
Use a minimal child environment with required Windows/Python process settings
and synthetic DB URL, without copying provider credentials into test configuration.

Reuse native security-sensitive helpers unchanged. Capture owned identities and
anonymous volumes, always cleanup and verify absence. Never prune Docker or
delete an unrelated/pre-existing resource. Collision/ambiguous create is a stop
with no unproven cleanup authority. Sanitize all child output/tracebacks/receipts;
no raw password/DSN. Unit failure probes may use inert fakes of OS/runner results
and synthetic values, not mock-provider governance evidence. A real failure is
not reset or silently rerun. No claim the backend remains running after cleanup.

## Evidence and review sequence

1. Rehydrate canonical state/active handoff, declare role and run inheritance.
2. Root commits accepted SPEC/WO/oracle; terminal dispatch review authorizes a
   dedicated five-path actual-SHA continuity commit before BUILD.
   **Before any Stage A source edit or test**, Root/worker passes
   `pre_implementation_autorun` against the actual committed authority, current
   inheritance, SPEC/oracle pins and handoff marker. Its normal pass is read-only.
   WO-AUTH-F1 repair route: a failure stops Stage A and records BLOCKED_WITH_REASON;
   no worker repair/redispatch follows. For an error confined to this WO and
   current handoff, Root may perform at most one consolidated authority-packet
   correction within the unchanged SPEC/objective/risk/effects. Independent review
   must accept it, then Root commits a CORRECTIVE_MATERIAL_COMMIT through normal
   hooks, obtains terminal correction review and a **fresh dedicated actual-SHA
   continuity commit**. Only after those commits may the pre-implementation gate
   be rerun before Stage A. This is a post-dispatch repair branch, not an attempt
   to use the already-past DISPATCH_COMMIT. If it still fails, or the cause is
   outside the exact WO/handoff surfaces (including reference drift), this WO is
   terminal blocked with no in-tranche repair, effect or automatic redispatch;
   return the named blocker to Root. Never change guards, frozen SPEC/oracle,
   references or effects to force a pass under this branch.
3. Worker Stage A: native helper reuse; meaningful unit failures for missing
   prerequisites, safe cleanup/error propagation and redaction; real domain
   fixture/lineage checks. Run only relevant focused tests and guards. No DB yet.
4. Root consolidated independent source review; same-scope repair if needed.
5. After recorded Stage B admission, worker acquires the permitted dependencies,
   invokes one real Docker rehearsal, retains actual SQL/driver/server/image/
   migration/fixture/oracle/test/cleanup facts and returns without committing.
6. Root independently checks source/evidence/oracle and ownership/claim boundaries,
   runs the mandatory normal material hook, commits material, then dedicated
   actual-SHA continuity. Clean committed-range review follows continuity.

Proof: 36 shifts/37 persisted Report versions; migration apply/reapply and real
reconnect; aware cutoff/created_at and immutable content/manifest/digests;
initial36h excludes future successor, later38h selects it; exact selected lineage
and analysis summary match frozen oracle (READY36/forecast4/band[4,4]).
Negative/missing/time/tamper/failure cases must refuse/fail accurately. This
fixture does not prove G06 access/query caps, operational retention/cohort,
forecast business quality, RAG, durable scheduled recommendations or AI governance.

## Invariant-Family Proof

Applicability NOT_APPLICABLE under `docs/cvf/INVARIANT_FAMILY_STANDARD.md` and
accepted SPEC rationale: unchanged parent pure result and legacy runner summary,
no new shared business model/schema/counter or cross-emitter outcome contract.
No matrix/pin/registry modification is admitted. A newly needed shared receipt
grammar is returned to SPEC before implementation. Commands: relevant new
pytest paths, `scripts/check_invariant_families.py`, `scripts/check_file_size.py`,
inheritance, knowledge/session and repository validator; full pytest only via
mandatory normal commit hooks unless a named contradiction justifies more.
Worker owns returned evidence; independent Root checks actual values and pins,
consumes valid evidence, and does not recreate implementation or duplicate suites.

## Return-Time Closeability Recheck

Worker return and repair return must include the canonical Return-Time
Closeability Recheck. COMPLETE_PENDING_REVIEW requires CLOSEABLE and
outsideAuthorityBlockers: NONE. An outside-authority blocker must be
BLOCKED_WITH_REASON, no redispatch, with the controlled route to Root.
At repair round3 without an independent new root cause, record
REVIEW_COST_ESCALATION_REQUIRED and stop. Source-reference movement, failed
mandatory gate, contract mismatch or effect/path/risk expansion stops dependent
work; preserve all spent attempts and partial evidence.

## Gate-To-Role Closeability Contract

closeabilityContractVersion: cvf.gate-role-closeability@1.0.0
closeabilityDisposition: CLOSEABLE
returnTimeRecheck: REQUIRED_BEFORE_REPAIR
implementationTopologyPolicy: BOUNDED_PATH_FAMILIES
foreseeableFileSplitDisposition: COVERED_BY_BOUNDED_PATH_FAMILY

| gateId | mustPassBy | repairOwner | repairPhase | mutationSurface | topology | commitOwner | commitPhase | dependsOn |
|---|---|---|---|---|---|---|---|---|
| authorization_review | PRE_DISPATCH | orchestrator | PRE_DISPATCH | docs/work_orders/P5A2_DOCKER_SYNTHETIC_BACKEND_WORK_ORDER.md | EXACT_PATHS | commit-steward | DISPATCH_COMMIT | NONE |
| pre_dispatch_gate | PRE_DISPATCH | work-order-author | PRE_DISPATCH | docs/specs/P5A2_DOCKER_SYNTHETIC_BACKEND_SPEC.md;tests/fixtures/p5a2_docker_backend_oracle.json;docs/work_orders/P5A2_DOCKER_SYNTHETIC_BACKEND_WORK_ORDER.md | EXACT_PATHS | commit-steward | DISPATCH_COMMIT | authorization_review |
| dispatch_continuity | IMPLEMENTATION | session-sync-steward | IMPLEMENTATION | SESSION/handoffs/AGENT_HANDOFF_P5A2_DOCKER_BACKEND_2026-10-25.md material-SHA marker | EXACT_PATHS | session-sync-steward | DISPATCH_CONTINUITY_COMMIT | pre_dispatch_gate |
| pre_implementation_autorun | IMPLEMENTATION | orchestrator | IMPLEMENTATION | docs/work_orders/P5A2_DOCKER_SYNTHETIC_BACKEND_WORK_ORDER.md;SESSION/handoffs/AGENT_HANDOFF_P5A2_DOCKER_BACKEND_2026-10-25.md | EXACT_PATHS | commit-steward | CORRECTIVE_MATERIAL_COMMIT | dispatch_continuity |
| focused_checker_tests | WORKER_RETURN | implementation-worker | IMPLEMENTATION | scripts/run_p5a2_docker_backend.py;scripts/_p5a2_docker_backend_*.py;tests/integration/test_p5a2_docker_backend.py;tests/integration/_p5a2_docker_*.py;tests/unit/test_p5a2_docker_backend*.py | BOUNDED_PATH_FAMILIES | commit-steward | MATERIAL_COMMIT | dispatch_continuity,pre_implementation_autorun |
| stage_b_effect_admission | IMPLEMENTATION | reviewer | IMPLEMENTATION | docs/decisions/P5A2_DOCKER_BACKEND_BUILD_REVIEW_2026-10-25.md;SESSION/handoffs/AGENT_HANDOFF_P5A2_DOCKER_BACKEND_2026-10-25.md | EXACT_PATHS | commit-steward | MATERIAL_COMMIT | focused_checker_tests,pre_implementation_autorun |
| adif_integrity | WORKER_RETURN | implementation-worker | IMPLEMENTATION | docs/decisions/P5A2_DOCKER_BACKEND_WORKER_RETURN_2026-10-25.md | EXACT_PATHS | commit-steward | MATERIAL_COMMIT | dispatch_continuity |
| worker_return_fast | WORKER_RETURN | implementation-worker | WORKER_RETURN | docs/decisions/P5A2_DOCKER_BACKEND_WORKER_RETURN_2026-10-25.md;docs/decisions/P5A2_DOCKER_BACKEND_EVIDENCE_2026-10-25.json | EXACT_PATHS | commit-steward | MATERIAL_COMMIT | focused_checker_tests,adif_integrity,pre_implementation_autorun,stage_b_effect_admission |
| reviewer_fast | REVIEW | reviewer | REVIEW | docs/decisions/P5A2_DOCKER_BACKEND_BUILD_REVIEW_2026-10-25.md | EXACT_PATHS | commit-steward | MATERIAL_COMMIT | worker_return_fast |
| pre_commit | PRE_MATERIAL_COMMIT | repair-worker | PRE_MATERIAL_COMMIT | scripts/run_p5a2_docker_backend.py;scripts/_p5a2_docker_backend_*.py;tests/integration/test_p5a2_docker_backend.py;tests/integration/_p5a2_docker_*.py;tests/unit/test_p5a2_docker_backend*.py;docs/decisions/P5A2_DOCKER_BACKEND_BUILD_REVIEW_2026-10-25.md | BOUNDED_PATH_FAMILIES | commit-steward | MATERIAL_COMMIT | reviewer_fast |
| terminal_completion_review | POST_MATERIAL | reviewer | POST_MATERIAL | docs/decisions/P5A2_DOCKER_BACKEND_BUILD_REVIEW_2026-10-25.md | EXACT_PATHS | commit-steward | CORRECTIVE_MATERIAL_COMMIT | pre_commit |
| continuity | CONTINUITY_COMMIT | session-sync-steward | CONTINUITY_COMMIT | SESSION/handoffs/AGENT_HANDOFF_P5A2_DOCKER_BACKEND_2026-10-25.md;SESSION/ACTIVE_SESSION_STATE.json;SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json;SESSION/SESSION_MEMORY.md;CVF_SESSION/ACTIVE_SESSION_STATE.json | EXACT_PATHS | session-sync-steward | CONTINUITY_COMMIT | terminal_completion_review |
| committed_range_closure | POST_MATERIAL_CLOSURE | reviewer | POST_MATERIAL_CLOSURE | SESSION/handoffs/AGENT_HANDOFF_P5A2_DOCKER_BACKEND_2026-10-25.md;docs/decisions/P5A2_DOCKER_BACKEND_BUILD_REVIEW_2026-10-25.md | EXACT_PATHS | session-sync-steward | CONTINUITY_COMMIT | continuity |

## Activation

Root records independent Luna/max AUTHORIZATION_REREVIEW_PASS_BOUNDED;
WO-AUTH-F1 resolved, no adjacent blockers. Root ORCHESTRATOR activates only
this reviewed scope. Stage A still needs committed dispatch, dedicated actual-SHA
continuity and pre-implementation gate; Stage B additionally needs independent
source acceptance and explicit bounded effect admission in the active handoff.

## AM1 — controlled installer recovery, proposed for independent authorization

AM1 status: APPROVED_FOR_EXECUTION_AFTER_COMMITTED_CONTINUITY. Original Stage B admission is STOPPED.
One pip command was spent and exited1 before package/network/image/container/
DB effects: projectvenv lacks pip. Its retained failure and original no-retry
ceiling stand. Worker did not retry. Root independently confirmed Python3.13.12,
no psycopg, installed uv0.10.7 and its native pip-compatible installer help.

Root ORCHESTRATOR/WORK_ORDER_AUTHOR invokes the operator's existing autonomous
roadmap/same-scope repair authority for a consolidated authority amendment,
not a worker retry or reset of history. Objective/G04-G05-G13 acceptance,
source families/SHA, R2 ceiling, official-PyPI package/localDocker external
class and Root commit ownership remain unchanged. No pip bootstrap, new
runtime dependency framework, provider, real credentials or production scope.

After independent AM1 acceptance, normal material commit, dedicated actual-SHA
continuity and fresh pre-effect pin/inheritance/session checks, AM1 may admit
ONE replacement driver installation using the ALREADY installed uv executable
with explicit `.venv/Scripts/python.exe` target, `--no-config`,
`--no-python-downloads`, `--default-index https://pypi.org/simple`,
`--only-binary :all:` and exact `psycopg[binary]==3.3.4`. Run installer in a
minimal process environment with Windows/PATH/temp/cache necessities, no ambient
UV/PIP/index/provider credential settings. No host/global Python modification.
Do not install pip or use system pip. Retain uv version/path, exact sanitized
command/exit/log and resolved psycopg/psycopg-binary versions; verify their
installed metadata under this projectvenv. ONE driver recovery attempt total;
failure is terminal, with no further installer repair or automatic successor.

The as-yet-unused original image acquisition and one physical container/
wrapper rehearsal ceilings carry forward unchanged and are NOT renewed:
missing official postgres:16-alpine acquisition once, one pinned-source run,
owned anonymous-volume/container cleanup and verified absence. Failed image
acquisition or physical run remains terminal with no automatic retry.
Worker returns original pip failure plus actual AM1 outcome; Root reviews both.

Full Product Milestone Binding remains the accepted SPEC G01–G14 table above:
this bounded environment repair is necessary only to unblock actual SQL proof
for G04/G05/G13. It closes no whole criterion. All G06 scoped query/auth/caps/
cohort/retention and all other operational/backend/UI/scheduler/approval/live
remainders retain their named Root/Sol/Luna/operator owners and canonical
P5-A2/P5-B/C/D destinations. Stop at this ONE recovery plus carried rehearsal,
then return directly to G04–G06 product query/cohort/coverage SPEC; Phase5 0/5.
Existing graph applies: AM1 independent authorization/pre-effect recheck precede
any renewed worker effect, material+dedicated continuity before that recheck;
worker return/reviewer/material/terminal continuity/range closure unchanged.
Frozen SPEC/oracle and accepted wrapper/SQL/unit SHA stay read-only.

AM1 activation: Root records independent Luna AUTHORIZATION_REVIEW_PASS_BOUNDED,
no blockers. Current material/dedicated continuity and fresh pre-effect gate
remain mandatory; this activation alone starts no recovery effect.

## Execution disposition — 2026-10-26

Root independent FINAL_RESULT_REVIEW_PASS_BOUNDED at the assigned review.
Original pip failure preserved; AM1 oneuv install and carried oneimage/onePG
rehearsal succeeded, exactownedcleanup independently verified. Source remains
43e7cfde/4d34a156/56b7e5a; frozen SPEC/oracle unchanged. Execution authority is
committed a2d189e plus dedicated7fd67f5; execution WO SHA256 e349653e2bebd967a4954e7f4569a75de32926ae854850e2630782b6037e69d7.
All effect ceilings are SPENT, no further effect/redispatch grant. Normal result
material/dedicatedactualSHAcontinuity/cleanrange still gate bounded closure;
G04/G05/G13 SQLfixture only, no wholemilestone closure or governance proof.

Post-result gate disposition: BLOCKED_RENEWED_REFERENCE_DRIFT. Actual SQLfixture
PASS and all effect ceilings SPENT; resultmaterial/closure NOT_COMMITTED because
privateHEAD no longer matches pinned operator-local authority. No redispatch,
new effect, in-tranche reference refresh or FREEZE. Assigned resultreview and
activehandoff own exact observed/pinned SHA and controlled reconciliation route.

Current carried-result disposition: the operator-authorized independently
accepted Core-only correction supersedes the historical privateHEAD stop.
Actual SQLfixture result remains accepted; no source/oracle/receipt or physical
repeat. Normal carriedresultmaterial and dedicatedactualSHAcontinuity/cleanrange
are recorded in the active Core-binding handoff before bounded closure.
All external-effect ceilings stay spent, no further execution authority.
