# Agent Handoff — 2026-07-22 (P2-A Task)

Provider-neutral handoff. Continues from
[`AGENT_HANDOFF_2026-07-21_P1A.md`](AGENT_HANDOFF_2026-07-21_P1A.md).

- **Mode:** cvf_enforcement_buildout
- **Tranche:** P2-A (Task domain) — Execution Roadmap Phase 2
- **Startup ack:** mode=cvf_enforcement_buildout; active handoff=this file;
  next allowed move=P2-A remaining domains or P2-C (frontend); blocked
  work=see `ACTIVE_SESSION_STATE.json`.

## Việc đã làm — CVF chain nhân bản sang Task domain (golden vertical #3)

Tái dùng **cùng** các gate cvf-runtime như Event/Correction, không fork:

1. `domain/models.py`: `Task` model + `TaskStatus` enum (khớp migration 002).
2. `domain/lifecycle.py`: `assert_task_transition` — máy trạng thái task riêng
   (OPEN/IN_PROGRESS/BLOCKED/CARRY_OVER → ...; DONE/CANCELLED terminal).
3. `operations-ledger`: bảng `tasks` map vào `tables.py` (FK shift + CHECK
   status khớp migration 002); parity test mở rộng đọc cả 2 migration file;
   `add_task/get_task/put_task` vào Protocol + InMemoryLedger + SqlLedger.
   **Refactor:** tách row-mappers ra `_rows.py` để `sql_ledger.py` không vượt
   file-size guard (đã sát warn 300).
4. `application/task_service.py`: `create_task` (permission → domain_lock →
   risk → evidence → approval → audit) và `transition` (permission →
   task-status lifecycle → audit). Permission thêm `task.create`/`task.transition`.
5. `api/tasks/router.py`: `POST /tasks`, `POST /tasks/{id}/transition`; gắn main.py.
6. Tests: `tests/cvf/test_task_vertical.py` (6) + task persistence trên SQLite.

## Kết quả kiểm chứng

- `pytest` → **65 passed** (58 trước + 6 task vertical + 1 task persistence).
- `validate_repository.py` → PASS (catalog + session + file-size).
- catalog: 20 module, 2312 LOC; workspace-api giờ 3 golden vertical.
- API import OK, 14 routes.

## Ghi chú database (theo yêu cầu operator "xử lý tốt DB")

Bảng `tasks` map đúng migration (FK + CHECK), parity test tự động bao nó nên
không tạo độ lệch mới. `_rows.py` giữ mọi row-mapping một chỗ cho từng domain —
khi map thêm customer_requests/reports thì thêm mapper ở đó, sql_ledger.py
không phình.

## Next allowed move

Theo `EXECUTION_ROADMAP.md`: tiếp P2-A domain còn lại (customer requests,
incidents, handovers) cùng khuôn `TaskService`, HOẶC P2-C (frontend UI cho các
vertical đã có backend). Không mở Phase 4 (AI) trước khi Phase 2 core + Phase 3
Refinery đạt gate.

## Blocked

Xem `blocked_work` trong `ACTIVE_SESSION_STATE.json` (không đổi trong tranche
này). Vẫn: PostgreSQL round-trip chưa chạy live; không batch nhiều tranche/commit.
