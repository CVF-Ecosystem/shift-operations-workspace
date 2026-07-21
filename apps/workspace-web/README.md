# workspace-web

**ROLE: FRONTEND (UI/UX)** · Stack: React/Vite PWA · Deploy: host tĩnh/CDN ·
Gọi backend qua HTTP (`VITE_API_URL`), không chạm database.
Ranh giới: [`docs/architecture/FRONTEND_BACKEND_BOUNDARY.md`](../../docs/architecture/FRONTEND_BACKEND_BOUNDARY.md).

React/Vite PWA dùng chung cho mobile và desktop.

## Responsibilities

Authentication UI, shift selection, operations chat, quick actions, timeline, open work, customer inbox, handover, reports, dashboard và administration.

## Offline boundary

Chỉ queue các command idempotent. Mỗi command có client_operation_id để backend chống trùng khi đồng bộ lại.

## Security

Không chứa provider API keys hoặc channel secrets. Chỉ nhận session token ngắn hạn và dữ liệu theo quyền.
