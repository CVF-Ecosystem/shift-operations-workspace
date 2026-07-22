# Agent Handoff — 2026-07-22 (P-FIX-2)

Provider-neutral handoff. Continues from
[`AGENT_HANDOFF_2026-07-22_PFIX1.md`](AGENT_HANDOFF_2026-07-22_PFIX1.md).

- **Mode:** corrective_fix_before_new_domains
- **Tranche:** P-FIX-2 (Execution Roadmap P-FIX corrective tranche)
- **Startup ack:** mode=corrective_fix_before_new_domains; active
  handoff=this file; next allowed move=P-FIX-3; blocked work=see
  `ACTIVE_SESSION_STATE.json`.

## Việc đã làm — mutation + audit atomic

Sửa **High Finding #5** của bản review Codex: trước đây mỗi ledger method tự
mở/đóng transaction riêng, nên state-change và audit-append là hai thao tác
tách biệt — audit fail thì mutation vẫn đứng, không có audit record.

1. **`Ledger` Protocol**: thêm `transaction()` (context manager) + tham số
   `unit=None` cho mọi method mutating (`create_shift`, `close_shift`,
   `freeze_shift`, `add_event`, `put_event`, `add_task`, `put_task`,
   `add_correction`, `append_audit`). Không truyền `unit` → hành vi cũ (tự mở
   transaction riêng); truyền `unit` → dùng chung transaction của caller.
2. **`SqlLedger.transaction()`**: `self.engine.begin()` — transaction SQL
   thật. Mỗi method nhận `unit` là chính connection đó.
3. **`InMemoryLedger.transaction()`**: snapshot toàn bộ state bằng
   `copy.deepcopy`, rollback nếu block raise.
4. **Cả 4 service** (`EventService.confirm`, `CorrectionService.correct_event`,
   `TaskService.create_task`/`transition`, `ShiftService.freeze`) giờ bọc mọi
   bước mutation + audit (+ correction insert) trong một
   `with self.ledger.transaction() as unit:`.

## Bug thật tìm thấy và sửa trong lúc viết test

Lần chạy test đầu tiên, 4/10 test atomicity **fail** — không phải vì thiết kế
transaction sai, mà vì `InMemoryLedger.get_event`/`get_task`/`get_shift` trả
về **reference sống** vào dict lưu trữ, không phải bản sao. Service pattern là:

```python
event = self.ledger.get_event(event_id)   # trước đây: chính object trong dict
event.state = DataState.CONFIRMED         # mutate NGAY object lưu trữ
...
with self.ledger.transaction() as unit:   # snapshot chụp SAU KHI đã mutate
    self.ledger.put_event(event, unit=unit)
```

`copy.deepcopy` lúc bắt đầu `transaction()` chụp state đã bị mutate từ trước —
rollback về "state cũ" thực chất là rollback về chính state mới. Sửa gốc rễ:
`get_event`/`get_task`/`get_shift` giờ trả `model_copy()`, khớp đúng cách
`SqlLedger` luôn tái tạo object mới từ row SELECT.

## Kết quả kiểm chứng

- **10 test mới** (`tests/cvf/test_atomic_mutation_audit.py`): failure-injection
  `append_audit` raise cho cả 4 service, cả 2 backend — xác nhận mutation
  KHÔNG sống sót khi audit fail (event/task giữ state cũ, version cũ,
  correction không tồn tại, shift giữ CLOSED thay vì FROZEN).
- `pytest` → **87 passed** (77 trước + 10 mới).
- `validate_repository.py` → PASS (catalog + session + file-size).

## Next allowed move

**P-FIX-3** — lưu evidence qua SqlLedger + xác thực approval server-side:
1. `_rows.py`/`tables.py`: map `evidence_links` (đã có trong migration 001,
   chưa được `SqlLedger` đọc/ghi) cho `OperationalEvent.evidence`; đọc lại
   đúng khi `get_event`.
2. `TaskInput`/`api/tasks/router.py`: thêm field `evidence` — hiện request
   HTTP luôn gửi evidence rỗng vì Pydantic bỏ field lạ.
3. Approval: không chấp nhận `approver_id`/`role` do caller tự khai trong
   cùng request mà không xác thực. Cần ít nhất: nguồn xác thực độc lập (registry
   role đã biết) hoặc ràng buộc approver phải khác với principal đã xác thực
   (hiện identity cũng chỉ qua header, chưa xác thực — P2-B có thể cần đi
   cùng bước này).

Không mở P2-A domain còn lại, P2-B, P2-C, hay bất kỳ phase mới nào cho tới khi
P-FIX-3 → P-FIX-5 xong.

## Blocked

Xem `blocked_work` trong `ACTIVE_SESSION_STATE.json`.
