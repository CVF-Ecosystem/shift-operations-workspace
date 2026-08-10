# P4-A1 Governed Retrieval Foundation Work Order Amendment 1

- Amendment id: `P4A1-GOVERNED-RETRIEVAL-FOUNDATION-WO-A1-2026-08-10`
- Parent Work Order: `docs/work_orders/P4A1_GOVERNED_RETRIEVAL_FOUNDATION_WORK_ORDER.md`
- Parent Work Order SHA-256: `b9889e4e207f408c705210207bfd1fcb32720ad7258522c2d0446e0d59d837e6`
- BUILD review: `docs/decisions/P4A1_GOVERNED_RETRIEVAL_BUILD_REVIEW.md`
- BUILD review SHA-256: `88ed37974b46b628f047a240cf878c4f24babefa8998c8b7c6ea6cbd37033c91`
- Review disposition: `BUILD_REVIEW_CHANGES_REQUIRED`
- Authority checkpoint HEAD: `d878001b6a1a536218b2c66019243510ef3f7aec`
- Risk: `R2` unchanged
- Status: `PENDING_INDEPENDENT_AMENDMENT_REVIEW`
- Commit mode: `WORKER_MUST_NOT_COMMIT`
- Live/provider/network/product-API/external-database call budget: `0`

## 1. Trigger And Objective

The first P4-A1 BUILD returned all exact31 candidate paths and passed its
focused suite, but independent review found 13 material defects. The candidate
is not accepted and must not enter FREEZE.

This amendment authorizes one bounded repair cycle with two isolated phases:

1. a session-sync steward creates a deterministic semantic-equivalent re-baseline
   for six protected governance files; then
2. a separate no-commit repair worker corrects only the existing exact31
   candidate and adds adversarial proof inside those same test paths.

The objective, 12 requirements, 12 acceptance criteria, INTERNAL/LOCAL_ONLY
Project Knowledge positive corpus, provider-free boundary, and stop-after-mapping
boundary remain unchanged. This amendment does not reopen DESIGN or SPEC.

No action is authorized until this exact amendment receives an independent
`WORK_ORDER_AMENDMENT_REVIEW_PASS`.

## 2. Authority And Finding Trace

| Finding | Requirement / boundary | Required repair | Primary evidence path |
|---|---|---|---|
| `P4A1-BUILD-F0` | execution isolation | deterministic exact-six re-baseline and new manifest hash | successor handoff; session/roadmap/knowledge paths |
| `P4A1-BUILD-F1` | R3, R7 | verified authentication and permission before one Ledger unit | application admission/composition |
| `P4A1-BUILD-F2` | R3, R9 | separate authenticated, permission and assignment stage truth | admission, composition, receipt tests |
| `P4A1-BUILD-F3` | R4 | immutable registry and post-auth filter narrowing | corpus, application, CVF tests |
| `P4A1-BUILD-F4` | R5, R7 | validate real owner, retention and source pins | Project Knowledge adapter/tests |
| `P4A1-BUILD-F5` | R7 | reread/rebuild/compare all use-time evidence facts | revalidation and adversarial tests |
| `P4A1-BUILD-F6` | R8 | enforce lower client snippet limits and P3-A sensitivity | projection assembly/tests |
| `P4A1-BUILD-F7` | R8-R10 | recompute and cross-bind evidence, receipt, result and handoff | strict models/schema/tests |
| `P4A1-BUILD-F8` | R9 | correct terminal stages and `RECEIPT_EMITTED=PASS` | admission/receipt tests |
| `P4A1-BUILD-F9` | R2 | JSON-safe closed validation with post-auth corpus resolution | request/admission/models tests |
| `P4A1-BUILD-F10` | R6 | return typed limit result; never silently truncate | knowledge/application/limit tests |
| `P4A1-BUILD-F11` | R7, R11 | safe manifest failure, timeout, cancellation, timing and UUIDv4 | application/models/variant tests |
| `P4A1-BUILD-F12` | R8 | remove high/end side on equal trim distance | projection unit tests |

All findings are mandatory. Waivers: `NONE`.

## 3. Source Verification Block

| Claimed item | Source file | Verified line/section | Verified path or symbol | Owning interface/function/schema | Verification class | Disposition |
|---|---|---|---|---|---|---|
| Verified bearer dependency exists | `apps/workspace-api/src/workspace_api/dependencies.py` | lines 31-50 | `get_principal` | workspace API authentication dependency | EXISTS | ACCEPT |
| Candidate accepts a direct principal | `apps/workspace-api/src/workspace_api/application/governed_retrieval.py` | lines 93-121 | `execute_governed_retrieval` | retrieval application composition | RUNTIME_BEHAVIOR | ACCEPT - repair target |
| Admission combines authorization stages | `apps/workspace-api/src/workspace_api/application/_governed_retrieval_admission.py` | lines 241-268 | `authenticate_and_authorize` | retrieval admission | RUNTIME_BEHAVIOR | ACCEPT - repair target |
| Corpus registry is mutable | `packages/governed-retrieval/src/governed_retrieval/corpus.py` | lines 61-75 | `CORPUS_REGISTRY` | corpus registry | VALUE_SET | ACCEPT - repair target |
| Filter narrowing helper exists | `packages/governed-retrieval/src/governed_retrieval/corpus.py` | lines 88-99 | `filters_within_descriptor` | corpus descriptor policy | EXISTS | ACCEPT - application call required |
| Project Knowledge construction exists | `apps/workspace-api/src/workspace_api/application/_governed_retrieval_knowledge.py` | lines 137-208 | `build_ready_contract` | Project Knowledge adapter | RUNTIME_BEHAVIOR | ACCEPT - repair target |
| Knowledge revalidation is id/path-only | `apps/workspace-api/src/workspace_api/application/_governed_retrieval_revalidation.py` | lines 38-55 | `revalidate_knowledge_candidates` | use-time revalidation | RUNTIME_BEHAVIOR | ACCEPT - repair target |
| Projection assembly lacks per-snippet client limits | `apps/workspace-api/src/workspace_api/application/_governed_retrieval_revalidation.py` | lines 88-105 | `assemble_projections` | projection assembly | RUNTIME_BEHAVIOR | ACCEPT - repair target |
| Request model owns structural validation | `packages/governed-retrieval/src/governed_retrieval/request_models.py` | lines 120-215 | `RetrievalFiltersV1`; `GovernedRetrievalRequestV1` | strict request schema | EXISTS | ACCEPT - repair target |
| Evidence model owns projection integrity | `packages/governed-retrieval/src/governed_retrieval/evidence_models.py` | lines 20-80 | `CitationV1`; `EvidenceProjectionV1` | evidence schema | EXISTS | ACCEPT - repair target |
| Receipt and handoff models exist | `packages/governed-retrieval/src/governed_retrieval/receipt_models.py` | lines 25-116 | `RetrievalReceiptV1`; `FutureContextHandoffV1` | receipt/handoff schema | EXISTS | ACCEPT - repair target |
| Ten result variants exist | `packages/governed-retrieval/src/governed_retrieval/result_models.py` | lines 17-61 | `EvidenceAvailableV1`; negative result variants | result union | EXISTS | ACCEPT - binding repair target |
| Byte trimming implementation exists | `packages/governed-retrieval/src/governed_retrieval/projection.py` | lines 42-79 | `_trim_to_byte_budget` | projection minimizer | RUNTIME_BEHAVIOR | ACCEPT - tie repair target |
| Catalog generator owns generated catalog truth | `scripts/generate_catalog.py` | full generator | catalog generation entry point | catalog closure tooling | RUNTIME_BEHAVIOR | ACCEPT - reviewer-owned after semantic pass |

No source item is `BLOCKED_SOURCE_NOT_FOUND`. Proposed repair behavior is new
implementation work and is not misrepresented as current source truth.

## 4. Phase A - Protected Byte Re-Baseline

Role: `SESSION_SYNC_STEWARD`. This phase is governance repair, not BUILD.
It must complete and receive read-only reviewer confirmation before the repair
worker changes any exact31 byte.

The old six-file byte state cannot be reconstructed by one uniform newline
conversion: an in-memory CRLF-to-LF projection reproduces only two of six old
hashes because the released files had mixed newline histories. This amendment
does not call the result a restoration. It authorizes one new deterministic
all-LF baseline while preserving current decoded text, except for the one
Project Knowledge source-pin refresh stated below.

Normalize CRLF to LF in exactly these six paths. In `knowledge/manifest.json`,
make exactly one additional 64-character substitution so the Project Context
source pin for `docs/implementation/EXECUTION_ROADMAP.md` changes from
`8daada8f9988798c992c5f4ddc5e8c63c09a8948afecb0d9ea952d07a635cb3a`
to the all-LF roadmap SHA-256
`e5fa3a5695f5817a7152e2ea983d456b38219ab1a79a5ba769a936016fd86f9e`.
No other decoded text may change.

Assert the post-image raw-byte SHA-256 values:

| Path | Required SHA-256 |
|---|---|
| `CVF_SESSION/ACTIVE_SESSION_STATE.json` | `dc7051824f62c06f6e95c6c0bd8352544ff4405f89c592363e92e3e8f28a67b9` |
| `SESSION/ACTIVE_SESSION_STATE.json` | `c9c9e2e0bb46d6b2585ab091deb6a721e455babccc7f8d3eb407178056c59c69` |
| `SESSION/SESSION_MEMORY.md` | `68c366677fb6a7a39229d371cc88acbf3ec27b247ff74f468070ffbded154e91` |
| `docs/implementation/EXECUTION_ROADMAP.md` | `e5fa3a5695f5817a7152e2ea983d456b38219ab1a79a5ba769a936016fd86f9e` |
| `knowledge/PROJECT_CONTEXT.md` | `f2318222889f428f1b6951510c79e2889255e3e3594179076efbfdb54c363a34` |
| `knowledge/manifest.json` | `e561a9bdb34cb9eb7949ec7fc6afc0ab9cc488d4984245d6c0d54f8974d963df` |

After re-baseline, recompute all 15 rows with the released algorithm and
require manifest SHA-256:

`bb180b1dfdd180d8d8350492d0803e5adb6eb08d4cc3385a4204f6a18b00eaa7`

Fail conditions:

- any decoded-text change other than the exact manifest pin substitution;
- any seventh path changes;
- any individual hash differs;
- the aggregate manifest differs;
- Project Knowledge, session-state, or diff checks fail after re-baseline.

On failure, stop and return `BLOCKED_PROTECTED_REBASELINE`; do not begin Phase
B. Nothing is staged or committed in Phase A.

## 5. Phase B - Exact31 Repair Authority

Role: separate `REPAIR_WORKER`. Entry evidence is the independently confirmed
Phase-A aggregate manifest `bb180b1d...eaa7` and the unchanged HEAD.

The repair ceiling is the same exact31 path list in parent Work Order section
5. No 32nd BUILD path is authorized. `pyproject.toml` and
`packages/cvf-runtime/src/cvf_runtime/permission.py` are already passing and
must remain byte-identical unless a source-backed repair finding proves they
must change; in that case the worker stops and returns to the reviewer instead
of changing them.

The worker may modify only the remaining existing exact31 package,
application, schema, README, fixture, and test paths needed to close F1-F12.
It must not create another helper/source/test file. File-size limits remain
binding; if a touched source would exceed 300 lines, refactor only within the
already authorized exact31 files.

### Required implementation behavior

1. Separate structural parsing, verified authentication, permission, assignment
   and corpus resolution. Unknown corpus validity is not disclosed before
   authorization. Open exactly one Ledger unit only after authentication and
   permission; reuse it through initial assignment, reads and final assignment.
2. Represent the registry immutably and apply all descriptor filters after
   authorization. Any widening returns the exact safe invalid-request outcome.
3. Validate Project Knowledge paths, pins, owner, classification, retention and
   raw bytes from current manifest truth. Do not invent owner, retention,
   sensitivity, source pin, or lifecycle facts.
4. At use time, reread and rebuild the admitted contract, then compare every
   source/content/version/chunk/token/owner/retention/sensitivity fact required
   by R7. Changed candidates are omitted as stale; no stale projection survives.
5. Reject manifest/document/record and execution-limit overflow with the typed
   result. Do not slice an oversized input to make it admissible.
6. Apply the minimum of server and client limits at every snippet, aggregate and
   token boundary. Preserve the P3-A candidate sensitivity. Continue scanning
   the deterministic selected-result window when an earlier survivor cannot fit.
7. Recompute all required SHA-256 bindings from canonical bytes. Enforce non-empty
   evidence and exact result/receipt/projection/handoff outcome, count, order,
   budget, citation and hash relationships on construction and validation.
8. Accept normal parsed JSON arrays while retaining strict closed validation.
   Convert malformed input to one of the normative R2 codes; no raw `TypeError`
   or Pydantic exception escapes the application boundary.
9. Emit truthful ordered stages for every result. Every returned receipt has
   `RECEIPT_EMITTED=PASS`; `corpus_id` and applied limits obey appendix
   population timing; the first terminal operational stage is `FAIL`.
10. Implement safe typed manifest/unavailable, timeout and cancellation paths;
    generate/enforce UUIDv4 receipt/correlation identity and measure local
    monotonic elapsed time without remote calls.
11. Correct equal-distance byte trimming by removing the high/end side.
12. Preserve all positive pass boundaries from the BUILD review.

### Required adversarial proof

Inside the existing exact31 test files, add failing-before/fixed-after cases for:

- forged/unverified principal, authentication failure, permission denial,
  assignment denial, transaction-open order and one-unit reuse;
- mutable registry attempts and every widening filter dimension;
- normal JSON arrays, malformed filter types, unsafe IDs, and unknown corpus
  before/after authorization;
- manifest path escape, missing owner, inactive retention, pin/raw-byte drift,
  all R7 use-time drift classes, source read failure and malformed manifest;
- 99/100/101 manifest entries and 65,535/65,536/65,537 document boundaries
  without silent truncation;
- lower client snippet/aggregate/token limits, multibyte exact limits, later
  fitting candidates, sensitivity preservation, and equal-distance trim ties;
- empty/tampered evidence, wrong digests, receipt hashes, outcome mismatch,
  citation order/count mismatch and handoff binding mismatch;
- all ten concrete result variants, timeout, cancellation, UUID version,
  measured timing, stage ordering and mandatory receipt emission.

Tests must assert contract behavior, not internal implementation shape alone.

## 6. Reviewer-Owned Catalog And Knowledge Closure

The repair worker does not modify catalog, implementation-status, roadmap,
knowledge, session, handoff, or decision paths. It reports the full-suite result
honestly. Catalog-drift-only failures caused by accepted exact31 source growth
are expected until reviewer closure conversion; no other failure is allowed.

After independent semantic review accepts the repaired exact31 candidate, the
reviewer/closer may use the parent Work Order's existing reviewer-owned closure
authority to update:

- `IMPLEMENTATION_STATUS.json`;
- `docs/catalog/MODULE_REGISTRY.json`;
- `docs/catalog/MODULE_CATALOG.md`;
- Project Knowledge context/manifest pins only when changed closure truth
  requires them; and
- the completion review and later continuity surfaces.

The reviewer then regenerates catalog truth and reruns the full sanitized suite
and all repository gates. A semantic finding blocks these closure writes.

## 7. Verification And Stop Conditions

Before tests, remove all listed live/provider/external-database environment
variables exactly as in parent Work Order section 12. Never run the
network-fetching workspace doctor, live evidence bundle, PostgreSQL, Docker,
product API, provider, deployment, route, UI, audit or persistence action.

Repair-worker verification order:

1. exact focused P4-A1 suite;
2. targeted adversarial tests for every F1-F12 row;
3. full sanitized non-live suite once;
4. file-size, Project Knowledge, session-state and diff checks;
5. catalog check and repository validation, with only source-derived catalog
   drift eligible for `PENDING_REVIEWER_CLOSURE`;
6. exact31/protected-manifest/staged-zero/secret/generated-residue/static-I/O
   audits.

Stop and return `BLOCKED` for any non-catalog failure, protected-path drift,
32nd path, missing typed variant, unverifiable source fact, file-size breach,
provider/network/product-API/external-database/audit call, secret exposure,
stage/commit/push, scope broadening, or need to alter accepted SPEC semantics.

## 8. Worker Return Contract

Return exactly `REPAIR_COMPLETE_PENDING_REVIEW` or `BLOCKED`. Include:

- starting and ending HEAD, which must be identical;
- exact amendment hash and Phase-A manifest proof;
- exact31 name-status and per-path hash manifest;
- finding-to-test-to-source closure table for F1-F12;
- focused/adversarial/full suite counts and every gate result;
- any catalog-only pending closure evidence separated from functional failures;
- local SQLite call count and zero provider/network/product-API/external-
  database/audit counts;
- file line counts, protected-path hashes, staged-zero and no-commit proof; and
- retained claim and stop-after-mapping boundary.

The worker stops after return. Only the independent reviewer/closer may accept,
repair reviewer-owned closure truth, commit, synchronize continuity, or FREEZE.

## 9. Agent Handoff Contract Control Block

| Field | Binding |
|---|---|
| Contract source | project `AGENTS.md` Provider-Neutral Role Contract and Handoff and Tranche Closure Protocol; parent Work Order section 10 |
| route | `MULTI_AGENT_MULTI_ROLE` |
| rolePattern | author, independent amendment reviewer, session-sync steward, separate repair worker, independent build reviewer/closer |
| phase | `WORK_ORDER_REPAIR_AUTHORIZATION`, `PROTECTED_REBASELINE`, `REPAIR_EXECUTION`, `REREVIEW`, `CLOSURE` |
| dispatchBaseHead | `d878001b6a1a536218b2c66019243510ef3f7aec` |
| executionBaseHead | same unchanged HEAD plus re-baselined manifest `bb180b1d...eaa7` |
| closureBaseHead | unchanged execution HEAD; reviewer binds returned working-tree diff |
| changedSetScope(phase) | exact-six deterministic re-baseline; same exact31 repair; reviewer-owned closure paths only after semantic pass |
| traceScope(phase, actor) | every role reports only its own reads, writes, commands and calls |
| commitOwner(phase) | nobody before accepted rereview; reviewer/closer for material closure; session-sync steward for later continuity |
| crossBatchIsolation | exact-six re-baseline and exact31 repair are sequential and separately proven |
| nextMoveSurfaces | unchanged until accepted rereview and reviewer closure conversion |

Designated closer: `INDEPENDENT_BUILD_REVIEWER_CLOSER`.

## 10. Checker Source Read-Ahead Block

The amendment author read the parent Work Order verification contract,
`scripts/check_project_knowledge.py`, `scripts/generate_catalog.py`,
`scripts/check_session_state.py`, `scripts/check_file_size.py`, and
`scripts/testing/validate_repository.py` ownership through current source and
reproduced their current outcomes. Literal result tokens and path boundaries in
this amendment follow project-native precedent; no CVF-core checker is treated
as downstream runtime authority.

## 11. ADIF Defect Registry Disclosure

Query basis: downstream R2 repair work-order authoring, author role, REVIEW to
WORK_ORDER repair lifecycle. The previously authorized parent Work Order query
returned `NONE` (`totalCandidates=0`, `truncated=false`). No new CVF-core ADIF
entry is created because the material findings are project implementation
defects, not a repeated shared-core agent-defect pattern established by this
single BUILD.

Returned defectIds: `NONE`.

## 12. Claim Boundary And Independent Review Return

This amendment repairs only the P4-A1 INTERNAL/LOCAL_ONLY Project Knowledge,
provider-free, evidence-grounded retrieval foundation. It does not authorize
LPCI1 answer generation,
API keys, LLM calls, vector/semantic RAG, restricted/confidential/full-document
access, durable audit/persistence, operational-corpus enablement, digest-owner
implementation, product API/UI, deployment, public release, P4-A, P4-A2, or
deeper project development.

An independent amendment reviewer must reproduce authority hashes, F0-F12
coverage, exact-six re-baseline hashes, exact31 ceiling, source verification,
catalog closure split, zero-call boundary and role separation. Return exactly:

- `WORK_ORDER_AMENDMENT_REVIEW_PASS`;
- `WORK_ORDER_AMENDMENT_CHANGES_REQUIRED`; or
- `WORK_ORDER_AMENDMENT_BLOCKED_SOURCE_OR_SCOPE`.

No re-baseline or repair begins from this candidate alone.
