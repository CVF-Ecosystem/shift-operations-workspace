# Work Order Amendment 2 — P2-C C3a1 Review-Repair Test Split

- Tranche: `P2C-MUTATION-FULL-UI-2026-07-31`
- Checkpoint: `C3a1`
- Risk: `R2`
- Status: `REVIEW_PASS / APPROVED UNDER OPERATOR-DELEGATED AUTHORITY`

## Exact ceiling change

The amended 50 paths remain authorized. Add exactly:

51. `tests/cvf/test_assignment_foundation_f1.py` — NEW
52. `tests/integration/test_assignment_ledger_parity_f1.py` — NEW
53. `tests/integration/test_assignment_postgres_live_f1.py` — NEW

The final C3a1 ceiling is exactly 53 unique paths. There is no wildcard,
conditional allowance, reserve, debt/exemption, self-review, dependency,
continuity or roadmap implementation path.

## Authorized repair use

- `test_assignment_foundation_f1.py` owns the F1 HTTP/application regression
  cases and the F2 `/auth/me` out-of-range NumericDate cases moved from the
  original foundation host;
- `test_assignment_ledger_parity_f1.py` owns InMemory/SQLite F1 parity for
  duplicate assignment id, duplicate-active distinction, unrelated database
  constraint passthrough and no-partial-write behavior;
- `test_assignment_postgres_live_f1.py` owns the corresponding real
  PostgreSQL F1 proof and may reuse only bounded helpers from the original
  PostgreSQL assignment module;
- the original three test hosts and all three companions must each finish at
  or below 300 lines;
- tests may be moved or minimally refactored for shared fixtures, but no
  accepted F1/F2 assertion may be removed or weakened;
- the BUILD receipt must correct the `49/50` statement to the independently
  verified pre-amendment truth: exactly 50/50 changed paths, zero outside.

All prior implementation/evidence commands, claim boundaries, stop
conditions, ownership and worker prohibitions remain unchanged. The worker
must not stage, commit, push, self-review or FREEZE. Any further required path
outside the exact 53 returns `BLOCKED_WORK_ORDER_CEILING`.
