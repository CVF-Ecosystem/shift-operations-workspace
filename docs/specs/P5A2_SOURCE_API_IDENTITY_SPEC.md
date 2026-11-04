# P5-A2 G06/G11 — source API identity contract

Status: REVIEWED_CONTRACT_ONLY
Date: 2026-10-26; risk R2. Owner: Root SPEC_AUTHOR.
Source baseline: dcaca2c02dfdb012cc55b16907b7c6f31fecf305.
This tranche delivers audited INTAKE/DESIGN/SPEC only. It grants no runtime
BUILD, provider call, database/container operation or production acceptance.

## Product Milestone Binding

Milestone: P5-A2, docs/implementation/EXECUTION_ROADMAP.md Phase 5, at the
baseline above. Full acceptance remains P5A2_PROACTIVE_REPORTING_SPEC.md:
an authorized operator inspects integrated scheduled signals/forecasts,
history, lineage, freshness, uncertainty and abstention; a human approves the
exact run/version/source digest before any durable recommendation/action.
The operator owns business acceptance. Root owns contracts/dispatch/commit;
backend owns future implementation, independent REVIEWER owns acceptance;
UI owner and operator own application/business remainders.

| Gap | Current evidence and remaining requirement | This tranche / owner and destination |
|---|---|---|
| G01/A7 | Retained one real provider401, no accepted A7 proof | NO; Root/operator, P5-A A7 then P5-A2, BLOCKED |
| G02 | Operational governed RAG/context/index/citations unproved | NO; backend/Root, P5-A2 context, BLOCKED |
| G03 | Pure metric/horizon accepted; business/cohort fit open | NO; backend/operator, P5-A2 metric acceptance |
| G04 | Pure, Stage A and Stage B synthetic native SQL accepted; operational history/integrated source open | Contract only; backend/Root, P5-A2 source integration |
| G05 | Fixture coverage/RR accepted; production coverage/retention and positive SQLite UNKNOWN | Refusal boundary only; backend/Root/operator, P5-A2 coverage |
| G06 | Native assignment/caps/fresh query accepted; API identity/use-time access open | YES contract only; backend/Root, P5-A2 source API |
| G07 | Scheduler/claim/lease/recovery open | NO; backend/Root, P5-A2 runtime |
| G08 | Pure signals accepted; operational false positives open | NO; backend/operator, P5-A2 signals |
| G09 | Pure forecast accepted; operational accuracy open | NO; backend/operator, P5-A2 forecast |
| G10 | Pure residual/drift accepted; monitoring/display open | NO; backend/UI/Root, P5-A2 quality and P5-B |
| G11 | Source function internal; no proactive route/UI | YES source-read API contract only; backend/UI/Root, P5-A2 application |
| G12 | Exact human recommendation approval open | NO; backend/UI/operator, P5-A2 approval |
| G13 | Pure/fixture SQL failure cases accepted; integrated runtime drills open | Contract test plan only; backend/Root, P5-A2 drills |
| G14 | Live AI governance proof deferred | NO; Root/operator, separately admitted P5-A2 REVIEW, HELD |

P5-B dashboard/search/observability: backend/UI/Root. P5-C backup/resilience/
security/performance: backend/Root/operator. P5-D deployment/Shadow Mode/release:
Root/operator. Phase 5 remains 0/5. No whole gap or milestone closes here.
Support stop: one source audit, one bounded contract and independent review;
return to a separate implementation Work Order. Unknown production coverage
never becomes fixture authority or a reason to expose an unverified success.

## Accepted input and source truth

Stage B result cad8ffc1e60a2ee753fb714e4336016e67634834 and continuity
0b7f870585d3ef9996b0cff1ab8b943a7d4b739f are accepted bounded: synthetic
PG16.15 target 1PASS31.18s, both full frozen contexts, six500/501 cases,
RR/read-only, four writer refusals and independent owned cleanup. No standing
backend remains; all previous physical/provider attempts remain spent.
The installed catalog kit changes documentation paths, not API capability.

Current query_source trusts an internal Principal/TrustedSourceScope and
returns SourceQueryResult(receipt, payload). It is not an authentication API.
The SQL filter is actor ACTIVE assignment plus shift-end window; a scope label
alone does not constrain the database. Coverage=None refuses before source IO.
Existing get_principal does not require exp; get_principal_with_expiry does.
The new route must not inherit the weaker claim assumption or trust client IDs.

## R1 — Small observable outcome and route

Proposed GET /proactive/source returns only the existing bare native source
receipt for the authenticated actor's complete self-assigned window. It adds
no forecast calculation, report body, HistoryInput serialization, durable run,
recommendation, approval, scheduler, UI, export or operational write.
With current operational coverage it is a refusal-only diagnostic, not an
integrated reporting feature. This contract does not dispatch that endpoint.

Request query keys are exactly query_start, query_end, run_as_of, each once.
No actor/role/scope/instance/shift/report/assignment/source IDs, fixture selector,
complete/coverage assertion, policy override, cursor or client digest is accepted.
Nonempty bodies, duplicate/unknown query keys and malformed timestamps return
generic 422 after authentication; never echo values, body or validation input.
Timestamp strings are bounded to 128 characters; total query bytes <=2048.
Offset-aware UTC normalization is mandatory; start < end <= as_of <= server UTC
clock. Naive timestamps map to native TIME_AMBIGUOUS; invalid ordered/future
windows map to native INVALID_WINDOW, without reading source bodies.
Framework validation must not precede the strict identity dependency: absent,
invalid or expired authentication plus malformed query still returns 401.
OpenAPI declares the request and both receipt shapes without allowing a second
runtime parser or schema drift. The implementation WO must bound its files.

## R2 — Identity, current user and permission

Use get_principal_with_expiry; require a real signed bearer token with valid,
finite exp. Never use X-User-Id/X-User-Role or query/body identity. Use the
existing server signing/test machinery; no real credential acquisition or .env
edit is authorized. Missing/invalid/expired token returns fixed 401 detail
"Authentication required" with no token decoder exception in the response.

Read current user by verified sub using the request's ledger. Missing/inactive
user or current stored role not equal to token role returns fixed 403 detail
"Access denied" before coverage/source diagnostics. Reuse canonical
require_action for a separately registered proactive.source.read at viewer bar;
no endpoint-local rank table and no executive/manager assignment bypass.
Unknown action fails closed. This is a deterministic API access contract,
not evidence that CVF controls AI or a provider-backed permission claim.

Recheck token expiry, current user activity/role and action permission at the
last application release point. If changed, discard every source-bearing field
and return the same fixed 401/403. Storage exceptions must not leak SQL/DSNs.
Global login, JWT issuance/refresh/revocation and unrelated routes remain outside
this contract. These checks do not promise atomic authorization until transport
delivery or replace future run/use/approval-time revalidation in G06/G12.

## R3 — Server scope and assignment boundary

Server configuration supplies one nonblank instance identity (max128 ASCII)
bound to the composition's single request ledger. Default is unconfigured and
refuses SOURCE_UNAVAILABLE; no process random value, app-name fallback, client
header, database URL or secret becomes an instance identifier. No multi-tenant
or cross-workspace database claim follows from this single-workspace contract.

Build TrustedSourceScope only inside server composition. actor_id is verified
sub; instance_id is that configured identity; both policy versions are the
accepted server constants. scope_id is P5A2-SELF- plus lowercase SHA256 of
canonical JSON over exactly {instance_id, actor_id, cohort_policy_version}.
Use UTF8 sorted keys, compact separators, no NaN; never client supplied labels.
Bind trusted coverage to this exact scope/instance/window/policy context.

After identity/permission and valid window, obtain a bounded metadata-only
cohort probe through the native scoped_source_read for that actor/window.
No list_shifts/all-user scan, client-selected subset, report-body load or new
selector is allowed. Empty cohort returns bare SOURCE_REFUSED/ACCESS_DENIED
before consulting coverage; >500 refuses SCOPE_INCOMPLETE with zero bodies.
Unavailable snapshot returns the existing closed native refusal.
The authoritative query then reuses query_source unchanged; its own snapshot,
caps, lineage and fresh cohort checks remain required. A probe does not prove
completeness or substitute for the authoritative query's independent snapshot.

Before releasing a source result, revalidate complete current membership in a
new current view. For READY compare every eligible shift/end/assignment ID and
version to the validated receipt manifest; revoked prior member is ACCESS_DENIED,
changed/additional/boundary membership is SCOPE_INCOMPLETE. Never selected IDs
alone. On refusals after a successful probe, recheck its enrolled cohort before
release so a revocation cannot be hidden by COVERAGE_UNKNOWN. No data-bearing
receipt or payload survives a failed recheck. Use existing native fresh ports;
unsupported backend capability refuses rather than inferring a fresh view.

## R4 — Coverage, response and confidentiality

Normal composition has no accepted operational CoverageVerifier: default None.
An identity-valid, assigned, configured request therefore returns the native
closed COVERAGE_UNKNOWN refusal; unassigned callers receive ACCESS_DENIED first.
The route must not auto-install a fixture verifier, infer retention from counts,
load test oracles at runtime or enable success through a query/header/env flag.
Positive synthetic tests may explicitly inject server-owned test dependencies,
with the unchanged frozen fixture authority. They prove composition only.
The current native emitter, validator and registered family accept only
coverage_mode=SYNTHETIC_FIXTURE. Adding an operational coverage resolver alone
cannot authorize operational READY. Such a future outcome requires a separately
reviewed native coverage-mode/receipt/family/emitter/validator contract and its
source-authority evidence before API work can consume it. That work is outside
this planning packet and cannot silently rename a fixture receipt as operational.
The explicit historical run_as_of query is allowed only under the server clock
bound in R1; it never grants historical rather than current assignment access.

HTTP200 body is exactly one validated existing SOURCE_READY/SOURCE_REFUSED
receipt, with no envelope, extra success flag, payload, source bodies, raw
exception or added public outcome. Other native reason precedence follows the
accepted source SPEC; identity/permission failures use fixed 401/403 transport
bodies above. Malformed request uses fixed {detail: "Invalid request"} 422.
Unexpected source/composition failures become closed SOURCE_UNAVAILABLE after
denial precedence. No success can be inferred from HTTP200 alone.
Set Cache-Control: no-store and Pragma: no-cache on success and errors. No app
response cache, durable result/audit write, provider/network call or action.
An existing request-id header is transport metadata, not a new receipt field.
Every authorized JSON response is bounded to 1048576 UTF8 bytes. Use bounded
incremental encoding before sending headers/body; never truncate or expose a
partial manifest. A READY receipt exceeding this transport budget is discarded
and replaced with closed SOURCE_REFUSED/SCOPE_INCOMPLETE, after the same final
access recheck. This proposed extra API refusal condition must be covered by the
future reviewed family/HTTP binding in R5; it does not change the native emitter.
The receipt itself contains sensitive manifest IDs; it is not a small or public
summary. Test exact byte boundary/overflow and zero emitted success prefix.

## R5 — Invariant applicability and future implementation gates

Follow docs/cvf/INVARIANT_FAMILY_STANDARD.md. Existing family
P5A2-SCOPED-SOURCE-OUTCOMES, canonical9b3ba818e647d228e453706fac1378a69388bbae7b1a02d81732e64d939d5d4c,
owns both native receipt shapes. No new business outcome/envelope is proposed.
This INTAKE/SPEC packet does not edit that matrix, existing emitters or pins.
HTTP exposure is a new representation/consumer: BEFORE future BUILD, a separate
bounded WO and independent review must cover its HTTP representation, strict
response adapter, ownership/parity evidence and updated family/consumer pins.
The matrix stays semantic owner; do not copy its field rules into a route model.
Existing frozen source/body/PG oracles and numeric/cohort contracts stay intact.
No positive SQLite, production coverage or fresh PostgreSQL API proof is inherited
from the old SQL-only run. Any new physical experiment needs its own authority.

Future acceptance must exercise real JWT verification, current stored users,
canonical action and native source adapters (no bypassed principal dependency):
1. Missing/bad signature/expired/missing or malformed exp, including malformed
   query alongside each denial: 401; no source or coverage access.
2. Spoofed header/query/body actor/scope, duplicates/unknown keys, inactive or
   role-changed/missing user, privileged unassigned user: fixed denial/no leak.
3. Identity-valid assigned request with no coverage: exact COVERAGE_UNKNOWN;
   configured vs unconfigured composition and unavailable backend are explicit.
4. Independently freeze two complete NEW API expected receipts BEFORE future
   implementation from the known old fixture inputs and the R3 server context.
   The new scope replaces old PUBLIC_SCOPE in coverage seeds/manifests and
   changes their coverage/source digests; literal equality to the old complete
   receipts is impossible. Freeze those new seeds/manifests/digests independently
   of the future route/loader, then compare complete new receipts, not digests
   alone. Preserve exact old body bytes, selected report lineage, as-of selection
   and numeric facts; old source/body/PG oracles remain unchanged. Synthetic
   positive evidence remains explicitly SYNTHETIC_FIXTURE.
5. Changed/revoked/added assignment, window-boundary move, user disable/role
   change and token expiry between read and release discard all source fields.
6. Native 500/501 and closed-receipt mutation corpus; HTTP field parity and
   confidentiality, no cache, no provider call and zero ledger writes on every
   branch. Count equality alone is not coverage proof.
7. Carry old physical source evidence honestly; no Docker/provider rerun,
   deployment, browser/UI or whole-milestone acceptance from in-process tests.

Stop this tranche after independently reviewed contract, normal material commit,
terminal actual-range review, dedicated actual-SHA continuity and clean closure.
Next move is a separate G06/G11 work-order decision. Before any product route
dispatch, independently accept the bounded assignment resolver and a concrete
development/operator outcome; an operational READY route additionally requires
the separate native coverage-mode/receipt/family/emitter/validator evolution and
accepted operational source authority described in R4. If these are missing,
keep the route parked and return
to the named P5-A2 coverage/integration gap with its owner, rather than repeatedly
authorizing refusal-only support work. No automatic BUILD grant.
