# workspace-api

**ROLE: BACKEND (REST API + CVF governance)** · Stack: FastAPI · Deploy: app
server · Nguồn sự thật qua `Ledger` Protocol (`DATABASE_URL`). Mọi CVF gate
(identity/permission/risk/approval/evidence/audit/freeze) enforce ở đây.
Ranh giới: [`docs/architecture/FRONTEND_BACKEND_BOUNDARY.md`](../../docs/architecture/FRONTEND_BACKEND_BOUNDARY.md).

FastAPI modular monolith cung cấp business API và giữ domain workflow độc lập provider.

## Boundary

API không nhận provider payload trực tiếp; external payload phải qua Integration Edge và Canonical Message Contract.

## Read endpoints (P2C-OPERATIONS-CONSOLE-READ-SLICE)

The following operational read routes require a valid JWT via `get_principal`
(identity-only read admission — not per-shift assignment, tenant isolation or
`data_scope` enforcement):

- `GET /shifts` — list all shifts;
- `GET /events?shift_id=<uuid>` — deterministic event list for a shift
  (ordered: starts_at non-null first, ascending starts_at, then ascending
  `str(event_id)`; evidence preserved; 500-record hard maximum, HTTP 422 on
  overflow);
- `GET /shifts/{shift_id}/open-work` — canonical open-work snapshot reusing
  `Ledger.open_work_snapshot` (tasks, customer_requests, incidents; 500-record
  hard maximum per group, HTTP 422 on overflow).

Missing shift returns HTTP 404. Anonymous, expired, malformed or mis-signed
tokens return HTTP 401. No mutation route is changed by this tranche.

## Persistence

Production target là PostgreSQL; skeleton sử dụng in-memory repository để minh họa lifecycle và test không phụ thuộc hạ tầng.
