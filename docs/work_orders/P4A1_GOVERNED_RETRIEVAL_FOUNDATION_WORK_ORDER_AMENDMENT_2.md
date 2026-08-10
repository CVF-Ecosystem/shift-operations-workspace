# P4-A1 Governed Retrieval Foundation Work Order Amendment 2

- Amendment id: `P4A1-GOVERNED-RETRIEVAL-FOUNDATION-WO-A2-2026-08-10`
- Parent Work Order SHA-256: `b9889e4e207f408c705210207bfd1fcb32720ad7258522c2d0446e0d59d837e6`
- Amendment 1 SHA-256: `92241ce23d84b80e6112e54e2cde1ddf4c005b9ea6e0146d3586f5792de499e1`
- Repair rereview: `docs/decisions/P4A1_GOVERNED_RETRIEVAL_BUILD_REREVIEW_1.md`
- Repair rereview SHA-256: `cadead0315517519ea66d95438bc18a5f9e5be2f9510a12d3c6216b87bb062ea`
- Rereview disposition: `REPAIR_REREVIEW_CHANGES_REQUIRED`
- Authority checkpoint HEAD: `d878001b6a1a536218b2c66019243510ef3f7aec`
- Risk: `R2` unchanged
- Status: `PENDING_INDEPENDENT_AMENDMENT_REVIEW`
- Commit mode: `WORKER_MUST_NOT_COMMIT`
- Provider/network/product-API/external-database/audit call budget: `0`

## 1. Purpose And Unchanged Boundary

Repair round 1 closed F0, F2, F9, F10 and F12 and increased the focused suite
to 156 passing tests. Independent rereview reproduced nine remaining findings.

This amendment authorizes one consolidated repair round for those nine findings
only. It does not change the accepted SPEC, enable another corpus, add a route,
or open any LPCI1 answer/provider, P4-A, P4-A2, RAG, vector, persistence, audit,
UI, deployment or deeper project lane.

No repair begins until this exact amendment receives independent
`WORK_ORDER_AMENDMENT_REVIEW_PASS`.

## 2. Finding-To-Repair Trace

| Rereview finding | Parent finding | Required closure |
|---|---|---|
| `P4A1-RR1-F1` | F1 | call canonical `get_principal` surface with explicit bearer credentials |
| `P4A1-RR1-F2` | F3 | enforce lifecycle narrowing and test every filter dimension |
| `P4A1-RR1-F3` | F4 | manifest shape, containment, retention-literal and pin admission |
| `P4A1-RR1-F4` | F5/F11 | close every use-time manifest/read/overflow failure |
| `P4A1-RR1-F5` | F6 | scan later fitting candidates before output ceiling is filled |
| `P4A1-RR1-F6` | F7 | enforce snippet, receipt, result and handoff cross-bindings |
| `P4A1-RR1-F7` | F8 | truthful negative stages and receipt field population timing |
| `P4A1-RR1-F8` | F11 | final stop check before positive result emission |
| `P4A1-RR1-F9` | proof boundary | construct/reach all variants and every reproduced defect |

Waivers: `NONE`.

## 3. Source Verification Block

| Claimed item | Source file | Verified line/section | Verified path or symbol | Owning interface/function/schema | Verification class | Disposition |
|---|---|---|---|---|---|---|
| Canonical bearer dependency | `apps/workspace-api/src/workspace_api/dependencies.py` | lines 31-49 | `get_principal` | workspace API authentication | RUNTIME_BEHAVIOR | ACCEPT - required call surface |
| Repair bypasses canonical dependency | `apps/workspace-api/src/workspace_api/application/_governed_retrieval_admission.py` | lines 249-266 | `authenticate` | retrieval admission | RUNTIME_BEHAVIOR | ACCEPT - repair target |
| Lifecycle filter exists in request | `packages/governed-retrieval/src/governed_retrieval/request_models.py` | lines 137-205 | `lifecycle_statuses` | `RetrievalFiltersV1` | EXISTS | ACCEPT |
| Corpus narrowing omits lifecycle | `packages/governed-retrieval/src/governed_retrieval/corpus.py` | lines 94-105 | `filters_within_descriptor` | corpus descriptor policy | RUNTIME_BEHAVIOR | ACCEPT - repair target |
| Manifest path joins lack containment | `apps/workspace-api/src/workspace_api/application/_governed_retrieval_knowledge.py` | lines 120-135, 186-188 | `_admissible_entries`; `build_ready_contract` | Project Knowledge adapter | RUNTIME_BEHAVIOR | ACCEPT - repair target |
| Revalidation exception set is incomplete | `apps/workspace-api/src/workspace_api/application/_governed_retrieval_revalidation.py` | lines 140-145 | `revalidate_knowledge_candidates` | use-time revalidation | RUNTIME_BEHAVIOR | ACCEPT - repair target |
| Projection scan is pre-sliced | `apps/workspace-api/src/workspace_api/application/_governed_retrieval_revalidation.py` | line 212 | `assemble_projections` | projection assembly | RUNTIME_BEHAVIOR | ACCEPT - repair target |
| Projection model lacks content binding | `packages/governed-retrieval/src/governed_retrieval/evidence_models.py` | lines 52-80 | `EvidenceProjectionV1` | evidence schema | RUNTIME_BEHAVIOR | ACCEPT - repair target |
| Receipt model accepts supplied hash | `packages/governed-retrieval/src/governed_retrieval/receipt_models.py` | lines 25-80 | `RetrievalReceiptV1` | receipt schema | RUNTIME_BEHAVIOR | ACCEPT - repair target |
| Result model lacks receipt binding | `packages/governed-retrieval/src/governed_retrieval/result_models.py` | lines 17-26 | `_BaseResult`; `EvidenceAvailableV1` | result union | RUNTIME_BEHAVIOR | ACCEPT - repair target |
| Negative terminal stages remain PASS | `apps/workspace-api/src/workspace_api/application/governed_retrieval.py` | lines 202-218 | no-evidence and stale branches | application composition | RUNTIME_BEHAVIOR | ACCEPT - repair target |
| Execution metadata accepts caller identity/time values | `apps/workspace-api/src/workspace_api/application/_governed_retrieval_admission.py` | lines 63-84, 133-145 | `GovernedRetrievalExecutionMetadataV1`; `ExecutionContext.build_receipt` | execution identity and timing | RUNTIME_BEHAVIOR | ACCEPT - retained F11 repair target |
| Current Project Knowledge date fixture is stale | `tests/unit/test_project_knowledge_pack.py` | line 44 | `date(2026, 8, 3)` | Project Knowledge pack test | VALUE_SET | ACCEPT - exact test-only repair |
| Catalog diagnostic assertion | `tests/integration/test_catalog_drift_detection.py` | lines 54-57 | `test_check_passes_on_unmodified_repository` | catalog drift integration test | EXISTS | ACCEPT - exact diagnostic deselection only |
| Hidden core does not match manifest pin | `.cvf/manifest.json`; sibling hidden core | `cvfCoreCommit`; current local HEAD | `cvfCoreCommit` | workspace binding | VALUE_SET | ACCEPT - external blocker, forbidden repair |

No source item is `BLOCKED_SOURCE_NOT_FOUND`. The hidden-core mismatch is known
but explicitly outside this worker's authority.

### New Runtime Contract Fields

These names are new implementation fields, not claims that they already exist:

| Proposed field | Owner | Required behavior | Disposition |
|---|---|---|---|
| `uuid4_factory` | `GovernedRetrievalExecutionMetadataV1` | injected callable; service invokes it twice before R2 to allocate distinct receipt and correlation UUIDv4 values | `DESIGN_NEW` |
| `utc_now` | `GovernedRetrievalExecutionMetadataV1` | injected callable; service captures start before R2, source cutoff after snapshot, and finish at receipt emission | `DESIGN_NEW` |

The old caller-supplied `receipt_id`, `retrieval_correlation_id`, and single
reused `now` receipt-timing behavior must not remain authoritative. Fixed
factories/clocks remain injectable for deterministic golden tests.

## 4. Exact Changed-Set Authority

The runtime/package/application/schema/fixture/test repair ceiling remains the
same exact31 list in parent Work Order section 5. No new runtime, package,
application, helper, schema or P4-A1 test path may be created.

One additional existing test-only path is authorized:

32. `tests/unit/test_project_knowledge_pack.py`

In path 32, change only the explicit validation date from `2026-08-03` to the
current authorized pack review date `2026-08-10`, and add no unrelated test
behavior. The final repair ceiling is therefore at most exact32.

Within parent exact31, `pyproject.toml` and
`packages/cvf-runtime/src/cvf_runtime/permission.py` remain byte-protected. All
six Phase A paths and aggregate `bb180b1d...eaa7` remain byte-protected.

Forbidden paths include `.cvf/manifest.json`, the hidden core, catalog/status,
knowledge, session, roadmap, handoff, decision, SPEC, Work Order, API route, UI,
provider, audit, deployment and operational-corpus source paths.

## 5. Required Repair Behavior

### 5.1 Authentication

`execute_governed_retrieval` continues accepting an unverified bearer string.
Admission constructs the explicit credential object expected by
`workspace_api.dependencies.get_principal` and calls that exact dependency
surface. Missing, malformed, expired or mis-signed credentials map to the safe
authentication denial. Do not call `decode_access_token` directly in a P4-A1
module and do not accept a caller-created Principal.

### 5.2 Corpus filters

Represent allowed lifecycle values in the immutable descriptor or prove the
corpus supports none. Apply record type, truth class and lifecycle filters after
authorization. For Project Knowledge, any non-empty lifecycle filter outside
its exact descriptor must return `FILTER_WIDENS_SCOPE`. Test empty, allowed and
widening values for every dimension.

### 5.3 Project Knowledge admission and revalidation

- validate the top-level manifest is an exact supported object shape before
  accessing fields;
- require entry ids and paths to be safe relative forms;
- resolve every entry under `knowledge/` and every source pin under repository
  root, rejecting absolute, parent, symlink or resolved escape;
- accept only the exact current active retention policy literal owned by the
  manifest contract, never any arbitrary non-empty string;
- validate expected source-pin declarations independently from current raw-byte
  digests;
- apply the 100-entry ceiling at initial read and every use-time reread;
- convert malformed/unreadable/overflow/path/P3-A/P3-C use-time conditions to
  the specified typed result or stale omission; no raw exception escapes; and
- retain full rebuild/comparison of every R7 drift fact.

### 5.4 Projection scan

Iterate the complete deterministic selected survivor window. Add an emitted
projection only when it fits; continue after an unfit candidate until
`max_projection_records` projections are emitted or the window is exhausted.
Aggregate trimming remains lowest-rank whole-projection removal.

### 5.5 Contract integrity

Enforce at model construction/validation, not only in the happy-path builder:

- non-empty content snippet;
- offsets equal the actual snippet code-point length/range contract;
- recomputed snippet digest equals projection and nested citation digest;
- receipt hash equals canonical receipt bytes with only that field omitted;
- result outcome equals `receipt.final_outcome` for every variant;
- positive projection order maps one-to-one to receipt and handoff citation ids;
- evidence-set hash recomputes from exact ordered citation/projection dumps;
- handoff receipt/evidence hashes, counts, classifications, sensitivities,
  byte/code-point/token facts, limits, elapsed/termination facts and citation
  order equal the positive result and receipt; and
- negative variants cannot carry positive projections/handoff facts.

Avoid recursive hash validation by using explicit canonical preimage helpers or
model-level validators with the hash field omitted exactly as the appendix says.

### 5.6 Receipt truth and final stop

Before structural validation, the service invokes the injected `uuid4_factory`
twice to allocate distinct receipt/correlation UUIDv4 identities and invokes
`utc_now` to capture start time. It must not accept those two identities as
already allocated caller values. Capture source cutoff only after a source
snapshot and capture finish time independently at receipt emission. Require
finish to be consistent with non-negative elapsed time; do not reuse the start
timestamp after execution work has elapsed. Golden tests inject deterministic
factory/clock sequences rather than bypassing service allocation.

Set applied limits immediately after `CORPUS_RESOLVED=PASS`. Set source cutoff
after a source snapshot for positive, no-match and stale outcomes. Record the
first terminal non-access stage as `FAIL`; later stages are `NOT_RUN`, while
`RECEIPT_EMITTED` remains `PASS`.

Run one final timeout/cancellation checkpoint after projection/serialization
work and immediately before constructing/emitting the positive receipt/handoff.
No partial evidence may escape on stop.

## 6. Required Adversarial Proof

Inside existing exact31 tests plus exact test-only path 32, add direct assertions
for:

1. a spy on the real `get_principal` dependency and a guard that fails if a
   P4-A1 module imports/calls `decode_access_token`;
2. every lifecycle filter subset/widening case;
3. absolute, parent and symlink escape for entry and source-pin paths;
4. non-object/malformed manifest, missing id, deleted/unknown retention,
   use-time 101-entry overflow and every revalidation exception class;
5. unfit-first/fitting-second replacement with output ceiling one;
6. empty/tampered snippet, arbitrary receipt hash, cross-outcome receipt,
   citation order/count/hash, evidence hash and every handoff mismatch;
7. no-evidence and stale terminal `FAIL`, applied limits, source cutoff and
   receipt-emission timing;
8. timeout/cancellation triggered at the final pre-emission checkpoint; and
9. service-owned distinct UUIDv4 allocation, injected deterministic id/clock
   sequences, independently captured start/source-cutoff/finish timestamps and
   elapsed-time consistency; and
10. concrete construction or application reachability of all ten result
   variants, including stale, limit and invariant outcomes.

Tests must fail against the current rereview candidate and pass only after the
contract behavior is corrected.

## 7. Verification And External Blocker Accounting

Sanitize all live/provider/external-database environment variables exactly as
Amendment 1. Do not run the workspace doctor, network, hidden-core update,
PostgreSQL, Docker, live evidence or provider command.

Run in order:

1. focused exact P4-A1 suite;
2. `tests/unit/test_project_knowledge_pack.py`;
3. targeted adversarial tests for every RR1-F1 through RR1-F9 row;
4. full sanitized non-live suite once, unfiltered;
5. the exact diagnostic remainder command:

   `python -m pytest -q --ignore=tests/integration/test_project_knowledge_ingest_rehearsal.py --deselect=tests/integration/test_catalog_drift_detection.py::test_check_passes_on_unmodified_repository`;

6. file-size, Project Knowledge, session-state and diff checks;
7. catalog/repository checks without writing generated truth; and
8. exact32/protected aggregate/staged-zero/secret/generated-residue/static-I/O
   audits.

Allowed pending results before independent rereview:

- catalog-drift-only failure caused by unconverted reviewer-owned catalog truth;
- pinned-helper rehearsal errors whose root cause is exclusively hidden core
  `2103a38f...` versus manifest pin `9b039ea6...`.

Every other failure is `BLOCKED`. The worker must not call network, change the
core, update `.cvf/manifest.json`, alter the knowledge manifest, or relabel an
implementation failure as an environment blocker.

The diagnostic remainder must pass. The unfiltered suite must be reported as
blocked, not PASS, while the core mismatch remains.

## 8. Worker Return

Return exactly `REPAIR_2_COMPLETE_PENDING_REVIEW` or `BLOCKED`. Include:

- unchanged starting/ending HEAD;
- exact Amendment 2 and authorization-review hashes;
- exact32 name-status and per-path hashes;
- RR1-F1 through RR1-F9 source/test closure matrix;
- focused, targeted, Project Knowledge, unfiltered full and diagnostic remainder
  results with exact counts;
- separate catalog and hidden-core blocker evidence;
- protected six hashes and aggregate `bb180b1d...eaa7`;
- staged-zero, no-commit, file-size and zero-call evidence; and
- unchanged stop-after-mapping claim boundary.

Stop after return. Only the independent reviewer/closer may update catalog,
status, knowledge, continuity, commit, FREEZE or decide the external core-pin
blocker.

## 9. Agent Handoff Contract Control Block

| Field | Binding |
|---|---|
| route | `MULTI_AGENT_MULTI_ROLE` |
| rolePattern | amendment author, independent amendment reviewer, separate repair worker, independent build reviewer/closer |
| phase | `WORK_ORDER_REPAIR_AUTHORIZATION`, `REPAIR_2_EXECUTION`, `REREVIEW_2`, `CLOSURE_OR_EXTERNAL_BLOCK` |
| dispatchBaseHead | `d878001b6a1a536218b2c66019243510ef3f7aec` |
| executionBaseHead | same HEAD plus protected aggregate `bb180b1d...eaa7` |
| closureBaseHead | unchanged execution HEAD; reviewer binds returned working-tree diff |
| changedSetScope(phase) | parent exact31 plus exact test-only path 32; reviewer-owned closure remains separate |
| commitOwner(phase) | nobody before accepted rereview; reviewer/closer after all closure gates |
| crossBatchIsolation | hidden core, manifest pin, catalog and continuity are outside repair worker scope |
| nextMoveSurfaces | unchanged until rereview and external blocker disposition |

Designated closer: `INDEPENDENT_BUILD_REVIEWER_CLOSER`.

## 10. Checker Source Read-Ahead Block

The author read current source for the Project Knowledge, session, file-size,
catalog and repository checks and reproduced the current results. The full-suite
core-pin error is recorded as an external condition, not converted to a PASS or
implementation waiver.

## 11. ADIF Defect Registry Disclosure

Query basis remains downstream R2 repair Work Order authoring. Returned
defectIds: `NONE`. The repeated P4-A1 defects are recorded in project-native
review evidence; no claim is made that one downstream repair establishes a
shared CVF-core agent-defect pattern.

## 12. Claim Boundary And Independent Review Return

This amendment remains an INTERNAL/LOCAL_ONLY, provider-free governed retrieval
foundation repair. It is not an LLM answer path, complete RAG system, release,
deployment or deeper project implementation.

An independent reviewer returns exactly:

- `WORK_ORDER_AMENDMENT_REVIEW_PASS`;
- `WORK_ORDER_AMENDMENT_CHANGES_REQUIRED`; or
- `WORK_ORDER_AMENDMENT_BLOCKED_SOURCE_OR_SCOPE`.

No Repair 2 edit begins from this candidate alone.
