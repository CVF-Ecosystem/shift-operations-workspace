# P2C C3a Amendment 3 Authorization Review

- Date: 2026-07-29
- Reviewer role: `INDEPENDENT_REVIEWER`
- Decision: `REVIEW_PASS`
- Scope: governance authorization only

## Reviewed evidence

The reviewer confirmed:

- the attempted F20 matrix makes
  `tests/integration/test_postgres_live_runner.py` 315 lines;
- `tests/integration/test_sql_ledger_postgres_live.py` is already 298 lines;
- `scripts/run_postgres_live_roundtrip.py` is already 300 lines;
- the worktree has zero staged files;
- a dedicated live-limit module is the smallest coherent repair.

## Authorization decision

Amendment 3 is authorized with exactly one new implementation path:

`tests/integration/test_p2c_read_postgres_limit_live.py`

No file-size exception is authorized. The new module is limited to the P2C R27
PostgreSQL 500/501 matrix, and the corresponding code must be moved out of the
runner test rather than duplicated.

The implementation ceiling becomes 30 paths. All prior findings and gates
remain active. This authorization is not a BUILD review pass and does not
authorize staging, commit, push, freeze, or C3b.
