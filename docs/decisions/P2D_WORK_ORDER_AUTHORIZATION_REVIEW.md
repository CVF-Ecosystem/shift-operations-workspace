# Authorization Review — P2-D Offline Queue and Polling Realtime

- Tranche: `P2D-OFFLINE-REALTIME-2026-08-02`
- Risk: `R2`
- Source baseline: `1f3646aba7d2bc4becea6c156475360331133f29`
- Reviewer: independent authorization reviewer, separate from later worker
- Final disposition: `REVIEW_PASS / APPROVED`
- BUILD: `BLOCKED UNTIL PUSHED PACKAGE, SEPARATE PRE-BUILD CHECKPOINT AND G6`

## Evidence reviewed

The reviewer compared INTAKE, ADR, SPEC and Work Order with current PWA shell,
offline storage, mutation transport/control, React console, accessibility
specs, real-browser harness, live evidence runners and protected backend/API/
migration/package boundaries. No implementation, browser, PostgreSQL or
provider run was claimed during authorization.

Mechanical review confirms exactly 49 numbered and 49 unique BUILD paths.
NEW/existing labels match the tree. The set includes the existing accessibility
specs, connection-health README and shared C3c evidence runner/test whose old
zero-queue assumptions must be parameterized. Backend, OpenAPI, migration,
dependency/lockfile, CI, roadmap and continuity paths remain protected.

## Findings closed without waiver

### `P2D-AUTH-F1 KNOWN_SUCCESS_MISCLASSIFIED_AS_OUTCOME_UNKNOWN`

HTTP mutation success followed by refresh failure is now non-replayable
`applied_stale`, not transport-ambiguous `outcome_unknown`. A committing fresh
read is required before removal/success display.

### `P2D-AUTH-F2 MANUAL_RETRY_STATE_MACHINE_UNDEFINED`

Only `pending` dispatches. Crash-left `replaying` becomes `outcome_unknown`.
Blocked/ambiguous commands never return to pending or rewrite recorded CAS;
after fresh read the operator discards and creates a new live action.

### `P2D-AUTH-F3 EXACT_CEILING_INSUFFICIENT`

The ceiling was expanded from 44 to exact 49 paths to include both existing
accessibility specs, connection-health documentation and shared C3c runner/
test semantics. C3c/C3d retain queue-prohibited evidence; P2-D requires the
bounded queue to be exercised and cleaned.

### `P2D-AUTH-F4 STRICT_STORED_SCHEMA_INCOMPLETE`

The contract now fixes schema version `1`, five exact states, state-specific
`lastErrorKind`, bounded ephemeral malformed-entry ids, fixed disclosure-safe
reasons and metadata-only `actorUserId` excluded from network bodies.

### `P2D-AUTH-F5 SINGLE_FLIGHT_SCOPE_OVERCLAIM`

Single-flight is explicitly per tab. Two same-actor tabs may race; recorded CAS
permits at most one commit and visibly blocks the loser. Cross-tab/request
exactly-once is not claimed, and real-browser evidence covers the race.

### `P2D-AUTH-REREVIEW-F6 SERVER_FAILURE_UNDEFINED`

ADR, SPEC and Work Order now agree that HTTP 5xx/server responses become
`blocked/server`, halt FIFO and prohibit automatic retry or CAS rewriting.

## Final disposition

Independent re-review returned `REVIEW_PASS`; no authorization finding or
waiver remains. The exact 49-path Work Order is necessary and sufficient for
the bounded P2-D BUILD against current source.

This receipt does not start BUILD or permit a provider call. The authoring
package must be committed and pushed, followed by a separate clean pre-BUILD
checkpoint and fresh G6. P2-D, the full-shift exit gate and Phase 2 remain open.
