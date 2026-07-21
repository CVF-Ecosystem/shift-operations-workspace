# Session Memory

Human companion to [`ACTIVE_SESSION_STATE.json`](ACTIVE_SESSION_STATE.json).
Provider-neutral — for every agent and human. Keep it short; details live in the
handoffs.

_Last updated: 2026-07-21_

## Where the project is

Repo bắt đầu là **blueprint trung thực nhưng CVF controls chỉ nằm trên giấy**
(xem `docs/decisions/EA_INDEPENDENT_REVIEW_2026-07-21.md`). Qua các phiên
buildout, CVF controls đã được đưa vào code + test, persistence có backend bền
vững, và có catalog + session governance.

## Trạng thái hiện tại (verify với `git status` / `make validate` trước khi tin)

- **CVF controls:** 12/12 có gate + test trong `packages/cvf-runtime`
  (`cost`/`termination` là **AI-gated** — chạy & test được, load-bearing khi AI
  mode ngoài NO_AI bật). Bản đồ: `docs/cvf/CVF_CONTROL_MAPPING.md`.
- **Golden verticals:** Event→confirm và Event→correct (post-freeze) trong
  `workspace-api`, cùng dùng chung các gate cvf-runtime.
- **Persistence:** `operations-ledger` có `Ledger` Protocol + `SqlLedger`
  append-only; `InMemoryLedger` cho test/offline. Audit + correction ghi qua
  ledger. **Chưa** test round-trip trên Postgres thật.
- **Catalog:** `docs/catalog/MODULE_REGISTRY.json` là machine SoT; `MODULE_CATALOG.md`
  sinh tự động; cổng chống drift trong `make validate`.
- **Tests:** 47 passed.

## Next allowed move

Nguồn thứ tự là [`docs/implementation/EXECUTION_ROADMAP.md`](../docs/implementation/EXECUTION_ROADMAP.md)
— 5 phase + P0, mỗi phase có exit gate. Bước kế tiếp theo dependency: **P1-A**
(SqlLedger Postgres round-trip test → operations-ledger partial→enforced), rồi
**P2-A** (nhân bản CVF chain sang tasks/customer-requests/incidents/handovers).
Không mở Phase 4 (AI) trước khi Phase 2 core + Phase 3 Refinery đạt gate.

## Không được làm (không có xác nhận mới)

Xem `blocked_work` trong `ACTIVE_SESSION_STATE.json`. Cốt lõi: không over-claim
SqlLedger/AI chưa kiểm chứng; **không tạo file điểm-vào theo provider** — front
door là `CONTRIBUTING.md`, trung lập.
