# P2-C C3a Amendment 2 — Independent Authorization Review

- Review ID: `P2C-C3A-AMENDMENT-2-AUTHORIZATION-REVIEW`
- Tranche: `P2C-OPERATIONS-CONSOLE-READ-SLICE-2026-07-28`
- Risk: R2
- Role: `REVIEWER`
- Date: 2026-07-29
- Disposition: `REVIEW_PASS`

## Reviewed artifacts

1. `docs/decisions/ADR_2026-07-29_P2C_READ_API_C3A_REPAIR_SCOPE_ADDENDUM_2.md`
2. `docs/specs/P2C_OPERATIONS_CONSOLE_READ_SLICE_SPEC_AMENDMENT_2.md`
3. `docs/work_orders/P2C_OPERATIONS_CONSOLE_READ_SLICE_WORK_ORDER_AMENDMENT_2.md`

This review covers authorization feasibility only. It does not approve the
dirty C3a BUILD, does not satisfy its PostgreSQL/provider evidence gates, and
does not authorize C3b.

## Re-review findings

The first authorization review returned three findings. All three are closed
without waiver:

- `AM2-REV-F1 NON_REPRODUCIBLE_DOCUMENTED_ASSUMPTION` — closed. R23 now
  requires exactly one deterministic policy: dependency constraints that
  actually resolve reproducibly, or an environment-independent structural
  proof that removes reliance on dependency-sensitive full-document hashes.
  A floating range plus a version note is explicitly rejected.
- `AM2-REV-F2 CONTRADICTORY_LIMIT_EVIDENCE_MATRIX` — closed. ADR, SPEC and
  Work Order now require the same exact matrix: shifts, events and all three
  open-work groups at both 500 and 501 on InMemory, SQLite and disposable
  PostgreSQL 16, through the real API/backend dependency path.
- `AM2-REV-F3 AMENDMENT_1_SCOPE_WORDING_DRIFT` — closed. The artifacts now
  state accurately that Amendment 1 authorized only the event-list query
  extraction into `_event_queries.py`, not mutation extraction.

For policy R23(a), “bounded” satisfies this review only if the permitted
resolution is demonstrably deterministic for the generated OpenAPI bytes.
A range admitting multiple byte-distinct resolutions fails AC-24. Policy
R23(b) remains the alternative when dependency-sensitive hashes are removed
in favor of structural negative protection.

## Scope and feasibility

The C3a ceiling expands from 25 to exactly 29 possible implementation paths,
adding only:

```text
pyproject.toml
packages/operations-ledger/src/operations_ledger/_shift_queries.py
packages/workspace-contracts/tasks/task.schema.json
packages/workspace-contracts/customers/customer-request.schema.json
```

The existing authorized API, parity, PostgreSQL-live and runner test paths
are sufficient to host the required full limit matrix without opening a
fifth implementation path. Every touched/new Python file remains subject to
the 300-line hard guard; the worker must split only through an independently
authorized path and must stop if the matrix cannot be implemented without
compression or a new path.

The provider gate remains intentionally unresolved by this authorization:
without a real credential and an exactly-one-call PASS receipt, the worker
must stop at `BLOCKED_LIVE_PROVIDER_CREDENTIAL`. No mock evidence or
load-bearing claim is permitted.

## Review evidence

- Shift `HEAD == origin/main` before authorization commit:
  `0ac5c4d4a97b20d71ca34949e60ea9ad007886f5`.
- CVF core pin and HEAD:
  `27137db4d9aa2aea931ddd2507185d5c24943080`; core clean.
- Amendment authoring changed exactly the three requested governance files.
- The pre-existing 23 C3a BUILD paths remained unstaged.
- `git diff --check` for the three authored artifacts: PASS.
- No runtime/provider claim is made by this authorization review, so a
  provider call is neither substituted nor claimed here.

## Disposition and next move

`REVIEW_PASS`.

The four-file authorization commit consists only of the three reviewed
artifacts plus this independent review. After that commit is pushed, Claude
may transition to `REPAIR_WORKER` under the exact 29-path ceiling, close
`P2C-C3A-REV-F10` through `F19`, and stop at
`READY_FOR_INDEPENDENT_P2C_READ_API_BUILD_REVIEW`.

Codex remains the independent BUILD reviewer and commit steward. C3b remains
gated until C3a receives independent `REVIEW_PASS` and is committed/pushed.
