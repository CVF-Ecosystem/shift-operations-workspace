# Authorization Review — P2-C C3b1 Work Order

- Review target: `docs/work_orders/P2C_MUTATION_FULL_UI_C3B1_WORK_ORDER.md`
- Tranche: `P2C-MUTATION-FULL-UI-2026-07-31`
- Checkpoint: `C3b1`
- Risk: `R2`
- Reviewer role: independent `AUTHORIZATION_REVIEWER`
- Final disposition: `REVIEW_PASS / APPROVED`
- BUILD status: `BLOCKED UNTIL PUSHED PRE-BUILD CHECKPOINT AND G6 PASS`

## Evidence reviewed

The reviewer compared the Work Order and feasibility DESIGN/SPEC amendments
with current source, pushed C3a2 `95b66b1`, the parent reviewed DESIGN/SPEC,
R11/R15-R17/R34-R37 and AC-11/AC-16..AC-18/AC-29..AC-34.

Mechanical inspection confirmed exactly 34 numbered BUILD paths, 34 unique,
with all existing/NEW classifications matching source. There is no wildcard,
conditional allowance, reserve, optional truth surface or self-review path.

## Findings and repairs

### `C3B1-WO-REV-F1 EXACT_SET_MISMATCH`

The draft omitted existing frontend `api.test.ts`, whose network expectation
must change to `outcome_unknown` and which must prove 401 session clearing. It
instead listed the unchanged incident OpenAPI contract, which would require a
synthetic edit. Repair exchanged those paths without changing the 34 ceiling.

Disposition: `CLOSED_WITHOUT_WAIVER`.

### `C3B1-WO-REV-F2 READ_PERMISSION_UNDEFINED`

The draft required a coarse read action that does not exist in the current
permission map. Parent R11 requires authenticated, assignment-scoped reads.
Repair fixes list admission to verified authentication then ACTIVE assignment;
readiness alone applies the requested canonical governed action before target
resolution and assignment.

Disposition: `CLOSED_WITHOUT_WAIVER`.

### `C3B1-WO-REV-F3 READINESS_SEMANTICS_INCOMPLETE`

Repair makes readiness deterministic and implementation-independent: maximum
bipartite matching, distinct approver per seat, preserved seat multiplicity
and order, requester independence, no premature confirmer/self-approval rule,
and exact current-Report behavior. Non-current Report is sanitized 409 after
action permission and assignment; current binding is derived regardless of
lifecycle because readiness is not lifecycle admission.

Disposition: `CLOSED_WITHOUT_WAIVER`.

### `C3B1-WO-REREV-F1 TASK_READINESS_RECORD_TYPE_CONTRADICTS_RUNTIME`

The repaired draft initially named `TaskCreationIntent/task.create`, but
durable runtime receipts use canonical `Task/task.create` with `record_id`
equal to the stored TaskCreationIntent id. ADR, SPEC and Work Order now use
that exact contract, and the reviewer scope includes R37.

Disposition: `CLOSED_WITHOUT_WAIVER`.

## Final disposition and boundary

Independent final re-review returned `REVIEW_PASS`. The C3b1/C3b2 split closes
the frontend-source contradiction without waiver; C3b1 allows only browser
transport/type/test source, no React feature source. The exact 34-path set is
necessary and sufficient for the bounded read/readiness/transport claim, with
no identified omission or synthetic path.

Under the operator's standing Work Order delegation, C3b1 is approved intact.
This approval does not itself authorize BUILD. This authorization package must
be committed and pushed, then a separate continuity checkpoint must record the
exact pre-BUILD parent and pass G6 before any source edit. C3b2-C3d remain
blocked. No Claude CLI/MCP, BUILD, provider call, staging, implementation
commit, push or FREEZE occurred during review.
