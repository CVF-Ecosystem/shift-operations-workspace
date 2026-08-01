# Work Order Amendment 2 — P2-C C3b1 Outcome-Unknown Compatibility Host

- Parent: `P2C-MUTATION-FULL-UI-C3B1-WO-001`
- Prior amendment: `P2C_MUTATION_FULL_UI_C3B1_WORK_ORDER_AMENDMENT_1.md`
- Finding: `C3B1-BUILD-FEAS-F1 OUTCOME_UNKNOWN_EXHAUSTIVE_CONSUMER`
- Risk: `R2`
- Status: `REVIEW_PASS / APPROVED — RESUME ONLY AFTER PUSHED CHECKPOINT`

## Amendment

Add exactly path 35 to the C3b1 BUILD ceiling:

35. `apps/workspace-web/src/components/AsyncState.tsx`

The final ceiling is exactly 35 numbered/35 unique paths: the original 34
plus this one path. No other Work Order path, command, requirement, evidence
class, stop condition, role or claim changes.

## Exact implementation authority

`AsyncState.tsx` may change only enough to keep its exhaustive
`Record<ApiErrorKind, string>` truthful by adding the `outcome_unknown`
message required by R38. The message must be sanitized and must state that the
request outcome cannot be confirmed and a fresh read is required before retry.

It may not add buttons, handlers, retry/refresh execution, storage, queueing,
new component state, styles, navigation, mutation controls or feature wiring.
Every other React component/feature/style path remains outside the ceiling.

The existing authorized frontend tests must prove the exact error kind and
sanitized message; no additional test path is added. Typecheck, frontend tests
and build must pass. Synthetic edits remain prohibited.

## Resume and ownership

The current partial candidate remains unstaged. After independent review and
push, a separate four-surface resume checkpoint becomes the new exact BUILD
parent. The worker must reconfirm continuity, 35-path authorization, zero
outside/staged files and rerun the applicable gates before editing path 35.

The worker still MUST NOT stage, commit, push, self-review or FREEZE. No
provider call or Claude CLI/MCP control is authorized. C3b2-C3d remain blocked.
