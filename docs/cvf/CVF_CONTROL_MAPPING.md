# CVF Control Mapping

Ánh xạ từng CVF `required_control` (khai báo trong
`packages/cvf-application-profile/profile.yaml`) tới **điểm thực thi bằng code**,
kèm trạng thái thật.

**2026-07-22 correction:** một review độc lập (Codex,
`docs/decisions/EA_INDEPENDENT_REVIEW_2026-07-22_CODEX.md`) chứng minh bằng
probe chạy thật rằng nhãn "enforced" trước đây trong file này đã bị dùng quá
rộng — nó chỉ đúng cho "có hàm gate + unit test", không có nghĩa "chặn được vi
phạm trong request path thật, không bypass được". Bảng dưới đây dùng lại đúng 2
mức đó, tách bạch.

**2026-07-22 P-FIX-6 correction:** một review độc lập **thứ hai** bác bỏ tuyên
bố đóng tranche P-FIX-5. `POST /shifts/{shift_id}/close` vẫn gọi thẳng
`ledger.close_shift()` từ router — không identity, không permission, không
audit (probe: `create=200`, `anonymous_close=200`, `status=CLOSED`,
`audit_count=0`). Vì `ShiftService.freeze` chỉ kiểm
`shift.status == ShiftStatus.CLOSED`, close vô danh này âm thầm thỏa mãn điều
kiện tiên quyết `shift_closed` của freeze — đúng loại bypass CVF được thiết kế
để chặn. P-FIX-6 thêm `shift.close` làm governed action thật (xem dòng
`freeze`/`shift.close` trong bảng dưới); đây KHÔNG đụng tới approval/High
Finding #4 (xem `docs/decisions/EA_INDEPENDENT_REVIEW_2026-07-22_CODEX.md`) —
phạm vi P-FIX-6 chỉ là shift-close.

**2026-07-22 P2-B correction (real authentication):** `identity` chuyển từ
**not verified server-side** sang **load-bearing**. `dependencies.py ·
get_principal` không còn đọc `X-User-Id`/`X-User-Role` trực tiếp — giờ yêu
cầu một JWT bearer token đã ký hợp lệ (`workspace_api/auth/tokens.py`,
HS256, ký bằng `JWT_SECRET_KEY` bắt buộc, không có default nên app fail-closed
lúc khởi động nếu thiếu) và chỉ dựng `Principal` từ claim `sub`/`role` đã xác
thực chữ ký — không còn từ bất kỳ field nào caller tự khai trực tiếp.
`POST /auth/login` (`workspace_api/auth/router.py`) cấp token sau khi kiểm
username/password so với bảng `users` mới (mật khẩu hash bằng bcrypt). **Cố ý
NGOÀI phạm vi tranche này, không tuyên bố đã sửa:** refresh token/revocation,
tự đăng ký, đặt lại mật khẩu, rate-limit đăng nhập, và — quan trọng nhất —
**không đụng tới `known-principals.yaml`** (registry approver riêng dùng cho
quorum approval R3/R4). High Finding #4 (approval fabrication) vẫn còn
nguyên, xem mục `approval` bên dưới.

## Trạng thái (2 mức — không gộp lại thành "enforced")

- **callable** — hàm gate tồn tại trong `cvf_runtime`, có unit test gọi trực
  tiếp và test đó pass. **Không** đảm bảo request path thật (router → service →
  ledger) gọi tới nó đúng lúc, đúng cách, không có đường vòng.
- **load-bearing** — đã xác nhận (bằng test end-to-end qua router/service, hoặc
  probe runtime) rằng vi phạm **thực sự bị chặn** trong luồng thật, ở cả hai
  backend (InMemory và Sql) khi có backend đó tham gia.
- **profile-only** — policy đã có trong YAML nhưng chưa có code đọc/enforce.
- **not verified server-side** — có gate, nhưng gate tin dữ liệu do caller tự
  cung cấp trong cùng request (vd định danh qua header, approver tự khai) thay
  vì xác thực độc lập.

## Golden verticals — phạm vi chính xác

**2026-07-22 P-FIX-6 closure-cleanup:** mục này trước đó chỉ liệt kê 3 service
(`EventService`, `CorrectionService`, `TaskService`) — đã lỗi thời từ khi
P-FIX-6 thêm `ShiftService.close` làm governed action thứ tư. Cập nhật lại:

**2026-07-22 P2-A-CUSTOMER-REQUEST:** thêm `CustomerRequestService` làm
service thứ năm — nhân bản đúng khuôn `TaskService`/`ShiftService` sang domain
`customer_request`. Xem mục 5 bên dưới.

Năm service (`EventService`, `CorrectionService`, `TaskService`,
`ShiftService`, `CustomerRequestService`) **đều import và gọi cùng các hàm
`cvf_runtime`** — không có bản sao logic permission/evidence/approval nào bị
fork. Đây là phần đã xác nhận đúng.

Nhưng gọi bất kỳ đường nào trong số này là "golden vertical durable/end-to-end"
không có giới hạn vẫn là **quá rộng** (đây chính là nhãn Codex gắn cờ ở review
2026-07-22 — xem `docs/decisions/EA_INDEPENDENT_REVIEW_2026-07-22_CODEX.md`).
Chính xác hơn, theo domain:

1. **Operational Event → confirm** — `EventService.confirm`. Load-bearing trên
   cả 2 backend: `operations_ledger/_rows.py` map cột `evidence` qua bảng
   `evidence_links` (P-FIX-3, 2026-07-22) — event ghi evidence rồi đọc lại
   không còn mất, `assert_evidence_sufficient` không còn từ chối sai một event
   đã có đủ evidence lúc ghi. (Critical Finding #2 trong bản review Codex gốc
   — đã sửa; xem mục `evidence` trong bảng dưới cho test xác nhận.) **Còn hạn
   chế:** approval quorum trong bước confirm **không xác thực approver độc
   lập** ngoài registry known-principals (xem mục approval bên dưới).
2. **Operational Event → correct** — `CorrectionService.correct_event`.
   Load-bearing về mặt state transition; nhưng approval quorum trong bước này
   **không xác thực approver** (xem mục approval bên dưới).
3. **Task → create / transition** — `TaskService`. Chain đúng ở tầng service
   (test trực tiếp construct `Task` kèm evidence, pass). **Qua HTTP cũng đã
   sửa** (P-FIX-3, 2026-07-22): `TaskInput`/`api/tasks/router.py` giờ có field
   `evidence` (`list[EvidenceRef] = []`) và truyền qua service — request thật
   không còn tự động rỗng evidence, task R2+ tạo qua API với evidence hợp lệ
   không còn bị `evidence` gate từ chối sai.
4. **Shift → close / freeze** — `ShiftService.close`/`ShiftService.freeze`
   (P-FIX-6, P-FIX-1). Load-bearing trên cả 2 backend, có test end-to-end qua
   HTTP (`tests/cvf/test_shift_close_governance.py`,
   `tests/cvf/test_freeze_invariant.py`). **Còn hạn chế:** freeze's
   `report_approved`/`open_handover_items_linked` không có model thật, chỉ
   override tường minh có audit. identity giờ xác thực thật qua JWT (P2-B,
   2026-07-22) — không còn là giới hạn ở domain này hay bất kỳ domain nào khác
   trong bảng.
5. **Customer Request → create / transition** — `CustomerRequestService`
   (P2-A-CUSTOMER-REQUEST, 2026-07-22; repaired after independent review,
   2026-07-22). Chain đúng ở tầng service và qua HTTP. Test:
   `tests/cvf/test_customer_request_vertical.py` (18 test: service-level +
   HTTP-level create, 401/403, lifecycle transitions hợp lệ/không hợp lệ,
   rollback atomic trên cả 2 backend, tạo có/không `shift_id`, tạo bị từ chối
   khi shift cha đã `FROZEN`) + `tests/cvf/test_customer_request_repair.py`
   (11 test, thêm sau review độc lập thứ ba: alias-bypass rollback InMemory,
   `source_message_id` hợp lệ/không tồn tại trên cả 2 backend + HTTP không
   còn 500, `promised_at` sai định dạng trả 422 không phải 500, **domain_lock
   negative-profile test thật** — profile loại `customer_request` khỏi
   `allowed_domains` phải bị `CvfDenied(control="domain_lock")`, không có
   customer_request/audit nào được ghi). Trước bản sửa này, tuyên bố
   "domain_lock được exercise" ở `test_customer_request_vertical.py` chỉ đúng
   theo nghĩa happy-path (test dùng profile mặc định luôn cho phép
   `customer_request`) — không có test âm chứng minh việc bị từ chối khi
   domain không được phép; giờ có. Bảng `customer_requests` khớp migration
   002 CHÍNH XÁC theo parity test hai chiều (FK/CHECK/nullability/PK/type
   family/status-CHECK-values — status-CHECK giờ parametrized qua cả
   `tasks` và `customer_requests`, không còn hardcode `tasks` như bản gốc
   tuyên bố nhầm). **Khác Task có chủ đích:** migration không có cột
   `version`/`risk`/`state`/evidence cho bảng này, nên `create` KHÔNG có gate
   risk/evidence/approval — không phải thiếu sót, mà khớp đúng schema đơn giản
   hơn của domain này. `domain_lock` giờ được exercise (cả positive và
   negative) ở một domain thứ hai ngoài `create_event` (xem dòng `domain_lock`
   trong bảng dưới). `source_message_id` (FK tới `messages.message_id`) giờ
   được validate qua `Ledger.message_exists()` trước khi persist trên cả 2
   backend, trả `CvfDenied(control="reference", http_status=404)` nhất quán
   thay vì một backend chấp nhận vô điều kiện còn backend kia rò
   `IntegrityError` thành HTTP 500. **Còn hạn chế:** `messages` vẫn chưa có
   persistence vertical thật (`SqlLedger.add_message` vẫn `NotImplementedError`
   — `message_exists` chỉ là existence-check tối thiểu, không phải write
   path). identity không còn là giới hạn riêng ở đây (P2-B, 2026-07-22).

**Không domain nào trong 5 cái trên là "durable end-to-end qua HTTP + SqlLedger
+ evidence + xác thực identity thật" không giới hạn** — ngoại trừ identity, mà
P2-B (2026-07-22) đã sửa thật cho cả 5 domain (xem mục `identity` ở trên).
Evidence persistence (SqlLedger) và evidence qua HTTP (TaskInput) đã sửa ở
P-FIX-3 — không còn là giới hạn của Event/Task. Giới hạn còn lại chung cho
Event/Correction là approval không xác thực approver độc lập ngoài registry
known-principals — P2-B KHÔNG đụng tới registry đó, xem mục `approval`.
`shift.close` và `customer_request` là các domain có ít giới hạn riêng nhất
tính đến 2026-07-22 (customer_request không có approval/evidence chain để
mang giới hạn "không xác thực approver" ngay từ đầu — domain này đơn giản là
không yêu cầu approval theo migration schema).

## Bảng ánh xạ

| CVF control | Trạng thái | Enforce ở đâu (file · symbol) | Giới hạn đã biết |
|---|---|---|---|
| identity | **load-bearing (P2-B, 2026-07-22)** | `dependencies.py · get_principal` giải mã/xác thực JWT bearer token qua `workspace_api/auth/tokens.py::decode_access_token` (HS256, `JWT_SECRET_KEY` bắt buộc); `POST /auth/login` (`workspace_api/auth/router.py`) cấp token sau khi kiểm username/password (bcrypt) so với bảng `users` mới | Sửa: caller không còn tự đặt header để thành principal — role luôn tới từ claim đã ký, không phải field caller tự khai. **Còn hạn chế:** không refresh token/revocation (access token TTL cố định, mặc định 60 phút); cấp user chỉ qua `scripts/seed_dev_users.py` (dev/test), chưa có admin flow thật; KHÔNG đụng tới `known-principals.yaml` — approval quorum (High Finding #4) vẫn tách biệt, xem mục `approval`. Test: `tests/cvf/test_auth_tokens.py` (8 test: round-trip, tamper, expiry, wrong-secret, `alg=none`, role ngoài `KNOWN_ROLES`), `tests/cvf/test_auth_login.py` (4 test), cộng probe hồi quy `tests/cvf/test_shift_close_governance.py::test_old_header_impersonation_no_longer_grants_any_identity` (claim `authorized_executive` qua header cũ, không có bearer token → vẫn 401). |
| permission | callable, load-bearing cho role check | `cvf_runtime/permission.py · require_action` | Đúng vai trò tối thiểu theo action, nhưng phụ thuộc identity chưa xác thực ở trên. |
| domain_lock | callable, load-bearing tại `create_event` và `create_customer_request`, kiểm cả positive lẫn negative (2026-07-22, P2-A + repair) | `cvf_runtime/domain_lock.py · assert_event_type_in_scope` (event); `CustomerRequestService.create_customer_request · assert_domain_allowed(profile, "customer_request")` | Gắn ở `create_event` và (từ P2-A-CUSTOMER-REQUEST) `create_customer_request`; chưa gắn `create_task` hay các domain khác (Task chưa cần domain_lock vì domain `shift_operation` của nó không nằm trong nhánh event-type-mapping). Test âm thật: `tests/cvf/test_customer_request_repair.py::test_customer_request_denied_when_domain_lock_excludes_it` xây `CvfProfile` loại `customer_request` khỏi `allowed_domains`, xác nhận `CvfDenied(control="domain_lock")` và không có customer_request/audit nào được ghi — trước bản sửa này (independent review thứ ba, 2026-07-22) chỉ có test happy-path, không có test âm. |
| data_scope | callable, **không có runtime caller** | `cvf_runtime/data_scope.py · assert_placement_allowed` | `allow_after_minimization` cho phép external placement mà không yêu cầu bằng chứng đã minimize — chính sách chỉ mang tính khuyến nghị. Chưa có nơi nào trong request path gọi hàm này. |
| risk | callable | `cvf_runtime/risk.py · requirement_for` | Đọc policy đúng; không tự nó là control chặn. |
| approval | **load-bearing, known-principal checked (P-FIX-3, 2026-07-22)** | `cvf_runtime/approval.py · assert_approval_satisfied` + `CvfProfile.known_role_for` (`known-principals.yaml`) | Sửa High Finding #4.1: trước đây approver_id/role do caller tự khai trong cùng request được chấp nhận vô điều kiện (HTTP probe: 2 approver bịa hoàn toàn confirm được R3, trả 200). Giờ mỗi seat quorum phải khớp một principal trong `known-principals.yaml` với role đăng ký đủ thẩm quyền — caller không còn bịa id hay tự nâng role. **Còn hạn chế:** đây KHÔNG phải xác thực thật (không chữ ký/token/session) — chỉ là registry chặn bịa hoàn toàn. P2-B (2026-07-22) triển khai auth thật cho `identity` (xem mục đó) nhưng **cố ý không đụng tới `known-principals.yaml`** — registry approver này vẫn tách biệt khỏi bảng `users` mới, chưa được thay bằng auth thật. Reconciliation này vẫn còn mở, chưa có tranche nào nhận. Test: `tests/cvf/test_approval_known_principals.py` (4 test) + HTTP probe xác nhận 409 thay vì 200. |
| evidence | **load-bearing trên cả 2 backend (P-FIX-3, 2026-07-22)** | `cvf_runtime/evidence.py · assert_evidence_sufficient`; persistence qua `operations_ledger._evidence` (bảng `evidence_links`, map trong `tables.py`) | Sửa Critical Finding #2: trước đây `SqlLedger` không map cột evidence — event R2+ ghi evidence xong đọc lại còn 0, `confirm` bị evidence gate từ chối chính event đã có đủ evidence. Task cũng gãy tương tự qua HTTP (`TaskInput` thiếu field evidence). Cả 2 đã sửa: evidence ghi 1 lần lúc tạo (bảng riêng, giống `corrections`), đọc lại đúng; `TaskInput`/router thêm field `evidence`. Test: `tests/integration/test_evidence_persistence.py` (4 test, reproduce đúng kịch bản probe cũ của Codex) + HTTP probe xác nhận R3 task với evidence qua API trả 200. |
| audit | **load-bearing, atomic với mutation (P-FIX-2, 2026-07-22)** | `Ledger.transaction()` (unit-of-work) qua `Ledger.append_audit(record, unit=unit)` | Sửa High Finding #5: trước đây mutation commit trước, audit ghi sau trong transaction riêng — audit fail thì mutation vẫn đứng không audit. Giờ `EventService.confirm`, `CorrectionService.correct_event`, `TaskService.create_task`/`transition`, `ShiftService.freeze` đều bọc state-change + audit-append trong `transaction()`; `SqlLedger` dùng transaction SQL thật, `InMemoryLedger` snapshot/rollback (deep copy). Test: `tests/cvf/test_atomic_mutation_audit.py` (10 test, failure-injection trên `append_audit`, cả 2 backend, cả 4 service). Phát hiện phụ trong lúc sửa: `InMemoryLedger.get_event/get_task/get_shift` trước đây trả về reference sống, không phải bản sao — service mutate object trước khi vào transaction đã làm rollback vô nghĩa; đã sửa trả `model_copy()`. |
| cost | callable, AI-gated (chưa có runtime caller) | `cvf_runtime/budget.py · assert_within_budget` | Không nơi nào trong request path gọi hàm này; sẽ load-bearing khi ai-gateway wire tới. |
| refusal | callable một phần | `cvf_runtime/errors.py · CvfDenied` → HTTP map | `CvfDenied` chỉ là exception container; refusal-policy.yaml yêu cầu route tới supervisor + ghi lý do — **chưa implement**, không route, không ghi audit riêng cho refusal. |
| termination | callable, AI-gated (chưa có runtime caller) | `cvf_runtime/termination.py` | Tương tự cost — chưa có caller thật. |
| freeze | **load-bearing (P-FIX-1, 2026-07-22)** | `ShiftService.freeze` (identity/permission/`shift_closed` + explicit audited override cho report/handover chưa implement); `InMemoryLedger`/`SqlLedger` chặn mọi mutation (`add_event/put_event/add_task/put_task`) khi shift cha `FROZEN`, trừ `CorrectionService` (`allow_when_frozen=True`, đúng thiết kế "post-freeze correction record only") | Sửa Critical Finding #1: trước đây `freeze_shift` bypass hoàn toàn (HTTP probe trả `200 FROZEN` không điều kiện); giờ trả `409` cho tới khi `shift_closed` + override tường minh. Test end-to-end: `tests/cvf/test_freeze_invariant.py` (12 test, cả 2 backend). **Còn hạn chế:** `report_approved`/`open_handover_items_linked` chưa có model (Phase 5/P2-D) nên dùng override tường minh có audit, không phải kiểm thật — ghi rõ để không lặp lại over-claim. Freeze's `shift_closed` check chỉ đọc `shift.status` — nó tin đúng bằng đúng mức mà `shift.close` (dòng dưới) đáng tin; trước P-FIX-6, `shift_closed` có thể bị thỏa mãn bởi một lần close vô danh không qua permission/audit. |
| shift.close | **load-bearing (P-FIX-6, 2026-07-22)** | `ShiftService.close` (identity/permission `shift.close` role tối thiểu `operator` + state-check chặn close một shift đã `FROZEN`) → `Ledger.transaction()` bọc `close_shift` + `append_audit` atomic, cùng khuôn `freeze`/`TaskService` | Sửa gap review độc lập thứ hai tìm ra 2026-07-22: `POST /shifts/{shift_id}/close` trước đây gọi thẳng `ledger.close_shift(shift_id)` từ router — không `get_principal`, không `require_action`, không audit; probe xác nhận `anonymous_close=200`, `audit_count=0`. Vì freeze chỉ kiểm `shift.status == CLOSED`, close vô danh đó có thể âm thầm thỏa mãn tiền đề `shift_closed` của freeze. Test: `tests/cvf/test_shift_close_governance.py` (13 test: 401 vô danh, 403 role thấp, 200 + audit cho principal hợp lệ, rollback atomic khi audit fail trên cả 2 backend, chặn close shift đã FROZEN, chuỗi đầy đủ create→close có governance→freeze qua cả service lẫn HTTP). **Không** đụng tới approval/known-principals (High Finding #4) — ngoài phạm vi tranche này. |
| customer_request.create / .transition | **load-bearing (P2-A-CUSTOMER-REQUEST, 2026-07-22; repaired after independent review, 2026-07-22)** | `CustomerRequestService.create_customer_request` (identity/permission `customer_request.create` role tối thiểu `operator` → `domain_lock` `customer_request` → `source_message_id` existence check qua `Ledger.message_exists()` khi được cung cấp → frozen-shift check chỉ khi `shift_id` được cung cấp → `Ledger.transaction()` bọc `add_customer_request` + `append_audit` atomic) / `.transition` (identity/permission `customer_request.transition` → `assert_customer_request_transition` lifecycle guard → transaction atomic) | Domain thứ năm nhân bản cùng khuôn `TaskService`/`ShiftService`. **Không có** risk/evidence/approval gate cho create — `customer_requests` không có cột `risk`/`state`/evidence trong migration 002, nên chain này ngắn hơn Task/Event có chủ đích, không phải thiếu sót. Test: `tests/cvf/test_customer_request_vertical.py` (18 test: service+HTTP create, 401/403, lifecycle hợp lệ/không hợp lệ bao gồm WAITING không được nhảy thẳng CLOSED, CLOSED terminal, rollback atomic cả 2 backend, tạo có/không `shift_id`, tạo bị chặn khi shift cha FROZEN) + `tests/cvf/test_customer_request_repair.py` (11 test: InMemory alias-bypass, `source_message_id` hợp lệ/không tồn tại trên cả 2 backend + HTTP không còn 500, `promised_at` sai định dạng trả 422, domain_lock negative-profile thật). **Sửa sau independent review 2026-07-22:** InMemoryLedger từng lưu/trả về CHÍNH object mutable của caller cho `add/get/put_customer_request` — `created.status = CLOSED` có thể âm thầm đổi state đã lưu, không qua permission/lifecycle/transaction/audit; giờ trả bản `model_copy()` giống mọi entity khác. `source_message_id` từng được kiểm không nhất quán: InMemory chấp nhận vô điều kiện, SqlLedger/SQLite raise `IntegrityError` từ FK không được bắt, có thể lộ ra HTTP 500; giờ validate qua `message_exists()` trước khi persist trên cả 2 backend, trả `CvfDenied(control="reference", http_status=404)` nhất quán. Router's `promised_at` từng khai `str | None`, giá trị sai định dạng chỉ fail khi construct `CustomerRequest(...)` trong route (ValidationError không được router bắt) → lộ HTTP 500; giờ khai `datetime | None` trên `CustomerRequestInput` để Pydantic reject ở request-boundary, trả 422. **Còn hạn chế:** `messages` vẫn chưa có persistence vertical thật; identity không còn là giới hạn ở đây (P2-B, 2026-07-22). |

## Thứ tự chain trong `EventService.confirm` (thiết kế — chưa phải bảo đảm runtime)

**Lưu ý:** sơ đồ dưới đây là snapshot lịch sử từ trước các tranche P-FIX; chỉ
dòng `identity` được cập nhật ở đây (P2-B, 2026-07-22). Các dòng khác
(freeze/state, evidence, audit) mô tả trạng thái TRƯỚC P-FIX-1/2/3 và đã lỗi
thời — trạng thái đúng hiện tại nằm ở "Golden verticals — phạm vi chính xác"
phía trên, không phải sơ đồ này.

```text
identity        (dependency: get_principal — xác thực thật qua JWT bearer
                 token, P2-B 2026-07-22; xem bảng trên)
   ↓
permission      (require_action "event.confirm")
   ↓
freeze/state    (assert_transition: PROPOSED → CONFIRMED — KHÔNG kiểm shift cha)
   ↓
evidence        (assert_evidence_sufficient — gãy trên SqlLedger)
   ↓
approval        (assert_approval_satisfied — KHÔNG xác thực approver)
   ↓
[mutation]      (state = CONFIRMED, version += 1)
   ↓
audit           (KHÔNG atomic với bước mutation ở trên)
```

## Việc cần làm trước khi dùng lại nhãn "enforced"/"12/12"

Xem `docs/implementation/EXECUTION_ROADMAP.md` các tranche `P-FIX-*`. Tóm tắt:
sửa freeze thành bất biến xuyên-record thật, gộp mutation+audit atomic, lưu
evidence qua SqlLedger + xác thực approval server-side, sửa migration Task và
siết parity test, sửa catalog `--check` và đồng bộ toàn bộ front door, và
(P-FIX-6) đóng gap `shift.close` vô danh không qua governance.

**Trạng thái sau P-FIX-6:** `P-FIX CLOSED_BOUNDED` — bounded nghĩa là: mọi gap
Critical/High mà 2 review độc lập tìm ra tới nay đã có test end-to-end xác
nhận, nhưng KHÔNG có nghĩa "tất cả High Finding đã sửa xong". High Finding #4
còn nguyên các giới hạn chưa sửa (liệt kê trong
`SESSION/ACTIVE_SESSION_STATE.json` `blocked_work` và
`IMPLEMENTATION_STATUS.json`). **2026-07-22 (P2-B):** identity đã chuyển từ
header-based sang xác thực thật qua JWT — không còn ở danh sách này. Vẫn còn
mở: data minimization chỉ mang tính khuyến nghị; `data_scope`/`cost`/
`termination` chưa có runtime caller; refusal routing/recording chưa
implement; known-principals chỉ là registry check, KHÔNG được P2-B thay thế
(reconciliation với bảng `users` mới vẫn chưa có tranche nào nhận). Không viết
"tất cả High Finding đã sửa" ở bất kỳ đâu.
