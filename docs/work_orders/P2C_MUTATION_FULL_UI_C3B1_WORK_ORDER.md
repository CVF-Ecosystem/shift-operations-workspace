# Work Order — P2-C C3b1 Browser Read/Readiness Contract

- ID: `P2C-MUTATION-FULL-UI-C3B1-WO-001`
- Tranche: `P2C-MUTATION-FULL-UI-2026-07-31`
- Checkpoint: `C3b1`
- Risk: `R2`
- Reviewed implementation parent: `95b66b15c9e7208f078c750cfbb7c30f051867f4`
- Parent DESIGN: `docs/decisions/ADR_2026-07-31_P2C_MUTATION_FULL_UI.md`
- Parent SPEC: `docs/specs/P2C_MUTATION_FULL_UI_SPEC.md`
- Feasibility DESIGN addendum:
  `docs/decisions/ADR_2026-08-01_P2C_C3B_FEASIBILITY_ADDENDUM.md`
- Feasibility SPEC amendment:
  `docs/specs/P2C_MUTATION_FULL_UI_SPEC_AMENDMENT_7.md`
- Status: `APPROVED — BUILD ONLY AFTER PUSHED PRE-BUILD CHECKPOINT AND G6`

## 1. Authority, roles and checkpoint boundary

The operator delegated Work Order approval authority to Codex. Codex authors
this exact-path authorization; an independent `AUTHORIZATION_REVIEWER` MUST
compare it with current source, pushed C3a2, reviewed DESIGN/SPEC/addendum,
R11/R15-R17/R34-R37 and AC-11/AC-16..AC-18/AC-29..AC-34.

The later `IMPLEMENTATION_WORKER` may edit only the exact BUILD paths below
and MUST NOT stage, commit, push, self-review or FREEZE. No Claude CLI,
provider-control MCP or automated Claude call is authorized. Codex may become
`COMMIT_STEWARD` only after independent BUILD `REVIEW_PASS`.

C3b1 adds browser-required reads, approval-readiness and the non-React browser
transport contract. It does not add CustomerRequest version, mutation
preconditions, React controls or any C3c/C3d behavior. C3b2-C3d remain blocked.

## 2. Exact 34-path C3b1 BUILD ceiling

Every path below MUST change or be created. There is no wildcard, conditional
allowance, reserve, optional truth surface or self-review path.

### Backend and browser contract implementation — 13 paths

1. `packages/operations-ledger/src/operations_ledger/ledger.py`
2. `packages/operations-ledger/src/operations_ledger/_message_store.py`
3. `apps/workspace-api/src/workspace_api/infrastructure/repository.py`
4. `apps/workspace-api/src/workspace_api/infrastructure/_message_repository.py` — NEW
5. `apps/workspace-api/src/workspace_api/application/browser_reads.py` — NEW
6. `apps/workspace-api/src/workspace_api/application/approval_readiness.py` — NEW
7. `apps/workspace-api/src/workspace_api/application/approval_service.py`
8. `apps/workspace-api/src/workspace_api/api/approvals/router.py`
9. `apps/workspace-api/src/workspace_api/api/messages/router.py`
10. `apps/workspace-api/src/workspace_api/api/tasks/router.py`
11. `apps/workspace-api/src/workspace_api/api/customer_requests/router.py`
12. `apps/workspace-web/src/services/api.ts`
13. `apps/workspace-web/src/types/backendContracts.ts` — NEW

### Focused, parity, OpenAPI and transport proof — 15 paths

14. `tests/cvf/_c3b_read_fixtures.py` — NEW
15. `tests/cvf/test_c3b_read_routes.py` — NEW
16. `tests/cvf/test_c3b_approval_readiness.py` — NEW
17. `tests/cvf/test_c3b_read_limits.py` — NEW
18. `tests/integration/test_c3b_read_ledger_parity.py` — NEW
19. `tests/integration/test_c3b_read_postgres_live.py` — NEW
20. `tests/unit/test_c3b_read_openapi_contract.py` — NEW
21. `tests/unit/test_assignment_openapi_contract.py`
22. `tests/unit/test_p2b_openapi_contract.py`
23. `tests/unit/test_p2c_read_openapi_contract.py`
24. `tests/unit/test_shift_create_openapi_contract.py`
25. `tests/unit/test_message_openapi_contract.py`
26. `tests/unit/test_report_openapi_contract.py`
27. `apps/workspace-web/src/tests/api.test.ts`
28. `apps/workspace-web/src/tests/apiBackendContracts.test.ts` — NEW

### PostgreSQL orchestration, receipt and truth surfaces — 6 paths

29. `scripts/run_postgres_live_roundtrip.py`
30. `tests/integration/test_postgres_live_runner.py`
31. `docs/decisions/P2C_C3B1_BUILD_EVIDENCE_RECEIPT.md` — NEW
32. `docs/cvf/CVF_CONTROL_MAPPING.md`
33. `docs/catalog/MODULE_REGISTRY.json`
34. `docs/catalog/MODULE_CATALOG.md`

A required path outside this list is `BLOCKED_WORK_ORDER_CEILING`. Stop before
editing it. Resume requires reviewed DESIGN→SPEC→WORK_ORDER amendment and a
renewed exact approval. Synthetic edits to consume an authorized path are
forbidden; if a listed path proves unnecessary, stop for exact-set contraction.

## 3. Implementation contract

### 3.1 Read services and persistence parity

- `browser_reads.py` is the single application boundary for the three list
  reads; every call requires verified authentication then current ACTIVE
  assignment, with no invented read-action permission;
- Message storage gains deterministic `list_messages_for_shift`; the existing
  InMemory message methods move intact into the feature-owned repository mixin
  before the list method is added, keeping the 300-line facade compliant;
- Task and CustomerRequest reads reuse the established ledger methods used by
  Report snapshots; no second repository/query implementation is allowed;
- orders are exact R36 order; 0-500 matches return fully and 501+ is controlled
  422, never silent truncation or invented pagination;
- list responses include terminal Task/CustomerRequest history and only bound
  CustomerRequests for the requested shift.

### 3.2 Approval readiness

- readiness accepts only `OperationalEvent/event.confirm`, `Task/task.create`
  (whose record id is the stored TaskCreationIntent id),
  `Incident/incident.acknowledge` and `Report/report.approve`; it applies the requested
  action's coarse permission before target resolution, then derives the target
  binding from stored truth and checks ACTIVE assignment; caller-supplied
  version/risk/digest is forbidden;
- missing and inaccessible targets share the existing sanitized operational
  404 boundary; coarse permission denial remains 403 before assignment 404;
- current active-user authority is resolved per request; stored receipt role is
  never authority. Deterministic maximum bipartite matching retains seat order
  and multiplicity, and one distinct approver fills at most one seat;
- readiness is requester-independent and does not evaluate later confirmer/
  self-approval. Satisfied output contains matched seat names, not identities;
- `ready` means quorum readiness only and never authorizes or predicts lifecycle
  admission; every later mutation re-runs all server gates;
- an exact non-current Report returns sanitized 409 after permission and
  assignment; a current Report's stored binding is used regardless of lifecycle;
- response/OpenAPI excludes digest, receipt identifiers, approver identities,
  credentials and raw policy internals.

### 3.3 Browser transport contract

- `api.ts` supports typed method, JSON body, query and AbortSignal, preserving
  bearer auth and encoded query values;
- 401 clears the tab-scoped session; 403/404/409/422 map to controlled kinds;
  aborted requests remain cancelled; ambiguous transport failure becomes
  `outcome_unknown`; there is no automatic retry;
- no token, body, raw response, transport exception or URL credential is
  logged or surfaced;
- only feature-owned DTO and transport-test source is added. React components,
  feature folders, CSS, offline queue, package manifests, lockfiles and build
  configuration remain byte-identical.

### 3.4 Contract history and evidence

- the new OpenAPI delta test owns the C3b1 paths/schemas and strips exactly
  that delta back to the C3a1/C3a2 document; earlier historical delta tests
  import the central stripping helper instead of refreshing old hashes blindly;
- InMemory, SQLite and disposable PostgreSQL 16 prove ordering, 500/501
  behavior, terminal-history completeness, assignment refusal, readiness
  authority refresh and migration reapply with zero owned residue;
- C3b1 makes no new AI/agent-governance claim and performs no provider call;
  the receipt must state this nonclaim and must not reuse earlier live evidence
  as proof of the new read contract;
- AC-29 uses the exact recorded pre-BUILD parent in an isolated temporary
  worktree/tree and removes/prunes it without touching the candidate tree.

## 4. Protected boundary

Zero diff is mandatory for:

- migrations, domain models, table metadata, row mappers and CustomerRequest
  version/concurrency reserved for C3b2;
- every mutation service and mutation request schema;
- C3a assignment persistence/scope/staffing/bootstrap semantics;
- approval receipt creation/quorum rules, lifecycle/risk/evidence/freeze/Report
  semantics and provider configuration;
- all React component/feature/style files, offline queue, dependency manifests,
  lockfiles, CI and file-size debt registry;
- `.cvf/**`, roadmap, implementation status, continuity and prior receipts.

## 5. Pre-BUILD G6

From a separate clean pushed pre-BUILD continuity commit:

1. verify `HEAD == origin/main`, clean worktree and record exact parent;
2. rehydrate manifest/policy/memory/state/handoff/DESIGN/SPEC/amendment/WO;
3. verify C3a2 `95b66b1` and closure `61aeeb6` are ancestors;
4. verify core/manifest/origin pin and doctor `PASS WITH NOTE 24/1` only;
5. run full Python non-live plus frozen frontend baseline and record counts;
6. pass session/catalog/file-size/repository/JSON/diff gates;
7. verify Docker/PostgreSQL prerequisites without printing secrets and prove
   zero owned container/volume residue.

Any failure is `BLOCKED_G6`; no source edit or provider call.

## 6. Required order and evidence

1. message list parity and central bounded read service;
2. readiness stored-target/current-authority service;
3. route/OpenAPI contracts and assignment/refusal matrices;
4. browser request primitive/DTO/transport tests, with no React feature edit;
5. focused tests, full Python non-live, frozen pnpm install, typecheck and
   frontend tests/build;
6. disposable PostgreSQL 16 suite, migration reapply and exact cleanup;
7. AC-29 isolated exact-parent rehearsal and cleanup;
8. catalog generation, repository/doctor gates and truthful BUILD receipt.

Required minimum commands include:

```powershell
python -m pytest -q tests/cvf/test_c3b_read_routes.py tests/cvf/test_c3b_approval_readiness.py tests/cvf/test_c3b_read_limits.py tests/integration/test_c3b_read_ledger_parity.py tests/unit/test_c3b_read_openapi_contract.py
python -m pytest -q
pnpm --dir apps/workspace-web install --frozen-lockfile
pnpm --dir apps/workspace-web run typecheck
pnpm --dir apps/workspace-web test -- --run
pnpm --dir apps/workspace-web run build
python scripts/run_postgres_live_roundtrip.py --json
python scripts/generate_catalog.py --write
python scripts/check_session_state.py
python scripts/generate_catalog.py --check
python scripts/check_file_size.py
python scripts/testing/validate_repository.py
powershell -ExecutionPolicy Bypass -File scripts/initialize_cvf_clone.ps1
git diff --check
```

The worker return MUST report exact results, actual changed set, failures and
repairs, PostgreSQL/Docker cleanup, AC-29 parent/results/cleanup, zero staged
files and:

`READY_FOR_INDEPENDENT_P2C_C3B1_BUILD_REVIEW`

## 7. Stop conditions and ownership

STOP on unexpected parent/continuity drift; any outside or unnecessary ceiling
path; hard-limit overflow; assignment/enumeration bypass; readiness identity or
digest exposure; inconsistent cross-backend order/limit; OpenAPI/frontend
contract drift; automatic retry; raw transport/secret exposure; regression;
Docker residue; unavailable PostgreSQL proof; or pressure to combine C3b1 with
C3b2/C3c/C3d.

The worker MUST NOT stage, commit, push, self-review or FREEZE. Codex performs
independent BUILD review and becomes `COMMIT_STEWARD` only after `REVIEW_PASS`.

## 8. Claim boundary

C3b1 may prove only authenticated, assignment-scoped, deterministic/bounded
browser-required Message/Task/CustomerRequest reads; sanitized current-binding
approval-readiness; and a non-React browser transport/DTO contract on the
proven backends. It does not prove mutation concurrency, CustomerRequest
versioning, UI controls, tenant/provider data scope, token revocation,
production PostgreSQL, P2-C/P2-D or Phase-2 completion.
