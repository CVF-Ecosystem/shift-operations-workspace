# operations-domain

Domain language và invariants cho shift, message, event, task, customer request, incident, handover, report, approval, correction và audit.

## Trạng thái (P1B-OPERATIONS-DOMAIN-EXTRACTION, 2026-07-23)

Package Python thật nằm ở `src/operations_domain/`:

- `models.py` — **định nghĩa canonical duy nhất** của 12 kiểu operational:
  `DataState`, `RiskClass`, `ShiftStatus`, `TaskStatus`,
  `CustomerRequestStatus`, `EvidenceRef`, `Shift`, `Message`,
  `OperationalEvent`, `Correction`, `Task`, `CustomerRequest`.
- `lifecycle.py` — 3 guard: `assert_transition`, `assert_task_transition`,
  `assert_customer_request_transition`.

`workspace_api.domain.models` và `workspace_api.domain.lifecycle` chỉ
**re-export** đúng các object đó (compatibility shim), nên
`workspace_api.domain.models.Shift is operations_domain.models.Shift`. Không
khai báo lại hay kế thừa để "re-export" — sẽ tạo hai class khác nhau, hỏng
`isinstance` và lệch schema Pydantic.

**Dependency một chiều.** Package này là sink: chỉ import standard library và
`pydantic`. Không được import `workspace_api`, `operations_ledger`,
`cvf_runtime`, `fastapi` hay `sqlalchemy`. Test chặn:
`tests/unit/test_operations_domain_boundary.py`.

**`User` KHÔNG nằm ở đây.** Nó mirror `database/migrations/003_users.sql`,
thuộc auth boundary; nhà canonical vẫn là `workspace_api/domain/models.py`.
Tranche reconciliation `known-principals.yaml` ↔ `users`
(P2B-APPROVER-IDENTITY-RECONCILIATION) đã quyết định: `users` là nguồn thẩm
quyền approver duy nhất lúc runtime, `known-principals.yaml` đã bị xoá, và
`User` vẫn không dời sang đây.

## Chưa làm

Các thư mục blueprint (`approvals/`, `audit/`, `corrections/`, `customers/`,
`events/`, `handovers/`, `incidents/`, `messages/`, `reports/`, `shifts/`,
`tasks/`) vẫn chỉ có README — chưa có model riêng. Vì vậy module status là
`partial`, **không** phải `enforced`.
