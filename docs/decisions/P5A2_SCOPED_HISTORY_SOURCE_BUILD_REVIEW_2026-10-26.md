# P5-A2 scoped history source — independent Stage A authorization review

docType: completion_review
Status: AM1_REPAIR_REVIEW_PASS_BOUNDED
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
