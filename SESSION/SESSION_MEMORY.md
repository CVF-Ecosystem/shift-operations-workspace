# Session Memory

Human companion to [`ACTIVE_SESSION_STATE.json`](ACTIVE_SESSION_STATE.json).
Provider-neutral — for every agent and human. Keep it short; details live in the
handoffs.

_Last updated: 2026-07-22_

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

Nguồn thứ tự là [`docs/implementation/EXECUTION_ROADMAP.md`](../docs/implementation/EXECUTION_ROADMAP.md),
tranche **P-FIX-0 → P-FIX-5** (sửa lỗi Codex tìm ra), **trước** khi mở lại P2-A
domain mới hay bất kỳ phase mới nào. Thứ tự: (0) nắn tuyên bố sai trong docs —
**đang làm, file này là một phần của nó**; (1) freeze thành bất biến thật; (2)
mutation+audit atomic; (3) evidence persist + approval xác thực server-side;
(4) migration Task.version + parity test siết chặt; (5) catalog `--check`
thật + đồng bộ mọi front door.

## Không được làm (không có xác nhận mới)

Xem `blocked_work` trong `ACTIVE_SESSION_STATE.json`. Cốt lõi: không dùng lại
nhãn "enforced"/"12/12"/"golden vertical" không giới hạn cho tới khi P-FIX-1
đến P-FIX-4 xong và có test end-to-end xác nhận; không thêm domain mới (P2-A
tiếp) trước khi P-FIX-0 xong; không tạo file điểm-vào theo provider — front
door là `CONTRIBUTING.md`, trung lập.
