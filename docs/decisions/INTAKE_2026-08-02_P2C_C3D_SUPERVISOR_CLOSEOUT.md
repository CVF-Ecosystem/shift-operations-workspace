# INTAKE — P2-C C3d Supervisor Closeout

- ID: `INTAKE-P2C-C3D-SUPERVISOR-CLOSEOUT-2026-08-02`
- Parent tranche: `P2C-MUTATION-FULL-UI-2026-07-31`
- Checkpoint: `C3d`
- Control-chain phase: `INTAKE`
- Risk: `R2`
- Status: `INTAKE_COMPLETE`

## 1. Authorized request boundary

The operator selected the sole next governed move: fresh C3d supervisor-
closeout `INTAKE -> DESIGN -> SPEC -> exact-path WORK_ORDER`. C3c is settled
at `65b10d25078dce57fca6ffc43eb2e144f3ab1789`, independently
`REVIEW_PASS`, pushed, and `CLOSED_BOUNDED`. No C3c BUILD authority or open
changed set carries forward.

This authoring round may create C3d governance artifacts and synchronize
continuity. It may not edit implementation source, run a provider, claim C3d
or P2-C complete, begin P2-D, run the full-shift exit gate, stage, commit,
push, review its own authorization, or FREEZE.

## 2. Verified starting truth

- `HEAD == origin/main == 8359f3f11bfafb1debd8d64ca8a8f5468adfbff5` and the
  worktree was clean before this intake.
- Workspace doctor passed 24 checks with only the bounded legacy catalog-kit
  warning.
- The React console has the complete C3c operator surface, shared ephemeral
  mutation control, typed no-retry transport and real Chromium harness.
- Existing FastAPI routes already provide staffing target/user/assignment
  reads and mutations, event confirm/correction, approval-receipt creation
  for both Event actions plus Task/Incident/Report targets,
  incident acknowledge, handover review/acknowledge, Report approve and
  approval revocation through the existing successor-version route, and
  Shift freeze.
- Operational shift reads remain assignment-scoped. Staffing discovery is a
  distinct supervisor-only control-plane exception and must stay separate.
- `useOperationsData` currently retains only confirmed events for the UI, so
  it cannot yet present an unconfirmed event to the supervisor.
- Incoming handovers have no separate destination list route. C3d must use
  the existing source-shift list and prove destination assignment at submit;
  it may not invent destination-wide discovery.
- Task-creation-intent approval has no list endpoint. A bounded manual stored
  intent-id target is permitted only if the backend still resolves the target,
  derives its scope/digest/version and returns enumeration-safe refusal.

## 3. Intake findings

### `C3D-INTAKE-F1 STAFFING_AND_OPERATIONAL_SCOPE_MUST_NOT_COLLAPSE`

Supervisor-wide staffing discovery is not authority to read or mutate the
shift. The UI needs separate staffing state and operational selected-shift
state; assignment changes must refresh both without client-side role ranking.

### `C3D-INTAKE-F2 SUPERVISOR_TARGET_DISCOVERY_IS_INCOMPLETE`

The console hides unconfirmed events, has no task-intent list and has no
incoming-handover list. C3d must bound target selection to truthful existing
reads plus an explicit stored task-intent id, without adding a backend route
or claiming destination-only discovery.

### `C3D-INTAKE-F3 REPORT_REVOCATION_ROUTE_IS_OVERLOADED`

The backend implements approval revocation by creating a successor from an
`APPROVED` Report through `POST /reports/{id}/versions`; there is no separate
revoke endpoint. The frontend must reflect this exact lifecycle/permission
contract and require a reason, `expected_version` and `expected_status`.

### `C3D-INTAKE-F4 FINAL_GOVERNANCE_PROOF_IS_NOT_C3C_EVIDENCE`

C3c made no provider claim. C3d's bounded P2-C governance claim requires a
fresh sanitized real-provider receipt after the complete refusal matrix has
observed zero provider calls and a durable assigned authorized closeout path
has been verified.

### `C3D-INTAKE-F5 PHASE_BOUNDARIES_REMAIN_OPEN`

C3d may close only P2-C after independent BUILD review/push and a separate C4
truth sync. P2-D and the full-shift exit gate remain later tranches; Phase 2
must remain `IN PROGRESS`.

## 4. Acceptance boundary for DESIGN

DESIGN must resolve F1-F5, enumerate every included supervisor control and
target source, preserve server authority and no-retry/offline boundaries,
define real-browser plus real-provider evidence, and split BUILD from C4
truth synchronization. No implementation or BUILD authorization exists.
