# Work Order Amendment 1 — P2-C C3b2 Handover Runner Test

- Parent Work Order: `P2C_MUTATION_FULL_UI_C3B2_WORK_ORDER.md`
- Finding: `C3B2-BUILD-FEAS-F1 HANDOVER_RUNNER_TEST_PRECONDITION_DRIFT`
- Risk: `R2`
- Status: `APPROVED — RESUME ONLY AFTER PUSHED CONTINUITY CHECKPOINT`

## Exact ceiling change

Add exactly path 83:

83. `tests/integration/test_handover_live_evidence_runner.py`

The amended C3b2 BUILD set is exactly 83 numbered, unique paths: the original
82 plus this one path. Every original boundary and stop condition remains.

## Required repair

- In the new path, capture each create/review/close response version and pass it
  explicitly to the next runner helper.
- In already-authorized
  `scripts/run_handover_live_governance_evidence.py`, remove the four permissive
  `expected_version=1` defaults. Required expected versions stay keyword-only.
- Preserve the ready-handover/no-report assertion: controlled 409 must identify
  the missing Report prerequisite and provider-call delta remains zero.
- Run the focused 16-test runner file, then every original C3b2 gate afresh.
- Rewrite the BUILD receipt as exact 83/83 and record this blocker/amendment
  history truthfully.

No other path, behavior, provider call, stage, commit, push, self-review or
FREEZE is authorized. A further outside/unnecessary path returns
`BLOCKED_WORK_ORDER_CEILING`.
