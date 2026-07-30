# Work Order — P2-R Operational Report and Freeze Prerequisite

- ID: `P2R-OPERATIONAL-REPORT-FREEZE-PREREQUISITE-WO-001`
- Tranche: `P2R-OPERATIONAL-REPORT-FREEZE-PREREQUISITE-2026-07-30`
- Risk: `R2`
- Intake:
  `docs/decisions/INTAKE_2026-07-30_P2R_OPERATIONAL_REPORT_FREEZE_PREREQUISITE.md`
- Design:
  `docs/decisions/ADR_2026-07-30_P2R_OPERATIONAL_REPORT_FREEZE_PREREQUISITE.md`
- Specification:
  `docs/specs/P2R_OPERATIONAL_REPORT_FREEZE_PREREQUISITE_SPEC.md`
- SPEC review:
  `docs/decisions/P2R_OPERATIONAL_REPORT_FREEZE_PREREQUISITE_SPEC_REVIEW.md`
- Status: `REVIEW_PASS — R2 HUMAN APPROVAL REQUIRED; BUILD PROHIBITED`

## 1. Roles and gates

- Current roles: `ORCHESTRATOR`, `WORK_ORDER_AUTHOR`.
- Future `IMPLEMENTATION_WORKER`/`REPAIR_WORKER`: unassigned.
- Post-BUILD `REVIEWER`: independent from the implementation worker.
- `COMMIT_STEWARD` and `SESSION_SYNC_STEWARD`: assigned only after review.

No implementation may begin until:

1. this Work Order has authorization `REVIEW_PASS`;
2. the operator supplies explicit R2 human approval;
3. the authorization checkpoint is committed and pushed;
4. a separate pre-BUILD continuity checkpoint records worker/reviewer
   assignment and acknowledgment;
5. G6 passes from that clean pushed checkpoint.

No provider-specific role or CLI control mechanism is assumed. The worker
receives this provider-neutral repository contract through an operator-owned
handoff.

## 2. Exact C3 BUILD changed set

Exactly these 59 paths are authorized. Every listed path is expected to
change or be created in C3; there is no wildcard, conditional allowance or
unnamed reserve.

### Domain, persistence, application and contract

1. `database/migrations/007_report_history_constraints.sql` — NEW
2. `packages/operations-domain/src/operations_domain/report_models.py` — NEW
3. `packages/operations-domain/src/operations_domain/models.py`
4. `packages/operations-domain/src/operations_domain/lifecycle.py`
5. `apps/workspace-api/src/workspace_api/domain/models.py`
6. `apps/workspace-api/src/workspace_api/domain/lifecycle.py`
7. `packages/cvf-runtime/src/cvf_runtime/permission.py`
8. `packages/operations-ledger/src/operations_ledger/ledger.py`
9. `packages/operations-ledger/src/operations_ledger/_report_tables.py` — NEW
10. `packages/operations-ledger/src/operations_ledger/tables.py`
11. `packages/operations-ledger/src/operations_ledger/_report_store.py` — NEW
12. `packages/operations-ledger/src/operations_ledger/sql_ledger.py`
13. `apps/workspace-api/src/workspace_api/infrastructure/_report_repository.py`
    — NEW
14. `apps/workspace-api/src/workspace_api/infrastructure/repository.py`
15. `apps/workspace-api/src/workspace_api/application/report_snapshot.py` — NEW
16. `apps/workspace-api/src/workspace_api/application/report_service.py` — NEW
17. `apps/workspace-api/src/workspace_api/application/report_freeze.py` — NEW
18. `apps/workspace-api/src/workspace_api/application/shift_service.py`
19. `apps/workspace-api/src/workspace_api/application/approval_receipts.py`
20. `apps/workspace-api/src/workspace_api/api/reports/router.py` — NEW
21. `apps/workspace-api/src/workspace_api/api/shifts/router.py`
22. `apps/workspace-api/src/workspace_api/main.py`
23. `packages/workspace-contracts/reports/shift-report.schema.json`
24. `docs/domain/REPORT_MODEL.md`
25. `docs/workflows/END_SHIFT_REPORT.md`

### Unit, CVF and integration tests

26. `tests/unit/test_report_snapshot.py` — NEW
27. `tests/unit/test_report_openapi_contract.py` — NEW
28. `tests/unit/test_operations_domain_shim_identity.py`
29. `tests/unit/test_operations_domain_serialization.py`
30. `tests/unit/test_p2b_openapi_contract.py`
31. `tests/unit/test_p2c_read_openapi_contract.py`
32. `tests/unit/test_shift_create_openapi_contract.py`
33. `tests/unit/test_message_openapi_contract.py`
34. `tests/cvf/test_report_vertical.py` — NEW
35. `tests/cvf/test_report_approval.py` — NEW
36. `tests/cvf/test_report_freeze.py` — NEW
37. `tests/cvf/test_ledger_protocol.py`
38. `tests/cvf/test_freeze_invariant.py`
39. `tests/cvf/test_atomic_mutation_audit.py`
40. `tests/cvf/test_customer_request_vertical.py`
41. `tests/cvf/test_shift_close_freeze_interaction.py`
42. `tests/integration/test_report_ledger_parity.py` — NEW
43. `tests/integration/test_schema_parity_reports.py` — NEW
44. `tests/integration/test_schema_parity.py`
45. `tests/integration/_schema_parity_parsing.py`
46. `tests/integration/test_report_postgres_live.py` — NEW
47. `tests/integration/test_handover_postgres_live.py`
48. `tests/integration/test_postgres_live_runner.py`
49. `tests/integration/test_report_live_evidence_runner.py` — NEW
50. `tests/integration/test_handover_live_evidence_runner.py`

### Live runners

51. `scripts/run_postgres_live_roundtrip.py`
52. `scripts/run_report_live_governance_evidence.py` — NEW
53. `scripts/_report_live_evidence_support.py` — NEW
54. `scripts/run_handover_live_governance_evidence.py`

### Receipts and implementation-truth surfaces

55. `docs/decisions/P2R_OPERATIONAL_REPORT_FREEZE_BUILD_EVIDENCE_RECEIPT.md`
    — NEW
56. `docs/decisions/P2R_OPERATIONAL_REPORT_FREEZE_LIVE_EVIDENCE_RECEIPT.md`
    — NEW, generated and sanitized
57. `docs/cvf/CVF_CONTROL_MAPPING.md`
58. `docs/catalog/MODULE_REGISTRY.json`
59. `docs/catalog/MODULE_CATALOG.md`

A required path outside this list is
`BLOCKED_WORK_ORDER_CEILING`. Stop without editing that path. A committed
DESIGN→SPEC→WORK_ORDER amendment and renewed R2 approval are required before
implementation may resume.

## 3. Exact implementation boundaries

### 3.1 Domain and lifecycle

- `report_models.py` owns only SPEC R1-R4 Report types and validators;
- `operations_domain.models` imports/re-exports the same objects on one
  compact line so the currently 293-line host remains at or below 300;
- canonical and compatibility lifecycle modules add only the R10 forward
  Report graph/identity re-export;
- no existing enum, model or lifecycle edge changes.

### 3.2 Migration and table mapping

- migration 007 implements only SPEC R23 and is safe on empty/valid history;
- duplicate `(shift_id, report_type, version)` history fails before current
  backfill/constraint creation;
- `_report_tables.py` owns Report table construction;
- `tables.py` only imports/wires the builder and remains at or below 300;
- migrations 001-006 have zero-byte diff;
- no destructive row deletion/content/status rewrite is allowed.

### 3.3 Ledger parity and transaction modes

- Protocol adds only SPEC R25 Report methods, complete shift-bound Task/
  CustomerRequest reads, `unit` support for corrections, and the bounded
  report transaction mode needed by R22;
- `_report_store.py` owns SQL Report/source reads and row mapping;
- `_report_repository.py` owns InMemory Report/source reads and copy
  semantics;
- host ledger/repository files only wire mixins/state/rollback and transaction
  mode while respecting hard limits;
- no unrelated event/task/customer/incident/handover persistence semantics
  change;
- existing callers using `transaction()` with no mode remain compatible.

### 3.4 Snapshot and service split

- `report_snapshot.py` is the single R3-R9 source selection/normalization/
  digest/limit implementation used at generate/review/approve/freeze;
- `report_service.py` owns R5 and R10-R18 Report commands;
- `report_freeze.py` owns Report readiness/freeze/idempotent integrity logic
  used by ShiftService;
- routers perform validation/dependency/error mapping only;
- no production module imports provider code;
- no caller content/status/type/version/digest/actor authority.

### 3.5 Approval and freeze

- permission map adds exactly the four R14 actions;
- approval receipt resolver adds only `("Report","report.approve")` with
  exact current IN_REVIEW/R2/version/digest derivation;
- ShiftService removes `_UNIMPLEMENTED_PREREQUISITES` and the override audit;
- legacy freeze fields remain deprecated/refused exactly as R19;
- handover readiness, Report FROZEN, Shift FROZEN and two audits are one
  transaction;
- existing handover tests/runners replace the retired override with genuine
  approved Report setup; historical receipts are not rewritten.

### 3.6 Contract and OpenAPI history

- Report API/JSON Schema is exactly SPEC R2-R4/R26-R28;
- the historical loose-schema facts are asserted in tests rather than
  fabricating an additional runtime schema;
- all four chained historical OpenAPI tests strip exactly the Report delta
  and retain their true earlier hashes;
- no unrelated operation/schema delta is accepted by digest refresh;
- Report/domain/workflow docs state only implemented operational behavior,
  not P5 rendering/export.

### 3.7 Tests and receipts

- new test modules remain coherent by concern; no catch-all compression;
- all existing override-dependent tests/runners use real Report setup;
- the three existing 300-line paths
  `scripts/run_postgres_live_roundtrip.py`,
  `scripts/run_handover_live_governance_evidence.py`, and
  `tests/cvf/test_freeze_invariant.py` change line-neutrally by removing
  superseded override comments/setup or delegating to the new bounded Report
  helpers; they may not exceed 300 or create a new split/debt path;
- BUILD receipt records commands/counts/failures/repairs/changed-set/nonclaims;
- live receipt stores only sanitized provider/model/host/status/call counts
  and durable admitted facts;
- `CVF_CONTROL_MAPPING.md` changes only Report approval/freeze qualification;
- catalog files change only through
  `python scripts/generate_catalog.py --write`.

No roadmap, `IMPLEMENTATION_STATUS.json`, continuity file or P2-R
authorization artifact is a C3 path.

## 4. Protected boundary

Zero-line/byte diff is mandatory for:

- migrations 001-006;
- operations-domain types/lifecycle semantics unrelated to Report;
- Incident/Handover/API behavior except the exact retired-override fixtures;
- authentication/JWT/dependency and user-provisioning code;
- approval policy YAML and risk-role ranking;
- messages, external Integration Edge, channels and canonical-message schema;
- P2-C frontend, P2-D offline/realtime, worker and reporting-engine stubs;
- P5 rendering/export/template surfaces;
- `.cvf/**`, CI/workflows, dependency manifests and lockfiles;
- file-size guard/debt/exception registry;
- roadmap, `IMPLEMENTATION_STATUS.json`, continuity and prior receipts;
- provider configuration/adapter implementation.

No production data/service, managed database or external channel credential
may be accessed.

## 5. Authorization checkpoint, pre-BUILD checkpoint and G6

### Authorization checkpoint

Contains exactly:

- this Work Order;
- its authorization review;
- active handoff;
- canonical active state;
- compatibility mirror;
- session memory.

It contains zero implementation/source/test/schema/migration/contract/live
receipt changes.

### Pre-BUILD checkpoint

After explicit R2 human approval and the pushed authorization checkpoint, a
separate commit contains exactly the four continuity surfaces:

- active handoff;
- canonical active state;
- compatibility mirror;
- session memory.

It records implementation/reviewer identities, acknowledgment of the exact
59 paths, parent commit, G6 outcome, no-CLI delegation boundary, and return
token. It contains no implementation.

### G6

Immediately before BUILD:

1. `HEAD == origin/main` at pushed pre-BUILD checkpoint; worktree clean;
2. core HEAD/origin/manifest equal
   `27137db4d9aa2aea931ddd2507185d5c24943080`; core clean;
3. canonical/mirror/handoff agree and worker rehydrates all required reads;
4. Docker daemon/image, psycopg and provider prerequisites are checked without
   printing or persisting secrets;
5. full baseline `python -m pytest -q` passes with exact counts;
6. validator/catalog/session/file-size/JSON/diff/doctor gates pass;
7. no owned test container/volume residue exists.

Any failure records `BLOCKED_G6`; no implementation edit may begin.

## 6. Required implementation order

1. Report domain/lifecycle/contract and focused unit tests;
2. migration/table/schema-parity tests;
3. Protocol/InMemory/SQLite Report parity and rollback;
4. deterministic snapshot/digest/limit implementation;
5. Report permission/service/API/OpenAPI;
6. receipt-bound approval and atomic freeze replacement;
7. update every retired-override fixture;
8. PostgreSQL target, migration/reconnect/rollback/concurrency proof;
9. provider runner tests, then one live call;
10. control mapping, generated catalog and receipts;
11. full gates, exact inventory and worker return.

Provider execution cannot precede passing focused/full non-live and
PostgreSQL admission proof.

## 7. Mandatory evidence commands

Focused non-live:

```powershell
python -m pytest -q tests/unit/test_report_snapshot.py tests/unit/test_report_openapi_contract.py tests/unit/test_operations_domain_shim_identity.py tests/unit/test_operations_domain_serialization.py tests/unit/test_p2b_openapi_contract.py tests/unit/test_p2c_read_openapi_contract.py tests/unit/test_shift_create_openapi_contract.py tests/unit/test_message_openapi_contract.py tests/cvf/test_report_vertical.py tests/cvf/test_report_approval.py tests/cvf/test_report_freeze.py tests/cvf/test_ledger_protocol.py tests/cvf/test_freeze_invariant.py tests/cvf/test_atomic_mutation_audit.py tests/cvf/test_customer_request_vertical.py tests/cvf/test_shift_close_freeze_interaction.py tests/integration/test_report_ledger_parity.py tests/integration/test_schema_parity_reports.py tests/integration/test_schema_parity.py tests/integration/test_postgres_live_runner.py tests/integration/test_report_live_evidence_runner.py tests/integration/test_handover_live_evidence_runner.py
```

Full and repository gates:

```powershell
python -m pytest -q
python scripts/testing/validate_repository.py
python scripts/generate_catalog.py --check
python scripts/check_session_state.py
python scripts/check_file_size.py
git diff --check
```

Live PostgreSQL and provider:

```powershell
python scripts/run_postgres_live_roundtrip.py --json
python scripts/run_report_live_governance_evidence.py --json
```

Also required:

- JSON parse for every changed JSON file;
- exact 59-path inventory and protected-boundary zero diff;
- diff/output/receipt secret scan;
- doctor `PASS WITH NOTE (24/1)` with only the bounded legacy warning;
- C3-parent (pushed pre-BUILD checkpoint) rollback rehearsal in an isolated
  temporary worktree, exact baseline restoration and cleanup.

No command may expose a provider key, JWT, password or database URL.

## 8. Live evidence matrix

PostgreSQL evidence must satisfy SPEC R30, run all six coherent live modules
(core, incident, handover, shift-create, message, Report), apply/reapply
migrations 001-007, and clean exactly its owned container/anonymous volumes.

Provider evidence observes exactly zero calls for each SPEC R31 refusal.
Before one real call it must read back:

- genuine CLOSED shift and acknowledged, current handover;
- generated current Report and exact digest;
- receipt from a distinct currently-authorized R2 approver;
- APPROVED then FROZEN Report;
- FROZEN Shift;
- exact Report/Shift freeze audits;
- zero override audit.

Exactly one real provider call may then request the deterministic expected
token. The Report API itself never calls a provider.

## 9. Secret and resource discipline

Never print/store API keys, JWT secrets/tokens, passwords, full database URLs,
Authorization values, raw provider bodies or machine-local secrets.

Docker actions are limited to the official uniquely named owned PostgreSQL 16
container and captured anonymous volumes. No broad prune/removal command is
allowed. Cleanup must run on success, failure, skip and interruption without
targeting pre-existing resources.

## 10. Stop conditions

Stop without waiver on:

- any path outside the exact 59;
- any protected-boundary drift;
- failed G6 or dirty/unpushed parent;
- caller-authored Report truth;
- mutable/overwritten history or ambiguous current Report;
- stale/wrong-scope approval accepted;
- partial Report/audit or Report/Shift freeze;
- concurrent stale freeze admitted;
- cross-backend/schema/migration mismatch;
- raw SQL/driver/internal exception at HTTP/evidence boundary;
- unrelated OpenAPI delta;
- file above hard limit or debt-registry change;
- failing/skipped required test;
- missing/ambiguous provider/PostgreSQL prerequisite;
- refusal call delta not zero or admitted delta not one;
- secret-bearing output/receipt;
- Docker residue/ownership uncertainty;
- P5/P2-C/P2-D/Phase-2 or production-readiness overclaim.

## 11. Worker return, review and commit ownership

The implementation worker returns:

- role declaration and exact parent/G6 acknowledgment;
- all 59 changed paths with per-path rationale;
- exact test/live commands and counts;
- sanitized receipt/call/cleanup results;
- all failures/repairs and preserved nonclaims;
- `READY_FOR_INDEPENDENT_P2R_BUILD_REVIEW`.

The worker must not stage, commit, push, self-review or FREEZE.

An independent reviewer compares source, SPEC R1-R33, AC-01..AC-32, exact
inventory, live receipts and claim boundaries. Findings return only to the
bounded repair worker. Any repair outside the 59 paths requires a governed
amendment.

Only `REVIEW_PASS` authorizes the Commit Steward to stage exactly the 59
paths, verify staged inventory/diff, commit C3 once and push. Authorization,
pre-BUILD continuity, C3 BUILD and C4 closure remain separate commits.

## 12. C4 and rollback

Only after pushed C3 and independent post-push verification may C4 update
roadmap, `IMPLEMENTATION_STATUS.json`, continuity and any generated truth not
owned by C3. C4 must use SPEC R33 verbatim or more narrowly.

C4 does not open P2-C. The next tranche is fresh P2-C mutation/full UI intake
under the operator-selected order.

Rollback rehearsal uses an isolated temporary worktree and never rewrites
history. Operational rollback, if later required, is a normal `git revert`
of C3 followed by the same gates.

## 13. Current disposition

Work Order authorization review is `REVIEW_PASS` after
`P2R-WO-REV-F1..F2` repair. Explicit R2 human approval is still required.

No BUILD, implementation edit, provider call, Docker/PostgreSQL run, staging,
commit or push authority is granted by this draft.
