# P5-A2 scoped history source — independent Stage A authorization review

docType: completion_review
Status: STAGE_A_REVIEW_PASS_BOUNDED
Date: 2026-10-26
Reviewer: independent REVIEWER; no Work Order, oracle, or implementation ownership

## Initial pre-dispatch decision (superseded by rereview below)

`CHANGES_REQUIRED_BOUNDED`. Stage A BUILD is not authorized yet. This is one
finite Work Order proof correction within the existing R2, fixture-only,
no-external-effect objective. Root must rerequest independent authorization
review before the normal dispatch commit and dedicated actual-SHA continuity.
Stage B remains held.

| Finding | Evidence | Finite correction |
|---|---|---|
| SOURCE-WO-F1 | The Work Order names a real emitter, samples both raw outcomes, and runs generic invariant-family tests, but does not require applying the registered matrix's full generated mutation basis to the **actual native emitted** `SOURCE_READY` and `SOURCE_REFUSED` receipts and proving every mutation is rejected by the native receipt validation/consumer path. The existing generic corpus exercises another emitter and matrix mechanics; it cannot supply that adapter parity proof. | Add this exact native emitter/consumer mutation obligation to the existing Stage A family test path, register that actual evidence path and emitter identity in the matrix binding once source exists, and require the independent reviewer to inspect raw positives, mutation rejection, and preserved backend manifest/count/digest/lineage corruption tests. Keep the accepted shape, domains, relations and exclusions unchanged. No new validator framework is needed. |

## Evidence and bounds

The accepted source SPEC canonical digest is
`db1d218083bfadac149f1c4415cfe0bc13213f41f33311a107447cad24abe7bf`;
the registered static matrix canonical digest is
`bca9bb9d5d201a6daeb05c58eb850dc53f27c3235a99cb71e15954bd1702273b`.
The frozen pre-loader oracle raw SHA256 is
`0f79676b627aceebd5e83a4b8143d29feda8deaad9392ad52cdd7204b593a044`.
Its standard-library recipe verifies the earlier immutable PG36 oracle raw
SHA256 `12ad36cbd335a8def5e7ac9a6ade6f0bf542cb45af4cec1760a7291a8f6973c0`;
it imports no new source loader. It freezes two complete ready receipts with
source digests `a27bdcd3...` and `57c64e0e...`, selected lineage and pure
analysis, plus 22 closed refusal receipt/payload expectations. The boundary
labels are expectations; worker-owned tests must construct valid native
500/501 inputs and show cap-before-body behavior. No query/emitter/runtime
truth is claimed from the oracle alone.

The Work Order otherwise supplies exact owned source and test paths; a native
ledger read unit, one SQL repeatable-read/read-only snapshot and a separate
fresh complete cohort/membership view; a memory lock/reacquire path; metadata
caps for every candidate before Report body construction; SQLite diagnostic
refusal; trusted fixture coverage and fail-closed unknown production coverage;
no provider, Docker, network, schema, route or durable effect. The 14-gap
Product Milestone Binding retains G04–G06 fixture mechanics and partial G13
drills as this tranche's only targets. G01/A7/G02 remain blocked, G03 and
G08–G10/G13 operational quality remain open, G07/G11/G12 remain open, G14 is
held; G05/G06 production coverage, retention and API/use-time authorization
remain unknown/open. Root, backend, independent reviewer, UI roadmap owner
and operator retain the accepted SPEC's P5-A2 and P5-B/C/D destinations.
Phase 5 remains 0/5.

`python scripts/check_cvf_core_machine_inheritance.py --enforce`,
`python scripts/check_session_state.py`, and
`python scripts/check_invariant_families.py` passed. These are packet/shape
checks, not source adapter or live governance proof. No full suite or external
effect was run for this authorization review.

## Return-Time Closeability Recheck

closeabilityDisposition: CLOSEABLE
outsideAuthorityBlockers: NONE
nextRepairRoute: NONE
workerRedispatchAllowed: YES

## Independent SOURCE-WO-F1 rereview and current decision

`AUTHORIZATION_REVIEW_PASS_BOUNDED`; SOURCE-WO-F1 is resolved, with no open
authorization findings or waiver. The revised Work Order now assigns
`validate_source_receipt(receipt)` to the exact native emitter path, requires
both emitters to consume it, and binds the complete registered mutation basis
of **both raw emitted outcomes** to rejection by that native consumer. It
separates this proof from the generic corpus, requires all four actual source
evidence test paths in the matrix binding, retains sample/mutation/rejection
counts, and checks parsed manifest, header, count, digest and lineage semantics
in native tests. The independent reviewer must rerun those tests, recompute
the static and runtime pins and inspect raw emitted outcomes. This closes the
specific adapter parity gap without changing the accepted receipt contract.

This PASS authorizes Root's bounded Stage A dispatch sequence only: normal
dispatch commit, dedicated actual-dispatch-SHA continuity, then fresh worker
acknowledgment. `DISPATCH_READY` alone does not authorize BUILD. All runtime
source mechanics and tests remain future implementation evidence; Stage B and
external effects remain held. The Product Milestone Binding and Phase 5 0/5
assessment above remain current.

## Independent AM1 pre-dispatch repair authorization

`AM1_REPAIR_AUTHORIZATION_PASS_BOUNDED`; no source BUILD authorization. The
unmodified normal dispatch hook stopped before commit with 1 failed,
3244 passed, 147 skipped, 4 warnings and 8 errors. The retained log
`.venv/p5a2-scoped-source-dispatch-20261026.log` traces all nine failing
integration cases to `_pinned_helper` in
`tests/integration/test_project_knowledge_ingest_rehearsal.py:47`: its global
Core `git status --porcelain` assertion sees four unrelated model-gateway
edits. The ordinary pinned-Core binding guard still passes; the selected
control bytes, Core HEAD, public origin and ingestion helper remain pinned.

The AM1 Work Order amendment adds only that one integration test path to a
pre-dispatch worker repair. It replaces the whole-Core cleanliness assumption
with existing exact installed-control verification plus the unchanged helper
Git-blob and raw SHA256 checks. It explicitly preserves the helper's network
token scan, real native PowerShell ingestion, index negative cases and cleanup.
The disposable local Git regression must prove unrelated tracked dirt is
tolerated while modified/missing helper or bound controls and wrong origin or
HEAD still fail. It cannot mutate either reference Core repository or contact
a remote. The same R2, no-effect, Root-commit ownership and product binding
apply. The complete G01–G14 remainders, P5-A2/P5-B/C/D destinations and
Phase 5 0/5 assessment above remain unchanged.

Independent AM1 authorization permits Root to activate the single-path
repair worker and independently review its diff and focused regression. The
failed full-hook result remains visible until the normal unmodified dispatch
hook passes; only then may Root create the dispatch commit and dedicated
actual-SHA continuity before main Stage A BUILD. No hook bypass, Core edit,
provider, network, Docker, package or production effect is authorized.

## Independent AM1 repair return review

`AM1_REPAIR_REVIEW_PASS_BOUNDED`; open AM1 findings `NONE`, waivers `NONE`.
The worker changed only the authorized integration test and its declared
worker-return artifact. The test file raw SHA256 is
`f803e7e0eb885a801abec9adabdb954dce510f44f45e7153ccdf91702cd01efc`
at 245 lines; the return raw SHA256 is
`24f365ecb04903254e66ded225eb70d675966e89200417ddd2886eb077ada841`.
The diff removes exactly the global Core `git status --porcelain` assertion
from `_pinned_helper` and allows an injected project root for isolated tests.
The ordinary call still invokes `verify_binding`, checks exact Core HEAD and
public origin, compares the helper to its pinned Git blob and unchanged
`HELPER_SHA256`, scans the same network tokens, and runs the existing native
PowerShell ingest, index negatives and cleanup tests.

The disposable Git fixture copies only pinned control/helper bytes into a
temporary repository. Its unrelated tracked dirt is accepted; its six
negative variants cover changed/missing helper, changed/missing bound control,
wrong origin and wrong pin. The fixture does not contact a remote or write to
the installed Core. I independently reran exactly the worker's focused
integration plus two Core unit paths: **37 passed in 19.03 s**. The worker's
reported 37 passed in 18.24 s is consistent; its focused log was not present
under the suggested name, so my rerun supplies direct result evidence.
`git diff --check` on the test path passed. The ordinary Core guard is
COMPLIANT, and native pinned `check_recheck` returned `[]` for the worker
return; removing its heading in a read-only negative control yielded
`return_recheck_missing`.

Root may retry the normal, unmodified dispatch hook. Only a passing hook may
precede the actual dispatch commit and dedicated SHA continuity; main Stage A
source BUILD still requires its separate fresh acknowledgment. The previous
full-hook failure stays recorded, and the P5-A2 G01–G14 remainders and
Phase 5 0/5 remain unchanged. No source adapter, provider, database or
production acceptance is claimed by this test repair.

## Independent Stage A source review — current decision

`STAGE_A_REVIEW_CHANGES_REQUIRED_BOUNDED`; no Stage A acceptance or material
commit yet. This is one consolidated same-scope repair packet for the exact
nine source and five test paths already admitted by the Work Order. No new
schema, route, provider, Docker, PostgreSQL rehearsal or effect is needed.

| Finding | Evidence | Finite repair and proof |
|---|---|---|
| SOURCE-A-F1 — native boundary and fixture authority | All three 501 refusal tests substitute a hand-written `Unit`, so none proves the native memory metadata path refuses before `Report.model_copy`/body creation. The 500 native tests use `BoundaryCoverage`, which checks only instance and sets of shift/report IDs, then returns a constant digest. It does not bind exact scope/actor/window/as-of/policy/assignment versions/candidate immutable metadata as the reviewed HARNESS attestor requires. | In existing cap/helper tests, construct valid native 501 cases for eligible shifts, total candidate versions and per-snapshot Incident refs, with a body-copy/load spy that fails if called before refusal. Bind boundary fixture coverage to independently seeded exact fixture context and complete cohort/candidate metadata, compute its canonical seed digest, and add mismatch negatives; retain the 500 positives. Do not claim operational retention. |
| SOURCE-A-F2 — receipt consumer semantics | With the frozen ready receipt, I changed a selected report's `created_at`, replaced its `source_manifest` with malformed refs, and replaced an eligible `assignment_id` with a non-UUID; after recomputing canonical source digest, `validate_source_receipt` accepted each. Changing both receipt and manifest `query_start` to `2026-99-99T99:99:99Z` was also accepted. The current native family tests mutate only one selected ID, list length, coverage digest, header or source bytes. The flat matrix's nested-object exclusion does not waive the Work Order's parsed manifest/lineage/time checks. | Extend the existing native consumer to validate real UTC timestamps and causal window ordering, UUID/positive-version metadata, full selected-to-candidate immutable fields including cutoff/created time, and selected lineage-ref structure; add focused recomputed-digest corruption tests for those examples. Keep the accepted flat outcome shapes and pre-BUILD oracle unchanged. This validates receipt metadata; it need not recreate report bodies or prove cryptographic source records from receipt alone. |
| SOURCE-A-F3 — snapshot and stored-content refusal mapping | A disposable fake PostgreSQL connection whose `execution_options(isolation_level="REPEATABLE READ")` raises returned `SOURCE_UNAVAILABLE` through the broad application exception handler. The accepted contract requires `SNAPSHOT_UNAVAILABLE` when coherent read/fresh capability cannot be established. Conversely malformed persisted Report reconstruction/validation should map to closed `INVALID_LINEAGE`, rather than a generic storage refusal. SQLite's diagnostic currently reads the first unscoped Shift, so an unrelated shift can decide between `TIME_AMBIGUOUS` and `SNAPSHOT_UNAVAILABLE`; this does not prove a scoped diagnostic. | In existing SQL/app paths, classify setup/fresh-view capability failures as `SNAPSHOT_UNAVAILABLE`, malformed persisted body as `INVALID_LINEAGE`, and genuine storage availability failures as `SOURCE_UNAVAILABLE`, all with sanitized receipts. Scope the SQLite diagnostic to the requested principal/window or use uniform `SNAPSHOT_UNAVAILABLE` when provenance cannot be established. Add inert negative fakes and a foreign naive-Shift case; actual PostgreSQL transaction proof remains Stage B. |
| SOURCE-A-F4 — denial and foreign-content precedence proof | The frozen `denied_actor_with_bad_time_and_overflow` test supplies an actor mismatch and naive start but no overflow; it therefore does not demonstrate denial ahead of a 501 cap. Existing source tests also do not inject a foreign assignment/oversized or invalid Report to prove bounded native queries never read foreign content. | In existing source/cap tests, combine denied actor with real native overflow and an instrumented read that must never be entered; separately add foreign shift/Report bad-time or 501-ref content while the authorized fixture remains ready, with a spy or exact selected IDs proving exclusion. Preserve the server-composed trusted-context precondition and do not infer API authentication. |

The worker return raw SHA256 is
`95a331eac5baf31a8a03309f34002f51da91197b81723fd98747cafa1eb7ab49`.
Root promoted the planned runtime matrix canonical digest
`9b3ba818e647d228e453706fac1378a69388bbae7b1a02d81732e64d939d5d4c`;
only its bounded claim, emitter identity, evidence paths and ownership consumers
changed from the accepted static matrix. The frozen pre-loader oracle raw
SHA256 `0f79676b627aceebd5e83a4b8143d29feda8deaad9392ad52cdd7204b593a044`
is unchanged. Actual ready/refused native samples and 54/30 matrix mutation
rejections are meaningful evidence, as are the two complete ready oracle
receipts, selected lineage and pure analysis. They do not resolve the four
specific gaps above. The initial focused result (35 passed, 1 failed) and
the corrected inert SQL assertion/retry (36 passed) are retained. I reran the
four focused paths plus the registered generic corpus independently:
**71 passed, 2 skipped**. Core, session, invariant-family and file-size
guards passed. No full hook or physical PostgreSQL/provider effect was run
for this review.

P5-A2 remains the integrated authorized forecast/history/freshness and exact
human-approval milestone. This Stage A can close only fixture-scoped G04–G06
mechanics and partial G13 failure handling after repair/review. G01/A7/G02
remain blocked; G03 and G08–G10/G13 operational quality remain open; G07/G11/
G12 remain open; G14 remains held. Production coverage/retention, API identity,
use-time approval, scheduler and physical PostgreSQL proof remain at their
named P5-A2 and later P5-B/C/D destinations, owned by Root/backend,
independent reviewer, UI roadmap owner and operator as reconciled in the
accepted SPEC and Work Order. Phase 5 remains 0/5. The bounded next move is
same-scope worker repair, focused evidence and independent rereview before
the unmodified material hook or any Stage B admission.

## Independent Stage A repair 1 rereview — current decision

`STAGE_A_REPAIR1_REVIEW_CHANGES_REQUIRED_BOUNDED`. SOURCE-A-F1 and F4 are
resolved. SOURCE-A-F2 has two adjacent parsed-receipt conditions still open;
SOURCE-A-F3 has one remaining reason-classification defect. They form one
consolidated final same-scope repair packet. No new path, effect, schema or
contract change is needed.

Native in-memory 501 cases now cover all three cap dimensions with zero
`load_reports` and `Report.model_copy` calls. The 500 boundary verifier freezes
full actor/scope/instance/window/as-of/policy, assignment/version and immutable
candidate metadata from a separately seeded fixture, and mismatch negatives
refuse. The native receipt consumer now rejects corrected-calendar, UUID,
selected metadata and lineage-ref corruption with recomputed digests; its
UTF-8 canonical encoding matches the accepted contract. The SQL/SQLite fakes
cover RR/read-only setup and fresh-view failure, persisted body versus storage
failure, and a foreign naive Shift. Denied actor with actual overflow never
opens a source read, and foreign bad-time/oversized Report content is excluded
from the exact authorized ready receipt. The frozen source oracle and accepted
matrix shapes remain unchanged.

| Remaining finding | Direct evidence | Finite correction |
|---|---|---|
| SOURCE-A-F2-R1 — selected window and strict lineage integer | From the frozen ready receipt, I changed the first selected `generated_from_cutoff` to `2025-12-31T23:00:00Z` (outside the declared window) and changed the corresponding candidate cutoff to match; after recomputing canonical manifest and digest, the native validator accepted it. I also changed the first selected source ref's `source_version` to JSON `true`; Pydantic coerced it to integer 1 and Python treated `1 == True`, so the native validator accepted it. These violate the SPEC's selected in-window rule and versioned ref integer domain, although the flat receipt shape still matches. | In the existing receipt consumer, require every selected cutoff in `[query_start,query_end)` and reject JSON bool/non-integer `source_version` before/coincident with model validation, without changing outcome shape or oracle. Add both recomputed-digest negatives to the existing family test. This checks receipt metadata, not source-body cryptographic truth. |
| SOURCE-A-F3-R1 — storage connection failure classified as snapshot incapability | `_read_only_rr` catches every `ledger.engine.connect()` exception and raises `SNAPSHOT_UNAVAILABLE`. I injected an `OSError` from `connect()` through the actual `SqlLedger` application path; `query_source` returned `SNAPSHOT_UNAVAILABLE`. The accepted SPEC trigger table assigns other storage/read failures to `SOURCE_UNAVAILABLE`, reserving `SNAPSHOT_UNAVAILABLE` for inability to provide a coherent/fresh snapshot. The repaired tests cover isolation setup and body-query availability, but not this connection failure. | Map initial storage connection failure to sanitized `SOURCE_UNAVAILABLE`; retain `SNAPSHOT_UNAVAILABLE` for RR/read-only setup and inability to establish the independent fresh view. Add an inert application-path connection-failure assertion beside the existing setup/body fakes. If the same helper serves both source and fresh views, distinguish the call context without changing the public receipt contract. |

The settled repair worker return raw SHA256 is
`af70aaa9462a48c8ea8c498b36378e89d37e0ab0b1020ff6e0f2ba282aad667c`.
Its exact three-source/four-test repair stays within the authorized nine-source/
five-test paths. The retained 85 passed/1 failed run was a test-host mistake;
the corrected focused plus generic corpus yielded 86 passed/2 skipped in
5.07 s. I independently reran the same corpus: **86 passed, 2 skipped in
4.70 s**. The two raw native outcomes and 54 READY/30 REFUSED matrix mutation
rejections remain valid evidence. Core, session, invariant-family, file-size,
knowledge and catalog guards passed. Direct receipt probes rejected changed
selected time, malformed lineage ref, bad assignment UUID and invalid calendar
after recomputing digest. The two additional probes above were accepted and
therefore remain findings. No actual PostgreSQL, provider or full suite was run.

The complete P5-A2 G01–G14 remainder and owner/destination binding above is
unchanged; Stage A remains fixture-scoped G04–G06/partial G13 only and Phase 5
remains 0/5. Root may route this one same-scope receipt/SQL/test repair and request
independent rereview before the normal material hook. Stage B is still held.

## Final independent Stage A repair 2 rereview — current decision

`STAGE_A_REVIEW_PASS_BOUNDED`; SOURCE-A-F1–F4 and adjacent F2-R1/F3-R1 are
resolved. Open Stage A findings `NONE`; waivers `NONE`. This PASS covers the
fixture-scoped source adapter and inert SQL/memory proof in the reviewed Work
Order. It does not claim physical PostgreSQL transaction execution, production
coverage/retention, API identity, scheduler, exact human approval, or CVF AI
governance behavior.

The final same-scope repair changed only the SQL read helper, native receipt
consumer, family test and inert SQL test. Their raw SHA256 values are
`3c719f293482734febfbbd19f8b3d9f68834065267076688a986a2700bf5505d`,
`ff8536e43cb043b2a0b5a921270a38ff729dc1f4b4df1a23a6a07e686715ecc1`,
`4eddde07066f642235f935a620022860d62f8d1aa7287edd176eac03edbb72cc`,
and `975e3eb78b52485073bc0d96938fab363e159f8543231839522f83aebb96a8fd`.
All 14 authorized source/test file hashes and line counts match the exact
worker-return manifest; the worker return raw SHA256 is
`0a15c53b45e2bdceff3e64dacd06f0bcf37e075c71a96af426d9d2eeae7ad60f`.

Initial storage connection failure now returns the frozen sanitized
`SOURCE_UNAVAILABLE` refusal. RR/read-only setup and fresh-view connection
capability failures remain `SNAPSHOT_UNAVAILABLE`. The native consumer
requires selected cutoffs in the declared window and strict integer
`source_version` fields in selected lineage refs. I independently changed a
selected and matching candidate cutoff outside the window, then changed a
versioned Incident ref to JSON bool, float and string values; each
recomputed-digest receipt was rejected. An application-path injected initial
connection `OSError` returned exact `SOURCE_REFUSED/SOURCE_UNAVAILABLE`
without payload or driver detail. The prior native 500/501 body-spy,
full-seed fixture coverage, foreign-content, denial-first, semantic receipt,
SQLite and inert SQL tests remain in the focused corpus.

The frozen oracle raw SHA256 is still
`0f79676b627aceebd5e83a4b8143d29feda8deaad9392ad52cdd7204b593a044`;
the registered runtime matrix canonical digest remains
`9b3ba818e647d228e453706fac1378a69388bbae7b1a02d81732e64d939d5d4c`.
Raw native sample SHA256 `0668e4f1b016e31c686cbebff62d9bd8f939b37ce91eae3c10f9cbabfeb1c90c`
contains the exact frozen first `SOURCE_READY` source digest `a27bdcd3...`
and a closed `SOURCE_REFUSED/ACCESS_DENIED`; the actual consumer rejects 54
READY and 30 REFUSED matrix mutations. The worker's final focused plus
generic run was **91 passed, 2 skipped in 5.71 s**; I independently reran
the same six paths: **91 passed, 2 skipped in 5.25 s**. The earlier 35/1 and
85/1 test mistakes remain recorded above. Core, session, invariant-family,
file-size, knowledge, catalog and diff checks passed.

The complete P5-A2 G01–G14 remainder and role/destination binding above is
still current. This bounded result advances fixture G04–G06 and partial G13
source mechanics only; G01/A7/G02 remain blocked, G03 and G08–G10/G13
operational quality remain open, G07/G11/G12 remain open, G14 remains held,
and production G05 retention/coverage and G06 API/use-time authorization are
unknown/open. Root/backend, independent reviewer, UI roadmap owner and
operator retain the P5-A2 and P5-B/C/D destinations in the accepted SPEC.
Phase 5 remains 0/5. Root may run the normal unmodified Stage A material
hook and commit the exact reviewed changed set if it passes; terminal actual
range review, dedicated actual-material-SHA continuity and clean-range
closure remain required before Stage B admission.
