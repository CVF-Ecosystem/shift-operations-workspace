# Contributing

Quy tắc đóng góp cho repository đã khóa. **Tài liệu này là front door
governance, trung lập provider — áp dụng cho MỌI agent (Claude, Codex, Gemini,
hay bất kỳ agent/dev nào) và mọi con người.** Không có file điểm-vào riêng theo
provider; không provider nào là trung tâm.

## Bắt đầu một phiên làm việc (mọi agent/dev đọc trước)

Trước khi làm bất kỳ việc governance nào (build, review, sửa contract, handoff),
đọc theo thứ tự:

1. **Session state (machine):** [`SESSION/ACTIVE_SESSION_STATE.json`](SESSION/ACTIVE_SESSION_STATE.json)
   — mode hiện tại, handoff đang hoạt động, next allowed move, blocked work,
   và danh sách required reads.
2. **Session memory (human):** [`SESSION/SESSION_MEMORY.md`](SESSION/SESSION_MEMORY.md)
   — tóm tắt tiến độ và next move.
3. **Handoff đang hoạt động:** file trong `SESSION/handoffs/` mà session state
   trỏ tới — đã làm gì, kết quả, việc kế tiếp.
4. **Roadmap (nguồn thứ tự):** [`docs/implementation/EXECUTION_ROADMAP.md`](docs/implementation/EXECUTION_ROADMAP.md)
   — 5 phase + P0, mỗi phase có exit gate; lấy item `[ ]` kế tiếp theo thứ tự,
   không nhảy phase khi gate trước chưa đạt.
5. **Cấu trúc dự án:** [`docs/catalog/MODULE_CATALOG.md`](docs/catalog/MODULE_CATALOG.md)
   (nguồn máy: `docs/catalog/MODULE_REGISTRY.json`) — module nào đã có code /
   contract / stub.
6. **CVF control → điểm enforce:** [`docs/cvf/CVF_CONTROL_MAPPING.md`](docs/cvf/CVF_CONTROL_MAPPING.md).

Sau đó, nêu một câu xác nhận khởi động: *mode hiện tại, handoff đang hoạt động,
next allowed move, blocked work* — trong handoff hoặc trong phản hồi.

## Khi kết thúc một phiên (ghi lại để phiên sau tiếp nối)

1. Viết/cập nhật handoff trong `SESSION/handoffs/AGENT_HANDOFF_<ngày>.md`:
   đã làm gì, kết quả kiểm chứng, next allowed move, blocked work.
2. Cập nhật `SESSION/ACTIVE_SESSION_STATE.json` (trỏ tới handoff mới, cập nhật
   next move) và `SESSION/SESSION_MEMORY.md`.
3. Nếu có thay đổi module: cập nhật `docs/catalog/MODULE_REGISTRY.json` rồi chạy
   `python scripts/generate_catalog.py --write`.
4. Chạy cổng: `python scripts/testing/validate_repository.py` (gồm catalog +
   session-state + file-size check) và `python -m pytest -q` phải pass.
5. **Commit ngay khi một tranche (roadmap item, vd P1-A) hoàn tất và cổng
   pass — không gộp nhiều tranche vào một commit.** Push lên
   `origin main` ngay sau mỗi commit để giữ vết. Message nêu rõ mã tranche
   (vd `P1-A: ...`) và kết quả kiểm chứng.

**File size:** trước khi thêm code/test/prose vào file gần ngưỡng, xem
[`docs/reference/FILE_SIZE_GUARD.md`](docs/reference/FILE_SIZE_GUARD.md). Vượt
hard limit thì tách module/file, **không** nén prose để lọt guard; file sinh tự
động hoặc có lý do chính đáng thì đăng ký trong exception registry.

## Workflow

Mọi thay đổi đi theo INTAKE → DESIGN → SPEC → WORK ORDER → BUILD → REVIEW →
FREEZE. Pull request phải nêu phase, acceptance gate và risk class liên quan.

## Architecture discipline

Không đổi tên module, di chuyển contract hoặc thêm provider-specific business
logic nếu chưa có Architecture Amendment (`docs/decisions/`). Không đặt tên
artifact hay khóa hành vi theo một provider cụ thể — CVF trung lập provider.

**Trước khi xây/động vào UI hoặc tầng API–DB, đọc**
[`docs/architecture/FRONTEND_BACKEND_BOUNDARY.md`](docs/architecture/FRONTEND_BACKEND_BOUNDARY.md).
Luật cốt lõi: frontend chỉ gọi backend qua HTTP (`VITE_API_URL`); **mọi CVF
governance enforce ở backend, không ở frontend**; database truy cập qua
`Ledger` Protocol (`DATABASE_URL`), lưu trữ riêng.

## Evidence

Mọi thay đổi behavior phải đi kèm test, fixture hoặc evidence có thể tái lập.

## Definition of done

Code compile, contract validation pass, tests liên quan pass, docs được cập
nhật, session state + handoff được cập nhật, và không có placeholder giả làm
production implementation.
