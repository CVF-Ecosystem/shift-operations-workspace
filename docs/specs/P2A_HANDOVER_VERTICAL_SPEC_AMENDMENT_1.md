# SPEC Amendment 1 — P2-A Handover Legacy Freeze Tests

ID: `P2A-HANDOVER-SPEC-AMENDMENT-1`
Tranche: `P2A-HANDOVER-VERTICAL-2026-07-26`
Risk: R2
Status: REVIEW_PASS
Design: `docs/decisions/ADR_2026-07-26_P2A_HANDOVER_LEGACY_FREEZE_TEST_ADDENDUM.md`
Amends: `P2A_HANDOVER_VERTICAL_SPEC.md`

## Scope

This amendment supersedes only the changed-set part of parent AC-20 and adds
the two legacy-regression requirements below. Parent R1-R17 and AC-01-AC-19,
AC-21-AC-23 remain in force verbatim.

## Added requirements

### R18 — atomic freeze regression

Both atomic freeze audit-failure tests must establish a genuine acknowledged
handover before invoking freeze. The readiness check, freeze mutation, freeze
audit and report-override audit must use one unit of work. When the injected
audit failure occurs, shift status and all audit effects remain unchanged.

### R19 — frozen-parent customer-request regression

Both backends' frozen-parent setup must establish a genuine acknowledged
handover before freezing. After freeze succeeds, creating a customer request
for that shift remains rejected and no customer-request record is persisted.

The test setup must use the application-service handover lifecycle. Directly
inserting ACKNOWLEDGED state, mocking readiness, or adding a production bypass
does not satisfy R18/R19.

## Amended acceptance criteria

- **AC-20 (superseded):** C3 changes exactly the 41 paths authorized by the
  parent Work Order plus Work Order Amendment 1; protected paths have zero
  diff.
- **AC-24:** the two atomic audit-failure tests reach the injected audit
  exception only after real handover readiness and still prove rollback.
- **AC-25:** the two customer-request cases freeze through a real acknowledged
  handover and still prove frozen-parent rejection.

## Claim boundary

This amendment updates legacy test setup to the new contract. It does not
change customer-request semantics, weaken freeze, expand the handover source
set, or authorize any 42nd C3 path.

## Independent disposition

`HOV-AUTH-F4` is closed at SPEC without waiver. Codex independently approves
AC-20/AC-24/AC-25 under the delegated reviewer authority.
