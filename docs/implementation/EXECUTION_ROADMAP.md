# Execution Roadmap

Roadmap thực thi có thứ tự, đặt trên 5 phase gốc
([`IMPLEMENTATION_PHASES.md`](IMPLEMENTATION_PHASES.md)). Đây là **nguồn thứ tự
duy nhất**: mọi phiên làm việc quy chiếu về roadmap này thay vì quyết định rời
rạc. Bước kế tiếp luôn khớp `next_allowed_move` trong
`SESSION/ACTIVE_SESSION_STATE.json`.

Dependency order (khóa, từ `DEPENDENCY_ORDER.md`):
contracts → domain → ledger → core workspace → CVF profile/Refinery → AI →
channels → reporting → hardening → freeze.

## Ghi chú thứ tự (quan trọng — vì sao trạng thái không tuần tự)

Bản EA review (`docs/decisions/EA_INDEPENDENT_REVIEW_2026-07-21.md`) chỉ ra CVF
controls là điểm yếu nhất. Vì vậy công việc đã **chủ động làm trước một phần
Phase 3 (CVF governance)** để dựng cái xương sống governance, trước khi Phase 2
(core operations) hoàn tất. Roadmap dưới đây ghi đúng sự thật đó thay vì giả vờ
tuần tự. Nền tảng ngang (catalog, session governance, boundary) là **P0** — hạ
tầng chung không thuộc phase nghiệp vụ nào.

---

## P0 — Governance foundation (ngang, phục vụ mọi phase) — ✅ DONE

Không thuộc 5 phase nghiệp vụ; là hạ tầng để mọi phase kiểm chứng được.

- [x] `cvf-runtime`: 12/12 CVF control có gate + test (`packages/cvf-runtime`).
- [x] Catalog: `docs/catalog/MODULE_REGISTRY.json` + generator + cổng chống drift.
- [x] Session governance: `CONTRIBUTING.md` front door + `SESSION/` + checker.
- [x] Boundary: `docs/architecture/FRONTEND_BACKEND_BOUNDARY.md`.
- [x] Security quick wins: CORS theo env, webhook fail-closed.
- [x] File size guard (GC-023 style): `scripts/check_file_size.py` + registry +
      `docs/reference/FILE_SIZE_GUARD.md`, gài vào validate/hook/CI.

**Exit gate:** `make validate` PASS (catalog + session + file-size) + 47 test. ✅

---

## Phase 1 — Foundation and Contracts — 🟡 IN PROGRESS

Gate gốc: tạo được một shift record hoàn chỉnh không cần LLM; schemas valid;
lifecycle/freeze rõ ràng.

- [x] Domain lifecycle + data states (`domain/lifecycle.py`, `domain/models.py`).
- [x] JSON Schemas (`packages/workspace-contracts`, contract test pass).
- [x] CVF risk/approval/evidence models (enforced trong cvf-runtime).
- [x] Ledger Protocol + append-only SqlLedger (`operations-ledger`).
- [ ] **P1-A:** DB-backed integration test cho SqlLedger (round-trip Postgres
      thật) → đưa `operations-ledger` từ `partial` lên `enforced`.
- [ ] **P1-B:** Tách domain models ra `operations-domain` (hiện nằm inline trong
      workspace-api) → `operations-domain` stub→partial.

**Exit gate:** shift record đầy đủ tạo/confirm/freeze được, có test; SqlLedger
round-trip Postgres pass; contract test pass.

---

## Phase 2 — Core Operations Workspace — 🟡 IN PROGRESS

Gate gốc: hoàn thành một ca 12 giờ start→freeze khi AI và external channels tắt.

- [x] Events: create + confirm chain (golden vertical #1).
- [x] Corrections: post-freeze correction (golden vertical #2).
- [x] Audit ghi bền vững qua ledger.
- [ ] **P2-A:** Nhân bản CVF chain sang các domain còn lại: tasks, customer
      requests, incidents, handovers (mỗi cái 1 router + service dùng chung gate).
- [ ] **P2-B:** Authentication thật (thay header-based principal bằng
      JWT/session) — nâng identity control.
- [ ] **P2-C:** Frontend UI cho các vertical đã có backend (bắt đầu Events/
      Open Work), tuân thủ boundary: FE gọi API, không tự enforce.
- [ ] **P2-D:** PWA offline queue + realtime.

**Exit gate:** chạy trọn một ca (start→updates→tasks→handover→report→freeze) qua
API với AI/channel tắt, mọi record truy vết được.

---

## Phase 3 — CVF Governance and Refinery — 🟡 PARTIAL (làm trước có chủ đích)

Gate gốc: protected actions đi qua policy, R3/R4 không bypass, Refinery lỗi có
fallback.

- [x] CVF Application Profile enforce đầy đủ (12/12 control trong cvf-runtime).
- [x] domain_lock, data_scope, cost, termination có gate + test.
- [x] R3/R4 approval quorum không bypass (test chứng minh).
- [ ] **P3-A:** Refinery boundary thật (`refinery-bridge`): normalize, dedupe,
      redact, classify, context candidates + fallback khi lỗi.
- [ ] **P3-B:** Wire các gate data_scope/cost/termination vào một điểm gọi thật
      (khi Phase 4 AI bật) — hết trạng thái "AI-gated only".

**Exit gate:** protected action đi qua policy; Refinery lỗi có fallback về
rules; R3/R4 không bypass được.

---

## Phase 4 — AI and Channel Capabilities — ⬜ NOT STARTED

Gate gốc: thay provider/channel không sửa core; invalid schema bị reject;
external prompt injection không vượt trust boundary.

- [ ] **P4-A:** AI Gateway (`ai-gateway`): model router, context builder,
      structured output, budget, fallback, kill switch — gọi cvf-runtime gates.
- [ ] **P4-B:** AI providers (`ai-providers`): NO_AI, RULES_ONLY, mock trước.
- [ ] **P4-C:** Integration Edge đầy đủ: raw_payload, quarantine, rate_limit,
      routing, outbound (hiện chỉ có webhook verify + dedup).
- [ ] **P4-D:** Channel adapters: generic webhook + mock Zalo/WhatsApp.
- [ ] **P4-E:** Identity mapping + conversation routing.

**Exit gate:** thay provider không sửa core; invalid schema reject; prompt
injection từ channel không vượt trust boundary.

---

## Phase 5 — Reporting, Hardening and Freeze — ⬜ NOT STARTED

Gate gốc: evidence traceability, outage drills, backup restore, owner review.

- [ ] **P5-A:** Reporting engine: report draft từ confirmed records, PDF/Excel.
- [ ] **P5-B:** Dashboard, search, observability.
- [ ] **P5-C:** Backup/restore, resilience drills, security review, performance.
- [ ] **P5-D:** Deployment profiles, runbook, Shadow Mode pilot, release freeze.

**Exit gate:** evidence traceability đạt; outage drill + backup restore pass;
owner review approve.

---

## Bước kế tiếp duy nhất (khớp session state)

Xem `next_allowed_move` trong `SESSION/ACTIVE_SESSION_STATE.json`. Thứ tự đề
xuất theo dependency: **P1-A** (SqlLedger Postgres round-trip) trước, vì ledger
là nền của mọi phase sau; rồi **P2-A** (nhân bản chain sang domain còn lại) để
Phase 2 tiến. Không mở Phase 4 (AI) trước khi Phase 2 core + Phase 3 Refinery
đạt gate.

## Cách dùng roadmap này

1. Mỗi phiên: đọc mục có `IN PROGRESS`, lấy item `[ ]` đầu tiên theo thứ tự.
2. Làm xong: tick `[x]`, cập nhật catalog + session state, chạy `make validate`.
3. Không nhảy phase khi exit gate của phase trước chưa đạt (ACCEPTANCE_GATES).
