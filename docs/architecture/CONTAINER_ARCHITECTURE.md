# Container Architecture

Bốn deployables độc lập, mỗi cái có Dockerfile riêng
(`infrastructure/docker/`), cấu hình trong `docker-compose.yml`.

| Deployable | Vai trò | Cổng | Phụ thuộc |
|------------|---------|------|-----------|
| `workspace-web` | Frontend PWA (React/Vite) | 5173 | workspace-api |
| `workspace-api` | Backend REST (FastAPI) | 8000 | postgres, redis, minio |
| `integration-edge` | Webhook gateway kênh ngoài | 8100 | redis |
| `workspace-worker` | Background jobs | — | postgres, redis, minio |

Supporting services: **PostgreSQL** (source of truth), **Redis** (queue/cache),
**S3-compatible storage / MinIO** (evidence attachments).

## Vì sao tách container

- Deploy độc lập: web lên host tĩnh, api lên app server, DB lưu trữ riêng.
- Scale độc lập từng tầng.
- Đổi/di chuyển một service (vd DB) không kéo theo service khác.

Ranh giới frontend ↔ backend ↔ database chi tiết:
[`FRONTEND_BACKEND_BOUNDARY.md`](FRONTEND_BACKEND_BOUNDARY.md).
Contracts giữ ranh giới ổn định qua mọi deployment:
[`DEPLOYMENT_MODES.md`](DEPLOYMENT_MODES.md).
