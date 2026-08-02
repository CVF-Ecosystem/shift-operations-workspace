# ADR — P2-C C3d Supervisor Closeout

- ID: `ADR-P2C-C3D-SUPERVISOR-CLOSEOUT-2026-08-02`
- Parent tranche: `P2C-MUTATION-FULL-UI-2026-07-31`
- Checkpoint: `C3d`
- Control-chain phase: `DESIGN`
- Risk: `R2`
- Status: `DESIGN_REVIEWED`

## 1. Context and decision

C3d consumes the reviewed parent ADR/SPEC and the pushed C3a-C3c contracts.
It adds no backend route, model, migration, ledger behavior or new permission.
It builds the supervisor presentation and evidence layer over existing server
authority, then—only after independent BUILD review/push—permits a separate C4
truth-sync decision for bounded P2-C closure.

## 2. D1 — Two deliberately separate supervisor contexts

The UI has two contexts:

1. **Staffing control plane:** calls the existing supervisor-only minimal
   staffing endpoints for all shift targets, active users and assignments.
   It does not load operational records and does not treat role text or a
   successful staffing read as operational authority.
2. **Operational closeout:** acts only on the ordinary selected shift returned
   by assignment-scoped operational reads. Capabilities are presentation
   hints; every mutation is re-authorized by the backend.

The browser will attempt the staffing reads and render the panel only on a
successful server response. It will not duplicate the backend role hierarchy.
Assign/revoke success refreshes staffing state and the assigned-shift list. It
does not silently select or expose an unassigned shift. If that refresh shows
the current operational shift is no longer assigned (including self-revoke),
the coordinator clears selection so the operational hook clears retained
records instead of leaving a stale disclosure on screen.

This resolves `C3D-INTAKE-F1`.

## 3. D2 — Exact supervisor vertical and target sources

C3d exposes only:

- minimal staffing shift/user/assignment list, assign and versioned revoke;
- event confirm for an unconfirmed event from the selected shift;
- durable approval receipt creation for the five POST-supported pairs: visible
  Event/`event.confirm`, visible Event/`event.correct`, explicit stored
  TaskCreationIntent id/`task.create`, visible Incident/
  `incident.acknowledge`, and current Report/`report.approve`; readiness is
  available only for the existing four readiness-supported pairs and is not
  invented for `event.correct`;
- incident acknowledge;
- source-shift handover review and acknowledge, with the backend independently
  requiring destination assignment for acknowledge;
- current Report approve, and approval revocation by successor creation only
  when current status is `APPROVED`, with a required bounded reason;
- shift freeze without either retired override field;
- post-freeze event correction with required reason.

The operational event collection remains complete in state; only the timeline
projects confirmed events. No destination-incoming handover discovery, task-
intent listing, raw digest, receipt identity or caller-declared authority is
invented. A manual task-intent id is merely an identifier; the backend remains
the only source for target existence, assignment, version, digest, risk and
approval scope.

This resolves `C3D-INTAKE-F2` and `C3D-INTAKE-F3`.

## 4. D3 — Lifecycle, prerequisites and refresh

The UI renders controls only for lifecycle states supported by the current
stored DTO. Advisory capabilities may annotate or suppress an action that the
server actually enumerates, but absence from that advisory list is not a
client-side authorization decision: notably, the current list has no
`approval.create` action. Direct 401/403/404/409/422 responses are
authoritative. Each control permits one in-flight request, never auto-retries,
and reuses the C3c mutation state machine:

- success and controlled conflict refresh operational reads/capabilities;
- staffing mutation refreshes staffing plus assigned-shift state;
- assignment, approval, incident, handover, Report and freeze changes refresh
  all affected presentation;
- an ambiguous outcome locks repeat until an explicit successful fresh read;
- a shift-selection change resets ephemeral target/control state.

Freeze presentation shows exact safe prerequisite categories: shift closed,
acknowledged current handover, current approved Report and current versions.
It never renders or sends `override_unimplemented_prerequisites` or
`override_reason`.

## 5. D4 — Evidence architecture

C3d reuses the pinned Playwright `1.62.1` toolchain and extends the owned C3c
harness into a parameterized C3d run. Real Chromium drives supervisor actions
against built Vite plus real FastAPI routes on an owned disposable SQLite
database. Mocks remain limited to isolated component/layout/error-state tests.

BUILD evidence must include:

- the complete current Python/frontend regression and C3a-d browser/refusal
  coverage;
- contract/typecheck/production build/static asset smoke;
- real-browser staffing, approval and closeout success paths;
- anonymous, wrong-role, unassigned, stale-version, missing-approval,
  wrong-destination-assignment, frozen-parent and retired-override refusals;
- zero offline queue/localStorage/background sync/realtime behavior;
- exact-parent rehearsal, repository gates and exact cleanup;
- a fresh provider runner whose counter observes zero calls for every refusal,
  verifies persisted assigned closeout state plus actor-bound audit records,
  then performs exactly one real provider call and writes only sanitized
  evidence.

No provider call is permitted during authoring or before the BUILD refusal and
durability preconditions pass. This resolves `C3D-INTAKE-F4`.

## 6. D5 — Checkpoint and closure separation

C3d BUILD, independent REVIEW and commit/push are one checkpoint. C4 is a
later, separate truth-sync changed set for roadmap/catalog/status/continuity.
C3d BUILD must not tick P2-C. After a successful C4, P2-D is the sole next
roadmap item; Phase 2 remains open pending P2-D and the separate full-shift
exit gate.

This resolves `C3D-INTAKE-F5`.

## 7. Rejected alternatives

- Client-side role ranking: rejected; the server decides authority.
- New backend convenience routes during C3d: rejected; this checkpoint is
  frontend/evidence-only and current contracts are sufficient for the bounded
  target matrix.
- A fake Report revoke endpoint: rejected; successor creation is canonical.
- Reusing a prior provider receipt: rejected; C3d makes the final P2-C
  governance claim and requires fresh evidence.
- Combining C3d BUILD with C4, P2-D or the full-shift exit: rejected.

## 8. Claim boundary

After C3d independent review/push and separate C4 truth sync, P2-C may claim
only that, within the single workspace, authenticated actively assigned users
use the specified operator and supervisor lifecycle controls while the backend
re-authorizes and audits every action on the proven backends.

No multi-tenant/provider `data_scope`, destination-only handover discovery,
offline/realtime, exactly-once, production PostgreSQL, external-channel, AI,
P5-A export, P2-D, full-shift-exit or Phase-2 completion claim is allowed.
