# P2-C Operations Console Read Slice — C3a BUILD Evidence Receipt

Tranche: `P2C-OPERATIONS-CONSOLE-READ-SLICE-2026-07-28`
Role: REPAIR_WORKER (Claude), repairing independent-review findings
`P2C-C3A-REV-F10`, `F20`-`F25` against the amended 30-path C3a ceiling
(`docs/work_orders/P2C_OPERATIONS_CONSOLE_READ_SLICE_WORK_ORDER_AMENDMENT_3.md`)
Status: `READY_FOR_INDEPENDENT_P2C_READ_API_BUILD_RE_REVIEW`

## 0. F25 — documentation-only repair round (`CONTROL_MAPPING_EVIDENCE_PATH_DRIFT`)

This round repairs exactly one finding raised after the F20-F24 round closed:
`docs/cvf/CVF_CONTROL_MAPPING.md`'s P2C read-surface row still attributed the
PostgreSQL 500/501 matrix evidence to `tests/integration/test_postgres_live_runner.py`,
which was the correct file *before* Amendment 3 moved the matrix out of it.
After that move, the row was never updated to name the actual evidence
module, so the mapping pointed a reviewer at a file (`test_postgres_live_runner.py`)
that no longer contains the matrix it claimed to prove.

**Fix (exactly two authorized paths, no other path touched):**

- `docs/cvf/CVF_CONTROL_MAPPING.md`: the P2C read-surface row's Test column
  now cites `tests/integration/test_p2c_read_postgres_limit_live.py` (PostgreSQL
  16 live 500/501 qua real API/SqlLedger, Amendment 3) in place of
  `tests/integration/test_postgres_live_runner.py` for that matrix. No other
  text in the row changed — the bounded/non-load-bearing provider status
  (`KHÔNG load-bearing ... mandatory live-provider proof (SPEC R16/AC-16)
  chưa PASS`) is untouched, and F10 is not claimed closed.
- `docs/decisions/P2C_READ_API_BUILD_EVIDENCE_RECEIPT.md` (this file): this
  §0 records the finding and the exact correction.

No code, test, schema, dependency, or any other path was modified this
round. `git diff --stat` for this round touches only the two files named
above.

## 1. Pre-repair rehydration (verified fresh)

- `HEAD == origin/main == ffd73ff8c9d4d7e0385f1f15b9b7ee49091d0a16` (Amendment
  3 authorization commit, unchanged throughout this repair — no
  stage/commit/push occurred at any point).
- CVF core pin/HEAD `27137db4d9aa2aea931ddd2507185d5c24943080`, hidden core
  clean.
- Docker daemon responded (`docker version` → Server `29.6.2`) before both
  PostgreSQL live runs.
- The prior repair round's 28-path changed set was preserved exactly as
  left; this round adds exactly the one Amendment-3-authorized path.

## 2. Amendment 3 file-size repair (F20's blocker)

`tests/integration/test_postgres_live_runner.py` was at 315 lines (F20's
`BLOCKED_AMENDMENT_2_CEILING_INFEASIBLE` disposition). Per Amendment 3, the
entire P2C R27 live matrix and its two dedicated helpers (`_live_seed`,
`_live_path_params`) were **moved**, not duplicated, into the newly
authorized `tests/integration/test_p2c_read_postgres_limit_live.py`. No
line was minified or compressed to fit either file:

- `tests/integration/test_postgres_live_runner.py`: **224 lines** (restored
  to its original runner-test-only scope; the module docstring was updated
  to note the historical move, and the now-unused `datetime`/`timedelta`/
  `timezone`/`os` imports and `LIVE_URL_ENV` constant were removed since
  nothing in the file uses them anymore).
- `tests/integration/test_p2c_read_postgres_limit_live.py`: **120 lines**
  (new file; contains the exact matrix logic moved verbatim, plus its own
  module docstring explaining its scope and the move).

`scripts/run_postgres_live_roundtrip.py` (300 lines) was **not touched** —
confirmed via `git diff --stat` showing zero changes. Its `LIVE_SUITE_TARGETS`
tuple and `test_live_suite_targets_pin_all_three_coherent_modules` (asserting
the original three standard targets) are unchanged and still pass.

## 3. Findings disposition (F10, F20-F24)

| Finding | Disposition |
|---|---|
| F20 `POSTGRES_FULL_MATRIX_NOT_IMPLEMENTED` | **Fixed and run live.** The moved `test_live_read_surface_ceiling` in the new module covers all 5 surfaces (shifts, events, tasks, customer_requests, incidents) × both 500 (admit, HTTP 200) and 501 (refuse, HTTP 422) = 10 parametrized cases, each through `TestClient` → `app.dependency_overrides[get_ledger]` → a live-PostgreSQL-backed `SqlLedger` — the real authenticated API/dependency chain, not a bare row-count check. Run against a fresh disposable PostgreSQL 16 container using the runner's own `ensure_image`/`start_container`/`wait_ready`/`apply_migrations_twice`/`container_volumes`/`remove_container` primitives: **10 passed, 0 failed** (§6). |
| F21 `OPEN_WORK_GROUP_GUARDS_NOT_INDEPENDENTLY_PROVEN` | Unchanged from the prior round — still closed. `tests/integration/test_p2c_read_api.py::test_open_work_group_ceiling` (InMemory+SQLite) and the moved live matrix's open-work cases both fill only the named group to `count`, holding the other two at exactly 1 record, proving true per-group independence rather than a combined-total check. |
| F22 `OPENAPI_POLICY_STILL_NONDETERMINISTIC` | Unchanged from the prior round — still closed. `pyproject.toml` pins exact `fastapi==0.118.3`, `starlette==0.48.0`, `pydantic==2.10.6`, `pydantic-core==2.27.2`. Re-verified this round: a fourth brand-new venv (`uv pip compile pyproject.toml --extra dev` on fresh CPython 3.13.12, zero cache reuse) resolved to exactly these four versions again. |
| F23 `REQUIRED_FIELD_WEAKENED_OUTSIDE_AUTHORITY` | Unchanged from the prior round — still closed. `task.schema.json`'s `required` list still includes `owner_id` (nullable value, `["string", "null"]` type). Re-verified this round: `test_open_work_schema_rejects_task_missing_owner_id_key` and `test_open_work_schema_accepts_task_with_null_owner_id` both still pass. |
| F24 `EVIDENCE_AND_MAPPING_OVERCLAIM` | This receipt states F20 as genuinely fixed only because §6 below shows a real live run with a real result, not an aspirational implementation. `docs/cvf/CVF_CONTROL_MAPPING.md` is **not modified** this round — it still states the bounded/non-load-bearing truth from the prior round (F19), and that remains accurate: the live-provider gate (F10) is still `BLOCKED`, so the P2C read surfaces cannot yet be described as load-bearing. No test docstring in the new module claims a completed run beyond what §6 documents. |
| F10 `LIVE_PROVIDER_EVIDENCE_BLOCKED` | Re-verified, not fixed by mocking. `scripts/run_p2c_read_live_governance_evidence.py` re-run in this environment: refusal gate 4/4 PASS (0 provider calls each), genuine admitted-JWT read construction PASS, real provider call **not attempted** — neither `ALIBABA_API_KEY` nor `DASHSCOPE_API_KEY` is present (script exits `2`, `READY_FOR_LIVE_EVIDENCE: no provider key`). This is now the **sole** remaining blocker — every other Amendment 2/3 finding is closed and every other gate is green. Per the provider stop rule, this repair does not mock, fabricate, or self-declare `REVIEW_PASS`. See `docs/decisions/P2C_READ_LIVE_EVIDENCE_RECEIPT.md`. |

## 4. Exact changed set (subset of the amended 30-path ceiling)

Prior checkpoint (end of the Amendment 2 repair round): **18 modified + 10
new = 28 paths**.

This round adds exactly **1 new path** (the Amendment 3 authorization) and
edits within **1 already-touched path** (no net new path count from that
edit):

Modified (18, same set as the prior round — `test_postgres_live_runner.py`
was already in the modified set and remains modified, now with the matrix
removed instead of added):

```
apps/workspace-api/README.md
apps/workspace-api/src/workspace_api/api/events/router.py
apps/workspace-api/src/workspace_api/api/shifts/router.py
apps/workspace-api/src/workspace_api/infrastructure/repository.py
docs/catalog/MODULE_CATALOG.md
docs/catalog/MODULE_REGISTRY.json
docs/cvf/CVF_CONTROL_MAPPING.md
packages/operations-ledger/src/operations_ledger/ledger.py
packages/operations-ledger/src/operations_ledger/sql_ledger.py
packages/workspace-contracts/README.md
packages/workspace-contracts/customers/customer-request.schema.json
packages/workspace-contracts/tasks/task.schema.json
pyproject.toml
tests/contract/test_contract_files.py
tests/cvf/test_ledger_protocol.py
tests/integration/test_postgres_live_runner.py
tests/integration/test_sql_ledger_postgres_live.py
tests/unit/test_p2b_openapi_contract.py
```

New (11, includes this receipt, the live receipt, and the Amendment-3 module):

```
packages/operations-ledger/src/operations_ledger/_event_queries.py
packages/operations-ledger/src/operations_ledger/_shift_queries.py
packages/workspace-contracts/open-work/open-work.schema.json
scripts/run_p2c_read_live_governance_evidence.py
tests/integration/test_p2c_read_api.py
tests/integration/test_p2c_read_ledger_parity.py
tests/integration/test_p2c_read_live_evidence_runner.py
tests/integration/test_p2c_read_postgres_limit_live.py
tests/unit/test_p2c_read_openapi_contract.py
docs/decisions/P2C_READ_API_BUILD_EVIDENCE_RECEIPT.md (this file)
docs/decisions/P2C_READ_LIVE_EVIDENCE_RECEIPT.md
```

**Total: 18 modified + 11 new = 29 paths**, a subset of the amended 30-path
ceiling. `scripts/run_postgres_live_roundtrip.py` remains on the authorized
list and needed zero changes (confirmed via `git diff --stat`, zero output).
No 31st path was touched.

## 5. File line counts (every touched/created Python file, hard limit 300)

```
packages/operations-ledger/src/operations_ledger/ledger.py             143
packages/operations-ledger/src/operations_ledger/sql_ledger.py         280
packages/operations-ledger/src/operations_ledger/_event_queries.py      52
packages/operations-ledger/src/operations_ledger/_shift_queries.py      56
apps/workspace-api/.../infrastructure/repository.py                    285
apps/workspace-api/.../api/events/router.py                             98
apps/workspace-api/.../api/shifts/router.py                            133
tests/cvf/test_ledger_protocol.py                                       46
tests/contract/test_contract_files.py                                  226
tests/integration/test_p2c_read_ledger_parity.py                       154
tests/integration/test_p2c_read_api.py                                 299
tests/integration/test_sql_ledger_postgres_live.py                     298
tests/integration/test_postgres_live_runner.py                         224
tests/integration/test_p2c_read_postgres_limit_live.py                 120
tests/unit/test_p2c_read_openapi_contract.py                           223
tests/unit/test_p2b_openapi_contract.py                                299
tests/integration/test_p2c_read_live_evidence_runner.py                190
scripts/run_postgres_live_roundtrip.py                                 300 (unchanged)
scripts/run_p2c_read_live_governance_evidence.py                       299
```

All at or under the 300-line hard limit. No file-size exception was used —
`test_postgres_live_runner.py` returned to 300-compliance purely by moving
its P2C-specific content to a newly authorized module.

## 6. Focused and live test results (this round)

Fresh CPython 3.13.12, fresh venv, dependencies resolved and installed
strictly from `pyproject.toml` (`uv pip compile --extra dev`, zero cache
reuse). Collection: **743 tests, zero collection errors**.

| Suite | Result |
|---|---|
| `tests/integration/test_p2c_read_api.py` | 29 passed (InMemory+SQLite full matrix, F21 independent-group) |
| `tests/contract/test_contract_files.py` | 14 passed (F23 required+nullable) |
| `tests/integration/test_postgres_live_runner.py` | 14 passed (non-live runner tests, unaffected by the move) |
| `tests/integration/test_p2c_read_postgres_limit_live.py` (non-live collection) | 10 skipped without `LIVE_POSTGRES_DATABASE_URL` |
| `tests/unit/test_p2b_openapi_contract.py` + `tests/unit/test_p2c_read_openapi_contract.py` | 12 passed (F22 exact pins + negative-protection) |

Full non-live suite: `python -m pytest -q` → **678 passed, 65 skipped, 0
failed, 1 warning** (pre-existing bcrypt key-length notice, unrelated).

### PostgreSQL 16 — standard live suite (unmodified `LIVE_SUITE_TARGETS`)

`python scripts/run_postgres_live_roundtrip.py --json`:

- `docker_server_version`: 29.6.2; `image`: `postgres:16-alpine`.
- Migrations: first attempt **21 applied / 0 skipped**; reapply
  **17 applied / 4 skipped**.
- Live suite (`test_sql_ledger_postgres_live.py`,
  `test_incident_postgres_live.py`, `test_handover_postgres_live.py`):
  **55 passed**, 0 failed.
- Cleanup: `container_absent_after_cleanup: true`;
  `anonymous_volumes_still_present: []`.

### PostgreSQL 16 — new F20 full matrix (separate disposable container)

Invoked via the same runner primitives (`ensure_image`, `start_container`,
`wait_ready`, `apply_migrations_twice`, `container_volumes`,
`remove_container`) against
`tests/integration/test_p2c_read_postgres_limit_live.py`:

- Container: `cvf-pg-live-de9d061195ce` (ephemeral, one-off name per run);
  image `postgres:16-alpine`, image id
  `sha256:20edbde7749f822887a1a022ad526fde0a47d6b2be9a8364433605cf65099416`.
- Migrations: first attempt **21 applied / 0 skipped**; reapply
  **17 applied / 4 skipped**.
- Matrix result: **10 passed, 0 failed** —
  `test_live_read_surface_ceiling` for
  `{shifts, events, tasks, customer_requests, incidents}` ×
  `{500→200, 501→422}`, every case run independently (each open-work group
  case seeds only that group to the target count, holding the other two at
  1 record — F21 discipline extended to the live matrix).
- Cleanup: `container_absent_after_cleanup: true`;
  `anonymous_volumes_still_present: []`.
- Independently confirmed with `docker ps -a --filter name=cvf-pg-live` and
  `docker volume ls --filter name=cvf` before and after both live runs (this
  section and the standard suite above) — zero residue at every check.

## 7. Repository gates (post-repair)

- `python scripts/check_file_size.py` → **PASS** (was `FAIL` at the end of
  the prior round; now green after the Amendment 3 move).
- `python scripts/generate_catalog.py --check` → PASS (no catalog-affecting
  source change this round; catalog paths from the prior round remain
  accurate — a new test file does not currently change catalog totals since
  it is a straight move of existing lines, not new logic. Re-verified with
  `--write` producing no diff.).
- `python scripts/check_session_state.py` → PASS.
- `python scripts/testing/validate_repository.py` → PASS (catalog + session
  + file-size).
- `git diff --check` → clean (only pre-existing LF/CRLF warnings, exit 0).
- `git diff --stat scripts/run_postgres_live_roundtrip.py` → empty (confirmed
  untouched).
- JSON validation across all touched/new JSON → all parse.
- Secret scan across every changed/new file → zero matches outside declared
  test-only sentinels.
- Zero staged files throughout.

## 8. Provider live-governance evidence

See `docs/decisions/P2C_READ_LIVE_EVIDENCE_RECEIPT.md`. Refusal gate (4/4
zero-call cases) and genuine admitted-read construction both PASS. The real
provider call remains `BLOCKED` — no `ALIBABA_API_KEY`/`DASHSCOPE_API_KEY`
present, confirmed by directly re-running the evidence script this round
(exit code `2`). Not mocked, not skipped silently, not claimed as PASS.
Provider call count: **0** (as required for every refusal case; the
exactly-one-call admitted path was never reached because the credential
gate blocks before it).

## 9. Statement

No stage, commit, or push occurred at any point during this repair. The
exact changed set (§4) is 29 paths, a subset of the amended 30-path C3a
ceiling; no 31st path was touched. `scripts/run_postgres_live_roundtrip.py`,
its `LIVE_SUITE_TARGETS`, and the test asserting the three standard targets
are all confirmed unchanged. F20-F23 are closed without waiver and F20 is
now backed by an actual live 10/10 PASS run, not an implementation claim.
F24's overclaim discipline is honored throughout this receipt and
`docs/cvf/CVF_CONTROL_MAPPING.md` (left at its prior-round bounded
statement). F10 is the sole open finding: honestly re-verified as
`BLOCKED_LIVE_PROVIDER_CREDENTIAL` — this repair did not, and could not,
manufacture a credential that does not exist in this environment. Final
state:

`BLOCKED_LIVE_PROVIDER_CREDENTIAL`

## 11. F10 live-provider closure — independent reviewer run

The prior blocked statements in §0, §3, §8, §9 and §10 are retained as
historical evidence of the credential-absent attempts. They are superseded by
this final run.

Codex independently loaded the operator-provided credential from the local
CSV export into process memory without printing it, persisted only the
credential binding in the Windows User environment, and ran:

`python scripts/run_p2c_read_live_governance_evidence.py`

Fresh result:

- four anonymous/malformed JWT refusal cases: PASS, zero provider calls each;
- valid JWT reads of shifts, events and open work: PASS;
- selected model: `qwen3.7-max`;
- provider endpoint recorded by host only;
- real provider response: HTTP 200;
- expected response token: `CVF_P2C_READ_EVIDENCE_OK`;
- admitted-path provider calls: exactly 1;
- receipt: `docs/decisions/P2C_READ_LIVE_EVIDENCE_RECEIPT.md`;
- receipt top-level outcome: `Overall outcome: PASS`;
- secret scan of the generated receipt: PASS.

F10 is closed without mock or waiver. F20-F25 remain closed. The BUILD is now
ready for independent C3a re-review; this receipt does not self-approve it.

This is not `READY_FOR_INDEPENDENT_P2C_READ_API_BUILD_RE_REVIEW` — per the
Work Order's explicit stop rule, that checkpoint requires the provider gate
to pass, and it does not in this environment. Every other mandatory gate
(focused, full regression, InMemory/SQLite/PostgreSQL full matrix, exact
dependency pins, file-size, catalog, session-state, repository validator,
`git diff --check`, secret scan, exact changed-set/ceiling audit) is green.

## 10. F25 round — updated statement

The F25 round above (§0) corrected only the stale evidence-file citation in
`docs/cvf/CVF_CONTROL_MAPPING.md`. No implementation, test, schema, or
dependency path changed; §1-§9 above (the F20-F24 evidence and gate results)
remain the accurate technical record and were not re-run from scratch this
round because nothing they measure changed — this round only touched
documentation. The changed-set for this round is exactly two files:
`docs/cvf/CVF_CONTROL_MAPPING.md` and this receipt. Zero staged, no
stage/commit/push, no self-approval, no FREEZE, no C3b.

Provider credential status is unchanged: still absent in this environment.
F10 remains open. Final state is unchanged from §9:

`BLOCKED_LIVE_PROVIDER_CREDENTIAL`
