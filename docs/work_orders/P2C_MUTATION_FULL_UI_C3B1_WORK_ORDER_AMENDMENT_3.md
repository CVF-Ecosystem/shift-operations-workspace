# Work Order Amendment 3 — P2-C C3b1 Outcome-Unknown Connection Expectation

- Parent: `P2C-MUTATION-FULL-UI-C3B1-WO-001`
- Prior amendment: `P2C_MUTATION_FULL_UI_C3B1_WORK_ORDER_AMENDMENT_2.md`
- Finding: `C3B1-BUILD-FEAS-F2 STALE_NETWORK_UI_EXPECTATION`
- Risk: `R2`
- Status: `REVIEW_PASS / APPROVED — RESUME ONLY AFTER PUSHED CHECKPOINT`

## Amendment

Add exactly path 36 to the C3b1 BUILD ceiling:

36. `apps/workspace-web/src/tests/App.test.tsx`

The final ceiling is exactly 36 numbered/36 unique paths: the amended 35 plus
this one path. No other Work Order path, command, requirement, evidence class,
stop condition, role or claim changes.

## Exact implementation authority

`App.test.tsx` may change only the existing ambiguous-transport UI case so it:

- expects `Connection issue` rather than `Offline`; and
- asserts the exact sanitized R38 outcome-unknown message.

The edit must remain at or below the existing 200-line hard limit and therefore
must be line-neutral. `OperationsConsole.tsx` is explicitly not authorized:
its existing generic controlled-error branch already handles
`outcome_unknown`. No application behavior, component, style, state, handler,
retry/refresh execution, storage, navigation, mutation control or feature
wiring may change.

## Resume and ownership

The partial candidate remains unstaged. After this amendment/review and a
separate four-surface checkpoint are pushed, the worker must reconfirm the
36-path ceiling, zero outside/staged files and absence of generated
`tsconfig.tsbuildinfo`, then resume without discarding prior work.

All Amendment 2 file-size obligations and original gates remain mandatory.
The worker MUST NOT stage, commit, push, self-review or FREEZE. No provider call
or Claude CLI/MCP control is authorized. C3b2-C3d remain blocked.
