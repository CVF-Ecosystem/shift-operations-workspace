# SPEC Amendment 8 — P2-C C3b1 Outcome-Unknown Compatibility Host

- Tranche: `P2C-MUTATION-FULL-UI-2026-07-31`
- Checkpoint: `C3b1`
- Risk: `R2`
- Status: `REVIEW_PASS`

## Amendment

Add `R38 — exhaustive outcome-unknown presentation compatibility`:

> C3b1 SHALL add exactly
> `apps/workspace-web/src/components/AsyncState.tsx` to its BUILD ceiling.
> Because that host is an exhaustive `Record<ApiErrorKind, string>`, it MUST
> map `outcome_unknown` to a deterministic sanitized message that tells the
> operator the outcome cannot be confirmed and a fresh read is required
> before retry. It MUST NOT add automatic/manual retry controls, mutation
> controls, storage, queueing, navigation, new state, styling or feature
> wiring. No other React path is authorized. Casts, broad string types,
> non-exhaustive maps or generic tricks that conceal the missing member are
> forbidden.

AC-16/AC-17/AC-32 additionally require typecheck plus a focused assertion for
the exact sanitized `outcome_unknown` mapping. The final exact C3b1 changed set
is 35 paths. All earlier requirements and acceptance criteria remain unchanged.

This amendment grants no BUILD resume, provider call, stage, commit, push,
self-review or FREEZE authority.
