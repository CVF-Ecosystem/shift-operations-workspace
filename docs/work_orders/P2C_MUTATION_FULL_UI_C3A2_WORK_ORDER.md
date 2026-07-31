# Work Order — P2-C C3a2 Operational Assignment Enforcement

- ID: `P2C-MUTATION-FULL-UI-C3A2-WO-001`
- Tranche: `P2C-MUTATION-FULL-UI-2026-07-31`
- Checkpoint: `C3a2`
- Risk: `R2`
- Reviewed implementation parent: `ec90c78c98c6d314e81d7b50506b514c81f7f580`
- Parent DESIGN: `docs/decisions/ADR_2026-07-31_P2C_MUTATION_FULL_UI.md`
- Parent SPEC: `docs/specs/P2C_MUTATION_FULL_UI_SPEC.md`
- Fan-out DESIGN amendment:
  `docs/decisions/ADR_2026-07-31_P2C_C3A_FANOUT_ADDENDUM.md`
- Fan-out SPEC amendment:
  `docs/specs/P2C_MUTATION_FULL_UI_SPEC_AMENDMENT_1.md`
- Status: `APPROVED — BUILD ONLY AFTER PUSHED PRE-BUILD CHECKPOINT AND G6`

## 1. Authority, roles and checkpoint boundary

The operator delegated Work Order approval authority to Codex. Codex authors
this exact-path authorization. An independent reviewer MUST compare it with
the pushed C3a1 contract, R6-R10/R30 and current source before approval.

The later `IMPLEMENTATION_WORKER` may edit only the exact C3a2 BUILD paths
below and MUST NOT stage, commit, push, self-review or FREEZE. No Claude CLI,
provider-control MCP or automated Claude call is authorized. Codex may become
`COMMIT_STEWARD` only after an independent `REVIEW_PASS` of the BUILD.

C3a2 consumes C3a1 at `ec90c78`: it adds route-wide operational assignment
enforcement and migrates affected fixtures. It does not reopen assignment
storage, staffing lifecycle or creator bootstrap. C3b, C3c and C3d remain
unauthorized.

## 2. Exact 79-path C3a2 BUILD ceiling

Every path below is expected to change or be created. There is no wildcard,
conditional allowance, reserve or self-review path.

### Operational scope implementation — 23 paths

1. `apps/workspace-api/src/workspace_api/application/assignment_scope.py` — NEW
2. `apps/workspace-api/src/workspace_api/dependencies.py`
3. `apps/workspace-api/src/workspace_api/api/approvals/router.py`
4. `apps/workspace-api/src/workspace_api/api/corrections/router.py`
5. `apps/workspace-api/src/workspace_api/api/customer_requests/router.py`
6. `apps/workspace-api/src/workspace_api/api/events/router.py`
7. `apps/workspace-api/src/workspace_api/api/handovers/router.py`
8. `apps/workspace-api/src/workspace_api/api/incidents/router.py`
9. `apps/workspace-api/src/workspace_api/api/messages/router.py`
10. `apps/workspace-api/src/workspace_api/api/reports/router.py`
11. `apps/workspace-api/src/workspace_api/api/shifts/router.py`
12. `apps/workspace-api/src/workspace_api/api/tasks/router.py`
13. `apps/workspace-api/src/workspace_api/application/approval_receipts.py`
14. `apps/workspace-api/src/workspace_api/application/correction_service.py`
15. `apps/workspace-api/src/workspace_api/application/customer_request_service.py`
16. `apps/workspace-api/src/workspace_api/application/handover_service.py`
17. `apps/workspace-api/src/workspace_api/application/incident_service.py`
18. `apps/workspace-api/src/workspace_api/application/message_service.py`
19. `apps/workspace-api/src/workspace_api/application/report_service.py`
20. `apps/workspace-api/src/workspace_api/application/services.py`
21. `apps/workspace-api/src/workspace_api/application/shift_service.py`
22. `apps/workspace-api/src/workspace_api/application/task_creation_intents.py`
23. `apps/workspace-api/src/workspace_api/application/task_service.py`

### Existing fixture and regression migration — 38 paths

24. `tests/cvf/_approver_identity_support.py`
25. `tests/cvf/_customer_request_fixtures.py`
26. `tests/cvf/_shift_close_fixtures.py`
27. `tests/cvf/test_approval_known_principals.py`
28. `tests/cvf/test_approver_identity_receipts.py`
29. `tests/cvf/test_approver_identity_reconciliation.py`
30. `tests/cvf/test_approver_identity_task_intents.py`
31. `tests/cvf/test_assignment_foundation.py`
32. `tests/cvf/test_atomic_mutation_audit.py`
33. `tests/cvf/test_correction_vertical.py`
34. `tests/cvf/test_customer_request_repair.py`
35. `tests/cvf/test_customer_request_transitions.py`
36. `tests/cvf/test_customer_request_vertical.py`
37. `tests/cvf/test_freeze_invariant.py`
38. `tests/cvf/test_handover_vertical.py`
39. `tests/cvf/test_incident_vertical.py`
40. `tests/cvf/test_message_admission.py`
41. `tests/cvf/test_report_approval.py`
42. `tests/cvf/test_report_freeze.py`
43. `tests/cvf/test_report_vertical.py`
44. `tests/cvf/test_shift_close_freeze_interaction.py`
45. `tests/cvf/test_shift_close_governance.py`
46. `tests/cvf/test_shift_create_admission.py`
47. `tests/cvf/test_task_vertical.py`
48. `tests/cvf/test_vertical_end_to_end.py`
49. `tests/integration/test_evidence_persistence.py`
50. `tests/integration/test_handover_ledger_parity.py`
51. `tests/integration/test_handover_postgres_live.py`
52. `tests/integration/test_incident_postgres_live.py`
53. `tests/integration/test_message_postgres_live.py`
54. `tests/integration/test_message_sqlite.py`
55. `tests/integration/test_p2c_read_api.py`
56. `tests/integration/test_p2c_read_postgres_limit_live.py`
57. `tests/integration/test_report_postgres_live.py`
58. `tests/integration/test_shift_create_live_evidence_runner.py`
59. `tests/integration/test_shift_create_postgres_live.py`
60. `tests/integration/test_shift_create_sqlite.py`
61. `tests/integration/test_sql_ledger_handovers.py`

### Feature-owned enforcement proof — 6 paths

62. `tests/cvf/_assignment_scope_fixtures.py` — NEW
63. `tests/cvf/test_assignment_scope_routes.py` — NEW
64. `tests/cvf/test_assignment_scope_cross_shift.py` — NEW
65. `tests/cvf/test_assignment_scope_enumeration.py` — NEW
66. `tests/integration/test_assignment_scope_postgres_live.py` — NEW
67. `tests/integration/test_assignment_scope_live_evidence_runner.py` — NEW

### Runners, receipts and truth surfaces — 12 paths

68. `scripts/run_postgres_live_roundtrip.py`
69. `scripts/run_handover_live_governance_evidence.py`
70. `scripts/run_report_live_governance_evidence.py`
71. `scripts/run_incident_live_governance_evidence.py`
72. `scripts/run_p2c_read_live_governance_evidence.py`
73. `scripts/run_assignment_scope_live_governance_evidence.py` — NEW
74. `tests/integration/test_postgres_live_runner.py`
75. `docs/decisions/P2C_C3A2_ASSIGNMENT_SCOPE_BUILD_EVIDENCE_RECEIPT.md` — NEW
76. `docs/decisions/P2C_C3A2_ASSIGNMENT_SCOPE_LIVE_EVIDENCE_RECEIPT.md` — NEW
77. `docs/cvf/CVF_CONTROL_MAPPING.md`
78. `docs/catalog/MODULE_REGISTRY.json`
79. `docs/catalog/MODULE_CATALOG.md`

A required path outside this list is `BLOCKED_WORK_ORDER_CEILING`. Stop before
editing it. Resume requires reviewed DESIGN→SPEC→WORK_ORDER amendment and a
renewed exact approval.

## 3. Implementation contract

### 3.1 One canonical server-side assignment guard

- `assignment_scope.py` owns the reusable ACTIVE-membership assertion and
  safe inaccessible-resource behavior; routers/services MUST not fork their
  own assignment logic;
- canonical shift identity is derived from the stored aggregate whenever a
  record id is supplied; a caller-provided `shift_id` cannot override stored
  ownership;
- the guard consumes C3a1 `get_active_assignment` behavior without changing
  assignment schema, lifecycle, uniqueness, staffing routes or audit shape;
- every mutation re-runs the guard even if a capability response previously
  advertised the action.

### 3.2 Exact R6 operational matrix

ACTIVE assignment is required for all existing shift-bound operations:

- shift list, open-work, close and freeze;
- internal message create;
- event create/list/confirm/correct;
- task creation-intent create/get, task create and transition;
- shift-bound customer-request create and transition;
- incident report/get/list/acknowledge/transition;
- handover create/get/list/review/acknowledge;
- Report generate/get/list/version/submit/approve;
- approval receipt creation for supported shift-bound targets.

`POST /shifts` remains the R4 bootstrap exception. Login, health and staffing
control-plane routes remain outside operational-resource reads. Null-shift
customer requests remain outside the shift console and receive no assignment
scope claim.

### 3.3 Cross-shift and stored-target rules

- handover create and review require source-shift assignment;
- handover acknowledge requires destination-shift assignment;
- approval target shift is resolved from the stored supported target before
  scope is checked; caller-supplied record type/id or scope assertions cannot
  confer access;
- task-intent get resolves the intent's stored task/shift before checking;
- every id-based operation resolves the stored record first and does not use
  a request-body shift id as authority.

### 3.4 Enumeration-safe and atomic refusal

- unauthenticated remains 401 and coarse permission denial remains 403;
- missing and inaccessible operational records share the same sanitized 404
  status and body shape;
- malformed input remains controlled 422; stale version/lifecycle remains
  controlled 409 only after scope is admitted;
- assignment refusal occurs before domain mutation, audit, approval receipt
  or provider call and leaves all of them unchanged;
- list routes return only assigned shifts/records; an unassigned record is
  never revealed through count, ordering, identifier or body differences.

### 3.5 Fixture migration and hard limits

- legacy tests that exercise governed services/routes create persisted ACTIVE
  assignment explicitly through shared feature-owned fixtures;
- the four authorized legacy live runners seed their existing principals as
  persisted active users with explicit ACTIVE assignments before invoking the
  newly scoped path; they preserve their established refusal/admission and
  provider call-count assertions;
- direct ledger setup remains available only where the test intentionally
  proves legacy/unassigned denial or migration behavior;
- no production bypass, autoprovisioning, blanket monkeypatch or default
  assignment is allowed to preserve an old test;
- every Python file remains <=300 physical lines with no new debt/exemption;
  near-limit hosts use line-neutral imports or the six authorized companions;
  handover/report/P2C-read runner repairs are line-neutral because their
  current physical sizes are 298/297/299 lines.

### 3.6 Evidence and truth

- focused matrices cover every R6 route/action, R7 cross-shift/nullable rule,
  R8 response shape and R9 capability non-authority behavior;
- InMemory, SQLite and disposable PostgreSQL 16 prove equivalent assignment
  admission/refusal, migration reapply and rollback with exact cleanup;
- fresh live evidence runs refusal cases at zero provider calls, verifies one
  durable assignment-scoped admitted operation and its audit, then performs
  exactly one sanitized real-provider call;
- receipts record exact counts, failures/repairs, changed set and cleanup and
  do not expose raw secret, bearer token, DSN, URL credential, provider body
  or raw exception;
- AC-29 runs in an isolated temporary worktree (or equivalent isolated tree)
  at the exact recorded pre-BUILD parent, proves that parent's baseline and
  repository gates, then removes and prunes the temporary tree; it MUST NOT
  stash, reset or mutate the primary candidate worktree, and its parent hash,
  results and cleanup are recorded in the BUILD receipt;
- catalog and control mapping state only the C3a2 bounded truth.

## 4. Protected boundary

Zero diff is mandatory for:

- migration 008, assignment model/table/store/repository/ledger protocol,
  `AssignmentService`, staffing router and C3a1 staffing/bootstrap semantics;
- authentication token format/TTL, user provisioning and global role policy;
- lifecycle, risk, evidence, approval quorum, Report content/freeze semantics;
- OpenAPI/schema shapes except pre-existing controlled status behavior;
- frontend, dependency/lock files, P2-D and full-shift exit surfaces;
- provider adapters/configuration, external channels and production data;
- `.cvf/**`, CI, file-size guard/debt list, roadmap, implementation status,
  continuity and all prior receipts.

## 5. Pre-BUILD G6

From a separate clean pushed pre-BUILD continuity commit:

1. verify `HEAD == origin/main`, clean worktree and record the exact parent;
2. rehydrate manifest/policy/memory/state/handoff/DESIGN/SPEC/amendment/WO;
3. verify C3a1 `ec90c78` is an ancestor and its final review receipt exists;
4. verify core/manifest/origin pin and doctor `PASS WITH NOTE 24/1` only;
5. run full non-live baseline and record exact pass/skip/warning counts;
6. pass session, catalog, file-size, repository, JSON and diff gates;
7. verify Docker/PostgreSQL/provider prerequisites without printing secrets;
8. verify zero owned container/volume residue.

Any failure is `BLOCKED_G6`; no source edit or provider call.

## 6. Required implementation and verification order

1. central guard and stored-record shift resolution;
2. read/list route scoping and enumeration-safe behavior;
3. mutation/service scoping, including approvals and task intents;
4. handover source/destination and nullable customer-request rules;
5. exact legacy fixture migration, then focused/full non-live tests;
6. disposable PostgreSQL migration/reapply/live suite and cleanup;
7. AC-29 isolated exact-parent baseline/gate rehearsal and complete cleanup;
8. fresh live proof in refusal→durable admission→one-call order;
9. catalog generation, repository gates and truthful receipts.

Required minimum commands include:

```powershell
python -m pytest -q tests/cvf/test_assignment_scope_routes.py tests/cvf/test_assignment_scope_cross_shift.py tests/cvf/test_assignment_scope_enumeration.py
python -m pytest -q
python scripts/run_postgres_live_roundtrip.py --json
python scripts/run_assignment_scope_live_governance_evidence.py
python scripts/generate_catalog.py --write
python scripts/check_session_state.py
python scripts/generate_catalog.py --check
python scripts/check_file_size.py
python scripts/testing/validate_repository.py
powershell -ExecutionPolicy Bypass -File scripts/initialize_cvf_clone.ps1
git diff --check
```

The AC-29 command sequence is environment-specific but MUST use the exact
recorded pre-BUILD parent in a separate temporary worktree/tree, run its
recorded full non-live baseline plus session/catalog/file-size/repository/diff
gates, and remove/prune that tree with path-absence proof afterward.

The worker return MUST report exact results, actual changed subset of the
79-path ceiling, failures/repairs, Docker cleanup, AC-29 parent hash/results/
temporary-tree cleanup, sanitized receipt result, zero staged files and:

`READY_FOR_INDEPENDENT_P2C_C3A2_BUILD_REVIEW`

## 7. Stop conditions and ownership

STOP on unexpected parent or continuity drift; any out-of-ceiling path;
C3a1 protected-boundary change; file-size overflow; scope bypass; inconsistent
404 shape; partial write; regression; Docker residue; missing PostgreSQL or
provider proof; secret exposure; nonzero provider call on refusal; or pressure
to combine C3a2 with C3b-d.

The worker MUST NOT stage, commit, push, self-review or FREEZE. Codex performs
independent BUILD review and becomes `COMMIT_STEWARD` only on `REVIEW_PASS`.
C3b still requires its own exact-path Work Order.

## 8. Claim boundary

C3a2 may prove only that the existing single-workspace operational routes in
R6/R7 enforce stored ACTIVE shift assignment, with enumeration-safe refusal
and capability non-authority, on the proven backends. It does not prove tenant
isolation, provider `data_scope`, token early revocation, production/managed
PostgreSQL, frontend mutation/full UI, P2-C completion, P2-D, the full-shift
exit gate or Phase-2 completion.
