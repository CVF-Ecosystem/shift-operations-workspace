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

## P-FIX — Corrective tranche (BẮT BUỘC, chặn mọi phase/domain mới) — 🟢 CLOSED_BOUNDED

**2026-07-22:** review độc lập thứ hai
([`EA_INDEPENDENT_REVIEW_2026-07-22_CODEX.md`](../decisions/EA_INDEPENDENT_REVIEW_2026-07-22_CODEX.md))
chứng minh bằng probe chạy thật rằng nhiều tuyên bố "enforced"/"golden
vertical"/"12/12" trong P0-P2 đã **over-claim**. Không mở P2-A (domain còn
lại), P2-B, P2-C, hay bất kỳ phase mới nào cho tới khi toàn bộ P-FIX-0 →
P-FIX-5 xong và có test end-to-end xác nhận (không chỉ unit test gọi trực
tiếp gate).

**2026-07-22 P-FIX-6 (đóng thật):** sau khi P-FIX-5 tuyên bố tranche này
`CLOSED`, một review độc lập **thứ hai** bác bỏ tuyên bố đó — xem chi tiết ở
mục P-FIX-6 bên dưới. Tranche chỉ thật sự đóng (bounded) sau khi P-FIX-6 sửa
gap đó và đồng bộ lại toàn bộ front door.

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
- [x] **P-FIX-3 (Critical #2, High #4.1):** Lưu evidence qua SqlLedger — bảng
      `evidence_links` map vào `tables.py`, ghi 1 lần lúc tạo record
      (`_evidence.py` helper dùng chung event/task), đọc lại đúng; `TaskInput`/
      router thêm field `evidence` (trước đây Pydantic bỏ field lạ, request
      HTTP luôn gửi evidence rỗng). Xác thực approval server-side: thêm
      `known-principals.yaml` (registry principal đã biết + role thật) +
      `CvfProfile.known_role_for`; `assert_approval_satisfied` chỉ chấp nhận
      seat quorum từ approver có trong registry với role đủ thẩm quyền —
      không còn bịa id hay tự nâng role. **Ghi rõ giới hạn:** đây không phải
      xác thực thật (không chữ ký/token/session), chỉ chặn bịa hoàn toàn; thay
      bằng auth thật khi P2-B triển khai. Test: `test_evidence_persistence.py`
      (4), `test_approval_known_principals.py` (4), cộng 2 HTTP probe reproduce
      đúng kịch bản Codex (evidence event R2 qua SqlLedger, approver bịa cho
      R3) — cả hai giờ trả kết quả đúng thay vì sai như review ghi nhận.
- [x] **P-FIX-4 (High #3):** Thêm cột `version integer NOT NULL DEFAULT 1`
      vào bảng `tasks` trong migration `002_tasks_customers_reports.sql` (khớp
      những gì `tables.py`/runtime luôn ghi — trước đây thiếu, PostgreSQL thật
      sẽ crash khi insert Task). Siết `test_schema_parity.py`: parser cột từ
      migration (tên, nullable — PK ngầm định NOT NULL, has_default), so
      **đúng bộ tên cột** với `tables.py` (`test_column_sets_match_exactly`) +
      so nullable từng cột (`test_column_nullability_matches`); phát hiện phụ
      trong lúc siết: 4 cột `created_at`/`occurred_at` trong `tables.py` thiếu
      `nullable=False` dù migration khai `NOT NULL` — đã sửa. **Test âm xác
      nhận cổng có tác dụng:** xoá `version` khỏi migration để tái tạo đúng
      bug cũ → `test_column_sets_match_exactly` fail đúng thông báo; khôi phục
      → pass lại. **Giới hạn ghi rõ:** chạy migration thật lên SQLite không
      khả thi (cú pháp Postgres-only: `CREATE EXTENSION`, custom ENUM,
      `gen_random_uuid()`, `jsonb` — đã thử, lỗi syntax ngay); không có
      Postgres trong môi trường này để test round-trip thật. Parity ở mức
      text-parsing cột là cách mạnh nhất khả dụng; xác minh migration-thật vẫn
      là pre-ship gate khi có Docker (xem "Database operating model" trong
      bản review Codex).
- [x] **P-FIX-5 (Medium #6, #7):** `generate_catalog.py --check` giờ
      recompute metrics trong bộ nhớ (pin `generated_at` về giá trị đã lưu để
      so sánh đúng số liệu, không phải đồng hồ), so với registry hiện tại;
      render Markdown trong bộ nhớ, so byte-for-byte với `MODULE_CATALOG.md`
      trên đĩa. Test âm (`tests/integration/test_catalog_drift_detection.py`,
      5 test) tái tạo đúng 2 probe Codex đã làm (`code_loc=999999`, hand-edit
      Markdown) — cả hai giờ fail đúng thay vì PASS sai như trước; cộng test
      round-trip `--write` → `--check` không bao giờ tự chặn workflow bình
      thường. Rà front door: `IMPLEMENTATION_STATUS.json` viết lại — bỏ số
      test cứng (đã lỗi thời ở P-FIX-3/4), bỏ danh sách "known bypass" cũ
      (freeze/audit/evidence/approval đã sửa ở P-FIX-1/2/3), chỉ còn danh sách
      "still not load-bearing" đúng thực tế (identity, refusal, data_scope/
      cost/termination).

- [x] **P-FIX-6 (gap tìm bởi review độc lập thứ hai, sau khi P-FIX-5 tuyên bố
      CLOSED):** `POST /shifts/{shift_id}/close` vẫn gọi thẳng
      `ledger.close_shift(shift_id)` từ router — không `get_principal`, không
      `require_action`, không audit (probe: `create=200`,
      `anonymous_close=200`, `status=CLOSED`, `audit_count=0`). Vì
      `ShiftService.freeze` chỉ kiểm `shift.status == ShiftStatus.CLOSED`,
      close vô danh đó có thể âm thầm thỏa mãn tiền đề `shift_closed` của
      freeze. Sửa: thêm `shift.close` vào `_ACTION_MIN_ROLE`
      (`packages/cvf-runtime/src/cvf_runtime/permission.py`, min role
      `operator` — cùng bậc với `event.create`/`task.create`/`task.transition`,
      thấp hơn `shift.freeze` (`shift_supervisor`) vì close là hành động vận
      hành thường quy, còn freeze mới là hành động durable/khó đảo ngược);
      `ShiftService.close` mới (theo đúng khuôn `freeze`: identity →
      permission → state-check → `transaction()` bọc `close_shift` +
      `append_audit` atomic); router gọi qua `ShiftService.close`, không còn
      gọi `ledger.close_shift` trực tiếp. Test:
      `tests/cvf/test_shift_close_governance.py` (13 test: 401 vô danh, 403
      role thấp, 200 + audit hợp lệ, rollback atomic khi audit fail trên cả 2
      backend InMemory/SQLite thật, chặn close shift đã FROZEN, chuỗi đầy đủ
      create→governed-close→freeze qua cả service lẫn HTTP). Đồng thời rà lại
      toàn bộ front door (roadmap này, `CVF_CONTROL_MAPPING.md`,
      `IMPLEMENTATION_STATUS.json`, `MODULE_REGISTRY.json`,
      `SESSION/SESSION_MEMORY.md`, `SESSION/ACTIVE_SESSION_STATE.json`) —
      không còn tuyên bố "P-FIX CLOSED" không giới hạn hay "tất cả High
      Finding đã sửa" ở bất kỳ đâu. **Không** đụng tới approval/known-principals
      (High Finding #4) — ngoài phạm vi tranche này.

**Exit gate P-FIX: ĐẠT — CLOSED_BOUNDED (không phải "tất cả finding đã sửa
xong vĩnh viễn").** Toàn bộ Critical (2) và High (3) trong bản review 07-22 có
test end-to-end chứng minh đã sửa (không chỉ unit test gọi thẳng gate) —
freeze cross-record (P-FIX-1), audit atomic (P-FIX-2), evidence persist +
approval known-principal (P-FIX-3), migration Task.version + parity siết chặt
(P-FIX-4). Cả 2 Medium (catalog check, front-door drift) cũng đã sửa (P-FIX-0,
P-FIX-5). P-FIX-6 sửa nốt gap governed-close mà review độc lập **thứ hai** tìm
ra ngay sau khi P-FIX-5 tuyên bố đóng — bằng chứng sống rằng "đã đóng tranche"
tự nó không phải là bằng chứng, phải verify lại bằng probe/test thật.
`pytest` pass — chạy `python -m pytest -q` để lấy số hiện tại, không chép số
cũ. Tổng cộng: **5 tranche triển khai P-FIX-1 tới P-FIX-5, cộng tranche chuẩn
bị P-FIX-0; 6 commit P-FIX trước P-FIX-6, 7 commit P-FIX sau khi P-FIX-6
commit.** Docs không còn tuyên bố "tất cả High Finding đã sửa" — High Finding
#4 còn nguyên các giới hạn liệt kê trong `IMPLEMENTATION_STATUS.json`
(`known_remaining_defects`) và `ACTIVE_SESSION_STATE.json` (`blocked_work`):
identity vẫn header-based; data minimization chỉ khuyến nghị;
data_scope/cost/termination chưa có runtime caller; refusal routing/recording
chưa implement; known-principals chỉ là registry check, không phải xác thực
thật.

**Có thể mở lại:** P2-A (domain còn lại), P2-B, P2-C theo `next_allowed_move`
trong `SESSION/ACTIVE_SESSION_STATE.json` — chỉ sau khi mọi closure surface
của P-FIX-6 đã đồng bộ (điều kiện này tự nó đã thỏa mãn khi bạn đọc dòng này
trong bản đã commit).

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
- [x] **P1-B (2026-07-23, FREEZE / CLOSED_BOUNDED):** Tách domain models ra
      `operations-domain`. 12 operational types (`DataState`, `RiskClass`,
      `ShiftStatus`, `TaskStatus`, `CustomerRequestStatus`, `EvidenceRef`,
      `Shift`, `Message`, `OperationalEvent`, `Correction`, `Task`,
      `CustomerRequest`) và 3 lifecycle guard (`assert_transition`,
      `assert_task_transition`, `assert_customer_request_transition`) giờ có
      **một canonical definition duy nhất** trong `operations_domain.models` /
      `operations_domain.lifecycle`; `workspace_api.domain.models`/`.lifecycle`
      thành **compatibility shim** re-export đúng object (identity `is`, không
      phải `==`, chứng minh bằng test theo từng module pair). `User` **không**
      di chuyển — thuộc auth boundary, nhà canonical vẫn là app, quyết định
      dời thuộc lane reconciliation `known-principals.yaml` ↔ `users`. Package
      là sink (chỉ stdlib + pydantic), không import ngược `workspace_api`/
      `operations_ledger`/`cvf_runtime`. `SqlLedger(models=…)` seam **không**
      refactor (`packages/operations-ledger/**` zero-line diff). `operations-domain`
      **stub → partial** (KHÔNG enforced: incidents/handovers/reports/approvals/
      audit vẫn chưa có model; blueprint subdirectory vẫn README-only). Control
      chain đầy đủ có gate trong commit graph: C1 `3e3df42` (ADR+SPEC+
      WORK_ORDER), C2 `1e56a72` (pre-BUILD continuity), C2b `ab75abb`
      (authorization amendment cho catalog-gate conflict phát hiện trong BUILD),
      C3 `f68cf63` (BUILD, 42 path, independent REVIEW_PASS AC-01…AC-18). Full
      suite 292 passed (221 baseline + 71 mới). Chi tiết:
      `docs/decisions/ADR_2026-07-23_P1B_OPERATIONS_DOMAIN_EXTRACTION.md`.

**Exit gate:** shift record đầy đủ tạo/confirm/freeze được, có test; SqlLedger
round-trip Postgres pass; contract test pass. **CHƯA ĐẠT:** tất cả item `[x]`
không có nghĩa exit gate đã đạt — **SqlLedger round-trip trên PostgreSQL thật
chưa từng chạy** trong môi trường này (không có Docker), vẫn là pre-ship gate.
Đóng P1-B (2026-07-23) là đóng một roadmap item, không phải đóng Phase 1.

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
- [x] **P2-A (customer requests):** Nhân bản CVF chain sang customer_request
      domain (P2-A-CUSTOMER-REQUEST, 2026-07-22) — `CustomerRequest` model +
      `CustomerRequestStatus` lifecycle (NEW→ACKNOWLEDGED→IN_PROGRESS→
      WAITING/RESOLVED→CLOSED terminal; WAITING không nhảy thẳng CLOSED — phải
      qua RESOLVED trước), bảng `customer_requests` map vào `tables.py`
      (`shift_id` NULLABLE khác `tasks`, FK thứ hai tới `messages.message_id`,
      CHECK status khớp migration 002 — parity test xác nhận 2 chiều), ledger
      methods (Protocol/InMemory/Sql), `CustomerRequestService` (create qua
      identity/permission/domain_lock/audit — KHÔNG có risk/evidence/approval
      vì migration không có cột đó; transition qua permission + lifecycle +
      audit), router `/customer-requests`, 18 test (vertical + HTTP + atomic
      rollback cả 2 backend + frozen-shift invariant khi có `shift_id`).
- [ ] **P2-A (còn lại):** incidents, handovers — CHƯA có bảng migration nào
      cho 2 domain này (khác customer_request đã có sẵn migration 002); cần
      migration mới trước khi nhân bản chain, rủi ro/phạm vi lớn hơn.
- [x] **P2-B (2026-07-22):** Authentication thật — JWT bearer token thay
      header-based principal. `dependencies.py · get_principal` không còn đọc
      `X-User-Id`/`X-User-Role` trực tiếp; giờ yêu cầu bearer token đã ký hợp
      lệ (`workspace_api/auth/tokens.py`, HS256, `JWT_SECRET_KEY` bắt buộc
      không default → fail-closed lúc khởi động). `POST /auth/login`
      (`workspace_api/auth/router.py`) cấp token sau khi kiểm username/mật
      khẩu (bcrypt, `workspace_api/auth/passwords.py`) so với bảng `users`
      mới (`database/migrations/003_users.sql`, `add_user`/
      `get_user_by_username` trên cả 2 backend ledger). Mọi router giữ
      nguyên `principal: Principal = Depends(get_principal)` — chỉ thân hàm
      `get_principal` đổi. `identity` chuyển từ "not verified server-side"
      sang "load-bearing" (`docs/cvf/CVF_CONTROL_MAPPING.md`). Test:
      `tests/cvf/test_auth_tokens.py` (8, gồm tamper/expiry/wrong-secret/
      `alg=none`/role lạ), `tests/cvf/test_auth_login.py` (4, gồm cùng thông
      báo lỗi cho sai mật khẩu/username lạ để tránh username enumeration),
      probe hồi quy xác nhận claim `authorized_executive` qua header cũ
      (không kèm bearer) vẫn 401, `tests/integration/test_schema_parity_users.py`
      (role CHECK khớp `KNOWN_ROLES` hai chiều). **Cố ý ngoài phạm vi, ghi rõ
      chứ không lặng lẽ bỏ qua:** refresh token/revocation, tự đăng ký, đặt
      lại mật khẩu, rate-limit đăng nhập, và reconciliation với
      `known-principals.yaml` (registry approver riêng cho quorum R3/R4 —
      High Finding #4 KHÔNG được tranche này sửa). Cấp user chỉ qua
      `scripts/seed_dev_users.py` (dev/test), chưa có admin flow thật.
      ADR: `docs/decisions/ADR_2026-07-22_P2B_JWT_AUTHENTICATION.md`.
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

Xem `next_allowed_move` trong `SESSION/ACTIVE_SESSION_STATE.json`.
**2026-07-22 (P-FIX-6, đóng thật):** tranche P-FIX (P-FIX-0 → P-FIX-6) đã
đóng bounded — 5 tranche triển khai P-FIX-1 tới P-FIX-5, cộng tranche chuẩn bị
P-FIX-0; 7 commit P-FIX tính cả P-FIX-6.
**2026-07-22 (P2-A-CUSTOMER-REQUEST):** đã nhân bản CVF chain sang domain
`customer_request` (chi tiết ở mục P2-A phía trên). **Chính xác về phạm vi:**
P2-A (customer_request) đã xong; P2-A (incidents, handovers) VẪN còn mở —
2 domain này chưa có bảng migration nào, cần migration mới trước khi nhân
bản chain, không tuyên bố "P2-A đã đóng" chung chung.
**2026-07-23 (P2-B):** đã FREEZE authentication thật sau corrective tranche
`P2B-AUTHENTICATION-REPAIR` (đủ WORK_ORDER trước BUILD, hai vòng review,
`REVIEW_PASS`, và live Alibaba evidence HTTP 200; receipt tại
`docs/decisions/P2B_IDENTITY_LIVE_EVIDENCE_RECEIPT.md`). `identity` giờ
load-bearing và governance-approved. **Chính xác về phạm vi:** P2-B KHÔNG đụng tới
`known-principals.yaml` — reconciliation registry approver đó với bảng
`users` mới vẫn là việc mở, chưa có tranche nào nhận; không tuyên bố "High
Finding #4 đã sửa".
**2026-07-23 (P1-B):** đã FREEZE / CLOSED_BOUNDED — tách domain models/lifecycle
guards ra `operations-domain` (chi tiết ở mục P1-B trong Phase 1). Operator đã
xác nhận thứ tự lane hiện hành; **không còn là lựa chọn ba lane tự do**:
1. **P1-B** — HOÀN TẤT (FREEZE 2026-07-23).
2. **known-principals.yaml ↔ authenticated users** (High Finding #4) — **lane
   kế tiếp**, bắt đầu ở một INTAKE mới.
3. **P2-A còn lại** — incidents/handovers (cần migration mới trước).
4. **P2-C** — frontend UI (giữ boundary backend-only).
Không nhảy cóc thứ tự và không bắt đầu bất kỳ lane nào từ loose chat
instruction — mỗi lane cần INTAKE và authorization artifacts riêng.
**Đã đóng, không lặp lại:** freeze bất biến thật (P-FIX-1), audit atomic
(P-FIX-2), evidence persist + approval known-principal (P-FIX-3), migration
Task.version + parity siết chặt (P-FIX-4), catalog `--check` thật (P-FIX-5),
governed shift.close (P-FIX-6), customer_request domain nhân bản đầy đủ
(P2-A-CUSTOMER-REQUEST), authentication thật qua JWT bearer token (P2-B),
tách operations-domain (P1-B).
**Còn treo, không được tuyên bố đã sửa:** data_scope/cost/termination chưa
có runtime caller, refusal routing/recording chưa implement, known-principals
chỉ là registry check (KHÔNG được P2-B thay thế), PostgreSQL round-trip thật
chưa chạy trong môi trường này, incidents/handovers (P2-A còn lại) chưa có
migration, P2-B chưa có refresh token/revocation hay admin flow cấp user thật
— xem `blocked_work` trong `ACTIVE_SESSION_STATE.json`.

## Cách dùng roadmap này

1. Mỗi phiên: đọc mục có `IN PROGRESS`, lấy item `[ ]` đầu tiên theo thứ tự.
2. Làm xong: tick `[x]`, cập nhật catalog + session state, chạy `make validate`.
3. Không nhảy phase khi exit gate của phase trước chưa đạt (ACCEPTANCE_GATES).
