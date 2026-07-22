# Agent Handoff — 2026-07-22 (P2-A-CUSTOMER-REQUEST)

Provider-neutral handoff. Continues from
[`AGENT_HANDOFF_2026-07-22_PFIX6.md`](AGENT_HANDOFF_2026-07-22_PFIX6.md).

- **Mode:** cvf_enforcement_buildout
- **Tranche:** P2-A-CUSTOMER-REQUEST — Execution Roadmap Phase 2, replicating
  the CVF chain to the `customer_request` domain
- **Startup ack:** mode=cvf_enforcement_buildout; active handoff=this file;
  next allowed move=P2-A (còn lại: incidents/handovers, cần migration mới
  trước) or P2-B or P2-C; parked checkpoint=none.

## Bối cảnh

Tranche P-FIX (P-FIX-0 → P-FIX-6) đã đóng bounded. Operator ủy quyền mở lại
Phase 2 roadmap, chỉ định cụ thể **P2-A: nhân bản CVF chain sang domain thứ
năm — customer requests**. `customer_requests` được chọn (thay vì incidents/
handovers) vì bảng đã có sẵn trong
`database/migrations/002_tasks_customers_reports.sql` (dòng 15-26) và
`customer_request` đã có tên trong `domain-lock.yaml`; incidents/handovers
chưa có bảng migration nào — implement 2 domain đó cần migration mới, rủi ro
lớn hơn, không phải việc của tranche này.

## Việc đã làm — CVF chain nhân bản sang CustomerRequest domain (golden vertical #5)

Tái dùng **cùng** các gate cvf-runtime như Event/Correction/Task/Shift, không
fork:

1. `domain/models.py`: `CustomerRequestStatus` StrEnum (`NEW, ACKNOWLEDGED,
   IN_PROGRESS, WAITING, RESOLVED, CLOSED` — khớp CHECK constraint migration)
   + `CustomerRequest` model khớp migration CHÍNH XÁC (`shift_id: UUID | None`
   nullable khác `Task.shift_id`; KHÔNG có `version`/`risk_class`/`state`/
   `evidence` — migration không có các cột đó, đơn giản hơn Task/
   OperationalEvent có chủ đích, không phải thiếu sót).
2. `domain/lifecycle.py`: `assert_customer_request_transition` — máy trạng
   thái riêng: NEW→ACKNOWLEDGED→IN_PROGRESS→WAITING/RESOLVED, WAITING↔
   IN_PROGRESS, RESOLVED→CLOSED (terminal). **Quyết định thiết kế:** WAITING
   không được nhảy thẳng CLOSED — phải qua RESOLVED trước, để đảm bảo có ghi
   nhận tường minh rằng vấn đề đã thực sự được giải quyết trước khi đóng, chứ
   không phải bị bỏ dở trong lúc chờ.
3. `operations-ledger`: bảng `customer_requests` map vào `tables.py` (nullable
   `shift_id` FK tới `shifts`, FK thứ hai tới `messages.message_id`, CHECK
   status 6 giá trị khớp migration). **Phụ:** thêm một `messages` Table tối
   thiểu vào `tables.py` — CHỈ để FK `source_message_id` resolve được trong
   cùng `MetaData` (SQLAlchemy raise `NoReferencedTableError` nếu không có);
   `SqlLedger.add_message` vẫn `NotImplementedError`, `messages` KHÔNG được
   thêm vào schema-parity `MAPPED` set (chưa có hành vi persist nào để parity
   -check). `add/get/put_customer_request` vào Protocol + `InMemoryLedger` +
   `SqlLedger`, đúng khuôn `add/get/put_task`; frozen-shift guard trong
   `InMemoryLedger`/`SqlLedger` chỉ chạy KHI `shift_id is not None` (vì
   nullable). Row-mappers `customer_request_row()`/`row_to_customer_request()`
   thêm vào `_rows.py`.
4. `application/customer_request_service.py`: `CustomerRequestService` —
   `create_customer_request` (identity→permission `customer_request.create`→
   domain_lock `customer_request`→persist qua `Ledger.transaction()` (frozen-
   shift check bên trong `add_customer_request`, chỉ khi có `shift_id`)→audit
   atomic) và `transition` (identity→permission `customer_request.transition`→
   `assert_customer_request_transition`→persist→audit atomic). **KHÔNG** có
   risk/evidence/approval gate cho create — migration không có cột đó, khác
   `TaskService` có chủ đích.
5. `cvf_runtime/permission.py`: thêm `customer_request.create`/
   `customer_request.transition` vào `_ACTION_MIN_ROLE`, cả hai role tối
   thiểu `operator` (cùng bậc `task.create`/`task.transition` — hành động vận
   hành thường quy, không phải commitment rủi ro cao).
6. `api/customer_requests/router.py` (mới): prefix `/customer-requests`
   (hyphen — không có tiền lệ router nhiều từ nào trong repo, chọn hyphen vì
   là quy ước REST phổ biến hơn). `POST ""` (create) + `POST
   "/{request_id}/transition"`, cùng khuôn identity/ledger dependency
   injection + exception mapping (`CvfDenied`→`exc.http_status`, `KeyError`→
   404, `ValueError`→409) như `tasks/router.py`. Đăng ký router trong
   `main.py`.
7. Tests: `tests/cvf/test_customer_request_vertical.py` (18 test) — service +
   HTTP create, 401 vô danh, 403 role thấp, domain-lock-allowed create,
   lifecycle hợp lệ đầy đủ (NEW→...→CLOSED) + WAITING không nhảy thẳng CLOSED
   + CLOSED terminal + skip bất hợp lệ (NEW→IN_PROGRESS), rollback atomic khi
   `append_audit` raise trên cả 2 backend (InMemoryLedger + SqlLedger/SQLite
   thật), tạo có/không `shift_id`, tạo bị chặn khi shift cha đã FROZEN.
8. `tests/integration/test_schema_parity.py`: thêm `customer_requests` vào
   `MAPPED`; thêm `("customer_requests", "request_id")` vào
   `_ALWAYS_EXPLICITLY_SUPPLIED_PK` (verified bằng cách đọc
   `customer_request_row()` — `request_id` luôn có trong row dict).

## Kết quả kiểm chứng

- `python -m pytest -q` → **136 passed** (118 trước + 18 test mới).
- `python scripts/testing/validate_repository.py` → PASS (catalog + session
  state + file-size).
- `python scripts/generate_catalog.py --check` → PASS (20 module, 3247 LOC).
- `tests/integration/test_schema_parity.py` +
  `tests/integration/test_schema_parity_types_and_checks.py` → **10 passed**,
  bao gồm `customer_requests` trong kiểm hai chiều (column-set, nullability,
  primary key, foreign key cả hai chiều, type family, CHECK expression).
- File-size guard: mọi file sửa/thêm còn xa hạn 400 dòng (file lớn nhất sau
  sửa là `sql_ledger.py` ở 335 dòng).

## Next allowed move

Theo `EXECUTION_ROADMAP.md`: P2-A (còn lại — incidents, handovers; CHƯA có
bảng migration nào cho 2 domain này, cần migration mới trước khi nhân bản
chain), HOẶC P2-B (authentication thật, nên thay thế known-principals.yaml),
HOẶC P2-C (frontend UI cho các vertical đã có backend, giữ boundary
backend-only theo `FRONTEND_BACKEND_BOUNDARY.md`).

## Blocked

Xem `blocked_work` trong `ACTIVE_SESSION_STATE.json` (không đổi trong tranche
này, cộng thêm điểm mới): **không tuyên bố "P2-A đã đóng" chung chung** — chỉ
customer_request xong; incidents/handovers vẫn mở và cần migration mới trước
khi bắt đầu. Vẫn: PostgreSQL round-trip chưa chạy live; identity vẫn
header-based chưa xác thực thật; không batch nhiều tranche/commit.
