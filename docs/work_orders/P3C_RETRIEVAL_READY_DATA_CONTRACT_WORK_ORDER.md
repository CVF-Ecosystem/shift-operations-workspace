# Work Order - P3-C Retrieval-Ready Data Contract BUILD

- Work order id: `P3C-RETRIEVAL-READY-DATA-CONTRACT-BUILD-2026-08-07`
- Tranche: `P3-C-RETRIEVAL-READY-DATA-CONTRACT-2026-08-06`
- Risk: `R2`
- Control-chain phase: `WORK_ORDER`
- Status: `WORK_ORDER_CANDIDATE_PENDING_INDEPENDENT_AUTHORIZATION_REVIEW`
- Authoring base: `2e01873`
- Parent ADR SHA-256: `f7c78d3e2e3a6e1de462b64e2b906a0cbb7e35e9f2d521b3e528aba6b2ea05f2`
- SPEC SHA-256: `0e2388623857423091aa76ba49e1338d57f6fd504aebd47bd1062e2b13356ed8`
- SPEC review: `SPEC_REVIEW_PASS`, findings/waivers `NONE/NONE`
- Commit mode: `WORKER_MUST_NOT_COMMIT`
- Provider/product-network/POST calls: `0/0/0`

## Dispatch Prompt Envelope

Mission: implement only the reviewed deterministic P3-C local contract package
and its additive P3-A source token, tests, schema export and catalog truth.

Authority source: the exact ADR, SPEC and independent review chain named below.
This packet is a candidate until independent authorization review passes.

Worker return: `COMPLETE_PENDING_REVIEW`, with the exact 22-path unstaged diff,
command evidence and zero-call accounting. The worker must not commit or push.

Hard boundary: no runtime retrieval caller, ledger/database, persistence,
provider, network, router, vector/index, tenant subsystem, digest-owner
promotion, `data_scope` enforcement or production claim.

## 1. Mission

Create a new pure local Python package at `packages/retrieval-contracts/` that
implements SPEC R1-R23 and AC-01 through AC-12. Add only the reviewed P3-A
`CANONICAL_OPERATIONAL_RECORD` source token needed for typed canonical inputs.
Current canonical record types must fail closed with
`SOURCE_DIGEST_OWNER_MISSING`; advisory Message and Project Knowledge fixtures
provide the bounded positive paths.

Success is an exact 22-path, zero-I/O, zero-provider candidate whose focused
and full non-live tests pass, whose schema bytes are reproducible, and whose
catalog truth remains `partial`/contract-only with no runtime claim.

## 2. Authority chain

- Operator authority: continued P3-C roadmap instruction and same-scope repair
  continuity; repeated confirmation is not required without a boundary change.
- Active state: `SESSION/ACTIVE_SESSION_STATE.json`.
- Active handoff:
  `SESSION/handoffs/AGENT_HANDOFF_2026-08-06_P3C_RETRIEVAL_READY_CONTRACT.md`.
- INTAKE:
  `docs/decisions/INTAKE_2026-08-06_P3C_RETRIEVAL_READY_DATA_CONTRACT.md`.
- ADR:
  `docs/decisions/ADR_2026-08-06_P3C_RETRIEVAL_READY_DATA_CONTRACT.md`.
- DESIGN pass:
  `docs/decisions/P3C_RETRIEVAL_READY_DATA_CONTRACT_DESIGN_REREVIEW.md`.
- SPEC: `docs/specs/P3C_RETRIEVAL_READY_DATA_CONTRACT_SPEC.md`.
- SPEC pass:
  `docs/decisions/P3C_RETRIEVAL_READY_DATA_CONTRACT_SPEC_REREVIEW.md`.
- Roadmap: `docs/implementation/EXECUTION_ROADMAP.md`, P3-C row and current
  single-next-move section.

Any hash drift, authority conflict or changed objective stops BUILD before an
edit. This Work Order does not grant BUILD until independent authorization
review passes and continuity records the exact pushed execution baseline.

## 3. Roles and independence

- Dispatcher/Orchestrator: current governed session.
- Work Order author: `WORK_ORDER_AUTHOR`.
- Implementation worker: `IMPLEMENTATION_WORKER` after authorization closure.
- Independent reviewer: must not be the implementation worker.
- Repair worker: may repair findings only inside the unchanged 22 paths.
- Commit steward: commits only after independent `REVIEW_PASS`.
- Session-sync steward: owns separate continuity commits and never mixes them
  into the BUILD changed set.

One agent may transition from worker to repair worker, but may not approve its
own BUILD. No additional operator confirmation is required for allowed-scope
local repairs, reruns or review responses. Operator intervention is required
only for path/objective/claim/risk expansion, secret or provider use, external
effect, destructive action, deployment, public release or commit-owner change.

## 4. Source Verification Block

| Claimed item | Source file | Verified line/section | Verified path or symbol | Owning interface/function/schema | Disposition |
|---|---|---|---|---|---|
| Current P3-A source enum has three values | `packages/refinery-bridge/src/refinery_bridge/enums.py` | `class SourceType` | `SourceType` | P3-A input enum | ACCEPT - additive fourth value is new BUILD work |
| Envelope carries source type and source provenance | `packages/refinery-bridge/src/refinery_bridge/input_models.py` | `class RefineryEnvelopeV1` | `RefineryEnvelopeV1` | P3-A admitted input | ACCEPT |
| Candidate/result bind redacted candidate and fingerprint | `packages/refinery-bridge/src/refinery_bridge/output_models.py` | `ContextCandidateV1`; `RefineryResultV1` | `ContextCandidateV1`; `RefineryResultV1` | P3-A output union | ACCEPT |
| Canonical operational models are package-owned | `packages/operations-domain/src/operations_domain/models.py` | named model classes | `OperationalEvent`; `Task`; `CustomerRequest`; `Incident`; `Handover`; `Message`; `Correction`; `Shift` | operations-domain | ACCEPT |
| Report stored digest and private helpers exist | `packages/operations-domain/src/operations_domain/report_models.py` | `ReportContent`; helper definitions | `ReportContent.snapshot_digest`; `_canonical_bytes`; `_recompute_record_digest` | ReportContent internal validation | ACCEPT - private helpers are forbidden imports |
| Application digest helpers exist outside allowed dependency direction | `apps/workspace-api/src/workspace_api/application/report_snapshot.py`; `handover_service.py` | `compute_source_digest` | `compute_source_digest` | workspace-api application layer | ACCEPT - forbidden import/copy boundary |
| Root test path wires packages explicitly | `pyproject.toml` | `[tool.pytest.ini_options]` | `pythonpath` | root pytest configuration | ACCEPT - one additive path required |
| Package-local project pattern exists | `packages/refinery-bridge/pyproject.toml`; `packages/operations-domain/pyproject.toml` | `[project]`; setuptools `src` discovery | `pyproject.toml` | package build metadata | ACCEPT |
| Refinery contract currently records zero calls and no retrieval/runtime caller | `packages/refinery-bridge/contracts/refinery_contract.yaml` | `constraints` | `provider_calls`; `network_calls`; `runtime_caller`; `retrieval_or_rag_claim` | P3-A contract | ACCEPT |
| Data scope has no load-bearing runtime caller | `docs/cvf/CVF_CONTROL_MAPPING.md` | `data_scope` row | `data_scope` | control mapping | ACCEPT |
| Catalog is generated from registry | `scripts/generate_catalog.py` | `REGISTRY_PATH`; `CATALOG_MD_PATH`; `--write/--check` | `enrich_metrics`; `render_markdown` | project catalog generator | ACCEPT |

No current `packages/retrieval-contracts/` path or `retrieval_contracts` symbol
is claimed to exist. Every new path and symbol below is explicitly planned
BUILD output, not a source-verification ACCEPT claim.

### Current-runtime freshness verification

At authoring base `2e01873`, repository search confirms:

- no `packages/retrieval-contracts/` directory;
- no root pytest path `packages/retrieval-contracts/src`;
- no `CANONICAL_OPERATIONAL_RECORD` token in P3-A source;
- no public digest-owner contract in the two allowed dependency packages;
- private Report helpers and application digest helpers named above remain
  present and must not be treated as the missing public owner.

The authorization reviewer must rerun these searches at the candidate commit.
Any new collision or owner surface returns the Work Order for correction.

## 5. Exact BUILD changed-set ceiling - 22 paths

Every path below is mandatory. BUILD may create or modify exactly these paths:

1. `pyproject.toml`
2. `packages/refinery-bridge/src/refinery_bridge/enums.py`
3. `packages/refinery-bridge/contracts/refinery_contract.yaml`
4. `tests/unit/test_refinery_contract.py`
5. `packages/retrieval-contracts/README.md`
6. `packages/retrieval-contracts/pyproject.toml`
7. `packages/retrieval-contracts/contracts/retrieval_contract.schema.json`
8. `packages/retrieval-contracts/src/retrieval_contracts/__init__.py`
9. `packages/retrieval-contracts/src/retrieval_contracts/enums.py`
10. `packages/retrieval-contracts/src/retrieval_contracts/common.py`
11. `packages/retrieval-contracts/src/retrieval_contracts/source_models.py`
12. `packages/retrieval-contracts/src/retrieval_contracts/contract_models.py`
13. `packages/retrieval-contracts/src/retrieval_contracts/canonical.py`
14. `packages/retrieval-contracts/src/retrieval_contracts/constructor.py`
15. `tests/unit/test_p3c_retrieval_contract_models.py`
16. `tests/unit/test_p3c_retrieval_contract_constructor.py`
17. `tests/unit/test_p3c_retrieval_contract_adversarial.py`
18. `tests/unit/test_p3c_retrieval_contract_digest_guards.py`
19. `tests/contract/test_p3c_retrieval_contract_schema.py`
20. `docs/catalog/MODULE_REGISTRY.json`
21. `docs/catalog/MODULE_CATALOG.md`
22. `IMPLEMENTATION_STATUS.json`

Paths 1-4 and 20-22 exist at authorization time. Paths 5-19 must be absent.
Any extra, missing, renamed, generated cache, lockfile, fixture, snapshot,
continuity or governance path stops the worker before handoff.

## 6. Protected and forbidden scope

Protected from BUILD changes:

- all `SESSION/**`, `CVF_SESSION/**`, roadmap, ADR, SPEC, review and Work Order
  files;
- `packages/operations-domain/**` including both private Report helpers;
- every `apps/**`, ledger, database, migration, router and web path;
- existing P3-A pipeline/candidate/result semantics outside the exact additive
  SourceType and contract declaration;
- the isolated rejected governed-plan-runner evidence branch.

Forbidden actions and claims:

- import/call/alias/wrap/copy `_canonical_bytes` or
  `_recompute_record_digest` into `retrieval_contracts`;
- import or copy either `workspace_api` digest helper;
- create a generic Pydantic-dump digest owner;
- add a source-owner helper to operations-domain;
- query/index/vector/persistence/database/filesystem/environment/provider/
  network/subprocess/router/ledger behavior;
- tenant authorization, minimization/placement enforcement, runtime retrieval,
  RAG, production readiness or AI-governance claims;
- provider/key/config reads, mock output presented as governance evidence,
  stage, commit or push by the worker.

## 7. Implementation contract

### 7.1 Package and public surface

- Follow the package-local `pyproject.toml` plus `src/` pattern and root
  `pythonpath` wiring already used by sibling packages.
- Package dependencies are exactly Pydantic plus local imports from
  `refinery_bridge` and `operations_domain`; no reverse import is permitted.
- Split model/canonical/constructor ownership across the planned files so each
  governed source file remains below the file-size threshold without compressed
  prose or hidden generated logic.
- Export only reviewed public enums, input/source/reference/result models,
  canonical helpers and the total constructor from `__init__.py`.

### 7.2 Models, construction and fail-closed behavior

- Implement the exact R1 enums, R2 strict bounds and R3 input field set.
- Bind the existing P3-A envelope/result/candidate/fingerprint exactly per R4.
- Implement the complete R5 eligibility matrix and R6 projection selectors.
- Message and Project Knowledge advisory positive cases follow R7 exactly.
- Every canonical type follows R8 and returns
  `SOURCE_DIGEST_OWNER_MISSING` at this BUILD baseline.
- Implement R9-R15 version/reference/scope/lifecycle/retention/data-scope/
  provenance models without extra fields or permissive defaults.
- Implement R16/R17 canonical bytes, content digest, chunk id and revalidation
  token; independent tests recompute each without implementation helpers.
- Implement the disjoint R18 union and fixed multi-defect precedence.
- Preserve R19 deterministic bytes/order and R22 version rejection.

### 7.3 Private-helper guard

AST/static tests must inspect imports and attribute access across every
`retrieval_contracts` source file. They must fail on direct import, module
attribute access, alias, wrapper or call of:

- `operations_domain.report_models._canonical_bytes`;
- `operations_domain.report_models._recompute_record_digest`.

They must also reject imports from `workspace_api`, `operations_ledger`,
`cvf_runtime`, FastAPI, SQLAlchemy, provider, vector/index and retrieval runtime
modules. Existing private helper use inside operations-domain is untouched.

### 7.4 Contract/schema and catalog truth

- Add `CANONICAL_OPERATIONAL_RECORD` to P3-A SourceType and exact YAML contract
  vocabulary; existing P3-A behavior and tests must remain byte/meaning stable.
- Export the strict result-union JSON Schema deterministically and prove the
  checked-in file equals a fresh model-generated schema.
- Add one `retrieval-contracts` module registry entry with status `partial`,
  dependencies `refinery-bridge` and `operations-domain`, exact tests and a
  claim boundary of local contract/no runtime caller.
- Regenerate `MODULE_CATALOG.md` only through
  `python scripts/generate_catalog.py --write`.
- Update implementation status only with bounded P3-C BUILD truth; do not claim
  P4, retrieval runtime, provider behavior or production readiness.

## 8. Roadmap-to-Work-Order trace matrix

| Roadmap/SPEC requirement | Work Order instruction | Output/evidence | Status |
|---|---|---|---|
| New bounded sibling owner | 5, 7.1 | paths 5-14; import tests | READY_FOR_REVIEW |
| Exact source classes/eligibility/version | 7.2 | model/constructor tests | READY_FOR_REVIEW |
| Deterministic field-bound chunk | 7.2 | golden digest/chunk tests | READY_FOR_REVIEW |
| Single workspace/no tenant | 7.2 | scope/tenant negative tests | READY_FOR_REVIEW |
| Lifecycle/correction/freeze revalidation | 7.2 | lifecycle/token tests | READY_FOR_REVIEW |
| Owner-asserted retention/erasure | 7.2 | four-disposition tests | READY_FOR_REVIEW |
| Closed provenance | 7.2 | receipt/rules mismatch tests | READY_FOR_REVIEW |
| Data-scope remains non-load-bearing | 6, 7.2 | exact evidence model/negative tests | READY_FOR_REVIEW |
| Strict ready/non-admission union | 7.2 | schema and contradictory-union tests | READY_FOR_REVIEW |
| Digest-owner absence/private-helper guard | 7.2, 7.3 | fail-closed and AST negative tests | READY_FOR_REVIEW |
| Cheap alternative/no runtime program | 6 | exact diff and forbidden-import audit | READY_FOR_REVIEW |
| Governance cost bounded | 3, 5, 11 | one BUILD, one review chain, exact 22 paths | READY_FOR_REVIEW |

## 9. Pre-BUILD gate

Before the first BUILD edit, the worker must record and verify:

1. clean `main`, `HEAD == origin/main == <executionBaseHead>`;
2. exact Work Order, SPEC and ADR SHA-256 values;
3. independent `WORK_ORDER_AUTHORIZATION_REVIEW_PASS`, findings/waivers NONE;
4. canonical state role `IMPLEMENTATION_WORKER` and phase `BUILD`;
5. paths 1-4 and 20-22 match the execution baseline; paths 5-19 are absent;
6. private helpers still resolve only at their source locations;
7. no retrieval-contract collision or unexpected untracked/staged file;
8. session, catalog, file-size, repository and workspace-doctor gates pass,
   allowing only the retained 24/1 legacy-catalog warning.

Failure stops before edit. The execution baseline is not guessed in this
candidate; authorization closure must record the exact pushed commit.

## 10. Required execution and verification order

The worker proceeds sequentially and stops on the first unresolved failure:

1. Capture pre-BUILD gate evidence.
2. Create package skeleton/models and run model/schema tests.
3. Implement canonical algorithms/constructor and run focused constructor and
   adversarial tests.
4. Add private-helper/forbidden-import guards and run their focused tests.
5. Apply additive P3-A enum/contract changes and rerun the complete retained
   P3-A focused suite.
6. Generate schema; independently compare fresh schema bytes.
7. Update registry/status and run catalog `--write` once.
8. Run all focused P3-C tests together.
9. Run the full non-live Python suite.
10. Run repository gates and exact changed-set/secret/residue audit.
11. Leave all 22 paths unstaged and return `COMPLETE_PENDING_REVIEW`.

Required commands include:

```powershell
python -m pytest tests/unit/test_p3c_retrieval_contract_models.py tests/unit/test_p3c_retrieval_contract_constructor.py tests/unit/test_p3c_retrieval_contract_adversarial.py tests/unit/test_p3c_retrieval_contract_digest_guards.py tests/contract/test_p3c_retrieval_contract_schema.py -q
python -m pytest tests/unit/test_refinery_models.py tests/unit/test_refinery_canonical.py tests/unit/test_refinery_pipeline.py tests/unit/test_refinery_adversarial.py tests/unit/test_refinery_contract.py -q
python scripts/generate_catalog.py --write
python scripts/generate_catalog.py --check
python -m pytest -q
python scripts/check_session_state.py
python scripts/check_file_size.py
python scripts/testing/validate_repository.py
git diff --check
git status --short --untracked-files=all
```

The worker must also parse all changed JSON/YAML, run a secret-pattern scan
without printing matched values, inspect AST imports/calls, audit exact 22-path
diff and run the workspace doctor. No live/provider command is authorized.

## 11. Worker autonomy and latency control

Inside the exact 22 paths, the worker must autonomously repair and rerun:

- source/test defects caused by its implementation;
- formatting, schema drift, catalog generation and file-size failures;
- deterministic golden mismatch caused by code that violates the SPEC;
- missing negative cases required by R23;
- unexpected cache/residue cleanup.

The worker must not ask the operator to choose routine fixes already determined
by the reviewed SPEC. It returns for amendment only when the smallest correct
repair needs an additional path, a changed requirement/claim/risk/external
effect, provider/secret access, destructive action or commit-owner change.

At repair round three without a new independent root cause, stop with
`REVIEW_COST_ESCALATION_REQUIRED`; do not recreate governance latency through
unbounded micro-amendments.

## 12. Evidence and worker return

The worker return must record:

- `executionBaseHead`, Work Order/SPEC/ADR hashes and Python/tool versions;
- exact changed-path classification and `git status --short --untracked-files=all`;
- every required command, exit result and exact test count;
- independent schema/digest/chunk/revalidation recomputation evidence;
- all R23 fixture groups and source-type matrix coverage;
- forbidden-import/private-helper AST evidence;
- provider/network/POST/secret-read counts, all zero;
- catalog/status claim boundary and file-size results;
- any failed intermediate result retained with its allowed-scope repair and
  final rerun, rather than hidden;
- `COMPLETE_PENDING_REVIEW`, never a closure or self-approval claim.

No worker commit, stage or push is permitted.

## 13. Independent BUILD review

The reviewer must independently verify the exact authority hashes, 22-path
diff, source topology, model/schema shapes, constructor precedence, every
negative branch, golden hashes, private-helper guards, full non-live suite,
catalog/status truth, zero-call accounting and no broadened claim.

The reviewer returns exactly one:

- `REVIEW_PASS`;
- `REVIEW_CHANGES_REQUIRED` with one consolidated finding set;
- `REVIEW_BLOCKED_SOURCE_OR_SCOPE`.

Same-scope repairs remain authorized inside the 22 paths. No waiver may convert
a source-integrity, disclosure, dependency, external-effect or union-invariant
failure into PASS.

## 14. Commit ownership and closure choreography

- Work Order authorization candidate/closure commits: `COMMIT_STEWARD`.
- Pre-BUILD role/baseline checkpoint: `SESSION_SYNC_STEWARD` plus
  `COMMIT_STEWARD`, continuity paths only.
- BUILD worker: `WORKER_MUST_NOT_COMMIT` and leaves exact 22 paths unstaged.
- BUILD commit: `COMMIT_STEWARD` only after independent `REVIEW_PASS`, exact
  reviewed 22 paths, clean residue audit and rerun gates.
- FREEZE/session/catalog closure: separate continuity commit after BUILD push.

Every commit is pushed to `origin main` before the next authority transfer.
No amend, squash, force-push or cross-tranche batching is permitted.

## 15. Stop conditions

Stop immediately on:

- missing/changed authorization, source baseline or lineage hash;
- missing/extra/renamed path or protected-path drift;
- a required digest owner that would need operations-domain/app changes;
- import/use/copy of private or application digest helpers;
- provider/network/POST/secret/config/database/filesystem/subprocess attempt;
- unsafe text/provenance disclosure, partial ready output or permissive default;
- ambiguous requirement requiring DESIGN/SPEC reinterpretation;
- failed gate that cannot be repaired inside the 22 paths;
- staged/committed worker changes, catalog drift, secret or generated residue;
- broadened tenant/data-scope/retrieval/RAG/runtime/production claim.

Return the exact blocker and smallest governed next move. Do not continue to a
later gate or consume external quota.

## 16. Acceptance and claim boundary

Acceptance requires every SPEC AC-01 through AC-12 to be independently mapped
to passing files/tests/evidence, exact 22-path compliance, zero external calls,
no unresolved finding and all repository gates passing.

The bounded BUILD may claim only a tested deterministic local P3-C contract,
typed fail-closed non-admission, advisory ready fixtures, reproducible contract
bytes and explicit no-owner behavior for canonical records. It may not claim a
runtime retrieval caller, durable index, vector search, provider behavior,
tenant isolation, placement/minimization enforcement, RAG, production readiness
or completed Phase 3.

## 17. Next governed move

Independent Work Order authorization review only. Return exactly one:

- `WORK_ORDER_AUTHORIZATION_REVIEW_PASS`;
- `WORK_ORDER_AUTHORIZATION_CHANGES_REQUIRED`;
- `WORK_ORDER_BLOCKED_SOURCE_OR_SCOPE`.

No BUILD, provider/network/POST call, staging by a worker, retrieval or later
roadmap lane is authorized by this candidate alone.
