# Authorization Review — P2-C C3a2 Ceiling Amendment 2

- Finding: `C3A2-BUILD-BLOCK-F2 HANDOVER_RUNNER_TEST_HOST_OMITTED`
- Reviewed artifacts: C3a2 handover-runner ceiling ADR addendum, SPEC
  Amendment 5 and Work Order Amendment 2
- Risk: `R2`
- Reviewer: independent `AUTHORIZATION_REVIEWER`
- Final disposition: `REVIEW_PASS / APPROVED`

## Review result

Independent mechanical review proves the Amendment-1 ceiling contains exactly
81 unique paths. Excluding the three drafted amendment artifacts, the partial
BUILD contains exactly 58 changed paths, all inside that ceiling, with zero
staged paths. `HEAD == origin/main ==
7b93f7522c513b3d1ae498e2b34b3a46c7f8beb7` at review time.

A fresh full non-live rerun reproduced exactly `1125 passed / 2 failed / 112
skipped`. Both failures occur only in
`tests/integration/test_handover_live_evidence_runner.py`; no other edit host
is required. Source inspection confirms the explicit setup needed:

- no-report scenario: `hov-ev-op2` and `hov-ev-sup3` ACTIVE on the source
  shift, and `hov-ev-sup4` ACTIVE on the destination shift;
- ready-report scenario: `hov-ev-op3` and `hov-ev-rep-approver2` ACTIVE on
  the source shift.

The existing runner `_seed` seam persists the user and ACTIVE assignment, so
the test host alone is necessary and sufficient. Implicit assignment in
`_auth_headers`/`_with_ledger`, production bypass and guard weakening remain
forbidden. The added path is not present in the prior 81; the combined ceiling
is exactly 82 unique paths. The host is 249 lines before repair, leaving
feasible headroom under the 300-line executable limit.

The amendment supersedes prior §2/§6 and Amendment-1 references to 79/81,
preserves the two P2-R regression meanings, and retains all original evidence,
stop/resume, role-separation, commit-ownership and claim boundaries. No
residual finding remains; all findings are `CLOSED_WITHOUT_WAIVER`.

Under the operator's standing Work Order delegation, Amendment 2 is approved.
BUILD remains blocked until these four authorization artifacts are pushed and
a separate four-surface resume checkpoint is pushed. No implementation edit,
provider call, stage, commit, push, self-review or FREEZE was performed by the
independent reviewer.
