# PostgreSQL Live Round-Trip Specification

Status: APPROVED SPECIFICATION — BUILD AWAITS C1/C2 GATES
Spec ID: `P1-PG-LIVE-SPEC-001`
Tranche: `P1-POSTGRESQL-LIVE-ROUNDTRIP-2026-07-26`

## 1. Intended result

The repository shall contain a reproducible, opt-in test that demonstrates
`SqlLedger` behavior against PostgreSQL 16 using a schema created exclusively
from the tracked SQL migrations.

## 2. Scope

### In scope

- disposable local PostgreSQL container orchestration;
- migration apply and live reapply;
- PostgreSQL-only ledger round-trip and constraint tests;
- live `pg_catalog` comparison for mapped persistence tables;
- sanitized evidence receipt;
- conditional catalog regeneration caused by new executable files.

### Out of scope

- edits to migrations, `SqlLedger`, table metadata or application code;
- repository Compose volumes or existing databases;
- performance/load/concurrency/HA/backup testing;
- production credentials or deployment;
- provider calls and AI-governance claims;
- P2-A incidents/handovers or P2-C;
- closing any Phase 1 criterion other than the PostgreSQL round-trip gate.

## 3. Normative requirements

### R1 — opt-in and fail closed

The live test runs only when given a runner-created PostgreSQL URL. Direct
execution without the explicit opt-in must skip or fail with a clear reason;
it must never silently fall back to SQLite.

### R2 — isolated container

The runner uses `postgres:16-alpine`, a unique container name, a dynamically
assigned loopback port and no named/bind data volume. It rejects a pre-existing
container with the same name and removes only its own exact container.

### R3 — readiness and cleanup

Readiness is bounded by a timeout and confirmed with `pg_isready`. Cleanup runs
on success, failure and interruption. Failure to confirm cleanup is a failed
run and must be reported.

### R4 — credential handling

The database credential is generated for the disposable run, remains
process-local and is never printed. Logs and the receipt must not contain a
password, complete database URL, Authorization header or environment dump.

### R5 — migration authority

The runner invokes the existing migration runner for all four ordered
migration files. Neither runner nor live test may invoke `metadata.create_all`.
The migrations are applied twice to the same live database; the second pass
must succeed only through the runner's documented duplicate-object handling.

### R6 — live identity

The test asserts SQLAlchemy dialect `postgresql`, server major version 16 and
the expected database name. A SQLite or mocked connection is a hard failure.

### R7 — live schema

The live catalog contains all tables and enum types created by migrations
001–004. For the exact `SqlLedger`-owned set declared by the static
schema-parity suite (`shifts`, `operational_events`, `evidence_links`,
`corrections`, `audit_records`, `tasks`, `customer_requests`, `users`,
`task_creation_intents`, `approval_receipts`), compare the live catalog
against the SQLAlchemy mapping for:

- column names and nullability;
- compatible type family;
- primary-key columns;
- foreign-key target table/column;
- CHECK/status constraints relevant to mapped behavior.

Unmapped migration tables may exist but must not be represented as
`SqlLedger`-verified behavior.

### R8 — round-trip

Through `SqlLedger`, the test persists and reads back, after engine disposal
and reconnect:

- a shift;
- an operational event with evidence;
- a task and transition/version;
- append-only corrections;
- an audit record;
- an authenticated user;
- approval receipt and task-creation intent data supported by the current
  ledger interface.

IDs, timestamps, enum values, JSON/evidence and versions must survive without
loss or coercion beyond the existing public model contract.

### R9 — constraints

Direct live inserts prove PostgreSQL rejects:

- an event referencing an unknown shift;
- an inverted shift window;
- an inverted event window;
- a status value outside the migration CHECK;
- a duplicate approval-receipt scope key.

Each rejection must be followed by a successful query, proving the test
transaction was correctly isolated rather than leaving the connection
aborted.

### R10 — rollback

A deliberate exception inside `SqlLedger.transaction()` after at least one
write must roll back every write in that unit. The record must be absent when
read through a new connection.

### R11 — receipt

The evidence receipt records:

- UTC timestamp;
- reviewed Git parent/commit state;
- Docker client/server and Compose versions;
- PostgreSQL image tag and immutable image ID/digest available locally;
- migration filenames and first/reapply result counts;
- focused and full test results;
- repository validators and doctor result;
- cleanup confirmation;
- explicit claim boundary and absence of provider/secret use.

It must contain no credential or full database URL.

### R12 — no production repair

If any live failure requires a production, migration or metadata change, BUILD
stops. No such repair is authorized by this specification.

## 4. Acceptance criteria

- **AC-01:** daemon, image and driver prerequisites are verified explicitly.
- **AC-02:** runner creates one isolated disposable container with dynamic
  loopback port and no data volume.
- **AC-03:** all four migrations apply in order to a fresh database.
- **AC-04:** live reapplication succeeds and records applied/skipped counts.
- **AC-05:** test proves PostgreSQL 16 and never calls `metadata.create_all`.
- **AC-06:** live mapped-schema catalog parity passes.
- **AC-07:** all R8 records round-trip across reconnect.
- **AC-08:** all R9 constraint-negative probes are rejected as expected.
- **AC-09:** R10 atomic rollback is proven from a fresh connection.
- **AC-10:** credential/output redaction tests pass.
- **AC-11:** focused live suite passes with zero failure/error/skip.
- **AC-12:** ordinary non-live root suite passes with zero failure/error.
- **AC-13:** repository validator, session-state, catalog, file-size and
  `git diff --check` pass.
- **AC-14:** source/migration/compose/runtime route surfaces remain
  byte-identical.
- **AC-15:** receipt is complete, sanitized and matches independently rerun
  evidence.
- **AC-16:** exact disposable container is absent after every reviewed run.
- **AC-17:** assessment remains untracked, unstaged and byte-identical.
- **AC-18:** no provider call, production secret or pre-existing database is
  used.
- **AC-19:** revert rehearsal restores the post-C2 parent tree and its
  recorded baseline, then removes the temporary worktree.
- **AC-20:** after AC-01–AC-19, independently rerun the existing complete
  shift create/confirm/close/freeze and contract suites. Phase 1 may be marked
  DONE only when those existing gates and the new PostgreSQL gate all pass
  together; otherwise record only the PostgreSQL component result and keep
  Phase 1 open.

## 5. Evidence boundary

This is real database evidence, not CVF AI-governance evidence. Mandatory live
provider proof is therefore not triggered. Mocked database output cannot
satisfy any live acceptance criterion.

## 6. Authorization review

Independent disposition: `REVIEW_PASS` after `PG-AUTH-F1`,
`PG-AUTH-F2` and `PG-AUTH-F3` were repaired without waiver.
