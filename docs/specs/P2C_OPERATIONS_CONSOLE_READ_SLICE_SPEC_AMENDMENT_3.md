# P2C Operations Console Read Slice — Spec Amendment 3

- Date: 2026-07-29
- Status: APPROVED
- Parent specification: `P2C_OPERATIONS_CONSOLE_READ_SLICE_SPEC.md`
- Prior amendment: `P2C_OPERATIONS_CONSOLE_READ_SLICE_SPEC_AMENDMENT_2.md`

## Scope delta

Add exactly one authorized C3a path:

`tests/integration/test_p2c_read_postgres_limit_live.py`

The maximum C3a implementation ceiling is now 30 paths. Governance amendment
documents are outside that implementation ceiling.

## R27 PostgreSQL live-limit proof

The new module shall contain the complete live PostgreSQL boundary matrix:

| Surface or group | Accepted | Rejected |
| --- | ---: | ---: |
| shifts | 500 | 501 |
| events | 500 | 501 |
| open-work tasks | 500 | 501 |
| open-work customer requests | 500 | 501 |
| open-work incidents | 500 | 501 |

The test shall:

1. use the real authenticated HTTP route through `TestClient`;
2. resolve the production application ledger dependency;
3. use `SqlLedger` against PostgreSQL 16;
4. isolate each open-work group from the other two groups;
5. assert the expected success or bounded-failure behavior at both limits;
6. leave no disposable PostgreSQL container behind.

The module remains opt-in and skips when
`LIVE_POSTGRES_DATABASE_URL` is absent.

## File responsibility

The P2C live matrix helpers and parameterized matrix presently appended to
`tests/integration/test_postgres_live_runner.py` must be moved to the new
module. They must not remain duplicated in the runner test.

No Python file-size exception is authorized. Both files must be at most 300
lines.

## Unchanged requirements

All requirements and findings from the parent specification and Amendments 1
and 2 remain in force, including:

- deterministic exact dependency pins;
- `owner_id` required but nullable in the task schema;
- truthful evidence and control mapping;
- the exactly-one-call live-provider gate;
- no C3b work.
