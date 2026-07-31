# P2-C Mutation and Full UI — DESIGN Review

Review ID: `P2C-MUT-DESIGN-REVIEW-2026-07-31`
Reviewed commit: `88a1573df08485ce0bfbfb23e964bdd5cf7d212b`
Reviewer role: `REVIEWER`
Disposition: `REVIEW_PASS_AFTER_REPAIR`

## Scope reviewed

- `docs/decisions/INTAKE_2026-07-31_P2C_MUTATION_FULL_UI.md`;
- `docs/decisions/ADR_2026-07-31_P2C_MUTATION_FULL_UI.md` at the reviewed
  commit and its repaired form in this review round;
- current FastAPI routes, Ledger Protocol/backends, migrations, frontend API,
  DTO/session code, roadmap and CVF control semantics.

No source, test, schema or runtime behavior was changed. No provider call,
secret read, Docker/PostgreSQL run or BUILD occurred.

## Findings and repairs

### P2C-DESIGN-REV-F1 — UI_READ_SURFACE_INCOMPLETE

The first ADR named mutation controls but omitted the absent history/readiness
APIs needed to use them safely. Message list, full task/customer-request
history and approval/readiness state are not currently browser-callable.

Repair: D6 now assigns these bounded assignment-scoped APIs to a dedicated
C3b backend-contract checkpoint with deterministic limits and sanitized
responses. Existing reads remain reused.

Status: `CLOSED_WITHOUT_WAIVER`.

### P2C-DESIGN-REV-F2 — LEGACY_SHIFT_LOCKOUT_UNDECIDED

The assignment migration could neither infer truthful memberships for existing
shifts nor leave recovery unspecified.

Repair: existing shifts receive no fabricated assignment and fail closed for
operational access; the narrow supervisor staffing control plane can discover
minimal shift identity and establish assignments. This recovery path requires
deployment evidence.

Status: `CLOSED_WITHOUT_WAIVER`.

### P2C-DESIGN-REV-F3 — AUTHORIZATION_CHECKPOINT_TOO_BROAD

The first C3a combined migration/cross-route assignment enforcement with all
new browser API contracts. That repeated the intake's unsafe-breadth problem.

Repair: four checkpoints replace three: C3a assignment foundation, C3b backend
contract readiness, C3c operator UI, C3d supervisor closeout UI. Each is
independently reviewed, committed and pushed before the next begins.

Status: `CLOSED_WITHOUT_WAIVER`.

### P2C-DESIGN-REV-F4 — NULL_SHIFT_CUSTOMER_REQUEST_UNRESOLVED

`CustomerRequest.shift_id` is nullable. “Every resource resolves a shift” was
false for existing unbound requests.

Repair: this shift console includes only selected-shift-bound requests.
Unbound customer-inbox workflow remains outside P2-C and receives no
assignment or full-UI claim.

Status: `CLOSED_WITHOUT_WAIVER`.

### P2C-DESIGN-REV-F5 — BREAKING_PRECONDITION_NOT_DECLARED

Required `expected_version`/Report `expected_status` changes would reject old
request shapes, but the first ADR did not acknowledge or govern that contract
break.

Repair: D4 explicitly makes this a pre-release tightening, requires controlled
422 for omitted preconditions and requires SPEC/OpenAPI enumeration of every
affected versus unchanged route.

Status: `CLOSED_WITHOUT_WAIVER`.

## Re-review

The repaired ADR:

- resolves intake F1-F6 without misusing provider-placement `data_scope`;
- defines a truthful single-workspace, assignment-scoped claim;
- provides a recoverable but fail-closed legacy migration path;
- separates authorization, backend contracts and two UI responsibility sets;
- bounds nullable customer requests and HTTP compatibility truthfully;
- keeps P2-D, tenant isolation, P5-A and Phase-2 exit proof outside scope.

No unresolved DESIGN finding remains. This review authorizes SPEC authoring
only. It does not authorize a Work Order, BUILD, provider call, stage, commit
of implementation, review bypass or FREEZE.

## Next governed move

Transition to `SPEC_AUTHOR` and write testable requirements/acceptance criteria
for the repaired four-checkpoint design. The SPEC itself requires independent
review before Work Order authoring.
