# Agent Handoff — PostgreSQL Live Round-Trip

## Disposition

- Tranche: `P1-POSTGRESQL-LIVE-ROUNDTRIP-2026-07-26`
- Control-chain phase: `FREEZE`
- Roadmap target: remaining PostgreSQL component of the Phase 1 exit gate
- Risk: R2
- Implementation worker: Claude
- Independent reviewer / commit steward: Codex
- BUILD status: **CLOSED_BOUNDED / REVIEW_PASS**

## Authorization

- C1: `668b7dfbb88a79c138191954f7e06e18b4a2fba6`
- Authorization review findings closed without waiver:
  - `PG-AUTH-F1 CATALOG_MUTATION_CONTRACT_CONFLICT`
  - `PG-AUTH-F2 PHASE1_CLOSURE_UNDER_SPECIFIED`
  - `PG-AUTH-F3 LIVE_SCHEMA_SCOPE_OVERBROAD`
- Re-review disposition: `REVIEW_PASS`
- Work Order `P1-PG-LIVE-WO-001` is explicitly approved by Codex under
  operator-delegated reviewer/approval authority.

Normative reads:

1. `docs/decisions/ADR_2026-07-26_POSTGRESQL_LIVE_ROUNDTRIP.md`
2. `docs/specs/POSTGRESQL_LIVE_ROUNDTRIP_SPEC.md`
3. `docs/work_orders/POSTGRESQL_LIVE_ROUNDTRIP_WORK_ORDER.md`

## Verified pre-C2 facts

- Project HEAD and `origin/main` equal C1.
- Hidden core HEAD/origin/manifest equal
  `27137db4d9aa2aea931ddd2507185d5c24943080`; core clean.
- Workspace doctor: `PASS WITH NOTE (24 passed, 1 warning)`; only the bounded
  legacy catalog-kit warning.
- Docker CLI 29.6.2 and Compose v5.3.1 are installed.
- Docker Desktop Linux daemon is currently unavailable.
- `psycopg` is currently absent from the local Python environment.
- Assessment remains untracked and untouched at SHA-256
  `168ea2c7a67a31bae50c9e4dbe78c2273a692f3a82a1074585e1bdb89b70fde2`.

## C3 boundary

Exactly five repository paths are authorized:

1. `scripts/run_postgres_live_roundtrip.py`
2. `tests/integration/test_sql_ledger_postgres_live.py`
3. `docs/decisions/POSTGRESQL_LIVE_ROUNDTRIP_EVIDENCE_RECEIPT.md`
4. `docs/catalog/MODULE_REGISTRY.json`
5. `docs/catalog/MODULE_CATALOG.md`

Production source, migrations, existing tests, Compose, CVF surfaces and
continuity are read-only during C3. A live defect is a stop condition and
requires a reviewed authorization amendment; it is not repair permission.

## Mandatory G6

After C2 is pushed, Claude must rehydrate this handoff and all three
authorization artifacts, declare `IMPLEMENTATION_WORKER`, and verify every
Work Order section 2 precondition.

The daemon check is decisive:

- if Docker responds, continue within the five-path ceiling;
- if it remains unavailable, stop at
  `BLOCKED_DOCKER_DAEMON_UNAVAILABLE`;
- do not start Docker Desktop automatically and do not substitute SQLite or
  mocked output.

## Return checkpoint

Claude performs no stage/commit/push. After implementation and one real
disposable PostgreSQL run, stop at:

`READY_FOR_INDEPENDENT_BUILD_REVIEW`

The return must contain every Work Order section 7 receipt, including exact
container cleanup proof and sanitized migration/live-test evidence.

## Closure boundary

PostgreSQL evidence alone does not automatically close Phase 1. Codex must
also rerun the existing complete shift create/confirm/close/freeze and contract
gates under SPEC AC-20. Only their combined PASS permits Phase 1 `DONE`.

No provider call is required or authorized; this tranche asserts database
behavior, not AI/agent governance.

## Amendment 1 repair acknowledgment

- Stopped BUILD produced three authorized untracked paths: runner, live test
  and failure receipt. Nothing was staged/committed/pushed.
- Independent reviewer reproduced migrations `17/0` then `14/3` and live
  result `26 passed, 7 failed`.
- Findings `PG-REV-F1` through `PG-REV-F5` are accepted without waiver:
  native enum bind failure, failure-output credential leak, cleanup ownership
  bug, incomplete enum type parity and receipt drift.
- Authorization Amendment 1:
  `6d6df205f355cd34552e37f8a75584e6a17623e8`.
- Repair ceiling is exactly eight paths in Work Order section 14.1.
- Migrations, `apply_migrations.py`, Compose, `sql_ledger.py`, `_rows.py`,
  application source, authorization and continuity remain read-only.
- Docker cleanup after reviewer reproduction: zero container and zero volume.
- Assessment hash remains exact.

After this C2b continuity commit is pushed, Claude transitions to
`REPAIR_WORKER`, runs G6R, repairs all five findings, executes a fresh real
PostgreSQL run, and stops at:

`READY_FOR_INDEPENDENT_BUILD_RE_REVIEW`

Claude still may not stage, commit or push.

## Final independent review and FREEZE

- Findings `PG-REV-F1` through `PG-REV-F7` closed without waiver.
- C3 BUILD commit:
  `68cb86eccaa4e542afd1193173efb02b5df4c4b3`; exactly eight authorized
  paths, independently `REVIEW_PASS`, pushed to `origin/main`.
- Fresh Codex PostgreSQL 16 run: migrations `17/0`, reapply `14/3`, live
  suite `36 passed`, zero skip/failure.
- SPEC AC-20 shift lifecycle + contract subset: `100 passed`.
- Root non-live suite: `427 passed, 36 skipped, 1 warning`.
- Repository validator, catalog, session-state, file-size and diff gates:
  PASS. Doctor: `PASS WITH NOTE (24 passed, 1 warning)`; only the bounded
  legacy catalog-kit note.
- Exact disposable container and captured anonymous volume absent.
- AC-19 rollback rehearsal: reverted tree matched parent
  `11c3ac5aee5e8127ec9f3fa3b53e817b831b9ad3`; baseline `405 passed`,
  repository gates PASS; temporary worktree removed.
- No provider call was made: this proves database behavior, not AI governance.

Disposition: `FREEZE / CLOSED_BOUNDED`. Phase 1 exit gate is `DONE` only
within the disposable-local PostgreSQL evidence boundary; this is not a
production deployment/load/HA/backup/managed-PostgreSQL claim.

Next governed move: fresh `INTAKE` for P2-A incidents/handovers, including a
governed migration design before implementation. P2-C remains after P2-A.
