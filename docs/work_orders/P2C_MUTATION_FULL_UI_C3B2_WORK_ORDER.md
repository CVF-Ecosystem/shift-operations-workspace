# Work Order — P2-C C3b2 Mutation Preconditions and CustomerRequest Version

- ID: `P2C-MUTATION-FULL-UI-C3B2-WO-001`
- Tranche: `P2C-MUTATION-FULL-UI-2026-07-31`
- Checkpoint: `C3b2`
- Risk: `R2`
- Reviewed implementation parent: `e3817b24e3150a730dd26ab2c1a4a2b550755b06`
- Parent DESIGN: `docs/decisions/ADR_2026-07-31_P2C_MUTATION_FULL_UI.md`
- Parent SPEC: `docs/specs/P2C_MUTATION_FULL_UI_SPEC.md`
- Concurrency DESIGN addendum:
  `docs/decisions/ADR_2026-07-31_P2C_CUSTOMER_REQUEST_CONCURRENCY_ADDENDUM.md`
- Feasibility DESIGN addendum:
  `docs/decisions/ADR_2026-08-01_P2C_C3B_FEASIBILITY_ADDENDUM.md`
- Feasibility SPEC amendment:
  `docs/specs/P2C_MUTATION_FULL_UI_SPEC_AMENDMENT_7.md`
- Status: `APPROVED — BUILD ONLY AFTER PUSHED PRE-BUILD CHECKPOINT AND G6`

## 1. Authority and boundary

The operator delegated Work Order approval authority to Codex. An independent
`AUTHORIZATION_REVIEWER` MUST compare this exact-path order with current source,
the pushed C3b1 closure, reviewed DESIGN/SPEC/addenda, R12-R17 and AC-12..AC-18.

The later `IMPLEMENTATION_WORKER` may edit only the exact BUILD paths below and
MUST NOT stage, commit, push, self-review or FREEZE. No Claude CLI, provider MCP
or automated Claude call is authorized. C3b2 adds CustomerRequest versioning
and server mutation preconditions only. It adds no React mutation control,
offline/realtime behavior, C3c or C3d claim.

## 2. Exact 82-path BUILD ceiling

Every path below MUST change or be created. There is no wildcard, reserve,
optional path or self-review path.

### Persistence, services and route contracts — 28 paths

1. `database/migrations/009_customer_request_version.sql` — NEW
2. `packages/operations-domain/src/operations_domain/models.py`
3. `packages/operations-ledger/src/operations_ledger/tables.py`
4. `packages/operations-ledger/src/operations_ledger/_rows.py`
5. `packages/operations-ledger/src/operations_ledger/ledger.py`
6. `packages/operations-ledger/src/operations_ledger/sql_ledger.py`
7. `packages/operations-ledger/src/operations_ledger/_customer_request_store.py` — NEW
8. `apps/workspace-api/src/workspace_api/infrastructure/repository.py`
9. `apps/workspace-api/src/workspace_api/infrastructure/_customer_request_repository.py` — NEW
10. `apps/workspace-api/src/workspace_api/application/mutation_preconditions.py` — NEW
11. `apps/workspace-api/src/workspace_api/application/shift_service.py`
12. `apps/workspace-api/src/workspace_api/application/services.py`
13. `apps/workspace-api/src/workspace_api/application/correction_service.py`
14. `apps/workspace-api/src/workspace_api/application/task_service.py`
15. `apps/workspace-api/src/workspace_api/application/customer_request_service.py`
16. `apps/workspace-api/src/workspace_api/application/incident_service.py`
17. `apps/workspace-api/src/workspace_api/application/handover_service.py`
18. `apps/workspace-api/src/workspace_api/application/report_service.py`
19. `apps/workspace-api/src/workspace_api/api/shifts/router.py`
20. `apps/workspace-api/src/workspace_api/api/events/router.py`
21. `apps/workspace-api/src/workspace_api/api/corrections/router.py`
22. `apps/workspace-api/src/workspace_api/api/tasks/router.py`
23. `apps/workspace-api/src/workspace_api/api/customer_requests/router.py`
24. `apps/workspace-api/src/workspace_api/api/incidents/router.py`
25. `apps/workspace-api/src/workspace_api/api/handovers/router.py`
26. `apps/workspace-api/src/workspace_api/api/reports/router.py`
27. `apps/workspace-web/src/types/operations.ts`
28. `apps/workspace-web/src/tests/apiBackendContracts.test.ts`

### Focused, schema and OpenAPI proof — 15 paths

29. `tests/cvf/test_c3b2_mutation_preconditions.py` — NEW
30. `tests/integration/test_customer_request_version_parity.py` — NEW
31. `tests/integration/test_c3b2_postgres_live.py` — NEW
32. `tests/unit/test_c3b2_mutation_openapi_contract.py` — NEW
33. `tests/integration/test_schema_parity.py`
34. `tests/integration/test_schema_parity_types_and_checks.py`
35. `tests/unit/test_operations_domain_serialization.py`
36. `tests/unit/test_c3b_read_openapi_contract.py`
37. `tests/unit/test_incident_openapi_contract.py`
38. `tests/unit/test_report_openapi_contract.py`
39. `tests/unit/test_message_openapi_contract.py`
40. `tests/unit/test_p2b_openapi_contract.py`
41. `tests/unit/test_p2c_read_openapi_contract.py`
42. `tests/unit/test_shift_create_openapi_contract.py`
43. `tests/unit/test_assignment_openapi_contract.py`

### Existing governed-chain regression call sites — 22 paths

44. `tests/cvf/_customer_request_fixtures.py`
45. `tests/cvf/_shift_close_fixtures.py`
46. `tests/cvf/test_approver_identity_receipts.py`
47. `tests/cvf/test_approver_identity_reconciliation.py`
48. `tests/cvf/test_assignment_scope_cross_shift.py`
49. `tests/cvf/test_assignment_scope_enumeration.py`
50. `tests/cvf/test_assignment_scope_routes.py`
51. `tests/cvf/test_atomic_mutation_audit.py`
52. `tests/cvf/test_correction_vertical.py`
53. `tests/cvf/test_customer_request_repair.py`
54. `tests/cvf/test_customer_request_transitions.py`
55. `tests/cvf/test_customer_request_vertical.py`
56. `tests/cvf/test_freeze_invariant.py`
57. `tests/cvf/test_handover_vertical.py`
58. `tests/cvf/test_incident_vertical.py`
59. `tests/cvf/test_report_approval.py`
60. `tests/cvf/test_report_freeze.py`
61. `tests/cvf/test_report_vertical.py`
62. `tests/cvf/test_shift_close_freeze_interaction.py`
63. `tests/cvf/test_shift_close_governance.py`
64. `tests/cvf/test_task_vertical.py`
65. `tests/cvf/test_vertical_end_to_end.py`

### Integration/live-runner call sites — 12 paths

66. `tests/integration/test_evidence_persistence.py`
67. `tests/integration/test_assignment_scope_postgres_live.py`
68. `tests/integration/test_handover_postgres_live.py`
69. `tests/integration/test_incident_postgres_live.py`
70. `tests/integration/test_report_postgres_live.py`
71. `tests/integration/test_sql_ledger_handovers.py`
72. `scripts/_approval_governance_evidence_support.py`
73. `scripts/run_assignment_scope_live_governance_evidence.py`
74. `scripts/run_handover_live_governance_evidence.py`
75. `scripts/run_incident_live_governance_evidence.py`
76. `scripts/run_report_live_governance_evidence.py`
77. `scripts/run_postgres_live_roundtrip.py`

### Orchestration and truth surfaces — 5 paths

78. `tests/integration/test_postgres_live_runner.py`
79. `docs/decisions/P2C_C3B2_BUILD_EVIDENCE_RECEIPT.md` — NEW
80. `docs/cvf/CVF_CONTROL_MAPPING.md`
81. `docs/catalog/MODULE_REGISTRY.json`
82. `docs/catalog/MODULE_CATALOG.md`

A required path outside this list is `BLOCKED_WORK_ORDER_CEILING`. Stop before
editing it. Resume requires reviewed DESIGN→SPEC→WORK_ORDER amendment and a
renewed exact approval. If a listed path proves unnecessary, stop for exact-set
contraction; synthetic edits are forbidden.

## 3. Implementation contract

### 3.1 CustomerRequest version and compare-and-swap

- Add non-null integer `CustomerRequest.version`, default/backfill `1`, with a
  database check `version >= 1`; model, metadata, row mapping, protocol and both
  ledgers MUST agree. Create persists and returns exactly `1`.
- The migration is forward-only, deterministic and idempotent under the
  repository migration runner; it must not rewrite unrelated schema.
- CustomerRequest transition requires `expected_version`, compares the stored
  value inside the same transaction, increments exactly once on success and
  persists via compare-and-swap. A missing precondition is controlled 422; a
  stale value is controlled 409 with zero request-row or audit change.
- InMemory, SQLite and PostgreSQL prove duplicate/stale/no-partial-write parity.
  Existing CustomerRequest methods move intact into the two feature-owned
  mixins before version/CAS is added, preserving facade size compliance.

### 3.2 Exact mutation-precondition matrix

The following routes and service entry points require integer
`expected_version >= 1`:

- shift close and freeze;
- event confirm and correction;
- task transition;
- CustomerRequest transition;
- incident acknowledge and transition;
- handover review and acknowledge;
- Report submit-review, approve and version-successor.

Report submit-review, approve and version-successor additionally require
`expected_status`. Report version-successor retains `reason`; shift freeze
retains only its already-deprecated override fields with their existing
defaults. Task/CustomerRequest/incident transitions retain `target_status`.
Create, append, task-intent and approval-receipt routes remain unchanged and
must reject any invented precondition field under their existing exact-body
rules.

Missing request fields fail at the HTTP boundary with 422 and no service call.
At direct service boundaries, an omitted/invalid precondition must also fail
controlled 422; no permissive default or caller-derived current value is
allowed. A supplied stale version or status fails controlled 409.

### 3.3 Transaction and admission order

- Permission remains before target disclosure. Stored target load, assignment
  admission, version/status comparison, lifecycle/quorum checks, mutation and
  audit all use one mutation transaction and one consistent stored truth.
- For previously non-atomic Task, CustomerRequest and Incident transition and
  shift close flows, move the read/assignment/decision into the transaction;
  do not merely re-read after mutating an object outside it.
- Compare after established permission and assignment admission, but before
  lifecycle, quorum, snapshot recalculation or any mutation. Sanitized
  assignment/missing-resource behavior remains unchanged.
- A failed precondition changes no domain row, audit, approval receipt,
  provider state or in-memory object visible after rollback.
- Successful versioned domain mutations increment exactly once. Report
  submit/approve are status-only and compare but do not increment Report
  content version. Report successor compares the predecessor then creates the
  next content version exactly as before.
- Freeze idempotency is admitted only when the supplied preconditions match the
  current frozen Shift and paired current Report integrity; stale retries are
  409, never silently successful.

### 3.4 OpenAPI, compatibility and evidence

- Exact request schemas are `extra=forbid`; OpenAPI makes required fields
  mechanically visible on all affected operations and shows no delta on the
  protected create/append/task-intent/approval-receipt operations.
- The new C3b2 OpenAPI link owns and strips exactly this mutation-schema delta
  back to the C3b1 golden. Historical files import that central strip helper;
  historical hashes are not blindly refreshed.
- Existing direct service, HTTP and live-evidence call sites pass explicit
  values read from the durable record they are exercising. Tests must not add
  a production bypass or helper that auto-fetches a current value for clients.
- The frontend domain type gains CustomerRequest `version`; no API mutation
  method, React component, feature state or offline queue is added in C3b2.
- Disposable PostgreSQL 16 applies all migrations twice, runs the new C3b2
  live module in the pinned target set and proves exact owned cleanup.
- C3b2 makes no new AI/agent-governance claim. No provider call or provider
  receipt is required or authorized.

## 4. Protected boundary

Zero diff is mandatory for C3b1 read/readiness/transport behavior; assignment,
staffing and scope semantics; approval receipt creation/quorum policy; Report
snapshot content; provider configuration; all React/feature/style files;
offline/realtime code; dependency manifests and lockfiles; CI; `.cvf/**`;
roadmap, continuity and prior receipts. No tenant/data-scope or production
PostgreSQL claim is authorized.

## 5. Pre-BUILD G6

From a separate clean pushed pre-BUILD continuity commit:

1. verify `HEAD == origin/main`, clean worktree and record the exact parent;
2. rehydrate manifest/policy/memory/state/handoff/DESIGN/SPEC/addenda/WO;
3. verify C3b1 BUILD `03e57f9` and closure `e3817b2` are ancestors;
4. verify core/manifest/origin pin and doctor `PASS WITH NOTE 24/1` only;
5. run full Python non-live and frozen frontend baseline, recording counts;
6. pass session/catalog/file-size/repository/JSON/diff gates;
7. verify Docker/PostgreSQL prerequisites and zero owned residue without
   printing secrets.

Any failure is `BLOCKED_G6`; no source edit or provider call.

## 6. Required order and evidence

1. migration/model/table/row/protocol parity and CustomerRequest store split;
2. shared precondition comparator and atomic service changes;
3. exact route schemas and protected-operation negative proof;
4. focused matrix, rollback, parity and OpenAPI tests;
5. update only genuine existing call sites with explicit preconditions;
6. full Python and frozen frontend gates;
7. disposable PostgreSQL 16, migration reapply and exact cleanup;
8. AC-29 isolated exact-parent rehearsal, catalog and repository gates;
9. truthful BUILD receipt with exact changed set and all repairs.

Minimum commands include:

```powershell
python -m pytest -q tests/cvf/test_c3b2_mutation_preconditions.py tests/integration/test_customer_request_version_parity.py tests/unit/test_c3b2_mutation_openapi_contract.py
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
repairs, migration first/reapply counts, PostgreSQL/Docker cleanup, AC-29
parent/results/cleanup, zero staged files and:

`READY_FOR_INDEPENDENT_P2C_C3B2_BUILD_REVIEW`

## 7. Stop conditions and claim boundary

STOP on parent/continuity drift; an outside or unnecessary ceiling path; any
hard-limit overflow; permissive or auto-filled preconditions; compare outside
the mutation transaction; partial write/audit; cross-backend divergence;
OpenAPI drift; regression; unavailable PostgreSQL proof; Docker residue; or
pressure to combine C3b2 with C3c/C3d.

The worker MUST NOT stage, commit, push, self-review or FREEZE. Codex becomes
`COMMIT_STEWARD` only after independent BUILD `REVIEW_PASS`.

C3b2 may prove only CustomerRequest version parity and explicit atomic mutation
preconditions on the enumerated backend routes/backends. It does not prove
browser mutation controls, offline/realtime behavior, tenant/provider scope,
production PostgreSQL, C3c/C3d, P2-C or Phase-2 completion.
