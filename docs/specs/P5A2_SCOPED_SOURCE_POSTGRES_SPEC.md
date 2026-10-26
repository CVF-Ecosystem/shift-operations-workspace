# P5-A2 Stage B — physical scoped PostgreSQL source proof

Status: IMPLEMENTED_BOUNDED_PHYSICAL_SOURCE_PROOF
Date: 2026-10-26; R2. Root SPEC_AUTHOR/WORK_ORDER_AUTHOR.
User `next` continues the named Stage B. No provider/operational-data action.
Inherit accepted source SPEC db1d2180, runtime family9b3, and Stage A source
material a7374f86 / continuity8dc39e1, exact31+5 clean closure. Enter DESIGN /
SPEC / WORK_ORDER for this new finite experiment; earlier numerical/cohort
contracts are not reopened. Independent review gates source BUILD and effect.

## Product Milestone Binding

Milestone P5-A2 at baseline8dc39e119e4c343a18c2f16375448eebf22467bf,
docs/implementation/EXECUTION_ROADMAP.md Phase5. Full user outcome: integrated
authorized scheduled signals/forecast/history/lineage/freshness/uncertainty/
abstention, then human approval of exact run/version/source digest before any
durable recommendation/action. The complete milestone acceptance remains the
parent P5A2_PROACTIVE_REPORTING_SPEC.md and source SPEC; operator owns business
acceptance. This assignment closes only physical fixture-query proof portions
of G04–G06 and partial G13, not entire criteria or milestone. Root accountable,
WO/oracles/effect/commit; backend IMPLEMENTATION_WORKER owns harness; independent
REVIEWER assesses source and result; UI roadmap owner and operator own remainders.

| Gap | Current truth / remaining destination and owner | This slice |
|---|---|---|
| G01/A7 | one provider401; P5-A A7 then P5-A2, Root/operator BLOCKED | NO |
| G02 | operational RAG/context/index/auth/citations unproved; P5-A2 context, backend/Root BLOCKED | NO |
| G03 | pure metric/horizon accepted; business/cohort fit open; P5-A2 metric, backend/operator | NO |
| G04 | pure + old PG36/37 + StageA memory + StageB physical scoped SQL fixture accepted; operational history completeness/integrated source remain open; P5-A2 source backend/Root | fixture PG accepted |
| G05 | pure/old PG aware fixture + StageA refusal + StageB physical fixture/RR accepted; production coverage/retention/SQLite positive UNKNOWN; P5-A2 coverage backend/Root/operator | fixture PG accepted only |
| G06 | current assignment + StageA memory/caps/freshness + StageB physical SQL/fresh writer refusal accepted; API identity/use-time access open; P5-A2 security/API backend/Root | internal PG accepted only |
| G07 | scheduler/claim/recovery open; P5-A2 runtime backend/Root | NO |
| G08 | pure signals accepted; operational false positives open; P5-A2 signals backend/operator | NO |
| G09 | pure forecast accepted; operational accuracy open; P5-A2 forecast backend/operator | NO |
| G10 | pure calibration/drift accepted; monitoring/display open; P5-A2 quality/P5-B backend/UI/Root | NO |
| G11 | API/UI/history/freshness open; P5-A2 application backend/UI/Root | NO |
| G12 | exact human approval open; P5-A2 approval backend/UI/operator | NO |
| G13 | pure/oldSQL/StageA source failure accepted; integrated runtime drills open; P5-A2 drills backend/Root | physical source only |
| G14 | real-provider governance HELD; P5-A2 separately admitted REVIEW Root/operator | NO |

P5-B dashboard/search/observability remains backend/UI/Root; P5-C backup/
resilience/security/performance backend/Root/operator; P5-D deployment/Shadow
Mode/release Root/operator. Phase5 stays0/5. Unknown production coverage is
not a dependency for synthetic fixture proof: default resolver must refuse.
Return after one reviewed experiment/result to next integrated P5-A2 gate;
no repeated support survey or automatic additional effect.

## Frozen independent expectations and native scope

New pre-harness oracle tests/fixtures/p5a2_scoped_source_pg_oracle.json rawSHA
0b69156fcb09a6b65a25c437320a5f4001f4068284d5bcf8b88438700a92f44f.
Root authored it from accepted contracts before the new harness exists. It pins
old full source oracle0f79676b and body oracle12ad36cb. Do not generate expected
results from a new loader. StageA/pure/oldrunners/oracles/sourcefamily stay read-only.
Executed helpers, pure/domain owners and all migration bytes are pinned in the admission JSON. Before effect require clean tracked worktree and no inherited application/package/database source change from baseline8dc39e1; only the five new admitted harness files and exact Root metadata/receipt paths may differ. Revalidate pins in child before seeding; runtime marker/observation are the only extra admitted transient artifacts.

A. Seed native SqlLedger with synthetic users, exact ACTIVE assignments and
36 shifts/37 immutable reports matching source oracle0f. Invoke actual
query_source with trusted internal Principal/context and harness-only fixture
verifier. Both initial_asof36/later_asof38 FULL receipts, selected lineage and
unchanged analyze output match frozen oracle. Compare loaded immutable content
hashes to old body oracle; verify aware times and future correction exclusion.

B. Six disjoint cap fixtures have explicit index/actor/window/versions in new
oracle: valid500 and refusal501 for eligible shifts, total candidate versions,
and per-candidate incident refs. Native persisted version history has exactly
one current report per shift. Seed expected membership/candidate metadata and
canonical coverage digest BEFORE query from known fixture inputs, independently
of new reader output. Actual SQL/native load_reports spy and statement trace
prove ZERO body fetch/construction on501; full500 cases yield SOURCE_READY.
No filtered foreign body or superseded large candidate can evade preflight.

C. Reportless enrolled shift refuses SCOPE_INCOMPLETE; absent production
coverage refuses COVERAGE_UNKNOWN. Foreign ACTIVE assignment/501-ref or malformed
report is INSIDE the baseline query time window and belongs to another actor,
so a missing actor filter cannot hide behind time filtering. Baseline full
oracle still matches; foreign report body never reaches materializer.

D. Actual source unit reports SHOW transaction_isolation=`repeatable read`
and SHOW transaction_read_only=`on`; trace same source connection/transaction
for cohort/candidate/scalar-preflight/body. Independent physical writer commits
assignment version2 while source snapshot is open: reread inside same unit
still version1, a NEW current view sees2. Record backend/transaction identity,
not passwords/DSNs. No fake query rows or mocked driver results in physical proof.

E. Four separate physical writer thread/transaction+bounded barrier cases after
source unit is sealed and before actual native fresh view: revoke→ACCESS_DENIED;
assignment add/version bump/Shift.ends_at enrollment move→SCOPE_INCOMPLETE.
Source/fresh/writer identities and committed mutation are observed. No sleep-only
ordering, no selected-IDs-only freshness shortcut. Refusals are exact closed
native family objects, no payload/IDs/counts/manifest/digest. Only READY may
reach pure analysis. These internal tests do not authenticate a public API.

## Bound run, fencing and cleanup

Read-only readiness on2026-10-26: Docker29.9.2, installed psycopg3.3.4 and cached
postgres:16-alpine image sha256:f4610795587492cd4fb887c2dc3de301b813278bb6f616992061141b5f15ac36.
No pull/install or container was performed during planning. One NEW experiment,
not reuse/reset of old spent substrate ceilings. Final sealed admission maxONE
wrapper invocation, ONE owned container, ONE comprehensive pytest target call.
Atomic O_EXCL attempt marker is write-once/spent, including failed run; no retry.

Use native lifecycle/readiness/migration001–011 reapply/cleanup helpers read-only.
Loopback dynamic port, random ephemeral local DB password only; no ambient
DB URL, .env, API key, real credential, provider/network install or CSV. Never
call base.ensure_image (it may pull), nor inherit tag-based base.start_container unchanged. New creation command MUST use --pull=never and the exact admitted cached image ID (not mutable tag). Inert command assertion must prove both; old runners stay unchanged. Minimal child environment strips all
provider credentials. New opt-in target requires runner-created owned context,
matching admission/marker/nonce/container identity/image/hostport and fixed local
DB/user; ambient LIVE_POSTGRES_DATABASE_URL alone cannot activate it. Paths stay
in project and fixed observation path; no arbitrary target/URL/force override.

Capture created container identity and anonymous volumes; finally remove ONLY
that owned container and its captured volumes. Never delete a pre-existing or
uncertain resource; unknown ownership/cleanup is FAILURE, not absent/success.
Independently verify named container and captured volumes absent afterward.
Image/driver caches remain. Sanitize every failure/tail/observation; no full DSN
or generated password in committed evidence. Record partial failures honestly.
If code/SQL fails during physical run, retain spent receipt and stop; no automatic
source change/retry under old budget. StageB acceptance requires independent
source/effect admission, committed sealed source plus dedicated continuity,
actual result and cleanup review, normal result commit and actual-SHA continuity.

## Invariant applicability and limits

Reuse P5A2-SCOPED-SOURCE-OUTCOMES canonical9b3ba818e647d228e453706fac1378a69388bbae7b1a02d81732e64d939d5d4c
under docs/cvf/INVARIANT_FAMILY_STANDARD.md. Existing native emitter/validator/
84-mutation corpus remains unchanged and must pass; physical SQL is supplemental
backend evidence, not a new representation/receipt contract or matrix change.
No new family: new harness reuses legacy experiment-summary format, its attempt
reservation is immutable (no lifecycle/counter schema), and case observations
are evidence-only references to native source outcomes and frozen test inputs.
Independent reviewer must accept this applicability decision; if a shared result
contract is introduced during BUILD, stop for contract review before adding it.
No AI governance, production retention, forecast accuracy, API, scheduler, human
approval or release claim follows from synthetic SQL success.

## Actual bounded acceptance

Independent PHYSICAL_RESULT_REVIEW_PASS_BOUNDED: one PG16.15 comprehensive target1PASS31.18s; both full frozen baselines, six500/501 cases, negatives/foreign exclusion, actual RR/read-only1→1→2 and four post-seal writer refusals accepted. Migrations46/0→42/4; owned container/volume independently absent. Exact durable evidence docs/decisions/P5A2_SCOPED_SOURCE_POSTGRES_EVIDENCE_2026-10-26.json embeds observation rawSHAeae18ef1. AttemptSPENT/no retry; no standing backend. Resultmaterial/terminal/dedicatedactualSHAcontinuity/cleanrange still gate tranche closure. No production/API/scheduler/approval/AI claim or milestone closure.
