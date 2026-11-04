# P5-A2 G04/G05 consolidated synthetic backend recovery

Status: DRAFT_CONTRACT
Date: 2026-10-27. Baseline: `08c62dad7b956faf7e1d1dd6cb56ee79e10cbead`.
Risk: R2. Roles: SPEC_AUTHOR for this contract; Root ORCHESTRATOR/effect and
commit owner; future backend IMPLEMENTATION_WORKER; independent REVIEWER.
This SPEC admits no BUILD or physical effect by itself.

## Product Milestone Binding

Milestone P5-A2 is the Phase 5 item in
`docs/implementation/EXECUTION_ROADMAP.md` at baseline `08c62da`.
The intended user outcome is an authorized integrated scheduled flow that
exposes signals, forecasts, source history and lineage, freshness, uncertainty
and abstention, and requires exact human run/version/source approval before
any durable recommendation or action. Full business acceptance remains in
`docs/specs/P5A2_PROACTIVE_REPORTING_SPEC.md` and the operator's decision.
Milestone evidence must cover actual source authority and retention, scheduler
and recovery, cohort/method fit, signal/forecast/drift quality, application
access and display, exact approval, integrated drills and applicable real
provider governance proof. The operator and independent reviewer accept those
criteria through their separately governed roadmap work. Mock output is never
AI-governance proof.

At this revision, accepted bounded evidence comprises native scoped fixture
history and physical PostgreSQL query substrate; source API and manual source
UI; pure numerical models; and Stage A synthetic backend source. The prior
Stage B start failed after one spent invocation. Its independent failed-result
material `555119e` and dedicated continuity `08c62da` are closed clean 15+5.
The only retained physical resource is the labeled volume, with registered
partial owner record and private generated local credential reference. The
database schema and contents are UNKNOWN. The exact standalone seed import
fails under the API-only launcher path. No API, web, smoke or UI proof occurred.
Normal API operational coverage is `None`; Phase 5 remains 0/5.

This assignment selects only the known synthetic G04/G05 local SQL/JWT/API/UI
proof. It repairs standalone child import roots and provides one reviewed
retained-volume recovery using the same owner nonce, named volume and existing
local generated credentials. It does not decide operational G04 or production
G05 coverage. Root owns effect, artifacts and commit; backend worker owns
source; independent reviewer owns authorization, actual-source checkpoint and
result. The finite return is physical synthetic proof or a recorded refusal,
then the P5-A2 integrated product gaps.

| Gap | Current evidence or limitation | In assignment | Accountable owner and concrete destination |
|---|---|---|---|
| G01/A7 | One real provider HTTP 401 spent; BLOCKED | No | Root/operator: P5-A A7, then P5-A2 |
| G02 | Operational RAG, context, index and citations BLOCKED | No | Backend/Root: P5-A2 context |
| G03 | Pure numeric policy accepted; business/cohort fit UNKNOWN | No | Backend/operator: P5-A2 method |
| G04 | Fixture memory, physical query substrate and API accepted; standing synthetic integration failed; operational integration UNKNOWN | Synthetic recovery only | Backend/Root: P5-A2 source for operational remainder |
| G05 | Fixture coverage accepted; production mode/authority/coverage/retention and positive SQLite UNKNOWN | Exact synthetic authority only | Backend/Root/operator: P5-A2 coverage for operational remainder |
| G06 | Native/HTTP identity and fresh release accepted; later use-time access OPEN | No | Backend/Root: P5-A2 approval |
| G07 | Scheduler, claim and recovery OPEN | No | Backend/Root: P5-A2 runtime |
| G08 | Pure signals accepted; operational quality OPEN | No | Backend/operator: P5-A2 signals |
| G09 | Pure forecasts accepted; operational accuracy OPEN | No | Backend/operator: P5-A2 forecasting |
| G10 | Pure residual/drift accepted; monitoring/display OPEN | No | Backend/UI/Root: P5-A2 quality and P5-B |
| G11 | Bounded source API/manual UI accepted; other application flows OPEN | Existing panel only | UI/Root/operator: P5-A2 application |
| G12 | Exact human approval OPEN | No | Backend/UI/operator: P5-A2 approval |
| G13 | Native fixture failures and stale/session UI drills accepted; integrated drills OPEN | No | Backend/Root: P5-A2 drills and P5-C |
| G14 | Live AI-governance proof HELD | No | Root/operator: separately admitted P5-A2 REVIEW |

P5-B dashboard/search/observability remains backend/UI/Root. P5-C backup,
resilience, security and performance remains backend/Root/operator. P5-D
deployment, Shadow Mode and release remains Root/operator. UNKNOWN means a
finite future verification decision, never accepted coverage. No whole gap,
milestone or Phase 5 item closes from this local synthetic tranche.

## Source and recovery contract

R1 — The launcher provides the exact trusted repository source roots needed
by the seed and complete demo app composition in clean isolated children.
Use explicit path construction under this project root, with no ambient
`PYTHONPATH`, `.env`, provider key, operator credential, package install or
normal application startup. A bootstrap helper may share this construction.
Clean standalone subprocess probes must import the real seed and compose the
real demo app with the exact marker and test injection, without DB, listener
or provider effects. Pytest's configured monorepo roots are not proof.

R2 — A distinct recovery entry point accepts only the registered
`PARTIAL_OWNED_FAILURE` volume-only state from the spent Stage B run. Under
the existing owner lock it validates exact profile, nonce, creation/cleanup
trail, named volume labels, pinned cached image ID, absent container and child
processes, fixed free loopback ports, private credential reference location and
file custody. It never generates a new nonce, volume, password, viewer secret
or JWT secret. It never reads or emits secret values into tracked artifacts.
Unknown, contradictory, foreign or already-running state refuses without a
physical effect. Existing start/preflight are not reused as if fresh.

R3 — Root reserves at most one new recovery attempt after all review gates.
Recovery may create at most one exact labeled container over the existing
volume, with `--pull never`, no new volume and no reset. Verify its exact
ID, image, labels and volume mount. Every Docker command must use the exact
`C:/Users/DELL/AppData/Local/Programs/DockerDesktop/resources/bin/docker.exe`
CLI and `--host npipe:////./pipe/dockerDesktopLinuxEngine`; ambient/remote
context routing, tag edits and pulls are forbidden. PostgreSQL startup is a bounded local
effect, including its possible internal WAL recovery; do not describe the
container phase as zero effect. Before any seed write, take a read-only,
repeatable-read SQL inventory of database name, server version, system
identifier, expected migration table/column/schema compatibility and counts
of ALL application tables. Record only secret-free identity, fingerprint,
schema verdict and counts. The initial database state is not guessed.

R4 — No migration replay, DDL repair, re-seed of partial data, deletion,
reset or volume replacement is authorized. Continue only if the already
created schema is compatible with all expected migration tables/columns and
either every application table is empty, or the four target tables have
exactly users=1, shifts=36, shift_assignments=36, reports=37 with every
other table empty. The native transaction-owned seed runs once for the empty
case, or native exact verification runs for the populated case. It must
reject partial/foreign rows, schema drift, mismatched model or report body
hashes, changed bundle/authority pins or viewer password mismatch. Recheck
all counts and identity after the permitted operation.

R5 — Only after R4 passes may one loopback API child and one static web child
start. Real JWT login and native source GET must return the two immutable
HTTP receipt digests `5523c755204ea4ee3e960394306c61d32d75d926806276748f99be481f6b0e64`
and `874e8e5693e1efeea30f92ab26ef48dacb00f0b0efa109f977fd3e8beba6f554`.
The accepted panel must visibly label both views synthetic and show the
initial 36 eligible/36 selected/36 candidates and later 36/36/37. Use one
browser context, two submits and two screenshots. The SQL proof must show
one user, 36 shifts, 36 assignments and 37 reports. HTTP/UI data are the
authorized synthetic source, not operational data.

R6 — On failure, preserve the original spent evidence, original owner
creation/cleanup trail, volume and local credentials. Clean only new exact
owned child processes and the newly created exact owned container, verifying
identity immediately before each effect. Record the new trail and all
remaining resources; refuse ambiguous cleanup. No automatic retry or later
stop is in this contract. A successful profile retains exactly the existing
volume plus one owned container, API and web process for inspection.

## Evidence, invariants and phase decision

The existing `P5A2-SOURCE-DEMO-RESOURCE-LIFECYCLE` family at canonical digest
`f323ef1062e791c1c8fa4bff880b765a79547b571b0cfca9083286d680dcef2c`
and existing source family at
`6fec188950fe752ac438e2952ec3d4e2ffd3b4156efa0b9a2e06e1048c568754`
remain unchanged. Follow
`docs/cvf/INVARIANT_FAMILY_STANDARD.md`; do not copy matrix rules or create a
second lifecycle grammar. Contextual owner, mount and fingerprint checks
supplement the registered record adapter. Run `python scripts/check_invariant_families.py`
before REVIEW/FREEZE if any family surface changes.

DESIGN selects one combined SOURCE+physical recovery BUILD. An independently
reviewed normal Work Order dispatch, dedicated actual-SHA five-path
continuity commit and independent clean range precede BUILD. During that
BUILD, focused source/import tests and an independent actual-hash source
checkpoint pin every changed source file and frozen predecessor before the
single physical reservation. Source can remain uncommitted until the
integrated result material, but its accepted bytes are immutable through
physical proof. A failed checkpoint or changed source pin stops physical
work. This preserves phase gates without a separate source-only tranche.

## Amendment 2 — retained seed outcome and conditional one-field repair

Status: CANDIDATE, operator scope approved 2026-10-27; BUILD and effects held
pending independent authorization and normal dispatch. Current revision is
`bc894360f4d6a532ca5554a3e1fb3d3ef1a384ea`. This section supersedes R4
and the old one-attempt budget only where stated; R1–R3 and R5–R6 continue to
bind the same G04/G05 synthetic acceptance unit. The predecessor failed-result
material `68d40b0` and continuity `bc89436` passed independent clean 17+5.
The old recovery attempt and AM1 preflights are spent and immutable. Its
prewrite inventory found a compatible empty 31-table PG16.15 database; the
native seed then failed. The transaction may have committed before its later
verifier failed, so present rows are UNKNOWN. The last exact container was
removed; one original labeled volume remains, API/web zero. The current owner
digest is `45c1678e3ba0c1972248588a895db01d205897a585f3fefb37d0b9e9cb810511`.

The operator approved exactly the concrete proposal in the predecessor
RETURN: demo seeder source and focused tests, read-only retained inspection,
conditional one-field correction of the synthetic user's `created_at`, and
maximum one new reviewed recovery without reset. The observed failure's
exception was not retained. The frozen user timestamp versus migration
`DEFAULT now()` is a source-supported hypothesis, not a finding about current
rows. No prior effect budget is refreshed or historical record rewritten.

AM2-S1 — Admit only `apps/workspace-api/src/workspace_api/demo/seed.py`,
necessary bounded `apps/workspace-api/src/workspace_api/demo/seed_*.py` splits,
focused `tests/unit/test_p5a2_demo_seed*.py`, and existing recovery entry,
inventory, custody helpers and matching focused recovery tests only if needed
for the new owner digest, read-only record comparison and atomic guard. Keep
every file at or below 300 Python lines. Global ledger, shared user
persistence, migrations, normal API/UI, fixtures, oracles, ACLs and secret
storage are frozen. The shared user-row writer omits `created_at`, so use a
demo-local explicit user INSERT including that frozen field within the existing
single transaction; do not alter the shared ledger writer. Seed construction
must persist the exact frozen
`created_at` for a new synthetic user inside its existing single transaction;
it must retain exact post-insert equality and the existing password hash
verification. A partial seed failure rolls back all inserted rows. Tests
exercise actual native SQL statement/transaction behavior with inert fakes or
disposable test data, including no write before full validation.

AM2-S2 — An independently reviewed source checkpoint pins every changed
source/test raw and LF hash, remaining frozen source/oracle/migration pins,
and the new seed-recovery invariant matrix before effects. A fresh AM2
read-only external preflight (maximum one) validates the unchanged exact
owner nonce, volume, image, loopback ports, private credential reference and
new owner digest. One exclusive AM2 reservation marker is created before the
sole AM2 recovery call. Old attempt markers cannot be reused. Recovery may
create at most one new exact owned container over the same existing volume;
the last failed container ID is known absent. No new volume/nonce/credentials,
migration, schema repair, reset, deletion or official Postgres auto-init.
Every Docker command uses the fixed local CLI and Desktop Linux pipe already
specified in R3. PostgreSQL internal WAL recovery on startup is permitted.

AM2-S3 — Before any application write, one consistent REPEATABLE READ, READ
ONLY inventory must record database/version/system-ID fingerprint, exact
schema/table/column verdict, all 31 table counts, and exact canonical
comparison of every synthetic user, shift, assignment and report field,
including password verification, role, IDs, timestamps, report/body hashes,
authority and source pins. Compare raw installed columns as well as native
model equality, so an unmodeled stored field cannot pass silently. Capture
only secret-free pass/fail summaries and
digests, not row bodies, password hashes or credential values. Compare against
the frozen bundle and authority using native model and persistence semantics.
The sole permissible prewrite states are: all 31 counts zero with compatible
schema; exact target counts plus exact row/security/hash equality; or exact
target counts plus equality of every field except this profile's one frozen
synthetic user's `created_at`. Any partial/foreign count, extra row, missing
field, mismatched hash/password/role/ID/other timestamp, fingerprint or
authority pin refuses with zero application writes. An unknown comparison is
a refusal. Inspection and comparison must complete before choosing a write.

AM2-S4 — Guard against time-of-check/time-of-use drift: the single write
transaction acquires protection on all 31 application tables and target rows
BEFORE full revalidation, then reclassifies empty/exact/sole-timestamp under
that same transaction. It revalidates exact owner/database/system-ID, source pins, schema, all counts
and every relevant raw column/row/security/hash predicate under locks on all
31 application tables that prevent a
concurrent application writer from changing the approved set. If this cannot
be proved with the existing native transaction/locking surface, refuse without
writing. The read-only inventory and this separate locked transaction are
distinct budgeted connections. For empty state, run the corrected atomic seed once; exact seeded
state performs native verification with no write. For the sole timestamp
mismatch state, perform one compare-and-set `UPDATE` of only `users.created_at`
for the exact synthetic user ID, matching the observed old timestamp, role,
immutable security identity and exact stored password-hash value as a CAS
predicate within the same owned transaction. Require exactly one affected
row, then exact raw-column/native-model readback before commit; failure rolls
back. Preserve the current password-hash bytes, role, ID and every other
byte/value. Existing recovery's SEEDED/VERIFY-only expectation must become
an explicit mapping for `SEEDED`, `VERIFY` and `CREATED_AT_REPAIRED`, with the
refusal outcome distinct and no second branch. No loose
`UPDATE`, broad timestamp normalization, retry, or repair of other data.
Post-operation read-only summary must recheck fingerprint, all counts and
exact raw-column/native-model row equality, not counts alone; no API/web
startup precedes this acceptance.

AM2-S5 — Accepted physical outcome remains exact SQL users=1/shifts=36/
assignments=36/reports=37, real JWT and native HTTP receipts
`5523c755204ea4ee3e960394306c61d32d75d926806276748f99be481f6b0e64`
and `874e8e5693e1efeea30f92ab26ef48dacb00f0b0efa109f977fd3e8beba6f554`,
then actual UI synthetic 36/36/36 and 36/36/37 in one browser context with
two submissions and two screenshots. One failure ends this AM2 budget;
preserve old trails, owner record, volume and credentials and clean only new
exact owned children/container after fresh identity verification. No new
automatic support tranche follows. Operational G04/G05 and all other
G01–G14 remainders in the binding table remain OPEN/UNKNOWN/BLOCKED/HELD;
Phase 5 stays 0/5. The product return is to P5-A2 integrated context,
runtime, quality, approval and drills after bounded synthetic proof or safe
refusal.

The `REFUSED_ZERO_WRITE` seed-family outcome is emitted only when a prewrite
refusal or transaction rollback proves zero durable application writes and
database identity/fingerprint was observed. Lost commit acknowledgment or a
postcommit failure leaves database state UNKNOWN, with no invented zero-write
outcome or fingerprint; the separate outer recovery failure/custody receipt
records that uncertainty. An established seed-family outcome may coexist
with a later outer API/web/smoke failure without erasing its established
database result.

## AM2 invariant-family admission

The new seed/recovery outcome contract triggers the invariant-family standard:
one classification controls whether a write is permitted, with multiple
inventory/native verifier/owner-receipt surfaces and exact zero-or-one write
relations. The independent contract source is the immutable predecessor
`P5A2_SYNTHETIC_BACKEND_RECOVERY_RETURN_2026-10-27.md` proposal plus this
pre-code AM2 specification. Register
`P5A2-SOURCE-DEMO-SEED-RECOVERY-OUTCOMES` under
`docs/cvf/invariants/p5a2-demo-seed-recovery.json` before implementation;
pin its canonical digest and materialize only bounded seed/recovery adapters
and focused tests against it. The existing resource-lifecycle and scoped
source families remain unchanged. Invariant-family structural tests alone do
not establish physical SQL, HTTP or UI proof.
