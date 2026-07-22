# Agent Handoff — 2026-07-22 (P-FIX-0)

Provider-neutral handoff. Continues from
[`AGENT_HANDOFF_2026-07-22_P2A.md`](AGENT_HANDOFF_2026-07-22_P2A.md).

- **Mode:** corrective_fix_before_new_domains
- **Tranche:** P-FIX-0 (Execution Roadmap, P-FIX corrective tranche)
- **Startup ack:** mode=corrective_fix_before_new_domains; active
  handoff=this file; next allowed move=P-FIX-1; blocked work=see
  `ACTIVE_SESSION_STATE.json` (do NOT open new domains/phases).

## Bối cảnh — vì sao có tranche P-FIX

Theo yêu cầu operator, một prompt review độc lập được soạn cho Codex
(`docs/decisions/CODEX_REVIEW_REQUEST_2026-07-22.md`) để kiểm chứng lại các
tuyên bố "12/12 enforced", "three golden verticals", "PostgreSQL same code
path" trước khi tiếp tục roadmap. Codex chạy review, thực hiện probe runtime
thật (không chỉ đọc code), và nộp báo cáo tại
`docs/decisions/EA_INDEPENDENT_REVIEW_2026-07-22_CODEX.md`.

**Kết quả: nhiều tuyên bố bị bác bỏ bằng bằng chứng chạy được.** 5 finding
nghiêm trọng (2 Critical, 3 High) và 2 finding trung bình:

1. **Critical — Freeze bypass được.** `freeze_shift` không kiểm identity/
   permission/prerequisite trước khi freeze; sau khi frozen, `EventService`/
   `TaskService` không kiểm shift cha; `SqlLedger` không chặn mutation trên
   record thuộc shift đã frozen trong khi `InMemoryLedger` có chặn — hai
   backend hành xử khác nhau.
2. **Critical — SqlLedger đánh rơi evidence.** `_rows.py` không map cột
   `evidence` cho event. Probe: ghi R2 event kèm evidence, đọc lại còn 0
   evidence, `EventService.confirm` bị evidence gate từ chối chính sự kiện đã
   có đủ evidence lúc ghi.
3. **High — Migration Task thiếu cột `version`.** `tables.py`/`Task` model
   dùng `version`, migration 002 không có cột đó → PostgreSQL insert Task sẽ
   crash thật. Parity test không đủ chặt để bắt (chỉ check tên bảng/FK
   table/có CheckConstraint nào đó, không check cột).
4. **High — Approval là tự khai.** Identity qua header không xác thực;
   approver_id/role trong `Approval` do caller tự gửi trong cùng request.
   Quorum đúng *hình dạng*, không xác thực approver thật.
5. **High — Audit không atomic với mutation.** Event confirm ghi state trước,
   audit sau, trong transaction riêng. Nếu audit fail, mutation đã đứng mà
   không có audit record.
6. **Medium — `generate_catalog.py --check` nông.** Chỉ validate cấu trúc
   registry, không recompute/so sánh metrics hay Markdown — probe âm (sửa
   `code_loc` thành số sai) vẫn PASS.
7. **Medium — Front doors đã drift.** `IMPLEMENTATION_STATUS.json` (25 tests,
   1 vertical), `CVF_CONTROL_MAPPING.md` (nói Task là "future work"),
   `ARCHITECTURE.md` ("chưa bắt đầu build"), `SESSION_MEMORY.md` (51 tests) —
   tất cả đều sai so với thực tế lúc review.

## P-FIX-0 (tranche này) — đã làm

Sửa toàn bộ tuyên bố sai trong docs, **không sửa code hành vi** (đó là
P-FIX-1 trở đi):

- `docs/cvf/CVF_CONTROL_MAPPING.md` — viết lại hoàn toàn theo phân biệt
  **callable** (có gate + unit test) vs **load-bearing** (chặn được vi phạm
  trong request path thật) vs **not verified server-side**. Mỗi control ghi
  rõ giới hạn đã biết, trỏ đúng finding trong bản review Codex.
- `IMPLEMENTATION_STATUS.json` — bỏ số liệu cũ (25 tests, 1 vertical), thêm
  block `cvf_enforcement.2026-07-22_correction` trỏ về bản review, liệt kê rõ
  control nào có known bypass/gap.
- `ARCHITECTURE.md` — sửa đúng 1 dòng ("Chưa bắt đầu build" → mô tả đúng +
  trỏ catalog), không động vào phần baseline khác (giữ đúng "frozen").
- `SESSION/SESSION_MEMORY.md` — viết lại, dẫn thẳng review Codex làm nguồn sự
  thật, liệt kê rõ known issues, sửa "51 tests" cũ.
- `docs/implementation/EXECUTION_ROADMAP.md` — thêm block **P-FIX** (bắt buộc,
  chặn mọi phase khác) với 6 tranche P-FIX-0..5, mỗi cái trỏ đúng finding;
  sửa "Bước kế tiếp duy nhất" bỏ tiền đề sai "same code path".
- `SESSION/ACTIVE_SESSION_STATE.json` — mode đổi thành
  `corrective_fix_before_new_domains`; `blocked_work` thêm 4 mục mới (không
  reuse nhãn enforced/12-12/golden-vertical bừa; không mở domain mới; không
  tin approval tự khai; không coi audit là bảo đảm).

## Kết quả kiểm chứng

- Chưa sửa code hành vi trong tranche này — `pytest` phải vẫn cho cùng kết quả
  như trước review (65 passed), vì P-FIX-0 chỉ sửa docs.
- `python scripts/testing/validate_repository.py` phải PASS sau khi tạo file
  handoff này (session-state check cần `active_handoff` trỏ tới file tồn tại).

## Next allowed move

**P-FIX-1** — sửa freeze thành bất biến xuyên-record thật:
1. `freeze_shift` (router + service) thêm identity/permission check +
   prerequisite (`shift_closed`, `report_approved`, handover linked theo
   `freeze-policy.yaml`).
2. `EventService.confirm`, `CorrectionService.correct_event`,
   `TaskService.transition` phải kiểm shift cha trước khi mutate — nếu shift
   FROZEN thì từ chối (trừ chính correction record, vốn được phép theo thiết
   kế "post-freeze correction record only").
3. `SqlLedger.add_event/put_event/add_task/put_task` phải kiểm shift status
   giống `InMemoryLedger` (hiện SqlLedger không kiểm gì).
4. Test: API + service + cả `InMemoryLedger` lẫn `SqlLedger`, dùng shift cha
   đã frozen làm fixture — xác nhận cả tạo mới lẫn sửa record con đều bị chặn
   ở cả hai backend.

Không mở P2-A domain còn lại (customer requests/incidents/handovers), P2-B,
P2-C hay bất kỳ phase mới nào cho tới khi P-FIX-1 → P-FIX-5 xong.

## Blocked

Xem `blocked_work` trong `ACTIVE_SESSION_STATE.json` — đã mở rộng đáng kể so
với handoff trước, đọc kỹ trước khi hành động.
