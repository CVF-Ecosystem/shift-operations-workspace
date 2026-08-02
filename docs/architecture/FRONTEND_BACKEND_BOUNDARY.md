# Frontend / Backend / Database Boundary

Ranh giới ba tầng đã được thiết kế tách rời **ngay từ đầu** để: (1) đưa lên web
mà không đụng backend, (2) giữ database lưu trữ riêng, (3) thêm client khác
(mobile, CLI) mà không viết lại logic. Tài liệu này khóa nguyên tắc ranh giới
đó — mọi agent/dev phải giữ khi xây UI thật.

## Vai trò các app trong `apps/`

Frontend và backend **đã tách sẵn** thành các app riêng dưới `apps/` (mô hình
monorepo — một repo, nhiều deployable). Không gom thành hai thư mục
"frontend" và "backend" ở gốc, vì hệ có 4 deployable chứ không phải 2, và thư
mục `packages/` chứa code dùng chung cho cả FE lẫn BE.

| App | Vai trò | Stack | Deploy |
|-----|---------|-------|--------|
| `apps/workspace-web` | **FRONTEND** (UI/UX) | React/Vite PWA | host tĩnh/CDN |
| `apps/workspace-api` | **BACKEND** (REST + CVF gate) | FastAPI | app server |
| `apps/workspace-worker` | **BACKEND** (background jobs) | Python | worker |
| `apps/integration-edge` | **BACKEND** (edge/DMZ gateway) | FastAPI | biên public |

Code dùng chung (contracts, cvf-runtime, operations-ledger…) ở `packages/`.

## Ba đơn vị deploy độc lập

```text
┌──────────────────────┐   HTTP (JSON)   ┌──────────────────────┐  Ledger Protocol  ┌────────────┐
│  apps/workspace-web  │ ──────────────▶ │  apps/workspace-api  │ ────────────────▶ │ PostgreSQL │
│  React / Vite PWA    │                 │  FastAPI backend     │  (DATABASE_URL)   │  (riêng)   │
│  deploy: host tĩnh   │ ◀────────────── │  deploy: app server  │ ◀──────────────── │            │
└──────────────────────┘                 └──────────────────────┘                   └────────────┘
```

Mỗi tầng có Dockerfile riêng (`docker-compose.yml`) và deploy độc lập.

## Luật ranh giới (BINDING)

1. **Frontend chỉ nói chuyện với backend qua HTTP.** `workspace-web` gọi
   `fetch(\`${VITE_API_URL}${path}\`)` (`src/services/api.ts`). Frontend **không**
   import domain model, **không** chạm SQL, **không** biết `DATABASE_URL`.
   Base URL là biến môi trường (`VITE_API_URL`) → trỏ tới API ở bất kỳ đâu.

2. **Mọi CVF governance enforce ở BACKEND.** Permission, risk, approval,
   evidence, domain_lock, data_scope, audit, freeze chạy trong
   `workspace-api` + `cvf-runtime`. Frontend chỉ **phản ánh** trạng thái
   (ẩn/hiện nút, hiển thị "cần phê duyệt"), **không tự enforce**.
   → Lý do: một client khác (mobile, script, curl) bỏ qua UI vẫn phải bị chặn
   bởi backend. Nếu gate nằm ở frontend, governance bị lách. Đây là điểm dễ sai
   nhất khi xây web.

3. **Database tách khỏi cả hai, truy cập qua `Ledger` Protocol.**
   `workspace-api` nói chuyện với DB qua `operations_ledger.Ledger` (chọn backend
   bằng `DATABASE_URL`). Đổi/di chuyển DB không sửa business logic, không đụng
   frontend. DB có thể lưu trữ ở hạ tầng riêng.

4. **Hợp đồng ranh giới là `packages/workspace-contracts` (JSON Schema).**
   Hình dạng dữ liệu đi qua HTTP được định nghĩa ở đây, là nguồn chung để
   frontend và backend không lệch nhau khi phát triển song song.

5. **Không provider/framework cụ thể rò qua ranh giới.** Frontend không phụ
   thuộc FastAPI; backend không phụ thuộc React. Đổi framework một tầng không
   kéo theo tầng kia.

## Điều này giúp gì về sau

| Nhu cầu | Vì đã tách nên |
|---------|----------------|
| Đưa web lên production | Deploy `workspace-web` lên host tĩnh/CDN, set `VITE_API_URL`. Backend không đổi. |
| DB lưu trữ riêng | Đổi `DATABASE_URL`. FE/BE không đổi. |
| Thêm mobile app | Dùng chung `workspace-api`. Không viết lại logic. |
| Scale | Scale web, API, DB độc lập. |
| Offline/degraded | FE chỉ stage ba CAS transition trong queue actor-bound; service worker chỉ navigation fallback. `InMemoryLedger` là test backend, không phải browser offline data. |

## Trạng thái hiện tại (trung thực)

- Ranh giới **thiết kế** đã đúng và đã có code khung ở cả ba tầng.
- P2-C hiện thực assignment-scoped reads cùng operator/supervisor mutations
  qua `VITE_API_URL`; token vẫn chỉ ở `sessionStorage`. P2-D thêm polling khi
  authenticated/online/visible và local staging giới hạn cho task, customer
  request, incident transition với recorded CAS. Create/approval/staffing/
  correction/report/close/freeze vẫn online-only. Service worker không cache
  API/auth data; polling không phải push và queue không phải exactly-once.
- Gợi ý an toàn kiểu: sinh TypeScript type từ `workspace-contracts` để FE↔BE
  không lệch (chưa làm; `src/types/operations.ts` hiện được viết tay khớp
  theo response model của backend, là bước tùy chọn khi mở rộng UI).

## Liên quan

- [`CONTAINER_ARCHITECTURE.md`](CONTAINER_ARCHITECTURE.md) — bốn deployables.
- [`TRUST_BOUNDARIES.md`](TRUST_BOUNDARIES.md) — vì sao UI vẫn phải qua backend auth.
- [`DEPLOYMENT_MODES.md`](DEPLOYMENT_MODES.md) — contracts không đổi theo deployment.
- [`../cvf/CVF_CONTROL_MAPPING.md`](../cvf/CVF_CONTROL_MAPPING.md) — gate CVF nằm ở đâu trong backend.
