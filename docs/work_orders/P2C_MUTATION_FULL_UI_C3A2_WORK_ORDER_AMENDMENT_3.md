# Work Order Amendment 3 — P2-C C3a2 Exact-Set Ceiling Contraction

- Parent: `docs/work_orders/P2C_MUTATION_FULL_UI_C3A2_WORK_ORDER.md`
- Prior amendments: `P2C_MUTATION_FULL_UI_C3A2_WORK_ORDER_AMENDMENT_1.md`,
  `P2C_MUTATION_FULL_UI_C3A2_WORK_ORDER_AMENDMENT_2.md`
- Finding: `C3A2-BUILD-REV-F3 AC32_EXACT_SET_MISMATCH`
- Risk: `R2`
- Status: `APPROVED — RESUME ONLY AFTER PUSHED CHECKPOINT AND G6 RECONFIRMATION`

## Exact contraction

Remove exactly these paths from the prior 82-path BUILD set:

- `tests/cvf/test_assignment_foundation.py`
- `tests/cvf/test_customer_request_repair.py`
- `tests/cvf/test_customer_request_transitions.py`
- `tests/cvf/test_shift_create_admission.py`
- `tests/integration/test_p2c_read_postgres_limit_live.py`
- `tests/integration/test_shift_create_live_evidence_runner.py`
- `tests/integration/test_shift_create_postgres_live.py`
- `tests/integration/test_shift_create_sqlite.py`

The final exact C3a2 BUILD set is exactly 74 unique paths: the original and
prior-amendment union of 82 minus these eight. For amended execution and
reporting, every earlier reference to a 79-, 81- or 82-path ceiling/set is
superseded by this exact contracted 74-path set. The removed paths are now
prohibited, not reserved.

## Repair contract

- keep all eight removed paths byte-identical to the resume/review parent;
- retain the current 74-path candidate with zero outside and zero staged;
- rewrite the BUILD receipt to state exact 74-of-74 equality and remove any
  suggestion that an authorized subset satisfies AC-32;
- rerun the focused matrix, full non-live suite, repository gates and exact
  set-difference proof after the receipt repair;
- retain the already-recorded fresh post-F2 provider receipt unless a
  provider-path implementation or live receipt changes; do not make another
  provider call merely because the ceiling contracted;
- return `READY_FOR_INDEPENDENT_P2C_C3A2_BUILD_RE_REVIEW` for independent
  verification of F1-F4 and all original requirements.

Every original evidence, PostgreSQL, AC-29, cleanup, protected-boundary,
worker/commit separation and claim limitation remains mandatory. The partial
BUILD stays unstaged. After independent approval and push, a separate
four-surface resume checkpoint is required. The worker does not stage, commit,
push, self-review or FREEZE.
