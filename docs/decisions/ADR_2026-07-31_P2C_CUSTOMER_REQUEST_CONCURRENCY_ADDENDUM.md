# DESIGN Addendum — P2-C Customer Request Concurrency

ID: `P2C-CUSTOMER-REQUEST-CONCURRENCY-ADDENDUM-2026-07-31`
Parent: `ADR-P2C-MUTATION-FULL-UI-2026-07-31`
Finding: `P2C-SPEC-FEAS-F1 CUSTOMER_REQUEST_NO_VERSION`
Status: `DESIGN_ADDENDUM_REVIEW_PASS`

## Finding

SPEC feasibility inspection found that `CustomerRequest` is the only mutable
lifecycle aggregate selected for the P2-C UI that has no concurrency version:

- the canonical model has no `version`;
- migration 002 and `operations_ledger.tables.customer_requests` have no
  version column;
- transition mutates status without an expected-version precondition.

The parent ADR requires safe mutation concurrency but only named “existing
versioned aggregates.” Leaving CustomerRequest outside that rule would make
the operator mutation claim internally inconsistent.

## Decision

C3b backend contract readiness adds `CustomerRequest.version`:

- integer, non-null, default 1, check `version >= 1`;
- migration backfills every existing row deterministically to 1;
- canonical model, SQL table mapping, row builders, InMemory and SqlLedger
  preserve the same value;
- create returns/persists version 1;
- transition requires caller `expected_version`, compares inside the atomic
  service transaction, increments exactly once on success and returns 409
  with zero mutation/audit on mismatch;
- OpenAPI, JSON contract, TypeScript DTO and schema-parity tests include the
  required response field and transition precondition.

The additive response field and newly required transition precondition are an
intentional pre-release contract tightening. Omission of `expected_version`
returns controlled 422. No route silently performs an unconditional write.

## Checkpoint and boundary

This repair belongs to C3b, not C3a. C3a remains only the assignment
authorization foundation. The four-checkpoint order does not change.

This addendum does not add risk/evidence/approval semantics to customer
requests, make unbound (`shift_id = null`) requests visible in the shift
console, authorize BUILD, or claim exactly-once/offline mutation.

## Required evidence carried to SPEC

- two-direction schema parity and migration reapply;
- existing-row backfill;
- cross-backend create/transition version parity;
- stale and missing precondition refusals with zero partial write/audit;
- OpenAPI/contract/browser DTO agreement;
- disposable PostgreSQL proof if C3b is authorized.

## Next governed move

Author the parent tranche SPEC including this addendum. No Work Order or BUILD
authority exists.
