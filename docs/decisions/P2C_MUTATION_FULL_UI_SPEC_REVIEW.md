# P2-C Mutation and Full UI — SPEC Review

Review ID: `P2C-MUT-SPEC-REVIEW-2026-07-31`
Reviewed commit: `4be9d0702d6db27202bf91536472ebf664899f2e`
Disposition: `REVIEW_PASS_AFTER_REPAIR`

## Findings

### P2C-SPEC-REV-F1 — STAFFING_USER_DISCOVERY_MISSING

The UI could assign only a raw user id but had no governed way to discover
active targets. R5 now requires supervisor-only `/staffing/users` with minimum
non-secret identity/role fields. `CLOSED_WITHOUT_WAIVER`.

### P2C-SPEC-REV-F2 — LIST_LIMIT_ALTERNATIVE_UNRESOLVED

R11 allowed either hard maximum or pagination, preventing exact Work Order and
tests. It now requires deterministic hard 500 and controlled 422 on the 501st
record. `CLOSED_WITHOUT_WAIVER`.

### P2C-SPEC-REV-F3 — APPROVAL_READINESS_CONTRACT_UNDERSPECIFIED

“Supported target” had no action set or response shape. R11 now fixes the four
supported record/action pairs and a digest-free readiness response.
`CLOSED_WITHOUT_WAIVER`.

### P2C-SPEC-REV-F4 — PRECONDITION_TRANSPORT_UNSPECIFIED

R13 named semantics but not whether values were body/query/header fields. It
now requires JSON bodies and enumerates exact fields by route family while
preserving deprecated freeze-field behavior. `CLOSED_WITHOUT_WAIVER`.

### P2C-SPEC-REV-F5 — REVOKE_IDEMPOTENCY_VERSION_CONFLICT

DESIGN selected bounded idempotent revoke while SPEC required expected
version, but repeat behavior was absent. R5 now distinguishes current-revoked
idempotent read/no-audit from stale pre-revoke 409. `CLOSED_WITHOUT_WAIVER`.

## Re-review result

The repaired SPEC is testable, consistent with the reviewed DESIGN and
complete enough for exact-path Work Order feasibility. R1-R29 and AC-01..
AC-35 remain numbered unchanged. No open SPEC finding or waiver remains.

This disposition authorizes Work Order authoring only. It does not approve an
unknown path ceiling, authorize BUILD/provider calls/staging/commit, or permit
checkpoint combination.
