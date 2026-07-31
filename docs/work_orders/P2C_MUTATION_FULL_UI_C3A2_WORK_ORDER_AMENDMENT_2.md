# Work Order Amendment 2 — P2-C C3a2 Handover Runner Test Ceiling Repair

- Parent: `docs/work_orders/P2C_MUTATION_FULL_UI_C3A2_WORK_ORDER.md`
- Prior amendment: `docs/work_orders/P2C_MUTATION_FULL_UI_C3A2_WORK_ORDER_AMENDMENT_1.md`
- Finding: `C3A2-BUILD-BLOCK-F2 HANDOVER_RUNNER_TEST_HOST_OMITTED`
- Risk: `R2`
- Status: `APPROVED — RESUME ONLY AFTER PUSHED CHECKPOINT AND G6 RECONFIRMATION`

## Exact amendment

Add exactly this BUILD path:

82. `tests/integration/test_handover_live_evidence_runner.py`

The final ceiling is exactly 82 unique paths: the original 79, the two paths
from Amendment 1, and this one path. No wildcard, reserve or other authority
is added. For amended execution and worker reporting, every earlier §2/§6 or
Amendment 1 reference to a 79- or 81-path ceiling is superseded by this exact
82-path ceiling.

## Repair contract

- explicitly persist ACTIVE assignments for the test-local principals and
  relevant shifts in the two failing P2-R scenarios;
- preserve the no-report freeze refusal at 409 and its observed zero provider
  calls;
- preserve genuine APPROVED/current END_SHIFT report construction;
- do not make `_auth_headers`, `_with_ledger` or another runner seam grant
  implicit assignment;
- keep the test host under the 300-line executable limit without debt,
  exemption or another file;
- retain every original C3a2 verification, AC-29, receipt, worker/commit
  separation, protected boundary and claim limitation.

The partial BUILD stays unstaged. After independent approval and push, a
separate four-surface resume checkpoint is required before this added path is
edited. The worker still returns
`READY_FOR_INDEPENDENT_P2C_C3A2_BUILD_REVIEW` and does not stage, commit,
push, self-review or FREEZE.
