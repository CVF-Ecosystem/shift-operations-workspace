# SPEC — P2-C Operations Console Read Slice

ID: `P2C-OPERATIONS-CONSOLE-READ-SLICE-SPEC-001`
Tranche: `P2C-OPERATIONS-CONSOLE-READ-SLICE-2026-07-28`
Risk: R2
Status: `SPEC_COMPLETE — PENDING_WORK_ORDER`
Design:
`docs/decisions/ADR_2026-07-28_P2C_OPERATIONS_CONSOLE_READ_SLICE.md`

## R1 — exact product boundary

The tranche implements a read-only authenticated operations console. It may
read shifts, events, canonical open work, incidents and handovers. It must not
expose UI controls that create or mutate operational records.

## R2 — open-work HTTP contract

Add authenticated:

`GET /shifts/{shift_id}/open-work`

The response shape is exactly:

```json
{
  "shift_id": "uuid",
  "tasks": [],
  "customer_requests": [],
  "incidents": []
}
```

The three arrays come from `Ledger.open_work_snapshot(shift_id)`, mapped from
its canonical `Task`, `CustomerRequest` and `Incident` groups. The route must
not reimplement open predicates. A missing shift returns controlled HTTP 404.

Array order remains the existing canonical UUID order. Task and Incident
evidence must survive unchanged.

## R3 — event timeline query

Add `Ledger.list_events_for_shift(shift_id)` to the Protocol and both backends,
then expose authenticated:

`GET /events?shift_id=<uuid>`

The result contains every event for that shift and no event from another
shift. Order is deterministic:

1. events with `starts_at` before events without it;
2. ascending `starts_at`;
3. ascending string form of `event_id`.

Evidence must be preserved. Missing shift returns controlled HTTP 404.
InMemoryLedger, SQLite and disposable PostgreSQL must agree.

## R4 — bounded result size

This first internal slice may remain unpaginated only with a hard maximum of
500 records per returned array. Exceeding the limit must return controlled
HTTP 409 or 422 with no partial result. The same limit applies across
backends. DESIGN of pagination is deferred.

## R5 — authenticated read admission

These routes must require `get_principal`:

- `GET /shifts`;
- `GET /shifts/{shift_id}/open-work`;
- `GET /events?shift_id=...`;
- existing incident and handover reads used by the UI.

No new `*.read` permission action is added. Every known-role JWT may read the
workspace-wide view. Anonymous, expired, malformed or mis-signed tokens return
401.

The implementation and receipts must not describe this as per-shift/tenant
authorization, personnel assignment or `data_scope` enforcement.

## R6 — explicit mutation exclusion

The UI contains no active create, confirm, transition, approve, correct,
review, acknowledge, close or freeze control. Local demo-feed submission is
removed. No backend mutation route is changed, including the separately
parked unauthenticated `POST /shifts` finding.

## R7 — login/session behavior

- Login uses real `POST /auth/login`.
- Username/password stay in transient form state.
- Only the access token is stored in `sessionStorage`.
- Logout clears token and operational data.
- A 401 from any operational request clears token and returns to login.
- Page reload in the same tab may restore the token.
- No token, password or Authorization header appears in rendered error text,
  logs, receipts or committed fixtures.
- Fixed TTL/no refresh/no early revocation is documented as a limitation.

## R8 — HTTP client boundary

All frontend traffic goes through `VITE_API_URL`. The frontend imports no
Python backend/domain/ledger source. The client:

- injects bearer authorization only when a token exists;
- handles empty bodies and JSON safely;
- maps network/401/403/404/409/422/5xx into controlled error categories;
- never renders raw transport objects;
- supports cancellation or stale-response suppression when shift selection
  changes.

## R9 — required UI states

The responsive console must provide:

- login form with pending and generic failure state;
- connection/session indicator;
- shift selector with lifecycle status;
- confirmed-event timeline;
- open work grouped into Task, CustomerRequest and Incident;
- incident severity/status summary;
- handover lifecycle summary;
- loading, empty, offline/network, unauthorized and controlled-server-error
  states;
- keyboard-operable controls, associated labels and visible focus.

Mobile and desktop must not require separate code paths.

## R10 — presentation semantics

Only confirmed events appear in the main timeline; non-confirmed events may be
counted separately but not presented as confirmed facts. Presentation filters
do not change backend records. Open-work status is not recalculated in the
frontend.

## R11 — contract truth

Add a JSON Schema for the open-work response under
`packages/workspace-contracts`. Contract tests must compare the route schema
and representative response to the committed contract. Existing canonical
Task, CustomerRequest and Incident shapes are referenced/reused, not forked
with contradictory status values.

Frontend DTO types must match the HTTP response fields used by the UI. A
contract fixture or type-level check must fail when required fields or enum
values drift.

## R12 — frontend test/build toolchain

- Exact Node version: `22.14.0`.
- Exact pnpm version: `9.15.0`.
- Commit root `pnpm-lock.yaml`.
- `pnpm install --frozen-lockfile` must succeed.
- Frontend unit/component tests run through Vitest + jsdom.
- TypeScript typecheck and Vite production build must pass.
- CI runs frozen install, test and build.
- `Dockerfile.web` uses an exact Node tag compatible with Node `22.14.0`, not
  `node:22-alpine` or `latest`, and uses the frozen lockfile.
- Local Docker validation leaves no repository `node_modules`, `dist`,
  coverage, container or anonymous-volume residue.

If the exact Docker tag selected by the Work Order is unavailable, STOP for
authorization repair; do not silently float the tag.

## R13 — file split guard

Every touched/new `.ts`, `.tsx`, `.js` or `.jsx` file is at most 200 physical
lines. No frontend debt entry or exception is authorized. Python files remain
at most 300 lines.

## R14 — backend and frontend test matrix

Mandatory non-live evidence includes:

- Protocol and both-backend event-list parity;
- open-work route exact-shape/order/limit/missing-shift cases;
- unauthenticated and malformed-token read refusals;
- authenticated reads for the lowest known role (`viewer`);
- OpenAPI/contract drift tests;
- frontend auth/session/API-client/view-state/component tests;
- full Python suite;
- frozen frontend install/test/typecheck/build;
- repository validator, catalog, session, file-size, JSON, secret and diff
  checks.

## R15 — PostgreSQL evidence

Disposable PostgreSQL 16 must exercise the new event-list query and open-work
route data dependencies using migration-created schema. It must prove evidence
preservation, ordering, limit behavior and exact cleanup. This remains local
disposable evidence, not production readiness.

## R16 — live governance evidence

Because closure will claim JWT identity is load-bearing for the new read
surfaces:

- refused anonymous/malformed reads must be observed before any provider call;
- a valid JWT read of shift, events and open work must succeed;
- only after the admitted path, make exactly one real provider API call;
- record a sanitized receipt with model, host-only endpoint, HTTP outcome and
  observed call counts;
- do not claim the production UI or read endpoint invokes a provider.

Mock provider output cannot satisfy R16.

## R17 — secret and browser-storage proof

Tests and diff scans must prove:

- no raw JWT, password, API key or Authorization header in receipts/fixtures;
- `localStorage` is not used for authentication;
- logout/401 removes the `sessionStorage` token;
- existing offline queue storage is not activated or repurposed.

## R18 — rollback

Reviewer rehearsal must restore the committed parent and verify:

- all tranche paths match parent after rollback;
- predecessor P2-A closures remain present;
- parent Python and repository gates return to their actual baseline;
- no frontend dependency/build artifacts or Docker residue remain.

## R19 — documentation truth

Update README/boundary/catalog/implementation truth only for behavior actually
built. The module may advance from a thin partial shell to a bounded
read-console partial state, not to `enforced` or Phase 2 complete.

`P2C-DESIGN-F1 UNGOVERNED_SHIFT_CREATE` remains recorded as a separate
security follow-up.

## Acceptance criteria

- **AC-01:** exact R2 open-work contract and canonical source reuse.
- **AC-02:** R3 event query parity/order/evidence on both backends.
- **AC-03:** R4 hard maximum refuses overflow with no partial response.
- **AC-04:** R5 operational reads reject missing/invalid JWT and admit viewer.
- **AC-05:** no assignment/data-scope/per-tenant claim appears.
- **AC-06:** R6 mutation exclusion and local demo feed removal.
- **AC-07:** R7 token lifecycle and secret-safe failure behavior.
- **AC-08:** R8 HTTP boundary and stale-response handling.
- **AC-09:** every R9 state has component evidence.
- **AC-10:** only confirmed events render as timeline facts.
- **AC-11:** HTTP/OpenAPI/JSON Schema/frontend DTO contract agreement.
- **AC-12:** frozen Node/pnpm install, tests, typecheck and production build.
- **AC-13:** every executable file respects R13 with no new debt/exception.
- **AC-14:** full non-live and repository matrix passes.
- **AC-15:** disposable PostgreSQL 16 matrix and cleanup pass.
- **AC-16:** real provider evidence passes with refusal zero-call and exactly
  one admitted call.
- **AC-17:** secret/browser-storage negative proofs pass.
- **AC-18:** reviewer rollback rehearsal passes.
- **AC-19:** docs/catalog/continuity claims remain bounded and truthful.

## Claim boundary

Passing AC-01 through AC-19 proves only the bounded read-console claim in the
ADR. It does not close Phase 2 or any excluded capability.

## Next governed move

Author an exact-path Work Order and independently review its feasibility before
any BUILD.
