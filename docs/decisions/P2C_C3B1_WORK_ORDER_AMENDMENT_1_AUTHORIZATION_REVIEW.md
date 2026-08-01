# Authorization Review — P2-C C3b1 Work Order Amendment 1

- Target: `docs/work_orders/P2C_MUTATION_FULL_UI_C3B1_WORK_ORDER_AMENDMENT_1.md`
- Finding: `C3B1-G6-F1 INVALID_FRONTEND_TEST_COMMAND`
- Risk: `R2`
- Reviewer role: independent `AUTHORIZATION_REVIEWER`
- Disposition: `REVIEW_PASS / APPROVED`
- BUILD status: `BLOCKED UNTIL PUSHED RESUME CHECKPOINT AND FULL G6 PASS`

## Review result

The amendment truthfully changes only the invalid pnpm invocation from
`pnpm --dir apps/workspace-web test -- --run` to the package-script form
`pnpm --dir apps/workspace-web run test`. The latter matches the committed
`"test": "vitest run"` script and passed the diagnostic baseline with 2 test
files / 22 tests.

The exact 34-path BUILD ceiling, R2 scope, DESIGN/SPEC requirements,
acceptance allocation, evidence classes, stop conditions, worker/reviewer/
commit separation and claim boundary are unchanged. No waiver or new path is
introduced.

The failed G6 attempt cannot be spliced into later evidence. After this
amendment and review are pushed, a separate four-surface resume checkpoint
must be pushed and the complete G6 rerun from the beginning. No BUILD,
provider call, source edit, stage, implementation commit, push, self-review
or FREEZE was authorized or performed during this review.
