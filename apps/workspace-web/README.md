# workspace-web

**ROLE: FRONTEND (UI/UX)** · Stack: React/Vite PWA · Deploy: host tĩnh/CDN ·
Gọi backend qua HTTP (`VITE_API_URL`), không chạm database.
Ranh giới: [`docs/architecture/FRONTEND_BACKEND_BOUNDARY.md`](../../docs/architecture/FRONTEND_BACKEND_BOUNDARY.md).

React/Vite PWA dùng chung cho mobile và desktop.

## Operations Console

The authenticated console supports the reviewed operator/supervisor workflows.
P2-D adds foreground polling and bounded local staging for exactly three
versioned transitions: task, customer request and incident. All creates,
approval, staffing, correction, close, freeze and report actions remain online
only. Polling is not push realtime and local staging is not exactly-once.

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

The service worker caches only the navigation fallback and never API/auth data.
Queue entries are bound to the authenticated user, expire after 24 hours and
retain recorded CAS without server-dedupe claims. Ambiguous/blocked actions
fail stop and require review/discard; they are never silently retried.

## Security

Không chứa provider API keys hoặc channel secrets. Chỉ nhận session token ngắn hạn và dữ liệu theo quyền.
