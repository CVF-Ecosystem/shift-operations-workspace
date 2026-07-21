# Deployment Modes

Contracts và core workflow **không thay đổi theo deployment**. Chỉ cấu hình
(endpoint, credentials, provider) khác nhau giữa các mode.

## Modes

| Mode | Mô tả |
|------|-------|
| `LOCAL_ON_PREMISE` | Toàn bộ chạy tại chỗ; DB, storage, model local. |
| `PRIVATE_CLOUD` | Hạ tầng riêng trên cloud của tổ chức. |
| `HYBRID` | Một phần local (vd DB/RESTRICTED data), một phần cloud. |
| `MANAGED_CLOUD` | Web trên host tĩnh/CDN, API trên app server, DB managed Postgres. |

## Vì sao đổi deployment không sửa code

- Frontend trỏ backend qua `VITE_API_URL` (biến môi trường).
- Backend trỏ DB qua `DATABASE_URL` (Ledger Protocol chọn backend).
- Provider/channel qua adapter contract, cấu hình bằng env.

Nhờ ranh giới ở [`FRONTEND_BACKEND_BOUNDARY.md`](FRONTEND_BACKEND_BOUNDARY.md),
cùng một codebase chạy được ở mọi mode: ví dụ "web lên cloud, database lưu trữ
riêng" là `MANAGED_CLOUD` hoặc `HYBRID` — chỉ đổi `VITE_API_URL` và
`DATABASE_URL`, không đổi business logic.

## Ràng buộc data theo mode

`data-policy.yaml` quyết định classification nào được rời khỏi biên local (vd
`RESTRICTED: local_only`). Enforce: `cvf_runtime/data_scope.py`. Chọn deployment
mode phải tương thích với ràng buộc này.
