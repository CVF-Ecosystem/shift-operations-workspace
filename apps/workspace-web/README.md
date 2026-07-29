# workspace-web

**ROLE: FRONTEND (UI/UX)** · Stack: React/Vite PWA · Deploy: host tĩnh/CDN ·
Gọi backend qua HTTP (`VITE_API_URL`), không chạm database.
Ranh giới: [`docs/architecture/FRONTEND_BACKEND_BOUNDARY.md`](../../docs/architecture/FRONTEND_BACKEND_BOUNDARY.md).

React/Vite PWA dùng chung cho mobile và desktop.

## Operations Console (read-only slice, P2C C3b)

The first implemented slice is a **read-only** authenticated Operations
Console: login/logout, shift selection, confirmed-event timeline, open work
(tasks/customer requests/incidents), incident severity/status summary, and
handover lifecycle summary. It has no create/confirm/transition/approve/
close/freeze controls, no offline queue activation, no realtime transport,
and no AI/RAG/reporting behavior — see the ADR/SPEC/Work Order under
`docs/decisions/` and `docs/specs/` for the exact authorized boundary.

Auth token lives only in `sessionStorage` (never `localStorage`); logout and
any HTTP 401 both clear it and return to the login screen.

## Toolchain

- Node exactly `22.14.0`, pnpm exactly `9.15.0` (see root `package.json`
  `packageManager` and this package's `engines.node`).
- `pnpm install --frozen-lockfile` from the repository root.
- `pnpm --filter workspace-web test` runs Vitest + jsdom.
- `pnpm --filter workspace-web typecheck` runs `tsc -b --noEmit`.
- `pnpm --filter workspace-web build` runs the production Vite build.

## Offline boundary

Chỉ queue các command idempotent. Mỗi command có client_operation_id để backend chống trùng khi đồng bộ lại.
The offline queue module is not wired into the read-only console in this
slice.

## Security

Không chứa provider API keys hoặc channel secrets. Chỉ nhận session token ngắn hạn và dữ liệu theo quyền.
