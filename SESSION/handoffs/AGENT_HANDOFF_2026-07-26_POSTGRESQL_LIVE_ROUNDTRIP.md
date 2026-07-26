# Agent Handoff — PostgreSQL Live Round-Trip

## Disposition

- Tranche: `P1-POSTGRESQL-LIVE-ROUNDTRIP-2026-07-26`
- Control-chain phase: approved `WORK_ORDER`, immediately before BUILD
- Roadmap target: remaining PostgreSQL component of the Phase 1 exit gate
- Risk: R2
- Implementation worker: Claude
- Independent reviewer / commit steward: Codex
- BUILD status: **NOT STARTED**

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
