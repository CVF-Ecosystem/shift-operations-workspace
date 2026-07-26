# PostgreSQL Live Round-Trip — Evidence Receipt

Tranche: `P1-POSTGRESQL-LIVE-ROUNDTRIP-2026-07-26` (Amendment 1 repair round)
Generated: 2026-07-26T08:56:41Z (UTC)
Produced by: `scripts/run_postgres_live_roundtrip.py` (real disposable
PostgreSQL 16 container, no mock/SQLite substitution)

## Overall outcome: **LIVE PASS (bounded) — PostgreSQL component only**

The originally stopped BUILD found a real production defect. Independent
review reproduced it and returned `REVIEW_CHANGES_REQUIRED` with findings
`PG-REV-F1` through `PG-REV-F5`. Amendment 1 authorized a repair within
exactly eight paths. All five findings are repaired below, and a fresh
disposable PostgreSQL 16 run — reproduced twice — now passes completely:
**36 passed, 0 failed, 0 skipped**. A subsequent independent review of the
runner script found one further finding, `PG-REV-F6` (exception-handling
robustness in `run_once()`'s orchestration try/except), repaired within the
same two already-authorized paths — no ninth path introduced (sections 2
and 3). Codex then independently reproduced the live result end-to-end
(section 12). This receipt supersedes the prior stopped-run receipt's
disposition; the original finding is kept in section 2 as history, not
deleted. Phase 1 is **not** closed by this receipt alone (see section 13
claim boundary).

## 1. Git / continuity state (G6R, this repair round)

- Project HEAD == `origin/main` == `11c3ac5aee5e8127ec9f3fa3b53e817b831b9ad3` (post-C2b, verified before repair).
- Zero tracked modifications and nothing staged at G6R time.
- Untracked at G6R: the preserved assessment plus exactly the three
  stopped-BUILD artifacts (`scripts/run_postgres_live_roundtrip.py`,
  `tests/integration/test_sql_ledger_postgres_live.py`, this receipt).
- Hidden CVF core HEAD == `origin/main` == manifest pin `27137db4d9aa2aea931ddd2507185d5c24943080`; core clean.
- Assessment file: untracked, byte-identical, SHA-256 `168ea2c7a67a31bae50c9e4dbe78c2273a692f3a82a1074585e1bdb89b70fde2` (unchanged throughout both the stopped BUILD and this repair).
- Doctor before and after repair: `PASS WITH NOTE (24 passed, 1 warning)` — same bounded legacy catalog-kit note; no new warning/failure.
- Docker daemon responsive at G6R; zero `cvf-pg-live-*` containers and zero residue volumes confirmed before repair began.

## 2. History — original stopped-BUILD finding (kept, not deleted)

The first live run against a genuine PostgreSQL 16 database (schema from
migrations only) failed with `psycopg.errors.DatatypeMismatch: column
"status" is of type shift_status but expression is of type character
varying`. Root cause: `tables.py` mapped every migration-native-`ENUM`
column as a generic SQLAlchemy `String`; invisible on SQLite, but PostgreSQL
under `psycopg` v3 refuses an explicit `VARCHAR` bind against a native enum
column. Original reproduction: migrations `17/0` then `14/3`; live suite
`26 passed, 7 failed` (all seven failures traced to this one root cause).
Independent review reproduced this exactly and returned
`REVIEW_CHANGES_REQUIRED` with:

- `PG-REV-F1 NATIVE_ENUM_BIND_FAILURE` — the defect above.
- `PG-REV-F2 FAILURE_OUTPUT_CREDENTIAL_LEAK` — a failed live-suite run's raw
  pytest traceback (containing the full generated database URL/password)
  was printed and stored in `live_suite_tail` unsanitized.
- `PG-REV-F3 CLEANUP_OWNERSHIP_BUG` — `main()`'s `finally` block called
  `remove_container()` unconditionally, so a name collision that correctly
  refused to run `docker run` would still force-delete whatever
  pre-existing container happened to hold that name.
- `PG-REV-F4 TYPE_PARITY_TEST_INCOMPLETE` — no test compared the actual
  native-enum type name/value list, only generic type-family/CHECK
  presence.
- `PG-REV-F5 RECEIPT_DRIFT` — the stopped-run receipt's own changed-path
  count contradicted the paths it listed (claimed "2 of 5" while listing
  three), among other drift.

After Amendment 1's live PASS (sections 6-7), a further independent review
of the runner script found one more finding:

- `PG-REV-F6 UNSANITIZED_EXCEPTION_ESCAPE` — `run_once()`'s `try`/`except`
  clause caught only `LiveRoundTripError`, so an ordinary exception raised
  during orchestration or migration (e.g. a raw SQLAlchemy/driver error
  from `apply_migrations_twice`) would propagate past all sanitization and
  print Python's default unhandled traceback — potentially embedding the
  real database URL/password, since driver exceptions often repr the DSN —
  and skip the evidence-summary path entirely.

## 3. Repairs applied (Amendment 1, exactly eight authorized paths)

**PG-REV-F1** — `packages/operations-ledger/src/operations_ledger/tables.py`:
added `_enum_type(pg_name, *values)` returning portable `String()` with a
`.with_variant(postgresql.ENUM(*values, name=pg_name, create_type=False),
"postgresql")`. Applied to exactly the eight R13-named columns:
`shifts.status`, `operational_events.risk`/`state`, `messages.state`,
`tasks.risk`/`state`, `task_creation_intents.risk_class`,
`approval_receipts.risk_class`. `create_type=False` on every variant: the
migrations already ran `CREATE TYPE`, so SQLAlchemy must never attempt to
(re)create or drop it. `tasks.status`/`customer_requests.status`/
`users.role` are migration `text + CHECK`, not native enums, and were left
untouched.

**PG-REV-F2** — `scripts/run_postgres_live_roundtrip.py`: added
`sanitize_output(text, *, password, database_url)`, applied to the live
suite's stdout/stderr before printing and before storing
`live_suite_tail`, and to every `LiveRoundTripError` message. Unit-tested
in `tests/integration/test_postgres_live_runner.py` with an injected
sentinel password embedded in a fake traceback, proving it appears nowhere
in the sanitized output.

**PG-REV-F3** — same file: extracted `run_once()`, which now tracks a local
`created` flag set `True` only after `start_container()` returns normally.
Cleanup (`remove_container()`) runs only when `created` is `True`; a name
collision or failed `docker run` now sets `container_absent_after_cleanup
= True` with `cleanup_skipped_reason` recorded and never touches any
container. Also captures the container's anonymous-volume IDs before
removal, requires `docker rm -f -v` to report success, and verifies every
captured volume is independently absent afterward — any uncertainty is
reported as a failure. Unit-tested with monkeypatched Docker calls (no
real Docker needed) proving: (a) a simulated name collision never invokes
`docker run`, (b) a simulated failed creation never invokes
`remove_container`, (c) a successful creation does invoke cleanup and
verifies both container and volume absence, (d) a volume that survives
cleanup is reported as a failure.

**PG-REV-F4** — `tests/integration/test_schema_parity_types_and_checks.py`:
added `test_native_enum_type_name_and_value_parity` (parametrized over all
eight enum columns), which extracts the PostgreSQL variant from
`column.type._variant_mapping["postgresql"]` and asserts its `.name`,
`.create_type is False`, and exact ordered `.enums` match migration 001's
`CREATE TYPE ... AS ENUM` text — plus
`test_native_enum_parity_check_actually_catches_regressions`, a negative
proof (plain-text regression, wrong name, missing value, extra value) using
synthetic types only. `tests/integration/test_sql_ledger_postgres_live.py`
adds the live counterpart, `test_live_enum_type_name_and_value_parity`,
querying `pg_enum`/`pg_type` directly against the running database.

**PG-REV-F5** — this receipt: rewritten with a correct changed-path count
(section 8), the original stopped-run finding preserved as history
(section 2) rather than silently dropped, and the disposition replaced
with PASS only now that the repaired live suite has actually passed twice
(section 6), independently of any prior claim.

**PG-REV-F6** (post-Amendment-1 follow-up, no ninth path) —
`scripts/run_postgres_live_roundtrip.py`: broadened `run_once()`'s
`except LiveRoundTripError as exc:` to `except Exception:`, using
`traceback.format_exc()` — still passed through the existing
`sanitize_output()` before being stored in `summary["failure"]` — so no
exception type, not only `LiveRoundTripError`, can ever escape unsanitized;
`finally` (cleanup, ownership-gated by the `created` flag from PG-REV-F3)
is unaffected and still always runs. Two new regression tests added to
`tests/integration/test_postgres_live_runner.py`, both using a shared
sentinel password and full database URL: one drives a failing subprocess
result (`returncode=1`) with the sentinel embedded in fake stdout/stderr;
the other drives an ordinary raised `RuntimeError` (the actual regression
case that previously escaped uncaught) from a monkeypatched
`apply_migrations_twice`. Both assert cleanup still ran and that the
sentinel is absent from all five surfaces: the serialized JSON summary,
captured stdout, captured stderr, `live_suite_tail`, and `failure` text.

**File-size compliance**: `run_postgres_live_roundtrip.py`'s non-live unit
tests (command construction, redaction, naming, parsing) plus the new
sanitization/cleanup-ownership tests moved to a new file,
`tests/integration/test_postgres_live_runner.py`, so every touched Python
file stays at or under the 300-line hard limit: `tables.py` 278,
`test_schema_parity_types_and_checks.py` 296,
`run_postgres_live_roundtrip.py` 291 (includes the PG-REV-F6
exception-handling fix),
`test_sql_ledger_postgres_live.py` 267,
`test_postgres_live_runner.py` 207 (includes the 2 PG-REV-F6 regression
tests).

## 4. Tooling versions

- Docker client/server: `29.6.2` / `29.6.2`
- Docker Compose: `v5.3.1`
- `psycopg`: `3.3.4` (already installed from the stopped BUILD; no
  dependency-file edited)
- PostgreSQL image: `postgres:16-alpine`, image ID
  `sha256:57c72fd2a128e416c7fcc499958864df5301e940bca0a56f58fddf30ffc07777`

## 5. Disposable container facts (both repaired runs)

- Container names: `cvf-pg-live-c4cbaca01d72` (run 1),
  `cvf-pg-live-9ca562908af7` (run 2) — unique per run, never reused.
- Host bind: `127.0.0.1:<dynamic-port>:5432` — loopback only, OS-assigned
  port each run (e.g. `58666` on run 1).
- No `-v`/`--mount` was ever passed to `docker run` (unit-tested via
  `docker_run_cmd()`). The official `postgres` image's own Dockerfile
  `VOLUME /var/lib/postgresql/data` still produces an anonymous volume per
  container; both runs captured it (`container_volumes()`) before removal
  and independently confirmed it absent after (`docker volume inspect
  <id>` returned "no such volume" both times).
- No existing container, image, Compose project, named volume or database
  was created, reused, deleted or modified — `docker ps -a` / `docker
  volume ls` were empty before both runs and after both runs' cleanup.
- Credential: generated per run with `secrets.token_urlsafe(24)`, held only
  in-process, never printed. Full database URL never printed; only the
  `redact()`-masked form appears anywhere
  (`postgresql+psycopg://<redacted>@127.0.0.1:<port>/cvf_live_roundtrip`).

## 6. Migration apply / reapply (identical across both repaired runs)

| Attempt | Applied | Already present (tolerated duplicate_object) |
|---|---:|---:|
| First   | 17 | 0 |
| Reapply | 14 | 3 |

The 3 tolerated-on-reapply statements are the three `CREATE TYPE ... AS
ENUM` statements (`data_state`, `risk_class`, `shift_status`) — PostgreSQL
has no `IF NOT EXISTS` form for `CREATE TYPE`, exactly the case
`apply_migrations.py` (unmodified, read-only) already tolerates. No
migration file was touched.

## 7. Focused live suite result (both repaired runs, identical)

`python -m pytest -v tests/integration/test_sql_ledger_postgres_live.py`
with `LIVE_POSTGRES_DATABASE_URL` set by the runner:

**36 passed, 0 failed, 0 skipped** (run 1: 2.15s; run 2: 2.28s).

Covers: live identity (R6, PostgreSQL 16 + correct database name); live
schema table/enum existence (R7); live column/nullability/PK/FK parity for
all 10 `SqlLedger`-owned tables (R7); live CHECK-constraint and
approval-receipts UNIQUE-constraint presence; live enum type-name/exact
ordered-value parity for all 8 enum columns (R14/AC-24, new); full
round-trip across engine disposal and reconnect for
shift/event+evidence/task+transition/correction/audit/user/approval-receipt/
task-creation-intent (R8); five constraint-rejection probes, each followed
by a working connection on a fresh transaction (R9); and atomic
`transaction()` rollback verified from a fresh connection (R10).

## 8. Changed set — exactly all eight authorized paths, no ninth

1. `packages/operations-ledger/src/operations_ledger/tables.py` — modified (PG-REV-F1)
2. `tests/integration/test_schema_parity_types_and_checks.py` — modified (PG-REV-F4 static)
3. `scripts/run_postgres_live_roundtrip.py` — modified (PG-REV-F2/F3; PG-REV-F6 follow-up)
4. `tests/integration/test_sql_ledger_postgres_live.py` — modified (non-live tests moved out; PG-REV-F4 live added)
5. `tests/integration/test_postgres_live_runner.py` — NEW (non-live unit tests + PG-REV-F2/F3 tests; PG-REV-F6 follow-up regression tests)
6. `docs/decisions/POSTGRESQL_LIVE_ROUNDTRIP_EVIDENCE_RECEIPT.md` — this file, rewritten (PG-REV-F5)
7. `docs/catalog/MODULE_REGISTRY.json` — `operations-ledger` enforcement/tests/next_step bounded truth + generated metrics, only after live PASS
8. `docs/catalog/MODULE_CATALOG.md` — regenerated output only, via `python scripts/generate_catalog.py --write`

`git status --porcelain` shows exactly these eight paths plus the
untouched, byte-identical assessment file. Nothing staged.

## 9. Ordinary (non-live) suite, Phase 1 exit-gate subset, repository gates

- `python -m pytest -q` (no `LIVE_POSTGRES_DATABASE_URL` set): **427
  passed, 36 skipped, 1 warning** (425 plus the 2 new PG-REV-F6 regression
  tests) — the 36 skips are exactly the live tests, skipping cleanly with
  the documented reason (SPEC R1); zero failures/errors (AC-12).
- Existing shift-lifecycle + contract exit-gate subset
  (`test_lifecycle.py`, `test_vertical_end_to_end.py`,
  `test_shift_close_governance.py`, `test_freeze_invariant.py`, all four
  schema-parity modules, `test_p2b_openapi_contract.py`,
  `test_operations_domain_serialization.py`): **100 passed** (includes the
  9 new static enum-parity tests).
- `python scripts/testing/validate_repository.py`: **PASS**
- `python scripts/check_session_state.py`: **PASS**
- `python scripts/generate_catalog.py --check`: **PASS** — drift confined
  to the `operations-ledger` metrics/enforcement/tests/next_step fields
  and totals, matching section 8 exactly; no unrelated field changed.
- `python scripts/check_file_size.py`: **PASS** (strict, no `--warn`).
- `git diff --check`: exit 0 (only CRLF-conversion notices).
- Workspace doctor: **PASS WITH NOTE (24 passed, 1 warning)** — unchanged.

## 10. Protected read-only surfaces — byte-identity confirmed

SHA-256 recorded before this repair and re-verified identical after:
`database/migrations/001_foundation.sql`,
`database/migrations/002_tasks_customers_reports.sql`,
`database/migrations/003_users.sql`,
`database/migrations/004_approval_receipts.sql`,
`scripts/apply_migrations.py`, `docker-compose.yml`,
`packages/operations-ledger/src/operations_ledger/sql_ledger.py`. All
matched exactly (`_rows.py` and `apps/workspace-api/src/**` are additionally
confirmed untouched via `git status` showing no diff for either). Only
`tables.py` changed, exactly as authorized by PG-REV-F1.

## 11. Cleanup confirmation (both repaired runs)

Independently verified via `docker ps -a`, `docker ps -a --filter
name=cvf-pg-live-` and `docker volume ls` after each run's cleanup:

- **Zero** containers matching the `cvf-pg-live-` prefix remain.
- **Zero** Docker volumes remain; the specific anonymous-volume ID captured
  by each run was independently confirmed absent
  (`docker volume inspect <id>` → "no such volume").

## 12. Independent Codex reproduction (post PG-REV-F6)

Following the PG-REV-F6 repair (section 3), Codex independently reproduced
the disposable PostgreSQL 16 live round-trip end-to-end, separately from
the Amendment 1 runs recorded in sections 5-7:

- Live suite: **36 passed, 0 failed, 0 skipped**.
- Migration apply/reapply: **17/0** (first attempt), **14/3** (reapply) —
  the same pattern as section 6, confirming no regression.
- Existing shift-lifecycle + contract exit-gate subset (SPEC AC-20): **100
  passed**.
- The disposable container and its captured anonymous volume were both
  independently confirmed **absent** after cleanup.

This evidence was produced independently by the reviewer, not by the
repair worker, and is recorded here for continuity. It corroborates, but
does not by itself close, Phase 1 (section 13).

## 13. Claim boundary

This receipt proves a disposable local PostgreSQL 16 round-trip against a
schema created exclusively from `database/migrations/001-004`, through the
real `SqlLedger`/`apply_migrations.py` code paths, reproduced twice with
identical results, plus one further independent Codex reproduction
(section 12). It does **not** prove production deployment, load,
concurrency, backup/restore, high availability, network security, or
managed-PostgreSQL parity. It is **not** AI/agent governance evidence — no
provider call was made and none is required. No secret or production
credential was read or used — only a process-local, single-use, randomly
generated password for containers that no longer exist, with their
anonymous volumes independently confirmed absent. No pre-existing
container, image, volume or database was touched.

**Phase 1 is not closed by this receipt alone and remains open.** Per SPEC
AC-20, Phase 1 may be marked `DONE` only after final reviewer disposition
on the complete PG-REV-F1 through F6 repair chain and a rollback rehearsal,
in addition to this PostgreSQL result and the independent shift-lifecycle +
contract exit-gate rerun (section 12) — all reviewed by Codex. Nothing in
this tranche was staged, committed or pushed.
