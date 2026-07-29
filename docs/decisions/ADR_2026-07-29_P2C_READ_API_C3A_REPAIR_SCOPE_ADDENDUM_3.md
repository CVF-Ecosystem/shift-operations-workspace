# ADR: P2C Read API C3a Repair Scope Addendum 3

- Date: 2026-07-29
- Status: ACCEPTED
- Tranche: `P2C-OPERATIONS-CONSOLE-READ-SLICE-2026-07-28`
- Phase: BUILD C3a repair

## Context

Amendment 2 authorized the implementation and repair paths required for the P2C
read slice. During repair of review finding F20, the required PostgreSQL 500/501
matrix was added to `tests/integration/test_postgres_live_runner.py`. That file
then reached 315 lines and violated the repository's 300-line Python guard.

The other natural hosts are also unsuitable:

- `tests/integration/test_sql_ledger_postgres_live.py`: 298 lines
- `scripts/run_postgres_live_roundtrip.py`: 300 lines

Compressing the matrix, mixing it into an unrelated test module, or granting a
file-size exception would reduce clarity and weaken the guard.

## Decision

Authorize exactly one additional C3a implementation path:

`tests/integration/test_p2c_read_postgres_limit_live.py`

This module owns only the P2C R27 PostgreSQL 500/501 live read-limit matrix. The
matrix currently placed in `test_postgres_live_runner.py` must be moved, not
duplicated, into the new module.

No file-size exception is granted. Every touched or new Python file remains at
or below 300 lines.

## Required matrix

The module must exercise the real API-to-ledger path using `TestClient`, the
application ledger dependency, and a live PostgreSQL-backed `SqlLedger`.

It must independently prove 500 succeeds and 501 is rejected for:

- shifts
- events
- open-work tasks
- open-work customer requests
- open-work incidents

Each open-work group must be seeded and evaluated independently so one group's
limit cannot mask another group's behavior.

## Execution boundary

The new test module is a separately invoked, opt-in live target under
`LIVE_POSTGRES_DATABASE_URL`. It must be executed against a disposable
PostgreSQL 16 container using the existing live-runner orchestration primitives,
with the exact invocation and cleanup result recorded in evidence.

This addendum does not authorize changes to:

- `scripts/run_postgres_live_roundtrip.py`
- its `LIVE_SUITE_TARGETS`
- the existing assertion covering that runner's three standard targets

## Consequences

- The C3a ceiling expands from 29 to 30 implementation paths.
- `tests/integration/test_postgres_live_runner.py` returns to its runner-test
  responsibility and to at most 300 lines.
- Amendment 2 findings F10 and F20-F24 remain mandatory.
- C3b remains unauthorized.
