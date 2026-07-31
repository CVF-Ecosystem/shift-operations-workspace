# Agent Handoff — P2-C Mutation and Full UI

## Disposition

- Tranche: `P2C-MUTATION-FULL-UI-2026-07-31`
- Control-chain phase: `WORK_ORDER`
- Roadmap target: remaining P2-C mutation/full UI and authorization boundary
- Risk: `R2`
- Active role: `WORK_ORDER_AUTHOR`
- Status: `C3A_FANOUT_AMENDMENT_REVIEW_PASS — C3A1_WORK_ORDER_NEXT`

## Settled predecessor

P2-R is `FREEZE / CLOSED_BOUNDED`:

- C3 `18e24e58e2bda83e18be21d5d25ad50c4b0fa24e` contains exactly 59
  authorized paths and is independently `REVIEW_PASS`/pushed;
- C4 `c738193ee0933db1799079fe98b8c77a635f2826` synchronizes closure truth;
- `HEAD == origin/main == c738193ee0933db1799079fe98b8c77a635f2826` and the
  worktree was clean before this intake;
- no P2-R DESIGN/SPEC/WORK_ORDER/BUILD authority carries forward.

Do not reopen or batch P2-R into this tranche.

## Canonical intake

`docs/decisions/INTAKE_2026-07-31_P2C_MUTATION_FULL_UI.md`

The intake records six unresolved findings:

- `P2C-MUT-INTAKE-F1 AUTHORIZATION_FOUNDATION_ABSENT`;
- `P2C-MUT-INTAKE-F2 MUTATION_BREADTH_UNBOUNDED`;
- `P2C-MUT-INTAKE-F3 CLIENT_CONTRACT_INCOMPLETE`;
- `P2C-MUT-INTAKE-F4 PRINCIPAL_CAPABILITY_VIEW_ABSENT`;
- `P2C-MUT-INTAKE-F5 PHASE_BOUNDARY_COLLISION`;
- `P2C-MUT-INTAKE-F6 END_TO_END_EXIT_PROOF_IS_LATER`.

## Verified source boundary

- P2-C read slice remains settled at C3a `fe2f312` and C3b `e24905f`.
- Frontend performs authenticated reads only; its request helper is GET-only
  except login, and no mutation controls exist.
- Backend mutation routes exist across the operational verticals, but no
  assignment/tenant registry or load-bearing operational data-scope check
  exists.
- Browser session stores only the bearer token and has no server-backed
  principal/capability view.
- Offline queue/realtime remain P2-D; Report rendering/export remains P5-A.

No source, test, schema, catalog or roadmap status changed during intake. No
provider call, secret read, Docker/PostgreSQL run, stage, BUILD, review or
FREEZE occurred.

## Governance boundary

DESIGN must resolve F1-F6 and split authorization foundation, backend
contract work and React mutation UI into independently reviewable/revertible
units wherever one checkpoint would be unsafe. Frontend may reflect server
authority but never enforce it.

This tranche does not yet claim assignment, tenant/data-scope enforcement,
full UI, P2-C completion, P2-D or Phase-2 completion.

## Next governed move

Transition explicitly to `SPEC_AUTHOR` for SPEC feasibility and authoring.
No WORK_ORDER or BUILD authority exists.

## Tranche-transition acknowledgment

On 2026-07-31 the orchestrator re-read the manifest, policy, canonical
continuity, active P2-R handoff, implementation truth, catalog, roadmap and
public-core instructions; verified P2-R C4 at clean pushed `c738193`; and
opened only this fresh INTAKE. No authority was inherited.

## DESIGN disposition

Canonical ADR:

`docs/decisions/ADR_2026-07-31_P2C_MUTATION_FULL_UI.md`

The design resolves intake F1-F6 by:

- retaining a truthful single-workspace boundary and rejecting fake tenant
  isolation or misuse of provider-placement `data_scope`;
- adding server-owned shift assignment/resource scope;
- adding advisory server capabilities while rechecking every backend gate;
- requiring expected-version checks and no automatic mutation retry;
- defining exact operator and supervisor vertical matrices;
- separating P2-D and the later Phase-2 exit run;
- splitting future BUILD into C3a assignment foundation, C3b backend contract
  readiness, C3c operator UI and C3d supervisor closeout UI, each independently
  reviewed/pushed.

Initial review found `P2C-DESIGN-REV-F1..F5`; all were repaired without
waiver and re-reviewed in:

`docs/decisions/P2C_MUTATION_FULL_UI_DESIGN_REVIEW.md`.

Final DESIGN disposition: `REVIEW_PASS_AFTER_REPAIR` for SPEC authoring only.
The repaired checkpoint order is C3a assignment foundation → C3b backend
contract readiness → C3c operator UI → C3d supervisor closeout UI.

Next move: author SPEC. No WORK_ORDER or BUILD authority exists.

## Pre-SPEC feasibility addendum

Source inspection found `P2C-SPEC-FEAS-F1 CUSTOMER_REQUEST_NO_VERSION`:
CustomerRequest is lifecycle-mutable but has no model/database version, so the
DESIGN concurrency rule could not cover it truthfully.

The reviewed repair is:

- `docs/decisions/ADR_2026-07-31_P2C_CUSTOMER_REQUEST_CONCURRENCY_ADDENDUM.md`;
- `docs/decisions/P2C_CUSTOMER_REQUEST_CONCURRENCY_ADDENDUM_REVIEW.md`.

Disposition: `CLOSED_WITHOUT_WAIVER / REVIEW_PASS`. C3b must add/backfill
CustomerRequest version and require expected-version transition semantics.
Four-checkpoint order is unchanged. SPEC authoring is now permitted; no Work
Order or BUILD authority exists.

## SPEC disposition

Canonical SPEC:

`docs/specs/P2C_MUTATION_FULL_UI_SPEC.md`

It defines R1-R29 and AC-01..AC-35 across four gated checkpoints, including
assignment route coverage, legacy recovery, CustomerRequest version backfill,
exact mutation-precondition matrix, real operator/supervisor UI verticals,
browser/PostgreSQL/provider evidence and bounded closure truth.

Initial SPEC review found `P2C-SPEC-REV-F1..F5`; all were repaired without
waiver and re-reviewed in:

`docs/decisions/P2C_MUTATION_FULL_UI_SPEC_REVIEW.md`.

Final SPEC disposition: `REVIEW_PASS_AFTER_REPAIR` for exact-path Work Order
authoring only. No Work Order has been approved and BUILD remains unauthorized.

## Work Order feasibility and C3a fan-out amendment

Exact-path feasibility found `P2C-WO-FEAS-F1
C3A_ROUTE_ENFORCEMENT_TEST_FANOUT`: the original C3a combines new assignment
storage/staffing/bootstrap with enforcement across 24 principal-bearing
production paths and at least 38 existing test/support paths, while multiple
required seams are already at 296-300 physical lines.

The reviewed repair is:

- `docs/decisions/ADR_2026-07-31_P2C_C3A_FANOUT_ADDENDUM.md`;
- `docs/specs/P2C_MUTATION_FULL_UI_SPEC_AMENDMENT_1.md`;
- `docs/decisions/P2C_C3A_FANOUT_AMENDMENT_REVIEW.md`.

Disposition: `CLOSED_WITHOUT_WAIVER / REVIEW_PASS`. C3a is now C3a1
assignment persistence/staffing/bootstrap followed by C3a2 route-wide
enforcement and legacy fixture migration. C3b-C3d keep their names and order.
Every final requirement remains mandatory.

Next move: author, independently review and approve the exact-path C3a1 Work
Order under the operator's standing delegation. BUILD/provider calls remain
unauthorized; Claude must be handed the later prompt manually and may not be
called through CLI.

## C3a1 Work Order authorization

The exact-path Work Order is:

`docs/work_orders/P2C_MUTATION_FULL_UI_C3A1_WORK_ORDER.md`.

Authorization review:

`docs/decisions/P2C_C3A1_WORK_ORDER_AUTHORIZATION_REVIEW.md`.

The 48-path BUILD ceiling has no wildcard/reserve or self-review path. Review findings
`P2C-C3A1-WO-REV-F1..F2` closed without waiver. Under the operator's standing
delegation the Work Order is `REVIEW_PASS / APPROVED`.

Next move after this authorization checkpoint is pushed: create and push a
separate four-surface pre-BUILD continuity checkpoint naming the exact parent,
manual external worker, independent Codex reviewer, G6-next status and return
token. No source edit/provider call before G6 passes.

## C3a1 pre-BUILD checkpoint

- Authorization commit: `1b0862fa756281166c270b573794cd2faed0eb31`
  (`HEAD == origin/main` before this sync).
- C3a1 implementation parent: this four-surface pre-BUILD commit itself; its
  exact pushed hash is obtained from `git rev-parse HEAD` after commit and MUST
  equal `origin/main` before G6 or any BUILD edit.
- Worker: external `IMPLEMENTATION_WORKER`, reached only through the
  operator's manual prompt transfer; no Claude CLI/MCP control call.
- Reviewer/Commit Steward: Codex, independent from implementation.
- Authorized ceiling: exactly 48 unique BUILD paths in
  `P2C_MUTATION_FULL_UI_C3A1_WORK_ORDER.md`; zero wildcard/reserve/self-review
  path.
- G6: `NEXT_MANDATORY_GATE`, not yet run or claimed by this checkpoint.
- Worker prohibition: no stage, commit, push, self-review or FREEZE.
- Required return token:
  `READY_FOR_INDEPENDENT_P2C_C3A1_BUILD_REVIEW`.

After G6 passes, only C3a1 BUILD is authorized. C3a2/C3b/C3c/C3d remain
blocked. Any needed path outside the ceiling returns
`BLOCKED_WORK_ORDER_CEILING` without editing it.

## C3a1 BUILD ceiling blocker and Amendment 1

Worker returned `BLOCKED_WORK_ORDER_CEILING` with an unstaged partial BUILD.
Independent inspection found `P2C-C3A1-BUILD-BLOCK-F1`: the new persisted-
creator invariant breaks both real legacy runners that call
ShiftService.create, but their scripts were omitted from the 48-path ceiling.
A test-only ledger-constructor monkeypatch would hide rather than repair this
regression. Four authorized test hosts also exceeded 300 lines, but all have
in-ceiling line-neutral repairs.

Reviewed amendment artifacts:

- `docs/decisions/ADR_2026-07-31_P2C_C3A1_LEGACY_RUNNER_CEILING_ADDENDUM.md`;
- `docs/specs/P2C_MUTATION_FULL_UI_SPEC_AMENDMENT_2.md`;
- `docs/work_orders/P2C_MUTATION_FULL_UI_C3A1_WORK_ORDER_AMENDMENT_1.md`;
- `docs/decisions/P2C_C3A1_CEILING_AMENDMENT_1_AUTHORIZATION_REVIEW.md`.

Disposition: `REVIEW_PASS / APPROVED`. Ceiling is exactly 50 paths after
adding only the shift-create and message-admission live runner scripts. No
other authority changes. This amendment checkpoint must be pushed, then a
separate four-surface resume checkpoint becomes the C3a1 parent. Worker diff
remains unstaged; no BUILD commit/provider rerun occurred during review.

## C3a1 Amendment 1 resume checkpoint

- Amendment authorization commit:
  `8f8d8b245957a94ca25651d57d1d1a05fcc5b2b5` (`origin/main` matched).
- Exact review/rollback parent: this four-surface resume commit itself; after
  push the worker MUST record `git rev-parse HEAD`, verify it equals
  `origin/main`, and retain the existing unstaged partial BUILD.
- Amended ceiling: exactly 50 paths; the only additions are the two named
  legacy live runner scripts.
- Mandatory repair: seed users in real runners, remove test-only masking,
  return all four named test hosts to <=300 using only authorized paths.
- Worker remains external/manual; no Claude CLI/MCP control.
- No stage/commit/push/self-review/FREEZE.
- Return token remains
  `READY_FOR_INDEPENDENT_P2C_C3A1_BUILD_REVIEW`.

C3a1 BUILD may resume. C3a2/C3b/C3c/C3d remain unauthorized.
