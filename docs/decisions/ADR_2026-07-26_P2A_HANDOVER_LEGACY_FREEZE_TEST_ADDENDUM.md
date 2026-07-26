# ADR Addendum — P2-A Handover Legacy Freeze Tests

ID: `ADR-2026-07-26-P2A-HANDOVER-LEGACY-FREEZE-TEST-ADDENDUM`
Tranche: `P2A-HANDOVER-VERTICAL-2026-07-26`
Risk: R2
Phase: DESIGN amendment after BUILD stop
Status: REVIEW_PASS
Amends: `ADR_2026-07-26_P2A_HANDOVER_VERTICAL.md`

## Finding

The IMPLEMENTATION_WORKER stopped without repair after the new
`open_handover_items_linked` prerequisite made four full-suite tests fail:

- two tests in `tests/cvf/test_atomic_mutation_audit.py`;
- two parameterized cases in `tests/cvf/test_customer_request_vertical.py`.

Those tests construct a closed shift and call freeze with the legacy
unimplemented-prerequisite override, but do not construct a real reviewed and
acknowledged handover. Both paths are outside the exact 39-path Work Order.

Codex independently reproduced the checkpoint:

```text
focused authorized handover/freeze suites: 71 passed
full tests/: 7 failed, 545 passed, 44 skipped, 1 warning
```

Three failures are expected unfinished authorized work (catalog and OpenAPI).
The remaining four are exactly the two omitted legacy test paths above.

Finding: `HOV-AUTH-F4 — LEGACY_FREEZE_TEST_SCOPE_OMISSION`.

## Decision

Authorize exactly the two omitted test paths and raise the C3 ceiling from 39
to 41:

1. `tests/cvf/test_atomic_mutation_audit.py`
2. `tests/cvf/test_customer_request_vertical.py`

Their permission is narrow: update freeze setup/assertions to create the same
real server-derived DRAFT -> REVIEWED -> ACKNOWLEDGED prerequisite required by
the parent SPEC. The atomic-audit tests must still reach the injected audit
failure and prove the entire freeze/readiness/audit transaction rolls back.
The customer-request tests must still prove a frozen parent rejects creation.

No production compatibility bypass is allowed. In particular, empty open work,
test mode, the report override, or a legacy caller may not waive the
acknowledged-handover prerequisite.

## Boundary

All other parent design decisions and protected paths remain unchanged. The
two files may not be refactored beyond the fixture/setup needed for the new
freeze contract. No service/router/domain behavior from customer requests,
tasks, incidents, reports, authentication, approval or events is authorized.

No provider call is needed for this authorization amendment. The parent
BUILD's PostgreSQL and real-provider evidence requirements remain mandatory.

## Independent disposition

Codex, acting as independent REVIEWER under the operator-delegated authority,
confirms the defect and approves this bounded design amendment without waiver.
BUILD/repair remains paused until the companion SPEC and Work Order amendment
are committed and continuity records the resumption.
