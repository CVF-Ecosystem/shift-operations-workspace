# Agent Handoff — 2026-07-21

Provider-neutral handoff. Written for whatever agent/human continues next.

- **Mode:** cvf_enforcement_buildout
- **Active state:** [`../ACTIVE_SESSION_STATE.json`](../ACTIVE_SESSION_STATE.json)
- **Startup ack:** mode=cvf_enforcement_buildout; active handoff=this file;
  next allowed move=see below; blocked work=see active state.

## Điểm xuất phát

Đánh giá độc lập (`docs/decisions/EA_INDEPENDENT_REVIEW_2026-07-21.md`) kết luận:
repo là blueprint trung thực nhưng ~5% hiện thực hóa, và **12 CVF required_controls
gần như không được enforce trong code**. Các phiên buildout xử lý lần lượt các
phát hiện của bản này.

## Đã làm (kiểm chứng được)

1. **cvf-runtime** — gói enforce CVF profile, self-contained trong workspace, đọc
   `packages/cvf-application-profile/*.yaml`. Gate cho cả 12 control:
   identity, permission, domain_lock, data_scope, risk, approval, evidence,
   audit, cost, refusal, termination, freeze. `cost`/`termination` là AI-gated.
2. **Hai golden vertical** trong `workspace-api`: Event→confirm
   (`application/services.py`) và Event→correct post-freeze
   (`application/correction_service.py`), dùng chung gate cvf-runtime.
3. **Persistence** — `operations-ledger`: `Ledger` Protocol + `SqlLedger`
   append-only (SQLAlchemy Core trên schema migration có sẵn); `InMemoryLedger`
   cho test/offline; `ledger_factory` chọn backend theo `DATABASE_URL`. Audit +
   correction ghi qua ledger (bền vững).
4. **Security fixes** (EA #3): CORS theo `app_env`; webhook secret fail-closed
   ngoài development.
5. **Catalog** (`docs/catalog/`): `MODULE_REGISTRY.json` machine SoT +
   `MODULE_CATALOG.md` sinh tự động + `scripts/generate_catalog.py`. Cổng chống
   drift gài vào `scripts/testing/validate_repository.py`, `.githooks/pre-commit`,
   `.github/workflows/ci.yml`.
6. **Docs**: 7 stub `docs/cvf/*.md` (mỗi cái 3 dòng) viết đầy đủ;
   `docs/cvf/CVF_CONTROL_MAPPING.md` là bảng 12 control → file/gate/test.
7. **Session governance** (phiên này): front door trung lập `CONTRIBUTING.md` +
   `SESSION/` (state, memory, handoff) + session-state checker.

## Kết quả kiểm chứng

- `python -m pytest -q` → **47 passed**
- `python scripts/testing/validate_repository.py` → PASS (catalog + session check)
- CVF controls: **12/12** có gate + test
- Module status: enforced=1, partial=5, contract-only=6, stub=8

## Next allowed move

Một trong:
- **(a)** DB-backed integration suite cho `SqlLedger` (cần `docker compose up
  postgres`) → đưa operations-ledger partial→enforced.
- **(b)** Wire `ai-gateway`/`ai-providers` gọi các gate data_scope/budget/
  termination → cost/termination hết "AI-gated-only".
- **(c)** Nhân bản CVF chain sang domain mới (Customer Request hoặc Incident).

## Blocked (không làm nếu không có xác nhận mới)

- Tuyên bố SqlLedger production-verified khi chưa test round-trip Postgres thật.
- Tuyên bố cost/termination load-bearing trước khi có AI mode được wire.
- Tạo file điểm-vào theo provider (ví dụ CLAUDE.md chứa nội dung) — front door
  phải trung lập provider (`CONTRIBUTING.md`).
