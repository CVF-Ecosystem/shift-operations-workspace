# Agent Handoff — 2026-07-22 (P-FIX-6, đóng thật tranche P-FIX)

Provider-neutral handoff. Continues from
[`AGENT_HANDOFF_2026-07-22_PFIX5.md`](AGENT_HANDOFF_2026-07-22_PFIX5.md).
Đây là handoff **sửa lại** tuyên bố "đóng toàn bộ tranche P-FIX" của handoff
trước — tuyên bố đó đã bị một review độc lập **thứ hai** bác bỏ.

- **Mode:** cvf_enforcement_buildout
- **Tranche:** P-FIX-6 (sửa gap governance-bypass mà P-FIX-5 bỏ sót)
- **Startup ack:** mode=cvf_enforcement_buildout; active handoff=this file;
  next allowed move=P2-A/P2-B/P2-C (mở lại, chỉ sau khi mọi closure surface
  đồng bộ đúng P-FIX-6 — đã đồng bộ trong chính commit này); parked
  checkpoint=none.

## Bối cảnh: vì sao handoff P-FIX-5 sai

Handoff trước (`AGENT_HANDOFF_2026-07-22_PFIX5.md`) tuyên bố: "Tranche P-FIX đã
đóng", "102 test pass", "Docs không còn tuyên bố nào bị bản review đó phủ
nhận". Một agent khác (vận hành theo yêu cầu operator) chạy **review độc lập
thứ hai** trên đúng repo đó và tìm ra: `POST /shifts/{shift_id}/close` —
router endpoint đóng ca — **vẫn gọi thẳng `ledger.close_shift(shift_id)` từ
router**, không có `Depends(get_principal)`, không `require_action`, không
audit nào cả. Probe xác nhận:

```
create=200
anonymous_close=200
status=CLOSED
audit_count=0
```

Đây là gap nghiêm trọng vì `ShiftService.freeze` (đã sửa đúng ở P-FIX-1) chỉ
kiểm tra `shift.status == ShiftStatus.CLOSED` — nó **tin** rằng nếu shift đang
ở trạng thái CLOSED thì đã có ai đó hợp lệ đóng nó. Nhưng vì `close_shift` chưa
governed, bất kỳ ai (không cần identity) cũng có thể đưa shift vào trạng thái
CLOSED, và từ đó freeze's `shift_closed` prerequisite bị thỏa mãn một cách âm
thầm, không qua permission, không audit. Đây đúng là loại bypass CVF được
thiết kế để bắt — xảy ra ngay trong chính tranche tuyên bố "đã sửa hết các
bypass đó". Bài học lặp lại với P-FIX-2/P-FIX-3 trước đây: **"đã có test" và
"đã tuyên bố CLOSED" không phải là bằng chứng — phải tự chạy lại probe.**

## P-FIX-6 (tranche này) — đã làm

1. **`packages/cvf-runtime/src/cvf_runtime/permission.py`:** thêm
   `"shift.close": "operator"` vào `_ACTION_MIN_ROLE`. Chọn `operator` (không
   phải `shift_supervisor`) vì đóng ca là hành động vận hành thường quy, cùng
   bậc với `event.create`/`task.create`/`task.transition` (đều `operator`);
   `shift.freeze` — hành động durable/khó đảo ngược (post-freeze chỉ cho phép
   correction record) — mới giữ bậc cao hơn `shift_supervisor`.
2. **`apps/workspace-api/src/workspace_api/application/shift_service.py`:**
   thêm `ShiftService.close(shift_id, principal)` theo đúng khuôn `freeze`:
   `get_shift` → `require_action(principal, "shift.close")` → chặn close một
   shift đã `FROZEN` (`CvfDenied` 409, cùng cách freeze map lỗi trạng thái) →
   `with self.ledger.transaction() as unit:` bọc `close_shift(unit=unit)` +
   `append_audit(..., unit=unit)` atomic. Thêm `_CLOSE_CHAIN = ["identity",
   "permission", "close", "audit"]`.
3. **`apps/workspace-api/src/workspace_api/api/shifts/router.py`:**
   `close_shift` endpoint giờ nhận `principal: Principal = Depends(get_principal)`,
   gọi `ShiftService(ledger).close(shift_id, principal)` thay vì
   `ledger.close_shift(shift_id)` trực tiếp; bắt `CvfDenied` map theo
   `http_status` (401 vô danh qua `get_principal`, 403 role thấp, 409 shift đã
   FROZEN) cộng `KeyError` → 404, đúng khuôn `freeze_shift`.
4. **Đọc lại toàn bộ `InMemoryLedger.close_shift`/`SqlLedger.close_shift`:**
   cả hai đã nhận đúng `unit=` từ trước (không phải bug mới) —
   `InMemoryLedger` mutate dict dưới `self._lock`, được bọc bởi snapshot/
   rollback của `transaction()` ở tầng ngoài; `SqlLedger` dùng
   `self._conn(unit)` đúng cách, tham gia transaction ngoài khi có. Không cần
   sửa gì ở tầng ledger — gap chỉ nằm ở router bỏ qua ShiftService.
5. **Test mới `tests/cvf/test_shift_close_governance.py`** (13 test): 401 close
   vô danh (và shift vẫn OPEN, audit rỗng sau đó), 403 role viewer, 200 +
   audit record đầy đủ field cho principal hợp lệ qua HTTP, rollback atomic
   khi `append_audit` raise (cả `InMemoryLedger` và `SqlLedger` với SQLite
   thật, không mock DB layer), chặn close một shift đã FROZEN (409, cả 2
   backend), chuỗi đầy đủ create → governed close → freeze (qua service lẫn
   qua HTTP thật), và một test hồi quy tái tạo đúng kịch bản review thứ hai:
   close vô danh bị 401 → shift vẫn OPEN → freeze vẫn bị 409 dù dùng principal
   hợp lệ (chứng minh gap đã đóng thật, không chỉ đóng một nửa).
6. **Rà toàn bộ front door:** `docs/implementation/EXECUTION_ROADMAP.md` (mục
   P-FIX chuyển 🔴 IN PROGRESS → 🟢 CLOSED_BOUNDED, thêm mục P-FIX-6, sửa "Exit
   gate P-FIX: ĐẠT" thành có giới hạn rõ ràng), `docs/cvf/CVF_CONTROL_MAPPING.md`
   (thêm dòng `shift.close` vào bảng, sửa dòng `freeze` ghi rõ phụ thuộc vào
   `shift.close` đã governed), `IMPLEMENTATION_STATUS.json` (status đổi thành
   `PHASE_1_2_IN_PROGRESS_PFIX_TRANCHE_CLOSED_BOUNDED`, thêm
   `2026-07-22_pfix6_correction` + `known_remaining_defects` tường minh),
   `docs/catalog/MODULE_REGISTRY.json` (enforcement/tests/next_step của
   `workspace-api` cập nhật), `SESSION/SESSION_MEMORY.md` (thêm đoạn P-FIX-6,
   sửa Next allowed move + Không được làm), `SESSION/ACTIVE_SESSION_STATE.json`
   (active_handoff trỏ file này, next_allowed_move viết lại không còn tuyên
   bố "all Critical/High findings" không giới hạn).
7. **Catalog regenerate:** `python scripts/generate_catalog.py --write` rồi
   `--check` để đồng bộ `docs/catalog/MODULE_REGISTRY.json` metrics +
   `docs/catalog/MODULE_CATALOG.md` với code LOC thật sau khi thêm
   `ShiftService.close` + test file mới (LOC tăng nên metrics cũ sẽ stale nếu
   không regenerate — đây chính là cổng P-FIX-5 dựng lên để bắt việc này).

## Kết quả kiểm chứng

Xem phần "Verification" trong báo cáo đóng tranche (chạy `python -m pytest -q`
và các script closure để lấy số hiện tại — không chép số cũ, đây chính là bài
học P-FIX-5 lặp lại nếu chép). Probe vô danh trước/sau:

- **Trước P-FIX-6:** `POST /shifts/{id}/close` không header → `200 CLOSED`,
  `audit_count=0`.
- **Sau P-FIX-6:** `POST /shifts/{id}/close` không header → `401`, shift vẫn
  `OPEN`, không audit record nào được tạo.

## Bài học quy trình (để không lặp lại lần ba)

1. **Review độc lập định kỳ vẫn có giá trị thật ngay cả sau khi tranche trước
   đã "đóng"** — đặc biệt đúng ngay sau một tranche tự tuyên bố đã sửa hết
   governance bypass. Đó chính là lúc dễ chủ quan nhất.
2. **Một router endpoint gọi thẳng ledger, bỏ qua application service, là
   đúng loại bug P-FIX-1 (freeze) đã từng có và đã sửa — nhưng sửa ở
   `freeze_shift` không tự động sửa `close_shift`.** Khi một domain có nhiều
   action (`close` + `freeze` cho Shift), mỗi action cần được audit riêng cho
   "có đi qua ShiftService/TaskService hay không", không suy diễn từ action
   khác trong cùng router đã được sửa.
3. **Một invariant (`freeze` kiểm `shift_closed`) chỉ mạnh bằng chính điều
   kiện tiên quyết của nó.** Nếu `shift_closed` tự nó không được governed,
   invariant "freeze cross-record thật" (P-FIX-1) không thật — đây là bài học
   kiểm chuỗi phụ thuộc, không chỉ kiểm từng action độc lập.
4. **"CLOSED" là tuyên bố, không phải bằng chứng.** Front-door "P-FIX CLOSED"
   ở P-FIX-5 tự nó không sai về mặt những gì nó liệt kê — 5 finding Critical/
   High liệt kê đều đã sửa đúng — nhưng nó over-claim phạm vi ("Không domain
   nào... còn bypass") vì không có ai kiểm tra lại toàn bộ router surface một
   lần nữa sau khi sửa. Trạng thái đúng phải luôn là "bounded" trừ khi có
   review độc lập xác nhận không còn gap nào khác.

## Next allowed move

Tranche P-FIX (P-FIX-0 → P-FIX-6) đã đóng bounded. Theo `EXECUTION_ROADMAP.md`
Phase 2, mở lại một trong:

- **P2-A (domain còn lại):** nhân bản CVF chain sang customer requests,
  incidents, hoặc handovers — dùng đúng khuôn mẫu `TaskService`/`ShiftService`
  đã sửa (bao gồm `ShiftService.close` mới): `Ledger.transaction()` cho
  atomic audit, kiểm shift cha frozen, persist evidence qua `_evidence.py`
  helper.
- **P2-B:** authentication thật — nên **thay thế** (không chỉ bổ sung)
  `known-principals.yaml` registry check tạm thời. High Finding #4 còn
  nguyên: identity header-based, data minimization chỉ khuyến nghị,
  data_scope/cost/termination chưa có runtime caller, refusal routing/
  recording chưa implement, known-principals chỉ là registry check.
- **P2-C:** frontend UI cho các vertical đã có — giữ đúng
  `FRONTEND_BACKEND_BOUNDARY.md` (governance gate chỉ ở backend).

## Blocked

Xem `blocked_work` trong `ACTIVE_SESSION_STATE.json`. Thêm mới từ P-FIX-6:
không tuyên bố "P-FIX CLOSED" không giới hạn (dùng `CLOSED_BOUNDED`); không
tuyên bố "tất cả High Finding đã sửa" (High Finding #4 còn nguyên các giới hạn
liệt kê ở trên); không tin tuyên bố "CLOSED" của bất kỳ agent nào — kể cả
chính agent viết ra handoff đó — mà không tự chạy lại probe/test trước khi mở
domain mới.
