# SPEC Amendment 7 — P2-C C3b Feasibility and Split

- Tranche: `P2C-MUTATION-FULL-UI-2026-07-31`
- Checkpoint: `C3b`
- Risk: `R2`
- Status: `REVIEW_PASS`

## Amendment

Add `R34 — C3b sub-checkpoint separation`:

> C3b SHALL execute as C3b1 then C3b2, each with an exact-path Work Order,
> independent review, commit and push. C3b1 owns R11, the read/readiness and
> browser-transport portions of R15-R17. C3b2 owns R12-R14 and the mutation-
> precondition portions of R15-R17. C3b2 cannot start before C3b1 is reviewed
> and pushed; C3c cannot start before both are reviewed and pushed.

Add `R35 — C3b1 exact read and readiness contract`:

> The exact supported readiness pairs are
> `OperationalEvent/event.confirm`, `Task/task.create` (with `record_id` equal
> to the stored TaskCreationIntent id), `Incident/incident.acknowledge` and
> `Report/report.approve`. The server MUST
> resolve the stored target, its shift, current version/risk/digest binding and
> require current ACTIVE assignment. Required roles come from current policy.
> A seat is satisfied only by a matching durable receipt whose approver is a
> currently active user with current authority for that seat. Deterministic
> maximum bipartite matching MUST retain required-seat order and multiplicity;
> one distinct approver may fill at most one seat. Readiness is requester-
> independent and MUST NOT evaluate the later confirmer/self-approval rule.
> `ready` means every required seat is matched; it does not assert lifecycle,
> capability or mutation authority. For Report, the exact target MUST be
> current; after requested-action permission and assignment, a non-current
> Report is sanitized 409. A current Report binding is derived regardless of
> lifecycle. The response exposes only record type/id, action,
> target version, risk class, ready, required-role names and satisfied-role
> names. It exposes no digest, receipt id, approver identity or credential.

Add `R36 — C3b1 deterministic bounds and frontend boundary`:

> Message order is `(created_at, message_id)`, Task order is
> `(created_at, task_id)`, and CustomerRequest order is
> `(received_at, request_id)`, all ascending and cross-backend equivalent.
> 0-500 matches return completely; 501 or more returns sanitized 422 with no
> truncation. C3b1 may change only frontend transport, feature-owned DTO and
> transport-test source needed by R15-R16. React components/features, styles,
> dependency manifests, lockfiles and build configuration MUST have zero diff.
> The request primitive clears session on 401, maps 403/404/409/422 to the
> controlled categories, maps ambiguous transport failure to outcome-unknown,
> never logs token/body/raw transport, and never retries automatically.

Add `R37 — C3b1 admission order`:

> Each list uses verified authentication followed directly by current ACTIVE
> assignment; no nonexistent read-action permission is invented. Readiness
> first validates a canonical pair, applies `require_action` for that requested
> action, resolves the stored target, then requires current ACTIVE assignment.
> Missing/inaccessible resources retain the common sanitized 404 boundary.

Acceptance allocation is clarified without renumbering:

- C3b1 owns AC-11, the read/readiness/transport parts of AC-16..AC-18, and
  applicable AC-29..AC-34 evidence.
- C3b2 owns AC-12..AC-15, the mutation-precondition parts of AC-16..AC-18,
  and applicable AC-29..AC-34 evidence.
- AC-32 applies independently to each exact sub-checkpoint changed set.

R1-R33 and AC-01..AC-35 remain mandatory. This amendment grants no BUILD,
provider-call, stage, commit, push, self-review or FREEZE authority.
