# P5-A2 G06/G11 — bounded source API implementation

Status: SOURCE_API_IMPLEMENTATION_CONTRACT
Date: 2026-10-26. Root SPEC_AUTHOR/WORK_ORDER_AUTHOR; R2.
Baseline59d63c66ce170ede7259c67a4f770d96e623f921. Inherit the accepted
P5A2_SOURCE_API_IDENTITY_SPEC.md at planning123d677/dedicated59d63c6.
Operator now explicitly requests continued roadmap execution across tranches;
independent Work Order admission, committed dispatch and continuity still gate BUILD.

## Product Milestone Binding

P5-A2 at docs/implementation/EXECUTION_ROADMAP.md Phase5. Complete user outcome:
integrated authorized scheduled signals/forecasts/history/lineage/freshness/
uncertainty/abstention, followed by exact human run/version/source approval
before durable recommendation/action. Full acceptance remains parent proactive
SPEC; operator owns business acceptance. Root accountable/contracts/effects/
commit, backend worker implementation, independent reviewer acceptance,
UI owner/operator application/business remainders.

| Gap | Current truth and remaining work | This slice / owner / destination |
|---|---|---|
| G01/A7 | One provider401 spent; A7 acceptance BLOCKED | NO; Root/operator, P5-A A7 then P5-A2 |
| G02 | Operational RAG/context/index/citations BLOCKED | NO; backend/Root, P5-A2 context |
| G03 | Pure numerical policy accepted; business fit open | NO; backend/operator, P5-A2 method |
| G04 | Native fixture memory/PG source accepted; operational integration open | HTTP composition only; backend/Root, P5-A2 source |
| G05 | Fixture coverage accepted; production mode/authority/retention/SQLite positive UNKNOWN | Default refusal only; backend/Root/operator, P5-A2 coverage |
| G06 | Native assignment/fresh view plus identity contract accepted; API absent | YES bounded source-read identity/release; backend/Root, P5-A2 API |
| G07 | Scheduler/claim/recovery open | NO; backend/Root, P5-A2 runtime |
| G08 | Pure signals accepted; operational quality open | NO; backend/operator, P5-A2 signals |
| G09 | Pure forecasts accepted; operational accuracy open | NO; backend/operator, P5-A2 forecasting |
| G10 | Pure residual/drift accepted; monitoring/display open | NO; backend/UI/Root, P5-A2 quality/P5-B |
| G11 | Accepted source API contract; no mounted route or UI | Source-read route only; backend/UI/Root, P5-A2 application |
| G12 | Exact human approval open | NO; backend/UI/operator, P5-A2 approval |
| G13 | Native fixture failures accepted; integrated drills open | HTTP auth/release/transport only; backend/Root, P5-A2 drills |
| G14 | Live AI-governance proof HELD | NO; Root/operator, separately admitted P5-A2 REVIEW |

P5-B dashboard/search/observability: backend/UI/Root; P5-C backup/resilience/
security/performance: backend/Root/operator; P5-D deployment/Shadow Mode/release:
Root/operator. Phase5 stays0/5; no whole milestone or entire gap closes here.

Concrete outcome and necessity: the authenticated application caller can inspect
its assigned source readiness or an exact nonleaking refusal through HTTP,
forming the missing G11 caller boundary for the next source-inspection UI.
Real signed JWT/current users/native cohort ports replace an internal-only
function seam. This is a finite product integration, not another source survey.
Normal coverage remains unavailable: a refusal diagnostic is not an operational
report. Positive fixture HTTP evidence is explicit test-only composition.
Stop after accepted route/source tests, normal source closure, then return to
G11 UI/application integration under a separately reviewed bounded work order;
do not loop through extra support surveys or ask for routine tranche approvals.

## Acceptance inherited from the frozen identity contract

Implement R1–R5 of P5A2_SOURCE_API_IDENTITY_SPEC.md without rewriting its bytes.
GET /proactive/source has exactly three timestamp query keys, strict verified
JWT expiry, fixed401/403/422 bodies after denial precedence, current stored
activity/role/action before input diagnostics and again at final release.
Server-only single-instance self scope, native bounded metadata-only cohort
probe before coverage, unchanged query_source, complete fresh membership after
read/encoding; no caller-controlled actor/scope/source/coverage/policy.
No privileged role bypass, whole-shift scan, report body or HistoryInput on HTTP.
No source cache, audit/durable/operational write, provider or network call.
All response branches use no-store/no-cache; 1MiB actual UTF8 response cap.
Use bounded incremental encoding; overflow discards success and becomes native
SCOPE_INCOMPLETE after the final identity/membership check, with no sent prefix.

The already accepted native scoped_source_read/fresh_scoped_cohort ports are
the bounded resolver, with at most501 metadata rows. Source SQL filtering and
snapshot behavior are inherited only at their previously proved revision;
in-process HTTP tests do not assert a new physical API/PG run or load guarantee.
Memory fixture work does not establish operational retention or SQLite success.

Freeze two complete NEW API receipts in tests/fixtures/p5a2_source_api_oracle.json
BEFORE API code exists. Independent author Luna/SPEC_AUTHOR used old immutable
fixture data, stdlib JSON/deepcopy/hashlib only; Root independently verified the
full transform. RawSHA5cc32b1a0484460c7eafb8d23d7112f19ae713699dfd560bb98c4b00411e49fe.
New server scope P5A2-SELF-bb627a60d0a68fcad8ad334af063da3c1a5d7edb60951ea54a2fe9cd8d074d8a;
old source/body/PG oracle bytes remain unchanged. Compare complete new receipts,
old exact selected lineage/content facts and native refusal shapes, not digests
alone. No expected value may be derived from new implementation output.

## Composition and responsibility boundaries

New application access helper owns current-user/action/clock/server-scope checks;
new preview helper owns metadata probe, authoritative native query and final
release context. API router owns strict dependency normalization and raw bounded
request parsing; response adapter owns native receipt validation, bounded JSON,
headers and structural OpenAPI projection. Reuse existing strict JWT dependency
and canonical require_action; add only proactive.source.read at viewer level.
Do not refactor global login/tokens or unrelated routes. New server instance
setting defaults blank; new context dependency defaults coverage None and never
loads fixture JSON at runtime. Invalid/unconfigured instance refuses rather than
falling back to app name/random/DSN/client data. Tests may replace context/clock
dependencies, never the principal verification boundary.

Final release checks run after building the bounded response buffer and before
returning headers/body. Store only receipt and bounded access context across
that boundary; HistoryInput never reaches the HTTP serializer. For READY compare
complete current cohort metadata to validated receipt membership; for refused
reads compare to the successful preflight cohort so revocation cannot hide behind
COVERAGE_UNKNOWN. Expired/disabled/role-changed identities discard all fields.
New source failures become closed SOURCE_UNAVAILABLE; token/permission errors
remain fixed401/403. No raw decoder/driver exception or input value is echoed.

## Invariant-family binding and staged materialization

Follow docs/cvf/INVARIANT_FAMILY_STANDARD.md. Existing registered
P5A2-SCOPED-SOURCE-OUTCOMES owns native READY/REFUSED; all shape fields, domains,
relations and mutation rules remain unchanged. Add HTTP_JSON representation,
APPLICABLE parity, identity/build SPEC contract sources and a real HTTP consumer
digest binding/evidence tests. The 1MiB API-only SCOPE_INCOMPLETE mapping is
defined by the accepted API identity contract, not a new business outcome.
OpenAPI is a structural projection; runtime acceptance reuses the existing
native validator, not copied route-local validation rules or fixture imports.

Root freezes a recoverable exact metadata-only matrix patch and final canonical
digest in the committed admission BEFORE worker BUILD. The full candidate is
reproducible from the pinned old matrix plus this patch; independent reviewer
reviews actual proposed contents, consumer/test paths and pin updates.
The current registered matrix remains active for dispatch because future files
do not exist yet; never create fake placeholder tests to satisfy its guard.
Worker writes only authorized new source/test paths, then STOPS before any
focused tests. Root installs only the preapproved patch and existing two pin
updates once real consumer/evidence files exist. Independent reviewer verifies
exact final digest/bytes, actual consumers/pin symbol, native/generic guards and
real test/mutation binding. Only then may worker resume tests/repairs/return.
Any semantic/path deviation returns to review before mutation; never silently
change the frozen patch or oracle. Root owns those matrix/pin operations.

## Required source evidence and limits

Use real TestClient HTTP and existing real signing/verification code with the
repository test secret only. No principal dependency bypass, mocked JWT decode
or fabricated native query result as acceptance. Seed current User records and
native in-memory assignments/reports before read-only assertions; fixture
authority validates the pre-frozen new coverage seed. No live provider claim.

Cover both positive contexts and all native family mutations across native and
actual HTTP/response consumers; raw positive/refused bodies and every outcome's
field presence/counter relations must match the family. Retain the native84
mutation corpus and old source tests. Test bad/missing/expired/missing-exp token
plus malformed input, role/activity changes and spoofed headers; unknown/duplicate
keys/nonempty body/query-byte bounds; aware/naive/future/malformed timestamps;
unassigned actor at every role; unconfigured instance and no accepted coverage;
501 preflight zero body reads; revoked/added/version-changed/boundary-moved
assignments between native seal and final release; user/expiry changes then;
exact1MiB and overflow/UTF8/no-prefix confidentiality; no-store on every branch,
OpenAPI field parity, unsupported source capability, sanitized read failures,
zero ledger writes and zero provider calls. Inert spies/barriers may observe
native calls and mutate independent fixture state; do not replace outcomes.

No new PostgreSQL/Docker, provider API, key/model/.env, package install, deployment,
production dataset, public release or browser session in this source tranche.
Old physical/provider attempts are spent and remain immutable. Operational READY
still needs separate native coverage-mode/receipt/family/emitter/validator and
accepted operational authority; this WO does not authorize that evolution.
Normal precommit full tests, catalog-detail→kit projection→manager generation,
session/file-size/knowledge/invariant guards and independent source review are
mandatory; all executable files <=300 lines. Source closure follows normal
material, terminal actual review, dedicated actual-SHA continuity and clean range.
