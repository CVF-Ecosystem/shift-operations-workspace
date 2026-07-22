# Agent Handoff — 2026-07-22 (P-FIX-3)

Provider-neutral handoff. Continues from
[`AGENT_HANDOFF_2026-07-22_PFIX2.md`](AGENT_HANDOFF_2026-07-22_PFIX2.md).

- **Mode:** corrective_fix_before_new_domains
- **Tranche:** P-FIX-3 (Execution Roadmap P-FIX corrective tranche)
- **Startup ack:** mode=corrective_fix_before_new_domains; active
  handoff=this file; next allowed move=P-FIX-4; blocked work=see
  `ACTIVE_SESSION_STATE.json`.

## Việc đã làm — evidence persistence + approval known-principal check

Sửa **Critical Finding #2** và **High Finding #4.1** của bản review Codex.

### Evidence (Critical #2)

- Bảng `evidence_links` (đã có trong migration 001, chưa được đọc/ghi) map
  vào `tables.py`.
- `_evidence.py` (mới): helper dùng chung `insert_evidence`/`evidence_for` cho
  cả event và task — tách ra khỏi `sql_ledger.py` để giữ file dưới ngưỡng
  file-size guard (đã chạm 326/400 dòng lúc thêm logic evidence trực tiếp).
- `SqlLedger.add_event`/`add_task`: ghi evidence 1 lần lúc tạo (append-only,
  không rewrite khi confirm/correct/transition).
- `SqlLedger.get_event`/`get_task`: đọc lại evidence đúng.
- `TaskInput`/`api/tasks/router.py`: thêm field `evidence` — trước đây
  Pydantic bỏ field lạ, request HTTP luôn gửi evidence rỗng dù client gửi kèm.

### Approval (High #4.1)

- `known-principals.yaml` (mới, trong `cvf-application-profile`): registry
  principal đã biết → role thật.
- `CvfProfile.known_role_for` (policy_loader.py): tra registry.
- `assert_approval_satisfied`/`_find_seat`: mỗi seat quorum giờ phải khớp một
  principal có trong registry **và** role đăng ký đủ thẩm quyền cho seat đó —
  không còn chấp nhận approver_id bịa hoàn toàn, không còn chấp nhận approver
  thật tự khai role cao hơn thực tế.

**Giới hạn ghi rõ:** đây KHÔNG phải xác thực thật — không chữ ký, không
token, không session. Chỉ chặn được việc bịa hoàn toàn hoặc tự nâng role.
Khi P2-B (auth thật) triển khai, registry này nên bị thay thế, không chỉ bổ
sung.

## Kết quả kiểm chứng

- **8 test mới**: `tests/integration/test_evidence_persistence.py` (4),
  `tests/cvf/test_approval_known_principals.py` (4).
- **2 HTTP probe reproduce đúng kịch bản Codex đã mô tả:**
  - Trước: R2 event ghi evidence qua SqlLedger, đọc lại 0 evidence, confirm bị
    từ chối sai. Sau: `test_r2_event_confirm_succeeds_on_sql_ledger_with_evidence`
    + probe thủ công xác nhận confirm thành công.
  - Trước: 2 approver bịa hoàn toàn confirm được R3 event, trả `200`. Sau:
    probe thủ công xác nhận trả `409` với lý do rõ ràng; approver thật trong
    registry vẫn `200`.
- `pytest` → **95 passed** (87 trước + 8 mới).
- File-size: `sql_ledger.py` từng chạm warn (326/400) khi thêm evidence trực
  tiếp; tách `_evidence.py` đưa về 293 dòng, PASS sạch (không warn).
- `validate_repository.py` → PASS (catalog + session + file-size).

## Next allowed move

**P-FIX-4** — sửa migration Task.version + siết parity test:
1. Thêm cột `version integer NOT NULL DEFAULT 1` vào bảng `tasks` trong
   `database/migrations/002_tasks_customers_reports.sql` (migration là schema
   authority; `tables.py`/runtime đã dùng `version` từ P2-A nhưng migration
   thiếu cột này — PostgreSQL thật sẽ crash khi insert Task).
2. Siết `tests/integration/test_schema_parity.py`: so sánh cột/type/
   nullable/default/PK/FK source-target/CHECK expression thật, không chỉ "tên
   bảng tồn tại" hay "có ít nhất 1 CheckConstraint nào đó" như hiện tại.
3. Test SqlLedger trên schema do **chính migration tạo** (chạy file `.sql`
   thật lên SQLite/Postgres), không chỉ `metadata.create_all()` (hiện tại
   test dùng `metadata.create_all` nên không phát hiện migration thiếu cột).

Không mở P2-A domain còn lại, P2-B, P2-C, hay bất kỳ phase mới nào cho tới khi
P-FIX-4 và P-FIX-5 xong.

## Blocked

Xem `blocked_work` trong `ACTIVE_SESSION_STATE.json`.
