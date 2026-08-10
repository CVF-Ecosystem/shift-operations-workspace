# P4-A1 Governed Retrieval Foundation Work Order Amendment 4

- Amendment id: `P4A1-GOVERNED-RETRIEVAL-FOUNDATION-WO-A4-2026-08-10`
- Parent Work Order SHA-256: `b9889e4e207f408c705210207bfd1fcb32720ad7258522c2d0446e0d59d837e6`
- Amendment 1 SHA-256: `92241ce23d84b80e6112e54e2cde1ddf4c005b9ea6e0146d3586f5792de499e1`
- Amendment 2 SHA-256: `4bd2f9a7d6252a7d8970fd8b86cc1e052c89b4ae4adc608a65ed9fd14d3a39ee`
- Amendment 3 SHA-256: `847a0a9705415ee6105f47c6b0b5eac0bd964ec8bc74849e60afd6d1af902661`
- Repair 3 rereview: `docs/decisions/P4A1_GOVERNED_RETRIEVAL_BUILD_REREVIEW_3.md`
- Repair 3 rereview SHA-256: `e8b390a0150841e58a7ccd3b82015e9fcb303a43dc8bf63821d931358cf5174f`
- Rereview disposition: `REPAIR_3_REVIEW_CHANGES_REQUIRED`
- Round-four checkpoint: `OPERATOR_RELEASED_2026-08-10`
- Authority checkpoint HEAD: `d878001b6a1a536218b2c66019243510ef3f7aec`
- Risk: `R2` unchanged
- Status: `PENDING_INDEPENDENT_AMENDMENT_REVIEW`
- Commit mode: `WORKER_MUST_NOT_COMMIT`
- Provider/network/product-API/external-database/audit call budget: `0`

## 1. Purpose And Unchanged Boundary

The operator explicitly authorized continued repair after receiving the Repair
3 rereview. This amendment authorizes one consolidated Repair 4 limited to the
four reproduced runtime failures and one proof-completeness finding in that
rereview.

The objective, exact32 ceiling, R2 risk, zero-external-effect class, accepted
SPEC, and stop-after-mapping boundary remain unchanged. No corpus, provider,
answer, API route, durable audit, persistence, UI, deployment, P4-A, P4-A2,
LPCI1-REF, semantic RAG, vector search, or deeper project lane is opened.

No Repair 4 source or test edit begins until this exact amendment receives an
independent `WORK_ORDER_AMENDMENT_4_REVIEW_PASS`.

## 2. Finding-To-Repair Trace

| Repair 3 rereview finding | Required closure |
|---|---|
| `P4A1-RR3-F1` | reject the whole initial manifest when any entry fails the retrieval-runtime subset; return typed `CORPUS_UNAVAILABLE` |
| `P4A1-RR3-F2` | convert every ordinary initial P3-A/P3-C exception into typed `CORPUS_UNAVAILABLE`; do not catch `BaseException` |
| `P4A1-RR3-F3` | reject a symlink at the `knowledge` base as well as every descendant component |
| `P4A1-RR3-F4` | reject positive elapsed time unless finish is strictly later than start |
| `P4A1-RR3-F5` | add direct, non-permissive adversarial proof for every retained edge |

Waivers: `NONE`.

## 3. Source Verification Block

| Claimed item | Source file | Verified line/section | Verified path or symbol | Owning interface/function/schema | Verification class | Disposition |
|---|---|---|---|---|---|---|
| Invalid entries are silently filtered | `apps/workspace-api/src/workspace_api/application/_governed_retrieval_knowledge.py` | lines 199-215 | `_admissible_entries` | Project Knowledge initial admission | RUNTIME_BEHAVIOR | ACCEPT - repair target |
| The initial caller maps only declared corpus/limit exceptions | `apps/workspace-api/src/workspace_api/application/_governed_retrieval_sources.py` | lines 208-253 | `admit_knowledge_candidates` | application source admission | RUNTIME_BEHAVIOR | ACCEPT - repair target |
| Initial P3-A/P3-C calls can raise ordinary exceptions | `apps/workspace-api/src/workspace_api/application/_governed_retrieval_knowledge.py` | lines 223-281 | `build_ready_contract` | Project Knowledge P3 composition | RUNTIME_BEHAVIOR | ACCEPT - caller boundary repair target |
| The symlink walk omits the base component | `apps/workspace-api/src/workspace_api/application/_governed_retrieval_knowledge.py` | lines 127-145 | `_resolve_contained` | Project Knowledge path admission | RUNTIME_BEHAVIOR | ACCEPT - repair target |
| Positive elapsed/equal wall-clock time is accepted | `packages/governed-retrieval/src/governed_retrieval/receipt_models.py` | lines 94-144 | `_stage_order_and_time` | `RetrievalReceiptV1` | RUNTIME_BEHAVIOR | ACCEPT - repair target |
| Coordinated tamper test changes only one side at a time | `tests/contract/test_p4a1_governed_retrieval_schema.py` | lines 148-169 | `test_coordinated_evidence_hash_tampering_rejected_even_with_correct_receipt_hash` | positive wrapper contract proof | RUNTIME_BEHAVIOR | ACCEPT - test repair target |
| Replacement proof permits a negative result | `tests/cvf/test_p4a1_governed_retrieval.py` | lines 161-188 | `test_unfit_first_fitting_second_projection_replacement_at_ceiling_one` | projection scan proof | RUNTIME_BEHAVIOR | ACCEPT - test repair target |
| Allocation proof counts calls but not exact call order | `tests/cvf/test_p4a1_retrieval_authorization.py` | lines 243-270 | `test_identity_and_start_time_allocated_before_r2_even_on_invalid_request` | pre-R2 allocation proof | RUNTIME_BEHAVIOR | ACCEPT - test repair target |
| Negative grammar loop omits four negative outcomes | `tests/unit/test_p4a1_retrieval_receipts.py` | lines 279-297 | `test_every_negative_outcome_accepts_its_own_grammar_and_rejects_swapped` | receipt grammar proof | RUNTIME_BEHAVIOR | ACCEPT - test repair target |

No source item is blocked. No new runtime field, result variant, receipt stage,
corpus id, provider surface, route, persistence owner, or path is introduced.

## 4. Exact Repair Changed Set

The Repair 4 worker may edit only these eight existing exact32 paths:

1. `apps/workspace-api/src/workspace_api/application/_governed_retrieval_knowledge.py`
2. `apps/workspace-api/src/workspace_api/application/_governed_retrieval_sources.py`
3. `packages/governed-retrieval/src/governed_retrieval/receipt_models.py`
4. `tests/contract/test_p4a1_governed_retrieval_schema.py`
5. `tests/cvf/test_p4a1_governed_retrieval.py`
6. `tests/cvf/test_p4a1_retrieval_authorization.py`
7. `tests/integration/test_p4a1_retrieval_ledger_parity.py`
8. `tests/unit/test_p4a1_retrieval_receipts.py`

The final ceiling remains exact32. No worker-created path 33 or change to any
other exact32 path is authorized. The reviewer-owned Repair 3 rereview and
this amendment are governance paths outside the worker changed set.

All six Phase A paths, protected aggregate
`bb180b1dfdd180d8d8350492d0803e5adb6eb08d4cc3385a4204f6a18b00eaa7`,
all other governance artifacts, `.cvf/manifest.json`, hidden core, catalog,
status, knowledge, session, roadmap, handoff, API route, UI, provider, audit,
deployment, and operational-corpus paths remain forbidden to the worker.

## 5. Required Repair Behavior

### 5.1 Whole-manifest fail-closed admission

Initial Project Knowledge admission must validate every entry before returning
any admissible entry. If any entry violates the exact retrieval-runtime entry
or pin shape, unique safe id/path constraints, owner allowlist, consumer rules,
metadata literals, current raw-byte pin, or path/symlink containment, raise the
safe internal corpus-unavailable signal so the application returns
`CORPUS_UNAVAILABLE` at `SOURCES_READ=FAIL`.

An empty but structurally valid entries list may remain an empty corpus and
lead to the existing downstream no-evidence behavior. Do not duplicate the
repository checker's count, mapping, date, purpose, trigger, correction, or
inventory rules into runtime.

### 5.2 Initial ordinary-exception boundary

The initial caller must convert every ordinary `Exception` from manifest
validation and candidate P3-A/P3-C construction into the same safe
`CORPUS_UNAVAILABLE` result. Preserve the existing typed
`RETRIEVAL_LIMIT_EXCEEDED` paths for manifest and document ceilings.

Do not catch `BaseException`, `KeyboardInterrupt`, or process termination. Do
not expose exception text in the result or receipt.

### 5.3 Governed-root symlink refusal

Path validation must inspect the path from `repository_root` through the
`knowledge` base and every entry or source-pin component. Reject a symlinked
`knowledge` base even when it resolves inside the repository, and reject it
when it resolves outside. Preserve absolute-path, parent-traversal, resolved-
escape, and descendant-symlink refusal.

The implementation must remain platform-neutral. Tests may use an injected or
monkeypatched path-observation seam when local symlink creation is unavailable.

### 5.4 Receipt wall-clock and monotonic consistency

Keep `finished_at_utc >= started_at_utc`. Additionally require:

- `elapsed_ms > 0` implies `finished_at_utc > started_at_utc`;
- `elapsed_ms == 0` may use equal or later wall-clock timestamps; and
- source cutoff, when present, remains between start and finish inclusive.

No new numeric wall-clock-to-monotonic equality claim is required.

### 5.5 Proof completion

Add direct tests that fail against the current candidate and pass only after
the required invariant is enforced:

1. one valid plus one malformed entry returns typed `CORPUS_UNAVAILABLE` and
   exposes no partial candidate;
2. wrong owner, malformed consumer, malformed pin, duplicate id/path, and
   unsafe path each invalidate the whole initial manifest;
3. an injected ordinary exception from `refine` and one from
   `construct_retrieval_contract` each return typed `CORPUS_UNAVAILABLE`, while
   an injected `BaseException` subclass is not swallowed;
4. a symlinked `knowledge` base resolving inside and outside is rejected, with
   a platform-neutral observation test;
5. positive elapsed with equal timestamps is rejected after recomputing the
   outer receipt hash; zero elapsed/equal timestamps remains accepted;
6. coordinate bogus evidence-set hashes across both receipt and handoff,
   recompute the receipt hash, and prove the result wrapper still rejects from
   its independent projection-derived hash;
7. directly reject every Amendment 3 handoff mismatch class: serialized bytes,
   token estimate, projection count, receipt count, classification,
   sensitivity, applied limit, elapsed, termination, and receipt hash;
8. replacement scanning must assert `EvidenceAvailableV1`, exactly one emitted
   projection, and at least two candidate build attempts; no negative wrapper
   is accepted by the test;
9. allocation proof must record and assert exact prefix order `UUID`, `UUID`,
   start clock, then R2 validation;
10. construct valid first-terminal grammar for all ten negative final outcomes
    and reject all-PASS history for each; and
11. timeout and cancellation firing only at the final third checkpoint each
    return no projections/handoff and an exact `PROJECTED=FAIL` receipt.

## 6. Verification And External Blocker Accounting

Sanitize provider/live and external-database environment variables exactly as
Amendment 2. Do not run the workspace doctor, network, hidden-core update,
PostgreSQL, Docker, live evidence, provider, product API, or external database
commands. Do not run concurrent full-suite processes against the shared tree.

Run serially:

1. the eleven new or strengthened adversarial proof groups in section 5.5;
2. focused exact P4-A1 suite;
3. `tests/unit/test_project_knowledge_pack.py`;
4. full sanitized non-live suite once, unfiltered;
5. the exact diagnostic remainder command retained by Amendment 2;
6. file-size, Project Knowledge, session-state and diff checks;
7. catalog/repository checks without writing generated truth; and
8. exact32, exact-eight repair diff, protected aggregate, staged-zero, secret,
   generated-residue and static-I/O audits.

Allowed pending results remain only reviewer-owned catalog drift and hidden-
core `2103a38f...` versus manifest pin `9b039ea6...` derivatives. The
diagnostic remainder must pass. Every other failure is `BLOCKED`.

## 7. Worker Return

Return exactly `REPAIR_4_COMPLETE_PENDING_REVIEW` or `BLOCKED`. Include:

- unchanged starting and ending HEAD;
- exact Amendment 4 and independent review hashes;
- exact-eight name-status and per-path hashes, plus exact32/no-path-33 proof;
- `P4A1-RR3-F1` through `P4A1-RR3-F5` source/test closure matrix;
- adversarial, focused, Project Knowledge, unfiltered and diagnostic results;
- separate catalog and hidden-core blocker evidence;
- protected six hashes and aggregate `bb180b1d...eaa7`;
- staged-zero, no-commit, file-size and zero-call evidence; and
- unchanged stop-after-mapping claim boundary.

Stop after return. Only the independent build reviewer/closer may decide
acceptance, catalog/status/continuity closure, commit, or FREEZE.

## 8. Agent Handoff Contract Control Block

| Field | Binding |
|---|---|
| route | `MULTI_AGENT_MULTI_ROLE` |
| rolePattern | work-order author, independent amendment reviewer, separate repair worker, independent build reviewer/closer |
| phase | `ROUND_4_AUTHORIZATION`, `REPAIR_4_EXECUTION`, `REREVIEW_4`, `CLOSURE_OR_BLOCK` |
| dispatchBaseHead | `d878001b6a1a536218b2c66019243510ef3f7aec` |
| executionBaseHead | same HEAD plus protected aggregate `bb180b1d...eaa7` |
| closureBaseHead | unchanged execution HEAD; reviewer binds the returned working-tree diff |
| changedSetScope(phase) | exact eight existing paths inside exact32; reviewer-owned decision artifacts remain separate |
| commitOwner(phase) | nobody before accepted rereview; reviewer/closer only after all closure gates |
| crossBatchIsolation | hidden core, manifest pin, catalog and continuity remain outside worker scope |
| nextMoveSurfaces | unchanged until accepted rereview and external-blocker disposition |

Designated closer: `INDEPENDENT_BUILD_REVIEWER_CLOSER`.

## 9. Reviewer Closure Conversion

- completionReviewPath:
  `docs/decisions/P4A1_GOVERNED_RETRIEVAL_BUILD_REREVIEW_4.md`
- reviewerOwnedClosurePaths: completion review first; catalog, status,
  continuity and commit paths only after semantic acceptance and separate
  closeout validation
- worker commit disposition: `WORKER_MUST_NOT_COMMIT`
- session-sync disposition: reviewer/closer owned and blocked until PASS

## 10. Checker Source Read-Ahead Block

The author read current Project Knowledge, session, file-size, catalog and
repository control sources, the current exact32 application/package owners,
and every test owner named in the Source Verification Block. Verification
commands confirm the repair; they are not used to discover artifact shape.

## 11. ADIF Defect Registry Disclosure

Query:
`python governance/compat/run_adif_defect_resolver.py --task-class "Work-order authoring / dispatch" --role dispatcher --lifecycle-phase pre-implementation --surface-selector receipt --risk-ceiling HIGH --max-results 20 --json`

Returned defectIds: `NONE`.

The operator explicitly released this Repair 4 after the final-repair stop in
Amendment 3. This amendment consolidates all current dependent findings and
does not silently waive the review-cost rule.

## 12. Dual Agent Surface Matrix

| Consumer class | Interface or owner surface | Authority and risk boundary | Evidence | Adapter boundary | Disposition |
|---|---|---|---|---|---|
| `INTERNAL_AGENT` | provider-free P4-A1 package and application composition | local R2 exact-eight repair only; no commit or external effect | accepted SPEC, rereview 3 and this source-verified packet | internal application function only | `CONTRACT_ONLY` |
| `EXTERNAL_AGENT_CLI_MCP` | no interface exists in P4-A1 | external ingress, authentication, mutation and receipt transport remain excluded | no current runtime evidence | no adapter is authorized | `N/A_WITH_REASON` |

## 13. Claim Boundary And Independent Review Return

This amendment authorizes only the provider-free INTERNAL/LOCAL_ONLY Repair 4
inside the existing P4-A1 foundation. It is not an LLM answer path, complete
RAG system, release, deployment, external-agent interface, LPCI1-REF
completion, P4-A, P4-A2, or deeper project implementation.

An independent reviewer returns exactly:

- `WORK_ORDER_AMENDMENT_4_REVIEW_PASS`;
- `WORK_ORDER_AMENDMENT_4_CHANGES_REQUIRED`; or
- `WORK_ORDER_AMENDMENT_4_BLOCKED_SOURCE_OR_SCOPE`.

Only the PASS token authorizes the Repair 4 worker prompt.
