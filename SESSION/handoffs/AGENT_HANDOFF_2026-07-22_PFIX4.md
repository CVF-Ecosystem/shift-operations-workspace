# Agent Handoff — 2026-07-22 (P-FIX-4)

Provider-neutral handoff. Continues from
[`AGENT_HANDOFF_2026-07-22_PFIX3.md`](AGENT_HANDOFF_2026-07-22_PFIX3.md).

- **Mode:** corrective_fix_before_new_domains
- **Tranche:** P-FIX-4 (Execution Roadmap P-FIX corrective tranche)
- **Startup ack:** mode=corrective_fix_before_new_domains; active
  handoff=this file; next allowed move=P-FIX-5 (last P-FIX tranche);
  blocked work=see `ACTIVE_SESSION_STATE.json`.

## Việc đã làm — migration Task.version + parity test siết chặt

Sửa **High Finding #3** của bản review Codex: migration
`002_tasks_customers_reports.sql` thiếu cột `version` mà `tables.py`/runtime
luôn ghi — một PostgreSQL thật sẽ crash khi insert Task. Parity test cũ không
đủ chặt để bắt lỗi này (chỉ check tên bảng/FK table/có ≥1 CheckConstraint).

1. Thêm `version integer NOT NULL DEFAULT 1` vào bảng `tasks` trong migration
   002, khớp `tables.py` và bảng `reports` (đã có sẵn `version` cùng dạng).
2. Viết lại `tests/integration/test_schema_parity.py`:
   - `test_column_sets_match_exactly`: parse tên cột từ migration, so **đúng
     bộ** với `tables.py` — đây là test trực tiếp bắt được bug Codex tìm ra.
   - `test_column_nullability_matches`: so nullable từng cột (PK ngầm định
     NOT NULL dù migration không viết tường minh).
   - Giữ nguyên `test_foreign_keys_match_migration` và
     `test_window_checks_present_where_migration_has_them` từ trước.
3. **Phát hiện phụ trong lúc siết:** 4 cột `created_at`/`occurred_at` trong
   `tables.py` (shifts, operational_events, corrections, tasks) thiếu
   `nullable=False` dù migration khai `NOT NULL DEFAULT now()`. Đã sửa.

## Test âm xác nhận cổng có tác dụng thật

Tái tạo chính xác bug cũ: xoá cột `version` khỏi migration →
`test_column_sets_match_exactly` fail đúng với thông báo "tables.py declares
columns the migration does not have: ['version']". Khôi phục → pass lại.

## Giới hạn ghi rõ (không lặp lại over-claim)

Đã thử chạy raw migration SQL lên SQLite: **thất bại ngay** với lỗi cú pháp
(`CREATE EXTENSION` không tồn tại trên SQLite). Migration dùng cú pháp
Postgres-only (`gen_random_uuid()`, custom ENUM, `jsonb`) nên không thể chạy
migration thật để test round-trip trên SQLite. Không có Postgres trong môi
trường này để test round-trip thật. Parity ở mức parse text cột là cách mạnh
nhất khả dụng hiện tại — verify migration-thật vẫn là pre-ship gate khi có
Docker/Postgres (theo đúng "database operating model" mà Codex đề xuất trong
bản review).

## Kết quả kiểm chứng

- `pytest` → **97 passed** (95 trước + 2 test parity mới ròng).
- `validate_repository.py` → PASS.
- File-size: không đổi đáng kể.

## Next allowed move

**P-FIX-5** (tranche P-FIX cuối cùng) — sửa `generate_catalog.py --check`
thật:
1. `--check` hiện chỉ validate cấu trúc registry (module id, path, status
   hợp lệ, dependency tồn tại) — **không** recompute metrics hay so Markdown.
   Probe âm của Codex xác nhận: sửa `code_loc` thành số sai, `--check` vẫn
   PASS.
2. Cần: `--check` phải recompute metrics trong bộ nhớ (giống `--write` làm),
   so với số trong registry hiện tại; render Markdown trong bộ nhớ, so
   byte-for-byte với `MODULE_CATALOG.md` trên đĩa.
3. Thêm test âm cho: metric drift (sửa số tay), Markdown drift (sửa MD tay
   không chạy generator).
4. Rà lại toàn bộ front door một lượt cuối (đã làm phần lớn ở P-FIX-0, nhưng
   kiểm lại sau khi P-FIX-1..4 hoàn tất để không còn mâu thuẫn).

Sau P-FIX-5, toàn bộ tranche P-FIX corrective sẽ đóng — có thể mở lại P2-A
(customer requests/incidents/handovers), P2-B, P2-C.

## Blocked

Xem `blocked_work` trong `ACTIVE_SESSION_STATE.json`.
