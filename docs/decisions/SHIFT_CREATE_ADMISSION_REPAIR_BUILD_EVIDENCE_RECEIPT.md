# Shift Create Admission Repair — BUILD Evidence Receipt

Tranche: `SHIFT-CREATE-ADMISSION-REPAIR-2026-07-29`
Role: `IMPLEMENTATION_WORKER` → `REPAIR_WORKER` (SCR-BUILD-REV-F1/F2/F3) (Claude)
Status: `READY_FOR_INDEPENDENT_SHIFT_CREATE_ADMISSION_BUILD_RE_REVIEW`

## 0. Repair round: SCR-BUILD-REV-F1/F2/F3 (all three closed without waiver)

Independent review returned three findings against the first BUILD; all
three were repaired strictly within the authorized repair paths named by the
reviewer (`test_shift_create_postgres_live.py`,
`run_shift_create_live_governance_evidence.py`,
`test_shift_create_live_evidence_runner.py`,
`test_shift_create_admission.py`, both evidence receipts). No 20th path was
touched.

- **`SCR-BUILD-REV-F1 POSTGRES_AUTHENTICATED_PATH_NOT_PROVEN`** — the
  PostgreSQL tests called `ShiftService.create` directly with a constructed
  `Principal`, never exercising the required JWT/FastAPI admission path.
  Fixed: `test_shift_create_postgres_live.py` now routes every case through
  a real `TestClient(app)` with `get_ledger` overridden to the live
  PostgreSQL-backed `SqlLedger` and a minted operator JWT bearer header —
  identical to how production traffic reaches the route. The
  injected-audit-failure cases now assert the unhandled exception
  propagates through the real route (`pytest.raises`), not a bare service
  call, and post-rollback usability is proven with a second real HTTP
  create.
- **`SCR-BUILD-REV-F2 LIVE_ADMISSION_PROOF_UNDERASSERTS_R5_R6`** — the live
  runner's `build_admitted_create_genuine` only checked one audit's
  `action`, so a tampered actor or an unexpected second shift both still
  returned `ok=True`. Fixed: it now asserts `list_shifts()` has **exactly
  one** entry matching the created id, and every audit field
  (`actor_id`, `actor_role`, `action`, `record_type`, `record_id`,
  `control_chain`, `before_state`, `after_state`) matches an exact expected
  dict, not just `action`. Two new adversarial non-live tests
  (`test_admitted_construction_rejects_a_tampered_actor_audit`,
  `test_admitted_construction_rejects_an_unexpected_second_shift`) reproduce
  the reviewer's exact probes via monkeypatched `InMemoryLedger` methods and
  confirm the repaired function now returns `ok=False` for both — proving
  the fix closes the gap, not just narrating it.
- **`SCR-BUILD-REV-F3 BACKEND_EVIDENCE_MATRIX_INCOMPLETE`** — SPEC R7's
  refusal-zero-write HTTP proof only ran against `InMemoryLedger`, and no
  test explicitly compared InMemory's returned record against its persisted
  record (SQLite already had this). Fixed:
  `test_shift_create_admission.py` gained a `sql_client` fixture and two new
  SQLite-backed HTTP refusal tests
  (`test_anonymous_create_rejected_with_no_writes_sql`,
  `test_viewer_role_rejected_with_no_writes_sql`), plus a new
  `test_returned_record_equals_persisted_record` parametrized across both
  `in_memory` and `sql` backends.

Fresh re-verification after all three repairs: focused command **94
passed** (was 88), full non-live suite **724 passed, 69 skipped** (was 718),
disposable PostgreSQL 16 evidence **59 passed** with all 4 shift-create
tests now going through the real authenticated route, and exactly one real
provider call **PASS** after the strengthened admission proof. See §14 for
the full fresh re-run record.

## 1. G6 preconditions (independently re-verified fresh, not trusted from the
handoff)

- `HEAD == origin/main == 87415c930804f14227ad889ab5d5fa94013c404e` (C2
  pre-BUILD continuity), worktree clean before BUILD started.
- CVF core HEAD == manifest `cvfCoreCommit` == `origin/main` ==
  `27137db4d9aa2aea931ddd2507185d5c24943080`, core worktree clean.
- Workspace doctor: `PASS WITH NOTE (24 passed, 1 warning(s))` — sole warning
  is the bounded legacy catalog-kit note, unchanged before and after BUILD.
- Session-state, repository validator, catalog check and file-size guard all
  PASS before BUILD started.
- Full non-live baseline before BUILD: **678 passed, 65 skipped**.
- Docker daemon responsive (Docker Desktop 4.83.0, engine 29.6.2);
  `postgres:16`/`postgres:16-alpine` images present; zero `cvf-pg-live-*`
  containers or volumes before BUILD.
- Provider credential presence confirmed as a boolean only
  (`ALIBABA_API_KEY`/`DASHSCOPE_API_KEY` candidate present: `True`) — value
  never read, printed, or logged.

## 2. Exact changed set (19 authorized paths, no 20th)

Production code (3):

1. `packages/cvf-runtime/src/cvf_runtime/permission.py` — added exactly
   `"shift.create": "operator"`.
2. `apps/workspace-api/src/workspace_api/application/shift_service.py` —
   added `ShiftService.create`.
3. `apps/workspace-api/src/workspace_api/api/shifts/router.py` — added
   `Depends(get_principal)` and delegated to `ShiftService.create`.

Non-live and contract tests (5):

4. `tests/cvf/test_shift_create_admission.py` — NEW.
5. `tests/integration/test_shift_create_sqlite.py` — NEW.
6. `tests/unit/test_shift_create_openapi_contract.py` — NEW.
7. `tests/unit/test_p2b_openapi_contract.py` — extended the chained golden
   proof one more link.
8. `tests/unit/test_p2c_read_openapi_contract.py` — historical reduction now
   also strips the new `POST /shifts` security delta before re-hashing.

PostgreSQL 16 evidence (3):

9. `tests/integration/test_shift_create_postgres_live.py` — NEW.
10. `tests/integration/test_postgres_live_runner.py` — pinned tuple extended
    to four modules.
11. `scripts/run_postgres_live_roundtrip.py` — line-neutral target-list
    extension (see §5).

Real-provider evidence (3):

12. `tests/integration/test_shift_create_live_evidence_runner.py` — NEW.
13. `scripts/run_shift_create_live_governance_evidence.py` — NEW.
14. `scripts/_shift_create_live_evidence_support.py` — NEW.

Receipts and bounded truth surfaces (5):

15. `docs/decisions/SHIFT_CREATE_ADMISSION_REPAIR_BUILD_EVIDENCE_RECEIPT.md`
    — NEW (this file).
16. `docs/decisions/SHIFT_CREATE_ADMISSION_REPAIR_LIVE_EVIDENCE_RECEIPT.md`
    — NEW, generated and sanitized (§8).
17. `docs/cvf/CVF_CONTROL_MAPPING.md` — added the `shift.create` row; closed
    the prior `P2C-DESIGN-F1 UNGOVERNED_SHIFT_CREATE` cross-reference.
18. `docs/catalog/MODULE_REGISTRY.json` — regenerated via
    `generate_catalog.py --write`.
19. `docs/catalog/MODULE_CATALOG.md` — regenerated via
    `generate_catalog.py --write`.

`git status --porcelain` shows exactly these 19 paths (10 modified + 9 new).
No 20th path.

## 3. Required implementation order followed

1. Failing permission/API/service admission tests added first
   (`test_shift_create_admission.py`), confirmed failing against
   pre-implementation source (12 failed / 5 passed).
2. Failing InMemory/SQLite atomicity/reconnect tests added
   (`test_shift_create_sqlite.py`), confirmed failing (2 failed).
3. OpenAPI delta and golden-chain negative tests added
   (`test_shift_create_openapi_contract.py`, plus extending
   `test_p2b_openapi_contract.py`/`test_p2c_read_openapi_contract.py`),
   confirmed failing against the pre-tranche document (9 failed / 8 passed).
4. Permission map, `ShiftService.create` and router changes implemented;
   all of the above turned green (with two real test-authoring defects
   found and fixed along the way — see §4).
5. Provider-runner non-live tests added before the runner/support code
   existed (`test_shift_create_live_evidence_runner.py` imports modules that
   did not yet exist), then `_shift_create_live_evidence_support.py` and
   `run_shift_create_live_governance_evidence.py` were added — all 16 tests
   passed on first run against the new modules.
6. PostgreSQL live test added
   (`test_shift_create_postgres_live.py`) plus the line-neutral
   `LIVE_SUITE_TARGETS` extension.
7. Focused suite, then full non-live suite, run and passing.
8. Disposable PostgreSQL 16 evidence run with verified exact cleanup.
9. Real provider call run only after all refusal/admission checks passed.
10. Sanitized receipts generated from actual results.
11. Control mapping updated; catalog regenerated via `--write` then verified
    via `--check`.
12. All final gates re-run; this receipt records the result.

## 4. Two test-authoring defects found and fixed during BUILD (not production
defects)

While writing `test_shift_create_admission.py` against the real backends
(not assumed shapes), two of my own initial test assumptions were wrong and
were corrected before the suite was accepted as green:

- **Audit row shape.** `SqlLedger.audit_entries_for` returns dict rows with
  `target_type`/`target_id` and `actor_role`/`control_chain`/`before_state`/
  `after_state` nested under `metadata`, not flat top-level keys as
  `InMemoryLedger`'s real `AuditRecord` objects have. Fixed by adding a
  `_audit_fields` normalizer (mirrors the existing `e.action`/`e["action"]`
  split pattern already used in `test_atomic_mutation_audit.py`), not by
  changing production code.
- **Invalid-window 422.** Constructing the canonical `Shift` model with
  `ends_at <= starts_at` raises `pydantic.ValidationError`, which FastAPI
  does not map to HTTP 422 on its own (only its own
  `RequestValidationError` has a default handler) — an unhandled
  `ValidationError` would have surfaced as HTTP 500. The router now also
  catches `pydantic.ValidationError` and maps it to 422, alongside the
  existing `CvfDenied` translation; this is a translation of the service's
  own construction error, not a second entry point, and the catch happens
  only after `require_action` inside the service, so refusal ordering
  (401/403 before any validation) is unaffected.

Both fixes are visible in the diff of `shift_service.py`'s test-adjacent
assertions and `router.py`'s exception handling respectively — neither
changed the service's transaction/audit shape from what SPEC R5/R6 require.

## 5. PostgreSQL runner line-neutral edit (SPEC §3.3)

`scripts/run_postgres_live_roundtrip.py` was exactly 300 lines before this
tranche. The two-line comment above `LIVE_SUITE_TARGETS` was condensed to
one line and the new `tests/integration/test_shift_create_postgres_live.py`
target was appended — net zero line change, still exactly **300 lines**
after the edit. No statement compression, multi-statement line, or
behavior change beyond the tuple extension.

## 6. Focused verification

```text
python -m pytest -q tests/cvf/test_shift_create_admission.py tests/integration/test_shift_create_sqlite.py tests/unit/test_shift_create_openapi_contract.py tests/unit/test_p2b_openapi_contract.py tests/unit/test_p2c_read_openapi_contract.py tests/integration/test_postgres_live_runner.py tests/integration/test_shift_create_live_evidence_runner.py tests/cvf/test_shift_close_governance.py tests/cvf/test_shift_close_freeze_interaction.py tests/cvf/test_atomic_mutation_audit.py
-> 88 passed
```

## 7. Full non-live suite and repository gates

```text
python -m pytest -q
-> 718 passed, 69 skipped, 0 failed

python scripts/testing/validate_repository.py
-> repository validation passed (catalog + session state + file-size checks)

python scripts/check_session_state.py       -> SESSION STATE: PASS
python scripts/generate_catalog.py --check  -> CATALOG VERIFY: PASS (20 modules)
python scripts/check_file_size.py           -> FILE SIZE GUARD: PASS
git diff --check                            -> exit 0 (clean)
powershell -ExecutionPolicy Bypass -File scripts/initialize_cvf_clone.ps1
-> RESULT: PASS WITH NOTE (24 passed, 1 warning(s)); FRESH_CLONE_CONTINUITY_PASS
```

Baseline before BUILD was 678 passed/65 skipped; the delta (+40 passed, +4
skipped) is exactly the new shift-create admission/SQLite/OpenAPI/runner
tests plus the 4 new PostgreSQL live tests, which skip without
`LIVE_POSTGRES_DATABASE_URL` in the non-live run.

Every touched/new Python file is at or below the 300-line hard limit (see
§2; `run_postgres_live_roundtrip.py` is exactly 300, the authorized
line-neutral edit).

Message and Integration Edge boundary: `git status --porcelain` and
`git diff --stat` against `apps/workspace-api/src/workspace_api/api/messages`,
message models, and Integration Edge/channel paths show **zero diff**.
Anonymous `POST /messages` remains open and is not claimed as fixed by this
tranche.

## 8. OpenAPI contract delta (SPEC R9)

- Pre-tranche full-document SHA (`PRE_SHIFT_CREATE_OPENAPI_SHA`):
  `a982980a1aa8af5585a1bf95006d66c73108dc2c33829c804650fe1b9828c67c`
  (reproduced independently before any edit, matching the existing
  `GOLDEN_OPENAPI_SHA` recorded at SPEC-review time).
- Post-tranche full-document SHA (`GOLDEN_OPENAPI_SHA`):
  `94f56893835b046736efe6697e4d2786ff1716702bfda2a4e9e712a131fee0b3`.
- Mechanical delta proof (`test_shift_create_openapi_contract.py`,
  `test_p2b_openapi_contract.py`): stripping exactly the new `security` key
  from `POST /shifts` and re-hashing the remainder reproduces
  `PRE_SHIFT_CREATE_OPENAPI_SHA` exactly. Negative-protection tests confirm
  an undisclosed path addition or an unrelated mutation-route removal both
  fail this proof.
- `POST /shifts` query parameters (`name`, `starts_at`, `ends_at`), response
  schema (`#/components/schemas/Shift`) and status contract (`200`/`422`)
  are unchanged — verified structurally, not by inspection alone.
- `test_p2c_read_openapi_contract.py`'s historical reduction now also strips
  the new `POST /shifts` security key before re-hashing against its own
  unchanged `PRE_P2C_READ_OPENAPI_SHA`; this required no change to that
  constant.

## 9. Disposable PostgreSQL 16 evidence (SPEC R8)

`python scripts/run_postgres_live_roundtrip.py --json`:

- `docker_server_version`: 29.6.2; `image`: `postgres:16-alpine`.
- Migrations: first attempt **21 applied / 0 skipped**; reapply
  **17 applied / 4 skipped** (idempotent).
- Live suite (`test_sql_ledger_postgres_live.py` + `test_incident_postgres_live.py`
  + `test_handover_postgres_live.py` + `test_shift_create_postgres_live.py`):
  **59 passed**, 0 failed — the 4 shift-create tests
  (`test_create_persists_shift_and_actor_bound_audit`,
  `test_create_and_audit_survive_reconnect`,
  `test_injected_audit_failure_rolls_back_creation`,
  `test_connection_remains_usable_after_rollback_case`) all passed **through
  the real `TestClient(app)` HTTP/JWT route** after the `SCR-BUILD-REV-F1`
  repair (§0/§14), not a bare service call.
- Cleanup: `container_absent_after_cleanup: true`;
  `anonymous_volumes_still_present: []`. Independently confirmed with
  `docker ps -a`/`docker volume ls` before and after — no `cvf-pg-live-*`
  container and no captured volume ID present at any point after cleanup.

## 10. Real provider-bound shift-create governance evidence (SPEC R12-R14)

`python scripts/run_shift_create_live_governance_evidence.py`:

- 4 refusal cases (anonymous, malformed token, viewer role, invalid window)
  — all **PASS**, **0 provider calls each**, through the real HTTP/JWT route
  chain; each case independently verified zero persisted shifts.
- Genuine operator-JWT create (minted token, real HTTP request) — **PASS**,
  persisting **exactly one** shift and **one exactly-field-matched**
  actor-bound `shift.create` audit (actor_id/actor_role/action/record_type/
  record_id/control_chain/before_state/after_state all asserted, after the
  `SCR-BUILD-REV-F2` repair — §0/§14).
- Real provider call: **exactly 1**, outcome **PASS**, HTTP 200, model
  `qwen3.7-max`, endpoint (host only)
  `https://ws-remplsp27g5oicq1.ap-southeast-1.maas.aliyuncs.com`.
- Sanitized receipt:
  `docs/decisions/SHIFT_CREATE_ADMISSION_REPAIR_LIVE_EVIDENCE_RECEIPT.md` —
  grepped for `Bearer `, `sk-`, `eyJ`, `api_key`, `Authorization:` and full
  endpoint path/query — none found.
- The production `POST /shifts` endpoint does not import or invoke any
  provider-facing code from either evidence script; the provider call is
  external release evidence only.

## 11. Secret and resource discipline

No provider API key, JWT signing secret, bearer token, PostgreSQL password,
or full database URL was printed, read back, or committed at any point.
Both live-evidence scripts reset a fresh `ProviderCallCounter` per
invocation. The PostgreSQL runner removed only the exact container it
created and the anonymous volume IDs captured from that container.

## 12. Statement

No stage, commit, or push occurred at any point during this BUILD or the
subsequent repair round. No self-approval, FREEZE, or next-tranche (message
admission) work was performed. Exactly the 19 authorized paths were touched
or created across both rounds; no 20th path. Message/Integration Edge,
migrations, `packages/operations-domain/**`, the Ledger Protocol/backends,
auth/JWT, frontend, dependency manifests and lockfiles, the file-size
guard/debt surfaces, P2-C evidence runners, and `.cvf/**`/CVF core/
authorization artifacts were not touched.

`READY_FOR_INDEPENDENT_SHIFT_CREATE_ADMISSION_BUILD_RE_REVIEW`

## 13. Claim boundary (SPEC R17)

Only the following is claimed:

> `POST /shifts` requires a verified JWT, enforces `shift.create` permission,
> and atomically persists the shift with an actor-bound audit record.

Not claimed: that all mutation routes are authenticated (anonymous
`POST /messages` remains open and is the sole next security tranche); that
message sender identity is verified; assignment/tenant/`data_scope`
authorization; frontend mutation support; PostgreSQL production readiness;
or P2-C/Phase 2 completion.

## 14. Repair-round fresh re-verification (replaces §6-§10's counts where noted)

```text
python -m pytest -q tests/cvf/test_shift_create_admission.py tests/integration/test_shift_create_sqlite.py tests/unit/test_shift_create_openapi_contract.py tests/unit/test_p2b_openapi_contract.py tests/unit/test_p2c_read_openapi_contract.py tests/integration/test_postgres_live_runner.py tests/integration/test_shift_create_live_evidence_runner.py tests/cvf/test_shift_close_governance.py tests/cvf/test_shift_close_freeze_interaction.py tests/cvf/test_atomic_mutation_audit.py tests/integration/test_shift_create_postgres_live.py
-> 94 passed, 4 skipped (was 88 passed before repair; +6 from F2's two
   adversarial probes and F3's two SQLite HTTP refusal tests plus one
   returned-vs-persisted parametrized test x2 backends, minus the prior
   count's non-inclusion of the postgres-live module which now correctly
   skips without a live URL)

python -m pytest -q
-> 724 passed, 69 skipped, 0 failed (was 718 passed/69 skipped before repair)

python scripts/check_file_size.py           -> FILE SIZE GUARD: PASS
python scripts/testing/validate_repository.py
-> repository validation passed (catalog + session state + file-size checks)
python scripts/check_session_state.py       -> SESSION STATE: PASS
git diff --check                            -> exit 0 (clean)
```

Disposable PostgreSQL 16 evidence (`python scripts/run_postgres_live_roundtrip.py --json`),
fresh rerun after the F1 repair:

- Migrations: first **21 applied / 0 skipped**; reapply **17 applied / 4
  skipped** (idempotent) — unchanged from the pre-repair run.
- Live suite: **59 passed**, 0 failed. All 4 shift-create tests now execute
  through a real `TestClient(app)` with a minted operator JWT and
  `get_ledger` overridden to the live PostgreSQL-backed `SqlLedger` — the
  authenticated API/service path SPEC R8 requires, not a bare
  `ShiftService(ledger).create(..., Principal(...))` call.
- Cleanup: `container_absent_after_cleanup: true`,
  `anonymous_volumes_still_present: []`; independently confirmed with
  `docker ps -a`/`docker volume ls` before and after this rerun — zero
  `cvf-pg-live-*` residue at any point.

Real provider-bound governance evidence
(`python scripts/run_shift_create_live_governance_evidence.py`), fresh
rerun after the F2 repair:

- Same 4 refusal cases, all **PASS**, **0 provider calls each**.
- Genuine admitted create — **PASS**, now verified against the strengthened
  assertion set: exactly one persisted shift matching the created id, and
  every audit field (actor_id, actor_role, action, record_type, record_id,
  control_chain, before_state, after_state) exactly matching the expected
  values — not just `action`.
- Real provider call: **exactly 1**, outcome **PASS**, HTTP 200, model
  `qwen3.7-max`, same host as before repair.
- Receipt regenerated fresh at
  `docs/decisions/SHIFT_CREATE_ADMISSION_REPAIR_LIVE_EVIDENCE_RECEIPT.md`;
  grepped for `Bearer`, `sk-`, `eyJ`, `api_key`, `Authorization:` and full
  endpoint path/query — none found.

Workspace doctor, rerun fresh:

```text
powershell -ExecutionPolicy Bypass -File scripts/initialize_cvf_clone.ps1
-> RESULT: PASS WITH NOTE (24 passed, 1 warning(s)); FRESH_CLONE_CONTINUITY_PASS
```

Exact changed-set after the repair round remains the same **19** paths as
before repair (`git status --porcelain` count unchanged at 19) — no 20th
path was introduced by any of the three fixes. Zero staged paths; no
stage/commit/push/self-approval/FREEZE at any point in the repair round.

`READY_FOR_INDEPENDENT_SHIFT_CREATE_ADMISSION_BUILD_RE_REVIEW`
