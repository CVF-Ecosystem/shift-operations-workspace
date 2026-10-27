# P5-A2 synthetic source verify-only continuation, Amendment 3

Status: DRAFT_CONTRACT
Date: 2026-10-27. Baseline: `153531bfa525cf56c2bd2758107bda345ab8b500`.
Risk R2. Operator authority: “Cho phép 1 lượt verify-only.” This is the
same G04/G05 SQL → JWT/API → UI acceptance unit, with one new runtime/browser
budget. SPEC_AUTHOR → WORK_ORDER_AUTHOR; Root owns effects, artifacts and
commit; a later IMPLEMENTATION_WORKER owns bounded source; REVIEWER is independent.
No BUILD or physical effect is released by this draft.

## Product Milestone Binding

P5-A2 in `docs/implementation/EXECUTION_ROADMAP.md` at the baseline above
requires an authorized integrated scheduled flow for signals, forecasts,
source history and lineage, freshness, uncertainty and abstention, with exact
human run/version/source approval before any durable recommendation or action.
Full acceptance is in `docs/specs/P5A2_PROACTIVE_REPORTING_SPEC.md`: operational
source authority and retention, scheduler/recovery, cohort/method fit,
signal/forecast/drift quality, application access/display, exact approval,
integrated drills and applicable real provider governance proof. Operator and
independent reviewer accept the milestone; mock output cannot prove AI governance.

Accepted source and physical evidence at `153531b`: scoped fixture history,
PostgreSQL query substrate, source API/manual UI, pure numeric models, AM2
canonical source repair (104 worker/102 independent source tests), and actual
retained PostgreSQL 16.15 SQL users1/shifts36/assignments36/reports37 with
all 27 other tables empty. AM2 used one guarded `PUBLIC_ACTOR.created_at` CAS;
real JWT and both frozen HTTP receipts passed. AM2 UI failed at LOGIN after one
browser context and before any login/query/screenshot. The exact exception and
later runtime termination cause are unknown. Reviewed cleanup left the same
volume only, container/API/web absent, owner digest
`3af5e4892aaea7bfe64422ed7f3b237a6d54f910c8e2d0dbc68e6e925b9599ab`.
AM2 budgets and records are spent/immutable. Operational coverage is UNKNOWN;
Phase 5 remains 0/5.

This assignment addresses only the missing *synthetic* UI portion of G04/G05:
one custody-bound verify-only runtime with no application data writes, followed
by one actual browser context that displays synthetic 36/36/36 and 36/36/37
for the two frozen as-of queries, with two screenshots. It closes no whole gap
or milestone. Root is effect and artifact owner; backend worker owns the guard;
UI/Root own actual panel evidence; independent reviewer checks source and
result. Failure or pass returns directly to P5-A2 product integration.

| Gap | Current evidence and remainder | In AM3 | Owner and roadmap destination |
|---|---|---|---|
| G01/A7 | Real provider 401 spent; BLOCKED | No | Root/operator → P5-A A7, then P5-A2 |
| G02 | Operational RAG/context/index/citations BLOCKED | No | Backend/Root → P5-A2 context |
| G03 | Pure numeric accepted; business/cohort fit UNKNOWN | No | Backend/operator → P5-A2 method |
| G04 | SQL/JWT/HTTP synthetic accepted; actual UI missing, operational integration UNKNOWN | Synthetic UI only | Backend/Root → P5-A2 source |
| G05 | Exact synthetic data accepted; production mode/authority/coverage/retention/SQLite UNKNOWN | Exact synthetic UI only | Backend/Root/operator → P5-A2 coverage |
| G06 | Identity/fresh release accepted; later use-time access OPEN | No | Backend/Root → P5-A2 approval |
| G07 | Scheduler/claim/recovery OPEN | No | Backend/Root → P5-A2 runtime |
| G08 | Pure signals accepted; operational quality OPEN | No | Backend/operator → P5-A2 signals |
| G09 | Pure forecasts accepted; operational accuracy OPEN | No | Backend/operator → P5-A2 forecasting |
| G10 | Pure drift accepted; monitoring/display OPEN | No | Backend/UI/Root → P5-A2 quality, P5-B |
| G11 | Source API/manual UI accepted; other flows OPEN | Existing source panel only | UI/Root/operator → P5-A2 application |
| G12 | Exact human approval OPEN | No | Backend/UI/operator → P5-A2 approval |
| G13 | Fixture/session drills accepted; integrated drills OPEN | No | Backend/Root → P5-A2 drills, P5-C |
| G14 | Live AI governance proof HELD | No | Root/operator → separately admitted P5-A2 REVIEW |

P5-B dashboard/search/observability remains backend/UI/Root; P5-C backup,
resilience/security/performance remains backend/Root/operator; P5-D deployment,
Shadow Mode/release remains Root/operator. UNKNOWN stays a blocker, never an
accepted result. A successful local synthetic panel does not prove operational
coverage or the whole integrated scheduled product.

## Verify-only and custody requirements

V1. Preserve the exact existing volume `shiftops-p5a2-source-demo-data-v1`,
owner nonce `3bf4a4c5d48d0f4ffc8a96a5aecfccaae6c07a9820cf8f7cf8757cf500ead999`,
private generated credential reference, immutable cached image ID
`sha256:f4610795587492cd4fb887c2dc3de301b813278bb6f616992061141b5f15ac36`,
local loopback ports 5433/8001/5174 and Docker Desktop Linux pipe. Preflight
must bind the latest `PARTIAL_OWNED_FAILURE` owner digest above, reason
`HEALTH_FAILED`, volume-only resource counts 1/0/0/0 and all creation/cleanup
trails including the AM2 container. Validate exact labels/mount/image/volume
identity, absent container/API/web, private owner/secret custody, free ports
and no contradictory residue. No new owner, nonce, credential or volume.

V2. Before reservation, Root prepares a concrete ignored local failure-cleanup
procedure and obtains independent static review against the *current* owner
and volume baseline. It accepts only the newly recorded container/PID handles
after creation, then checks their exact live identity. It covers both live API/web children and the
already-absent PID/stopped-container route observed in AM2. Every Docker
operation uses the fixed local CLI/pipe; each process/container is freshly
matched to the newly created exact owned identity before any stop/removal.
Foreign or ambiguous identity forbids a kill/removal, and the old volume and
credentials remain. Only after this reviewed cleanup plan, independent source
checkpoint and one read-only preflight may Root reserve a new exclusive
immutable AM3 marker. Marker binds ID, profile,
owner nonce/digest, image ID, exact budget and `RESERVED_SPENT_NO_RETRY`; it
cannot be confused with either spent predecessor marker. One container may
start over the retained volume using the fixed local Docker CLI and explicit
`--host npipe:////./pipe/dockerDesktopLinuxEngine`, `--pull never`, exact
labels/mount/loopback binding, and the existing PG_VERSION=16 guard that
bypasses the official auto-init entrypoint. PostgreSQL internal startup/WAL
is a bounded effect; no application data write, migration, DDL, reset or
deletion is allowed.

V3. After DB readiness, use the already accepted
`inventory(dsn, viewer_password)` in one repeatable-read/read-only connection.
Require `EXACT_SEEDED`, all 31 expected tables and all raw columns/security/
password/body values, counts 1/36/36/37 with 27 others zero, database
fingerprint `afeb7f5ca42aec45a1bdc9f8a6d10c7401a401c080ce4b6097279badb3cadca9`,
schema digest `d1b13a0a45bad4c3607e5fbdb6439082df6f4b1ff3cd2f90398d4d0c228716db`
and state digest `d9418536c37fadc684a73ecfb2d2c67199bae29dfe5f43db5f12239b4ad8518b`.
Immediately use existing `post_seed_summary` in a second RR/read-only
connection, requiring the same exact schema/state/fingerprint/rows/counts.
Both inspections precede API/web startup. Any empty, partial, foreign,
sole-timestamp, changed hash or unknown state refuses. There is NO native
seed child, `seed_transaction`, INSERT, UPDATE or CAS in AM3. Emit the existing
registered seed-family `EXACT_VERIFIED` zero-write result only after both
complete inspections; receipt may not claim zero writes after an unknown
commit or unverified transaction.

V4. Start at most one API and one web child using existing clean environment
and approved services helpers only after V3 passes. Prior real JWT/two HTTP
digests `5523c755204ea4ee3e960394306c61d32d75d926806276748f99be481f6b0e64`
and `874e8e5693e1efeea30f92ab26ef48dacb00f0b0efa109f977fd3e8beba6f554`
are inherited, not rerun. Native smoke budget is zero. Immediately before
contiguous browser work, freshly verify exact owned container identity and
running state, saved API/web PID identity and liveness, readiness and owner
digest. The browser executor uses one direct top-level awaited JS body, no
`eval`; one context, one login, two frozen as-of submissions/GETs and two
screenshots. Each panel must visibly say synthetic and show 36 eligible,
36 selected, candidates 36 then 37. Save exact screenshots to the admitted
AM3 paths. Do not capture credentials, JWT, report bodies or full exceptions.

V5. On failure, preserve all old packets, trails, volume and credentials.
Execute only the independently reviewed exact-owned cleanup procedure. Stop
only the newly created exact owned API/web processes and container after
fresh identity checks. The already-absent PID/stopped-container route verifies
absence and removes only the exact stopped new container. Register actual
remaining resources and a fixed
sanitized failure stage; ambiguous custody remains UNKNOWN and stops cleanup.
No retry, additional browser context, restart or data repair. Success keeps
the newly owned runtime only under the reviewed result disposition; any later
stop is separately governed.

## Invariant and evidence boundary

Reuse registered `P5A2-SOURCE-DEMO-RESOURCE-LIFECYCLE` and
`P5A2-SOURCE-DEMO-SEED-RECOVERY-OUTCOMES` matrices at the pinned AD digests;
see `docs/cvf/INVARIANT_FAMILY_STANDARD.md`. No new outcome or copied grammar.
Focused source tests must include a canary that fails if `_native_seed` or
`seed_transaction` is called, both read-only digest mismatch branches, owner
and marker mismatch, unknown cleanup, and existing adapter/full mutation
corpus. These inert tests are not physical SQL/UI or AI-governance proof.
Root's AM3 evidence records two real read-only receipts, zero application
writes by AM3-owned call paths, resource effects, actual browser outcome/screenshots or precise
sanitized refusal, and all spent counters. The result review reconciles all
G01–G14 and claim limits. The second SQL snapshot is the last pre-service
observation. UI success may cite that snapshot and the frozen read-only
login/source routes; no post-UI SQL observation exists in this budget, so no
claim that the global database is unchanged after UI is allowed. Provider/API key/model, public network, installs,
pulls, deployment and push remain outside this contract.
