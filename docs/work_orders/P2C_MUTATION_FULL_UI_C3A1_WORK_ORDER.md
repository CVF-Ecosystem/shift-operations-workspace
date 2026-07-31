# Work Order — P2-C C3a1 Assignment Foundation

- ID: `P2C-MUTATION-FULL-UI-C3A1-WO-001`
- Tranche: `P2C-MUTATION-FULL-UI-2026-07-31`
- Checkpoint: `C3a1`
- Risk: `R2`
- Parent DESIGN: `docs/decisions/ADR_2026-07-31_P2C_MUTATION_FULL_UI.md`
- Parent SPEC: `docs/specs/P2C_MUTATION_FULL_UI_SPEC.md`
- Fan-out amendment:
  `docs/decisions/ADR_2026-07-31_P2C_C3A_FANOUT_ADDENDUM.md`
- SPEC amendment: `docs/specs/P2C_MUTATION_FULL_UI_SPEC_AMENDMENT_1.md`
- Status: `APPROVED — BUILD ONLY AFTER PUSHED PRE-BUILD CHECKPOINT AND G6`

## 1. Authority, roles and checkpoint boundary

The operator delegated Work Order approval authority to Codex. Codex is the
`WORK_ORDER_AUTHOR` and `AUTHORIZATION_REVIEWER`; it is not the implementation
worker. The external `IMPLEMENTATION_WORKER` receives the prompt manually
from the operator. No Claude CLI, provider-control MCP, or automated
cross-agent call is authorized.

The worker may edit only the exact C3a1 paths below and must not stage, commit,
push, self-review or FREEZE. Codex independently reviews and later acts as
`COMMIT_STEWARD` only after `REVIEW_PASS`.

C3a1 implements assignment persistence, staffing, session/capability reads
and atomic new-shift bootstrap. It does **not** enforce assignments across
existing operational routes and cannot claim R6/R7 or C3a completion. C3a2,
C3b, C3c and C3d remain unauthorized.

## 2. Exact 48-path C3a1 BUILD ceiling

Every path below is expected to change or be created. There is no wildcard,
conditional allowance or reserve path.

### Domain, permission, persistence and API

1. `database/migrations/008_shift_assignments.sql` — NEW
2. `packages/operations-domain/src/operations_domain/assignment_models.py` — NEW
3. `apps/workspace-api/src/workspace_api/domain/models.py`
4. `packages/cvf-runtime/src/cvf_runtime/permission.py`
5. `packages/operations-ledger/src/operations_ledger/ledger.py`
6. `packages/operations-ledger/src/operations_ledger/_assignment_tables.py` — NEW
7. `packages/operations-ledger/src/operations_ledger/tables.py`
8. `packages/operations-ledger/src/operations_ledger/_assignment_store.py` — NEW
9. `packages/operations-ledger/src/operations_ledger/sql_ledger.py`
10. `apps/workspace-api/src/workspace_api/infrastructure/_assignment_repository.py` — NEW
11. `apps/workspace-api/src/workspace_api/infrastructure/repository.py`
12. `apps/workspace-api/src/workspace_api/application/assignment_service.py` — NEW
13. `apps/workspace-api/src/workspace_api/application/shift_service.py`
14. `apps/workspace-api/src/workspace_api/auth/tokens.py`
15. `apps/workspace-api/src/workspace_api/dependencies.py`
16. `apps/workspace-api/src/workspace_api/auth/router.py`
17. `apps/workspace-api/src/workspace_api/api/staffing/__init__.py` — NEW
18. `apps/workspace-api/src/workspace_api/api/staffing/router.py` — NEW
19. `apps/workspace-api/src/workspace_api/main.py`

### Unit, CVF and integration tests

20. `tests/unit/test_assignment_model.py` — NEW
21. `tests/unit/test_assignment_openapi_contract.py` — NEW
22. `tests/unit/test_p2b_openapi_contract.py`
23. `tests/unit/test_p2c_read_openapi_contract.py`
24. `tests/unit/test_shift_create_openapi_contract.py`
25. `tests/unit/test_message_openapi_contract.py`
26. `tests/unit/test_report_openapi_contract.py`
27. `tests/cvf/test_auth_tokens.py`
28. `tests/cvf/test_gates_unit.py`
29. `tests/cvf/test_ledger_protocol.py`
30. `tests/cvf/test_assignment_foundation.py` — NEW
31. `tests/cvf/test_shift_create_admission.py`
32. `tests/cvf/test_message_admission.py`
33. `tests/integration/test_assignment_ledger_parity.py` — NEW
34. `tests/integration/test_schema_parity_assignments.py` — NEW
35. `tests/integration/test_assignment_postgres_live.py` — NEW
36. `tests/integration/test_shift_create_sqlite.py`
37. `tests/integration/test_shift_create_postgres_live.py`
38. `tests/integration/test_shift_create_live_evidence_runner.py`
39. `tests/integration/test_message_postgres_live.py`
40. `tests/integration/test_assignment_live_evidence_runner.py` — NEW
41. `tests/integration/test_postgres_live_runner.py`

### Live runners, receipts and truth surfaces

42. `scripts/run_postgres_live_roundtrip.py`
43. `scripts/run_assignment_live_governance_evidence.py` — NEW
44. `docs/decisions/P2C_C3A1_ASSIGNMENT_BUILD_EVIDENCE_RECEIPT.md` — NEW
45. `docs/decisions/P2C_C3A1_ASSIGNMENT_LIVE_EVIDENCE_RECEIPT.md` — NEW
46. `docs/cvf/CVF_CONTROL_MAPPING.md`
47. `docs/catalog/MODULE_REGISTRY.json`
48. `docs/catalog/MODULE_CATALOG.md`
A required path outside this list is `BLOCKED_WORK_ORDER_CEILING`. Stop before
editing it. Resume requires reviewed DESIGN→SPEC→WORK_ORDER amendment and
renewed approval.

## 3. Implementation contract

### 3.1 Canonical assignment and migration

- `assignment_models.py` owns `ShiftAssignment` and `AssignmentStatus` only;
- fields and validation match SPEC R1 exactly; no tenant or provider
  `data_scope` field;
- migration 008 creates foreign keys to shifts/users, status/version checks,
  retained revoked history and a PostgreSQL/SQLite-compatible unique-active
  rule represented equivalently in SQLAlchemy metadata;
- existing shifts receive no inferred/backfilled assignment;
- migration reapply is safe and migrations 001-007 have zero-byte diff.

### 3.2 Ledger parity and hard-limit seams

- Ledger exposes add/get/list/current-membership/revoke plus active-user list;
- `_assignment_tables.py`, `_assignment_store.py` and
  `_assignment_repository.py` contain the new feature-owned implementation;
- InMemory returns deep copies and includes assignment state in transaction
  rollback snapshots;
- add/revoke and audit share one transaction; duplicate-active, missing
  identity, stale version and lifecycle errors are controlled and equivalent;
- the 300-line `tables.py`, `sql_ledger.py` and `repository.py` hosts change
  line-neutrally by split-module wiring; no debt/exemption or extra split path.

### 3.3 Staffing and session contracts

- permission map adds exactly `shift.assignment.manage` at
  `shift_supervisor` minimum;
- staffing router implements exactly the five R5 routes and minimum response
  fields, with no operational events/work/messages/Reports;
- add target must be persisted and active; actor/status/timestamps are
  server-derived;
- revoke semantics are exact: success increments once; current revoked
  version is idempotent/no second audit; pre-revoke version is stale 409;
- `/auth/me` returns verified token user id, role and the actual verified JWT
  expiry, not a freshly calculated approximation; existing principal
  dependency behavior remains compatible;
- `/shifts/{shift_id}/capabilities` requires ACTIVE assignment and returns
  advisory action names plus bounded reasons only; it never authorizes and
  exposes no credential/digest/policy internals.

### 3.4 Atomic shift bootstrap

- `ShiftService.create` first verifies `shift.create`, then requires the
  authenticated creator to be a persisted active user;
- Shift, creator ACTIVE assignment and actor-bound shift-create audit are one
  transaction; any failure rolls back all three;
- existing shift-create/message tests using the governed service/route seed
  the exact persisted user rather than weakening the invariant;
- direct `ledger.create_shift` setup remains available for legacy-data and
  migration tests and creates no inferred assignment.

### 3.5 OpenAPI history and evidence

- new OpenAPI tests prove the exact five staffing operations, `/auth/me`,
  capabilities, security and schemas;
- all five historical OpenAPI delta files strip exactly the later assignment
  delta before checking their immutable earlier hashes; digest refresh alone
  is forbidden;
- PostgreSQL runner adds the assignment module to its explicit target tuple;
- C3a1 live proof runs refusals at zero provider calls, verifies one genuine
  durable staffing/bootstrap assignment plus exact audit facts, then performs
  exactly one sanitized real-provider call;
- receipts state counts, failures/repairs, changed set, Docker cleanup and
  excluded claims truthfully; no raw secret/DSN/provider body.

## 4. Protected boundary

Zero diff is mandatory for:

- migrations 001-007 and unrelated domain/lifecycle semantics;
- every existing operational router/service except ShiftService.create;
- route-wide assignment enforcement, enumeration changes and legacy fixture
  migration reserved for C3a2;
- approval/risk/evidence/freeze/report behavior;
- frontend, P2-D offline/realtime and full-shift exit surfaces;
- provider adapters/configuration, external channels and production data;
- `.cvf/**`, dependency manifests/lockfiles, CI, file-size guard/debt list;
- roadmap, implementation status, continuity and prior receipts.

## 5. Pre-BUILD G6

From the clean pushed pre-BUILD continuity commit, before any C3a1 edit:

1. verify `HEAD == origin/main`, clean worktree and exact recorded parent;
2. rehydrate manifest/policy/memory/state/handoff/ADR/SPEC/amendments/WO;
3. verify core/manifest/origin pin and doctor `PASS WITH NOTE 24/1` only;
4. run the full non-live baseline and record exact pass/skip/warning counts;
5. pass session, catalog, file-size, repository, JSON and diff gates;
6. verify Docker/PostgreSQL/provider prerequisites without printing secrets;
7. verify no owned container/volume residue.

Any failure is `BLOCKED_G6`; no source edit or provider call.

## 6. Required implementation and verification order

1. model/migration/table mapping and static parity;
2. Ledger/InMemory/SQLite assignment parity and rollback;
3. permission, staffing service/API and `/auth/me`/capabilities;
4. atomic ShiftService.create and exact legacy test repairs;
5. OpenAPI exact-delta chain;
6. focused tests, then full non-live regression;
7. disposable PostgreSQL 16 migration/reapply/live suite with exact cleanup;
8. fresh live-governance evidence in refusal→durable proof→one-call order;
9. canonical catalog generation, all repository gates and receipt completion.

Required minimum commands include:

```powershell
python -m pytest -q tests/unit/test_assignment_model.py tests/unit/test_assignment_openapi_contract.py tests/cvf/test_assignment_foundation.py tests/integration/test_assignment_ledger_parity.py tests/integration/test_schema_parity_assignments.py
python -m pytest -q
python scripts/run_postgres_live_roundtrip.py --json
python scripts/run_assignment_live_governance_evidence.py
python scripts/generate_catalog.py --write
python scripts/check_session_state.py
python scripts/generate_catalog.py --check
python scripts/check_file_size.py
python scripts/testing/validate_repository.py
powershell -ExecutionPolicy Bypass -File scripts/initialize_cvf_clone.ps1
git diff --check
```

The worker return must give exact command results, the actual changed subset
of the 48-path ceiling, failures and repairs, Docker cleanup, sanitized live
receipt result and token:

`READY_FOR_INDEPENDENT_P2C_C3A1_BUILD_REVIEW`

## 7. Stop conditions and ownership

STOP on dirty/unexpected parent, continuity drift, required out-of-ceiling
path, hard-limit overflow, migration/schema/OpenAPI mismatch, partial rollback,
uncontrolled exception, full-suite regression, Docker residue, unavailable
mandatory PostgreSQL/provider proof, secret exposure, nonzero provider call on
refusal, or pressure to combine checkpoints.

The worker must not stage/commit/push/review/FREEZE. After the return, Codex
independently inspects source/diff/tests/evidence. Only `REVIEW_PASS` permits
Codex to commit and push C3a1. C3a2 still requires a new exact-path Work Order.

## 8. Claim boundary

C3a1 may prove only a single-workspace assignment persistence/staffing
foundation, advisory session/capability reads and atomic creator assignment
for newly created shifts on the proven backends. It does not prove existing
operational routes are assignment-scoped, tenant isolation, provider
`data_scope`, fixed-token early revocation, production PostgreSQL, frontend
mutation, P2-C completion, P2-D or Phase-2 completion.
