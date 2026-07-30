# SPEC Amendment 2 — Independent BUILD Review Repair

- Tranche: `MESSAGE-ADMISSION-TRUST-REPAIR-2026-07-30`
- Risk: R2
- Status: `REVIEW_PASS`

R1-R20 and AC-01 through AC-23 remain in force. Add:

## R21 — complete historical OpenAPI reduction

The predecessor shift-create OpenAPI proof must reverse the complete later
message-admission delta — bearer security plus exact `MessageInput`
requiredness and property shapes — before hashing its own pre-shift-create
baseline. It must assert the current shape before reversal and must not
refresh any historical baseline digest.

## R22 — total endpoint-failure sanitization

Endpoint parsing, hostname/port handling, request construction and transport
must share one sanitized failure boundary. Invalid ports, malformed IPv6,
userinfo, query, fragment and ordinary transport exceptions must never
return, print, traceback or persist their secret-bearing fragments.
Adversarial tests must prove the call returns a sanitized failure instead of
raising a raw exception.

## R23 — observed zero-write refusal evidence

Each of the seven R16 refusals observes both:

- provider-call delta exactly zero;
- message-write and audit-write deltas exactly zero.

The runner must fail if an otherwise correctly refused request appends an
audit. A negative test injects such an audit and proves the gate does not
report PASS.

## R24 — exact rollback and PostgreSQL state assertions

InMemory and SQLite audit-failure tests assert that message and audit state
are unchanged after the exception. PostgreSQL proofs assert:

- exact R6 audit fields on success and after reconnect;
- zero new message/audit state after frozen-shift refusal;
- exactly the original row and no extra audit after duplicate refusal;
- connection usability after every rollback/refusal case.

Test names and receipts must not claim no-partial-state behavior from a
status/exception assertion alone.

## R25 — truthful evidence and catalog

The BUILD receipt records the full-suite failure and its repair without
contradiction. The registry/catalog no longer lists message persistence as
remaining work. Because R22-R24 change evidence validity, fresh PostgreSQL
and provider runs are mandatory after all non-live tests pass; prior live
output cannot be reused for closure.

## Added acceptance criteria

- **AC-24:** full suite passes with the predecessor OpenAPI proof intact and
  no blind historical digest refresh.
- **AC-25:** invalid-port and malformed-endpoint adversarial probes return
  sanitized failures with no secret in result/stdout/stderr/receipt.
- **AC-26:** every refusal proves zero provider, message and audit deltas;
  injected refusal audit is detected.
- **AC-27:** InMemory/SQLite/PostgreSQL rollback and no-partial-state
  assertions satisfy R24 mechanically.
- **AC-28:** receipts/catalog are internally consistent and fresh live
  PostgreSQL/provider evidence follows the repaired non-live gates.

No waiver is granted for `MAR-BUILD-REV-F1` through `MAR-BUILD-REV-F5`.

