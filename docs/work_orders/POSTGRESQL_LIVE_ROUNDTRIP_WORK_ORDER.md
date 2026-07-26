# Work Order — PostgreSQL Live Round-Trip

Status: APPROVED — BUILD AWAITS C1/C2 PUSH AND FRESH G6
Work Order ID: `P1-PG-LIVE-WO-001`
Risk: R2
Implementation worker: Claude
Independent reviewer / commit steward: Codex

## 1. Objective

Implement and execute `P1-PG-LIVE-SPEC-001`, producing independently
reviewable proof that `SqlLedger` round-trips against a PostgreSQL 16 schema
created only by migrations 001–004.

## 2. Preconditions

Before any BUILD edit or container creation, Claude must:

1. rehydrate mandatory CVF continuity and declare `IMPLEMENTATION_WORKER`;
2. verify `HEAD == origin/main` at the post-C2 commit;
3. verify zero tracked modifications;
4. verify the only untracked path is the preserved assessment with SHA-256
   `168ea2c7a67a31bae50c9e4dbe78c2273a692f3a82a1074585e1bdb89b70fde2`;
5. verify hidden core HEAD/origin/manifest all equal
   `27137db4d9aa2aea931ddd2507185d5c24943080` and core is clean;
6. run the doctor and accept only 24 PASS, zero FAIL and the bounded legacy
   catalog-kit warning;
7. run the root suite and record the actual post-C2 baseline;
8. verify Docker Linux daemon responds; if not, stop with
   `BLOCKED_DOCKER_DAEMON_UNAVAILABLE` and do not start Docker Desktop
   automatically;
9. verify or install only `psycopg[binary]>=3.2` in the local Python
   environment, recording its version and making no dependency-file edit;
10. verify every authorized path exists or is explicitly marked NEW.

## 3. C3 BUILD changed-set ceiling

Only these five paths are authorized:

1. `scripts/run_postgres_live_roundtrip.py` — NEW
2. `tests/integration/test_sql_ledger_postgres_live.py` — NEW
3. `docs/decisions/POSTGRESQL_LIVE_ROUNDTRIP_EVIDENCE_RECEIPT.md` — NEW
4. `docs/catalog/MODULE_REGISTRY.json` — bounded semantic truth plus metrics
5. `docs/catalog/MODULE_CATALOG.md` — regenerated output only

`MODULE_REGISTRY.json` may receive only:

- exact generated metrics caused by the two new executable files;
- the `operations-ledger` `enforcement`, `tests` and `next_step` fields needed
  to replace “PostgreSQL never live verified” with the bounded reviewed truth.

`MODULE_CATALOG.md` must then be regenerated only through
`python scripts/generate_catalog.py --write`; it may contain only the
corresponding rendered semantic and metric changes.

No sixth path is conditionally authorized.

## 4. Read-only protected surfaces

These must remain byte-identical throughout C3:

- `database/migrations/001_foundation.sql`
- `database/migrations/002_tasks_customers_reports.sql`
- `database/migrations/003_users.sql`
- `database/migrations/004_approval_receipts.sql`
- `scripts/apply_migrations.py`
- `docker-compose.yml`
- `packages/operations-ledger/src/operations_ledger/**`
- `apps/workspace-api/src/**`
- existing tests, including SQLite and static schema-parity suites
- `.cvf/**`, authorization artifacts and continuity files.

## 5. Authorized external actions

After G6 passes, Claude may:

1. inspect or pull only `postgres:16-alpine`;
2. create one uniquely named disposable test container with no data volume and
   a dynamic `127.0.0.1` port;
3. generate a process-local ephemeral database credential;
4. install the scoped PostgreSQL Python driver if absent;
5. execute migrations and tests against only that disposable database;
6. stop/remove only the exact container it created.

No existing container, image, Compose project, named volume or database may be
deleted or modified. Pulling the named image is allowed; pruning is not.

## 6. Required implementation order

1. Add the opt-in live test from SPEC R5–R10.
2. Add runner orchestration and redaction/cleanup behavior.
3. Add non-live unit coverage inside the new test/runner files for command
   construction, redaction and cleanup targeting where practical.
4. Run the focused non-live tests.
5. Start the isolated container and apply migrations twice.
6. Run the live suite with zero skips.
7. Remove the container and prove it is absent.
8. Run the ordinary full suite and repository gates.
9. Run the existing complete shift create/confirm/close/freeze and contract
   suites required by the Phase 1 exit gate.
10. Write the sanitized receipt from actual output.
11. Update only the authorized `operations-ledger` registry truth, then
    regenerate the catalog.
12. Stop at `READY_FOR_INDEPENDENT_BUILD_REVIEW`.

## 7. Required return evidence

Claude returns:

- exact changed path set/count;
- G6 Git/core/doctor/baseline facts;
- Docker and driver versions;
- container name, image ID/digest, dynamic host port with credential omitted;
- proof of no volume mounts and cleanup;
- ordered migration first/reapply summaries;
- focused non-live, focused live and root-suite results;
- existing shift-lifecycle and contract exit-gate results;
- live schema/round-trip/constraint/rollback results;
- validator/session/catalog/file-size/diff results;
- protected-surface byte-identity hashes;
- assessment hash/status;
- confirmation of no provider call, production secret, stage, commit or push.

## 8. Reviewer probes

Codex independently:

1. audits runner command construction, timeout, redaction and exact cleanup;
2. verifies no `metadata.create_all` or SQLite fallback exists;
3. starts a fresh second disposable container and reruns migrations twice;
4. reruns the live suite with zero skips;
5. queries PostgreSQL directly for server identity, tables/enums and critical
   constraints;
6. verifies reconnect, rollback and post-error connection usability;
7. checks the receipt against raw sanitized output;
8. confirms all protected surfaces and the five-path ceiling;
9. runs ordinary full suite and all repository gates;
10. performs AC-19 revert rehearsal in a temporary sibling worktree.

Worker evidence is input to review, never self-approval.

## 9. Stop conditions

Stop immediately if:

- Docker daemon is unavailable;
- container identity or cleanup target is ambiguous;
- an existing container/database/volume would be touched;
- migrations require `metadata.create_all` or manual SQL repair;
- any production/migration/metadata defect is found;
- a sixth repository path is required;
- catalog generation causes unrelated drift;
- a credential or full database URL reaches output;
- live suite skips or uses a non-PostgreSQL dialect;
- doctor gains a new warning/failure;
- assessment changes;
- staging, commit or push occurs.

Return the finding; do not widen scope or repair production code.

## 10. Commit discipline

- C1: ADR + SPEC + WORK_ORDER only after authorization `REVIEW_PASS`.
- C2: canonical state, mirror, session memory and new active handoff only.
- C3: the five-path BUILD ceiling only, after independent BUILD
  `REVIEW_PASS`.
- C4: FREEZE continuity/status/roadmap only.

Claude owns no commit/push action. Codex owns reviewed commits and pushes.

## 11. C4 closure ceiling

C4 may change only:

1. `SESSION/ACTIVE_SESSION_STATE.json`
2. `SESSION/SESSION_MEMORY.md`
3. `CVF_SESSION/ACTIVE_SESSION_STATE.json`
4. the active PostgreSQL handoff
5. `IMPLEMENTATION_STATUS.json`
6. `docs/implementation/EXECUTION_ROADMAP.md`

## 12. Claim boundary

Closure proves only the SPEC's disposable local PostgreSQL 16 evidence
boundary. Phase 1 may close only under SPEC AC-20. It is not production
certification or AI-governance evidence.

## 13. Authorization gate

Independent review found and repaired without waiver:

- `PG-AUTH-F1 CATALOG_MUTATION_CONTRACT_CONFLICT`;
- `PG-AUTH-F2 PHASE1_CLOSURE_UNDER_SPECIFIED`;
- `PG-AUTH-F3 LIVE_SCHEMA_SCOPE_OVERBROAD`.

Re-review disposition: `REVIEW_PASS`.

Under the operator-delegated reviewer and Work Order approval authority, Codex
approves this Work Order intact on 2026-07-26.

BUILD remains prohibited until Codex pushes C1 and C2 separately and directs
Claude to run fresh G6 at the actual post-C2 HEAD.
