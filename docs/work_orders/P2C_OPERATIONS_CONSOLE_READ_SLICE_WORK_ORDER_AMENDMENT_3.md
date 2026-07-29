# P2C Operations Console Read Slice — Work Order Amendment 3

- Date: 2026-07-29
- Role: `IMPLEMENTATION_WORKER`
- Parent work order: `P2C_OPERATIONS_CONSOLE_READ_SLICE_WORK_ORDER.md`
- Prior amendment: `P2C_OPERATIONS_CONSOLE_READ_SLICE_WORK_ORDER_AMENDMENT_2.md`
- Authorization: C3a repair only

## Authorized path delta

Add exactly:

`tests/integration/test_p2c_read_postgres_limit_live.py`

The complete C3a implementation ceiling is 30 paths. No other implementation,
test, script, schema, catalog, or configuration path is authorized by this
amendment.

## Required work

1. Move the P2C PostgreSQL 500/501 matrix and its dedicated helpers out of
   `tests/integration/test_postgres_live_runner.py` into the newly authorized
   module. Do not duplicate or minify it.
2. Restore `test_postgres_live_runner.py` to at most 300 lines and preserve its
   existing runner-test responsibilities.
3. Keep the new module at or below 300 lines.
4. Exercise shifts, events, tasks, customer requests, and incidents at both 500
   and 501 through the authenticated API and live PostgreSQL `SqlLedger`.
5. Seed tasks, customer requests, and incidents independently.
6. Run the module as a separate opt-in live target in a disposable PostgreSQL
   16 container using the existing orchestration primitives.
7. Record the exact command, test result, PostgreSQL version, container identity,
   and successful cleanup in the live evidence receipt.

Do not alter `scripts/run_postgres_live_roundtrip.py`, its
`LIVE_SUITE_TARGETS`, or the existing test that asserts those standard targets.

## Continuing repair obligations

Complete the independent-review findings F10 and F20-F24:

- F20: full live PostgreSQL matrix described above;
- F21: independent InMemory and SQLite open-work group limits;
- F22: exact dependency pins;
- F23: task `owner_id` remains required and nullable;
- F24: receipts and control mapping state only freshly proven facts;
- F10: exactly one live provider call with credential-backed evidence.

## Verification and stop rules

Run focused C3a tests, full regression, repository gates, the PostgreSQL 16 live
suite and matrix, cleanup audit, and exactly-one-call live-provider evidence.

Do not stage, commit, push, self-approve, freeze, or begin C3b.

- Report `READY_FOR_INDEPENDENT_P2C_READ_API_BUILD_RE_REVIEW` only when every
  mandatory gate, including the provider gate, passes.
- If the only remaining failure is unavailable provider credentials, report
  `BLOCKED_LIVE_PROVIDER_CREDENTIAL` with zero provider calls.
- Report any other concrete blocker by its actual cause.
