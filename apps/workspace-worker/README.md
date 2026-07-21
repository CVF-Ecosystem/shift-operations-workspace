# workspace-worker

**ROLE: BACKEND (background jobs)** · Deploy riêng · Xử lý bất đồng bộ, không
phục vụ HTTP cho frontend.
Ranh giới: [`docs/architecture/FRONTEND_BACKEND_BOUNDARY.md`](../../docs/architecture/FRONTEND_BACKEND_BOUNDARY.md).

Background processing cho message normalization, AI proposals, report generation, outbound delivery và maintenance.

## Idempotency

Mọi job nhận job_id/client_operation_id và phải an toàn khi retry.

## Failure

Job thất bại không làm mất raw evidence; chuyển retry hoặc dead-letter/quarantine theo policy.
