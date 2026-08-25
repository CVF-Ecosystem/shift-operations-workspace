# P4-C Amendment 3 — P4-A1 test-clock repair Work Order

- Parent: `P4C-INTEGRATION-EDGE-2026-08-23`
- Risk: `R2`
- Operator authority: granted 2026-08-25
- Accepted full-suite amendment SHA-256:
  `a00006f2239c371f0d3ee31430a3002067fee6d7917e05f0100e33d051f39119`
- BUILD: `STOPPED_PENDING_AUTHORIZATION_REVIEW`

## Diagnosed contract

The amended P4-C full run has one remaining failure. The local spy
`counting_utc_now()` in
`tests/cvf/test_p4a1_retrieval_authorization_ordering.py` always returns one
fixed UTC value, while the runtime correctly measures real monotonic elapsed
time. If elapsed rounds positive, the receipt correctly rejects equal start
and finish timestamps. Peer P4-A1 tests already use advancing injected clocks.

This is a deterministic test-fixture defect, not a runtime or receipt-contract
defect. The test's actual purpose—prove two UUID allocations and a pre-R2 clock
read—does not require a frozen wall clock.

## Exact changed-set amendment

Add exactly path 68:

68. `tests/cvf/test_p4a1_retrieval_authorization_ordering.py`

Preimage SHA-256:
`139b87fb8ca221eef3cf25cf5476781b5de78a1c6e678ac1de3ba8f42b16800f`.
The final P4-C implementation union becomes exactly 68 unique paths.

## Sole authorized edit

Inside `counting_utc_now()`, preserve `clock_calls.append(1)` and change only
the return expression so successive calls advance by their 1-based call count:

`return datetime(2026, 8, 10, 12, 0, tzinfo=timezone.utc) + timedelta(microseconds=len(clock_calls))`

`timedelta` is already imported. No helper, assertion, runtime, receipt model,
schema, timeout, monotonic logic or other test may change.

## Evidence

1. Verify preimage, staged-zero and exact path boundary before edit.
2. Run the repaired test isolated and its containing test file.
3. Run exactly the accepted amended full command from Amendment 2, with only
   the named XR1 node deselected; require `2836 passed, 132 skipped, 1
   deselected` and zero failures.
4. Run Knowledge, invariant-family, session, catalog, file-size, repository,
   diff, exact-68, staged-zero and secret guards. Retain the accepted doctor
   receipt and verify Core equality/cleanliness offline; do not rerun doctor.
5. Independent reviewer recomputes the one-expression diff and all evidence,
   retaining XR1 as unresolved environmental debt.

## Effects and stop conditions

No network, doctor rerun, sibling mutation, provider, credential, install,
deployment, database action, commit or push. Stop on any second test-file
change, runtime/contract change, different failure, unexpected count or guard
failure. The repair worker cannot self-approve.

## Disposition

`READY_FOR_INDEPENDENT_AUTHORIZATION_REVIEW`.
