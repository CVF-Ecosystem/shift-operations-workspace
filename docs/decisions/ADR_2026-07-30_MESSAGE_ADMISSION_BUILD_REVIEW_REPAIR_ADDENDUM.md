# ADR Addendum — Message Admission BUILD Review Repair

- Tranche: `MESSAGE-ADMISSION-TRUST-REPAIR-2026-07-30`
- Phase: `DESIGN AMENDMENT`
- Risk: R2
- Status: `REVIEW_PASS — REPAIR AUTHORIZATION ONLY`
- Independent reviewer: Codex

## Review disposition

The first independent BUILD review returns `REVIEW_CHANGES_REQUIRED`.
Focused tests pass, but the full suite has one historical OpenAPI-chain
failure and adversarial review probes found two live-evidence false-positive
paths. Five findings must close without waiver:

- `MAR-BUILD-REV-F1 FULL_REGRESSION_AND_CEILING_GAP`: the predecessor
  shift-create OpenAPI proof does not reverse the later message-admission
  delta. It fails the full suite, but its test path is outside the original
  29-path ceiling.
- `MAR-BUILD-REV-F2 ENDPOINT_PORT_SECRET_LEAK`: endpoint cleaning reads
  `urlsplit(...).port` outside the protected/sanitized exception boundary.
  An invalid secret-bearing port raises a `ValueError` containing the raw
  secret.
- `MAR-BUILD-REV-F3 REFUSAL_AUDIT_FALSE_PASS`: the provider-evidence refusal
  runner verifies status and zero messages but not zero audit-write delta.
  An adversarial probe injected seven refusal audits while all seven cases
  still reported PASS.
- `MAR-BUILD-REV-F4 ROLLBACK_AND_POSTGRES_ASSERTION_GAPS`: non-live
  audit-failure tests assert only the exception, while PostgreSQL frozen and
  duplicate tests are named as no-partial-state proofs without asserting the
  complete row/audit state required by SPEC R11-R12.
- `MAR-BUILD-REV-F5 RECEIPT_AND_CATALOG_TRUTH_DRIFT`: the BUILD receipt
  simultaneously says the predecessor OpenAPI test passes and records it as
  the sole full-suite failure. The module registry still lists message
  persistence as remaining work after implementing it.

## Decision

The final C3 ceiling gains exactly one path:

30. `tests/unit/test_shift_create_openapi_contract.py`

That test may change only to reverse the complete, later SPEC R13
message-admission delta before proving its own older shift-create delta. Its
historical digest must not be blindly refreshed.

All other findings are repaired only inside paths already authorized by the
original 29-path ceiling. Endpoint parsing and cleaning must be inside a
sanitized failure boundary, including invalid port and malformed URL cases.
Every refusal must observe both message and audit deltas, with an adversarial
test proving an injected refusal audit fails the gate. Rollback and
PostgreSQL tests must assert the exact persisted message/audit state they
claim. Receipts and generated catalog surfaces must agree with executable
truth.

The existing live receipt is invalidated as closure evidence by F2-F4.
Repair must first make focused and full non-live suites green, then rerun the
disposable PostgreSQL 16 proof and exactly one fresh real-provider proof.
Fresh sanitized receipts replace the invalidated evidence before re-review.

## Boundary

No production behavior beyond the original SPEC changes. Integration Edge,
canonical-message contract, migrations, operations-domain, auth/JWT,
frontend, dependency manifests, CVF core, file-size debt registry and prior
tranche receipts remain protected.

Repair is prohibited until the matching SPEC Amendment 2, Work Order
Amendment 2, authorization review and successor continuity acknowledgment
are committed and pushed.

