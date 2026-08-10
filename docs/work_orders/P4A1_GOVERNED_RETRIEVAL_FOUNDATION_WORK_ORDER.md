# Work Order - P4-A1 Governed Retrieval Foundation BUILD

- Tranche: `P4-A1-GOVERNED-RETRIEVAL-2026-08-10`
- Risk ceiling: `R2`
- Status: `WORK_ORDER_CANDIDATE_PENDING_INDEPENDENT_AUTHORIZATION_REVIEW`
- Role: `IMPLEMENTATION_WORKER`
- Commit mode: `WORKER_MUST_NOT_COMMIT`
- Provider/network/product-API/external-database call budget: `0/0/0/0`
- Dispatch base HEAD: `d878001b6a1a536218b2c66019243510ef3f7aec`
- Stop boundary: return after the bounded P4-A1 mapping candidate; do not open
  P4-A, P4-A2, provider, RAG, vector/index, durable audit, UI, or deployment.

## Dispatch Prompt Envelope

Implement only the exact 31-path provider-free P4-A1 BUILD in this Work Order.
Rehydrate the authority packet, verify the execution checkpoint released by the
authorization reviewer, preserve every pre-existing governance/continuity path,
and stop at first failed prerequisite or verification command. Return unstaged
`COMPLETE_PENDING_REVIEW` evidence; do not commit, push, deploy, or call any
provider, network service, product API, or external database. Disposable local
SQLite is authorized only for the required SqlLedger parity test.

## 1. Mission and bounded outcome

Map the LPCI1 evidence-grounding pattern into this project as a local governed
retrieval foundation:

`validated query -> authenticated principal -> retrieval.query permission ->`
`all-shift assignment -> server corpus -> P3-C admission -> deterministic`
`lexical rank -> use-time revalidation -> bounded projection -> hashed receipt`

The only positive corpus in this tranche is
`PROJECT_KNOWLEDGE_LOCAL_V1`. `SHIFT_CONFIRMED_OPERATIONS_V1` and
`SHIFT_ADVISORY_MESSAGES_V1` remain `DEPENDENCY_BLOCKED`. The BUILD provides no
answer generation, provider key handling, LLM call, public/restricted document
authority, complete-document context, semantic RAG, vector search, durable
audit/persistence, production route, UI, or live deployment.

## 2. Authority chain and dependency release

| Authority | Exact evidence | Disposition |
|---|---|---|
| P4-A1 INTAKE | `docs/decisions/INTAKE_2026-08-10_P4A1_GOVERNED_RETRIEVAL.md`; SHA `7c32cd312ad4d889aa5039fbc32c032ee4312e0976224411cac106145b1ffde7` | ACCEPT |
| P4-A1 ADR | `docs/decisions/ADR_2026-08-10_P4A1_GOVERNED_RETRIEVAL.md`; SHA `8dbdfbaded8ed523eb465bc3c657620a323fafae465f5d0d0d66fe8cac6aa4fc` | ACCEPT |
| Main SPEC | `docs/specs/P4A1_GOVERNED_RETRIEVAL_SPEC.md`; SHA `f2385689b4ccca2bf669500bc984383f223e62b46fbf5a87f54587ad9530bb09` | ACCEPT |
| R9 appendix | `docs/specs/P4A1_GOVERNED_RETRIEVAL_RECEIPT_CONTRACT.md`; SHA `11af01c38a45e1891b752eb65c49c86827a6504c95d35d9ab2e8206a148df619` | ACCEPT - inseparable from SPEC |
| SPEC review | `docs/decisions/P4A1_GOVERNED_RETRIEVAL_SPEC_REVIEW.md`; SHA `ae7bf0275504abe650afa3286e5864ec97a902b76fe1520651d653a9d644c394` | `SPEC_REVIEW_PASS`; findings/waivers `NONE/NONE` |

The worker MUST NOT start until an independent authorization review pins this
Work Order hash, then a `SESSION_SYNC_STEWARD` completes the pre-BUILD release
below. Every one of the 31 BUILD paths MUST be clean or absent at release. A
missing review or continuity release keeps this packet on HOLD.

### Pre-BUILD continuity release - session-sync owned

After `WORK_ORDER_AUTHORIZATION_REVIEW_PASS`, and before any worker edit, the
session-sync steward changes only these six non-BUILD paths:

1. `SESSION/ACTIVE_SESSION_STATE.json`;
2. `CVF_SESSION/ACTIVE_SESSION_STATE.json`;
3. `SESSION/SESSION_MEMORY.md`;
4. `docs/implementation/EXECUTION_ROADMAP.md` (replace only the stale next-move
   statement; do not change the P4-A1 checkbox or claim BUILD completion);
5. `knowledge/manifest.json` (update only the Project Context source pin for the
   changed roadmap bytes); and
6. a new successor
   `SESSION/handoffs/AGENT_HANDOFF_2026-08-10_P4A1_GOVERNED_RETRIEVAL_WORK_ORDER.md`.

The synchronized state MUST set mode
`p4a1_governed_retrieval_build_authorized`, active role
`IMPLEMENTATION_WORKER`, the successor handoff, and next move to this exact
Work Order plus authorization-review hashes. It MUST preserve P4-A/P4-A2 and
all deeper development as parked. The successor handoff records
`executionBaseHead`, exact31-clean evidence, and a secret-safe sorted
path/status/SHA-256 manifest for every pre-existing non-BUILD dirty path.
Project session-state, file-size, Project Knowledge, repository, and diff checks
must pass, including the refreshed exact roadmap source pin. The worker prompt
MUST pin the released successor-handoff hash.

## 3. Roles and independence

- Work Order author: owns this dispatch contract, not BUILD acceptance.
- Implementation worker: changes only the exact 31 paths and does not commit.
- Independent BUILD reviewer/closer: designated closer; reproduces evidence,
  owns the completion review, and alone may accept/commit BUILD material.
- Session-sync steward: separately reconciles continuity after accepted BUILD.
- Operator: owns any later authority expansion or live/provider checkpoint.

No actor may combine candidate authorship with its independent BUILD review.

## 4. Source Verification Block

| Claimed item | Source file | Verified line/section | Verified path or symbol | Owning interface/function/schema | Verification class | Disposition |
|---|---|---|---|---|---|---|
| Root test import paths are explicit | `pyproject.toml` | `tool.pytest.ini_options.pythonpath` | `pythonpath` | root project configuration | VALUE_SET | ACCEPT - governed-retrieval path is absent |
| JWT principal boundary exists | `apps/workspace-api/src/workspace_api/dependencies.py` | line 31 | `get_principal` | workspace API dependency | EXISTS | ACCEPT |
| Unknown permission actions deny | `packages/cvf-runtime/src/cvf_runtime/permission.py` | lines 28, 100-106 | `_ACTION_MIN_ROLE`; `require_action` | CVF runtime permission map | RUNTIME_BEHAVIOR | ACCEPT - `retrieval.query` is absent |
| Assignment admission accepts a shared unit | `apps/workspace-api/src/workspace_api/application/assignment_scope.py` | line 23 | `AssignmentScope.require_shift` | application assignment boundary | EXISTS | ACCEPT |
| Ledger exposes one transaction seam and unit-aware reads | `packages/operations-ledger/src/operations_ledger/ledger.py` | lines 28-216 | `Ledger.transaction`; list/get/correction/assignment methods | Ledger protocol | EXISTS | ACCEPT |
| Six canonical P3-C branches fail on missing digest owner | `packages/retrieval-contracts/src/retrieval_contracts/constructor.py` | lines 179-182 | `SOURCE_DIGEST_OWNER_MISSING` | P3-C constructor | RUNTIME_BEHAVIOR | ACCEPT |
| Active retention remains fail-closed | `packages/retrieval-contracts/src/retrieval_contracts/constructor.py` | lines 217-239 | retention admission branch | P3-C constructor | RUNTIME_BEHAVIOR | ACCEPT |
| Canonical source facts/selectors are centralized | `packages/retrieval-contracts/src/retrieval_contracts/canonical.py` | lines 129, 193 | `source_facts`; `expected_selector` | P3-C canonical helpers | EXISTS | ACCEPT |
| Canonical JSON fixes UUID/datetime/enum/string rules | `packages/retrieval-contracts/src/retrieval_contracts/canonical.py` | lines 203-249 | `canonical_json_bytes`; `canonical_sha256` | P3-C canonical serializer | RUNTIME_BEHAVIOR | ACCEPT |
| P3-C evidence and 65,536 text ceiling exist | `packages/retrieval-contracts/src/retrieval_contracts/contract_models.py` | lines 210-223 | `RetrievalReadyV1` | P3-C result schema | VALUE_SET | ACCEPT |
| Project Knowledge has a public P3-C source model | `packages/retrieval-contracts/src/retrieval_contracts/source_models.py` | lines 12-16 | `ProjectKnowledgeSourceV1` | P3-C source schema | EXISTS | ACCEPT |
| Project Knowledge has a positive P3-C construction branch | `packages/retrieval-contracts/src/retrieval_contracts/constructor.py` | lines 161-187 | `RecordType.PROJECT_KNOWLEDGE` branch | P3-C constructor | RUNTIME_BEHAVIOR | ACCEPT |
| Sensitivity belongs to the P3-A candidate | `packages/refinery-bridge/src/refinery_bridge/output_models.py` | lines 84-99 | `ContextCandidateV1.sensitivity` | P3-A candidate schema | EXISTS | ACCEPT |
| P3-B literals remain non-load-bearing | `packages/retrieval-contracts/src/retrieval_contracts/contract_models.py` | lines 161-165 | `NOT_PROVEN`; `NOT_EVALUATED`; `NO_LOAD_BEARING_CALLER` | `DataScopeEvidenceV1` | LITERAL_INVARIANT | ACCEPT |
| Project Knowledge is INTERNAL and locally eligible | `knowledge/manifest.json` | lines 4, 8-43 | `classification`; `allowedConsumers`; `sourcePins`; `eligibleForLocalIndex` | Project Knowledge manifest | VALUE_SET | ACCEPT |
| Audit write surfaces exist and are forbidden here | `packages/cvf-runtime/src/cvf_runtime/audit.py`; `packages/operations-ledger/src/operations_ledger/ledger.py` | lines 46, 216 | `AuditLog.record`; `Ledger.append_audit` | audit interfaces | EXISTS | ACCEPT - zero calls required |

### Current-runtime freshness verification

Before editing, rerun exact-hash checks for every ACCEPT source above and search
for `retrieval.query`, `packages/governed-retrieval`, the six R5 digest-owner
symbols, and all 31 paths. Any changed source fact or pre-existing BUILD-path
change returns `BLOCKED_SOURCE_DRIFT` to the Work Order author.

### New design-owned symbols

These are new contract outputs, not claims that current runtime already owns
them: package `governed_retrieval`; strict V1 request/filter/budget, corpus,
citation/projection, receipt/stage/count/limit/termination, handoff and ten result
models; lexical offset mapping/ranking; canonical hashes; and application
composition modules named in the path ceiling. Their sole authority is the
reviewed SPEC pair.

## 5. Exact BUILD changed-set ceiling - 31 paths

Existing paths to modify:

1. `pyproject.toml`
2. `packages/cvf-runtime/src/cvf_runtime/permission.py`

New pure-package paths:

3. `packages/governed-retrieval/README.md`
4. `packages/governed-retrieval/pyproject.toml`
5. `packages/governed-retrieval/contracts/governed_retrieval.schema.json`
6. `packages/governed-retrieval/src/governed_retrieval/__init__.py`
7. `packages/governed-retrieval/src/governed_retrieval/model_base.py`
8. `packages/governed-retrieval/src/governed_retrieval/enums.py`
9. `packages/governed-retrieval/src/governed_retrieval/request_models.py`
10. `packages/governed-retrieval/src/governed_retrieval/corpus.py`
11. `packages/governed-retrieval/src/governed_retrieval/lexical.py`
12. `packages/governed-retrieval/src/governed_retrieval/evidence_models.py`
13. `packages/governed-retrieval/src/governed_retrieval/projection.py`
14. `packages/governed-retrieval/src/governed_retrieval/receipt_models.py`
15. `packages/governed-retrieval/src/governed_retrieval/hashing.py`
16. `packages/governed-retrieval/src/governed_retrieval/result_models.py`

New application paths:

17. `apps/workspace-api/src/workspace_api/application/governed_retrieval.py`
18. `apps/workspace-api/src/workspace_api/application/_governed_retrieval_admission.py`
19. `apps/workspace-api/src/workspace_api/application/_governed_retrieval_sources.py`
20. `apps/workspace-api/src/workspace_api/application/_governed_retrieval_knowledge.py`
21. `apps/workspace-api/src/workspace_api/application/_governed_retrieval_revalidation.py`

New proof paths:

22. `tests/unit/_p4a1_retrieval_fixtures.py`
23. `tests/unit/test_p4a1_retrieval_models.py`
24. `tests/unit/test_p4a1_retrieval_lexical.py`
25. `tests/unit/test_p4a1_retrieval_projection.py`
26. `tests/unit/test_p4a1_retrieval_receipts.py`
27. `tests/unit/test_p4a1_retrieval_dependencies.py`
28. `tests/cvf/test_p4a1_retrieval_authorization.py`
29. `tests/cvf/test_p4a1_governed_retrieval.py`
30. `tests/integration/test_p4a1_retrieval_ledger_parity.py`
31. `tests/contract/test_p4a1_governed_retrieval_schema.py`

Every new Python file MUST stay at or below 300 physical lines. A necessary
32nd path is not worker-autonomous; stop and return it as a source-backed scope
finding.

## 6. Protected and forbidden scope

Zero worker changes are allowed under:

- `packages/operations-ledger/**`, `packages/operations-domain/**`, and
  `packages/retrieval-contracts/**`;
- API route/main, workspace web, AI gateway, provider adapters, migrations,
  audit implementations, catalog/status/knowledge, roadmap, and continuity;
- the six `operations_domain.retrieval_digests.*` R5 owners.

Do not copy/alias/call application digest helpers, invent a generic digest,
weaken P3-C or retention, add a route, accept client corpus descriptors, log raw
query/evidence, persist receipts, construct answer text, or create provider,
embedding, vector, index, memory, deployment, or secret configuration.

## 7. Implementation contract

### 7.1 Pure package

- Enforce the reviewed exact V1 schemas, strict fields/enums, ten structural
  result variants, caps, normalization, integer score, seven-field tie-break,
  duplicate rule, source offset transducer, match-preserving projection, and
  canonical receipt/citation/evidence hashes.
- Import only standard library, Pydantic, and public `retrieval_contracts`.
  Perform no I/O, clock/id creation, secret lookup, environment, auth, Ledger,
  API, network, provider, or audit operation.
- Expose immutable corpus descriptors for exactly the three SPEC corpora. Mark
  both operational corpora `DEPENDENCY_BLOCKED`; do not make them readable.

### 7.2 Application composition

- Add only `"retrieval.query": "viewer"` to `_ACTION_MIN_ROLE`; preserve
  unknown-action denial and every other permission mapping.
- Execute R3 in exact order. Open one `Ledger.transaction()` only after auth and
  permission; pass the same unit to all assignment/read/reload/final checks.
- Treat P3-A sensitivity as explicit execution metadata from the same candidate
  and revalidate it with the unchanged `RetrievalReadyV1`; do not create a
  second provenance envelope.
- The Project Knowledge adapter receives repository root, P3-A control bundle,
  clock/ids, dedupe context, and quarantine route explicitly. It validates the
  current manifest, local consumer, INTERNAL classification, active owner and
  disposition, pins, raw document digest, local-index flag, and local retention
  before positive evidence.
- No production default exists for the P3-A control bundle. Tests inject it;
  absence fails closed. Do not claim autonomous or deployed operation.
- Use neither `AuditLog.record` nor `Ledger.append_audit`; receipts are response
  data only. Register no HTTP route.

### 7.3 Fail-closed corpus boundary

The operational adapters may prove dependency-blocked registry behavior but
MUST NOT read or admit canonical/Message records. P3-C missing-owner outcomes
remain unchanged. Digest success never substitutes for retention authority.
No confirmed-record or Message retrieval claim is allowed.

## 8. Roadmap-to-Work-Order Trace Matrix

| Roadmap/SPEC obligation | Work Order section | Evidence path/class | Dispatch state |
|---|---|---|---|
| P4-A1 governed deterministic filtered retrieval | 5, 7 | pure package + focused proofs | READY_AFTER_RELEASE |
| R1 dependency/I/O boundary | 5-7 | dependency AST/static tests | READY_AFTER_RELEASE |
| R2-R4 request/auth/corpus contract | 7.1-7.2 | models + authorization call spies | READY_AFTER_RELEASE |
| R5 P3-C/fail-closed sources | 6, 7.3 | dependency/adversarial tests | READY_AFTER_RELEASE |
| R6-R8 rank/revalidate/projection | 7 | lexical/projection/Ledger parity tests | READY_AFTER_RELEASE |
| R9 and normative appendix | 2, 7 | schema + golden-byte/hash tests | READY_AFTER_RELEASE |
| R10-R11 handoff/result/provider-zero | 6-7 | model/static/call proofs | READY_AFTER_RELEASE |
| R12 evolution/seven proof classes/LPCI1 boundary | 10-14 | full evidence return + claim boundary | READY_AFTER_RELEASE |
| Stop after project mapping | 1, 6, 14 | exact diff and zero-call evidence | READY_AFTER_RELEASE |

## 9. ADIF Defect Registry Disclosure

Query:
`python governance/compat/run_adif_defect_resolver.py --task-class work_order --role WORK_ORDER_AUTHOR --lifecycle-phase WORK_ORDER --risk-ceiling MEDIUM --max-results 20 --json`

Returned defectIds: `NONE` (`totalCandidates=0`, `truncated=false`). The resolver
is read-only and this disclosure is not evidence that a worker understood it.

## 10. Agent Handoff Contract Control Block

| Field | Binding |
|---|---|
| Contract source | project `AGENTS.md` sections `Governed Seven-Step Workflow`, `Provider-Neutral Role Contract`, and `Handoff and Tranche Closure Protocol`; project precedent `docs/work_orders/P3C_RETRIEVAL_READY_DATA_CONTRACT_WORK_ORDER.md` sections 3, 9, and 12-14 |
| route | `MULTI_AGENT_MULTI_ROLE` |
| rolePattern | three-or-more-agent chain with worker-no-commit split |
| phase | `DISPATCH_AUTHORING`, `EXECUTION`, `CLOSURE`, `SESSION_SYNC` |
| dispatchBaseHead | `d878001b6a1a536218b2c66019243510ef3f7aec` |
| executionBaseHead | pre-BUILD successor handoff pins released HEAD and governance manifest |
| closureBaseHead | execution HEAD remains unchanged; closer binds returned exact diff |
| changedSetScope(phase) | dispatch artifacts; exact31 BUILD; reviewer-owned closure; continuity-only sync |
| traceScope(phase, actor) | each author owns only its phase command/diff/call trace |
| commitOwner(phase) | dispatch steward; nobody in EXECUTION; reviewer/closer in CLOSURE; sync steward in SESSION_SYNC |
| crossBatchIsolation | worker paths clean/absent at release; hashed pre-existing governance set remains untouched |
| nextMoveSurfaces | session-sync-owned six-path pre-BUILD release; reviewer-owned closure sync only after accepted BUILD |

Designated closer: `INDEPENDENT_BUILD_REVIEWER_CLOSER`.

## Reviewer Closure Conversion

- `completionReviewPath`:
  `docs/decisions/P4A1_GOVERNED_RETRIEVAL_BUILD_REVIEW.md`
- `reviewerOwnedClosurePaths`: completion review; `IMPLEMENTATION_STATUS.json`;
  catalog registry/generated catalog; Project Knowledge context/manifest pins;
  P4 cross-repository coordination; canonical/mirror session state, session
  memory, and successor handoff.
- Worker return is never closure. The closer may accept/commit exact31 only
  after independent reproduction, then uses a separate continuity commit.

## 11. Required execution order

1. Rehydrate `AGENTS.md`, manifest, current session front doors, authority chain,
   SPEC pair, review, Work Order, and authorization review.
2. Verify mode `p4a1_governed_retrieval_build_authorized`, the released successor
   handoff hash and dirty-manifest hash; prove every exact31 path clean/absent
   and every protected baseline path unchanged.
3. Re-run source freshness searches and hashes. Stop on drift.
4. Add permission action and pure package/models/schema with tests first.
5. Add lexical, projection, hashes, corpus registry, and adversarial proofs.
6. Add application composition and Project Knowledge-only positive path.
7. Run focused tests, then full non-live suite and repository gates once each.
8. Audit exact31/protected diff, zero calls/secrets/generated residue, and return
   unstaged evidence to the independent reviewer. Stop; do not open a next lane.

## 12. Verification commands

```powershell
Remove-Item Env:DASHSCOPE_API_KEY,Env:ALIBABA_API_KEY,Env:CVF_ALIBABA_API_KEY,Env:CVF_BENCHMARK_ALIBABA_KEY,Env:DEEPSEEK_API_KEY,Env:LIVE_POSTGRES_DATABASE_URL,Env:DATABASE_URL -ErrorAction SilentlyContinue
python -m pytest -q tests/unit/test_p4a1_retrieval_models.py tests/unit/test_p4a1_retrieval_lexical.py tests/unit/test_p4a1_retrieval_projection.py tests/unit/test_p4a1_retrieval_receipts.py tests/unit/test_p4a1_retrieval_dependencies.py tests/cvf/test_p4a1_retrieval_authorization.py tests/cvf/test_p4a1_governed_retrieval.py tests/integration/test_p4a1_retrieval_ledger_parity.py tests/contract/test_p4a1_governed_retrieval_schema.py
python -m pytest -q
python scripts/check_file_size.py
python scripts/check_project_knowledge.py
python scripts/generate_catalog.py --check
python scripts/check_session_state.py
python scripts/testing/validate_repository.py
git diff --check
git diff --name-status
git status --short
```

The worker also runs AST/static guards proving forbidden imports/I/O, provider
symbols, digest helper use, audit writes, and protected-path changes are absent.
The full suite runs only after the listed environment names are removed from the
worker process. It MUST NOT run live-evidence scripts, the network-fetching
workspace doctor, PostgreSQL, Docker, or a configured external database.
Disposable local SQLite is required for parity and is reported separately from
external-call accounting. No live-provider release gate is authorized;
therefore this BUILD cannot make a release-quality or live-governance claim.

## 13. Worker return contract

Return exactly one of `COMPLETE_PENDING_REVIEW` or `BLOCKED`. Include:

- starting/ending HEAD (identical) and authorization-review hash;
- exact `git diff --name-status` limited to the 31 paths;
- pre-existing governance manifest unchanged proof;
- focused/full test and every gate command/result/count;
- independent recomputation evidence for schema, normalization offsets, score,
  tie order, budgets, citation/evidence/receipt hashes, and tamper failures;
- one-unit InMemory/SQLite identity evidence and PostgreSQL `NOT_CLAIMED`;
- corpus matrix: Project Knowledge positive; both operational corpora blocked;
- provider/network/product-API/external-database/audit-write counts
  `0/0/0/0/0`, plus the local SQLite test count;
- file-size evidence for each new Python file; secret/residue audit;
- bounded claim and all stop conditions checked.

Leave every change unstaged. Do not commit or push.

## 14. Stop conditions, acceptance, and claim boundary

Stop `BLOCKED` on source/hash/authority drift, dirty exact31 input, a 32nd path,
missing explicit P3-A input, weakened auth/retention/P3-C behavior, nonzero
external/audit call, test/gate failure, file-size failure, secret/residue, or an
attempt to enable either operational corpus.

Acceptance requires independent mapping of AC-01 through AC-12, exact31 diff,
all checks PASS, zero calls/writes, and findings/waivers `NONE/NONE`. The maximum
candidate claim is:

`Project-native P4-A1 local-only, deterministic, permission-gated,
P3-C-grounded, bounded-projection retrieval with ephemeral hashed receipts;
operational corpora remain dependency-blocked; provider attempts are zero.`

This is not LPCI1 Web completion and not a complete RAG system. It proves no
LLM answer, API-key path, public/restricted/confidential document access,
full-document context, semantic/vector retrieval, durable audit/persistence,
provider safety, production API/UI, deployment, or production readiness.

After return, the worker stops. Only the independent reviewer may review this
candidate. P4-A/P4-A2 and deeper project development remain parked until fresh
operator authority after this mapping tranche.
