# P2-C Operations Console Read Slice — Authorization Review

- Review id: `P2C-READ-SLICE-AUTHORIZATION-REVIEW-2026-07-28`
- Reviewed artifact:
  `docs/work_orders/P2C_OPERATIONS_CONSOLE_READ_SLICE_WORK_ORDER.md`
- Design:
  `docs/decisions/ADR_2026-07-28_P2C_OPERATIONS_CONSOLE_READ_SLICE.md`
- Specification:
  `docs/specs/P2C_OPERATIONS_CONSOLE_READ_SLICE_SPEC.md`
- Reviewer: Codex, independent from the assigned IMPLEMENTATION_WORKER
- Risk: R2
- Disposition: **REVIEW_PASS — C3a AUTHORIZED; C3b GATED**

## Review result

The Work Order is feasible and consistent with the approved design/spec:

- C3a has an exact 23-path ceiling and is sufficient for protocol, both
  ledgers, API, contracts, PostgreSQL 16 and real-provider evidence.
- C3b has a separate exact 28-path ceiling and cannot begin before independent
  C3a review, commit/push and continuity acknowledgment.
- The existing `open_work_snapshot` seam is reused; no redundant task,
  customer-request or incident list APIs are introduced.
- JWT admission is added only to authorized reads. The permission/data-scope
  model and the parked unauthenticated `POST /shifts` finding are not silently
  changed.
- The exact Node image tag `node:22.14.0-alpine3.21` resolves in the public
  registry. Node/pnpm versions, lockfile, frozen install and CI gates are
  pinned.
- Split-file limits are machine-enforced and no debt-baseline/exception escape
  is authorized.
- Live PostgreSQL and provider evidence are mandatory for C3a; frontend-only
  C3b may use UI mocks only after the backend governance proof is accepted.
- Claude has no stage/commit/push or self-approval authority. Codex owns
  independent reruns and commits.

## Current environment note

The Docker image manifest resolved during feasibility review, but the local
Docker Desktop daemon did not answer the server-version probe. This is not a
Work Order design defect. It is an explicit pre-BUILD gate: C3a must stop as
`BLOCKED_DOCKER_UNAVAILABLE` if the daemon is still unavailable immediately
before implementation/live verification.

## Operator authority

The operator explicitly delegated independent reviewer authority and Work
Order approval to Codex. This review exercises that bounded authority. It
does not waive the control chain, the C3a/C3b split, real-provider evidence,
or independent BUILD review.

## Authorization

After this review and Work Order are committed/pushed and the separate
pre-BUILD continuity commit passes its gates, Claude may begin **C3a only** as
`IMPLEMENTATION_WORKER`.

