# INTAKE — P2-C Operations Console Read Slice

ID: `P2C-OPERATIONS-CONSOLE-READ-SLICE-2026-07-28`
Roadmap lane: `P2-C`
Control-chain phase: `INTAKE`
Risk: `R2`
Status: `INTAKE_COMPLETE — DESIGN_NOT_STARTED`
Owner intent: continue the roadmap after P2-A handover `FREEZE`, following the
CVF control chain with no inherited BUILD authority.

## 1. Intent

Open the first usable P2-C frontend slice over the backend verticals already
closed bounded. The slice should let an authenticated operator select a shift
and read real operational state through `workspace-api`, starting with the
timeline/open-work surfaces named in the roadmap.

This is not authority to implement the whole frontend, PWA/offline behavior,
reporting, AI, RAG, memory or channel integration.

## 2. Current truth

- `apps/workspace-web` is a thin React/Vite shell. Its only real API call is
  unauthenticated `GET /health`; its local feed is React state only.
- Authentication, feature, routing, guard, store and test folders are README
  stubs.
- `workspace-api` exposes reads for shifts, incidents and handovers.
- Events, tasks and customer requests expose mutations but no list/read API
  suitable for timeline/open-work UI.
- The Ledger Protocol and both backends have single-record getters for those
  three families, but no shift-scoped list methods.
- `GET /shifts` is currently unauthenticated. Incident/handover reads require
  a valid JWT identity but have no per-shift assignment/data-scope model.
- The repository declares `pnpm@9.15.0`, but has no lockfile. Current CI runs
  Python only. This reviewer environment has no Node/npm/corepack/pnpm.
- Frontend/backend/database separation in
  `docs/architecture/FRONTEND_BACKEND_BOUNDARY.md` is binding.

## 3. Intake findings

### P2C-INTAKE-F1 — READ_SURFACE_PREREQUISITE

The roadmap's Events/Open Work UI cannot use real data without bounded,
shift-scoped read methods and HTTP endpoints for events, tasks and customer
requests. Mock data may prove layout only and cannot satisfy a functional
P2-C claim.

### P2C-INTAKE-F2 — FRONTEND_REPRODUCIBILITY_GATE_ABSENT

There is no committed package lock, no frontend CI build/test job and no
available local Node toolchain. DESIGN must define a reproducible pinned
install/build/test path, including how it runs on this Windows/Docker
workspace without committing generated dependencies.

### P2C-INTAKE-F3 — READ_AUTHORITY_BOUNDARY_UNDEFINED

Read endpoints are inconsistent: shifts are public, while incident/handover
reads authenticate but do not enforce shift/tenant assignment. The project has
no assignment registry. DESIGN must state the exact bounded read claim and
must not imply row-level/tenant authorization that the model cannot prove.

## 4. Proposed tranche boundary for DESIGN

The recommended first slice is read-first and cross-layer only where required
to avoid a fake UI:

- authenticated login/logout and short-lived access-token handling;
- authenticated shift selection;
- read-only shift timeline and open-work views backed by real HTTP data;
- read-only incident and handover summaries using existing APIs;
- minimal shift-scoped ledger/query/API seams required by those views;
- loading, empty, offline and controlled-error states;
- responsive desktop/mobile presentation and accessibility basics;
- reproducible frontend install/build/test/CI gate.

No durable mutation is in this slice. Buttons that would create, transition,
review, acknowledge, close or freeze records are excluded rather than mocked.

## 5. Explicit exclusions

- P2-D offline mutation queue and realtime;
- reports, report approval, dashboard/administration breadth;
- provider calls from production UI, AI Gateway, Refinery, retrieval/RAG,
  application memory or forecasting;
- destination-shift personnel assignment;
- refresh tokens, revocation, device trust or admin provisioning;
- tenant/shift assignment registry or a claim of row-level authorization;
- database migration unless DESIGN proves it unavoidable;
- any write to CVF core or sibling repositories.

## 6. Governance and evidence boundary

- UI structure/layout tests may use mocks.
- Real-data or authentication/governance claims must exercise the real HTTP
  route and backend. Any claim that CVF governs AI/agent behavior still
  requires a real provider API call and a sanitized receipt.
- Frontend never enforces authority; it reflects server responses.
- Access tokens must not be committed, logged or placed in durable application
  data. DESIGN must decide bounded browser storage and document the fixed-TTL,
  no-revocation limitation.
- TypeScript/TSX/JavaScript files must remain at or below 200 physical lines.

## 7. DESIGN questions

1. Exact read permission model: identity-only bounded claim versus new
   provider-neutral `*.read` actions, without inventing assignment semantics.
2. Exact API/query shape and deterministic ordering/pagination limits.
3. Token lifetime/storage, logout and 401 recovery behavior.
4. Contract strategy: generated types versus a small checked DTO boundary.
5. Test runner and pinned package/lockfile strategy.
6. Docker-based versus host-based reproducible frontend validation.
7. Exact first-screen information hierarchy and responsive behavior.

## 8. Stop conditions

STOP before DESIGN if continuity or current Git truth disagrees with this
intake. STOP before BUILD until a reviewed ADR, testable SPEC, exact-path Work
Order and pre-BUILD acknowledgment are committed and pushed.

## 9. Next governed move

Author DESIGN for this exact read-first slice. DESIGN may split the read API
prerequisite into a separately committed sub-tranche if that yields a safer,
more independently revertible boundary. No implementation is authorized.
