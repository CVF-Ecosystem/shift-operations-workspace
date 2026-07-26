# ADR — PostgreSQL Live Round-Trip

Status: ACCEPTED — AMENDMENT 1 INDEPENDENT REVIEW PASS
Tranche: `P1-POSTGRESQL-LIVE-ROUNDTRIP-2026-07-26`
Risk: R2
Owner boundary: disposable local PostgreSQL evidence for the Phase 1 exit gate

## 1. Intake

Phase 1 remains open because `SqlLedger` has been exercised end-to-end only
against SQLite. Static migration/schema-parity tests repaired known drift, but
they do not prove that PostgreSQL accepts the migration-created schema or that
the production dialect survives write, reconnect, constraint and rollback
paths.

The operator confirmed Docker is installed. Intake verification found Docker
CLI 29.6.2 and Compose v5.3.1, but the Docker Desktop Linux daemon was not
running. `psycopg` is also not installed in the current Python environment.
Those are explicit BUILD prerequisites, not reasons to weaken the evidence.

## 2. Decision

Create an opt-in live PostgreSQL test and a small runner that:

1. starts a uniquely named, disposable `postgres:16-alpine` container;
2. publishes PostgreSQL on a dynamically assigned loopback port;
3. uses no repository Compose volume and no pre-existing database;
4. waits for server readiness;
5. applies migrations `001` through `004` using
   `scripts/apply_migrations.py`, then reapplies them to prove the live
   idempotency path;
6. runs a PostgreSQL-only pytest against that migration-created schema;
7. records sanitized evidence and exact tool/image/test facts;
8. removes only the exact disposable container it created, including on test
   failure.

The test must never call SQLAlchemy `metadata.create_all()`. The SQL migration
files remain the sole schema authority.

## 3. Required proof boundary

The live test covers:

- real PostgreSQL dialect and server identity;
- expected migration tables and enum types;
- `SqlLedger` shift/event/evidence/task/correction/audit/user/approval storage;
- persistence after engine disposal and reconnect;
- foreign-key and CHECK rejection;
- real transaction rollback;
- live-catalog parity for the exact `SqlLedger`-owned table set already named
  by the static schema-parity suite;
- migration reapplication against an already initialized database.

## 4. Isolation and safety

- No existing Compose project, named volume, database or container is reused.
- The runner generates an ephemeral credential and never prints it or the full
  database URL.
- Container cleanup targets the exact name created by the runner.
- No production endpoint, provider API or external business system is called.
- A missing daemon, unavailable image, occupied/invalid runtime, migration
  failure or cleanup uncertainty fails closed.

## 5. Alternatives rejected

### Use the repository `docker-compose.yml` and `postgres_data`

Rejected because the named volume may predate later migrations and may contain
user data. It is unsuitable for a deterministic fresh-schema proof.

### Use `metadata.create_all()`

Rejected because it proves SQLAlchemy metadata, not the migration-created
production schema that the Phase 1 gate explicitly names.

### Run only `psql` smoke queries

Rejected because that would not exercise `SqlLedger`, reconnect, evidence,
constraints and transaction behavior through the application persistence
boundary.

### Fix any discovered production defect immediately

Rejected. A live defect changes the design/changed set. The worker must stop
and return evidence for an independently reviewed repair amendment.

## 6. Claim boundary

Passing this tranche proves a local disposable PostgreSQL 16 round-trip
against the repository migrations. C4 may close Phase 1 only if the reviewer
also reruns and verifies the other existing Phase 1 exit-gate evidence:
complete shift create/confirm/close/freeze behavior and contract tests. It
does not prove production deployment, load,
concurrency, backup/restore, high availability, network security, managed
PostgreSQL parity or AI/agent governance.

No provider call is required because no AI-governance claim is asserted.

## 7. Roles

- Codex: `ORCHESTRATOR → SPEC_AUTHOR → WORK_ORDER_AUTHOR`
- Codex: independent authorization `REVIEWER / COMMIT_STEWARD`
- Claude: `IMPLEMENTATION_WORKER`, only after approved C1 and C2 are pushed
- Codex: independent BUILD `REVIEWER → COMMIT_STEWARD → CLOSER`

Claude may not self-approve, stage, commit or push.

## 8. Normative artifacts

- `docs/specs/POSTGRESQL_LIVE_ROUNDTRIP_SPEC.md`
- `docs/work_orders/POSTGRESQL_LIVE_ROUNDTRIP_WORK_ORDER.md`

This ADR alone does not authorize BUILD.

## 9. Independent authorization review

Codex found and repaired without waiver:

- `PG-AUTH-F1 CATALOG_MUTATION_CONTRACT_CONFLICT`;
- `PG-AUTH-F2 PHASE1_CLOSURE_UNDER_SPECIFIED`;
- `PG-AUTH-F3 LIVE_SCHEMA_SCOPE_OVERBROAD`.

Disposition: `REVIEW_PASS` on 2026-07-26.

## 10. Amendment 1 — native PostgreSQL ENUM repair

The first real live run correctly stopped with
`psycopg.errors.DatatypeMismatch`: migration-native enum columns were mapped
as generic `String`, so psycopg bound explicit values as `VARCHAR`.
Independent review reproduced `26 passed, 7 failed` and confirmed the same
root cause.

The repair decision is:

1. keep `String` as the portable SQLite type;
2. attach PostgreSQL variants using `postgresql.ENUM`, exact migration type
   names/values and `create_type=False`;
3. repair every mapped native-enum column, including the minimally mapped
   `messages.state`, not only the first failing `shifts.status`;
4. leave migrations and `SqlLedger` byte-identical;
5. make static and live parity distinguish `ENUM:<type_name>` from text;
6. scrub the generated URL and password from all failure stdout/stderr and
   stored tails;
7. clean up only a container proven to have been created by this runner, and
   fail if container removal or anonymous-volume removal cannot be verified.

Independent review also found:

- `PG-REV-F2 FAILURE_OUTPUT_CREDENTIAL_LEAK`;
- `PG-REV-F3 CLEANUP_OWNERSHIP_BUG`;
- `PG-REV-F4 TYPE_PARITY_TEST_INCOMPLETE`;
- `PG-REV-F5 RECEIPT_DRIFT`.

All five review findings, including the production enum defect
`PG-REV-F1`, are repair obligations. No waiver is granted.

Alternative bind casts in every insert/update were rejected because they
would duplicate schema knowledge throughout `SqlLedger`. Correct type mapping
keeps the fix centralized at the existing metadata boundary.
