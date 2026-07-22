# Session Memory

Human companion to [`ACTIVE_SESSION_STATE.json`](ACTIVE_SESSION_STATE.json).
Provider-neutral — for every agent and human. Keep it short; details live in the
handoffs.

_Last updated: 2026-07-22 (P-FIX-6)_

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

## Trạng thái hiện tại (verify bằng lệnh, không tin số liệu trong file)

- **CVF controls:** 12/12 có hàm gate + unit test ("callable"). **Không phải
  12/12 "load-bearing"** — xem bảng chi tiết ở
  `docs/cvf/CVF_CONTROL_MAPPING.md` (đã viết lại 2026-07-22 theo đúng phân
  biệt callable/load-bearing/not-verified-server-side).
- **Ba service tái dùng đúng gate** (Event/Correction/Task đều gọi cùng hàm
  `cvf_runtime`, không fork) — điểm này Codex xác nhận đúng. Nhưng gọi chúng là
  "golden vertical durable end-to-end" là sai: xem Critical Finding #1, #2 và
  High Finding #3, #4 trong bản review 07-22.
- **Persistence:** `operations-ledger` dual-backend (SQLite/PostgreSQL qua
  `Ledger` Protocol). SQLite verified cho scalar field, nhưng **đánh rơi
  evidence** (event) — Critical #2. PostgreSQL **sẽ crash thật** khi insert
  Task vì migration 002 thiếu cột `version` mà runtime luôn ghi — High #3.
- **Catalog/session/file-size guard:** file-size và session-state check là
  **cổng thật** (probe âm xác nhận). Catalog `--check` là **cổng nông** — chỉ
  validate cấu trúc registry, không phát hiện metric/Markdown bị lệch (Medium
  #6). Không dùng nó làm bằng chứng "catalog luôn tươi".
- **Tests:** chạy `python -m pytest -q` để lấy số hiện tại; đừng chép số cũ từ
  file khác — đây chính là spec-drift Codex nêu ở Medium #7.

## Next allowed move

Tranche **P-FIX** (P-FIX-0 → P-FIX-6) đã đóng — **5 tranche triển khai
P-FIX-1 tới P-FIX-5, cộng tranche chuẩn bị P-FIX-0; 6 commit trước P-FIX-6,
7 commit P-FIX sau P-FIX-6.** P2-A (domain còn lại)/P2-B/P2-C chỉ mở lại
**sau khi** toàn bộ closure surface (roadmap, control mapping, implementation
status, catalog, session memory, active session state, handoff) đã đồng bộ
đúng trạng thái P-FIX-6 — xem `next_allowed_move` trong
`ACTIVE_SESSION_STATE.json` cho câu chính xác.

## Không được làm (không có xác nhận mới)

Xem `blocked_work` trong `ACTIVE_SESSION_STATE.json`. Cốt lõi: không dùng lại
nhãn "enforced"/"12/12"/"golden vertical"/"tất cả High Finding đã sửa" không
giới hạn; không thêm domain mới (P2-A tiếp) trước khi mọi closure surface của
P-FIX-6 đồng bộ xong; không tạo file điểm-vào theo provider — front door là
`CONTRIBUTING.md`, trung lập; không tin tuyên bố "CLOSED" của bất kỳ agent nào
(kể cả chính agent viết ra nó) mà không tự chạy lại probe/test — đây chính là
bài học P-FIX-6.
