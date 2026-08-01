# SPEC Amendment 9 — P2-C C3b1 Outcome-Unknown Connection Expectation

- Tranche: `P2C-MUTATION-FULL-UI-2026-07-31`
- Checkpoint: `C3b1`
- Risk: `R2`
- Status: `REVIEW_PASS`

## Amendment

Add `R39 — rendered outcome-unknown integration expectation`:

> C3b1 SHALL add exactly
> `apps/workspace-web/src/tests/App.test.tsx` to its BUILD ceiling. Its existing
> fetch-level ambiguous-transport case MUST expect the controlled
> `Connection issue` state, not the known-offline state, and MUST assert the
> exact sanitized R38 message. The edit MUST be line-neutral and MUST NOT alter
> application source, production behavior, styles, retry/refresh execution,
> state, storage, navigation, mutation controls or feature wiring.

AC-17 and AC-32 additionally require the rendered integration assertion and
the full frontend suite to pass. The final exact C3b1 changed set is 36 paths.
All earlier requirements, acceptance criteria and nonclaims remain unchanged.

This amendment grants no BUILD resume, provider call, stage, commit, push,
self-review or FREEZE authority.
