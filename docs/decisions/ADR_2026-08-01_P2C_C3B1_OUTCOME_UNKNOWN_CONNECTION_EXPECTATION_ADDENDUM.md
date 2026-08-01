# ADR Addendum — P2-C C3b1 Outcome-Unknown Connection Expectation

- Tranche: `P2C-MUTATION-FULL-UI-2026-07-31`
- Checkpoint: `C3b1`
- Finding: `C3B1-BUILD-FEAS-F2 STALE_NETWORK_UI_EXPECTATION`
- Phase: `DESIGN AMENDMENT`
- Risk: `R2`
- Status: `REVIEW_PASS — CLOSED_WITHOUT_WAIVER`

## Finding

After Amendment 2, the preserved candidate contains 31 of the 35 authorized
paths, zero staged. Frontend typecheck passes. The full frontend suite proves
one failure: `App.test.tsx` still expects `Offline` after a fetch-level
`TypeError`, while R16 now classifies that ambiguous transport result as
`outcome_unknown`. Runtime correctly renders the controlled `Connection issue`
indicator plus the sanitized R38 message.

Source inspection disproves the worker's broader proposed host. Existing
`deriveConnectionState` already maps every non-null kind other than the known
`network` kind to controlled `error`; therefore `outcome_unknown` is handled
without a source change. Editing `OperationsConsole.tsx` would be synthetic.
The stale integration expectation cannot be repaired inside any existing
authorized test host because `App.test.tsx` owns the rendered-console proof.

## Decision

Add exactly one C3b1 BUILD path:

`apps/workspace-web/src/tests/App.test.tsx`

Authority is limited to reclassifying the existing ambiguous-transport test
expectation from `Offline` to `Connection issue` and proving the exact
sanitized outcome-unknown alert already required by R38. The repair must be
line-neutral because the file is exactly 200 lines.

`OperationsConsole.tsx` and all other React source remain protected. No new
state, behavior, control, retry, refresh execution, styling or feature wiring
is authorized. The final exact C3b1 ceiling becomes 36 paths, with no wildcard,
reserve or optional path.

No provider call, BUILD edit, staging, commit, push, self-review or FREEZE is
authorized by this DESIGN amendment.
