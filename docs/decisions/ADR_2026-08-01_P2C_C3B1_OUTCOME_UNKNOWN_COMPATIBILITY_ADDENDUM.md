# ADR Addendum — P2-C C3b1 Outcome-Unknown Compatibility Host

- Tranche: `P2C-MUTATION-FULL-UI-2026-07-31`
- Checkpoint: `C3b1`
- Finding: `C3B1-BUILD-FEAS-F1 OUTCOME_UNKNOWN_EXHAUSTIVE_CONSUMER`
- Phase: `DESIGN AMENDMENT`
- Risk: `R2`
- Status: `REVIEW_PASS — CLOSED_WITHOUT_WAIVER`

## Finding

The worker stopped with 30 of 34 authorized BUILD paths changed, zero outside
and zero staged. Typecheck reproduced the exact blocker:

```text
src/components/AsyncState.tsx(4,7): error TS2741:
Property 'outcome_unknown' is missing ... Record<ApiErrorKind, string>
```

R16/R36 requires `outcome_unknown` to be a load-bearing `ApiErrorKind`.
`AsyncState.tsx` is the sole exhaustive consumer: it maps every member through
`Record<ApiErrorKind, string>`. The other consumers accept the union as props
or compare selected values and do not require a source edit. A second observed
type error is inside already-authorized `api.ts` and creates no ceiling issue.

The reviewed C3b feasibility DESIGN had prohibited every React component path.
Satisfying R16 without changing this exhaustive host is impossible unless the
type contract is weakened or hidden through an unsound generic/cast. Both are
rejected.

## Decision

Add exactly one C3b1 BUILD path:

`apps/workspace-web/src/components/AsyncState.tsx`

Its authority is limited to adding the deterministic, non-secret presentation
message for `outcome_unknown`. It may not add a control, mutation, retry,
refresh action, state machine, storage, styling, navigation or feature wiring.
All other React component/feature/style paths remain protected and unchanged.

The final C3b1 exact ceiling becomes 35 paths. No wildcard, reserve or optional
consumer path is added. If another consumer proves necessary, the worker must
stop again; this addendum cannot be interpreted as family-level React access.

## Boundary

This is compatibility fallout from making the reviewed transport error kind
exhaustive, not C3c UI implementation. R11/R15-R17/R34-R37, evidence classes,
no-provider decision, C3b1 claim and C3b2/C3c/C3d ordering remain unchanged.
No BUILD resume exists until DESIGN/SPEC/WORK_ORDER amendment review, push and
a separate resume checkpoint.
