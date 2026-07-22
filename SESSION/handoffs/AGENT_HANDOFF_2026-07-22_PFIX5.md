# Agent Handoff — 2026-07-22 (P-FIX-5, đóng tranche P-FIX)

Provider-neutral handoff. Continues from
[`AGENT_HANDOFF_2026-07-22_PFIX4.md`](AGENT_HANDOFF_2026-07-22_PFIX4.md).
Đây là handoff **đóng toàn bộ tranche P-FIX**.

- **Mode:** cvf_enforcement_buildout (trở lại bình thường, không còn
  `corrective_fix_before_new_domains`)
- **Tranche:** P-FIX-5 (cuối cùng) — Execution Roadmap P-FIX corrective tranche
- **Startup ack:** mode=cvf_enforcement_buildout; active handoff=this file;
  next allowed move=P2-A/P2-B/P2-C (mở lại); blocked work=xem
  `ACTIVE_SESSION_STATE.json`.

## Bối cảnh toàn bộ tranche P-FIX (tóm tắt 5 phiên)

Operator yêu cầu review độc lập bằng Codex trước khi tiếp roadmap
(`docs/decisions/CODEX_REVIEW_REQUEST_2026-07-22.md`). Kết quả
(`docs/decisions/EA_INDEPENDENT_REVIEW_2026-07-22_CODEX.md`) tìm ra 2 Critical
+ 3 High + 2 Medium finding — nhiều tuyên bố "12/12 enforced"/"golden
vertical" trước đó đã over-claim. Operator yêu cầu "fix toàn bộ" theo đúng
thứ tự Codex đề xuất. 5 tranche đã đóng:

| Tranche | Finding | Kết quả |
|---|---|---|
| P-FIX-0 | (chuẩn bị) | Nắn lại mọi tuyên bố sai trong docs trước khi sửa code |
| P-FIX-1 | Critical #1 | Freeze thành bất biến xuyên-record thật (cả 2 backend) |
| P-FIX-2 | High #5 | Mutation + audit atomic (unit-of-work, cả 2 backend) |
| P-FIX-3 | Critical #2, High #4.1 | Evidence persist qua SqlLedger + approval known-principal check |
| P-FIX-4 | High #3 | Migration Task.version + parity test siết chặt |
| P-FIX-5 | Medium #6, #7 | Catalog `--check` thật + front-door sweep cuối |

## P-FIX-5 (tranche này) — đã làm

1. **`generate_catalog.py --check`** viết lại: `enrich_metrics()` nhận
   `generated_at` tùy chọn để pin về giá trị đã lưu (so sánh đúng số liệu,
   không phải đồng hồ); `--check` giờ recompute metrics + render Markdown
   trong bộ nhớ, so với registry/MD trên đĩa, fail nếu lệch.
2. **`tests/integration/test_catalog_drift_detection.py`** (5 test mới):
   tái tạo đúng 2 probe Codex đã làm (`code_loc=999999`, hand-edit Markdown)
   — cả hai giờ fail đúng; cộng test module-metrics drift + round-trip
   `--write`→`--check` không tự chặn workflow bình thường.
3. **`IMPLEMENTATION_STATUS.json`** viết lại hoàn toàn: bỏ số test cứng (đã
   lỗi thời — ghi "65 passed" trong khi thực tế 97+), bỏ danh sách "known
   bypass" cũ (freeze/audit/evidence/approval đã sửa ở P-FIX-1/2/3), chỉ giữ
   danh sách "still not load-bearing" đúng thực tế hiện tại.
4. **`docs/implementation/EXECUTION_ROADMAP.md`**: tick P-FIX-5, ghi "Exit
   gate P-FIX: ĐẠT" với tóm tắt bằng chứng từng finding.
5. **`SESSION/ACTIVE_SESSION_STATE.json`**: mode trở lại
   `cvf_enforcement_buildout`, `next_allowed_move` mở lại P2-A/P2-B/P2-C,
   `blocked_work` cập nhật thành quy tắc lâu dài (không chỉ ràng buộc tạm
   thời của tranche P-FIX).

## Kết quả kiểm chứng

- **102 test pass** tại thời điểm đóng tranche (chạy `python -m pytest -q`
  để lấy số hiện tại — đừng tin số này mãi, đó chính là bài học P-FIX-5).
- `validate_repository.py` → PASS.
- Test âm xác nhận catalog check có tác dụng thật (5 test, bao gồm tái tạo
  đúng 2 probe của Codex).

## Bài học quy trình (để không lặp lại)

1. **Review độc lập định kỳ có giá trị thật** — không phải thủ tục hình
   thức. Codex tìm ra 5 lỗi nghiêm trọng mà chính tác giả code (tôi) không
   tự phát hiện, vì tôi tin vào chính unit test do mình viết mà không tự hỏi
   "test này có thực sự exercise đường dẫn thật không".
2. **Unit test gọi thẳng gate ≠ test end-to-end.** Nhiều "test pass" trước
   đây chỉ chứng minh hàm gate hoạt động đúng khi gọi trực tiếp với tham số
   đã chuẩn bị sẵn — không chứng minh request thật (HTTP → router → service
   → ledger) đi qua đúng đường đó. Từ nay: mọi golden vertical mới cần ít
   nhất 1 test qua tầng cao nhất có thể (HTTP hoặc service+cả 2 ledger).
3. **"Đã có test" không bằng "đã kiểm chứng đúng thứ cần kiểm chứng."** Ví dụ
   `test_freeze` cũ (trước P-FIX-1) test đúng cú pháp nhưng test nhầm đối
   tượng (freeze event thay vì freeze shift cha).
4. **Ghi số liệu cứng vào front door là nợ kỹ thuật.** Mọi chỗ từng ghi "65
   passed"/"8 controls enforced" đều lỗi thời trong vòng 1-2 tranche. Từ nay
   front door trỏ lệnh để chạy, không ghi số.

## Next allowed move

Tranche P-FIX đã đóng. Theo `EXECUTION_ROADMAP.md` Phase 2, mở lại một trong:

- **P2-A (domain còn lại):** nhân bản CVF chain sang customer requests,
  incidents, hoặc handovers — dùng đúng khuôn mẫu `TaskService`/`ShiftService`
  đã sửa: `Ledger.transaction()` cho atomic audit, kiểm shift cha frozen,
  persist evidence qua `_evidence.py` helper.
- **P2-B:** authentication thật — nên **thay thế** (không chỉ bổ sung)
  `known-principals.yaml` registry check tạm thời.
- **P2-C:** frontend UI cho các vertical đã có — giữ đúng
  `FRONTEND_BACKEND_BOUNDARY.md` (governance gate chỉ ở backend).

## Blocked

Xem `blocked_work` trong `ACTIVE_SESSION_STATE.json` — giờ là quy tắc lâu dài,
không chỉ ràng buộc tạm thời của tranche P-FIX.
