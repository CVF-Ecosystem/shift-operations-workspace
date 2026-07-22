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
- **Bốn service tái dùng đúng gate** (Event/Correction/Task/Shift đều gọi cùng
  hàm `cvf_runtime`, không fork). Tránh nhãn "golden vertical durable
  end-to-end" không giới hạn — xem "Golden verticals — phạm vi chính xác" trong
  `CVF_CONTROL_MAPPING.md` cho giới hạn còn lại theo từng domain (Event/Task
  vẫn có gap qua SqlLedger/HTTP; Shift là domain có bằng chứng end-to-end mạnh
  nhất tính đến P-FIX-6).
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
- **Tests:** chạy `python -m pytest -q` để lấy số hiện tại; đừng chép số cũ từ
  file khác — spec-drift là chính lỗi Codex nêu ở Medium #7 của review gốc.

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
