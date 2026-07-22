# Agent Handoff — 2026-07-22 (P-FIX-1)

Provider-neutral handoff. Continues from
[`AGENT_HANDOFF_2026-07-22_PFIX.md`](AGENT_HANDOFF_2026-07-22_PFIX.md).

- **Mode:** corrective_fix_before_new_domains
- **Tranche:** P-FIX-1 (Execution Roadmap P-FIX corrective tranche)
- **Startup ack:** mode=corrective_fix_before_new_domains; active
  handoff=this file; next allowed move=P-FIX-2; blocked work=see
  `ACTIVE_SESSION_STATE.json` (do NOT open new domains/phases).

## Việc đã làm — freeze thành bất biến xuyên-record thật

Sửa Critical Finding #1 của bản review Codex
(`docs/decisions/EA_INDEPENDENT_REVIEW_2026-07-22_CODEX.md`): trước đây
`POST /shifts/{id}/freeze` freeze một shift OPEN mới tạo ngay lập tức, không
kiểm identity/permission/prerequisite; sau freeze, `SqlLedger` không chặn
mutation trên record con trong khi `InMemoryLedger` chỉ chặn *tạo mới*.

1. **`ShiftService`** (mới, `application/shift_service.py`): `freeze()` chạy
   chain identity → permission (`shift.freeze`, min-role `shift_supervisor`) →
   `shift_closed` (kiểm thật, có model) → prerequisite chưa implement
   (`report_approved`, `open_handover_items_linked` — Report/Handover model
   chưa tồn tại, Phase 5/P2-D) yêu cầu **override tường minh + lý do bắt
   buộc**, ghi 2 audit record riêng (freeze + override) — không giả vờ đã
   kiểm điều không kiểm được.
2. **`close_shift`** thêm vào `Ledger` Protocol + `InMemoryLedger` + `SqlLedger`
   (trước đây không có cách nào đóng ca).
3. **Cross-record invariant ở tầng ledger** (chỗ Codex chỉ đích danh):
   `InMemoryLedger`/`SqlLedger.add_event/put_event/add_task/put_task` giờ đều
   chặn khi shift cha `FROZEN`, qua `_assert_shift_not_frozen` mỗi backend.
   Trước đây `SqlLedger` không kiểm gì; `InMemoryLedger` chỉ kiểm `add_*`
   (tạo mới), không kiểm `put_*` (sửa) — đã sửa cả hai.
4. **`CorrectionService`** dùng `put_event(event, allow_when_frozen=True)` —
   đường mutation hợp lệ duy nhất sau freeze (đúng
   `post_freeze_mutation: correction_record_only`).
5. Router `shifts`: thêm `POST /shifts/{id}/close`; `freeze` chuyển qua
   `ShiftService`, nhận `principal` + `FreezeInput` (override flag + reason).

## Kết quả kiểm chứng

- **12 test mới** (`tests/cvf/test_freeze_invariant.py`), tham số hoá cả
  `InMemoryLedger` và `SqlLedger`: permission chặn, thiếu `shift_closed` chặn,
  thiếu override chặn, thiếu reason chặn, freeze thành công có 2 audit record,
  event/task mutation bị chặn sau freeze (cả 2 backend), event mới bị chặn sau
  freeze, correction vẫn được phép sau freeze.
- **HTTP probe trực tiếp** (cùng cách Codex dùng để tìm ra lỗi): trước fix
  `POST /shifts/{id}/freeze` không tham số → `200 FROZEN`. Sau fix → `409`
  với lý do rõ ("freeze requires shift_closed..."); chỉ `200 FROZEN` sau khi
  `close` + gửi `override_unimplemented_prerequisites=true` kèm `override_reason`.
- `pytest` → **77 passed** (65 trước + 12 mới).
- `validate_repository.py` → PASS (catalog + session + file-size).

## Giới hạn còn lại (ghi rõ, không lặp lại over-claim)

`report_approved`/`open_handover_items_linked` **không được kiểm thật** — chỉ
override tường minh có audit. Khi Report/Handover model được xây (Phase 5/
P2-D), phải thay override bằng kiểm thật và xoá field
`override_unimplemented_prerequisites` khỏi API.

## Next allowed move

**P-FIX-2** — mutation + audit atomic. Hiện `EventService.confirm` ghi state
trước, audit sau, hai bước riêng; `CorrectionService` ba bước riêng (update
event, insert correction, append audit); mỗi `SqlLedger` method tự mở/đóng
transaction riêng. Cần: gộp thành unit-of-work mỗi ledger (transaction chung
cho SqlLedger; cùng nguyên tắc InMemoryLedger); test failure-injection khiến
audit raise — mutation phải rollback, không đứng ở trạng thái "confirmed
nhưng không audit".

Không mở P2-A domain còn lại, P2-B, P2-C, hay bất kỳ phase mới nào cho tới khi
P-FIX-2 → P-FIX-5 xong.

## Blocked

Xem `blocked_work` trong `ACTIVE_SESSION_STATE.json`.
