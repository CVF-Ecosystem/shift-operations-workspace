# Independent Review — Message Admission and Trust Repair SPEC

- Review id: `MESSAGE-ADMISSION-TRUST-REPAIR-SPEC-REVIEW-001`
- Tranche: `MESSAGE-ADMISSION-TRUST-REPAIR-2026-07-30`
- Date: 2026-07-30
- Phase reviewed: `SPEC`
- Reviewer: Codex, `ORCHESTRATOR / REVIEWER`
- Future implementation worker: unassigned and must be independent
- Disposition: `REVIEW_PASS — WORK_ORDER AUTHORING ONLY`

## Independence and boundary

The reviewer is independent from the future R2 implementation/repair worker.
No BUILD, source/test/contract implementation, provider call, credential read
or Docker/PostgreSQL action occurred.

## Inputs and reproduced truth

The review compared INTAKE, ADR, SPEC, active continuity, current message
router/domain/table, Ledger Protocol, InMemoryLedger, SqlLedger, permission
map, schema parity, PostgreSQL runner and shift-create evidence architecture.

It reconfirmed:

- the route is anonymous and trusts caller sender/source;
- InMemory stores/returns a caller alias and has no duplicate guard/read;
- SqlLedger `add_message` is `NotImplemented`;
- the existing table can represent the bounded internal projection without a
  migration;
- the domain has `evidence` but the table does not, requiring explicit refusal
  rather than silent loss;
- the PostgreSQL runner is exactly 300 lines;
- customer-request and schema-parity comments/tests explicitly await this
  vertical;
- external canonical ingestion dependencies remain absent.

## Review findings repaired

### `MAR-SPEC-REV-F1 CLOSED_SHIFT_SEMANTICS_AMBIGUOUS`

The draft said “mutable shift”, which could be read as OPEN-only and conflict
with the existing freeze invariant. R7 now freezes exact behavior: OPEN,
HANDOVER_PENDING and CLOSED accept append-only RAW input; only FROZEN refuses.

### `MAR-SPEC-REV-F2 SILENT_EVIDENCE_LOSS`

The domain Message has evidence while the existing table does not. R9-R10 now
require both backends to reject non-empty evidence instead of returning a
record that cannot round-trip.

### `MAR-SPEC-REV-F3 SQL_EXCEPTION_PARITY`

The draft required duplicate handling but did not block raw FK/PK exceptions.
R10 now requires controlled cross-backend exception categories and explicitly
forbids raw `IntegrityError` escape.

All three findings closed without waiver.

## Coverage

| Intake finding | SPEC controls |
|---|---|
| F1 entrypoint | Scope, R1-R3, R14 |
| F2 sender authority | R2, R4-R5 |
| F3 edge handoff | Scope, R14, R19 |
| F4 model drift | R5, R9-R12 |
| F5 routing/shift | R7, R16 |
| F6 durable parity | R8-R12 |
| F7 governance | R4, R6 |
| F8 failures/HTTP | R1-R3, R7, R9-R10 |
| F9 live evidence | R16-R18 |

## Feasibility probes

- current message router: 22 lines;
- InMemory repository: 285 lines;
- Ledger Protocol: 143 lines;
- SqlLedger: 280 lines;
- row mappers: 235 lines;
- tables mapping: 291 lines;
- permission map: 101 lines;
- PostgreSQL runner: exactly 300 lines.

The Work Order must therefore authorize coherent helpers for SQL message
persistence, exact existing stale-reference paths, and a line-neutral
PostgreSQL target-list edit. No file-size exception is acceptable.

Focused current contract/freeze baseline: 15 passed. Session, catalog,
repository, file-size, JSON and diff gates pass. Doctor is `PASS WITH NOTE
(24 passed, 1 warning)` with only the bounded legacy catalog-kit warning.
These are planning-baseline probes, not future BUILD evidence.

## Disposition

`REVIEW_PASS` on R1-R19 and AC-01..AC-23 after
`MAR-SPEC-REV-F1..F3` closed without waiver.

Only a bounded Work Order may be authored next. BUILD remains unauthorized.
