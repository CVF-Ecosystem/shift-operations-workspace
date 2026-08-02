# INTAKE — P2-D Offline Queue and Realtime Sync

- Tranche: `P2D-OFFLINE-REALTIME-2026-08-02`
- Roadmap item: `P2-D`
- Date: 2026-08-02
- Risk: `R2`
- Phase: `INTAKE`
- Active role: `ORCHESTRATOR / INTAKE_AUTHOR`
- Source parent: `1f3646aba7d2bc4becea6c156475360331133f29`

## 1. Intent and authority boundary

Open the only move authorized by the P2-C C4 closure: define a bounded P2-D
implementation for an installable/degraded PWA shell, a safe offline command
queue and timely multi-actor UI refresh. This INTAKE authorizes analysis and
later DESIGN/SPEC/WORK_ORDER authoring only. It authorizes no source edit,
provider call, staging, commit, push, BUILD, P2-D closure or Phase 2 claim.

## 2. Current implementation truth

- P2-C is `FREEZE / CLOSED_BOUNDED` at C4 `1f3646a`; Phase 2 remains open.
- `public/manifest.webmanifest` exists but has no icons, `main.tsx` registers
  no service worker, and `offline.html` claims updates are saved although no
  activated PWA/offline flow makes that generally true.
- `src/offline/queue.ts` is five lines of unvalidated `localStorage` CRUD. It
  is not wired to the console, has no actor binding, bounded schema, status,
  conflict handling or safe replay contract.
- `services/api.ts` deliberately maps a fetch failure after dispatch to
  `outcome_unknown`; `useMutationControl` locks and never auto-retries it.
- Existing mutation APIs have version/status preconditions for selected
  transitions, but create, receipt, closeout and staffing actions are not a
  uniform idempotent command surface. No durable backend
  `client_operation_id` receipt exists.
- No WebSocket, SSE or polling coordinator exists. Reads refresh only on
  selection, explicit mutation completion or manual control flow.
- Auth tokens are tab-scoped in `sessionStorage`; no token may enter the
  offline queue, Cache Storage or service-worker messages.

## 3. Bounded requested outcome

1. Provide an offline navigation fallback and install metadata without
   caching authenticated API responses.
2. Bind every persisted queue to the authenticated user and store only a
   strict, size/age-bounded command schema with no token, free text, approval
   receipt or provider data.
3. Queue only operator `task.transition`, `customer_request.transition` and
   `incident.transition` commands carrying record id, legal target state and
   the last-read `expected_version`.
4. Enqueue only when the browser is observably offline before dispatch. Never
   convert an online `outcome_unknown` into a queued retry.
5. Replay FIFO after reconnect under the current authenticated session. Stop
   on conflict, authorization failure, invalid data or ambiguous transport;
   expose bounded pending/review/discard/manual-refresh controls instead of
   silent looping or rewriting a recorded CAS value.
6. Add serialized, foreground-only, authenticated polling with a documented
   freshness interval plus immediate refresh on `online`/visibility recovery.
   Name this truthfully as polling-based realtime sync, not push transport.
7. Prove in a real browser against real FastAPI routes that offline enqueue
   makes zero mutation calls, reconnect applies one authorized transition,
   ambiguous outcomes do not auto-retry, and another actor's committed change
   appears without a manual refresh.

## 4. Explicit exclusions

- No offline create, message/event/report generation, approval/receipt,
  staffing, close/freeze or correction command.
- No background sync after the authenticated page/tab is gone.
- No backend idempotency table/header claim, exactly-once claim, WebSocket,
  SSE, push notification or production latency/SLA claim.
- No cached JWT, authenticated JSON/API response, operational snapshot,
  secret, provider payload or raw error.
- No database, migration, domain, ledger, OpenAPI, CVF policy or backend
  permission change unless a later reviewed DESIGN proves the frontend-only
  boundary impossible and a new authorization explicitly adds it.
- No full-shift exit execution, Phase 2 closure or post-Phase-2 queue start.

## 5. Risk classification

`R2`: queued mutations cross time/connectivity boundaries and can duplicate,
misattribute or apply stale authority if designed incorrectly. Realtime refresh
can race mutation-owned reads and disclose stale assignment-scoped data. Human
review and independent authorization are mandatory before BUILD.

## 6. Evidence obligations

- Frozen frontend install, typecheck, full frontend tests and production build.
- Full Python non-live regression and repository gates.
- Real Chromium/FastAPI offline/reconnect and polling evidence.
- Fresh disposable PostgreSQL evidence only if the reviewed Work Order keeps a
  governance-behavior claim over the existing backend matrix.
- Because the tranche will claim refusal/authorization behavior remains
  governing during sync, fresh sanitized evidence must observe zero provider
  calls across refusal/ambiguous paths, verify durable admitted state first,
  then make exactly one real provider call.
- Exact-parent rollback rehearsal and owned-resource cleanup.

## 7. Exit from INTAKE

DESIGN may begin only with the frontend-only boundary, CAS-only queue subset,
actor/session isolation, no-cache service-worker rule, serialized refresh rule,
evidence ordering and exclusions above recorded as binding constraints. Any
proposal to auto-retry `outcome_unknown`, queue an unversioned create, cache API
data or call a provider before refusal/durability proof is a stop condition.
