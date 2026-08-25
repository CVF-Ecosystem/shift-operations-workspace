# P4-C full-suite external-failure acceptance amendment

- Tranche: `P4C-INTEGRATION-EDGE-2026-08-23`
- Risk: `R2`
- Operator authority: granted 2026-08-25
- Purpose: supersede only the XR1 environmental portion of SPEC AC-09 and the
  corresponding Work Order full-suite gate
- Product/source/test changed set: unchanged at exact 67 paths

## INTAKE

Independent completion review accepted all exact-67 P4-C evidence but blocked
FREEZE because the unqualified full suite contained two non-P4C failures. The
P4-A1 timing test passed isolated and passed in the subsequent full run. The
remaining failure is exactly:

`tests/integration/test_xr1s_workspace_link_descriptor.py::test_operations_authorized_contract_is_reciprocal_when_sibling_present`

Independent evidence proves this optional cross-workspace test fails before
reading P4-C behavior because the separate Operations sibling lacks historical
git object `f99b3bf...`. Attempting to reconcile that sibling was independently
rejected due to its own continuity/Core drift. No sibling mutation occurred.

## DESIGN

Keep every P4-C requirement and test. For this completion review only, replace
the unqualified full-suite gate with:

1. independently prove the named XR1 node's sole failure cause remains the
   missing sibling git object and that no P4-C path is involved;
2. run the full non-live suite with exactly that one node deselected;
3. require every remaining test, including the P4-A1 timing test, to pass in
   that same run.

This is not a general environmental waiver. No other node, failure, skip,
warning or flaky rerun may be excluded. The XR1 contract remains unresolved;
this amendment only prevents an unrelated optional sibling probe from
misrepresenting P4-C implementation quality.

## SPEC amendment

- **A2-R1:** The exact deselection node is the fully qualified node above;
  zero additional `--deselect`, ignore, keyword, marker or max-failure filter
  is allowed.
- **A2-R2:** Before the amended full run, independently record sibling clean
  worktree/staged state, unchanged HEAD, missing `f99b3bf...`, and isolated
  XR1 failure whose traceback is solely the missing commit.
- **A2-R3:** The amended full run must report exactly one deselection and zero
  failures. Expected current result is `2836 passed, 132 skipped, 1
  deselected`; any different pass/skip count requires explanation and review.
  The sole executable full-suite command is:

  `python -m pytest -q --deselect tests/integration/test_xr1s_workspace_link_descriptor.py::test_operations_authorized_contract_is_reciprocal_when_sibling_present`

  No other collection/filter option is allowed, including another
  `--deselect`, `--ignore`, `-k`, `-m`, `--lf`, `--ff` or `--maxfail`.
- **A2-R4:** The P4-A1 timing node must pass inside that same amended full run;
  an isolated rerun cannot substitute for it.
- **A2-R5:** Knowledge, invariant-family, session, catalog, file-size,
  repository, diff, exact-67, staged-zero and secret gates remain mandatory.
  Retain the independently accepted doctor receipt (`24 PASS + 1` bounded
  legacy warning) from the same exact-67 review state; do not rerun doctor in
  this zero-network amendment. Instead verify offline that Core worktree is
  clean and local Core HEAD/origin-main, manifest pin and AGENTS header all
  equal `9c01832930226f2f770eafa346e01279160f22cb`.
- **A2-R6:** No file edit, doctor rerun, sibling fetch, provider, credential, install,
  deployment, database mutation, commit or push is authorized.

## WORK_ORDER amendment

The `INDEPENDENT_COMPLETION_REVIEWER` may run read-only Git probes, the exact
isolated XR1 node, the exact A2-R3 command and deterministic repository
guards. The reviewer must append a bounded rereview to the existing P4-C
completion review, explicitly retain the unresolved XR1 environmental fact,
and report findings/waivers. No implementation worker is required because the
authorized file changed set is zero.

Stop on changed sibling state, a different XR1 traceback, any second
deselection, any remaining test/guard failure, P4-C scope drift or need for an
external effect. `REVIEW_PASS` is permitted only when all amended requirements
pass; otherwise P4-C remains blocked.

## Disposition

`READY_FOR_INDEPENDENT_AMENDMENT_AUTHORIZATION_REVIEW`. No test gate has been
waived or rerun under this amendment yet.
