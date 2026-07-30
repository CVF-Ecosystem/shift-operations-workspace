# Work Order — Shift Create Admission Repair

- ID: `SHIFT-CREATE-ADMISSION-REPAIR-WO-001`
- Tranche: `SHIFT-CREATE-ADMISSION-REPAIR-2026-07-29`
- Risk: `R2`
- Intake:
  `docs/decisions/INTAKE_2026-07-29_SHIFT_CREATE_ADMISSION_REPAIR.md`
- Design:
  `docs/decisions/ADR_2026-07-29_SHIFT_CREATE_ADMISSION_REPAIR.md`
- Specification:
  `docs/specs/SHIFT_CREATE_ADMISSION_REPAIR_SPEC.md`
- SPEC review:
  `docs/decisions/SHIFT_CREATE_ADMISSION_REPAIR_SPEC_REVIEW.md`
- Status:
  `REVIEW_PASS — C1/C2 AND G6 REQUIRED; BUILD PROHIBITED`

## 1. Roles and authority

- Codex: `ORCHESTRATOR`, `WORK_ORDER_AUTHOR`, independent `REVIEWER`, later
  `COMMIT_STEWARD` and `CLOSER`.
- Claude: future `IMPLEMENTATION_WORKER`, or `REPAIR_WORKER` only for findings
  accepted and bounded by Codex.

Codex does not perform BUILD. Claude does not review, self-approve, stage,
commit, push or FREEZE. Because this is R2 security/governance work, Claude
may begin BUILD only after:

1. this Work Order receives an independent authorization `REVIEW_PASS`;
2. the C1 authorization commit is pushed;
3. a separate C2 pre-BUILD continuity acknowledgment is pushed; and
4. G6 passes immediately before implementation.

An operator instruction to continue does not waive these gates.

## 2. Exact C3 BUILD changed-set ceiling

Exactly these 19 paths are authorized:

### Production code

1. `packages/cvf-runtime/src/cvf_runtime/permission.py`
2. `apps/workspace-api/src/workspace_api/application/shift_service.py`
3. `apps/workspace-api/src/workspace_api/api/shifts/router.py`

### Non-live and contract tests

4. `tests/cvf/test_shift_create_admission.py` — NEW
5. `tests/integration/test_shift_create_sqlite.py` — NEW
6. `tests/unit/test_shift_create_openapi_contract.py` — NEW
7. `tests/unit/test_p2b_openapi_contract.py`
8. `tests/unit/test_p2c_read_openapi_contract.py`

### PostgreSQL 16 evidence

9. `tests/integration/test_shift_create_postgres_live.py` — NEW
10. `tests/integration/test_postgres_live_runner.py`
11. `scripts/run_postgres_live_roundtrip.py`

### Real-provider evidence

12. `tests/integration/test_shift_create_live_evidence_runner.py` — NEW
13. `scripts/run_shift_create_live_governance_evidence.py` — NEW
14. `scripts/_shift_create_live_evidence_support.py` — NEW

### Receipts and bounded truth surfaces

15. `docs/decisions/SHIFT_CREATE_ADMISSION_REPAIR_BUILD_EVIDENCE_RECEIPT.md`
    — NEW
16. `docs/decisions/SHIFT_CREATE_ADMISSION_REPAIR_LIVE_EVIDENCE_RECEIPT.md`
    — NEW, generated and sanitized
17. `docs/cvf/CVF_CONTROL_MAPPING.md`
18. `docs/catalog/MODULE_REGISTRY.json`
19. `docs/catalog/MODULE_CATALOG.md`

There is no conditional 20th path. If implementation needs any other path,
the worker stops at `BLOCKED_WORK_ORDER_CEILING` and names the exact reason.
Only a committed DESIGN → SPEC → WORK_ORDER amendment may expand the ceiling.

## 3. Exact edit boundaries

### 3.1 Production code

- `permission.py` adds exactly `"shift.create": "operator"` without changing
  role rank or unknown-action fail-closed behavior.
- `shift_service.py` adds only the SPEC R3/R5/R6 create path. It must use one
  public `Ledger.transaction()` unit for `create_shift` plus actor-bound audit.
- the shifts router adds verified JWT admission and delegates only to
  `ShiftService.create`; its three required query parameters and canonical
  `Shift` response remain unchanged.

No Ledger Protocol, backend implementation, canonical domain model, migration,
auth/JWT or dependency change is authorized.

### 3.2 OpenAPI golden chain

- the new shift-create OpenAPI test proves the exact bearer-security-only
  delta on `POST /shifts`, including unchanged query, response and status
  shape;
- `test_p2b_openapi_contract.py` may change only to extend the chained golden
  proof and current full-document digest for this exact delta;
- `test_p2c_read_openapi_contract.py` may change only so its historical P2-C
  reduction removes the later authorized `POST /shifts` security delta before
  re-hashing its original baseline;
- both historical tests must retain negative protection against unrelated
  path, method, schema, parameter, response or security drift.

A blind hash refresh without a mechanical delta proof is a STOP condition.

### 3.3 PostgreSQL runner

`test_shift_create_postgres_live.py` owns the coherent PostgreSQL create,
actor-bound audit, reconnect, injected-audit rollback and post-rollback
usability cases.

The existing runner and its non-live test may change only to append that exact
module to `LIVE_SUITE_TARGETS`. Because
`scripts/run_postgres_live_roundtrip.py` is already 300 physical lines, the
target may be added only by a line-neutral edit: at most one adjacent blank or
obsolete target-list comment line may be removed. No statement compression,
multi-statement line, behavior change or file-size exception is authorized.

### 3.4 Provider runner split

The pre-existing P2-C provider runner is closed and read-only. The new
shift-create evidence is split exactly as follows:

- `run_shift_create_live_governance_evidence.py` owns orchestration, the real
  FastAPI/JWT refusal/admission chain and CLI entry point;
- `_shift_create_live_evidence_support.py` owns provider HTTP, per-run call
  accounting, safe endpoint description, sanitization and receipt rendering;
- its non-live test owns adversarial sentinel, stdout/stderr/receipt, call
  count and failure-path probes.

Each Python file must remain at or below 300 physical lines. Production
`POST /shifts` never imports or invokes provider code.

### 3.5 Documentation and catalog

The two receipts record actual results only. `CVF_CONTROL_MAPPING.md` may add
only the bounded shift-create admission truth and must preserve the anonymous
message finding. Catalog files change only through:

```text
python scripts/generate_catalog.py --write
```

No roadmap, implementation-status or continuity closure claim is part of C3.

## 4. Protected boundary

The following are read-only during BUILD:

- `apps/workspace-api/src/workspace_api/api/messages/**`;
- message models, message ledger/repository code, Integration Edge and channel
  adapters;
- every migration and all table metadata;
- `packages/operations-domain/**`;
- Ledger Protocol, InMemoryLedger, SqlLedger and all ledger helper modules;
- auth/JWT/login/user provisioning and role hierarchy;
- shift list, events, open-work, close and freeze semantics;
- frontend, offline queue, realtime, reporting, assignment, tenant and
  `data_scope` surfaces;
- P2-C source, evidence runners and receipts;
- dependency manifests and lockfiles;
- file-size guard/debt/exception surfaces;
- `.cvf/**`, pinned CVF core and all authorization/continuity artifacts.

Review must record zero-line diff for message and Integration Edge paths and
must preserve anonymous `POST /messages` as the sole next security tranche.

## 5. G6 pre-BUILD gate

Immediately before Claude declares `IMPLEMENTATION_WORKER`, Codex must verify
and record:

1. `HEAD == origin/main` at the pushed C2 commit;
2. project tracked tree, staged area and untracked set are empty;
3. core HEAD, manifest pin and `origin/main` all equal
   `27137db4d9aa2aea931ddd2507185d5c24943080`, with a clean core tree;
4. workspace doctor has zero FAIL and only the bounded legacy catalog note;
5. session, catalog, repository and file-size gates pass;
6. the full non-live baseline passes with its exact pass/skip counts;
7. Docker daemon responds, PostgreSQL 16 image resolves, and no foreign
   `cvf-pg-live-*` resource is present;
8. an operator-authorized provider credential is available from local secret
   storage/environment, checked as a boolean only; its value is never printed,
   copied into chat or committed;
9. Claude rehydrates the pushed Work Order/authorization/continuity and
   declares `IMPLEMENTATION_WORKER`.

Any mismatch stops before BUILD with a truthful, specific blocker.

## 6. Required implementation order

1. Add failing permission/API/service admission tests.
2. Add failing InMemory/SQLite atomicity and reconnect tests.
3. Add the exact OpenAPI delta and golden-chain negative tests.
4. Implement permission, service and router changes.
5. Add provider-runner non-live tests before its runner/support code.
6. Add PostgreSQL live test and the bounded line-neutral target extension.
7. Run focused non-live tests, then the full non-live suite.
8. Run disposable PostgreSQL 16 evidence and verify exact cleanup.
9. Only after all refusal and persisted admitted-route checks pass, run
   exactly one real provider call.
10. Generate sanitized receipts from the actual results.
11. Update the bounded control mapping and regenerate the catalog.
12. Run all final gates and stop for independent review.

## 7. Mandatory evidence matrix

| Requirement | Required proof |
|---|---|
| R1-R4 | real FastAPI/JWT 401/403/422/admitted role matrix; exact permission-map and router-source checks |
| R5-R6 | public service/Ledger transaction tests; exact audit fields; exactly one shift and one audit |
| R7 | InMemory and SQLite success, refusal, injected rollback, persisted equality and SQLite reconnect |
| R8 | owned disposable PostgreSQL 16 API/service create, audit, reconnect, rollback, usable connection and exact cleanup |
| R9-R11 | structural OpenAPI delta, chained golden hashes, lifecycle regression and protected message boundary |
| R12-R14 | observed per-case zero calls, admitted persistence before exactly one real call, adversarial sanitization |
| R15-R16 | line counts and separated test/evidence modules |
| R17 | receipts and final wording stay inside the bounded claim |

Focused non-live command:

```text
python -m pytest -q tests/cvf/test_shift_create_admission.py tests/integration/test_shift_create_sqlite.py tests/unit/test_shift_create_openapi_contract.py tests/unit/test_p2b_openapi_contract.py tests/unit/test_p2c_read_openapi_contract.py tests/integration/test_postgres_live_runner.py tests/integration/test_shift_create_live_evidence_runner.py tests/cvf/test_shift_close_governance.py tests/cvf/test_shift_close_freeze_interaction.py tests/cvf/test_atomic_mutation_audit.py
```

Full and repository gates:

```text
python -m pytest -q
python scripts/testing/validate_repository.py
python scripts/check_session_state.py
python scripts/generate_catalog.py --check
python scripts/check_file_size.py
git diff --check
powershell -ExecutionPolicy Bypass -File scripts/initialize_cvf_clone.ps1
```

Live gates:

```text
python scripts/run_postgres_live_roundtrip.py
python scripts/run_shift_create_live_governance_evidence.py
```

The PostgreSQL and provider gates are independently mandatory. A missing or
failed provider credential does not erase a PostgreSQL result; Docker failure
does not become a provider failure. Neither condition permits REVIEW_PASS.

## 8. Secret and resource discipline

- Never print/read back the provider key, JWT secret, bearer token,
  PostgreSQL password or full DSN.
- Runner summaries, exceptions, stdout/stderr and receipts must remove exact
  secret sentinels, bearer/JWT shapes, Authorization headers and URL
  userinfo/query/fragment.
- The provider runner must reset and observe its call counter per invocation.
- Missing, malformed, expired, quota-exhausted or rejected credentials produce
  `BLOCKED_LIVE_PROVIDER_CREDENTIAL` or a truthful failure, never PASS.
- The PostgreSQL runner may remove only the exact container it created and
  the anonymous volume IDs captured from that container.
- Cleanup proof must show both the owned container and captured volumes absent.

## 9. Worker return contract

Claude returns:

- G6 facts and declared role;
- exact modified/new/staged inventory;
- focused and full test commands with exact pass/skip/fail counts;
- OpenAPI pre/post digest and structural-delta result;
- PostgreSQL migration first/reapply counts, live test count and cleanup IDs;
- provider family/model/safe host/HTTP outcome/expected token and observed
  refusal/success call deltas, fully sanitized;
- line count of every touched Python file;
- repository/session/catalog/file-size/diff/doctor results;
- protected message/Integration Edge zero diff;
- statement that no stage, commit, push, self-approval, FREEZE or message
  tranche work occurred.

Stop exactly at:

`READY_FOR_INDEPENDENT_SHIFT_CREATE_ADMISSION_BUILD_REVIEW`

## 10. Stop conditions

Stop immediately on:

- a required 20th path or ambiguity in an authorized path's edit boundary;
- auth/permission bypass, direct router-ledger mutation or non-atomic audit;
- a refusal that writes state or changes the provider counter;
- provider call count other than exactly zero per refusal and exactly one
  after admitted persistence proof;
- provider, JWT or PostgreSQL secret-bearing output;
- unrelated OpenAPI, query, response, lifecycle or role-rank drift;
- any message/Integration Edge diff;
- migration, schema, domain-model, ledger-backend or frontend change;
- failed/skipped/weakened/deleted governance proof;
- file-size, full regression, catalog, session, repository, diff or doctor
  failure;
- Docker ownership uncertainty, cleanup residue or a production defect;
- worker stage/commit/push/self-approval or attempt to begin the next tranche.

The worker preserves evidence and returns the exact blocker. No unreviewed
self-repair outside the ceiling is allowed.

## 11. Review, repair and commit ownership

Codex independently compares source, tests, generated OpenAPI, both live runs,
receipts and the exact 19-path inventory against SPEC R1-R17/AC-01..AC-21.

- On findings, Codex names stable finding IDs and exact repair paths. Claude
  transitions to `REPAIR_WORKER` only inside that accepted boundary.
- On `REVIEW_PASS`, Codex transitions to `COMMIT_STEWARD`, verifies that the
  passing C3 inventory is exactly the 19 authorized paths, stages that exact
  set, commits and pushes C3.
- Claude never owns a git mutation.

C1 authorization, C2 pre-BUILD continuity, C3 BUILD and C4 closure are
separate commits. No squash, amend, force-push or batching with another
tranche is allowed.

## 12. C4 closure and rollback

Only after pushed C3 and an independent post-push re-review may Codex, as
`CLOSER / SESSION_SYNC_STEWARD`, update the six closure surfaces:

1. `SESSION/ACTIVE_SESSION_STATE.json`
2. `CVF_SESSION/ACTIVE_SESSION_STATE.json`
3. `SESSION/SESSION_MEMORY.md`
4. the active shift-create handoff
5. `IMPLEMENTATION_STATUS.json`
6. `docs/implementation/EXECUTION_ROADMAP.md`

C4 may state only SPEC R17's bounded claim. It must make anonymous message
admission the sole next governed security tranche.

Rollback rehearsal uses a detached temporary worktree at the C3 parent,
re-runs the predecessor focused baseline there, and removes only that exact
temporary worktree after verifying its resolved path is outside both the
project and CVF-core directories. Operational rollback is a normal `git
revert` of C3 from a clean tree followed by the same gates; history is never
rewritten. No database down migration is claimed because this tranche adds no
migration.

## 13. Current authorization disposition

`REVIEW_PASS` after `SCR-WO-AUTH-F1 NON_PORTABLE_FOCUSED_COMMAND` was repaired
without waiver. Review record:
`docs/decisions/SHIFT_CREATE_ADMISSION_REPAIR_WORK_ORDER_AUTHORIZATION_REVIEW.md`.

This disposition authorizes C1/C2 commit stewardship and G6 only. It grants no
BUILD or provider-call authority until the pushed C1/C2 and G6 conditions in
§1/§5 are all satisfied.
