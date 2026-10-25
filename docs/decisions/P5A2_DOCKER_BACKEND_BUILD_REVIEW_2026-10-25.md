# P5-A2 Docker backend — independent build/effect review

docType: completion_review
Status: IMPLEMENTATION_REVIEW_READY
Date: 2026-10-25
Reviewer: Root, independent from Sol implementation worker

## Product Milestone Binding

Accepted Docker SPEC/WO and their complete G01–G14 table remain authoritative.
This review evaluates only G04/G05/G13 synthetic SQL substrate. G06 source
query/auth/caps and operational cohort/retention, G01/A7/G02, G07/G11/G12/G14
and the operational parts of G03/G08–G10/G13 retain their named owners/gates.
Root accountable, Sol backend, Luna UI, operator business acceptance;
P5-B/C/D retain roadmap destinations. P5-A/P5-A2 OPEN, Phase5 0/5.

## Consolidated Stage A review

Root inspected the complete wrapper, opt-in SQL target, unit tests, worker
return/evidence against R1–R4 and exact WO surfaces. Native lifecycle/readiness/
migration/sanitize helpers and domain/pure/fixture oracle remain unchanged.
The target seeds one known fixture, reconnects through SqlLedger and verifies
37 versions, currentness-independent as-of choices and exact frozen oracle
projections. Wrapper drops provider credentials from test child, rejects skipped
SQL success, verifies image identity and reports cleanup uncertainty as failure.
No real SQL/container/pip/image/provider effect has run; inert evidence is not
physical PostgreSQL proof or AI-governance proof. Existing final focused
10-pass/1-opt-in-skip evidence is consumed; no broad suite recreated here.

| Finding | Evidence | Controlled repair |
|---|---|---|
| DB-A-F1 | `tests/unit/test_p5a2_docker_runner.py` is outside the admitted `test_p5a2_docker_backend*.py` family, despite the return claiming all paths allowed | Reviewer-local rename of this new owned file to `tests/unit/test_p5a2_docker_backend_runner.py`, bytes unchanged; worker then reconciles manifest/evidence and reruns focused collection |
| DB-A-F2 | Worker return places self-declared marker and recheck scalars inline/bold, so canonical anchored parser cannot apply the mandatory recheck | Exact standalone `Self-declared worker-return artifact: yes`, Status line, and section scalar fields; preserve initial collection failure and the out-of-family rename truth |

All other R1–R4 source and effect prerequisites were assessed together. Root
selects REVIEWER_LOCAL_REPAIR to align the owned filename first, without
expanding the allowed family, content, risk, effect class or commit owner.
No worker redispatch until that outside-manifest condition is removed. Then
worker may repair only its return/evidence and focused collection under the
existing WO; Stage B remains NOT_ADMITTED pending rereview of settled bytes.

## Return-Time Closeability Recheck

closeabilityDisposition: CLOSEABLE
outsideAuthorityBlockers: NONE
nextRepairRoute: NONE
workerRedispatchAllowed: YES

## Reviewer-local filename alignment

Root rehydrated current continuity and verified doctor24/2/inheritance0.
DB-A-F1 local alignment completed: new owned unit file renamed to admitted
`tests/unit/test_p5a2_docker_backend_runner.py`; exact bytes/SHA56b7e5a unchanged.
No family expansion, code behavior edit or effect occurred. Outside-manifest
blocker removed. Existing WO permits worker metadata-only repair DB-A-F2 and
reconciliation of return/evidence plus one justified focused collection after
this rename. Stage B still NOT_ADMITTED pending independent rereview.

## Independent Stage A rereview and Stage B admission

STAGE_A_SOURCE_REVIEW_PASS_BOUNDED. Root inspected settled source, exact WO
families and both repaired artifacts. DB-A-F1/F2 RESOLVED, no waivers or open
source finding. Direct canonical applicable recheck returns0 for return/review;
source hashes match worker evidence and frozen SPEC/oracle/native helper pins.
Focused recollection10passed/1SQLopt-in-skip0.87s consumed, no duplicate suite.

Accepted source SHA256:
- wrapper43e7cfde098821cd64ba315ea61eb32d517278cb76d2741f8261b2ddff79dcc4
- SQLtarget4d34a1567bff544ae5dc0815fb8a48ec211ef084944835bd553f397fd5a29d7b
- unittests56b7e5a19f0aa2447a04133a0f77339a8e72b6d3be9a05ae90e980be723f580b

Root REVIEWER to ORCHESTRATOR records STAGE_B_ADMITTED under unchanged WO:
one missing official postgres:16-alpine acquisition; one projectvenv-only
psycopg[binary]==3.3.4 officialPyPI install; one wrapper invocation creating
one isolated loopback PG16, migrations001–011 twice, exactSQLtarget/oracle,
owned cleanup and verified absence. Source stays pinned. Failure stops with
spent/partial evidence, no automatic retry. No .env/operatorcredential/provider/
production/push/deployment effect. Actual results remain pending, not PASS.
Full14gap binding/remainders above retained; no whole criterion/milestone closure.

## Actual Stage B prerequisite failure and controlled disposition

Root RESULT_REVIEW_PASS_FAILURE_RECORDED: original driver install command1
exited1 because projectvenv has no pip module. Log SHA453c25791c5ae0d7dc53351cffd51ace485d9950c1ac749e2d758ddf19c0e471 verified.
No package acquisition/image pull/container/DB/provider occurred; no worker
retry. Stage A source acceptance remains valid, actual SQL proof NOT_RUN.
Root independently read-only confirmed uv0.10.7 exists and supports explicit
venv targeting/no-config/official-index/wheel-only/no-Python-download options.
Root REVIEWER to ORCHESTRATOR/WORK_ORDER_AUTHOR proposes AM1 in same WO,
requiring independent authorization plus normal material/dedicated continuity
before one controlled uv recovery. Same objective/path/risk/effect class/commit
owner uses standing operator autonomy; no new general capability or blanket
retry grant. Current worker remains blocked; proposed AM1 is not dispatch.

## AM1 authorization disposition and material boundary

Independent Luna AM1 authorization PASS_BOUNDED, no blockers. Root activates
accepted same-scope repair; original failed pip attempt remains spent and
original return truth remains historical. Missing pip no longer blocks the
approved uv route. Worker redispatch remains conditional on successful normal
material plus dedicated actual-SHA continuity and fresh pin/inheritance/session
pre-effect gate. No installer/image/container effect has occurred under AM1.
Source/inert mechanics accepted; actual SQL proof pending. This material records
accepted source, actual failure and reviewed AM1. Full14gap remainders retained.

## Public Export Disposition

DEFERRED_PRIVATE_ONLY — local downstream source/evidence and continuity;
no public release, push, deployment or AI-governance behavior proof.
