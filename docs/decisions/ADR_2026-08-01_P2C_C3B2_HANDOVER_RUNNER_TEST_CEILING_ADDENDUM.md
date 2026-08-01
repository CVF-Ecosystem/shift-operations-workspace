# ADR Addendum — P2-C C3b2 Handover Runner Test Ceiling

- Tranche: `P2C-MUTATION-FULL-UI-2026-07-31`
- Checkpoint: `C3b2 BUILD repair`
- Parent: `ADR_2026-08-01_P2C_C3B_FEASIBILITY_ADDENDUM.md`
- Finding: `C3B2-BUILD-FEAS-F1 HANDOVER_RUNNER_TEST_PRECONDITION_DRIFT`
- Disposition: `CLOSED_WITHOUT_WAIVER`

## Context and observed evidence

The partial exact-path BUILD correctly stopped without editing outside its
ceiling. The full regression fan-out reaches the existing P2-R runner test
`tests/integration/test_handover_live_evidence_runner.py`, which directly calls
the runner helpers changed by C3b2. A focused reproduction returned `1 failed /
15 passed`: the test's ready-handover/no-report scenario used the helpers'
temporary `expected_version=1` defaults, so freeze failed on stale Shift
version instead of proving the intended independent missing-Report refusal.

## Decision

Add exactly that one existing test path to C3b2. The test must thread versions
from each preceding HTTP response into review, acknowledge, close and freeze.
The already-authorized runner must remove permissive expected-version defaults;
helpers may not fetch or invent the current value for a caller.

This raises the exact BUILD set from 82 to 83 paths. No wildcard, reserve,
waiver, provider call, React/C3c work or change to the precondition semantics is
authorized. The original design remains intact.
