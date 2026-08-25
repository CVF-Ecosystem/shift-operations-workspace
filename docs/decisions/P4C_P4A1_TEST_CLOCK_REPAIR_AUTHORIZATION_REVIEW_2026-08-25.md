# Independent Authorization Review — P4-C P4-A1 test-clock repair

- Parent: `P4C-INTEGRATION-EDGE-2026-08-23`
- Phase: `WORK_ORDER`
- Risk ceiling: `R2`
- Reviewer role: `INDEPENDENT_AUTHORIZATION_REVIEWER`
- Reviewed Work Order SHA-256:
  `9c1d7856ffaa72454de89410f122d4e8aeaec1a90afbc50f0907de12aafc25f3`
- Findings: `NONE`
- Waivers: `NONE`
- Disposition: `AUTHORIZATION_REVIEW_PASS`

## Independent checks

The sole added path is unique path 68,
`tests/cvf/test_p4a1_retrieval_authorization_ordering.py`; it is absent from
the accepted 66-path parent ceiling and path-67 amendment. Its current bytes
are unchanged from `HEAD` and hash exactly to the pinned preimage
`139b87fb8ca221eef3cf25cf5476781b5de78a1c6e678ac1de3ba8f42b16800f`.
The staged set is empty.

The observed failure matches the diagnosis. Production records real monotonic
elapsed time, obtains `started_at_utc` and `finished_at_utc` through separate
injected-clock calls, and the receipt contract correctly requires a strictly
later finish when `elapsed_ms > 0`. The local spy currently returns one frozen
UTC value for both calls. That fixture can therefore violate the receipt
contract whenever real elapsed time rounds positive; no runtime or receipt
contract defect is demonstrated.

The authorized replacement is one return expression only. `timedelta` is
already imported, while `datetime` and `timezone` are in the enclosing test
scope. Independent evaluation confirms successive calls return `+1us`, then
`+2us`. The existing `clock_calls.append(1)`, UUID spy and assertions remain
unchanged, so the test continues to prove identity allocation and a pre-R2
clock read without imposing an invalid frozen-clock assumption. Existing peer
P4-A1 fixtures use the same advancing-clock pattern.

## Executable evidence boundary

The isolated node and containing-file requirements resolve unambiguously to:

- `python -m pytest -q tests/cvf/test_p4a1_retrieval_authorization_ordering.py::test_identity_and_start_time_allocated_before_r2_even_on_invalid_request`
- `python -m pytest -q tests/cvf/test_p4a1_retrieval_authorization_ordering.py`

The Work Order pins Amendment 2 at its current SHA-256
`a00006f2239c371f0d3ee31430a3002067fee6d7917e05f0100e33d051f39119`;
therefore its full-suite requirement remains exactly:

`python -m pytest -q --deselect tests/integration/test_xr1s_workspace_link_descriptor.py::test_operations_authorized_contract_is_reciprocal_when_sibling_present`

No other filter is permitted. It must return exactly `2836 passed, 132
skipped, 1 deselected`, including a same-run PASS for the repaired P4-A1 node.
Knowledge, invariant-family, session, catalog, file-size, repository,
`git diff --check`, exact-68, staged-zero and secret guards remain mandatory.
The independent completion reviewer must recompute the one-expression diff;
the repair worker cannot self-approve.

## Effects, stop conditions and retained evidence

The exact-68 ceiling and sole-expression rule prohibit any second file, any
other edit in path 68, and every runtime/model/schema/timeout/monotonic change.
Preimage mismatch, scope drift, a different failure, unexpected count, guard
failure or need for an external effect triggers the Work Order stop boundary.

The accepted doctor receipt is retained and a rerun is forbidden. Offline
verification is green: Core worktree is clean and Core `HEAD`, local
`origin/main`, manifest pin and AGENTS header all equal
`9c01832930226f2f770eafa346e01279160f22cb`; session-state validation passes.

Network, sibling mutation, provider/credential use, install, deployment,
database action, commit and push remain unauthorized. XR1 remains unresolved
environmental debt. This test-fixture repair makes no CVF governance-behavior
claim and requires no live-provider proof.

## Disposition

`AUTHORIZATION_REVIEW_PASS`, findings/waivers `NONE/NONE`.

The separate repair worker may perform only the authorized one-expression
path-68 edit and return the complete evidence set. P4-C FREEZE remains blocked
until a fresh independent completion review observes every required result.
