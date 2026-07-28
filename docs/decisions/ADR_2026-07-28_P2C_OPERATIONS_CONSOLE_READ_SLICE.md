# ADR — P2-C Operations Console Read Slice

ID: `ADR-2026-07-28-P2C-OPERATIONS-CONSOLE-READ-SLICE`
Tranche: `P2C-OPERATIONS-CONSOLE-READ-SLICE-2026-07-28`
Risk: R2
Phase: DESIGN
Status: `DESIGN_COMPLETE — PENDING_SPEC`
Intake:
`docs/decisions/INTAKE_2026-07-28_P2C_OPERATIONS_CONSOLE_READ_SLICE.md`

## 1. Decision summary

Build one read-only, authenticated operations-console slice backed by real
HTTP data. The tranche may add the minimum backend query surface needed to
avoid mock operational data, but it may not add durable UI mutations.

The slice contains:

- login/logout and tab-scoped token persistence;
- authenticated shift selection;
- confirmed-event timeline presentation;
- server-derived open work for Task, CustomerRequest and Incident;
- read-only incident and handover summaries;
- reproducible package install, frontend tests, production build and CI.

## 2. Resolution of intake findings

### F1 — minimal real read surface

Do not add three unrelated list APIs.

Reuse the already-reviewed `Ledger.open_work_snapshot(shift_id)` seam for a
new authenticated endpoint:

`GET /shifts/{shift_id}/open-work`

Its response groups the canonical server-derived open Task, CustomerRequest
and Incident objects. This is the same source set used by handover creation
and revalidation, so the UI cannot silently invent a different definition of
"open".

Add only one new Ledger query seam:

`list_events_for_shift(shift_id)`

and expose it as:

`GET /events?shift_id=<uuid>`

Both backends must return the same deterministic order and preserve event
evidence. No pagination is added in this first internal slice; SPEC must set a
bounded maximum or explicitly document the initial unpaginated boundary.

### F2 — reproducible frontend gate

- Commit `pnpm-lock.yaml`.
- Keep root `packageManager` pinned to `pnpm@9.15.0`.
- Add frontend `test` and `typecheck` scripts plus production build.
- Add CI steps that install the declared Node line, activate the exact pnpm
  version, use `pnpm install --frozen-lockfile`, run tests and build.
- On a machine without Node, validation may run in a pinned Node Docker image
  against a temporary copy/cache. Generated `node_modules`, coverage and
  `dist` remain untracked and absent after the gate.

The SPEC/Work Order must pin the exact Node version or immutable container
reference before BUILD; a floating `latest` image is prohibited.

### F3 — bounded read authority

Every operational read used by this UI requires a valid JWT via
`get_principal`, including `GET /shifts`, which is currently public.

Do not add new `*.read` permission actions in this tranche. The repository has
no assignment/tenant model, so role-based action permission would imply
granularity it cannot enforce. The exact claim is:

> any authenticated active-user token with a known role may read the
> workspace-wide operational views in this internal slice.

This is identity-only read admission, not per-shift assignment, tenant
isolation or data-scope enforcement. Existing incident/handover read routes
already follow this identity-only shape.

## 3. Frontend architecture

`workspace-web` remains a separately deployable React/Vite app and imports no
backend/domain/ledger Python code.

Use small modules, each within the repository's 200-line TS/TSX hard limit:

- auth session store and login screen;
- typed HTTP client with bearer injection and controlled error mapping;
- shift selector;
- timeline;
- open-work groups;
- incident summary;
- handover summary;
- loading/empty/offline/error states;
- responsive application shell and accessible navigation.

No broad state framework or component library is required for this slice.
React state/context is sufficient. Add dependencies only when acceptance
criteria require them.

## 4. Token and error handling

- Store the access token in `sessionStorage`, never `localStorage`.
- Keep username/password only in transient form state; never persist or log
  them.
- Logout removes the token and all cached operational data.
- Any API 401 clears the session and returns to login.
- The UI may display controlled HTTP status/category and safe server detail;
  it must not render stack traces, tokens, Authorization headers or raw
  transport objects.
- The fixed access-token TTL, no refresh and no early revocation remain known
  P2-B limitations. This tranche does not conceal or repair them.

## 5. UI behavior boundary

The first screen prioritizes:

1. connection/session state;
2. selected shift and its lifecycle status;
3. confirmed operational timeline;
4. open work grouped by canonical record family;
5. incidents and handover state.

The frontend may filter/sort for presentation only. Backend canonical state
and refusal remain authoritative. There are no create/confirm/transition/
review/acknowledge/close/freeze controls in this tranche.

## 6. Contract and test strategy

- Define an explicit open-work response contract at the HTTP boundary.
- Add two-backend parity tests for event list order/evidence.
- Add API integration tests for authenticated success, anonymous 401, missing
  shift and exact response shape.
- Add frontend tests for login, token clearing, loading/error/empty states,
  shift switching and rendering of real DTO shapes.
- Mocks may test UI structure only. Real API/auth claims use real FastAPI/JWT
  paths.
- Because the tranche asserts CVF identity behavior, release evidence must
  include a real provider API call after the admitted authenticated read path,
  plus zero-call proof for refused unauthenticated cases. The receipt must be
  sanitized and must not claim any production endpoint calls a provider.

## 7. Security follow-up not absorbed here

`POST /shifts` is also currently unauthenticated. It is a pre-existing mutation
boundary outside this read-only intake. It must be recorded as
`P2C-DESIGN-F1 UNGOVERNED_SHIFT_CREATE` and routed to a separate governed
security repair; this tranche may not silently add shift-create semantics or
permission policy.

The read slice may proceed only with an explicit claim boundary that does not
suggest all shift routes are governed.

## 8. Alternatives rejected

### Frontend-only mock UI

Rejected for functional closure. It could prove layout only and would leave
Events/Open Work disconnected from project truth.

### Full CRUD console

Rejected as too broad. It would mix many protected mutations, approvals,
evidence and freeze controls into the first frontend tranche.

### New list endpoint for every record family

Rejected for this slice. The existing handover open-work seam already provides
the canonical open set with cross-backend tests.

### Wire data_scope now

Rejected as premature Phase 3 work. There is no assignment/tenant registry to
evaluate. Authentication must not be mislabeled as row-level authorization.

## 9. Claim boundary

Potential closure proves a reproducibly built read-only React console over
real authenticated workspace APIs, with canonical open-work and event data.

It does not prove:

- per-shift/tenant authorization or personnel assignment;
- full shift lifecycle UI or Phase 2 completion;
- PWA offline/realtime behavior;
- report approval, reporting, AI, RAG, memory or forecasting;
- token refresh/revocation/device trust;
- production hosting, browser matrix, load or managed PostgreSQL readiness;
- that a production UI/API endpoint invokes a provider.

## 10. Next governed move

Translate this decision into a testable SPEC. No BUILD is authorized.
