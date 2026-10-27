# P5-A2 synthetic source UI completion, Amendment 4

Status: DRAFT_CONTRACT
Date: 2026-10-27. Baseline `43ea7d048422f29c49c89a71f1e81394839485e2`.
Risk R2. Operator authority: “tiếp 1 lượt cho xong phần UI.” This is one
additional attempt in the *same* SQL → JWT/API → UI acceptance unit. Root owns
effects, artifacts and commit; SPEC_AUTHOR → WORK_ORDER_AUTHOR authors this
contract; a later worker owns only the admitted new source/tests; REVIEWER is
independent. This draft releases no BUILD or physical effect.

## Product Milestone Binding

P5-A2 in `docs/implementation/EXECUTION_ROADMAP.md` at the baseline above
requires authorized scheduled signals/forecasts with source history and
lineage, freshness, uncertainty and abstention, and exact human run/version/
source approval before any durable recommendation or action. Full acceptance
is `docs/specs/P5A2_PROACTIVE_REPORTING_SPEC.md`: operational source authority
and retention, scheduler/recovery, business/cohort method fit, signal/forecast/
drift quality, integrated application access/display, exact approval and
drills, plus real provider proof for applicable AI-governance claims. Operator
and independent reviewer own full milestone acceptance; mock UI/source checks
cannot prove AI governance.

At `43ea7d0`, accepted bounded source/substrate and AM2 real SQL/JWT/two
frozen HTTP receipts remain valid. AM3 accepted 135 worker/135 independent
inert tests, two actual PostgreSQL 16.15 RR/read-only snapshots proving exact
31-table 1/36/36/37/other27zero data and hashes, and `EXACT_VERIFIED` with
zero AM3 application writes. Its one browser context/login returned HTTP200,
then `PANEL_READY` Error before source queries/screenshots; the precise
historical operation/cause remains UNKNOWN. Reviewed cleanup left the same
volume only, container/API/web absent, final owner digest
`fe9b89263d8e4f17f87238940622bd73fa9598e3df70e23c46b5a80b4737f158`.
AM2/AM3 packets, markers, source and budgets are spent/immutable. Current
operational coverage is UNKNOWN and Phase 5 remains 0/5.

AM4 selects only the missing *synthetic* G04/G05 UI proof: one guarded
verify-only runtime and one real browser context that executes the two frozen
source queries and saves two real panels showing synthetic 36/36/36 then
36/36/37. It closes no whole gap or milestone. Root owns runtime/browser and
evidence, backend worker owns the narrow new source, UI/Root own panel proof,
independent reviewer owns source/result judgment. Pass or failure returns
directly to the remaining P5-A2 product work.

| Gap | Current evidence / remainder | In AM4 | Accountable owner / destination |
|---|---|---|---|
| G01/A7 | Real provider 401 spent; BLOCKED | No | Root/operator → P5-A A7, then P5-A2 |
| G02 | Operational RAG/context/index/citations BLOCKED | No | Backend/Root → P5-A2 context |
| G03 | Business/cohort fit UNKNOWN | No | Backend/operator → P5-A2 method |
| G04 | Synthetic SQL/JWT/HTTP and exact AM3 read-only state accepted; UI proof missing; operational integration UNKNOWN | Synthetic UI only | Backend/Root → P5-A2 source |
| G05 | Exact synthetic authority/hash accepted; production mode/authority/coverage/retention/SQLite UNKNOWN | Synthetic UI only | Backend/Root/operator → P5-A2 coverage |
| G06 | Later use-time access OPEN | No | Backend/Root → P5-A2 approval |
| G07 | Scheduler/claim/recovery OPEN | No | Backend/Root → P5-A2 runtime |
| G08 | Operational signal quality OPEN | No | Backend/operator → P5-A2 signals |
| G09 | Operational forecast accuracy OPEN | No | Backend/operator → P5-A2 forecasting |
| G10 | Drift monitoring/display OPEN | No | Backend/UI/Root → P5-A2 quality, P5-B |
| G11 | Other application flows OPEN; actual source panel still unproved | Existing source panel only | UI/Root/operator → P5-A2 application |
| G12 | Exact human approval OPEN | No | Backend/UI/operator → P5-A2 approval |
| G13 | Integrated drills OPEN | No | Backend/Root → P5-A2 drills, P5-C |
| G14 | Live AI-governance proof HELD | No | Root/operator → separately admitted P5-A2 REVIEW |

P5-B dashboard/search/observability remains backend/UI/Root; P5-C backup,
resilience/security/performance remains backend/Root/operator; P5-D deployment,
Shadow Mode/release remains Root/operator. UNKNOWN blocks dependent product
acceptance. No synthetic panel result closes the integrated milestone.

## Narrow correction and verify-only contract

A1. Root's isolated standard Node/JSDOM inspection of installed Playwright
1.62.1 shows that filling a `datetime-local` field with
`2026-01-01T00:00:00` normalizes its value to `2026-01-01T00:00`, while
`2026-01-01T00:00` round-trips unchanged; 12:00 follows the same rule.
Playwright's installed fill code rejects a supplied value when the resulting
input value differs. This is a test-executor defect that can explain the
failure, but the AM3 historical Chromium operation/cause was not captured
and remains UNKNOWN. AM4's reviewed browser procedure uses minute-format
values for every date field, checks each fill as a separately named fixed
stage, and records only an allowlisted error category. It never logs raw
errors, DOM, tokens, credentials or report bodies. No application UI/API fix
is authorized or inferred.

A2. A new AM4 entry under `scripts/p5a2_source_demo_verify_am4.py` may reuse
frozen AM3 guard, Docker, inventory, services and lifecycle helpers, but must
bind the *current* registered `PARTIAL_OWNED_FAILURE` / `HEALTH_FAILED`
volume-only owner digest above and its nine creation/eight cleanup entries.
It uses the same nonce, image ID, volume identity, private generated credential
reference and loopback ports. The new immutable exclusive AM4 marker has a
distinct ID/path and exact one-call counter. Prior markers cannot authorize it.
No predecessor source or packet edits, new volume/nonce/credential, reset,
DDL, migration, seed, CAS or application data write are permitted.

A3. After one externally budgeted read-only preflight and marker reservation,
at most one guarded PostgreSQL container may start over the retained volume
using the fixed local Docker CLI/pipe and existing PG_VERSION=16 guard. Use
the frozen AM3 `inventory(dsn,viewer)` and `post_seed_summary` in exactly two
RR/read-only connections before API/web. Both must independently prove
`EXACT_SEEDED`, 31 exact tables, users1/shifts36/assignments36/reports37,
other27zero, full raw/security/body equality, fingerprint
`afeb7f5ca42aec45a1bdc9f8a6d10c7401a401c080ce4b6097279badb3cadca9`,
schema digest `d1b13a0a45bad4c3607e5fbdb6439082df6f4b1ff3cd2f90398d4d0c228716db`
and state digest `d9418536c37fadc684a73ecfb2d2c67199bae29dfe5f43db5f12239b4ad8518b`.
Reuse frozen `verify_only` and its registered `EXACT_VERIFIED` zero-write
emitter. No `_native_seed`/`seed_transaction` call or write branch is reachable.
Any drift/empty/partial/foreign/sole timestamp state refuses before services.
The second SQL snapshot is the last database observation; zero writes means
AM4-owned call paths, not a post-UI global unchanged-database claim.

A4. After exact SQL, start at most one API and one web child. AM2 real JWT and
two HTTP digests `5523c755204ea4ee3e960394306c61d32d75d926806276748f99be481f6b0e64`
and `874e8e5693e1efeea30f92ab26ef48dacb00f0b0efa109f977fd3e8beba6f554`
are inherited, not replayed as native smoke. Immediately before contiguous
browser work, Root freshly checks exact container/volume/TCP and saved
API/web PID identity/liveness. A direct top-level awaited JS body (no `eval`)
creates one context, logs in once, fills canonical minute values, submits
the initial and later as-of queries once each, observes exactly two source
GETs and compares their canonical receipt hashes. Two real screenshots at
the admitted AM4 paths must visibly label both panels synthetic and show
36 eligible/36 selected/candidates36 then 36/36/37. A successful login alone
or placeholder screenshot is not UI acceptance.

A5. Before marker spend, Root prepares concrete ignored local verify/browser
and exact-owned failure-cleanup procedures, bound to current owner/volume and
future newly recorded CID/PID handles, and gets independent static review of
their actual hashes. Cleanup covers live and already-absent PID/stopped exact
container cases using the fixed local Docker transport, verifies identity
before stop/removal, never kills foreign resources, and retains old volume,
credentials and trails. Any failure spends the budget, records a fixed stage
and actual remaining resources, then stops without retry. Unknown custody
forbids destructive cleanup. On full two-query/two-screenshot proof, the
reviewed procedure also performs an automatic exact-owned shutdown of this
new runtime only, retaining volume/credentials. It checks accepted browser
proof and fresh exact owner/CID/PID/volume handles before stopping web/API/
container, then emits the existing registered `STOPPED_RETAINED` lifecycle
with stopped IDs from this verified runtime, fingerprint and remaining counts
volume1/containerAPIweb0. Failure stays `PARTIAL_OWNED_FAILURE` with
`HEALTH_FAILED`; unknown or partial cleanup stops for review. Neither path
restarts the runtime or grants another attempt. A successful UI proof remains
reviewable from its immutable receipts and screenshots after shutdown.

## Invariants and evidence limit

Reuse unchanged registered source, resource lifecycle and seed-recovery
families via `docs/cvf/INVARIANT_FAMILY_STANDARD.md`; no new outcome or copied
grammar. New inert source tests prove current owner/marker binding, strict
double-snapshot ordering, no seed/CAS, existing family output and refusal,
minute-format fill compatibility and stage/error-category policy. They are
not physical SQL/UI or AI-governance proof. Root evidence records actual
resource effects, read-only receipts, UI GETs/counts/screenshots or truthful
sanitized failure, and all spent counters. Review reconciles all G01–G14.
