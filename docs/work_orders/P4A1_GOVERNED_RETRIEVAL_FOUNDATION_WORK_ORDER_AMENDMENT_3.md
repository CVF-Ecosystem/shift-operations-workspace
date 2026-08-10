# P4-A1 Governed Retrieval Foundation Work Order Amendment 3

- Amendment id: `P4A1-GOVERNED-RETRIEVAL-FOUNDATION-WO-A3-2026-08-10`
- Parent Work Order SHA-256: `b9889e4e207f408c705210207bfd1fcb32720ad7258522c2d0446e0d59d837e6`
- Amendment 1 SHA-256: `92241ce23d84b80e6112e54e2cde1ddf4c005b9ea6e0146d3586f5792de499e1`
- Amendment 2 SHA-256: `4bd2f9a7d6252a7d8970fd8b86cc1e052c89b4ae4adc608a65ed9fd14d3a39ee`
- Repair 2 rereview: `docs/decisions/P4A1_GOVERNED_RETRIEVAL_BUILD_REREVIEW_2.md`
- Repair 2 rereview SHA-256: `bbe16df476d303acb365d5bf32ea4469d5f61714c3a1fc892c9c6c412e7e8464`
- Rereview disposition: `REPAIR_2_REVIEW_CHANGES_REQUIRED`
- Round-three checkpoint: `OPERATOR_RELEASED_2026-08-10`
- Authority checkpoint HEAD: `d878001b6a1a536218b2c66019243510ef3f7aec`
- Risk: `R2` unchanged
- Status: `PENDING_INDEPENDENT_AMENDMENT_REVIEW`
- Commit mode: `WORKER_MUST_NOT_COMMIT`
- Provider/network/product-API/external-database/audit call budget: `0`

## 1. Purpose And Unchanged Boundary

The operator explicitly cleared the round-three review-cost checkpoint after
receiving the consolidated Repair 2 rereview. This amendment authorizes one
final same-scope repair for the six accepted findings in that rereview. It does
not authorize another sequential repair cascade.

The objective, exact32 ceiling, R2 risk, zero-external-effect class, role route,
commit owner, accepted SPEC, and stop-after-mapping boundary remain unchanged.
No corpus, route, provider, answer, durable audit, persistence, UI, deployment,
P4-A, P4-A2, LPCI1-REF, semantic RAG, vector search, or deeper project lane is
opened.

No Repair 3 source or test edit begins until this exact amendment receives an
independent `WORK_ORDER_AMENDMENT_3_REVIEW_PASS`.

## 2. Finding-To-Repair Trace

| Repair 2 rereview finding | Parent finding | Required closure |
|---|---|---|
| `P4A1-RR2-F1` | `P4A1-RR1-F6` | recompute and cross-bind evidence, byte, token, projection-count and receipt facts |
| `P4A1-RR2-F2` | `P4A1-RR1-F3/F4` | exact manifest shapes, owner/consumer authority, symlink refusal and typed exception boundary |
| `P4A1-RR2-F3` | retained F11 | service allocation before R2, distinct UUIDv4 identities and consistent timing |
| `P4A1-RR2-F4` | `P4A1-RR1-F7/F8` | final stop produces a truthful terminal stage and no partial evidence |
| `P4A1-RR2-F5` | `P4A1-RR1-F6/F7` | negative receipt stage grammar is enforced at construction |
| `P4A1-RR2-F6` | `P4A1-RR1-F9` | direct adversarial proof for every repaired edge |

Waivers: `NONE`.

## 3. Source Verification Block

| Claimed item | Source file | Verified line/section | Verified path or symbol | Owning interface/function/schema | Verification class | Disposition |
|---|---|---|---|---|---|---|
| Positive result binding is incomplete | `packages/governed-retrieval/src/governed_retrieval/result_models.py` | lines 41-75 | `_bindings` | `EvidenceAvailableV1` | RUNTIME_BEHAVIOR | ACCEPT - repair target |
| Receipt identity/timing validation is incomplete | `packages/governed-retrieval/src/governed_retrieval/receipt_models.py` | lines 50-91 | `_stage_order_and_time` | `RetrievalReceiptV1` | RUNTIME_BEHAVIOR | ACCEPT - repair target |
| Handoff facts are caller-provided fields | `packages/governed-retrieval/src/governed_retrieval/receipt_models.py` | lines 95-140 | `FutureContextHandoffV1` | future context handoff schema | EXISTS | ACCEPT - positive wrapper must cross-bind |
| Service context is allocated after structural validation | `apps/workspace-api/src/workspace_api/application/governed_retrieval.py` | lines 90-105 | `execute_governed_retrieval` | application composition | RUNTIME_BEHAVIOR | ACCEPT - repair target |
| Final stop uses receipt-emission stage | `apps/workspace-api/src/workspace_api/application/governed_retrieval.py` | lines 269-275 | `check_stopped` | positive emission boundary | RUNTIME_BEHAVIOR | ACCEPT - repair target |
| Stop helper overwrites terminal stage with receipt PASS | `apps/workspace-api/src/workspace_api/application/_governed_retrieval_sources.py` | lines 94-114 | `check_stopped` | termination receipt construction | RUNTIME_BEHAVIOR | ACCEPT - repair target |
| Runtime manifest loader is not exact-shape closed | `apps/workspace-api/src/workspace_api/application/_governed_retrieval_knowledge.py` | lines 80-99 | `_load_manifest` | Project Knowledge admission | RUNTIME_BEHAVIOR | ACCEPT - repair target |
| Runtime owner and consumer checks are incomplete | `apps/workspace-api/src/workspace_api/application/_governed_retrieval_knowledge.py` | lines 102-107, 150-172 | `_entry_admissible` | Project Knowledge admission | RUNTIME_BEHAVIOR | ACCEPT - repair target |
| Runtime path containment does not refuse every symlink | `apps/workspace-api/src/workspace_api/application/_governed_retrieval_knowledge.py` | lines 110-147 | `_resolve_contained` | Project Knowledge path admission | RUNTIME_BEHAVIOR | ACCEPT - repair target |
| Revalidation catches only selected exception classes | `apps/workspace-api/src/workspace_api/application/_governed_retrieval_revalidation.py` | lines 116-167 | `revalidate_knowledge_candidates` | use-time Project Knowledge revalidation | RUNTIME_BEHAVIOR | ACCEPT - repair target |
| Initial admission catches only selected manifest failures | `apps/workspace-api/src/workspace_api/application/_governed_retrieval_sources.py` | lines 208-254 | `admit_knowledge_candidates` | Project Knowledge source admission | RUNTIME_BEHAVIOR | ACCEPT - repair target |
| Canonical top-level and nested manifest vocabularies | `scripts/check_project_knowledge.py` | lines 12-16, 165-182 | `TOP_FIELDS`; `ENTRY_FIELDS`; `PIN_FIELDS`; `OWNERS`; `CONSUMERS` | Project Knowledge manifest owner | VALUE_SET | ACCEPT - source for the explicit retrieval subset below |
| Repository-pack-only validation is broader than retrieval admission | `scripts/check_project_knowledge.py` | lines 168-225, 247-270 | `validate_pack` | Project Knowledge repository checker | RUNTIME_BEHAVIOR | ACCEPT - exact count/mapping/date/purpose/trigger/correction rules remain checker-only |
| Negative fixture fabricates all-PASS history | `tests/unit/_p4a1_retrieval_fixtures.py` | lines 167-195 | `minimal_negative_receipt` | P4-A1 proof fixture | RUNTIME_BEHAVIOR | ACCEPT - repair target |
| Factory proof covers only cooperative identities | `tests/cvf/test_p4a1_governed_retrieval.py` | lines 218-250 | `test_execution_metadata_uses_injected_uuid4_factory_and_utc_now_not_caller_ids` | application proof | RUNTIME_BEHAVIOR | ACCEPT - expand adversarially |
| Cancellation proof stops before final emission | `tests/integration/test_p4a1_retrieval_ledger_parity.py` | lines 189-201 | `test_retrieval_cancelled_variant_reachable` | termination proof | RUNTIME_BEHAVIOR | ACCEPT - expand final checkpoint |
| Positive contract tests do not cover coordinated mismatch | `tests/contract/test_p4a1_governed_retrieval_schema.py` | lines 124-167 | positive/negative construction tests | schema proof | RUNTIME_BEHAVIOR | ACCEPT - expand adversarially |

No source item is blocked. No new runtime field, result variant, receipt stage,
corpus id, provider surface, route, or persistence owner is introduced.

## 4. Exact Changed-Set Authority

The Repair 3 worker may edit only the parent exact31 paths plus the existing
test-only path 32 authorized by Amendment 2:

`tests/unit/test_project_knowledge_pack.py`.

The final ceiling remains at most exact32. No worker-created path 33 is
authorized. Within exact32, `pyproject.toml`,
`packages/cvf-runtime/src/cvf_runtime/permission.py`, and
`tests/unit/test_project_knowledge_pack.py` remain byte-protected during Repair
3 because none of the six findings requires them.

All six Phase A paths, the protected 15-row aggregate
`bb180b1dfdd180d8d8350492d0803e5adb6eb08d4cc3385a4204f6a18b00eaa7`,
all governance artifacts, `.cvf/manifest.json`, the hidden core, catalog,
status, knowledge, session, roadmap, handoff, API route, UI, provider, audit,
deployment and operational-corpus source paths remain forbidden to the worker.

## 5. Required Repair Behavior

### 5.1 Positive integrity closure

At `EvidenceAvailableV1` construction, independently recompute from the exact
ordered projection tuple:

- citation ids;
- evidence-set hash using the canonical bare citation dumps and projection
  dumps;
- canonical serialized projection bytes;
- the `UTF8_BYTES_DIV_2_ESTIMATE_V1` token estimate;
- projection count; and
- snippet code-point total.

Require those values to equal the receipt and handoff values. Also require
`receipt.counts.projections_emitted` to equal the positive projection count,
handoff classifications/sensitivities to equal the derived positive facts,
and every already-specified limit, termination, elapsed and receipt-hash edge
to remain bound. Coordinated tampering across receipt and handoff must fail even
when the attacker recomputes the outer receipt hash.

### 5.2 Project Knowledge exact admission

Consume the following deliberately narrower retrieval-runtime subset of the
Project Knowledge owner contract without importing the checker script into
runtime:

- exact `TOP_FIELDS`, `ENTRY_FIELDS` and `PIN_FIELDS` shapes;
- top-level `schemaVersion="1.0"`,
  `packId="shift-operations-project-knowledge"`, and
  `classification="INTERNAL"`;
- an entries list at or below the existing 100-entry ceiling;
- unique safe entry ids and unique safe entry paths;
- entry `classification="INTERNAL"`, `disposition="ACTIVE"`, owner in the
  exact `OWNERS` allowlist, strict `eligibleForLocalIndex=true`, and the exact
  active retention literal;
- `allowedConsumers` is a duplicate-free list containing
  `LOCAL_GOVERNED_AGENT`, every value belongs to the exact `CONSUMERS`
  allowlist, and no unknown or malformed value is accepted; and
- a non-empty source-pin list with unique safe paths, exact pin shape, valid
  SHA-256 declarations and current raw-byte equality.

The repository checker remains the sole owner of pack-maintenance rules that
do not affect retrieval eligibility: exactly three current entries,
path-specific id/owner/source-pin mappings, exact complete consumer-set parity,
review-date policy, purpose text, refresh triggers, correction policy, and the
current markdown inventory. Repair 3 must not duplicate those checker-only
rules into runtime and must not claim full runtime parity with `validate_pack`.

Reject an absolute path, parent traversal, resolved escape, or any symlink in
the traversed path from the governed root to an entry or source pin. An
in-root symlink is still rejected.

Malformed top-level, entry, pin, owner, consumer, metadata, path and initial
admission failures return safe `CORPUS_UNAVAILABLE`, except the existing typed
limit outcome. During use-time revalidation, malformed/unreadable/path,
overflow, P3-A, P3-C and other ordinary `Exception` failures remove the
individual candidate as stale; no raw exception escapes. Do not catch
`BaseException` classes such as process termination or keyboard interruption.

### 5.3 Service identity and time ordering

Construct the execution context before structural request validation so the
service invokes `uuid4_factory` exactly twice and captures start time before
R2 for every safe result, including invalid request. After successful
validation, populate requested limits without reallocating identity or start
time.

Require receipt and correlation identities to be distinct UUIDv4 values.
Require `finished_at_utc >= started_at_utc`, require positive `elapsed_ms` to
have a strictly later finish, and when present require source cutoff to be
between start and finish inclusive. Keep monotonic elapsed measurement and
independent start/source-cutoff/finish clock calls.

### 5.4 Receipt stage grammar and final stop

Enforce at receipt construction:

- `EVIDENCE_AVAILABLE` has PASS for the first ten stages and
  `RECEIPT_EMITTED=PASS`;
- every negative receipt has exactly one terminal `FAIL` or `DENY` among the
  first ten stages;
- stages before that terminal stage are PASS;
- stages after it and before receipt emission are NOT_RUN;
- authentication failure is exactly
  `AUTHENTICATED=DENY / AUTHENTICATION_FAILED`;
- permission failure is exactly
  `PERMISSION_AUTHORIZED=DENY / ACCESS_DENIED`;
- initial assignment failure is exactly
  `ASSIGNMENT_AUTHORIZED=DENY / ACCESS_DENIED`;
- final assignment drift is exactly `REVALIDATED=DENY / ACCESS_DENIED`;
- every access-denial stage after the terminal stage and before receipt
  emission is NOT_RUN;
- non-access negative outcomes use FAIL and their allowed reason code; and
- `RECEIPT_EMITTED` remains PASS for every returned receipt.

At the final timeout/cancellation checkpoint, record `PROJECTED=FAIL` with the
exact termination reason, then emit the safe negative receipt. It may overwrite
the prior projection PASS because no positive projection is returned. Never
record the terminal condition in `RECEIPT_EMITTED`, and never expose partial
projections or handoff.

### 5.5 Proof completion

Replace every all-PASS negative fixture with a valid outcome-specific stage
history. Preserve construction/reachability of all ten variants while proving
their receipt semantics, not only their wrapper discriminator.

## 6. Required Adversarial Proof

Add direct tests inside existing exact32 paths for:

1. coordinated bogus evidence hashes with a recomputed receipt hash;
2. serialized-byte, token-estimate, projection-count, receipt-count,
   classification, sensitivity, limit, elapsed and termination mismatches;
3. exact top-level, entry and pin shapes plus wrong metadata;
4. unknown owner, malformed/empty consumer, absolute/parent/resolved escape and
   in-root symlink refusal;
5. initial malformed admission returns safe typed output and use-time
   `Exception` becomes stale omission;
6. service allocation order is UUID, UUID, start clock, then R2 validation;
7. duplicate/non-v4 identities and inconsistent start/cutoff/finish/elapsed
   facts are rejected;
8. cancellation and timeout firing only at the final third checkpoint produce
   no projections/handoff and a truthful `PROJECTED=FAIL` receipt;
9. every negative variant rejects an all-PASS history and accepts its valid
   first-terminal grammar; access probes also reject authentication mapped to
   FAIL and every wrong access stage/reason pairing; and
10. unfit-first/fitting-second projection replacement is exercised directly at
    output ceiling one.

Tests must reproduce each current defect before the repair and pass only after
the corresponding invariant is enforced. Platform-neutral symlink-component
tests are mandatory even if local symlink creation is unavailable.

## 7. Verification And External Blocker Accounting

Sanitize all provider/live and external-database environment variables exactly
as Amendment 2. Do not run the workspace doctor, network, hidden-core update,
PostgreSQL, Docker, live evidence or provider commands. Do not run concurrent
full-suite processes against the shared worktree.

Run in order:

1. focused exact P4-A1 suite;
2. `tests/unit/test_project_knowledge_pack.py`;
3. targeted adversarial tests for `P4A1-RR2-F1` through `P4A1-RR2-F6`;
4. full sanitized non-live suite once, unfiltered;
5. the exact diagnostic remainder command from Amendment 2;
6. file-size, Project Knowledge, session-state and diff checks;
7. catalog/repository checks without writing generated truth; and
8. exact32, protected aggregate, staged-zero, secret, generated-residue and
   static-I/O audits.

Allowed pending results remain only the reviewer-owned catalog drift and the
hidden-core `2103a38f...` versus manifest pin `9b039ea6...` derivatives. The
diagnostic remainder must pass. Every other failure is `BLOCKED`.

## 8. Worker Return

Return exactly `REPAIR_3_COMPLETE_PENDING_REVIEW` or `BLOCKED`. Include:

- unchanged starting and ending HEAD;
- exact Amendment 3 and authorization-review hashes;
- exact32 name-status and per-path hashes;
- `P4A1-RR2-F1` through `P4A1-RR2-F6` source/test closure matrix;
- focused, targeted, Project Knowledge, unfiltered and diagnostic results;
- separate catalog and hidden-core blocker evidence;
- protected six hashes and aggregate `bb180b1d...eaa7`;
- staged-zero, no-commit, file-size and zero-call evidence; and
- unchanged stop-after-mapping claim boundary.

Stop after return. Only the independent build reviewer/closer may decide
acceptance, catalog/status/continuity closure, commit or FREEZE.

## 9. Agent Handoff Contract Control Block

| Field | Binding |
|---|---|
| route | `MULTI_AGENT_MULTI_ROLE` |
| rolePattern | work-order author, independent amendment reviewer, separate repair worker, independent build reviewer/closer |
| phase | `ROUND_3_AUTHORIZATION`, `REPAIR_3_EXECUTION`, `REREVIEW_3`, `CLOSURE_OR_BLOCK` |
| dispatchBaseHead | `d878001b6a1a536218b2c66019243510ef3f7aec` |
| executionBaseHead | same HEAD plus protected aggregate `bb180b1d...eaa7` |
| closureBaseHead | unchanged execution HEAD; reviewer binds the returned working-tree diff |
| changedSetScope(phase) | existing exact32 only; reviewer-owned decision artifacts remain separate |
| commitOwner(phase) | nobody before accepted rereview; reviewer/closer after all closure gates |
| crossBatchIsolation | hidden core, manifest pin, catalog and continuity remain outside worker scope |
| nextMoveSurfaces | unchanged until accepted rereview and external-blocker disposition |

Designated closer: `INDEPENDENT_BUILD_REVIEWER_CLOSER`.

## 10. Checker Source Read-Ahead Block

The author read current source for Project Knowledge, session, file-size,
catalog and repository checks, plus the current exact32 application/package
and test owners cited above. The verification commands confirm the repair;
they are not used to discover required artifact shape.

## 11. ADIF Defect Registry Disclosure

Query:
`python governance/compat/run_adif_defect_resolver.py --task-class "Work-order authoring / dispatch" --role dispatcher --lifecycle-phase pre-implementation --surface-selector receipt --risk-ceiling HIGH --max-results 20 --json`

Returned defectIds: `NONE`.

Separately applicable review-control source: `CVF_ADIF-0026`. Its round-three
checkpoint was disclosed in the Repair 2 rereview and explicitly cleared by
the operator before this amendment was authored. This amendment consolidates
all dependent findings into one final repair and does not weaken the stop rule.

## 12. Dual Agent Surface Matrix

| Consumer class | Interface or owner surface | Authority and risk boundary | Evidence | Adapter boundary | Disposition |
|---|---|---|---|---|---|
| `INTERNAL_AGENT` | provider-free P4-A1 package and application composition | local R2 exact32 repair only; no commit or external effect | accepted SPEC, rereview 2 and this source-verified packet | internal application function only | `CONTRACT_ONLY` |
| `EXTERNAL_AGENT_CLI_MCP` | no interface exists in P4-A1 | external ingress, authentication, mutation and receipt transport remain excluded | no current source or runtime evidence | no adapter is authorized | `N/A_WITH_REASON` |

## 13. Claim Boundary And Independent Review Return

This amendment authorizes only the final provider-free INTERNAL/LOCAL_ONLY
P4-A1 foundation repair. It is not an LLM answer path, complete RAG system,
release, deployment, external-agent interface, LPCI1-REF completion, P4-A,
P4-A2 or deeper project implementation.

An independent reviewer returns exactly:

- `WORK_ORDER_AMENDMENT_3_REVIEW_PASS`;
- `WORK_ORDER_AMENDMENT_3_CHANGES_REQUIRED`; or
- `WORK_ORDER_AMENDMENT_3_BLOCKED_SOURCE_OR_SCOPE`.

Only the PASS token authorizes the Repair 3 worker prompt.
