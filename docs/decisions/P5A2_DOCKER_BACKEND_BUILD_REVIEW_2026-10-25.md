# P5-A2 Docker backend — independent build/effect review

docType: completion_review
Status: REVIEW_PASS_BOUNDED
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

## Independent actual-result review — 2026-10-26

FINAL_RESULT_REVIEW_PASS_BOUNDED. Root independent from Sol worker consumed
actual uv/image/wrapper logs and verified all four raw SHA256 values, retained
original pip failure, accepted source hashes and frozen SPEC/oracle. Original
failed pip command remains spent; AM1 oneuv install/onepull/onephysicalwrapper
is independently authorized and separately recorded. No rerun was performed.
Root verified installed psycopg/psycopg-binary3.3.4 metadata is inside projectvenv.
Raw runner exit0, SQLtarget1passed1.37s, image/container identity MATCH, migrations
001–011 twice46/0 then42/4. Source target matches exact frozen37versions and both
as-of36h/38h lineage/analysis oracles:36observations,forecast4,band[4,4].
No attaching UTC to naive values or expected-value regeneration occurred.
Root independently queried exactowned container name and captured anonymous
volume identity after worker return: both ABSENT. No deletion/rerun was issued.
Raw outputs have no PostgreSQL URI or POSTGRES_PASSWORD assignment. No real
operator secret, .env, production/provider/model/key/CSV or app source change.
R1–R4 accepted within syntheticfixture boundary; findings NONE, waivers NONE.
Historical DB-A-F1/F2 and original missing-pip failure remain disclosed above.

### Current complete milestone coverage and owned return

| Gap | Accepted now and remaining gap | Accountable owner / destination |
|---|---|---|
| G01 | P5-A A7 failed401 retained; dependency BLOCKED | Root/operator, P5-A A7 then P5-A2 entry gate |
| G02 | Operational RAG corpus/index/auth/citations BLOCKED | Root/Sol, P5-A2 context readiness |
| G03 | Pure metric/horizon accepted; operational cohort/method fit OPEN | Sol/Root/operator, P5-A2 operational metric/cohort SPEC |
| G04 | Pure and actual synthetic SQL version/as-of/lineage ACCEPTED; scoped source integration OPEN | Sol/Root, P5-A2 G04–G06 query/cohort/coverage SPEC/WO |
| G05 | Pure and actual PostgreSQL aware-time fixture ACCEPTED; real retention/timezone/coverage UNKNOWN | Sol/Root/operator, P5-A2 G05 coverage/retention authority |
| G06 | Assignment foundations exist; exhaustive bounded query/auth/revocation/caps/reportless cohort UNKNOWN/OPEN | Sol/Root, P5-A2 G04–G06 source adapter SPEC/WO |
| G07 | Scheduler identity/idempotency/missed/duplicate/recovery OPEN | Sol/Root, P5-A2 scheduler contract |
| G08 | Pure signal accepted; operational false-positive acceptance OPEN | Sol/Root/operator, P5-A2 signal business review |
| G09 | Pure and fixture forecast accepted; business forecast accuracy OPEN | Sol/Root/operator, P5-A2 prospective evaluation |
| G10 | Pure calibration/drift accepted; operational monitoring/UI OPEN | Sol/Luna/Root, P5-A2 monitoring and P5-B observability |
| G11 | Forecast API/UI/current/history/freshness OPEN | Sol/Luna/Root, P5-A2 integrated application slice |
| G12 | Exact recommendation approval/durable action gate OPEN | Sol/Luna/Root/operator, P5-A2 approval lifecycle |
| G13 | Pure chronology, SQL roundtrip and inert failure probes ACCEPTED; scheduler/auth/outage/recovery drills OPEN | Sol/Root, P5-A2 integrated drills; P5-C resilience |
| G14 | Applicable real-provider governance proof HELD | Root/operator, separately admitted P5-A2 REVIEW proof |

P5-A/P5-A2 and Phase5 0/5 remain OPEN. P5-B dashboard/search/observability,
P5-C backup/restore/resilience/security/performance, P5-D deployment/runbook/
ShadowMode/release retain roadmap owners/destinations. Root accountable,
Sol backend/contracts, Luna UI, operator business acceptance. Supporting
Docker tranche reaches its finite outcome; no new supporting survey/retry.
Next governed product move is G04–G06 query/cohort/completeness/coverage/
retention/snapshot/cap SPEC/WO, not an implementation grant or operational claim.
No backend remains running after this disposable test. Current result is
accepted locally; normal evidence material, terminal review, dedicated actualSHA
continuity and clean range remain necessary before bounded FREEZE/closure.

### Sanitized observed runner result

```json
{
  "docker_server_version": "29.9.2",
  "psycopg_version": "3.3.4",
  "image": "postgres:16-alpine",
  "image_id": "sha256:f4610795587492cd4fb887c2dc3de301b813278bb6f616992061141b5f15ac36",
  "container_name": "cvf-pg-live-90742cad83c4",
  "host_port": 59088,
  "container_image_id": "sha256:f4610795587492cd4fb887c2dc3de301b813278bb6f616992061141b5f15ac36",
  "server_version": "16.15",
  "migration_files": [
    "001_foundation.sql",
    "002_tasks_customers_reports.sql",
    "003_users.sql",
    "004_approval_receipts.sql",
    "005_incidents.sql",
    "006_handovers.sql",
    "007_report_history_constraints.sql",
    "008_shift_assignments.sql",
    "009_customer_request_version.sql",
    "010_integration_edge.sql",
    "011_p4e_identity_conversation_routing.sql"
  ],
  "migrations": [
    {
      "attempt": "first",
      "applied": 46,
      "skipped": 0
    },
    {
      "attempt": "reapply",
      "applied": 42,
      "skipped": 4
    }
  ],
  "target_returncode": 0,
  "target_tail": ".                                                                        [100%]\n1 passed in 1.37s\n",
  "anonymous_volumes_captured": [
    "117fa785e907ca7f1c419d1a1d3382ec16f310329ee5feca50f08937e8edff50"
  ],
  "anonymous_volumes_still_present": [],
  "container_absent_after_cleanup": true,
  "failure": null
}
```

## Post-result mandatory gate stop — 2026-10-26 local time

BLOCKED_RENEWED_REFERENCE_DRIFT. After actual SQL result verification, mandatory
inheritance preflight observed private HEAD bc921d2bf4429bca2a07d0261b5006f970d0da81
versus project/rulepack pin d3b2f73ca0746978673c649ed407974a1d1772a5.
Binding violations1; no result material commit/full commit hook attempted.
Previous accepted source/effect receipts remain evidence of their actual run;
this stop forbids bounded closure/FREEZE, new dispatch, retry or in-tranche
reference chase. Public/private references were not modified. Last committed
HEAD remains7fd67f5; result receipt/review/continuity changes are LOCAL_UNCOMMITTED.
This top-level blocked disposition supersedes the earlier next-commit intention;
actual synthetic SQL outcome stays PASS_BOUNDED, product milestone stays OPEN.

A separate metadata preflight also retained KPK_DATE errors after using local
2026-10-26 for reviewedAt while the checker clock is UTC2026-10-25. Session-sync
corrects knowledge review dates to actual UTC date2026-10-25 without changing
any guard. This date correction does not resolve provenance drift. Source and
actual SQL are unchanged. No additional effect or provider call was made.

Root SESSION_SYNC_STEWARD records the blocker and stops. The next permitted
move is controlled reference-binding reconciliation in its owning workflow,
then current continuity rehydration/inheritance before normal result material,
terminal review, dedicated actualSHAcontinuity and clean committed closure.
No automatic refresh, successor support tranche or package/container rerun.

## Operator-corrected Core binding / carried result disposition

The operator clarified the architecture and explicitly ordered correction on
2026-10-26: project inherits installed pinned workspace Core, never direct
privateHEAD/sharedpack/frameworkcontinuity or latestremote. Independent Core-only
SPEC/source/config REVIEW_PASS_BOUNDED after F1/F2 repair preserves actual native
controls and normalhook; installedordinaryadapter now0 even with newer upstream
refs. Earlier drift stop remains historical evidence, superseded by the accepted
controlled architecture correction, not by repinning/chasing provenance.
Carried SQLreceipt SHA1c2eefad2bfae0ab2e77a4bdf2bc0e7115b189a1440d8e37ee58e4d2e41d5a6f,
SQLsource/oracle/rawsummary pins remain unchanged and are consumed, not rerun.
Current result/source disposition PASS_BOUNDED, findingsNONE/waiversNONE;
normal resultmaterial/terminalreview/dedicatedactualSHAcontinuity/cleanrange
still gate closure and are owned by active Core-binding handoff. All effect
ceilings remain SPENT, no renewed worker effect or AI-governance proof. G04/G05/
G13 fixture portions only; G06/operational/wholemilestoneOPEN,Phase5 0/5.
