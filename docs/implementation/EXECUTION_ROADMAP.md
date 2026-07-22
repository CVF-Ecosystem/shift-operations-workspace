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

## P-FIX — Corrective tranche (BẮT BUỘC, chặn mọi phase/domain mới) — 🔴 IN PROGRESS

**2026-07-22:** review độc lập thứ hai
([`EA_INDEPENDENT_REVIEW_2026-07-22_CODEX.md`](../decisions/EA_INDEPENDENT_REVIEW_2026-07-22_CODEX.md))
chứng minh bằng probe chạy thật rằng nhiều tuyên bố "enforced"/"golden
vertical"/"12/12" trong P0-P2 đã **over-claim**. Không mở P2-A (domain còn
lại), P2-B, P2-C, hay bất kỳ phase mới nào cho tới khi toàn bộ P-FIX-0 →
P-FIX-5 xong và có test end-to-end xác nhận (không chỉ unit test gọi trực
tiếp gate).

- [x] **P-FIX-0:** Nắn lại tuyên bố sai trong `docs/cvf/CVF_CONTROL_MAPPING.md`,
      `IMPLEMENTATION_STATUS.json`, `ARCHITECTURE.md` (dòng trạng thái),
      `SESSION/SESSION_MEMORY.md`, roadmap này — dùng đúng phân biệt
      callable/load-bearing/not-verified-server-side thay vì "enforced" gộp
      chung.
- [x] **P-FIX-1 (Critical #1):** Freeze thành bất biến xuyên-record thật.
      `ShiftService.freeze` (mới) enforce identity/permission + `shift_closed`
      thật (`close_shift` thêm vào Ledger Protocol/cả 2 backend); `report_approved`/
      `open_handover_items_linked` chưa có model (Phase 5/P2-D) nên dùng override
      tường minh bắt buộc kèm lý do, ghi 2 audit record riêng (freeze +
      override) — không giả vờ đã kiểm. Sau khi frozen: `InMemoryLedger`/
      `SqlLedger` chặn `add_event/put_event/add_task/put_task` khi shift cha
      FROZEN; `CorrectionService` dùng `allow_when_frozen=True` (đường mutation
      hợp lệ duy nhất sau freeze). HTTP probe xác nhận: trước fix
      `POST /shifts/{id}/freeze` trả `200 FROZEN` vô điều kiện; sau fix trả
      `409` cho tới khi close + override. Test: `tests/cvf/test_freeze_invariant.py`
      (12 test, tham số hoá cả `InMemoryLedger` và `SqlLedger`).
- [x] **P-FIX-2 (High #5):** Mutation + audit atomic. `Ledger.transaction()`
      (unit-of-work) thêm vào Protocol + cả 2 backend: `SqlLedger` dùng
      transaction SQL thật (mọi mutation method nhận `unit=` connection tùy
      chọn); `InMemoryLedger` snapshot/rollback bằng `copy.deepcopy`. Cả 4
      service (`EventService.confirm`, `CorrectionService.correct_event`,
      `TaskService.create_task`/`transition`, `ShiftService.freeze`) giờ bọc
      state-change + audit-append (+ correction-insert) trong một
      `transaction()`. Test: `tests/cvf/test_atomic_mutation_audit.py` (10
      test, failure-injection `append_audit` raise, cả 2 backend × 4 service).
      **Bug thật tìm thấy trong lúc viết test:** `InMemoryLedger.get_event/
      get_task/get_shift` trả reference sống thay vì bản sao — service mutate
      object trước khi vào transaction khiến rollback vô nghĩa; sửa bằng
      `model_copy()`.
- [ ] **P-FIX-3 (Critical #2, High #4.1):** Lưu evidence qua SqlLedger (map
      `evidence_links`, đọc lại đúng) + thêm field evidence vào `TaskInput`/
      router; xác thực approval server-side (không chấp nhận approver_id/role
      do caller tự khai trong cùng request — cần nguồn xác thực độc lập, ít
      nhất một registry role đã biết, tối thiểu chặn approver trùng với
      identity chưa xác thực). P2-B (auth thật) có thể cần đi cùng bước này.
- [ ] **P-FIX-4 (High #3):** Thêm cột `version` vào migration
      `002_tasks_customers_reports.sql` cho bảng `tasks` (khớp những gì runtime
      luôn ghi). Siết `test_schema_parity.py`: so sánh cột/type/nullable/
      default/PK/FK source-target/CHECK expression thật, không chỉ "tên bảng
      tồn tại" hay "có ít nhất 1 CheckConstraint nào đó". Test SqlLedger trên
      schema do chính migration tạo (không chỉ `metadata.create_all`).
- [ ] **P-FIX-5 (Medium #6, #7):** `generate_catalog.py --check` phải recompute
      metrics trong bộ nhớ, so với registry, render Markdown trong bộ nhớ và
      so byte-for-byte với `MODULE_CATALOG.md` — hiện chỉ validate cấu trúc.
      Thêm test âm cho metric drift + Markdown drift. Rà lại mọi front door
      một lượt cuối để không còn số liệu/tuyên bố mâu thuẫn nhau.

**Exit gate P-FIX:** mọi Critical/High trong bản review 07-22 có test end-to-end
chứng minh đã sửa (không phải unit test gọi thẳng gate); `pytest` pass; docs
không còn tuyên bố nào bị bản review đó phủ nhận.

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
- [x] **P1-A':** SqlLedger dual-backend (SQLite dev/eval + PostgreSQL prod, cùng
      schema qua `Uuid`/`JSON.with_variant(JSONB)`) + integration test round-trip
      thật trên SQLite (create/reconnect/read, append-only corrections, audit
      persist, freeze persist) → `operations-ledger` `partial` → `enforced`.
      **Còn treo:** chạy cùng suite trên PostgreSQL thật (môi trường này không
      có Docker daemon khả dụng) — xem `next_step` của module trong
      `MODULE_REGISTRY.json`.
- [x] **P1-A2:** Schema integrity hardening — phát hiện `tables.py` lệch với
      migration (thiếu FK/CHECK) và SQLite tắt FK mặc định. Thêm FK
      (event→shifts) + CHECK (time-window) khớp migration; `make_engine()` bật
      `PRAGMA foreign_keys=ON` cho SQLite; test chứng minh FK/CHECK chặn thật
      trên DB; parity test chống lệch `tables.py`↔migration tương lai (có test
      âm). Giữ SQLite và PostgreSQL enforce integrity giống nhau.
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
- [x] **P2-A (Task):** Nhân bản CVF chain sang Task domain — Task model +
      TaskStatus lifecycle, bảng `tasks` map vào tables.py (FK+CHECK khớp
      migration 002, parity test mở rộng), ledger methods (Protocol/InMemory/Sql,
      `_rows.py` tách ra để giữ file-size), `TaskService` (create qua
      permission/domain_lock/risk/evidence/approval/audit; transition qua
      permission + task-status lifecycle + audit), router `/tasks`, tests
      (vertical + SQLite persistence). Tái dùng gate cvf-runtime, không fork.
- [ ] **P2-A (còn lại):** Nhân bản tiếp sang customer requests, incidents,
      handovers cùng khuôn mẫu.
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

Xem `next_allowed_move` trong `SESSION/ACTIVE_SESSION_STATE.json`. **2026-07-22:**
review độc lập Codex tìm ra P2-A (Task) và các vertical trước đó over-claim
("golden vertical durable" không đúng qua HTTP+SqlLedger; freeze bypass được).
Bước kế tiếp bắt buộc là **P-FIX-1** (freeze thành bất biến thật), rồi
P-FIX-2 → P-FIX-5 theo thứ tự. **Không** mở P2-A (customer requests/incidents/
handovers) hay bất kỳ phase mới nào cho tới khi P-FIX xong. Xem tiền đề
"PostgreSQL same code path" đã bị bác bỏ (migration Task thiếu cột `version`)
— sửa ở P-FIX-4 trước khi nói lại câu đó.

## Cách dùng roadmap này

1. Mỗi phiên: đọc mục có `IN PROGRESS`, lấy item `[ ]` đầu tiên theo thứ tự.
2. Làm xong: tick `[x]`, cập nhật catalog + session state, chạy `make validate`.
3. Không nhảy phase khi exit gate của phase trước chưa đạt (ACCEPTANCE_GATES).
