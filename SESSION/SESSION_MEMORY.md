# Session Memory

Human companion to [`ACTIVE_SESSION_STATE.json`](ACTIVE_SESSION_STATE.json).
Provider-neutral — for every agent and human. Keep it short; details live in the
handoffs.

_Last updated: 2026-07-22 (P2-B real authentication)_

## Where the project is

Repo bắt đầu là **blueprint trung thực nhưng CVF controls chỉ nằm trên giấy**
(xem `docs/decisions/EA_INDEPENDENT_REVIEW_2026-07-21.md`). Qua các phiên
buildout, CVF controls được đưa vào code + test, và một **review độc lập thứ
hai** (`docs/decisions/EA_INDEPENDENT_REVIEW_2026-07-22_CODEX.md`) chứng minh
bằng probe chạy thật rằng nhiều tuyên bố của các phiên đó — "12/12 enforced",
"golden vertical durable", "PostgreSQL same code path" — **đã over-claim**.
Freeze bypass được, evidence mất trên SqlLedger, approval là tự khai, audit
không atomic, migration Task thiếu cột `version`. Đây là bằng chứng đúng thứ
CVF được thiết kế để bắt: không một agent nào (kể cả agent đã build) được tin
tuyệt đối lời tự khai của chính nó.

**2026-07-22 (P-FIX-6):** một agent tuyên bố tranche P-FIX **CLOSED** sau
P-FIX-5. Một review độc lập **thứ hai** bác bỏ tuyên bố đó: `POST
/shifts/{shift_id}/close` vẫn gọi thẳng `ledger.close_shift()` từ router —
không identity, không permission, không audit (probe: `create=200`,
`anonymous_close=200`, `status=CLOSED`, `audit_count=0`). Vì
`ShiftService.freeze` chỉ kiểm `shift.status == ShiftStatus.CLOSED`, close vô
danh đó có thể âm thầm thỏa mãn tiền đề `shift_closed` của freeze — đúng loại
bypass CVF được thiết kế để bắt, xảy ra ngay trong chính tranche tuyên bố đã
sửa hết các bypass đó. Bài học lặp lại: front-door "CLOSED" là tuyên bố của
agent, không phải bằng chứng — luôn verify bằng probe/test thật trước khi tin.
P-FIX-6 thêm `shift.close` làm governed action thật và sửa toàn bộ front-door
drift bên dưới. Trạng thái đúng bây giờ là **`P-FIX CLOSED_BOUNDED`** — xem
"Không được làm" bên dưới cho danh sách giới hạn vẫn còn treo (KHÔNG phải "tất
cả High Finding đã sửa").

**2026-07-22 (P2-A-CUSTOMER-REQUEST):** với P-FIX đã đóng bounded, operator
mở lại Phase 2 roadmap, chỉ định P2-A: nhân bản CVF chain sang domain thứ năm
— `customer_request`. Đã nhân bản đúng khuôn `TaskService`/`ShiftService`:
`CustomerRequest` model + `CustomerRequestStatus` lifecycle, bảng
`customer_requests` map vào `tables.py` (khớp migration 002 hai chiều qua
schema-parity test), `add/get/put_customer_request` trên cả Protocol/
InMemoryLedger/SqlLedger, `CustomerRequestService` (create: identity→
permission→domain_lock→persist(frozen-shift check chỉ khi có shift_id)→audit;
transition: identity→permission→lifecycle guard→persist→audit), router
`/customer-requests`, 18 test mới. **Chính xác về phạm vi:** P2-A
(customer_request) đã xong; P2-A (incidents, handovers) VẪN còn mở — 2 domain
đó chưa có bảng migration, cần migration mới trước. Không tuyên bố "P2-A đã
đóng" chung chung.

**2026-07-22 (P2-B):** operator chọn P2-B (authentication thật) trong 3 lane
hợp lệ. `dependencies.py · get_principal` không còn đọc `X-User-Id`/
`X-User-Role` — giờ yêu cầu JWT bearer token đã ký hợp lệ
(`workspace_api/auth/tokens.py`, `JWT_SECRET_KEY` bắt buộc không default),
xây `Principal` chỉ từ claim đã xác thực chữ ký. `POST /auth/login` cấp token
sau khi kiểm username/mật khẩu (bcrypt) so với bảng `users` mới. Mọi router
giữ nguyên `Depends(get_principal)`. `identity` chuyển từ "not verified
server-side" sang "load-bearing". **Cố ý KHÔNG đụng tới:**
`known-principals.yaml` (registry approver riêng cho quorum R3/R4 — High
Finding #4 vẫn mở), refresh token/revocation, tự đăng ký, đặt lại mật khẩu,
rate-limit đăng nhập. Cấp user chỉ qua `scripts/seed_dev_users.py` (dev/test).
Chi tiết: `docs/decisions/ADR_2026-07-22_P2B_JWT_AUTHENTICATION.md`,
`SESSION/handoffs/AGENT_HANDOFF_2026-07-22_P2B_AUTHENTICATION.md`.

## Trạng thái hiện tại (verify bằng lệnh, không tin số liệu trong file)

Bốn bullet dưới đây mô tả tình trạng **sau P-FIX-6**. Bản review Codex gốc
(2026-07-22, trước P-FIX-1..6) tìm ra các lỗi nghiêm trọng hơn — freeze bypass,
evidence mất trên SqlLedger, PostgreSQL Task.version thiếu cột — nhưng những
lỗi đó **đã sửa** ở P-FIX-1/P-FIX-3/P-FIX-4; xem
`docs/decisions/EA_INDEPENDENT_REVIEW_2026-07-22_CODEX.md` cho snapshot lịch
sử, không phải trạng thái hiện tại.

- **CVF controls:** 12/12 có hàm gate + unit test ("callable"). **Không phải
  12/12 "load-bearing"** — xem bảng chi tiết ở
  `docs/cvf/CVF_CONTROL_MAPPING.md` (đã viết lại 2026-07-22, cập nhật lần nữa
  ở P-FIX-6 closure-cleanup để thêm dòng `shift.close`).
- **Năm service tái dùng đúng gate** (Event/Correction/Task/Shift/
  CustomerRequest đều gọi cùng hàm `cvf_runtime`, không fork). Tránh nhãn
  "golden vertical durable end-to-end" không giới hạn — xem "Golden verticals
  — phạm vi chính xác" trong `CVF_CONTROL_MAPPING.md` cho giới hạn còn lại
  theo từng domain. Evidence qua SqlLedger/HTTP (Event/Task) đã sửa ở P-FIX-3,
  không còn là gap; identity không còn là giới hạn chung (P2-B, 2026-07-22) —
  giới hạn còn lại là approval không xác thực approver độc lập (Event/
  Correction). Shift và
  CustomerRequest là các domain có ít giới hạn riêng nhất tính đến
  2026-07-22 (CustomerRequest không có approval/evidence chain vì migration
  không có cột đó).
- **Persistence:** `operations-ledger` dual-backend (SQLite/PostgreSQL qua
  `Ledger` Protocol). Evidence persist đúng qua cả 2 backend (P-FIX-3);
  migration Task.version đã có cột và schema-parity test đã siết (P-FIX-4,
  P-FIX-6 closure-cleanup thêm PK/FK hai chiều + type-family + CHECK
  expression). **Vẫn NOT LIVE VERIFIED**: chưa từng chạy migration + round-trip
  thật trên PostgreSQL (không có Docker trong môi trường này) — pre-ship gate.
- **Catalog/session/file-size guard:** file-size và session-state check là
  **cổng thật** (probe âm xác nhận). Catalog `--check` từ P-FIX-5 recompute
  metrics/Markdown thật và diff với đĩa (probe âm xác nhận, không còn là cổng
  nông).
- **Identity:** load-bearing (P2-B, 2026-07-22) — JWT bearer token thật thay
  header. Không còn là giới hạn chung của 5 domain; giới hạn còn lại của
  Event/Correction là approval không xác thực approver độc lập (registry
  known-principals, KHÔNG được P2-B thay thế).
- **Tests:** chạy `python -m pytest -q` để lấy số hiện tại; đừng chép số cũ từ
  file khác — spec-drift là chính lỗi Codex nêu ở Medium #7 của review gốc.

## Hai batch đã hoàn tất (2026-07-22)

Batch customer_request và bootstrap-continuity đã review và commit riêng. Xem
active handoff `AGENT_HANDOFF_2026-07-22_POST_BOOTSTRAP.md`; handoff
`AGENT_HANDOFF_2026-07-22_TWO_PENDING_BATCHES.md` giữ lại lịch sử checkpoint:

1. **customer_request repair** — `COMMITTED_REVIEW_PASS` tại `0429c4a`.
   lập đã PASS (35/35 test mục tiêu, 149/149 toàn bộ suite, validate_repository
   PASS, catalog PASS, session-state PASS). Đã xong, đã review và **đã
   commit riêng**. Không sửa lại code này trừ khi có regression mới được chứng
   minh.
2. **bootstrap-continuity** — `COMMITTED_REVIEW_PASS` tại `acc5d09`. Review
   độc lập lần 1 trả `REVIEW_CHANGES_REQUIRED` (5 finding: token
   `{{CVF_CORE_PATH}}` chưa resolve, `CVF_SESSION_MEMORY.md` khai sai là
   không có `CVF_SESSION/`, bootstrap log mâu thuẫn với worktree thật,
   continuity không phản ánh 2 batch đang treo, mirror không có drift-check
   xác định). Review độc lập lần 2 đã sửa và xác nhận lại checker bằng probe
   âm; batch đã commit riêng.

## Portable clone continuity (2026-07-22)

Project dùng manifest schema 2.0 với repository URL, commit pin và đường dẫn
tương đối. `scripts/initialize_cvf_clone.ps1` tự dựng/kiểm tra CVF core sibling,
tạo `.cvf/local-binding.json` bị Git ignore và chạy doctor. Fresh clone thật từ
GitHub đã PASS 24/24, resolve đúng active handoff và pin public core
`c1076dc4be9ef9058b7c4e7b96def59c26aab148`. Active handoff hiện tại là
`AGENT_HANDOFF_2026-07-22_PORTABLE_CLONE.md`.

## Next allowed move

Operator chọn đúng một lane mới và bắt đầu tại INTAKE: P2-A (còn lại —
incidents/handovers, cần migration mới trước), reconcile
`known-principals.yaml` với bảng `users` mới (High Finding #4 vẫn mở), hoặc
P2-C (frontend UI).
Xem `next_allowed_move` trong `ACTIVE_SESSION_STATE.json` cho câu chính xác.

## Không được làm (không có xác nhận mới)

Xem `blocked_work` trong `ACTIVE_SESSION_STATE.json`. Cốt lõi: không dùng lại
nhãn "enforced"/"12/12"/"golden vertical"/"tất cả High Finding đã sửa" không
giới hạn; không tuyên bố "P2-A đã đóng" chung chung — chỉ customer_request
xong, incidents/handovers vẫn mở và cần migration mới; không tuyên bố "High
Finding #4 đã sửa" — P2-B chỉ sửa identity, KHÔNG đụng known-principals.yaml/
approval; không tuyên bố P2-B có refresh token/revocation hay admin
user-provisioning thật (chỉ có `scripts/seed_dev_users.py`, dev/test); không
tạo file điểm-vào theo provider — front door là `CONTRIBUTING.md`, trung lập;
không tin tuyên bố "CLOSED"/"đã xong" của bất kỳ agent nào (kể cả chính agent
viết ra nó) mà không tự chạy lại probe/test — đây chính là bài học P-FIX-6;
không coi `CVF_SESSION/ACTIVE_SESSION_STATE.json` là nguồn canonical — nó chỉ
là compatibility mirror, `python scripts/check_session_state.py` xác nhận
không lệch trước khi kết thúc phiên có sửa 1 trong 2 file state.
