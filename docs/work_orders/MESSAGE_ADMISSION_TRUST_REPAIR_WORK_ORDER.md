# Work Order — Message Admission and Trust Repair

- ID: `MESSAGE-ADMISSION-TRUST-REPAIR-WO-001`
- Tranche: `MESSAGE-ADMISSION-TRUST-REPAIR-2026-07-30`
- Risk: R2
- Intake:
  `docs/decisions/INTAKE_2026-07-30_MESSAGE_ADMISSION_TRUST_REPAIR.md`
- Design:
  `docs/decisions/ADR_2026-07-30_MESSAGE_ADMISSION_TRUST_REPAIR.md`
- Specification:
  `docs/specs/MESSAGE_ADMISSION_TRUST_REPAIR_SPEC.md`
- SPEC review:
  `docs/decisions/MESSAGE_ADMISSION_TRUST_REPAIR_SPEC_REVIEW.md`
- Status: `REVIEW_PASS — C1/C2 AND G6 REQUIRED; BUILD PROHIBITED`

## 1. Roles and gates

- Codex: current `ORCHESTRATOR`, `WORK_ORDER_AUTHOR`, authorization
  `REVIEWER`, `COMMIT_STEWARD`.
- Future `IMPLEMENTATION_WORKER`/`REPAIR_WORKER`: unassigned; must be
  independent from the authorization reviewer.
- Post-BUILD `REVIEWER`: must be independent from the implementation worker.

No worker may begin until:

1. this Work Order has authorization `REVIEW_PASS`;
2. C1 authorization artifacts are committed and pushed;
3. C2 pre-BUILD continuity is separately committed and pushed;
4. G6 passes from clean pushed C2 state.

The user request for SPEC and Work Order does not itself authorize BUILD.

## 2. Exact C3 BUILD ceiling

Exactly these 29 paths are authorized.

### Production code

1. `packages/cvf-runtime/src/cvf_runtime/permission.py`
2. `apps/workspace-api/src/workspace_api/application/message_service.py` — NEW
3. `apps/workspace-api/src/workspace_api/api/messages/router.py`
4. `apps/workspace-api/src/workspace_api/infrastructure/repository.py`
5. `apps/workspace-api/src/workspace_api/application/customer_request_service.py`
6. `packages/operations-ledger/src/operations_ledger/ledger.py`
7. `packages/operations-ledger/src/operations_ledger/sql_ledger.py`
8. `packages/operations-ledger/src/operations_ledger/_message_store.py` — NEW
9. `packages/operations-ledger/src/operations_ledger/_rows.py`
10. `packages/operations-ledger/src/operations_ledger/tables.py`

### Non-live and contract tests

11. `tests/cvf/test_message_admission.py` — NEW
12. `tests/integration/test_message_sqlite.py` — NEW
13. `tests/unit/test_message_openapi_contract.py` — NEW
14. `tests/unit/test_p2b_openapi_contract.py`
15. `tests/unit/test_p2c_read_openapi_contract.py`
16. `tests/integration/test_schema_parity.py`
17. `tests/cvf/test_customer_request_repair.py`
18. `tests/cvf/test_ledger_protocol.py`

### PostgreSQL 16 evidence

19. `tests/integration/test_message_postgres_live.py` — NEW
20. `scripts/run_postgres_live_roundtrip.py`
21. `tests/integration/test_postgres_live_runner.py`

### Real-provider evidence

22. `scripts/run_message_admission_live_governance_evidence.py` — NEW
23. `scripts/_message_admission_live_evidence_support.py` — NEW
24. `tests/integration/test_message_admission_live_evidence_runner.py` — NEW

### Receipts and truth surfaces

25. `docs/decisions/MESSAGE_ADMISSION_TRUST_REPAIR_BUILD_EVIDENCE_RECEIPT.md`
    — NEW
26. `docs/decisions/MESSAGE_ADMISSION_TRUST_REPAIR_LIVE_EVIDENCE_RECEIPT.md`
    — NEW, generated and sanitized
27. `docs/cvf/CVF_CONTROL_MAPPING.md`
28. `docs/catalog/MODULE_REGISTRY.json`
29. `docs/catalog/MODULE_CATALOG.md`

There is no conditional 30th path. A needed extra path triggers
`BLOCKED_WORK_ORDER_CEILING` and requires a committed
DESIGN→SPEC→WORK_ORDER amendment before implementation resumes.

## 3. Exact edit boundaries

### 3.1 Application and permission

- add only `message.create: operator`; no role/JWT/other-action change;
- new `MessageService` implements SPEC R2-R7 only;
- router keeps one JSON body and canonical Message response, adds JWT, and
  delegates only to the service;
- no domain Message or migration edit.

### 3.2 Ledger

- Protocol adds `get_message`;
- InMemory gains duplicate/evidence checks and deep-copy add/get semantics;
- `_message_store.py` is the bounded SqlLedger mixin for add/get/exists and
  controlled parity;
- `sql_ledger.py` only wires that mixin and removes the NotImplemented stub;
- `_rows.py` adds exact message row/read mapping;
- `tables.py` changes only stale comments unless a test proves an existing
  mapping defect; table columns are frozen;
- customer-request service changes only its now-stale persistence comment.

No generic transaction, shift, event, task, incident, handover, approval or
audit behavior may change.

### 3.3 Tests and OpenAPI

- tests are separated by API/service, SQLite/alias, OpenAPI, schema/reference,
  PostgreSQL and provider concerns;
- `test_customer_request_repair.py` replaces direct SQL fixture insertion with
  public `SqlLedger.add_message`;
- `test_schema_parity.py` adds messages to `MAPPED` and the verified explicit
  UUID-PK set;
- historical P2-B/P2-C OpenAPI tests accept only SPEC R13's message delta;
- no golden regeneration may absorb an unrelated operation/schema change.

### 3.4 PostgreSQL runner

The runner adds exactly the message live target. Because it is already 300
lines, the edit must be line-neutral by removing an adjacent obsolete
target-list comment/blank line, not by compressing logic or changing the debt
registry. Its non-live test pins all five exact target paths.

### 3.5 Provider runner

The new runner/support split must:

- run all seven refusals as independent zero-call observations;
- admit one genuine JWT/FastAPI message;
- verify exact persisted message/audit before one provider call;
- count observed calls rather than infer from status;
- sanitize every success/failure/exception path;
- use existing provider configuration conventions without changing them.

No production endpoint imports provider code.

### 3.6 Receipts/catalog

Receipts record exact commands/counts, backend facts, sanitized provider
outcome, changed-set and nonclaims. `CVF_CONTROL_MAPPING.md` may add only the
internal message-create row/qualification. Catalog files are updated only by
`python scripts/generate_catalog.py --write`.

No roadmap, `IMPLEMENTATION_STATUS.json` or continuity closure edit is part of
C3.

## 4. Protected boundary

Zero-line diff is mandatory for:

- `database/migrations/**`;
- `packages/operations-domain/**`;
- `packages/workspace-contracts/**`;
- `apps/integration-edge/**`;
- `packages/channel-sdk/**`, `packages/channel-adapters/**`;
- `packages/identity-mapping/**`, `packages/conversation-routing/**`;
- auth/token/dependency implementation;
- frontend and worker code;
- `.cvf/**`, CI/workflows, dependency manifests/locks;
- file-size debt registry and all prior receipts.

No production/managed database, external webhook or channel credential may be
used.

## 5. C1, C2 and G6

### C1

C1 contains exactly the four new authorization artifacts plus the same four
continuity surfaces:

- SPEC, SPEC review, Work Order, authorization review;
- active handoff, canonical active state, compatibility mirror, session
  memory.

It contains zero BUILD/source/test/permission/schema/migration/evidence
receipt changes.

### C2

After C1 is pushed, C2 contains exactly:

- `SESSION/handoffs/AGENT_HANDOFF_2026-07-30_MESSAGE_ADMISSION_TRUST_REPAIR.md`;
- `SESSION/ACTIVE_SESSION_STATE.json`;
- `CVF_SESSION/ACTIVE_SESSION_STATE.json`;
- `SESSION/SESSION_MEMORY.md`.

C2 records the implementation/reviewer identities, C1 acknowledgment, exact
29-path ceiling and G6 result. It contains no implementation.

### G6

Immediately before BUILD:

1. `HEAD == origin/main` at pushed C2 and worktree is clean;
2. core HEAD/origin/manifest equal
   `27137db4d9aa2aea931ddd2507185d5c24943080`, core clean;
3. canonical/mirror/handoff agree;
4. Docker daemon, `postgres:16-alpine`, psycopg and provider prerequisites are
   checked truthfully without exposing secrets;
5. `python -m pytest -q` baseline passes with exact counts;
6. repository, catalog, session, file-size, JSON, diff and doctor gates pass;
7. no owned test container/volume residue exists.

Any failure blocks BUILD and is recorded without editing implementation.

## 6. Required implementation order

1. permission and MessageService tests;
2. service/router;
3. Protocol and InMemory parity;
4. SQL mapper/store and SQLite tests;
5. schema/customer-reference/OpenAPI chain;
6. PostgreSQL target and live proof;
7. provider runner tests, then live evidence;
8. control mapping, generated catalog and receipts;
9. full gates and worker return.

Provider execution cannot precede all non-live and PostgreSQL admission proof.

## 7. Mandatory evidence commands

Focused non-live:

```powershell
python -m pytest -q tests/cvf/test_message_admission.py tests/integration/test_message_sqlite.py tests/unit/test_message_openapi_contract.py tests/unit/test_p2b_openapi_contract.py tests/unit/test_p2c_read_openapi_contract.py tests/integration/test_schema_parity.py tests/cvf/test_customer_request_repair.py tests/cvf/test_ledger_protocol.py tests/integration/test_postgres_live_runner.py tests/integration/test_message_admission_live_evidence_runner.py tests/integration/test_freeze.py
```

Full and gates:

```powershell
python -m pytest -q
python scripts/testing/validate_repository.py
python scripts/generate_catalog.py --check
python scripts/check_session_state.py
python scripts/check_file_size.py
git diff --check
```

Live PostgreSQL:

```powershell
python scripts/run_postgres_live_roundtrip.py --json
```

Live provider:

```powershell
python scripts/run_message_admission_live_governance_evidence.py --json
```

Also required:

- JSON parse for changed JSON;
- exact 29-path inventory and protected-boundary zero diff;
- secret scan of diff, receipts and captured output;
- doctor `PASS WITH NOTE (24/1)` with no warning beyond legacy catalog;
- authorization-parent rollback rehearsal in an isolated temporary worktree,
  exact cleanup and baseline restoration.

## 8. Secret/resource discipline

Never print or persist API keys, JWT secrets/tokens, passwords, full database
URLs, auth headers, raw provider responses or external payloads. Read
credentials only at the moment the authorized live runner requires them.

Docker actions are limited to the official uniquely named owned container and
its captured anonymous volumes. No broad prune/remove command is allowed.

## 9. Stop conditions

Stop on:

- any path outside the 29-path ceiling;
- any protected-boundary diff;
- authentication/permission/provenance bypass;
- caller sender/source persisted as authority;
- partial message/audit state;
- cross-backend mismatch or silent field loss;
- raw SQL exception at the API boundary;
- unrelated OpenAPI delta;
- file > hard limit or debt-registry change;
- failing/skipped required test;
- missing/ambiguous live prerequisite;
- refusal call delta other than zero or admitted delta other than one;
- secret-bearing output/receipt;
- Docker residue;
- any attempt to claim external ingestion or production readiness.

## 10. Return, review and commit ownership

The worker returns:

- declared role and G6/C1/C2 facts;
- exact changed paths and per-path rationale;
- test/live commands with exact counts;
- sanitized receipts and call accounting;
- protected-boundary/secret/resource results;
- failures, repairs and remaining nonclaims;
- `READY_FOR_INDEPENDENT_MESSAGE_ADMISSION_BUILD_REVIEW`.

The worker does not stage, commit, push, review or FREEZE.

An independent reviewer compares source, output, SPEC AC-01..AC-23, exact
inventory and receipts. Findings return to the bounded repair worker. Only
`REVIEW_PASS` lets the `COMMIT_STEWARD` stage exactly all 29 authorized paths
and push C3.

C1 authorization, C2 pre-BUILD continuity, C3 BUILD and C4 closure are
separate commits.

## 11. C4 and rollback

Only after pushed C3 and independent post-push review may C4 update
`IMPLEMENTATION_STATUS.json`, continuity and any roadmap wording that source
truth requires. C4 must repeat SPEC R19 verbatim or more narrowly and keep
external Integration Edge work as the next separate governed tranche.

Rollback rehearsal is non-destructive in a temporary worktree. Operational
rollback, if ever needed, is a normal `git revert` of C3 followed by the same
gates; history is never rewritten.

## 12. Disposition

`REVIEW_PASS` after authorization review. This authorizes C1/C2 stewardship
and G6 only. BUILD/provider/Docker/PostgreSQL execution remains prohibited
until pushed C1/C2 and passing G6.
