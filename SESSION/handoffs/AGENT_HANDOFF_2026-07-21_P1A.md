# Agent Handoff — 2026-07-21 (P1-A')

Provider-neutral handoff. Continues from
[`AGENT_HANDOFF_2026-07-21.md`](AGENT_HANDOFF_2026-07-21.md).

- **Mode:** cvf_enforcement_buildout
- **Tranche:** P1-A' (Execution Roadmap Phase 1)
- **Startup ack:** mode=cvf_enforcement_buildout; active handoff=this file;
  next allowed move=P2-A; blocked work=see `ACTIVE_SESSION_STATE.json`.

## Việc đã làm

`docs/implementation/EXECUTION_ROADMAP.md` P1-A ban đầu yêu cầu "DB-backed
integration test cho SqlLedger (round-trip Postgres thật)". Docker Desktop
không khả dụng trong môi trường này (service Stopped, không start được từ
CLI/không đủ quyền) — không thể dựng Postgres thật. Sau trao đổi với operator,
phạm vi được đổi thành **P1-A'**: làm `SqlLedger` **dual-backend** (SQLite cho
dev/eval không cần setup, PostgreSQL cho production), verify thật trên SQLite.

1. `packages/operations-ledger/src/operations_ledger/tables.py`: thay
   `sqlalchemy.dialects.postgresql.UUID` bằng `sqlalchemy.Uuid` (generic, native
   trên Postgres / CHAR(32) trên SQLite); thay `JSONB` trần bằng
   `JSON().with_variant(JSONB(), "postgresql")`. Một định nghĩa bảng, hai
   backend, không rẽ nhánh code thủ công.
2. `sql_ledger.py`: cập nhật docstring cho đúng dual-backend (logic không đổi —
   `Uuid`/`JSON` generic tự xử lý qua SQLAlchemy).
3. `tests/integration/test_sql_ledger_sqlite.py` (mới, 4 test): round-trip thật
   qua file SQLite trên đĩa, đóng/mở lại kết nối (mô phỏng restart process) —
   shift+event persist, correction append-only (2 correction không ghi đè
   nhau), audit record persist, freeze persist.

## Kết quả kiểm chứng

- `python -m pytest -q` → **51 passed** (47 trước + 4 mới).
- `python scripts/testing/validate_repository.py` → PASS (catalog + session +
  file-size).
- `python scripts/generate_catalog.py --write` → 20 module, 1961 LOC,
  **operations-ledger: partial → enforced**.

## Ranh giới trung thực (không over-claim)

- **Đã verify:** round-trip thật trên SQLite — tạo bảng, ghi, đóng kết nối, mở
  lại, đọc đúng dữ liệu. Đây là bằng chứng thật, không phải test giả.
- **Chưa verify:** cùng suite chạy trên PostgreSQL thật. Code path giống hệt
  (cùng `tables.py`, cùng `SqlLedger`), nhưng **chưa được chạy live** vì môi
  trường không có Docker daemon. Ghi rõ trong `blocked_work` của session state
  để không ai tuyên bố "production-verified" khi chưa đúng.

## P1-A2 (tiếp theo, cùng phiên): schema integrity hardening

Rà lại phần database (theo yêu cầu operator "xử lý tốt, không để rắc rối về
sau") phát hiện 2 vấn đề thật:

1. `tables.py` **lệch** với migration `001_foundation.sql`: thiếu FK
   (`event.shift_id → shifts`) và CHECK (time-window). Migration là schema
   authority nhưng SQLAlchemy backend không enforce cùng ràng buộc.
2. SQLite **tắt foreign-key mặc định** — FK định nghĩa trong tables.py bị bỏ
   qua trên SQLite (Postgres thì enforce) → hai backend hành xử khác nhau.

Đã sửa:
- Thêm FK + CHECK vào `tables.py` khớp migration.
- `make_engine()` (factory mới) bật `PRAGMA foreign_keys=ON` cho SQLite ngay
  lúc tạo engine (trước khi pool giữ connection), dùng nhất quán ở mọi nơi.
- `tests/integration/test_sql_ledger_integrity.py`: chứng minh FK chặn event
  với shift_id ma, CHECK chặn time-window đảo — ở tầng DB, không phải app.
- `tests/integration/test_schema_parity.py`: cổng chống lệch tương lai (FK/CHECK
  trong migration phải có trong tables.py); có test âm xác nhận cổng chặn thật.

Verify: **58 passed**, validate PASS. SQLite và PostgreSQL giờ enforce integrity
giống nhau.

## Next allowed move

**P2-A** — nhân bản CVF chain (identity/permission/risk/approval/evidence/audit)
sang một domain khác (tasks, customer-requests, incidents, hoặc handovers),
tái dùng gate cvf-runtime giống cách `EventService`/`CorrectionService` đã làm.
Không mở Phase 4 (AI) trước khi Phase 2 core + Phase 3 Refinery đạt gate.

## Blocked (không làm nếu không có xác nhận mới)

Xem `blocked_work` trong `ACTIVE_SESSION_STATE.json`. Thêm mới trong tranche
này: không tuyên bố SqlLedger production-verified trên PostgreSQL cho tới khi
suite này (hoặc tương đương) chạy thật trên một Postgres instance thật.
