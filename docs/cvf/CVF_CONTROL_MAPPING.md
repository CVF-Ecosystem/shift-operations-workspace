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

Ba service (`EventService`, `CorrectionService`, `TaskService`) **đều import và
gọi cùng các hàm `cvf_runtime`** — không có bản sao logic permission/evidence/
approval nào bị fork. Đây là phần đã xác nhận đúng.

Nhưng gọi là "golden vertical durable/end-to-end" là **quá rộng**. Chính xác
hơn:

1. **Operational Event → confirm** — `EventService.confirm`. Load-bearing trên
   `InMemoryLedger`. **Trên `SqlLedger`: gãy cho risk R2+** vì
   `operations_ledger/_rows.py` không map cột `evidence` — event mất evidence
   khi đọc lại, nên `assert_evidence_sufficient` từ chối một event đã có đủ
   evidence lúc ghi. Xem Critical Finding #2 trong bản review Codex.
2. **Operational Event → correct** — `CorrectionService.correct_event`.
   Load-bearing về mặt state transition; nhưng approval quorum trong bước này
   **không xác thực approver** (xem mục approval bên dưới).
3. **Task → create / transition** — `TaskService`. Chain đúng ở tầng service
   (test trực tiếp construct `Task` kèm evidence, pass). **Qua HTTP thì gãy**:
   `TaskInput`/`api/tasks/router.py` không có field evidence, nên request thật
   luôn gửi evidence rỗng — task R2+ tạo qua API sẽ bị `evidence` gate từ chối
   dù client gửi kèm evidence (Pydantic bỏ field lạ).

**Không domain nào trong 3 cái trên là "durable end-to-end qua HTTP + SqlLedger
+ evidence" tại thời điểm 2026-07-22.** Sẽ cập nhật khi các fix trong roadmap
(P-FIX-1 → P-FIX-4) hoàn tất và có test end-to-end xác nhận.

## Bảng ánh xạ

| CVF control | Trạng thái | Enforce ở đâu (file · symbol) | Giới hạn đã biết |
|---|---|---|---|
| identity | **not verified server-side** | `dependencies.py · get_principal` đọc header `X-User-Id`/`X-User-Role` | Không xác thực — bất kỳ caller nào tự đặt header là thành principal đó. |
| permission | callable, load-bearing cho role check | `cvf_runtime/permission.py · require_action` | Đúng vai trò tối thiểu theo action, nhưng phụ thuộc identity chưa xác thực ở trên. |
| domain_lock | callable, load-bearing tại `create_event` | `cvf_runtime/domain_lock.py · assert_event_type_in_scope` | Chỉ gắn ở `create_event`; chưa gắn `create_task` hay các domain khác. |
| data_scope | callable, **không có runtime caller** | `cvf_runtime/data_scope.py · assert_placement_allowed` | `allow_after_minimization` cho phép external placement mà không yêu cầu bằng chứng đã minimize — chính sách chỉ mang tính khuyến nghị. Chưa có nơi nào trong request path gọi hàm này. |
| risk | callable | `cvf_runtime/risk.py · requirement_for` | Đọc policy đúng; không tự nó là control chặn. |
| approval | callable, **not verified server-side** | `cvf_runtime/approval.py · assert_approval_satisfied` | Kiểm đúng *hình dạng* quorum (đủ role, đủ người, không tự duyệt), nhưng approver_id/role do caller gửi trong cùng request — không xác thực approver có thật hay có thẩm quyền đó không. |
| evidence | callable, **gãy trên SqlLedger cho event** | `cvf_runtime/evidence.py · assert_evidence_sufficient` | Xem mục Event ở trên — evidence không được SqlLedger persist. |
| audit | **load-bearing, atomic với mutation (P-FIX-2, 2026-07-22)** | `Ledger.transaction()` (unit-of-work) qua `Ledger.append_audit(record, unit=unit)` | Sửa High Finding #5: trước đây mutation commit trước, audit ghi sau trong transaction riêng — audit fail thì mutation vẫn đứng không audit. Giờ `EventService.confirm`, `CorrectionService.correct_event`, `TaskService.create_task`/`transition`, `ShiftService.freeze` đều bọc state-change + audit-append trong `transaction()`; `SqlLedger` dùng transaction SQL thật, `InMemoryLedger` snapshot/rollback (deep copy). Test: `tests/cvf/test_atomic_mutation_audit.py` (10 test, failure-injection trên `append_audit`, cả 2 backend, cả 4 service). Phát hiện phụ trong lúc sửa: `InMemoryLedger.get_event/get_task/get_shift` trước đây trả về reference sống, không phải bản sao — service mutate object trước khi vào transaction đã làm rollback vô nghĩa; đã sửa trả `model_copy()`. |
| cost | callable, AI-gated (chưa có runtime caller) | `cvf_runtime/budget.py · assert_within_budget` | Không nơi nào trong request path gọi hàm này; sẽ load-bearing khi ai-gateway wire tới. |
| refusal | callable một phần | `cvf_runtime/errors.py · CvfDenied` → HTTP map | `CvfDenied` chỉ là exception container; refusal-policy.yaml yêu cầu route tới supervisor + ghi lý do — **chưa implement**, không route, không ghi audit riêng cho refusal. |
| termination | callable, AI-gated (chưa có runtime caller) | `cvf_runtime/termination.py` | Tương tự cost — chưa có caller thật. |
| freeze | **load-bearing (P-FIX-1, 2026-07-22)** | `ShiftService.freeze` (identity/permission/`shift_closed` + explicit audited override cho report/handover chưa implement); `InMemoryLedger`/`SqlLedger` chặn mọi mutation (`add_event/put_event/add_task/put_task`) khi shift cha `FROZEN`, trừ `CorrectionService` (`allow_when_frozen=True`, đúng thiết kế "post-freeze correction record only") | Sửa Critical Finding #1: trước đây `freeze_shift` bypass hoàn toàn (HTTP probe trả `200 FROZEN` không điều kiện); giờ trả `409` cho tới khi `shift_closed` + override tường minh. Test end-to-end: `tests/cvf/test_freeze_invariant.py` (12 test, cả 2 backend). **Còn hạn chế:** `report_approved`/`open_handover_items_linked` chưa có model (Phase 5/P2-D) nên dùng override tường minh có audit, không phải kiểm thật — ghi rõ để không lặp lại over-claim. |

## Thứ tự chain trong `EventService.confirm` (thiết kế — chưa phải bảo đảm runtime)

```text
identity        (dependency: get_principal — KHÔNG xác thực, xem bảng trên)
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
siết parity test, sửa catalog `--check` và đồng bộ toàn bộ front door.
