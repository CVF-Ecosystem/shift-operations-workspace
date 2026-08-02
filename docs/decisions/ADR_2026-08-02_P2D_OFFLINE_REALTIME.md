# ADR — P2-D Offline Queue and Polling-Based Realtime Sync

- ADR id: `ADR-P2D-OFFLINE-REALTIME-2026-08-02`
- Status: `PROPOSED_FOR_INDEPENDENT_REVIEW`
- Risk: `R2`
- Phase: `DESIGN`
- Role: `DESIGN_AUTHOR`
- INTAKE: `INTAKE_2026-08-02_P2D_OFFLINE_REALTIME.md`
- Baseline: `1f3646aba7d2bc4becea6c156475360331133f29`

## 1. Decision summary

P2-D will remain frontend/evidence-only and will close a deliberately bounded
connectivity contract:

- a service worker handles navigation fallback only and never caches API data;
- a versioned, authenticated-user-bound local queue supports exactly three
  existing CAS transitions;
- replay is FIFO, per-tab single-flight and fail-stop, never exactly-once;
- every read refresh, whether polling-, mutation- or staffing-triggered, passes
  through one serial coordinator so it cannot invalidate another owner's fresh
  read by racing it;
- “realtime” means measured foreground polling plus recovery events, not a push
  channel that does not exist.

## 2. Decisions

### D1 — Navigation-only service worker

Register a same-origin service worker from `main.tsx`. It may cache only the
static offline fallback and may answer only failed navigation requests with
that fallback. It MUST pass through non-navigation requests and MUST NOT put
API responses, Authorization headers, application JSON or authenticated HTML
snapshots in Cache Storage. The offline page states the bounded truth: commands
can be queued only from an already-open authenticated console, not from the
fallback page itself.

The manifest gains a same-origin SVG icon and remains `display: standalone`.
No third-party PWA plugin or package/lock update is needed.

### D2 — Authenticated-user queue namespace

After authentication, the console resolves `/auth/me`. The principal id is
retained only in tab-scoped session state and is used to select a localStorage
namespace derived from a fixed application prefix plus the exact user id.
Queue payloads never carry the bearer token or role. A different authenticated
user cannot list, display, replay or discard another user's commands.

Logout does not silently replay or silently delete pending commands. The queue
becomes inaccessible until the same user authenticates again. A malformed user
id cannot alter the fixed prefix or enumerate another namespace.

### D3 — Strict local command contract

Each stored object has only:

```text
schemaVersion, clientOperationId, actorUserId, commandType,
recordId, targetStatus, expectedVersion, createdAt, state, lastErrorKind
```

The command union is exactly:

- `task.transition` with a legal `TaskStatus` target;
- `customer_request.transition` with a legal `CustomerRequestStatus` target;
- `incident.transition` with a legal operator-permitted `IncidentStatus`
  target.

`schemaVersion` is the literal integer `1`. States are exactly `pending`,
`replaying`, `blocked`, `outcome_unknown` and `applied_stale`. `lastErrorKind`
is `null` for pending/replaying; `blocked` permits only `conflict`, `forbidden`,
`not_found`, `invalid`, `unauthorized`, `server` or `storage`;
`outcome_unknown` requires that same literal; and `applied_stale` requires
`refresh_failed`. Runtime parsing rejects unknown keys/types/enums, mismatched
actor, invalid UUID or positive-version constraints, impossible timestamps and
unknown schema versions. Storage is bounded to 50 commands and 24 hours.
Expired/malformed entries are quarantined from replay under ephemeral bounded
ids `invalid-<index>` with a fixed reason and explicit discard; their raw JSON
is never rendered or copied into a valid entry. No free text, record body,
approval id/digest, evidence or secret is persisted. `actorUserId` is persisted
queue metadata only and is never added to the network mutation body.

`clientOperationId` is local correlation only. Since the backend has no durable
idempotency receipt, it MUST NOT be described as a server dedupe key.

### D4 — Enqueue boundary

The UI enqueues only when `navigator.onLine === false` before the mutation
function is invoked. In that branch no fetch is constructed and the browser
evidence must observe zero mutation requests. If a fetch was attempted and
throws `outcome_unknown`, the current lockout behavior remains: do not enqueue,
refresh or retry automatically.

Create, approval, staffing, correction, report, shift close/freeze and all
supervisor commands remain online-only. Capability hints never enlarge the
queue union and backend gates remain authoritative during replay.

### D5 — Replay state machine

Queue states are `pending`, `replaying`, `blocked`, `outcome_unknown` and
`applied_stale`. Replaying is FIFO and single-flight per visible browser tab
under the active principal:

1. verify principal and command schema again;
2. dispatch exactly the existing typed transition call with its recorded CAS;
3. on HTTP success, change it to `applied_stale`; remove it only after a
   serialized fresh read commits, without ever dispatching it again;
4. on 409/403/404/422/401 or HTTP 5xx/server failure, mark `blocked` with the
   exact error kind, stop the entire queue and require visible resolution;
5. on transport ambiguity, mark `outcome_unknown`, stop and prohibit automatic
   retry until an explicit fresh read and operator decision;
6. never skip a blocked head item to apply later commands out of order.

Only `pending` may dispatch. A crash-left `replaying` item becomes
`outcome_unknown`. Neither `blocked` nor `outcome_unknown` can transition back
to `pending`: after a genuine fresh read, the operator may explicitly discard
it and create a new action from the live UI, which captures a new CAS value;
the recorded command/CAS is never rewritten. `applied_stale` permits fresh-read
resolution or discard only, never dispatch. A conflict/ambiguous item is not
silently translated into success even if a later read shows the target state.

### D6 — One serialized refresh coordinator

All mutation-owned, staffing-owned, queue-owned, recovery and polling refreshes
share a single FIFO coordinator. Only one composite refresh may run at a time;
equivalent pending requests may coalesce onto the same promise. The coordinator
does not swallow rejection or report success until the underlying hooks commit
their own current state. Shift changes and self-revocation still clear retained
operational state through the existing request-token/selection boundary.
This is not a cross-tab leader election: same-actor tabs may race, but recorded
CAS permits at most one state transition to commit and the loser must visibly
block. Request-exactly-once across tabs is outside this tranche.

### D7 — Polling-based realtime contract

While authenticated, online and visible, the console runs one serialized
refresh at a default 15-second interval. It immediately refreshes after an
`online` event and when a hidden page becomes visible. It pauses when offline,
hidden or signed out, permits no overlapping request, and applies bounded
backoff after failures. A validated build-time override may shorten the
interval for browser evidence but cannot disable serialization or set an
unsafe production value.

The UI labels this `Live sync: polling` and exposes last-success time plus
syncing/offline/error/queue-blocked state. It MUST NOT display “live push”, SSE
or WebSocket.

### D8 — Failure and disclosure behavior

- 401 clears the session and stops queue/polling.
- Assignment-scoped 403/404 or a refreshed shift list that no longer contains
  the selected shift clears selection and retained operational state.
- Poll failure retains last rendered data but marks it stale; it never converts
  stale content into a successful freshness claim.
- A mutation HTTP success followed by refresh failure is known-applied but
  stale (`applied_stale`), never `outcome_unknown` and never replayable.
- The queue panel exposes only command type, target id suffix, target status,
  age and state. It never displays stored raw JSON.

### D9 — Evidence architecture

Vitest covers schema/parser/storage/state-machine/actor isolation/serialization
and React wiring. Real Playwright against real FastAPI proves zero POST while
offline, one reconnect transition, conflict/ambiguous fail-stop, service-worker
API no-cache behavior and another actor's update appearing through polling.

A dedicated harness reuses the C3d process/port/readiness/cleanup contract.
Fresh live-governance evidence runs only after full non-live, real-browser and
durability gates: refusal/ambiguous cases hold provider calls at zero, an
admitted assigned transition is verified durably, then exactly one provider
call is permitted and sanitized.

## 3. Alternatives

### A — Queue every mutation and retry until success — rejected

Creates and receipt-bearing actions have no uniform durable idempotency key;
transport ambiguity could duplicate effects or reuse stale authority.

### B — Add backend idempotency receipts in P2-D — deferred

This would require migration, ledger, transaction and every mutation route to
share an atomic receipt contract. It is valuable future work but materially
larger than the current frontend connectivity milestone and needs its own
governed tranche.

### C — WebSocket or SSE push — deferred

Neither transport nor a multi-instance event broker exists. Adding one here
would cross backend/deployment boundaries and still require reconnect/cursor
semantics. Polling supplies a testable bounded freshness contract now.

### D — Cache authenticated GET responses for full offline operation — rejected

It risks cross-user disclosure and stale governance/assignment state. P2-D
provides command staging and navigation fallback, not an offline read replica.

### E — Treat 409 plus matching state as replay success — rejected

The frontend cannot prove which actor produced that state or that every audit
effect matches the queued intent. Conflict remains visible and manual.

### F — Cross-tab local lease as exactly-once replay — deferred

A browser lease can reduce races but cannot prove server-side exactly-once
delivery after transport ambiguity. P2-D therefore keeps per-tab single-flight
and CAS fail-stop; durable idempotency needs a separate backend tranche.

## 4. Consequences and claim boundary

The design improves degraded connectivity without weakening the existing CAS,
identity, permission, assignment or approval boundary. It deliberately offers
only at-least-once user intent staging with fail-stop replay; it does not prove
exactly-once delivery, background execution, push realtime, offline data
availability, production SLA or multi-tenant isolation.

P2-D may become `CLOSED_BOUNDED` only after its SPEC, exact-path Work Order,
independent authorization, BUILD, independent review/push and separate C4
truth sync. The full-shift exit gate and Phase 2 remain open afterward until a
separate end-to-end tranche passes.
