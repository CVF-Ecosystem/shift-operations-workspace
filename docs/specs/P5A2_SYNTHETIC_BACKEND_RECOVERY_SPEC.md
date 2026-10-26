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
