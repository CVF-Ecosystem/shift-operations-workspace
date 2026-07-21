# workspace-api

**ROLE: BACKEND (REST API + CVF governance)** · Stack: FastAPI · Deploy: app
server · Nguồn sự thật qua `Ledger` Protocol (`DATABASE_URL`). Mọi CVF gate
(identity/permission/risk/approval/evidence/audit/freeze) enforce ở đây.
Ranh giới: [`docs/architecture/FRONTEND_BACKEND_BOUNDARY.md`](../../docs/architecture/FRONTEND_BACKEND_BOUNDARY.md).

FastAPI modular monolith cung cấp business API và giữ domain workflow độc lập provider.

## Boundary

API không nhận provider payload trực tiếp; external payload phải qua Integration Edge và Canonical Message Contract.

## Persistence

Production target là PostgreSQL; skeleton sử dụng in-memory repository để minh họa lifecycle và test không phụ thuộc hạ tầng.
