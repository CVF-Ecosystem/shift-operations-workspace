# Workspace Contracts

Canonical JSON Schemas là stable boundary giữa core, providers, channels, Refinery và CVF.

## Open-work response contract

`open-work/open-work.schema.json` defines the exact response shape for
`GET /shifts/{shift_id}/open-work` (P2C-OPERATIONS-CONSOLE-READ-SLICE, SPEC R2).

The response contains:
- `shift_id` (UUID) — the queried shift;
- `tasks` (array) — open Task objects from `Ledger.open_work_snapshot`;
- `customer_requests` (array) — open CustomerRequest objects;
- `incidents` (array) — open Incident objects.

The three arrays reuse the canonical open-work snapshot — they do not fork
open predicates. Array order is the existing canonical UUID order. Task and
Incident evidence must survive unchanged.

## Rules

Không sửa breaking schema âm thầm. Mọi breaking change cần version strategy, migration và contract conformance tests.
