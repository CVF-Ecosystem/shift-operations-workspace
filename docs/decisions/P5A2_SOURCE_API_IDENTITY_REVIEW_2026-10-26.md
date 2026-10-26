# P5-A2 G06/G11 source API identity — independent planning review

docType: completion_review
Status: PLANNING_REVIEW_PASS_BOUNDED
Date: 2026-10-26
Reviewer: independent REVIEWER; no SPEC, intake, Work Order, API or catalog ownership

## Decision

The INTAKE/SPEC packet remains docs-only and does not authorize an endpoint or
other runtime BUILD. Its deny-first signed-token/current-user/action contract,
server-only self scope, native bounded cohort probe, final fresh-membership
release check, default `COVERAGE_UNKNOWN`, receipt-only HTTP shape and 1 MiB
UTF8 limit are coherent as proposed behavior. The actual API is absent from
`main.py`; internal `query_source` is not HTTP authentication. Two finite
clarifications are required before accepting the contract for a normal
planning commit.

| Finding | Source-backed reason | Finite correction |
|---|---|---|
| API-SPEC-F1 — full positive oracle comparison is ambiguous | R3 requires `scope_id=P5A2-SELF-` plus SHA-256 of server instance/actor/cohort policy. The two old full source-oracle receipts literally use `scope_id=PUBLIC_SCOPE`, and their canonical manifests, coverage seed digests and `source_digest` bind that value. For the old `PUBLIC-SOURCE-INSTANCE-1`/`PUBLIC_ACTOR` fixture inputs, the proposed server formula yields `P5A2-SELF-bb627a60...`, so R5's phrase “match old frozen receipts after expected server scope context independently frozen” cannot mean byte-equal old receipts. | State that a **new, independently authored pair of complete API expected receipts** must be frozen before future implementation from the old known fixture data plus the new server-owned scope/context. Specify which old lineage/body/selection facts remain equal, and that scope, coverage digest, canonical manifest and source digest are independently recomputed in the new expected receipts. Preserve all old oracle bytes; future review must compare full new receipts, not digest-only or BUILD-derived expectations. |
| API-SPEC-F2 — operational READY requires a further native contract gate | Current `emit_source_ready()` hardcodes `coverage_mode=SYNTHETIC_FIXTURE`; `validate_source_receipt()` and registered family `P5A2-SCOPED-SOURCE-OUTCOMES` require that constant. A future accepted production coverage resolver by itself cannot yield an operational READY receipt under the unchanged emitter/family. R5 correctly defers HTTP consumer binding and production coverage, but its return-to-product gate could be read as resolver plus operator outcome being sufficient. | Explicitly retain operational READY as blocked until a separately reviewed native coverage-mode/receipt/family/emitter/validator change is authorized and proved alongside a real operational resolver. The proposed route remains refusal-only by default; synthetic positive tests use explicit server-owned fixture injection and do not promote fixture coverage. Keep all matrix and native source files unchanged in this planning tranche. |

## Authority, source facts and milestone coverage

The strict `get_principal_with_expiry` decoder requires a finite token expiry,
while the ordinary principal decoder does not. The strict dependency's current
HTTP error details are variable, so a future route must normalize them to the
SPEC's fixed 401 without changing unrelated routes; raw request parsing or
equivalent ordering must keep 401 ahead of FastAPI's query 422. Current stored
`get_user_by_id`/`is_active`, canonical `require_action` and the native
`scoped_source_read`/`fresh_scoped_cohort` ports exist; no proactive read action
or router is mounted. `query_source(..., coverage=None)` refuses before source
I/O. The proposed bounded actor/window cohort probe is necessary to deny an
unassigned caller before that coverage refusal. No application, source, test,
matrix, oracle, Core or prior result path changed in this packet.

The planning Work Order has an active native structural closeability graph,
with the exact active handoff's material-SHA surface and session-sync owner.
Its generic implementation/return rows are responsibility topology only;
they are **not** evidence that runtime BUILD, dispatch continuity or a new
source endpoint has occurred. The actual docs-only route is independent
contract review, normal planning material commit, terminal actual-range
review, dedicated actual-SHA continuity and clean range. A separate reviewed
implementation Work Order remains mandatory. The proposed 1 MiB overflow
mapping to existing `SCOPE_INCOMPLETE` is explicitly unimplemented and must be
bound to the native family/HTTP consumer before future BUILD; it does not
change the current matrix or emitter.

P5-A2's full outcome remains integrated authorized scheduled signals,
forecast/history/lineage/freshness/uncertainty/abstention and exact human
approval before durable recommendation/action. This packet can settle only a
G06/G11 contract and partial G13 test plan. G01/A7 provider 401 and G02 RAG
are blocked; G03 business fit, G04 operational integration, G05 production
coverage/retention and positive SQLite, G06 API/use-time access, G07
scheduler, G08–G10 operational quality, G11 API/UI, G12 approval and G13
integrated drills remain open/unknown; G14 provider proof is held. The SPEC's
complete G01–G14 table retains accountable Root/backend, independent reviewer,
UI owner and operator and concrete P5-A2/P5-B/C/D destinations. Phase 5 is
0/5. A refusal-only diagnostic without accepted resolver and operator outcome
does not automatically qualify for another implementation tranche.

Installed Core closeability and invariant-family guards passed. The intake's
standalone `Self-declared worker-return artifact: yes` makes pinned native
`check_recheck` applicable and it returned `[]`; the Core CLI's legacy
`docs/decisions/` selector is not automatic review coverage. Detailed catalog
generator, kit projection and governed catalog manager checks each passed,
including the active handoff pointer. No Docker, database, provider, network,
credential, source test or full suite was run for this docs-only review.

## Independent planning repair 1 rereview — current decision

`PLANNING_REVIEW_PASS_BOUNDED`. API-SPEC-F1 and API-SPEC-F2 are resolved in the
existing SPEC and intake, with the original findings above retained as review
history. R5 now requires two **new complete API receipt expectations** frozen
independently before future implementation from old known fixture data and the
server-composed R3 scope. It explicitly recognizes that old literal
`PUBLIC_SCOPE`, coverage seeds/manifests and source digests cannot equal the
new server-scope receipts. Old immutable body bytes, selected lineage, as-of
selection, numeric facts and all old source/body/PG oracles remain fixed.

R4 and the product return gate now state that the existing native emitter,
validator and registered family accept only `SYNTHETIC_FIXTURE` READY. A
production resolver alone cannot authorize operational READY: a separate
reviewed native coverage-mode/receipt/family/emitter/validator contract and
accepted operational source authority are required. The default route remains
unimplemented and refusal-only under no accepted operational coverage;
synthetic positives remain explicit test dependency injection. The proposed
1 MiB overflow refusal still requires future family/HTTP consumer binding
before any BUILD. No matrix, native emitter, API, test or prior proof changed.

This PASS authorizes only Root's normal docs-only planning material commit,
independent actual-range terminal review, dedicated five-path material-SHA
continuity and clean range. It does not authorize a route, provider call,
runtime BUILD, operational coverage claim or another refusal-only support
tranche. The full G01–G14 gap/owner/destination table and P5-B/C/D remainder
routes in the SPEC remain current; Phase 5 stays 0/5. Pinned Core guard and
explicit native intake/review rechecks pass; generic graph structure is not
proof that runtime implementation gates have occurred.

## Return-Time Closeability Recheck

closeabilityDisposition: CLOSEABLE
outsideAuthorityBlockers: NONE
nextRepairRoute: NONE
workerRedispatchAllowed: NO
