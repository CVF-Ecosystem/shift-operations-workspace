# Independent EA Review - `shift-operations-workspace`

**Date:** 2026-07-22  
**Reviewer:** Codex, independent review role  
**Reviewed HEAD:** `c91c4fc` (review request), with application buildout at `7a3bb29`  
**Method:** Read the baseline review and governed front doors, inspected runtime code and tests, ran the full and focused test suites, measured the repository independently, and executed bounded negative/runtime probes. No implementation fix was made.

## Overall verdict

This repository has made real progress since the 2026-07-21 review: it now contains a small but coherent runtime, reusable CVF gate functions, 65 passing tests, a real SQLite-backed ledger, and three service-level verticals that import the same gate modules instead of copying them. However, the current headline claims are materially ahead of the implementation. I do **not** accept "12/12 controls enforced," "three golden verticals" as durable end-to-end paths, or "PostgreSQL same code path" as currently written. Freeze can be bypassed, approval identities can be fabricated by the caller, SqlLedger drops evidence needed by its own gate, Task cannot carry evidence through the HTTP API, audit is not atomic with mutation, and the PostgreSQL migration lacks a column that Task persistence always writes. This is now an early governed build rather than a blueprint-only skeleton, but it is still far from production and its integrity-of-claims score has fallen because several precise claims are disproved by the current code.

## Scorecard

| Dimension | Score | Reason |
|---|---:|---|
| Claim integrity / anti-over-claim | **5/10** | The repo honestly discloses no live PostgreSQL run, header-based identity, thin frontend, and AI-only cost/termination wiring. But stronger claims about 12/12 enforcement, non-bypassable approval, schema parity, catalog drift protection, and the PostgreSQL path are not supported. Several front-door artifacts are stale. |
| Quality of real code | **6/10** | The code is compact, readable, typed, and sensibly split. The main deductions are missing transactional boundaries, backend semantic divergence, missing persistence for evidence, and shallow integration coverage. |
| Coverage versus declared architecture | **3.5/10** | 6/20 catalog modules have runtime behavior (`enforced` or `partial`); only 2/20 are labeled enforced. Fourteen modules remain contract-only or stub, and Phase 4/5 product capability is not built. |
| CVF control enforcement in code | **4/10** | Callable/tested primitives exist for all 12 labels, which is a major improvement. Several are not load-bearing or do not enforce their declared policy: identity/approval trust caller assertions, data minimization is advisory, refusal routing/recording is absent, freeze prerequisites and parent-shift freeze are bypassable, and audit can fail after mutation commits. |
| Production readiness | **2/10** | No authenticated identity, no verified approval records, no successful PostgreSQL round trip, a statically identifiable PostgreSQL Task failure, no atomic governed mutation, incomplete SQL domain coverage, and only a minimal frontend shell. |

## Measured evidence

### Commands run

| Command / probe | Result |
|---|---|
| `python -m pytest -q` | **65 passed in 1.12s**; one `pytest-asyncio` deprecation warning |
| `python -m pytest -q tests/integration/test_sql_ledger_sqlite.py tests/integration/test_sql_ledger_integrity.py tests/integration/test_schema_parity.py` | **12 passed in 0.86s** |
| `python scripts/generate_catalog.py --check` | PASS, but the negative probe below proves it does not validate generated metrics or Markdown drift |
| `python scripts/testing/validate_repository.py` | PASS on the unmodified tree |
| Independent in-memory call to `enrich_metrics` | 20 modules, 2,312 module LOC, 85 module code files; `enforced=2`, `partial=4`, `contract-only=6`, `stub=8` |
| Session negative probe: nonexistent `active_handoff` | `check_session_state.py` failed with exit 1, as expected |
| File-size negative probe: temporary Python hard limit of 1 line | `check_file_size.py` failed with exit 1, as expected |
| Catalog negative probe: temporary registry `code_loc=999999` | `generate_catalog.py --check` still returned PASS; `validate_repository.py` also returned PASS |

All negative-probe edits were reverted. The worktree was clean after probe cleanup and before this report was created.

### Independent repository measurements

Excluded `.git`, caches, virtual environments, `node_modules`, `dist`, and `build`.

| Measurement | Observed |
|---|---:|
| Total files | 488 |
| Markdown files / lines | 307 / 4,291 |
| Python + TypeScript + TSX files / lines, including tests and scripts | 103 / 3,941 |
| Runtime source under `apps/` and `packages/`, excluding tests | 84 files / 2,300 lines |
| Test files / lines | 14 / 1,109 |
| Markdown-to-all-code LOC ratio | 1.09:1 |
| Markdown-to-runtime-source LOC ratio | 1.87:1 |
| Modules with runtime behavior | 6/20 (30%) |
| Modules labeled enforced | 2/20 (10%) |

The baseline review's approximately 5:1 docs/code ratio is no longer current. The repository now has substantial code and tests, but most of the architecture's module surface is still not runtime behavior: 14/20 modules are contract-only or stub.

## Findings

### Critical 1 - Freeze is not a load-bearing system control

The profile requires `shift_closed`, `report_approved`, and linked open handover items before freeze (`packages/cvf-application-profile/freeze-policy.yaml:1`). The API nevertheless freezes a newly created OPEN shift without identity, permission, report, or handover checks (`apps/workspace-api/src/workspace_api/api/shifts/router.py:10`, `apps/workspace-api/src/workspace_api/api/shifts/router.py:18`). My HTTP probe returned `200 FROZEN` immediately.

The freeze boundary is also bypassable after a shift becomes frozen:

- `EventService.confirm` checks only the event data-state transition, not the parent shift (`apps/workspace-api/src/workspace_api/application/services.py:46`, `apps/workspace-api/src/workspace_api/application/services.py:52`).
- `TaskService.transition` checks only task status (`apps/workspace-api/src/workspace_api/application/task_service.py:76`, `apps/workspace-api/src/workspace_api/application/task_service.py:78`).
- `SqlLedger.add_event`, `put_event`, `add_task`, and `put_task` never inspect shift status (`packages/operations-ledger/src/operations_ledger/sql_ledger.py:111`, `packages/operations-ledger/src/operations_ledger/sql_ledger.py:127`, `packages/operations-ledger/src/operations_ledger/sql_ledger.py:137`, `packages/operations-ledger/src/operations_ledger/sql_ledger.py:151`).
- InMemoryLedger blocks *new* events/tasks on a frozen shift (`apps/workspace-api/src/workspace_api/infrastructure/repository.py:47`, `apps/workspace-api/src/workspace_api/infrastructure/repository.py:61`), while SqlLedger permits them. The two backends therefore do not enforce the same behavior.
- The existing freeze vertical test freezes the event object itself, not its parent shift (`tests/cvf/test_vertical_end_to_end.py:120`). It does not exercise the architecture's shift freeze boundary.

Runtime probes confirmed all of the following were allowed: confirming a pre-existing event after its shift was frozen; transitioning a task after its shift was frozen; and adding an event/task through SqlLedger after the shift was frozen.

This disproves full freeze enforcement and weakens the three-vertical claim. Severity is critical because freeze is the repository's core immutability boundary.

### Critical 2 - The durable golden vertical loses evidence and R2+ confirmation fails

`event_row` and `row_to_event` do not persist or reconstruct `OperationalEvent.evidence` (`packages/operations-ledger/src/operations_ledger/_rows.py:24`, `packages/operations-ledger/src/operations_ledger/_rows.py:40`). The migration defines `evidence_links` (`database/migrations/001_foundation.sql:45`), but SqlLedger never maps or queries it. The SQLite reconnect test asserts basic event fields and risk only, not evidence (`tests/integration/test_sql_ledger_sqlite.py:47`, `tests/integration/test_sql_ledger_sqlite.py:68`).

My SqlLedger probe stored an R2 event with one evidence item, read it back with zero evidence items, and then called `EventService.confirm`. The service refused with `[evidence] R2 requires at least 1 evidence link(s); found 0`. Thus the event golden vertical passes only on InMemoryLedger for risk classes that require evidence; it is not an end-to-end durable vertical.

Task has a second evidence break. `TaskService.create_task` correctly requires evidence for higher risk (`apps/workspace-api/src/workspace_api/application/task_service.py:54`), but `TaskInput` exposes no evidence field and the router constructs `Task` without evidence (`apps/workspace-api/src/workspace_api/api/tasks/router.py:18`, `apps/workspace-api/src/workspace_api/api/tasks/router.py:37`). An HTTP probe supplied an `evidence` array plus a valid R3 quorum; Pydantic ignored the extra field, the service saw zero evidence, and the request returned 409. The service-level R3 test succeeds only because it bypasses the API and directly constructs a Task with evidence (`tests/cvf/test_task_vertical.py:42`, `tests/cvf/test_task_vertical.py:87`).

The phrase "three golden verticals" is acceptable only if explicitly scoped to selected service-level tests on InMemoryLedger. It is false as a durable/API end-to-end claim.

### High 3 - PostgreSQL Task persistence is statically broken, and the parity test misses real column drift

The production PostgreSQL container initializes from the SQL migrations (`docker-compose.yml:9`). Migration 002 creates `tasks` without a `version` column (`database/migrations/002_tasks_customers_reports.sql:1`). The SQLAlchemy table declares `version` (`packages/operations-ledger/src/operations_ledger/tables.py:104`, `packages/operations-ledger/src/operations_ledger/tables.py:116`), and every Task insert/update supplies it (`packages/operations-ledger/src/operations_ledger/_rows.py:56`, `packages/operations-ledger/src/operations_ledger/_rows.py:67`). A migration-created PostgreSQL `tasks` table will therefore reject the runtime's Task statement because the column does not exist.

The SQLite tests mask this by calling `metadata.create_all(engine)` instead of exercising the migration-created schema (`tests/integration/test_sql_ledger_sqlite.py:41`, `tests/integration/test_sql_ledger_integrity.py:28`).

The parity test is not strict enough for its claim:

- it checks that mapped table names exist (`tests/integration/test_schema_parity.py:58`);
- it compares only referenced **table names**, not FK columns/options (`tests/integration/test_schema_parity.py:64`);
- for CHECK constraints it verifies only that at least one CheckConstraint exists, not that the expressions match (`tests/integration/test_schema_parity.py:81`).

It does not compare columns, types, nullability, defaults, primary keys, exact FKs, or exact CHECK expressions. An independent column-set comparison reported `tasks: code_only=['version'] migration_only=[]`, while the official parity suite still passed.

The limitation "PostgreSQL round-trip not yet run" is honest. The additional phrase "same code path" is not an adequate limitation because current static evidence predicts an actual PostgreSQL Task failure.

### High 4 - "12/12 enforced" conflates callable primitives with trusted, load-bearing controls

There is real value in `cvf-runtime`: the gate functions are not empty and their unit tests exercise denial paths. But several controls do not meet the catalog definition of runtime enforcement that blocks violations.

1. **Identity and approval are caller assertions.** `get_principal` trusts `X-User-Id` and `X-User-Role` headers (`apps/workspace-api/src/workspace_api/dependencies.py:20`). `Approval` contains only caller-supplied `approver_id` and `role` strings (`packages/cvf-runtime/src/cvf_runtime/approval.py:26`), and confirm accepts those records in the same request (`apps/workspace-api/src/workspace_api/api/events/router.py:32`, `apps/workspace-api/src/workspace_api/api/events/router.py:52`). A probe using self-asserted supervisor headers and two fabricated approver identities/roles confirmed an R3 event with HTTP 200. The quorum *shape* is checked, but approver identity and authority are not verified.

2. **Data minimization is advisory.** Policy says INTERNAL requires minimization before external AI (`packages/cvf-application-profile/data-policy.yaml:4`). `assert_placement_allowed` includes external placement in the allowed set for `allow_after_minimization` and accepts no `minimized` evidence/state (`packages/cvf-runtime/src/cvf_runtime/data_scope.py:29`, `packages/cvf-runtime/src/cvf_runtime/data_scope.py:52`). The test only checks that a separate helper returns `True` (`tests/cvf/test_remaining_controls.py:65`). My probe confirmed INTERNAL-to-EXTERNAL was allowed without minimization evidence.

3. **Data scope, cost, and termination have no runtime caller.** The roadmap itself leaves the wiring open (`docs/implementation/EXECUTION_ROADMAP.md:107`). The mapping marks only cost and termination as AI-gated (`docs/cvf/CVF_CONTROL_MAPPING.md:56`), but data_scope is equally non-load-bearing today.

4. **Refusal policy is not implemented as declared.** The policy requires routing to a supervisor and recording the reason (`packages/cvf-application-profile/refusal-policy.yaml:7`). `policy_loader.py` does not load refusal-policy or freeze-policy (`packages/cvf-runtime/src/cvf_runtime/policy_loader.py:24`), and `CvfDenied` is only an exception container (`packages/cvf-runtime/src/cvf_runtime/errors.py:11`). Denied attempts are not routed or durably audited.

5. **Freeze is materially bypassable**, as Finding 1 shows.

The accurate statement is: "all 12 control names have code-level primitives or domain checks and at least one test; only a subset is currently trusted and load-bearing in implemented request paths."

### High 5 - Governed mutation and audit are not atomic

`EventService.confirm` updates the event first and appends audit afterward (`apps/workspace-api/src/workspace_api/application/services.py:70`, `apps/workspace-api/src/workspace_api/application/services.py:77`). Correction performs three separate operations: update event, insert correction, append audit (`apps/workspace-api/src/workspace_api/application/correction_service.py:91`, `apps/workspace-api/src/workspace_api/application/correction_service.py:105`, `apps/workspace-api/src/workspace_api/application/correction_service.py:107`). Each SqlLedger method opens and commits its own transaction (`packages/operations-ledger/src/operations_ledger/sql_ledger.py:127`, `packages/operations-ledger/src/operations_ledger/sql_ledger.py:159`, `packages/operations-ledger/src/operations_ledger/sql_ledger.py:179`).

A failure-injection probe made `append_audit` raise. `EventService.confirm` returned an error, but the event remained `CONFIRMED` with zero audit records. The same partial-commit shape exists in the SQL backend and correction path.

Therefore audit is not an enforced invariant of mutation; it is a best-effort follow-up on the happy path. This must be fixed before `audit` or `operations-ledger` is called enforced for governed mutations.

### Medium 6 - Catalog and repository validation do not protect generated metrics from drift

`generate_catalog.py --check` calls only `verify`, which validates module IDs, paths, status vocabulary, controls, and dependency names (`scripts/generate_catalog.py:65`, `scripts/generate_catalog.py:229`). The check branch never calls `enrich_metrics` or `render_markdown`, despite the comment claiming metrics are compared (`scripts/generate_catalog.py:251`). `validate_repository.py` delegates to this same shallow command (`scripts/testing/validate_repository.py:41`).

Negative probe:

1. temporarily changed registry total `code_loc` from 2,312 to 999,999;
2. ran `python scripts/generate_catalog.py --check` - PASS;
3. ran `python scripts/testing/validate_repository.py` - PASS;
4. reverted and revalidated.

The file-size and session-state checks are real gates: their negative probes failed correctly. The catalog check is real only for registry structure. It is decoration for metrics freshness and generated Markdown drift, and it cannot validate whether a self-reported semantic status such as `enforced` is true.

### Medium 7 - Canonical status surfaces have already drifted

Several front-door artifacts contradict the actual repository:

- `IMPLEMENTATION_STATUS.json` still says 25 tests, four profile-only controls, one golden vertical, and in-memory-only persistence (`IMPLEMENTATION_STATUS.json:9`, `IMPLEMENTATION_STATUS.json:15`, `IMPLEMENTATION_STATUS.json:17`, `IMPLEMENTATION_STATUS.json:24`).
- `CVF_CONTROL_MAPPING.md` lists only two verticals and says Task is future work (`docs/cvf/CVF_CONTROL_MAPPING.md:13`, `docs/cvf/CVF_CONTROL_MAPPING.md:18`). It also says SqlLedger has only structural conformance testing (`docs/cvf/CVF_CONTROL_MAPPING.md:65`), while SQLite round-trip tests now exist.
- The roadmap's final "single next step" still includes Task as work to do and relies on the disproved "same code path" premise (`docs/implementation/EXECUTION_ROADMAP.md:147`).
- `ARCHITECTURE.md` still says implementation has not started (`ARCHITECTURE.md:7`).
- `SESSION/SESSION_MEMORY.md` reports 51 tests while active session state reports 65.

This is classic spec/status drift. The machine session state and generated catalog are newer, but a new reviewer following all mandatory reads receives conflicting truth.

### Low 8 - The frontend/backend boundary is structurally respected, but the frontend is not a product UI yet

The current frontend does not import backend domain or database code. Its only API call is `GET /health` through `VITE_API_URL` (`apps/workspace-web/src/services/api.ts:1`), so the intended HTTP boundary is respected in the code that exists.

There is no functional events/tasks/approvals UI to test. `App.tsx` is a local feed shell whose submit button only appends text to React state (`apps/workspace-web/src/app/App.tsx:16`, `apps/workspace-web/src/app/App.tsx:26`); feature directories contain README stubs; and the catalog has no frontend tests. The boundary document accurately admits this (`docs/architecture/FRONTEND_BACKEND_BOUNDARY.md:74`). Therefore the boundary is a valid structural foundation, but enforcement against a real frontend workflow remains aspirational.

## What is actually solid

1. **The buildout is real.** The repository is no longer the near-empty skeleton described on 2026-07-21. The 65-test suite is fast and reproducible in this environment.
2. **Gate reuse is genuine at import/call level.** Event, Correction, and Task services call the same `cvf_runtime` functions; I found no copied permission, evidence, or approval implementation in the later verticals (`services.py`, `correction_service.py`, `task_service.py`).
3. **Several gate primitives are well implemented within their bounded assumptions.** Unknown roles/actions fail closed; evidence counts and risk lookup work; approval enforces required role seats and distinct supplied IDs; task/data-state transition tables block illegal transitions.
4. **SQLite persistence is real for the mapped scalar fields.** Reconnect persistence, FK enforcement, time-window CHECK rejection, correction inserts, audit inserts, shift freeze persistence, and Task scalar persistence were exercised by the focused 12-test suite.
5. **The PostgreSQL limitation is disclosed.** The repo does not claim a live PostgreSQL pass. That honesty should be retained, while removing the unsupported "same code path" reassurance until migration-backed testing passes.
6. **Two governance gates survived negative testing.** Session-state reference integrity and file-size hard limits failed as designed and passed again after exact restoration.
7. **Frontend/backend separation is currently clean.** The frontend shell talks over HTTP and contains no copied CVF governance logic.

## Database operating model for follow-up implementation

The intended workflow is deliberately asymmetric and should be preserved:

- **SQLite is the default development backend.** Local coding, fast feedback, ordinary unit/integration tests, demos, and low-resource work should continue to use SQLite. Docker/PostgreSQL is not required for every development loop.
- **Docker PostgreSQL is the pre-ship backend gate.** Bring it up when validating a release candidate, deployment migration, or other explicit production-like integration checkpoint. A missing local Docker daemon does not block ordinary SQLite-based feature development.
- **The two databases are alternatives, not a replicated pair.** Do not run both simultaneously for normal operation and do not add automatic SQLite/PostgreSQL synchronization or silent failover.
- **Backend selection must remain explicit.** `DATABASE_URL` selects SQLite or PostgreSQL through the same `Ledger` contract. If PostgreSQL is selected and unavailable, fail clearly; do not silently fall back to SQLite in a shipping/production profile.
- **Behavioral parity is still required.** Every Ledger invariant should first have a fast SQLite test. Before shipping, the applicable suite must be rerun against a Docker PostgreSQL database initialized from the real SQL migrations. Only that pre-ship result authorizes a PostgreSQL-verified or dual-backend claim.
- **Fix static cross-backend defects during normal SQLite development.** The missing Task `version` migration, evidence persistence, freeze behavior, and transaction boundaries should be repaired now because they are source-contract defects; actually starting Docker can remain a later pre-ship checkpoint.

Implementation sequence for the next worker:

1. Keep SQLite as the default and make the complete governed vertical pass locally.
2. Make migration/table parity strict enough to catch PostgreSQL-shape defects without requiring Docker on every edit.
3. Add an explicitly invoked Docker PostgreSQL profile and reuse the same Ledger acceptance suite.
4. Run that profile only at the designated integration/pre-ship gate and record the result without changing the normal local workflow.

## Recommendations

1. **Immediately narrow the claims.** Replace "12/12 enforced," "non-bypassable R3/R4," "three golden verticals," and "PostgreSQL same code path" with bounded statements matching the evidence above. Do this before adding another domain.
2. **Repair freeze as a cross-record invariant.** Enforce freeze prerequisites, require identity/permission/audit on shift freeze, block every mutation under a frozen shift in both backends, and add API/service/SQLite negative tests using a frozen parent shift.
3. **Make each governed mutation atomic.** Introduce ledger unit-of-work operations for confirm, correct, task create/transition, and freeze so state/correction/evidence/approval/audit commit or roll back together.
4. **Persist and verify governance evidence.** Map `evidence_links` and approvals, reconstruct evidence on reads, add evidence to TaskInput, and accept approval references only after server-side identity/authority verification. P2-B authentication alone is insufficient if inline approval records remain caller-fabricated.
5. **Fix the schema authority and parity gate.** Add the missing Task `version` migration or stop writing it. Compare exact column sets, type families, nullability, defaults, PKs, FK source/target columns, and normalized CHECK expressions. Test SqlLedger against a schema created by the actual PostgreSQL migrations.
6. **Fix catalog verification.** In `--check`, recompute metrics in memory, compare them to registry metrics, render Markdown in memory, and byte-compare with `MODULE_CATALOG.md`. Add negative fixtures for metric drift, catalog text drift, and invalid semantic status evidence where feasible.
7. **Reconcile all front doors in one bounded documentation tranche.** Update `IMPLEMENTATION_STATUS.json`, `CVF_CONTROL_MAPPING.md`, the roadmap's final next step, session memory, and `ARCHITECTURE.md` implementation marker so the required reading chain gives one consistent state.
8. **Keep the frontend claim bounded until P2-C.** Add real API-backed events/tasks/approval flows and frontend tests before claiming the boundary is proven by a product workflow.
9. **Add failure-injection tests.** At minimum: audit sink failure, correction insert failure, lost evidence after reconnect, frozen-parent mutation, fabricated approval identities, and migration-vs-table Task insert shape.

## One-line conclusion

> The repo has advanced from an honest blueprint to a promising early implementation, but its current governance headlines are not yet true end to end: freeze, evidence, approval trust, transactional audit, PostgreSQL schema parity, and catalog freshness must be repaired before "CVF enforced" or "dual-backend golden vertical" is a defensible claim.
