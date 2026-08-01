# P2-C Mutation/Full UI SPEC — Amendment 9

- Scope: C3b2 handover live-evidence runner regression host only
- DESIGN authority:
  `docs/decisions/ADR_2026-08-01_P2C_C3B2_HANDOVER_RUNNER_TEST_CEILING_ADDENDUM.md`
- Parent SPEC: `docs/specs/P2C_MUTATION_FULL_UI_SPEC.md`
- Status: `REVIEW_PASS / APPROVED FOR WORK_ORDER AMENDMENT`

## R39 — Explicit runner preconditions

Every handover live-runner helper invocation affected by R13 must receive an
explicit expected version obtained from the durable response immediately
preceding that mutation. Helper defaults, fixed version literals used as a
general compatibility path, and helper-side current-version lookup are
forbidden.

The ready-handover/no-report regression must still reach the Report prerequisite
and return controlled 409 with zero provider-call delta. It must not terminate
earlier on a stale precondition.

## AC-36

- the focused runner test file passes all 16 tests;
- the added path is the only expansion of the original ceiling;
- the runner helpers have no expected-version default;
- all original C3b2 gates and bounded nonclaims remain mandatory.
