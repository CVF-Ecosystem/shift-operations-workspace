# P4-A1 Governed Retrieval Foundation Work Order Amendment 5

- Amendment id: `P4A1-GOVERNED-RETRIEVAL-FOUNDATION-WO-A5-2026-08-10`
- Parent Work Order SHA-256: `b9889e4e207f408c705210207bfd1fcb32720ad7258522c2d0446e0d59d837e6`
- Amendment 1 SHA-256: `92241ce23d84b80e6112e54e2cde1ddf4c005b9ea6e0146d3586f5792de499e1`
- Amendment 2 SHA-256: `4bd2f9a7d6252a7d8970fd8b86cc1e052c89b4ae4adc608a65ed9fd14d3a39ee`
- Amendment 3 SHA-256: `847a0a9705415ee6105f47c6b0b5eac0bd964ec8bc74849e60afd6d1af902661`
- Amendment 4 SHA-256: `7c8189e37170a2aa4200737137c47ac19d16389716d2de7cc6d7a6d1c48ebbf0`
- Amendment 4 review SHA-256: `b64d2433704837cf810ea43011614e09c44289cf50088990897e328799bd16fd`
- Authority checkpoint HEAD: `d878001b6a1a536218b2c66019243510ef3f7aec`
- Risk: `R2` unchanged
- Status: `PENDING_INDEPENDENT_AMENDMENT_REVIEW`
- Commit mode: `WORKER_MUST_NOT_COMMIT`
- External-call budget: `0`

## 1. Purpose And Disposition

Repair 4 correctly stopped because four authorized Python test files exceed the
hard 300-line ceiling after the required RR3-F1 through RR3-F5 adversarial
proof was added. The source repairs are within the ceiling, staged paths are
zero, and no runtime defect is reopened by this amendment.

The local file-size policy forbids executable-file exceptions. This amendment
therefore authorizes one test-only structural split. It does not authorize
semantic compression, assertion deletion, runtime edits, a debt-baseline entry,
or an exception-registry entry.

The P4-A1 objective, accepted SPEC, R2 ceiling, provider-free behavior,
protected Phase A aggregate, and stop-after-mapping boundary remain unchanged.
No P4-A, P4-A2, LPCI1-REF, provider, answer, route, UI, audit, persistence,
deployment, vector search, semantic RAG, or deeper project lane is opened.

No Amendment 5 worker edit begins until this exact amendment receives an
independent `WORK_ORDER_AMENDMENT_5_REVIEW_PASS`.

## 2. Source Verification Block

| Claimed item | Source file | Verified line/section | Verified path or symbol | Owning interface/function/schema | Verification class | Disposition |
|---|---|---|---|---|---|---|
| Python warn/hard ceilings are 250/300 | `scripts/check_file_size.py` | line 32 | `EXECUTABLE_THRESHOLDS` | file-size guard | LITERAL_INVARIANT | ACCEPT |
| Executable paths cannot use the exception registry | `scripts/check_file_size.py` | lines 242-248 | `is_executable` | file-size guard | RUNTIME_BEHAVIOR | ACCEPT |
| Python over hard must split and cannot use an exception | `docs/reference/FILE_SIZE_GUARD.md` | lines 16 and 78-80 | `.py` | local file-size policy | LITERAL_INVARIANT | ACCEPT |
| Contract test owner is 324 lines | `tests/contract/test_p4a1_governed_retrieval_schema.py` | current file | `test_manifest_entry_boundary_99_100_101_no_silent_truncation` | contract test owner | RUNTIME_BEHAVIOR | ACCEPT - split target |
| Main CVF test owner is 354 lines | `tests/cvf/test_p4a1_governed_retrieval.py` | current file | `test_execution_metadata_uses_injected_uuid4_factory_and_utc_now_not_caller_ids` | application test owner | RUNTIME_BEHAVIOR | ACCEPT - split target |
| Authorization test owner is 346 lines | `tests/cvf/test_p4a1_retrieval_authorization.py` | current file | `test_identity_and_start_time_allocated_before_r2_even_on_invalid_request` | authorization test owner | RUNTIME_BEHAVIOR | ACCEPT - split target |
| Ledger parity test owner is 355 lines | `tests/integration/test_p4a1_retrieval_ledger_parity.py` | current file | `test_one_valid_one_malformed_entry_fails_whole_corpus_no_partial_candidate` | integration test owner | RUNTIME_BEHAVIOR | ACCEPT - split target |
| Four companion test paths do not yet exist | this amendment section 5 | Exact Amendment 5 Worker Changed Set | four paths marked new | Amendment 5 document authority | DOC_ONLY_NEW | ACCEPT |

No runtime/source symbol is proposed or renamed. The four new paths are
document-authorized outputs, not claims that pre-existing source files exist.

## 3. Protected Phase A Pre-Entry Restoration

Independent Amendment 5 review reproduced a checkout-only CRLF drift on all
six protected Phase A paths. Each current LF-normalized hash exactly matches
the approved Phase A post-image, but every raw-byte hash differs and the
Project Knowledge check fails on `PROJECT_CONTEXT.md`. The test-split worker
must not repair this drift.

After Amendment 5 review PASS and before worker dispatch, the designated
`PRE_ENTRY_SESSION_SYNC_STEWARD` may normalize only CRLF and bare CR to LF in
these exact six paths. The steward must first prove that the LF-normalized hash
equals the listed post-image. Any content drift beyond line endings is
`BLOCKED_PROTECTED_CONTENT_DRIFT`.

| Protected path | Current CRLF count | Required raw LF post-image SHA-256 |
|---|---:|---|
| `CVF_SESSION/ACTIVE_SESSION_STATE.json` | 16 | `dc7051824f62c06f6e95c6c0bd8352544ff4405f89c592363e92e3e8f28a67b9` |
| `SESSION/ACTIVE_SESSION_STATE.json` | 1364 | `c9c9e2e0bb46d6b2585ab091deb6a721e455babccc7f8d3eb407178056c59c69` |
| `SESSION/SESSION_MEMORY.md` | 375 | `68c366677fb6a7a39229d371cc88acbf3ec27b247ff74f468070ffbded154e91` |
| `docs/implementation/EXECUTION_ROADMAP.md` | 600 | `e5fa3a5695f5817a7152e2ea983d456b38219ab1a79a5ba769a936016fd86f9e` |
| `knowledge/PROJECT_CONTEXT.md` | 34 | `f2318222889f428f1b6951510c79e2889255e3e3594179076efbfdb54c363a34` |
| `knowledge/manifest.json` | 150 | `e561a9bdb34cb9eb7949ec7fc6afc0ab9cc488d4984245d6c0d54f8974d963df` |

The steward then proves:

1. CRLF and bare-CR counts are zero on all six paths;
2. all six raw hashes equal the table;
3. the protected 15-row aggregate equals
   `bb180b1dfdd180d8d8350492d0803e5adb6eb08d4cc3385a4204f6a18b00eaa7`;
4. Project Knowledge and session-state checks PASS;
5. HEAD remains unchanged and staged paths remain zero; and
6. no other path changes during this restoration.

The steward records the compact pre-entry receipt at
`docs/decisions/P4A1_GOVERNED_RETRIEVAL_AMENDMENT_5_PRE_ENTRY_RESTORATION.md`.
The test-split worker remains forbidden from editing all six protected paths.
If the six raw hashes and aggregate are not exact at worker entry, return
`BLOCKED_PROTECTED_ENTRY_DRIFT` without modifying a test.

## 4. Bound Repair 4 Post-Image

These current hashes are the Amendment 5 entry image. The worker must not edit
the four non-split paths.

| Path | Lines | SHA-256 | Amendment 5 disposition |
|---|---:|---|---|
| `apps/workspace-api/src/workspace_api/application/_governed_retrieval_knowledge.py` | 299 | `ea6789b16eed466a10f53505c7e8ff05a3b2810bd88e1a18cfd25e7f09a803bb` | byte-identical |
| `apps/workspace-api/src/workspace_api/application/_governed_retrieval_sources.py` | 284 | `9dbf3a5c176cd7c6668bf59ceecfad3f6b77d6ae2112672842288694710f5876` | byte-identical |
| `packages/governed-retrieval/src/governed_retrieval/receipt_models.py` | 229 | `6497cacf86c5c4298d2d32600c8c6959d0466ccc12f2bee505ebe74668561fda` | byte-identical |
| `tests/contract/test_p4a1_governed_retrieval_schema.py` | 324 | `d1605ed9935a0bcb3b029209ec498baff63cb19eb176512ea2c0cf6697023cea` | split owner |
| `tests/cvf/test_p4a1_governed_retrieval.py` | 354 | `0eee2a428c0360c81d3f5f55164a25741effa56295cd1fc6e9defd6be073318b` | split owner |
| `tests/cvf/test_p4a1_retrieval_authorization.py` | 346 | `e77100c65655ba9d77d9fe1ba07918ddb9fb1b44eb97db2f39086d81863321ad` | split owner |
| `tests/integration/test_p4a1_retrieval_ledger_parity.py` | 355 | `f23656afd842e59b70b0c057b96d129501c312ac4904087e4a26363af9bba826` | split owner |
| `tests/unit/test_p4a1_retrieval_receipts.py` | 300 | `af703ab2b250d7a38a27b71f3ee96c585ef1c056ea96053c2518f17538b430b5` | byte-identical |

If any bound hash differs at entry, stop `BLOCKED_ENTRY_IMAGE_DRIFT`; do not
infer a new baseline.

## 5. Exact Amendment 5 Worker Changed Set

The worker may edit or create only these exact eight test paths:

1. `tests/contract/test_p4a1_governed_retrieval_schema.py`
2. `tests/contract/test_p4a1_governed_retrieval_source_limits.py` - new
3. `tests/cvf/test_p4a1_governed_retrieval.py`
4. `tests/cvf/test_p4a1_governed_retrieval_boundaries.py` - new
5. `tests/cvf/test_p4a1_retrieval_authorization.py`
6. `tests/cvf/test_p4a1_retrieval_authorization_ordering.py` - new
7. `tests/integration/test_p4a1_retrieval_ledger_parity.py`
8. `tests/integration/test_p4a1_retrieval_project_knowledge.py` - new

The final P4-A1 candidate ceiling becomes exact36. No path 37 is authorized.
Every production path, `tests/unit/test_p4a1_retrieval_receipts.py`, all other
exact32 paths, governance artifacts, catalog, knowledge, session, roadmap,
handoff, hidden core, `.cvf`, and the six protected Phase A paths are forbidden
to the worker.

## 6. Required Move-Only Split

Move complete top-level test functions and their test-only helpers. Preserve
test names, assertion bodies, parameter values, failure expectations, and
RR3-F1 through RR3-F5 semantics. Minimal import, module-docstring, helper-copy,
and repository-root path adjustments required by relocation are allowed.

| Existing owner | New companion | Complete symbols to move |
|---|---|---|
| `tests/contract/test_p4a1_governed_retrieval_schema.py` | `tests/contract/test_p4a1_governed_retrieval_source_limits.py` | `_minimal_manifest_entries`; `test_manifest_entry_boundary_99_100_101_no_silent_truncation`; `test_document_length_boundary_65535_65536_65537_no_silent_truncation` |
| `tests/cvf/test_p4a1_governed_retrieval.py` | `tests/cvf/test_p4a1_governed_retrieval_boundaries.py` | `test_execution_metadata_uses_injected_uuid4_factory_and_utc_now_not_caller_ids`; `test_no_p4a1_source_file_imports_a_provider_module`; `test_request_model_rejects_unknown_enum_value_for_corpus_id`; `test_request_model_rejects_a_new_unknown_field` |
| `tests/cvf/test_p4a1_retrieval_authorization.py` | `tests/cvf/test_p4a1_retrieval_authorization_ordering.py` | `test_structural_validation_failure_makes_zero_authorization_calls`; `test_identity_and_start_time_allocated_before_r2_even_on_invalid_request`; `test_one_ledger_unit_reused_through_assignment_and_final_check` |
| `tests/integration/test_p4a1_retrieval_ledger_parity.py` | `tests/integration/test_p4a1_retrieval_project_knowledge.py` | `_sha256_of`; `_pk_entry`; `test_one_valid_one_malformed_entry_fails_whole_corpus_no_partial_candidate`; `test_initial_exception_boundary_and_symlinked_base_rejection`; `test_owner_retention_and_consumer_admission_rules_are_strict` |

All eight changed files must be at or below 300 lines. Prefer each new
companion below the 250-line warning threshold. Do not merge statements,
remove comments that explain adversarial intent, weaken exact type checks,
replace direct assertions with permissive loops, or hide tests behind shared
generic metaprogramming merely to reduce line count.

## 7. Acceptance And Verification

The Amendment 5 worker runs only after independent authorization review and
the section 3 pre-entry receipt, then runs serially with provider/live/
external-database variables sanitized:

1. targeted collection for all four new companions and four original owners;
2. the eleven Amendment 4 section 5.5 adversarial proof groups;
3. the focused exact P4-A1 suite;
4. `tests/unit/test_project_knowledge_pack.py`;
5. `python scripts/check_file_size.py`;
6. Project Knowledge, session-state, catalog, repository and diff checks;
7. exact36/no-path-37, exact-eight Amendment 5 diff, protected aggregate,
   staged-zero, secret, generated-residue and static-I/O audits.

The worker must not run the workspace doctor, full suite, diagnostic remainder,
network, provider, product API, PostgreSQL, Docker, audit, deployment, hidden-
core update, or external database command. The broad suites already passed in
Repair 4 and this amendment changes only test layout. Independent review may
request a fresh broad serial run only if collection or semantic parity is not
proven by the bounded suite.

Acceptance requires:

- all eight changed test files at or below 300 lines;
- the four new companions collected and executed;
- the same relevant test count before and after the split, with no renamed,
  skipped, deselected, xfailed, or deleted test;
- all targeted and focused results PASS;
- the four non-split Repair 4 paths remain at their bound hashes;
- protected aggregate remains
  `bb180b1dfdd180d8d8350492d0803e5adb6eb08d4cc3385a4204f6a18b00eaa7`;
- exact36 and no path 37;
- HEAD unchanged, staged zero, no commit, no external call; and
- unchanged stop-after-mapping claim boundary.

## 8. Worker Return

Return exactly `REPAIR_5_TEST_SPLIT_COMPLETE_PENDING_REVIEW` or `BLOCKED`.
Include entry/end HEAD, Amendment 5 and review hashes, exact-eight name-status
and per-path hashes, before/after test inventory, all line counts, targeted and
focused results, file-size and local guard results, exact36/no-path-37 proof,
four immutable post-image hashes, protected aggregate, staged-zero and zero-
call evidence.

Stop after return. Only the independent reviewer/closer may accept the Repair
4 semantic result, run any broader suite, create closure artifacts, commit, or
park P4-A1.

## 9. Worker Autonomy / No-Question Rule

The worker may perform non-destructive reads, move the exact named symbols,
repair imports inside the exact-eight scope, and rerun the bounded commands.
Any need to edit a ninth path, change an assertion's meaning, update a bound
runtime/test path, use an exception/debt registry, or make an external call is
an immediate `BLOCKED` return, not a request to widen scope.

## 10. Intake Role Routing Decision

| Field | Decision |
|---|---|
| intake summary | Repair 4 is semantically implemented but blocked only by four test files above the hard line ceiling |
| scope classification | test-layout repair only |
| risk sensitivity | R2 retained; zero runtime behavior change |
| selected route mode | `MULTI_AGENT_MULTI_ROLE` |
| role separation basis | dispatch author, independent amendment reviewer, worker, independent reviewer/closer |
| escalation condition | any ninth path, semantic test change, runtime drift, protected drift, or external effect |

## 11. Agent Handoff Contract Control Block

| Field | Binding |
|---|---|
| route | `MULTI_AGENT_MULTI_ROLE` |
| rolePattern | dispatch author, independent amendment reviewer, separate worker, independent reviewer/closer |
| phase | `ROUND_5_AUTHORIZATION`, `TEST_SPLIT_EXECUTION`, `REREVIEW_5`, `CLOSURE_OR_BLOCK` |
| dispatchBaseHead | `d878001b6a1a536218b2c66019243510ef3f7aec` |
| executionBaseHead | same HEAD plus section 3 pre-entry receipt, section 4 entry hashes and protected aggregate |
| closureBaseHead | unchanged execution HEAD; reviewer binds the returned working-tree diff |
| changedSetScope(phase) | exact eight test paths; four existing plus four new; final exact36 |
| commitOwner(phase) | nobody before accepted rereview; reviewer/closer only after closure gates |
| crossBatchIsolation | Core continuity-read-cost roadmap and all downstream non-P4-A1 work remain isolated |
| nextMoveSurfaces | unchanged until accepted rereview; session-sync remains reviewer/closer-owned |

Designated closer: `INDEPENDENT_BUILD_REVIEWER_CLOSER`.

## 12. Reviewer Closure Conversion

- `completionReviewPath`:
  `docs/decisions/P4A1_GOVERNED_RETRIEVAL_BUILD_REREVIEW_4.md`
- `reviewerOwnedClosurePaths`: completion review plus separately authorized
  catalog/status/continuity paths only after semantic acceptance
- allowed pending worker-return token:
  `REPAIR_5_TEST_SPLIT_COMPLETE_PENDING_REVIEW`
- forbidden final residue: `BLOCKED`, `PENDING_INDEPENDENT_AMENDMENT_REVIEW`,
  `NOT_RUN`, unchecked required items, or file-size failure
- predecessor closure fact: Amendment 4 review at the hash pinned above

## 13. Dual Agent Surface Matrix

| Surface | Role | Interface | Authority/risk boundary | Evidence | Adapter boundary |
|---|---|---|---|---|---|
| `INTERNAL_AGENT` | test-split worker | local filesystem and local pytest | exact-eight tests, R2, no commit/external call | worker return plus hashes and test inventory | direct governed workspace edit |
| `EXTERNAL_AGENT_CLI_MCP` | not used | N/A with reason | provider/CLI/MCP execution is outside scope | zero-call accounting | deferred; no adapter authorized |

## 14. Checker Source Read-Ahead Block

The author read the local file-size policy and checker, all four over-ceiling
test owners, the Amendment 1 Phase A authority and review, the Phase A review
receipt, current raw and LF-normalized protected bytes, and every bound Repair
4 post-image. Verification commands confirm the packet; they are not used to
discover worker-output shape.

## 15. ADIF Defect Registry Disclosure

Query:
`python governance/compat/run_adif_defect_resolver.py --task-class work_order_authoring --role dispatcher --lifecycle-phase pre-dispatch --risk-ceiling MEDIUM --max-results 20 --json`

Returned defectIds: `NONE`.

## 16. Negative And Fail-Condition Scan

Closure fails on any missing moved test, changed test name, reduced relevant
test count, weakened assertion, file above 300 lines, ninth worker path,
runtime or protected drift, exception/debt registry edit, stage/commit/push,
external call, exact36 mismatch, path 37, or claim beyond the P4-A1 mapping
foundation.

## 17. Claim Boundary

This amendment authorizes only a structural test split needed to satisfy the
existing local maintainability guard. It does not by itself prove Repair 4
semantic acceptance, a complete RAG system, provider behavior, live deployment,
durable audit, operational-corpus retrieval, or product readiness.
