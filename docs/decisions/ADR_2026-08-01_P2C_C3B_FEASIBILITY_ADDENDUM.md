# ADR Addendum — P2-C C3b Contract Feasibility

- Tranche: `P2C-MUTATION-FULL-UI-2026-07-31`
- Checkpoint: `C3b`
- Phase: `DESIGN AMENDMENT`
- Risk: `R2`
- Status: `REVIEW_PASS — CLOSED_WITHOUT_WAIVER`

## Findings

### `P2C-C3B-WO-FEAS-F1 FRONTEND_CONTRACT_BOUNDARY_CONTRADICTION`

The reviewed DESIGN says C3b changes no frontend source, while SPEC R15-R16
requires browser TypeScript DTO agreement and a request primitive supporting
typed bodies, queries, abort, controlled errors and no retry. Those
requirements cannot be proven without changing transport/type source.

### `P2C-C3B-WO-FEAS-F2 BACKEND_CHECKPOINT_BLAST_RADIUS`

C3b currently combines two independently revertible concerns:

1. four assignment-scoped reads plus approval-readiness and browser transport;
2. a CustomerRequest migration/version plus optimistic preconditions across
   nine service/router families and their existing fixtures/runners.

The second concern necessarily fans out across legacy direct-service tests and
live runners because missing preconditions must fail closed. Combining both
would make exact-path review and rollback needlessly broad.

### `P2C-C3B-WO-FEAS-F3 READ_CONTRACT_AMBIGUITY`

The SPEC says `Event/event.confirm`, while the existing approval contract's
canonical stored record type is `OperationalEvent`. It also leaves ordering
and the meaning of readiness insufficiently exact for cross-backend proof.

## Decision

Split C3b into two separately authorized, reviewed, committed and pushed
sub-checkpoints:

1. **C3b1 — browser reads, approval readiness and transport contract**;
2. **C3b2 — CustomerRequest version and atomic mutation preconditions**.

C3b1 may change only non-React frontend transport/type/test files. It may not
change a component, feature, styling, package manifest, lockfile or build
configuration and makes no UI-completion claim. This is the narrow correction
to the DESIGN's “no frontend source” sentence: it means no React feature
source, not no browser contract source.

C3b2 begins only after C3b1 independent `REVIEW_PASS` and push. It owns R12-R14
and the mutation half of R15-R17. C3c remains blocked until both C3b1 and C3b2
are reviewed and pushed.

The canonical readiness pair is
`OperationalEvent/event.confirm`, alongside
`Task/task.create` (whose `record_id` is the stored TaskCreationIntent id),
`Incident/incident.acknowledge` and
`Report/report.approve`. Readiness means approval quorum readiness for the
stored target's current binding only; it is not lifecycle, capability or
mutation authorization. A required role seat is satisfied only by a current
receipt whose approver still exists, is active and presently has authority
for that seat. Readiness uses deterministic maximum bipartite matching: each
distinct approver may fill at most one seat; repeated role seats retain their
multiplicity and declared order. `ready` is true exactly when all seats are
matched. It is requester-independent and deliberately does not apply the
later confirmer/self-approval rule; mutation remains authoritative and
re-evaluates that rule. For Report, the exact `report_id` must be current;
after requested-action permission and assignment admission, a historical or
non-current Report returns sanitized 409. A current Report's stored binding
is used regardless of lifecycle because readiness is not lifecycle admission.
Payload digests, approver identities and credentials are excluded.

Canonical list order is:

- Message: `(created_at, message_id)` ascending;
- Task: `(created_at, task_id)` ascending;
- CustomerRequest: `(received_at, request_id)` ascending.

Exactly 0-500 matching records return normally; 501 or more returns controlled
422 without truncation.

## Boundary

No requirement, acceptance criterion or final P2-C claim is removed. C3b1
makes no new AI/agent-governance claim and therefore performs no provider
call; it consumes the already-reviewed assignment and approval authority and
proves only read/readiness/transport contract behavior on the authorized
backends. C3b2, C3c, C3d, P2-D and Phase-2 completion remain unauthorized.
