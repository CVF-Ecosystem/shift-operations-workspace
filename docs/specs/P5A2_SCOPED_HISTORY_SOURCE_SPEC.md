# P5-A2 G04–G06 scoped history source contract

Status: CONTRACT_CANDIDATE
Date: 2026-10-26 (Asia/Saigon)
Phase: SPEC; risk R2; SPEC_AUTHOR Root, independent review pending.
This contract grants no query/adapter BUILD, provider or database effect.
Core-only correction and carried SQL substrate closed bounded at material
`3de6c50e3f7932a1e79dba68c8dc21672a5d6579` / dedicated continuity
`7134f9eafbf2b19cbb8e24081d4b8bacecc3154b`; clean split-range verified.
Normal material/continuity hooks:3253passed147skipped4warnings220.78s/146.38s.
Installed public Core remains `aa672d11910ae1982557e4810a2a8002a611e9e6`.
Current business-source revision7134 is unchanged from the accepted audit;
old private-pin text inside frozen parent documents is historical only.
Parent SPEC/matrix, pure numerical code and36/37 SQL oracle remain read-only.


## Product Milestone Binding

P5-A2 user outcome: an authorized operator views integrated assignment-scoped scheduled signals and one-shift-ahead forecasts with history, lineage, cutoff, freshness, uncertainty and abstention, then a human approves the exact run/version/source digest before any durable recommendation/action. This contract closes, if independently accepted, **only the G04–G06 source-query/cohort/coverage/snapshot/cap contract**. It closes no implementation or whole gap. Root owns contract/accountability/commit; backend SPEC/worker owns query; independent REVIEWER evaluates; Luna owns UI per roadmap; operator owns business acceptance. Phase 5 remains 0/5.

| Gap | Evidence now; remainder and destination/owner |
|---|---|
| G01/A7 | One provider 401; blocked P5-A A7 decision then P5-A2 integrated gate — Root/operator. |
| G02 | Operational RAG corpus/index/auth/citations/application unproved — Root/backend, P5-A2 context gate. |
| G03 | Pure metric/horizon accepted; cohort/business fit open — Root/backend/operator, P5-A2 metric gate. |
| G04 | Pure as-of/digest and real synthetic PG versions/lineage accepted; scoped adapter open — backend/Root, P5-A2 source gate. |
| G05 | Pure time refusal and PG aware fixture accepted; operational retention/coverage and SQLite provenance unknown — backend/Root, P5-A2 time/coverage gate. |
| G06 | Current assignment primitives exist; exhaustive bounded authorized snapshot/revocation open — backend/Root, P5-A2 security/API gate. |
| G07 | Schedule/claim/recovery open — backend/Root, P5-A2 runtime gate. |
| G08 | Pure trend/anomaly accepted; false-positive operational review open — backend/Root/operator, P5-A2 signal gate. |
| G09 | Pure baseline/forecast accepted; operational accuracy/fit open — backend/Root/operator, P5-A2 forecast gate. |
| G10 | Pure calibration/drift accepted; operational monitoring/display open — backend/Luna/Root, P5-A2 quality and P5-B observability. |
| G11 | API/UI history/freshness open — backend/Luna/Root, P5-A2 application gate. |
| G12 | Exact run/version/digest human approval open — backend/Luna/Root/operator, P5-A2 approval gate. |
| G13 | Pure + synthetic SQL lineage proof accepted; integrated scheduler/failure/recovery drills open — backend/Root, P5-A2 drills. |
| G14 | Real-provider governance evidence held; no AI claim here — Root/operator, newly admitted P5-A2 REVIEW if applicable. |

P5-B dashboard/search/observability stays with backend/Luna/Root at roadmap P5-B; P5-C backup/restore/resilience/security/performance stays with Root/backend/operator at P5-C; P5-D deployment/Shadow Mode/release stays with Root/operator at P5-D. No remainder is absorbed by this slice.

## Native anchors and reviewed development decision

The accepted 20-file source audit is the finite source inventory; six focused bytes were rehashed today and match its pins: `assignment_scope.py` `0598284c...` lines23–49 checks current active assignment; `_shift_queries.py` `142fb0ab...` lines21–24 unbounded `.all()`; `_assignment_store.py` `2a815867...` lines179–242 active membership/revoke; `_report_store.py` `9b1c56f6...` lines152–285 history materialization; `proactive_history.py` `cad9546d...` lines15–43,97–154 pure validation/selection; `proactive_models.py` `f61fbbfc...` lines23–32,67–77 `HistoryInput`/pure policy. Native `Ledger`/`SqlLedger`, Report tables/immutable digest, authenticated `Principal`, `AssignmentScope`, accepted pure `select_history`/`analyze`, and existing migration-owned PostgreSQL are owners to reuse. This is not a complete repository survey.

D1 design decision for independent review: version the **dual-axis fixture cohort rule** separately from numeric policy. Development fixture policy `P5A2-COHORT-ENDS-1`: at one trusted read, eligible IDs are every currently ACTIVE-assigned Shift for verified `Principal.user_id` with aware `Shift.ends_at` in `[query_start, query_end)`, ordered UUID, including reportless shifts. `scope_id` is a server-owned query label bound to this principal/cohort and **never itself permission**. This makes reportless enrollment possible; selected END_SHIFT Report still must have `generated_from_cutoff` in the parent `[start,end)` and `created_at <= run_as_of`. If an enrolled shift has no selectable report, has a cutoff outside that window, or mixed policy, refuse `SCOPE_INCOMPLETE` rather than drop it or treat it as zero. Mutable Shift/Report `status` and `is_current` never choose historical versions. Assignment tenure, operational scope enrollment, business metric fit and retention authority remain UNKNOWN/BLOCKED until named operator/backend owner accepts evidence; no production `complete=true` from this fixture rule. Numeric `P5A2-INITIAL-1` remains the frozen algorithm/metric/horizon policy; cohort `P5A2-COHORT-ENDS-1` is a new source-admission policy, fixture-only in this slice. Both versions MUST be bound in the source manifest/digest and retained with an analytical result. This does not amend or silently reinterpret old run identities, `POLICY_VERSION`, old results or the 36/37 oracle. Any later operational adoption or scheduled-run/API/approval adapter needs reviewed composite-policy mapping under G03/G07/G11/G12 before use. SOURCE_READY does not clear the parent drift/changed-cohort gates or make a cross-policy result actionable. No historical production population/retention authority is inferred.

## Proposed testable source contract

R1 — Entry/auth: backend accepts verified `Principal`, trusted server scope mapping, aware query window and `run_as_of`; it obtains active assignment from the canonical repository. A caller-supplied actor/scope string or boolean `complete`/`retention_complete` is never trusted. In-memory path must copy/query under one shared lock; SQL path uses one read-only consistent transaction/connection for enrolled IDs, candidate IDs/counts, selected source records and assignment state, or returns a scoped refusal. For PostgreSQL, prove transaction isolation and a fresh complete cohort/membership-manifest recheck before releasing a result (including added/revoked assignments, assignment versions and shift-time enrollment changes, not merely the previously selected IDs); later run/approval/use paths must recheck again. If mutation/revocation makes consistency uncertain, refuse without exposing IDs/counts. Existing per-shift `AssignmentScope.require_shift` remains useful but its current list loop is not the integrated query.

R2 — Exhaustive cohort/caps: query enrolled shift IDs **from Shift+ACTIVE assignment**, including reportless, then candidate END_SHIFT version IDs for all enrolled shifts available at `run_as_of`. Count before Report content/body materialization: at most **500 eligible shifts and 500 candidate report versions total**; separately count at most **500 incident references per snapshot** before constructing its content. The source preflight conservatively checks every candidate snapshot that will be loaded, including superseded versions, so no oversized unselected body is loaded ahead of the parent whole-candidate validation. At 501 in each dimension, refuse `SCOPE_INCOMPLETE` with non-sensitive diagnostics; no first-500 page, filtered-away overflow, or partial success. A later stable pagination contract needs independent proof. Stable ordered IDs and count equality across snapshot are mandatory. Report version/created/cutoff are read from immutable native rows, including superseded versions; as-of selection follows accepted pure logic, never today's current flag.

R3 — Causal/time/lineage: reject naive stored Shift/Report timestamps as `TIMEZONE_UNSPECIFIED` (mapped to pure `TIME_AMBIGUOUS`); do not infer UTC from SQLite `DateTime(timezone=True)`. Positive PostgreSQL awareness requires actual proof. Preserve whole canonical Report content, `snapshot_digest`, source manifest and immutable IDs/version; pass exact objects into unchanged `HistoryInput`, `select_history` and `analyze`. Compare selected lineage and analysis against a **Root-frozen pre-BUILD independent oracle**; reuse 36/37 golden where valid, separately freeze reportless/late-correction/permission/cap oracles. A correction with `created_at > run_as_of` cannot leak into an earlier run. No second truth store, forecast engine or scheduler.

R4 — Coverage attestation: emit `complete=true`/`retention_complete=true` only from a trusted backend coverage authority. For a disposable synthetic rehearsal, a HARNESS-owned exact expected eligible-ID/version manifest may attest only that fixture; a caller boolean or reports-only scan cannot. The production retention enrollment/expiry owner and historical completeness evidence are absent; production query must return `SCOPE_INCOMPLETE`/blocked until separately accepted. Count equality alone does not prove retention. No operational completeness or business accuracy claim from synthetic fixtures.

R5 — Shared source receipt contract: family `P5A2-SCOPED-SOURCE-OUTCOMES`
at `docs/cvf/invariants/p5a2-scoped-source-outcomes.json`, source=this SPEC,
static ownership pin `docs/specs/p5a2_scoped_source_invariant_pin.py`, under
`docs/cvf/INVARIANT_FAMILY_STANDARD.md`. The matrix is the sole machine shape,
field-presence, count-domain, relation and mutation owner; reference it rather
than duplicating its per-shape rules into a Work Order. The policy decisions
below are the independent contract source, frozen before a source adapter exists.
Registration/generic guard proves contract structure only, not query/AI behavior.

The source query returns an internal `SourceQueryResult(receipt, payload)`.
`receipt` is one CLOSED flat family object. `payload` is unchanged `HistoryInput`
ONLY for `SOURCE_READY`, otherwise None. Payloads are server-internal; no route,
public serialization, durable run, recommendation or operational write is added.
SOURCE_READY means an authorized complete FIXTURE input is admissible for the
existing pure selector/analysis. It does not mean forecast READY or production
readiness. Only SOURCE_READY may call pure analysis; refuse on all other outcomes.

| Outcome | Contract / non-sensitive state |
|---|---|
| SOURCE_READY | Receipt/versions, authorized scope+actor+window/asof, SYNTHETIC_FIXTURE coverage, eligible/selected/candidate/max-ref counts, canonical source manifest and its SHA-256. Payload carries the same exact immutable data. selected_count=eligible_count, counts1..500 except max refs0..500; candidate_count>=selected_count is also a backend semantic check. |
| SOURCE_REFUSED | Only outcome, receipt/versions and a closed reason. No actor/scope/window, identifiers, counts, manifest, digest or payload. Reasons: ACCESS_DENIED, INVALID_WINDOW, TIME_AMBIGUOUS, COVERAGE_UNKNOWN, SCOPE_INCOMPLETE, SNAPSHOT_UNAVAILABLE, INVALID_LINEAGE, INCOMPATIBLE_POLICY, SOURCE_UNAVAILABLE. |

Receipt version `P5A2-SOURCE-RECEIPT-1`; numeric version `P5A2-INITIAL-1`;
cohort version `P5A2-COHORT-ENDS-1`. All three 501-cap cases return SOURCE_REFUSED/SCOPE_INCOMPLETE; no alternate cap reason is allowed. Auth/principal/server-scope validation is
first; a denied caller cannot probe data quality/caps/coverage through reasons.
Thereafter validate aware input window, snapshot capability, trusted coverage,
complete bounded membership/version metadata, immutable content, fresh current
assignment before release. Unknown source failures are SOURCE_UNAVAILABLE,
never raw driver errors/DSN. If fresh assignment check fails, discard payload
and every data-bearing field; later run/use/approval checks are still G06/G12.
A zero eligible cohort returns SCOPE_INCOMPLETE, not an empty success or zero
observation. Missing any enrolled report also returns SCOPE_INCOMPLETE.

Reason precedence/conditions are closed for this source contract:

| Reason | Exact class of trigger after deny-first validation |
|---|---|
| ACCESS_DENIED | Missing/untrusted principal or server scope, canonical authorization denial, or a selected assignment revoked before release. |
| INVALID_WINDOW | Offset-aware input fails start<end<=run_as_of. |
| TIME_AMBIGUOUS | Required timestamp is naive/missing or violates causal timestamp ordering; no inferred UTC. |
| COVERAGE_UNKNOWN | No accepted trusted coverage authority/attestation exists for the requested fixture/window. |
| SCOPE_INCOMPLETE | Zero cohort, enrolled shift without selectable report, attested manifest mismatch, fresh cohort boundary/version change, or any501 cap overflow. |
| SNAPSHOT_UNAVAILABLE | Backend cannot provide/prove one coherent read snapshot or an independent fresh current membership view. |
| INVALID_LINEAGE | Canonical content/manifest/digest/version conflict fails the unchanged parent validator. |
| INCOMPATIBLE_POLICY | Request/context/attestation policy does not match the declared accepted version pair; never reinterpret old data under it. |
| SOURCE_UNAVAILABLE | Other storage/read failure, with no raw driver details or data. |

The fresh complete membership/cohort check uses a NEW current view after the
read snapshot is sealed; repeating a query inside the same repeatable-read
snapshot is not a fresh recheck. A second connection is allowed only for this
post-snapshot check, not inside the single source read unit. If that view cannot
be established, refuse rather than claim fresh access. A detected revoke maps
to ACCESS_DENIED; additions/enrollment/version changes without a revoke map to
SCOPE_INCOMPLETE. Any refusal discards the internal payload before publication.

Source manifest canonical object has EXACT keys:
`scope_id`, `actor_id`, `query_start`, `query_end`, `run_as_of`,
`cohort_policy_version`, `numeric_policy_version`, `coverage_fixture_id`,
`coverage_manifest_digest`, `eligible_shifts`, `candidate_reports`,
`selected_reports`. eligible_shifts is UUID-sorted `{shift_id,ends_at,
assignment_id,assignment_version}`; candidate_reports is sorted by
`(shift_id,version,report_id)` and contains `{shift_id,report_id,version,
generated_from_cutoff,created_at,snapshot_digest}`; selected_reports is the
unchanged pure selector's lineage items in its native chronological order.
All relevant timestamps are explicit-offset values normalized to UTC Z.
Use canonical UTF-8 JSON, sorted keys/compact separators/no NaN, and SHA-256
of those exact canonical bytes as source_digest. Volatile transaction nonce,
read time and database statement counters are diagnostics, not source identity.
Whole content and record digests remain independently validated by parent owners;
the source digest alone does not replace that validation or prove retention.
Source report/eligible/selected counts equal manifest cardinalities, and the
receipt header equals manifest header. The source manifest contains authorized
metadata/hash references, not full report/incident bodies. New scope or cohort
policy/assignment versions change source identity; never approve a new policy
under an old result. Later G12 additionally detects source corrections after
an old run's logical asof, not just the same historical digest.

No source receipt DB-call counter is equated to parent `source_read_attempts`:
the latter remains one logical bounded admission, not SQL statements/pages.
Static family pin is not a real emitter. Before query BUILD, the reviewed WO
must bind actual model/emitter+mutation tests and Root-frozen independent source
oracle. Any ownership amendment must preserve the reviewed contract and refresh
its pin under independent review, not derive expectations from implementation.


## Acceptance boundaries and finite handoff

Stage A proposed after formal SPEC/family/WO review: one native bounded query/adapter plus inert memory/local fixture tests for authorized/reportless/revoked, 500 and 501 in three separate dimensions, late correction, naive-time refusal, digest/lineage and no mutation. Prove no pre-cap Report body creation and no extra SQL connections inside the read snapshot; inspect query plans/statement counts where relevant. Stage B only after independent Stage A and effect admission: **one new justified disposable PG query rehearsal** using existing installed driver/image/native runner lifecycle, synthetic data, frozen oracle and owned cleanup. No reset/repeat of the prior SQL rehearsal's spent ceiling; no package/pull/provider/.env/real credential/CSV effects. SQLite positive readiness and operational cohort/retention are separate unresolved gates. No API, UI, scheduler, durable approval, provider call or operational accuracy acceptance in this slice. The fixture dual-axis decision is part of this versioned contract, subject to independent review. No operational owner is invented. Missing production coverage, unsupported snapshot or missing pre-BUILD family/oracle/WO proof blocks dependent BUILD/readiness. Return to named Root/backend contract owners, not an automatic support survey.

## Principal, scope and fixture authority boundary

Native Principal/current assignment owners remain authoritative; this package
slice does not authenticate arbitrary Python objects or create a new tenant
model. Its application caller must supply a context from the existing trusted
auth boundary, and the source query must derive active membership itself.
Scope label is server-mapped identity of this project's query/fixture, not an
access token. A caller cannot grant access by naming PUBLIC_SCOPE or setting
complete/retention_complete. Future public API caller authentication/wiring is
G11 and must have its own actual integration evidence before full G06 closure.

CoverageVerifier is a trusted server-composed port, not request JSON or a client
boolean. For tests only, an independent harness-owned seed manifest binds
fixture id, instance/window/asof/policy, exact eligible assignments/shifts and
available report versions/digests. Query output must match that manifest; no
reports-only enumeration attests reportless coverage. The default operational
resolver has NO accepted authority and fails COVERAGE_UNKNOWN. A test fixture
attestor cannot be selected through an API/request flag or packaged as a
production completeness override. Real owner/retention authority is an explicit
Root/operator/backend G05 decision with accepted historical evidence later.

## Contract-stage acceptance / remaining implementation gates

This tranche may freeze SPEC + static family + independent review only. Existing
generic invariant tests/guard verify declared shapes, source/pin and ownership;
no actual source emitter/query, count-before-body, coherent transaction, runtime
authorization or new PG proof is claimed. Future source BUILD requires a reviewed
complete gate-to-role Work Order, native query/UOW ownership and final exact
paths, independent pre-loader fixture oracle and concrete snapshot/race tests.
G04/G05/G06/G13 operational portions and whole P5-A2 stay OPEN. Field domains
and generic mutations are structural; backend tests additionally prove canonical
manifest internals/count equality, candidate>=selected, real authorizer, timing,
source bytes, confidentiality and transaction behavior. No new provider call.
