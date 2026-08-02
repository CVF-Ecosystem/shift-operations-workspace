# Authorization Review — P2-C C3d Work Order

- Review target: `docs/work_orders/P2C_C3D_SUPERVISOR_CLOSEOUT_WORK_ORDER.md`
- Tranche: `P2C-MUTATION-FULL-UI-2026-07-31`
- Checkpoint: `C3d`
- Risk: `R2`
- Reviewer role: operator-assigned `AUTHORIZATION_REVIEWER`, independent from
  the later external `IMPLEMENTATION_WORKER`
- Source inspected: `8359f3f11bfafb1debd8d64ca8a8f5468adfbff5`
- Final disposition: `REVIEW_PASS / APPROVED`
- BUILD status: `BLOCKED UNTIL PUSHED PRE-BUILD CHECKPOINT AND G6 PASS`

## Evidence reviewed

The review compared INTAKE, DESIGN, SPEC and Work Order with pushed C3c
closure, current React state/transport/mutation code, every used FastAPI route
and Pydantic payload, approval/readiness services, assignment and handover
scope, Report successor semantics, correction quorum, the current C3c browser
harness, pinned frontend toolchain, PostgreSQL runner targets and repository
guards.

Mechanical review found exactly 36 numbered and 36 unique BUILD paths. Every
NEW/existing classification matches the tree. No backend/domain/ledger/
database/migration/OpenAPI path is present. The current high-line frontend
hosts have bounded split paths: `App.test.tsx` is 198 lines but its C3d proof
lives in new feature tests; `OperationsConsole.tsx` is 152 lines and remains a
coordinator. No executable exception or debt is authorized.

JSON parsing, session-state, catalog, file-size, repository validation and
`git diff --check` passed after repair. The workspace doctor baseline remains
24 PASS / 1 bounded legacy catalog-kit note. No implementation test, browser,
Docker PostgreSQL run or provider call was claimed during authorization.

## Findings closed during authorization

### `C3D-WO-REV-F1 ADVISORY_CAPABILITY_FALSE_DENIAL`

The current capability response does not enumerate `approval.create`. DESIGN
previously implied every control required a matching advisory capability,
which could hide all receipt controls even though POST `/approvals` is the
authoritative route. DESIGN/SPEC/Work Order now state that capabilities are
hints only and their omission cannot become client-side refusal authority.

Disposition: `CLOSED_WITHOUT_WAIVER`.

### `C3D-WO-REV-F2 CORRECTION_APPROVAL_PAIR_OMITTED`

Correction consumes stored `OperationalEvent/event.correct` receipts for the
event's current version, while the draft listed only the four pairs supported
by the readiness GET. POST `/approvals` supports five pairs. The repaired
contract includes `event.correct`, keeps its exact three-field POST body and
requires an operational refresh without inventing unsupported readiness.

Disposition: `CLOSED_WITHOUT_WAIVER`.

### `C3D-WO-REV-F3 POSTGRESQL_MATRIX_OVERCLAIM`

`scripts/run_postgres_live_roundtrip.py` currently pins backend targets through
C3b2. C3c and C3d are frontend/evidence checkpoints with protected backend.
The repaired wording requires the runner's exact current target matrix and
byte-identical backend/runner, instead of calling nonexistent C3c/C3d backend
targets part of that matrix.

Disposition: `CLOSED_WITHOUT_WAIVER`.

### `C3D-WO-REV-F4 SELF_REVOKE_STALE_DISCLOSURE`

Refreshing after a successful self-revoke can remove the current shift from
the ordinary assigned list while a failed operational refresh leaves old
React data visible. The repaired contract requires the coordinator to clear
selection and retained operational state whenever the refreshed assigned list
omits the selected shift.

Disposition: `CLOSED_WITHOUT_WAIVER`.

## Route and contract disposition

- staffing list/assign/revoke uses the existing supervisor-only control plane;
- Event confirm/correct, Incident acknowledge, Handover review/acknowledge,
  Report approve/successor and Shift freeze all have exact stored-version or
  status preconditions in existing routes;
- destination assignment and different reviewer/receiver remain server gates;
- freeze sends only `expected_version`; retired override fields remain absent;
- approval POST accepts only the exact three caller fields and derives all
  authority/scope data server-side;
- no new dependency, backend route, schema, migration or provider integration
  is necessary for the bounded implementation.

## Final disposition

After the four repairs, the exact 36-path set is necessary and sufficient for
the bounded C3d claim against current source. Authorization review returns
`REVIEW_PASS / APPROVED`.

This review does not itself unlock BUILD. The authorization package must be
committed and pushed, then a separate clean pre-BUILD continuity checkpoint
must pin the exact parent. The external worker must pass fresh G6 before any
source edit or provider call. C3d/P2-C remain open; C4 truth sync, P2-D, the
full-shift exit gate and Phase 2 remain later work.
