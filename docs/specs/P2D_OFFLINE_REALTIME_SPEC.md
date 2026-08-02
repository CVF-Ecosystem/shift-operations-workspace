# Specification — P2-D Offline Queue and Realtime Sync

- Spec id: `P2D-OFFLINE-REALTIME-SPEC-001`
- Tranche: `P2D-OFFLINE-REALTIME-2026-08-02`
- Phase: `SPEC`
- Risk: `R2`
- Status: `PROPOSED_FOR_INDEPENDENT_REVIEW`
- Parent ADR: `ADR_2026-08-02_P2D_OFFLINE_REALTIME.md`
- Baseline: `1f3646aba7d2bc4becea6c156475360331133f29`

## 1. Truth boundary

Current truth is a manifest without icons, no registered service worker, an
unwired five-line localStorage queue and no polling/push transport. Everything
below is intended behavior, not current implementation truth, until a reviewed
BUILD proves it. Backend/domain/ledger/OpenAPI behavior is already established
by P2-C and remains authoritative and unchanged.

## 2. Requirements

### R1 — PWA fallback without API caching

The app MUST register a same-origin service worker. The worker MAY cache only a
versioned static offline fallback. It MUST intercept only navigation requests,
try network first and use the fallback only on network failure. It MUST NOT
cache or synthesize non-navigation requests, API JSON, Authorization-bearing
responses, authenticated page snapshots or mutation responses. Cache upgrade
MUST delete only prior caches owned by this application prefix.

### R2 — Honest install metadata and fallback copy

The manifest MUST reference an existing same-origin icon and retain standalone
display metadata. The fallback MUST NOT claim that arbitrary updates are saved;
it MUST state that only an already-open authenticated console can stage the
three supported transitions.

### R3 — Current principal resolution

An authenticated console MUST resolve `/auth/me` before queue display/replay or
poll activation. The bearer token remains only in `sessionStorage`. The current
user id MAY be stored tab-scoped and as the required `actorUserId` queue
metadata, but MUST NOT appear in a command payload or Cache Storage. 401 MUST
clear the session and stop all sync activity.

### R4 — Actor-bound namespace

Persistent queue storage MUST use a deterministic, encoded namespace for the
exact current `user_id`. Queue APIs MUST require that user id and reject every
entry whose `actorUserId` differs. No UI/control MAY enumerate or mutate a
different namespace.

### R5 — Exact command union

Only these commands are valid:

1. `task.transition(recordId, targetStatus, expectedVersion)`;
2. `customer_request.transition(recordId, targetStatus, expectedVersion)`;
3. `incident.transition(recordId, targetStatus, expectedVersion)`.

Targets MUST belong to the existing frontend lifecycle tables, incident targets
MUST remain in the operator subset, record ids MUST be UUIDs and versions MUST
be positive integers. No command contains free text, token, role, shift data,
receipt, approval, digest, evidence, response body or raw error.

### R6 — Versioned strict parser and bounds

Stored entries MUST have exactly the ADR D3 fields. `schemaVersion` MUST be the
literal integer `1`; states MUST be exactly `pending`, `replaying`, `blocked`,
`outcome_unknown` or `applied_stale`. `lastErrorKind` MUST be `null` for
pending/replaying; blocked MUST use exactly `conflict|forbidden|not_found|
invalid|unauthorized|server|storage`; outcome_unknown MUST use
`outcome_unknown`; applied_stale MUST use `refresh_failed`. Unknown keys,
types, enum values, schema versions, actors and invalid timestamps MUST reject.
The queue MUST accept at most 50 valid entries per actor and entries younger
than 24 hours. Malformed/expired entries MUST be excluded from replay and
surfaced under ephemeral bounded ids `invalid-<index>` with a fixed reason for
explicit discard, without rendering raw JSON. `actorUserId` is persisted queue
metadata only and MUST NOT enter the network mutation body.

### R7 — Local operation identity

New entries MUST use `crypto.randomUUID()` and an ISO UTC creation time.
`clientOperationId` is local correlation only. Source, docs and UI MUST NOT call
it a backend idempotency receipt/key or make an exactly-once claim.

### R8 — Pre-dispatch offline enqueue

Transition controls MUST consult connectivity before invoking the typed API
method. Only `navigator.onLine === false` may take the enqueue branch. A
successful storage write returns a distinct `queued` result and visible state;
storage failure returns an error and MUST NOT claim queued success. The branch
MUST issue zero fetch/mutation calls.

### R9 — Ambiguous outcome preservation

Any request attempted while online that fails at the transport boundary remains
`outcome_unknown`. It MUST NOT be added to the offline queue, auto-refreshed,
auto-retried or unlocked. Existing mutation lockout semantics MUST not regress.

### R10 — Replay state recovery

Persisted states are `pending`, `replaying`, `blocked`, `outcome_unknown` and
`applied_stale`.
On load, any item left `replaying` by a crash/reload MUST become
`outcome_unknown`, because dispatch may have occurred. It MUST never return to
`pending` automatically.

### R11 — FIFO per-tab single-flight replay

Replay MUST operate only for the authenticated matching actor, online/visible
page and one command at a time per tab from oldest to newest. It MUST execute
the exact existing typed API transition with recorded CAS data. No later item
may bypass a non-pending head item. This tranche does not claim cross-tab leader
election: two same-actor tabs may race, but CAS MUST permit at most one commit
and the loser MUST become visibly blocked; no request-exactly-once claim is
allowed.

### R12 — Success and fresh-read rule

After HTTP success, the item MUST become `applied_stale` and MUST never dispatch
again. Only after the shared serialized refresh genuinely commits may it be
removed and reported applied. If refresh fails or is superseded, it remains
known-applied/stale; it MUST NOT become `outcome_unknown`, return to pending or
be replayed.

### R13 — Fail-stop matrix

- 409, 403, 404 and 422: mark `blocked`, halt replay and require a fresh read
  plus explicit discard/new-action decision.
- 401: clear session, halt and retain the actor-bound queue.
- HTTP 5xx/server response: mark `blocked/server`, halt FIFO and prohibit
  automatic retry.
- transport ambiguity: mark `outcome_unknown`, halt and prohibit auto-retry.
- local parse/storage error: quarantine/halt without dispatch.

A matching state observed after conflict MUST NOT silently convert the command
to success.

### R14 — Explicit queue controls

The panel MUST show bounded metadata only: type, shortened record id, target,
age and state. Only `pending` may dispatch. `blocked` and `outcome_unknown`
MUST never return to pending or rewrite recorded CAS; after a genuine fresh
read, the operator may explicitly discard and create a new live action.
`applied_stale` permits fresh-read removal or confirmed discard only. Discard
requires confirmation; bulk silent clear is forbidden.

### R15 — Global refresh serialization

Mutation, staffing, queue, visibility, online-recovery and polling refreshes
MUST share one FIFO coordinator. At most one composite refresh executes.
Equivalent requests MAY coalesce but every caller MUST receive the same real
settlement. Rejection/supersession MUST not be swallowed as success.

### R16 — Polling schedule

While authenticated, online and visible, polling MUST run every 15 seconds by
default. A build-time interval MUST parse to an integer from 5 through 60
seconds or fall back to 15. Polling pauses offline/hidden/signed-out, never
overlaps, and resumes with one immediate serialized refresh on `online` or
visibility recovery. Failures use bounded backoff and remain visible.

### R17 — Assignment/disclosure preservation

Each polling/reconnect composite refresh MUST include the ordinary shift list
and selected-shift operational data. Supervisor staffing reads are included
only when already authorized. If refreshed assignment scope removes the
selected shift, selection and retained operational state MUST clear exactly as
in C3d. Client capability/queue state never grants access.

### R18 — Connection UI truth

The UI MUST distinguish offline, syncing, connected/last-success, stale/error,
pending queue, blocked, outcome-unknown and known-applied/stale states with
accessible live status.
It MUST use `polling sync` wording and MUST NOT say push/WebSocket/SSE,
exactly-once or fully offline.

### R19 — Frontend-only protected boundary

BUILD MUST have zero diff in backend/domain/ledger/database/migrations/OpenAPI,
auth/CVF policy, dependency versions/lockfile, CI and Phase 2 roadmap/continuity.
No provider configuration or secret handling changes are allowed.

### R20 — Browser evidence

Real Chromium against real FastAPI routes MUST prove:

1. offline enqueue of a legal transition observes zero mutation requests;
2. reconnect replays it once and a fresh GET renders the committed version;
3. an online ambiguous request is not queued or automatically retried;
4. conflict blocks FIFO and later commands do not pass it;
5. another authenticated actor's committed update appears through polling
   without manual refresh;
6. assignment loss clears selected/retained data;
7. service worker never caches/intercepts API traffic and navigation fallback
   copy is truthful;
8. two same-actor tabs racing the same recorded CAS produce at most one commit,
   with the loser visibly blocked and no exactly-once claim.

### R21 — Regression and live evidence

Frozen install, frontend typecheck/all tests/build, full Python, focused harness
tests, disposable PostgreSQL 16 current pinned matrix, session/catalog/file-
size/repository/JSON/diff/doctor and exact cleanup MUST pass. Fresh live evidence
MUST keep provider count zero through refusal/ambiguous cases, verify one
assigned admitted transition and actor-bound audit durably, then allow exactly
one sanitized real provider call. Mock output is not governance proof.

### R22 — Parent rehearsal and closure

An exact-parent detached rehearsal MUST reproduce the recorded baseline and
clean up. BUILD changed set MUST equal the reviewed Work Order ceiling. P2-D
closure requires independent BUILD `REVIEW_PASS`, push and separate C4 truth
sync. Full-shift exit and Phase 2 remain open and require a fresh tranche.

## 3. Acceptance criteria

- **AC-01:** service worker fallback works for navigation and its cache contains
  no API/authenticated response.
- **AC-02:** manifest icon exists; fallback copy states the bounded truth.
- **AC-03:** `/auth/me` gates queue/polling; 401 stops both and clears session.
- **AC-04:** actor namespaces are isolated and cross-actor entries reject.
- **AC-05:** parser accepts only R5/R6 exact schemas, enums and bounds.
- **AC-06:** 50-item/24-hour limits and malformed quarantine are proven.
- **AC-07:** offline enqueue yields visible `queued` and zero fetch calls.
- **AC-08:** storage failure cannot claim queued success.
- **AC-09:** online `outcome_unknown` never enters/retries from the queue.
- **AC-10:** crash-left `replaying` recovers as `outcome_unknown`; all state and
  `lastErrorKind` invariants pass strict parsing.
- **AC-11:** replay is actor-bound, FIFO and single-flight per tab; two-tab CAS
  race yields at most one commit and a visibly blocked loser.
- **AC-12:** HTTP success becomes non-replayable `applied_stale`; removal occurs
  only after a committing fresh read.
- **AC-13:** the complete R13 matrix, including 5xx/server failure, halts
  without later-item bypass, automatic retry or CAS rewrite; matching target
  state is not attributed silently.
- **AC-14:** discard/new action is explicit; no raw payload or silent bulk clear.
- **AC-15:** one refresh coordinator serializes every refresh owner.
- **AC-16:** polling interval, pause/resume/immediate recovery and backoff pass.
- **AC-17:** another actor's real mutation appears without manual refresh.
- **AC-18:** assignment loss clears selection and all retained operational data.
- **AC-19:** UI/accessibility wording covers known-applied/stale, matches R18 and
  avoids forbidden push/exactly-once/fully-offline claims.
- **AC-20:** real Chromium/FastAPI matrix R20 passes with owned cleanup.
- **AC-21:** no backend/OpenAPI/package-lock/CI/continuity protected diff.
- **AC-22:** frontend/full-Python/PostgreSQL/repository gates pass.
- **AC-23:** fresh receipt proves zero calls then exactly one real provider call.
- **AC-24:** exact-parent rehearsal and exact changed-set checks pass.
- **AC-25:** independent reviewer returns `REVIEW_PASS`; no open finding/waiver.
- **AC-26:** C4 may close P2-D bounded only; full-shift exit/Phase 2 stay open.

## 4. Stop conditions

STOP on continuity/parent drift, dirty baseline, missing browser/provider,
outside/unnecessary path, file-size overflow, backend/lockfile change, cached
API/auth data, cross-user queue access, unsupported command, auto-retry of an
ambiguous outcome, replay past a blocked head, overlapping refresh, fake push
claim, mocked governance proof, unsanitized receipt or cleanup residue.
