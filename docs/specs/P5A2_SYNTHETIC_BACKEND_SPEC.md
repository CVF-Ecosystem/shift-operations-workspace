# P5-A2 G04/G05 synthetic PostgreSQL development backend

Status: SYNTHETIC_DEVELOPMENT_BACKEND_IMPLEMENTATION_CONTRACT
Date: 2026-10-26; baseline `674d98e35f0fbafa868c34d3c3adbdd215ef3aa5`; R2.
Roles: Root SPEC_AUTHOR/WORK_ORDER_AUTHOR and effect/commit owner; backend worker
future implementation; independent REVIEWER acceptance. This document is a
pre-code contract; BUILD requires admitted Work Order and committed dispatch.
Physical execution requires a separate Stage B Work Order.

## Product Milestone Binding

Milestone P5-A2, `docs/implementation/EXECUTION_ROADMAP.md` Phase 5, at the
baseline above. Its user outcome remains an authorized, integrated scheduled
flow for signals, forecasts, history, lineage, freshness, uncertainty and
abstention, with exact human run/version/source approval before any durable
recommendation or action. `P5A2_PROACTIVE_REPORTING_SPEC.md` and the operator
own full business acceptance. Native fixture source, real PostgreSQL substrate,
bounded authenticated source API and the manual source UI have independent
bounded acceptance. Normal API coverage is `None`; operational source history,
retention, quality and business fit are not established. Phase 5 stays 0/5.

This contract selects a finite G04/G05 development path: a persistent,
isolated local PostgreSQL database seeded with a coherent synthetic 36-shift,
36-assignment, 37-report-version history; an exact synthetic-only server
coverage descriptor; real JWT login; native source API; and the accepted G11
source panel displaying a synthetic label. Stage A can establish code and
in-process contracts. Stage B physical SQL/API/UI proof requires a later,
separately admitted execution Work Order and budget. Root owns contracts,
effects and commit; backend worker owns implementation, independent reviewer
owns acceptance. No UNKNOWN operational completeness is a BUILD precondition.

| Gap | Current truth and remainder | This contract / owner / destination |
|---|---|---|
| G01/A7 | One real provider 401 spent; A7 BLOCKED | NO; Root/operator, P5-A A7 then P5-A2 |
| G02 | Operational RAG/context/index/citations BLOCKED | NO; backend/Root, P5-A2 context |
| G03 | Pure numerical policy accepted; business/cohort fit open | NO; backend/operator, P5-A2 method |
| G04 | Native fixture memory/PG and API accepted; operational integration UNKNOWN | YES synthetic local plumbing only; operational remainder backend/Root, P5-A2 source |
| G05 | Fixture coverage accepted; production authority/mode/coverage/retention and positive SQLite UNKNOWN | YES exact synthetic authority only; operational remainder backend/Root/operator, P5-A2 coverage |
| G06 | Native and HTTP identity/fresh release accepted; later use-time access open | NO; backend/Root, P5-A2 approval |
| G07 | Scheduler/claim/recovery open | NO; backend/Root, P5-A2 runtime |
| G08 | Pure signals accepted; operational quality open | NO; backend/operator, P5-A2 signals |
| G09 | Pure forecasts accepted; operational accuracy open | NO; backend/operator, P5-A2 forecasting |
| G10 | Pure residual/drift accepted; monitoring/display open | NO; backend/UI/Root, P5-A2 quality and P5-B |
| G11 | Bounded source API/manual UI accepted; other flows open | This uses accepted UI without changing it; UI/Root/operator, P5-A2 application |
| G12 | Exact human approval open | NO; backend/UI/operator, P5-A2 approval |
| G13 | Native fixture failures and UI stale/session drills accepted; integrated drills open | NO; backend/Root, P5-A2 drills |
| G14 | Live AI-governance proof HELD | NO; Root/operator, separately admitted P5-A2 REVIEW |

P5-B dashboard/search/observability stays backend/UI/Root; P5-C backup,
resilience, security and performance stays backend/Root/operator; P5-D
deployment, Shadow Mode and release stays Root/operator. The product return is
one accepted bounded local synthetic source path, then an explicit return to
integrated runtime, quality, context and approval gaps. No whole gap or
milestone closes from fixture integration.

## Independent pre-code inputs and authority

Root freezes, before loader/verifier BUILD, three independent artifacts:

1. `fixtures/p5a2_source_demo_v1.json`: full synthetic 36 shifts,
   36 active assignments and 37 immutable END_SHIFT report versions, including
   whole canonical report sections, source manifest and snapshot digests.
   Top-level `bundle_version` is `P5A2-SOURCE-DEMO-DATA-1`; the actor is
   `PUBLIC_ACTOR`; the user descriptor has username `source-demo-viewer`
   and role `viewer` but no password, hash, JWT key or database secret.
   Its fixture ID is `P5A2-SOURCE-DEMO-1` and instance ID is fixed below.
2. `fixtures/p5a2_source_demo_authority_v1.json`: metadata-only,
   synthetic-only authority for fixed instance
   `P5A2-SOURCE-DEMO-LOCAL-1`, actor, accepted cohort/numeric policies,
   exact two approved UTC windows/as-of values, expected eligible and
   candidate metadata including immutable digests, fixture identity and
   dataset hash. Top-level `authority_version` is
   `P5A2-SOURCE-DEMO-AUTHORITY-1`; `coverage_mode` is
   `SYNTHETIC_FIXTURE`; two profiles each carry `case`, `coverage_seed` and
   `coverage_seed_digest`. It contains no report body or credential.
3. `tests/fixtures/p5a2_source_demo_oracle.json`: two complete expected HTTP
   SOURCE_READY receipts for the NEW server scope and fixture identity,
   computed offline from independently frozen prior API/body inputs before
   new seed/verifier code. Changed scope and dataset identity require complete
   new receipts; replacing only expected hashes is invalid.

Independent pre-code bytes now exist: data SHA-256
`5a7f1dbc61fbdc40b4c201763c18c463902ea8d928ad105eddeff7b16a617cae`,
authority SHA-256
`3ed09877a15b7bbd9ae1178392e6262688607e73a678a95c86e0132e213baecb`,
and test-only oracle SHA-256
`b43b5aa27cd593ba560cc48e534d7c7c12f2299d084d8c45dcbfb40a5c1a6aca`.
The fixed server self-scope is
`P5A2-SELF-77b89304823a5d39f60ff3872317a3d2de8403b72b740f33140cfc61aca03311`.
Both profiles use `2026-01-01T00:00:00Z` through
`2026-01-02T12:00:00Z`; their as-of values are respectively
`2026-01-02T12:00:00Z` and `2026-01-02T14:00:00Z`. They admit 36 eligible
shifts and respectively 36/37 candidate report versions. All 37 immutable
report body hashes were independently checked against the prior frozen body
oracle; the complete new source receipts were derived offline from prior
frozen inputs. These files have no secret or operational-completeness flag.

Root records exact raw SHA-256 pins, recipe, predecessor hashes and independent
review in an admission artifact before dispatch. The three paths are frozen
inputs, never worker-edited. Tests may import them; runtime must load only a
separately owned deployable data bundle and metadata authority under
`apps/workspace-api/src/workspace_api/demo/` whose bytes are checked against
those Root-frozen hashes. The two deployable JSON files are byte-exact copies
of their frozen input counterparts, checked at Stage A and runtime; there is no runtime
`tests/` import or arbitrary user-selected JSON path. The descriptor is
synthetic authority for these exact records only. No `complete=true` request,
client fixture selector, role header, policy override or operational source
enrollment is accepted.

## Stage A functional contract

R1 — Isolated settings and application. Normal `settings = Settings()` behavior,
normal `main.app`, source dependency `get_proactive_source_coverage() -> None`,
and all existing routes remain unchanged. A separate demo entry point must
recognize one exact isolated profile marker before importing auth/router
modules that instantiate module-level settings. Under that marker only, the
settings seam disables dotenv and accepts a strict allowlist of child-process
values: `NO_AI`, a generated JWT signing secret of at least 32 bytes, a
loopback PostgreSQL DSN for the owned database, fixed source instance, and
loopback CORS origin. A clean child environment prevents ambient API/provider
keys and operator `.env` from entering. If marker, values, database identity,
or trusted bundle/authority checks fail, startup refuses before binding a
listener. Never import `main.app` or unrelated P4-E service composition to
construct this demo. The demo app uses its exact loopback CORS allowlist,
not the normal development wildcard. No global settings mutation after import.

R2 — Durable native data. Stage A defines an idempotent, transaction-owned
seeder for the exact frozen synthetic dataset. It checks migrations/schema,
owned database identity, schema version and all expected row/digest counts
before declaring `SEEDED`. It refuses mismatched or partly preexisting
records; it never truncates, deletes, resets a volume, appends a second
cohort, or falls back to memory/SQLite. Immutable report bodies and hashes
must match the frozen bundle. A viewer-only synthetic user uses a password
generated in Stage B and hashed with the existing real password machinery;
the password and JWT key never enter Git, fixture JSON, logs or evidence.
Only the owned database may be written, and seeding is not executed in Stage A.

R3 — Exact coverage. The development `CoverageVerifier` checks the exact
fixed instance, actor, policy pair, normalized approved start/end/as-of,
fixture ID/dataset hash and every bounded native `CohortKey`/`CandidateKey`
field against the frozen metadata descriptor. It returns the accepted fixture
ID and deterministic metadata digest only for an exact match. Absent/untrusted
descriptor maps to native `COVERAGE_UNKNOWN`; a previously admitted fixture
whose actual cohort/candidates differ maps to native `SCOPE_INCOMPLETE`.
Wrong policy remains `INCOMPATIBLE_POLICY`; denied actor remains
`ACCESS_DENIED` under native precedence. It never reads report bodies or
performs source queries itself. Native `query_source`, fresh release, caps,
closed receipt grammar and canonical manifest/digest remain authoritative.
No production mode can select this verifier.

R4 — Real but narrow HTTP composition. The demo app uses the existing real
`POST /auth/login`, `GET /auth/me` and `GET /proactive/source` handlers with
the owned `SqlLedger`, real stored viewer, actual signed/verified JWT and
canonical assignment check. Add only the safe GET routes the current
`OperationsConsole` needs for source-panel mounting and optional shift
selection, explicitly allowlisted in one read-route table; no generic router
inclusion may accidentally expose POST/PUT/PATCH/DELETE or P4-E routes.
Each allowed read reuses the existing GET handler and native ledger query after
strict finite verified JWT, current stored viewer/actor and assignment guards.
Data comes from the owned synthetic PostgreSQL dataset. Empty results may
appear only when the real query is empty; no fabricated empty operational
response substitutes for a database read. The demo app's OpenAPI route set is
tested exactly. The source panel
must remain manual and display `Dữ liệu thử nghiệm` for READY; refusal is
truthful when authority is absent/mismatched. No frontend feature or shared
API transport behavior changes in this tranche.

The allowlist is `POST /auth/login`; `GET /auth/me`, `/proactive/source`,
`/health`, `/shifts`, `/staffing/shifts`, `/staffing/users`; and, only for a
selected authorized synthetic shift, `GET /events`, `/shifts/{shift_id}/open-work`,
`/incidents`, `/handovers`, `/messages`, `/tasks`, `/customer-requests`,
`/shifts/{shift_id}/capabilities`, `/reports`. `/shifts` exposes only assigned
synthetic shifts. Staffing GETs reuse the canonical viewer denial (403).
Selected-shift GETs use existing read behavior against the synthetic database;
capabilities cannot grant mutation authority through this demo route set.
Every endpoint still checks the real bearer/current user and selected shift
assignment. Unknown path/method returns 404/405 without a mutation. The
exact path/method set is asserted; no complete normal router is mounted.

R5 — Error, privacy and evidence. All auth and source denials retain the
accepted fixed status/body and no-store behavior. No DSN, password, JWT,
raw SQL, raw report body or private source manifest is emitted in diagnostics,
lifecycle records or secret-free execution metadata. Authorized SOURCE_READY
HTTP legitimately carries the complete native raw
receipt to the browser; the accepted UI safe projection owns DOM/state
minimization. In-process tests use actual TestClient/auth token issuance and
native source path; test-only dependency injection may stand in for physical
PostgreSQL only when explicitly labeled nonphysical. They compare complete
response bodies with both frozen new-scope oracles and test mismatched hash,
cohort, candidate, actor, policy, window, absent descriptor, stale assignment,
default normal refusal, no memory fallback and route allowlist negatives.

## Stage B physical profile contract, HELD

Stage B is a separate effect Work Order after accepted Stage A source, normal
material commit, actual-SHA continuity and clean split-range closure. It
authorizes at most one newly owned persistent PostgreSQL 16 container/volume,
one loopback API process and one loopback static web process, with a bounded
single seed and two approved query contexts. Only a locally cached, inspected
`postgres:16` image may be used, with no pull or install. A dedicated
PostgreSQL-only compose file uses an owned project/container/volume name and
explicit `network_mode: bridge`, reusing Docker's existing default bridge;
it declares no new network and creates no Compose project network. It
binds PostgreSQL at `127.0.0.1:5433`; API uses `127.0.0.1:8001` and static
web uses `127.0.0.1:5174`. All three ports must be free before effects; the
repository's full-stack
`docker-compose.yml` is forbidden here. Image absence, port collision,
ambiguous prior ownership, partial state or unknown DB/profile fails before
effects. Preflight also verifies the existing project Python environment,
`psycopg`/SQLAlchemy, exact cached Node `22.14.0`, installed frontend packages
and migration file set without installation. Migrations and seed run only
against the newly owned database.

The profile-only frontend build config must set `envDir: false` and explicit
`VITE_API_URL=http://127.0.0.1:8001`, direct cached Node `22.14.0` CLI and
an ignored output under `.venv/`. Normal Vite config and UI code stay
unchanged; no frontend `.env` is read.

The launcher writes an owner record in a task-specific user-local runtime
directory outside Git: exact container/volume IDs, database fingerprint,
image ID, chosen ports, generated secret references and child PIDs. It passes
only allowlisted environment values to hidden background processes; Windows
background helpers use `Start-Process -WindowStyle Hidden` unless an explicitly
interactive browser is selected. Secrets
are generated in memory or stored with local user-only access, never on CLI,
committed files or evidence. Success leaves the verified backend in
`OWNED_RUNNING` with exact handles and stop instructions, so the user can
inspect the live synthetic UI and database. `stop` executes only on explicit
later invocation; it validates exact IDs/PIDs, stops only owned
API/web/container processes and retains the named volume for inspection.
Volume deletion, seed reset and unrelated-process termination are separate
destructive actions with their own authority. A secret-free receipt records
ownership IDs, PG version, migration/schema checks, counts/digests, actual
SQL/JWT/native HTTP responses for both approved contexts and real browser UI
only if that later WO explicitly budgets a browser. No simulated database or
provider response may be reported as physical proof. Old one-shot source
rehearsal budgets are spent and cannot be reused.

## Invariant family and evidence gate

The registered `P5A2-SCOPED-SOURCE-OUTCOMES` matrix at native LF SHA-256
`cb0fb2427848d58aaf44a3c675f3a4d9d4d59cc38214993684eb5cd4dc492243`
continues to own native/HTTP/UI receipt outcomes; its shapes, domains,
relations and mutation rules do not change. Root must freeze a recoverable
metadata-only patch adding this SPEC, real new verifier/seed and evidence
paths, then recompute the matrix digest and update all four literal consumers
only after real files exist. Original API/UI/PG oracles remain immutable.
Follow `docs/cvf/INVARIANT_FAMILY_STANDARD.md`; do not copy its matrix rules
into implementation prompts.

Persistent container/process ownership has lifecycle states and cross-agent
mutation evidence, so the invariant-family applicability trigger is met for
Stage A code and Stage B effects. The independent pre-code normative source
for Root's proposed `P5A2-SOURCE-DEMO-RESOURCE-LIFECYCLE` family is below.
Root must register a complete matrix and real docpin before Stage A dispatch;
the first registration is STATIC_CONTRACT_ONLY, with no runtime acceptance
claim. Its initial consumer is the Root-owned docpin and existing generic
family tests. Root freezes a full prospective metadata extension and final
digest for the future real lifecycle adapter/tests. Only after those files
exist may Root add their actual paths/pins, followed by independent binding
review before focused tests. No unregistered shared startup receipt or
lifecycle grammar is invented in code. Before Stage A REVIEW/FREEZE run
`python scripts/check_invariant_families.py` after the real source-family
binding; Stage B runs both registered families with physical evidence.

### Pre-code lifecycle contract source for the new matrix

The resource unit is one fixed profile namespace with exactly one owned
container, one named persistent volume, one API process and one static-web
process. The owner record contains a random invocation ID, project/profile
identity, image ID, exact resource IDs/names, loopback ports, database
fingerprint, process IDs, state and secret *references* only. It contains no
password, JWT key, bearer token, DSN credential or raw provider value.
Before any effect, the implementation establishes an exclusive owner-file
lock and rechecks image, ports, existing labels/names and empty ownership.

The matrix's exact flat field names are `outcome`, `profile_id`,
`owner_nonce`, the four 0/1 resource flags `container_count`,
`volume_count`, `api_count`, `web_count`, and `total_owned_count`.
Each successful/persisted shape has a fixed counter relation for each flag
and total; total equals the sum of the four flags. Resource identifiers
are `container_id`, `volume_id`, `api_pid`, `web_pid`. Each partial shape
requires an identifier exactly when its matching flag is one and forbids it
when zero. The owned creation order is volume, container, API, web; cleanup
is reverse. The four reachable nonzero owned sets are volume only,
volume+container, volume+container+API, and all four. They have distinct
closed partial shapes; all other flag combinations are forbidden.
`OWNED_RUNNING` requires all four. `STOPPED_RETAINED` has only
`volume_count=1` and requires `stopped_container_id`, `stopped_api_pid` and
`stopped_web_pid` as stop evidence from the full running owner record.
`REFUSED_NO_EFFECT` has all counts zero and `effect_count=0`.
Transient `STOP_REFUSED` has `effect_count=0` and equal
`owner_record_digest_before`/`owner_record_digest_after`, with no owned
resource fields; it never overwrites the persisted owner record.
`profile_id` is fixed to `P5A2-SOURCE-DEMO-LOCAL-1`; ports are exact
`db_port=5433`, `api_port=8001`, `web_port=5174` on owned states.
`owner_nonce` is a 64-character lowercase hex invocation token generated
from 32 random bytes (`secrets.token_hex(32)`). `container_id`,
`stopped_container_id`, `db_fingerprint`, `image_id` and persisted owner
digests are normalized lowercase 64-hex values. The inspected Docker image
ID's known `sha256:` prefix is stripped before `image_id` enters this flat
record; the full raw ID and prefix are still verified at the OS boundary.
`volume_id` is the fixed name `shiftops-p5a2-source-demo-data-v1` and must
also match the actual labeled Docker volume. `api_pid`, `web_pid`,
`stopped_api_pid` and `stopped_web_pid` are INTEGER fields. The existing
invariant mutation generator supports the 64-hex pattern and constant field
domains; PID positivity, process liveness/reuse and exact foreign/swap
ownership checks remain mandatory contextual adapter/Stage B checks. A bool
or fractional PID is invalid even if it resembles an integer. No generic
guard/schema extension is in this tranche.

| Outcome/state | Required evidence | Forbidden assertion or effect |
|---|---|---|
| `REFUSED_NO_EFFECT` | fixed safe reason (`IMAGE_ABSENT`, `PORT_BUSY`, `OWNER_CONFLICT`, `PROFILE_INVALID`, `SCHEMA_UNKNOWN`), profile/invocation only, observed no-effect count zero | no created resource ID/PID or claim of cleanup |
| `OWNED_RUNNING` | exact one container ID, volume ID, API PID and web PID; local image ID/PG version, bound loopback ports, DB fingerprint and current owner nonce; creation counts exactly one each | no wildcard bind, missing owner ID, unverified inherited resource, or secret value |
| `PARTIAL_OWNED_FAILURE` | only actually created IDs/PIDs, per-resource ownership proof and exact still-owned count 0–1 after bounded cleanup, plus fixed safe failure class | no claim that absent/unverified resources are owned or stopped |
| `STOPPED_RETAINED` | exact stopped owned container/API/web IDs, volume ID retained, matched owner nonce and zero still-running owned processes/container | no volume deletion or unrelated resource stop |
| `STOP_REFUSED` | fixed mismatch/unverifiable reason and no stop effect; current recorded owner state unchanged | no forced kill/remove on collision or ambiguous PID/ID |

The matrix encodes flat shape, field presence and constant counter relations.
It does not prove PID liveness, ownership of an OS/container ID, port binding,
or the sum relation for an arbitrary runtime emitter beyond its declared
closed shapes. Those are contextual checks in the future adapter and Stage B
physical review. Static sample IDs/PIDs are synthetic shape examples, never
actual resource proof.

Allowed transitions: absent to transient `REFUSED_NO_EFFECT` or persisted
`OWNED_RUNNING`/`PARTIAL_OWNED_FAILURE` after a passing preflight;
`OWNED_RUNNING` to persisted `STOPPED_RETAINED` only by the same owner after
ID/PID revalidation, otherwise transient `STOP_REFUSED`. A partial failure
retains truthful still-owned IDs after bounded cleanup and is not silently
promoted to success. Its later recovery/stop needs a distinct reviewed
transition and complete owner proof. Transient refusals never replace the
persisted owner record. A retained
volume cannot be treated as a fresh empty database or restarted without a
new separately admitted effect decision and exact owner/dataset validation.
Each flat resource counter describes currently still-owned resources, not the
cumulative number created before cleanup. Contextual evidence must retain the
creation/cleanup trail and exact IDs: a seed failure after container creation
may truthfully retain only the volume after verified container cleanup.
Every still-owned/stopped count must equal the cardinality of its recorded IDs,
and no resource category may exceed one. Mutation cases must cover missing,
duplicate, swapped and foreign IDs, stale nonce, image/port collision,
nonpositive/boolean/fractional PIDs, partial creation and partial cleanup;
all must fail closed without touching
unowned resources. The future matrix is the sole registered machine owner of
these field and transition rules; this section is its independent pre-code
contract source, not proof they have been implemented.

## Acceptance and failure conditions

Stage A acceptance needs Root-frozen three artifacts and raw hashes before
BUILD; independent admission of this SPEC/WO, exact paths and source-family
patch; normal dispatch/actual-SHA child/clean gate; real code files; independent
family materialization before focused tests; meaningful unit and in-process
HTTP tests against both complete new receipts; normal full repository gates;
independent REVIEW and actual-SHA continuity/clean closure. Tests cannot
create a container, server or persistent database. Any missing image/port/
secret decision remains a Stage B preflight fact, not Stage A readiness.

Stage B acceptance, if later admitted, requires real owned PostgreSQL/JWT/
native-source/UI evidence for two contexts and retained owned resources;
failures and cleanup dispositions are recorded. No provider call or AI
governance claim is requested. Operational completeness, retention, SQLite
positive, forecast accuracy, scheduler, context, approval, production and
deployment remain OPEN/UNKNOWN/HELD as in the milestone table.
