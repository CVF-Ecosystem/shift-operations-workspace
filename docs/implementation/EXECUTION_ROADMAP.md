# Execution Roadmap

Roadmap thực thi có thứ tự, đặt trên 5 phase gốc
([`IMPLEMENTATION_PHASES.md`](IMPLEMENTATION_PHASES.md)). Đây là **nguồn thứ tự
duy nhất**: mọi phiên làm việc quy chiếu về roadmap này thay vì quyết định rời
rạc. Bước kế tiếp luôn khớp `next_allowed_move` trong
`SESSION/ACTIVE_SESSION_STATE.json`.

Dependency order (khóa, từ `DEPENDENCY_ORDER.md`):
contracts → domain → ledger → core workspace → CVF profile/Refinery → AI →
channels → reporting → hardening → freeze.

## Trạng thái hiện tại — đọc mục này trước

_Cập nhật: 2026-08-02, sau Phase 2 full-shift exit BUILD `d02186a` nhận independent final `REVIEW_PASS` và C4 truth-sync._ Quy ước:

- `[x]` / `DONE` / `CLOSED_BOUNDED`: phần được nêu đã có implementation,
  independent review và closure trong đúng claim boundary;
- `[~]` / `PARTIAL`: đã có một phần dùng được nhưng milestone/phase chưa đóng;
- `[ ]` / `NOT STARTED`: chưa có implementation đáp ứng milestone; scaffold,
  README, contract hoặc test helper không được tính là hoàn tất.
| Khu vực | Trạng thái | Đã xong | Còn lại để đóng |
|---|---|---|---|
| P-FIX | 🟢 `CLOSED_BOUNDED` | P-FIX-0 → P-FIX-6 | Không mở lại; các giới hạn mới đi theo tranche riêng |
| P0 governance foundation | ✅ `DONE` (6/6) | runtime gates, catalog/session/boundary/file-size guard | Duy trì gate; không có milestone mở |
| Phase 1 Foundation and Contracts | ✅ `DONE` (7/7) | domain/contracts/ledger, SQLite và disposable PostgreSQL 16 proof | Production/managed PostgreSQL, HA/load/backup không thuộc claim đã đóng |
| Phase 2 Core Operations | ✅ `CLOSED_BOUNDED` | P2-A/P2-B/P2-R/P2-C/P2-D + full-shift exit gate | Chỉ giới hạn ngoài claim: production/managed, soak, push/exactly-once, full-offline |
| Phase 3 Governance and Refinery | 🟡 `PARTIAL` (4/6) | policy gates, approval quorum và P3-A Refinery deterministic local | runtime wiring cho data_scope/cost/termination; retrieval-ready contract |
| Phase 4 AI and Channels | ⬜ `NOT STARTED` (0/8 milestone) | Chỉ có contract/scaffold và webhook verify/dedup nền | AI Gateway, retrieval/RAG/memory, provider modes, Integration Edge đầy đủ, adapters, identity/routing |
| Phase 5 Reporting/Hardening/Freeze | ⬜ `NOT STARTED` (0/5) | Chưa có milestone đóng | reporting engine/output, observability, resilience/security/performance, deployment/Shadow Mode/release freeze |

**Phase 2 đã đóng bounded:** exit gate `start → updates → tasks → handover → report → freeze` PASS tại reviewed/pushed BUILD `d02186a` và C4 này. Claim chỉ cho scheduled 12-hour lineage trên real Chromium/FastAPI/JWT và disposable PostgreSQL 16; không phải wall-clock soak hay production readiness.

## Ghi chú thứ tự (quan trọng — vì sao trạng thái không tuần tự)

Bản EA review (`docs/decisions/EA_INDEPENDENT_REVIEW_2026-07-21.md`) chỉ ra CVF
controls là điểm yếu nhất. Vì vậy công việc đã **chủ động làm trước một phần
Phase 3 (CVF governance)** để dựng cái xương sống governance, trước khi Phase 2
(core operations) hoàn tất. Roadmap dưới đây ghi đúng sự thật đó thay vì giả vờ
tuần tự. Nền tảng ngang (catalog, session governance, boundary) là **P0** — hạ
tầng chung không thuộc phase nghiệp vụ nào.

---

## P-FIX — Corrective tranche — 🟢 CLOSED_BOUNDED (7/7)

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
commit.** Tại closure P-FIX-6, High Finding #4 vẫn mở và identity còn
header-based; các tranche P2-B/P2B sau đó đã thay thế hai sự thật lịch sử này.
Trạng thái còn mở hiện tại: data minimization chỉ khuyến nghị;
data_scope/cost/termination chưa có runtime caller; refusal routing/recording
chưa implement; PostgreSQL đã có disposable-local proof nhưng chưa có
production/managed deployment, load, HA hay backup/restore proof.

**Successor hiện tại:** P2-A incidents/handovers, P2-B authentication và
approver reconciliation đều đã đóng trong các tranche sau; P2-C read-only
slice đã đóng bounded nhưng P2-C tổng thể vẫn mở. Xem bảng trạng thái đầu file
và `next_allowed_move` trong `SESSION/ACTIVE_SESSION_STATE.json`.

---

## P0 — Governance foundation (ngang, phục vụ mọi phase) — ✅ DONE (6/6)

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

## Phase 1 — Foundation and Contracts — ✅ DONE (7/7)

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
      PostgreSQL 16 disposable-local round-trip đã independently REVIEW_PASS
      tại C3 `68cb86e`: migrations 17/0 rồi 14/3, live 36/36, reconnect,
      enum/parity/constraint/rollback và cleanup đều pass. Đây không phải
      production-readiness claim — xem receipt và `MODULE_REGISTRY.json`.
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
      di chuyển — thuộc auth boundary, nhà canonical vẫn là app. Tranche
      reconciliation sau đó đã bỏ `known-principals.yaml` khỏi runtime
      authority nhưng vẫn giữ `User` tại auth boundary; mọi relocation tương
      lai cần tranche riêng. Package là sink (chỉ stdlib + pydantic), không
      import ngược `workspace_api`/
      `operations_ledger`/`cvf_runtime`. `SqlLedger(models=…)` seam **không**
      refactor (`packages/operations-ledger/**` zero-line diff). `operations-domain`
      **stub → partial**. **Tại thời điểm P1-B đóng**, incidents/handovers/
      reports/approvals/audit vẫn chưa có model; incidents và handovers đã
      được bổ sung trong các tranche P2-A sau đó, còn reports/approvals/audit
      package ownership và các blueprint subdirectory vẫn chưa hoàn tất. Control
      chain đầy đủ có gate trong commit graph: C1 `3e3df42` (ADR+SPEC+
      WORK_ORDER), C2 `1e56a72` (pre-BUILD continuity), C2b `ab75abb`
      (authorization amendment cho catalog-gate conflict phát hiện trong BUILD),
      C3 `f68cf63` (BUILD, 42 path, independent REVIEW_PASS AC-01…AC-18). Full
      suite 292 passed (221 baseline + 71 mới). Chi tiết:
      `docs/decisions/ADR_2026-07-23_P1B_OPERATIONS_DOMAIN_EXTRACTION.md`.

**Exit gate: ĐẠT (2026-07-26).** Shift create/confirm/close/freeze + contract
subset 100 pass; disposable PostgreSQL 16 live round-trip 36 pass;
migrations 17/0 rồi 14/3; full non-live 427 pass/36 skip/1 warning;
repository gates và AC-19 rollback rehearsal PASS. Phase 1 `DONE` chỉ trong
boundary này, không chứng minh production deployment/load/concurrency/HA/
backup/managed-PostgreSQL parity.

---

## Phase 2 — Core Operations Workspace — ✅ CLOSED_BOUNDED (14/14)

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
- [x] **P2-A (incidents, 2026-07-26, CLOSED_BOUNDED):** migration 005 +
      canonical `Incident`/`IncidentStatus`, lifecycle, native PostgreSQL
      risk enum parity, evidence persistence, ledger parity, governed
      report/acknowledge/transition services and five API operations.
      Acknowledgement reuses authenticated durable scope-bound approval
      receipts; no caller-supplied approval. C3 `eac28f9` changed exactly 39
      authorized paths and received independent REVIEW_PASS after
      `INC-REV-F1..F6` closed without waiver. Evidence: full non-live 511,
      PostgreSQL 16 live 44 with exact cleanup, real provider HTTP 200 and
      AC-18 parent baseline 427. Boundary: local/disposable evidence only;
      handovers/reports/freeze semantics were not changed.
- [x] **P2-A (handovers, 2026-07-27, CLOSED_BOUNDED):** migration 006 +
      canonical model/lifecycle, server-derived open-item snapshot và digest,
      ledger parity, governed sender review và distinct receiver
      acknowledgement. `open_handover_items_linked` giờ là prerequisite thật;
      report approval vẫn là audited override. C3 `8485ef9` gồm đúng 47 path
      và nhận independent REVIEW_PASS sau `HOV-AUTH-F1..F4` và
      `HOV-REV-F5..F15` đóng không waiver. Evidence: full non-live 610/606,
      PostgreSQL 16 live 53 với cleanup sạch, real provider HTTP 200 sau bốn
      refusal zero-call. Boundary: không chứng minh destination personnel
      assignment, report approval, UI hay production readiness.
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
- [x] **P2-B approver identity reconciliation (2026-07-26, FREEZE /
      CLOSED_BOUNDED):** bỏ approver do caller tự khai và xóa
      `known-principals.yaml` khỏi runtime authority. Approver đã xác thực JWT
      tạo durable receipt qua `/approvals`; authority hiện tại được đọc lại từ
      active `users`; receipt bind đúng sáu trường `(record_type, record_id,
      action, target_version, risk_class, payload_digest)`. Task creation dùng
      durable intent/digest; quorum matching deterministic, order-invariant,
      chặn self-approval; receipt/intent/mutation/audit atomic trên cả hai
      ledger. C3 `9376ddb` có 38 path, independent `REVIEW_PASS`; focused 116,
      full 369 pass; live Alibaba receipt PASS; AC-21 revert rehearsal PASS.
      **Boundary:** không production endpoint nào gọi provider; không thêm
      refresh/revocation/admin provisioning. Tại thời điểm tranche này đóng,
      PostgreSQL chưa live verified; dependency đó đã được đóng bounded sau
      đó bởi tranche PostgreSQL disposable-local, không phải production proof.
- [x] **Shift-create admission repair (2026-07-30, CLOSED_BOUNDED):**
      internal `POST /shifts` yêu cầu verified JWT, enforce `shift.create` và
      atomic persist shift + actor-bound audit. C3 `3f9e456`; không mở rộng
      thành claim mọi mutation/assignment/data_scope hay production readiness.
- [x] **Internal message admission repair (2026-07-30, CLOSED_BOUNDED):**
      internal `POST /messages` yêu cầu verified JWT, derive sender/source
      authority server-side, enforce `message.create` và atomic persist
      Message + actor-bound audit. C3 `ab92f51`; external/channel ingestion và
      Canonical Message Contract vẫn chưa implement.
- [x] **P2-R — Operational report và prerequisite `report_approved` thật
      (2026-07-31, FREEZE / CLOSED_BOUNDED):** canonical `END_SHIFT` Report,
      immutable version history, exact source manifest/digests, governed
      service/API, R2 receipt binding và atomic Report+Shift freeze đã được
      prove trên InMemory/SQLite/disposable PostgreSQL 16. C3 `18e24e5` đổi
      đúng 59 path, nhận independent final `REVIEW_PASS` và đã push. Đây là
      operational record cho Phase 2 exit gate, không phải P5-A render/export.
- [x] **P2-C — UI tổng thể (CLOSED_BOUNDED 2026-08-02):**
  - [x] **Read-only slice (CLOSED_BOUNDED 2026-07-29):** C3a `fe2f312` và
        C3b `e24905f` cung cấp authenticated shifts/events/open-work reads và
        React console chỉ-đọc với sessionStorage/loading/error/stale suppression.
  - [x] **Assignment foundation + route enforcement (CLOSED_BOUNDED 2026-08-01):**
        C3a1 `ec90c78`; C3a2 `95b66b1` enforce ACTIVE scope và enumeration-safe
        refusal, 74 paths/ba backend; không claim tenant/data_scope/frontend.
  - [x] **C3b1 browser reads/readiness/transport (REVIEW_PASS 2026-08-01):**
        BUILD `03e57f9`, đúng 36/36 path, pass independent review sau F1/F2 và
        PostgreSQL 110/110; không claim mutation concurrency/React feature UI.
  - [x] **C3b2 version/mutation preconditions (REVIEW_PASS 2026-08-02):** BUILD
        `9b751de`, đúng 83/83; F1-F5/residual đóng không waiver; full 1314/127,
        PostgreSQL 117, frontend 31, cleanup PASS.
  - [x] **C3c operator mutation UI (CLOSED_BOUNDED 2026-08-02):** BUILD `65b10d2`, đúng 38/38, independent final `REVIEW_PASS`; frontend 58, full 1327/127, hai real-browser runs và AC-29 exact-parent PASS. Claim chỉ operator controls; không supervisor/offline/realtime/P2-C closure.
  - [x] **C3d supervisor closeout:** BUILD `e120a7f`, 36/36 path, independent
        `REVIEW_PASS`; frontend 92, Python 1351/127, Chromium/FastAPI,
        PostgreSQL 117, AC-29 và fresh exactly-one-provider-call đều PASS.
- [x] **P2-D — bounded offline queue + polling realtime (CLOSED_BOUNDED 2026-08-02):** BUILD `6fc4359`, đúng 49/49 path, independent final `REVIEW_PASS`; frontend 119/typecheck/build, real Chromium/FastAPI 6/6, Python 1356/127, PostgreSQL 117 với cleanup, AC-29 và fresh exactly-one-provider-call đều PASS. Claim chỉ navigation fallback, actor-bound queue cho ba CAS transition, per-tab fail-stop replay và foreground polling; không push, cross-tab/request exactly-once, full-offline hay production readiness.
- [x] **Full-shift exit gate (CLOSED_BOUNDED 2026-08-02):** BUILD `d02186a`, đúng 15/15 path, independent final post-call `REVIEW_PASS`; frontend 119/typecheck/build, Python 1378/128, real Chromium/FastAPI, PostgreSQL 118 với migrations 29/0→25/4 và cleanup, AC-14 exact-parent PASS. Provider accounting physical 2/accepted 1 giữ nguyên invalidated first call và chặn call thứ ba. Boundary: scheduled 12-hour local/disposable lineage; không soak, push/exactly-once, full-offline hay production.

**Exit gate: ĐẠT / CLOSED_BOUNDED.** Trọn ca `start → updates → tasks → handover → report → freeze` có truy vết đã PASS; các giới hạn trên vẫn mở và không bị làm tròn thành production readiness.

### Hàng đợi tự động ngay sau Phase 2

Trigger đã thỏa tại BUILD `d02186a` + C4. Orchestrator kích hoạt đúng mục đầu tiên dưới đây ở mức fresh INTAKE; các mục sau chưa có BUILD authority:

1. **PROJECT-OPERATIONS-SKILL — FREEZE / CLOSED_BOUNDED:** BUILD
   `ad7e037` đúng tám path, independent final `REVIEW_PASS`; focused 76, full 1454/128, exact-parent 1378/128 và repository gates PASS. Replacement 4 đạt
   4/4; tổng lịch sử 12/8/4, không retry/call thứ 13. C4 authorization
   `d953b18` đã push; independent C4 FREEZE re-review PASS sau một continuity
   finding đóng không waiver. Claim chỉ bốn synthetic fixtures theo skill navigation đã review;
   không prompt enforcement, production governance, installation hay Phase 3.
2. **PROJECT-KNOWLEDGE-PACK — FREEZE / CLOSED_BOUNDED:** BUILD `bb3e336` đúng tám path, independent `FINAL_REVIEW_PASS`, F1-F4 đóng không waiver;
   BUILD validator/focused 86/full 1540/128/repository gates/doctor 24/1 PASS, zero provider/network/POST; C4 exact 10 paths qua `c32b5c5`/`ffd548e`/`5c50706`, zero provider/helper/POST và chỉ bounded git-governance network. Claim chỉ INTERNAL advisory pack, deterministic local validator và disposable local helper transform;
   không remote ingest, retrieval, automatic injection, provider behavior, Refinery/RAG/production.
3. **P3-A Refinery — FREEZE / CLOSED_BOUNDED:** reviewed BUILD `a6cf978` implements deterministic local normalize, dedupe, redact, classify, quarantine, provenance and data-quality with no runtime caller/provider/remote-ingest claim;
4. **P3-C retrieval-ready contract → P4-A1 governed retrieval → P4-A2 RAG**;
5. **governed learning runtime:** chỉ mở sau Refinery, authorization/
   data-scope, provenance và retrieval gates hoạt động thật; learning không
   được tự biến provider/chat history thành canonical operational truth.

Đây là hàng đợi bắt buộc, không phải authority BUILD sớm. Mỗi mục vẫn phải mở
fresh INTAKE và đi đủ `INTAKE → DESIGN → SPEC → WORK_ORDER → BUILD → REVIEW →
FREEZE`. Trong lúc Phase 2 còn mở, skill/knowledge chỉ là nền móng và learning
runtime vẫn `NOT_BUILT`.

---

## Phase 3 — CVF Governance and Refinery — 🟡 PARTIAL (4/6)

Gate gốc: protected actions đi qua policy, R3/R4 không bypass, Refinery lỗi có
fallback.

- [x] CVF Application Profile enforce đầy đủ (12/12 control trong cvf-runtime).
- [x] domain_lock, data_scope, cost, termination có gate + test.
- [x] R3/R4 approval quorum không bypass (test chứng minh).
- [x] **P3-A:** Refinery boundary thật (`refinery-bridge`): normalize, dedupe,
      redact, classify, quarantine, provenance và data-quality score trước khi
      dữ liệu được phép thành context candidate; fallback về rules khi lỗi.
      Đây là lớp làm sạch bắt buộc trước retrieval/LLM, chưa phải RAG.
- [ ] **P3-B:** Wire các gate data_scope/cost/termination vào một điểm gọi thật
      (khi Phase 4 AI bật) — hết trạng thái "AI-gated only".
- [ ] **P3-C:** Retrieval-ready data contract: canonical chunks/record links,
      tenant/shift/time scope, source version, correction/freeze state,
      retention/erasure marker và deterministic provenance. Không vector hóa
      dữ liệu chưa qua Refinery hoặc chưa vượt data-scope gate.

**Exit gate:** protected action đi qua policy; Refinery lỗi có fallback về
rules; R3/R4 không bypass được.

---

## Phase 4 — AI and Channel Capabilities — ⬜ NOT STARTED (0/8 milestone)

Gate gốc: thay provider/channel không sửa core; invalid schema bị reject;
external prompt injection không vượt trust boundary.

`ai-providers` và `integration-edge` có scaffold/contract hoặc capability nền
(quota/config evidence; webhook verify + dedup), nhưng chưa work item nào bên
dưới đạt milestone Phase 4. Vì vậy phase vẫn là `NOT STARTED`, không phải
`PARTIAL`.

- [ ] **P4-A:** AI Gateway (`ai-gateway`): model router, context builder,
      structured output, budget, fallback, kill switch — gọi cvf-runtime gates.
- [ ] **P4-A1:** Governed retrieval foundation: deterministic filtered search
      trên confirmed records, authorization + data-scope trước retrieval,
      citation/source-version bắt buộc và context budget. Triển khai trước
      generation; chưa cần vector database nếu lexical/structured retrieval
      đáp ứng nhu cầu ban đầu.
- [ ] **P4-A2:** Governed RAG khi AI integration đủ sâu: hybrid retrieval,
      rerank, prompt-injection isolation, context lineage, stale-index
      detection và output citation validation. Provider không được trở thành
      nguồn sự thật hay bypass ledger/CVF gates.
- [ ] **P4-A3:** Application memory theo lớp: session/working memory trước,
      episodic/semantic memory sau; mỗi entry có owner, purpose, provenance,
      TTL/retention, correction/delete path và scope. Chat history hoặc
      provider-local memory không phải canonical operational truth.
- [ ] **P4-B:** AI providers (`ai-providers`): NO_AI, RULES_ONLY, mock trước.
- [ ] **P4-C:** Integration Edge đầy đủ: raw_payload, quarantine, rate_limit,
      routing, outbound (hiện chỉ có webhook verify + dedup).
- [ ] **P4-D:** Channel adapters: generic webhook + mock Zalo/WhatsApp.
- [ ] **P4-E:** Identity mapping + conversation routing.

**Exit gate:** thay provider không sửa core; invalid schema reject; prompt
injection từ channel không vượt trust boundary.

---

## Phase 5 — Reporting, Hardening and Freeze — ⬜ NOT STARTED (0/5)

Gate gốc: evidence traceability, outage drills, backup restore, owner review.

P5-A là engine trình bày/tổng hợp và xuất báo cáo. Nó không thay thế P2-R
operational report record cần để hoàn thành một ca và thỏa freeze prerequisite.

- [ ] **P5-A:** Reporting engine: report draft từ confirmed records, PDF/Excel.
- [ ] **P5-A2:** Proactive reporting và forecasting sau khi reporting +
      governed retrieval/RAG ổn định: scheduled signals, anomaly/trend
      detection, forecast confidence/calibration, drift monitoring và human
      approval trước mọi durable recommendation/action. Dự báo không tự biến
      thành operational fact hoặc kích hoạt protected action.
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
**2026-07-27 (P2-A):** customer_request, incidents và handovers đều đã đóng
bounded trong các tranche riêng. Điều này chưa đóng Phase 2: frontend,
reporting và report-approval prerequisite vẫn còn mở.
**2026-07-23 (P2-B):** đã FREEZE authentication thật sau corrective tranche
`P2B-AUTHENTICATION-REPAIR` (đủ WORK_ORDER trước BUILD, hai vòng review,
`REVIEW_PASS`, và live Alibaba evidence HTTP 200; receipt tại
`docs/decisions/P2B_IDENTITY_LIVE_EVIDENCE_RECEIPT.md`). `identity` giờ
load-bearing và governance-approved. **Chính xác về phạm vi:** P2-B KHÔNG đụng tới
`known-principals.yaml` — reconciliation registry approver đó với bảng
`users` mới vẫn là việc mở, chưa có tranche nào nhận; không tuyên bố "High
Finding #4 đã sửa".
**2026-07-26 (P2B approver identity reconciliation):** đã FREEZE /
`CLOSED_BOUNDED`; High Finding #4 đóng trong boundary authenticated durable
scope-bound receipts, không phải tuyên bố "mọi finding đã sửa".

**2026-07-26 (CVF file-split guard hardening):** đã `FREEZE /
CLOSED_BOUNDED`; C3 `46da20a` đổi đúng 23 path được authorize và nhận
independent `REVIEW_PASS`. Python 300 và TS/TSX/JS/JSX 200 hiện là hard guard;
legacy debt được khóa bằng exact path/SHA-256/line count ở đúng bốn path.
Guard 36 pass, full suite 405 pass/1 warning, AC-24 revert rehearsal PASS.
Tranche này không đổi trạng thái roadmap/module và tại thời điểm đó chưa đóng
Phase 1; PostgreSQL-live tranche kế tiếp đã đóng gate vào 2026-07-26.

**2026-07-29 (P2-C read slice):** `FREEZE / CLOSED_BOUNDED`; C3a `fe2f312`
và C3b `e24905f` được review/commit/push riêng. Đây chỉ là read-only slice,
không đóng P2-C hoặc Phase 2.

**2026-07-30 (Shift-create admission repair):** `FREEZE / CLOSED_BOUNDED`;
C3 `3f9e456` đổi đúng 19 path được authorize và nhận independent
`REVIEW_PASS` sau khi `SCR-BUILD-REV-F1..F3` đóng không waiver. `POST /shifts`
giờ yêu cầu JWT đã verify, enforce `shift.create` tối thiểu `operator`, và
atomic persist shift + actor-bound audit. PostgreSQL 16 disposable-local chạy
qua JWT/FastAPI thật; live Alibaba evidence chỉ gọi đúng một lần sau admitted
proof. Boundary không bao gồm message identity, assignment/data_scope,
frontend mutation, production PostgreSQL, P2-C completion hay Phase 2
completion.

**2026-07-30 (Message admission trust repair):** `FREEZE / CLOSED_BOUNDED`;
C3 `ab92f51` đổi đúng 30 path được authorize và nhận independent final
`REVIEW_PASS` sau khi `MAR-BUILD-REV-F1..F5` đóng không waiver qua nhiều vòng
repair. Internal `POST /messages` giờ yêu cầu JWT đã verify, derive
sender/source authority server-side, enforce `message.create`, và atomic
persist Message + actor-bound audit trên các backend đã prove. Evidence:
focused 82/7 skipped; full 789/76 skipped; PostgreSQL 66 của vòng repair trước
được giữ đúng sự thật và không giả nhận rerun ở vòng F2 cuối; fresh Alibaba
HTTP 200 sau bảy refusal zero-call và đúng một admitted provider call.
Boundary không bao gồm external/channel ingestion, Canonical Message Contract,
assignment/data_scope, production PostgreSQL, P2-C completion hay Phase 2
completion.

**2026-07-31 (P2-R operational Report + freeze prerequisite):** `FREEZE /
CLOSED_BOUNDED`; C3 `18e24e5` đổi đúng 59 path và được push sau independent
final `REVIEW_PASS`, toàn bộ findings qua nhiều vòng đóng không waiver.
Evidence cuối: focused 385; full 998/87 skipped; PostgreSQL 77 với migrations
22/0 rồi 18/4 và exact cleanup; retained provider receipt hợp lệ với bảy
zero-call refusals rồi đúng một Alibaba call HTTP 200; doctor 24/1. Parent
rehearsal tại `6b2d014` trả 788/77 skipped và cleanup PASS. Boundary không
bao gồm P5-A rendering/export, managed PostgreSQL, P2-C, P2-D hoặc Phase 2.

**2026-08-01 (P2-C C3a2):** `FREEZE / CLOSED_BOUNDED`; C3 `95b66b1`, exact 74 paths, final `REVIEW_PASS`, mọi finding đóng không waiver; 39/1180/116/PostgreSQL 106/live pass. Chỉ claim single-workspace stored ACTIVE;
C3b-d/P2-D/exit còn mở.
**2026-08-02 (P2-C C3d / P2-C closure):** BUILD `e120a7f`, 36/36 path,
independent `REVIEW_PASS`/push; frontend 92, Python 1351/127, Chromium/FastAPI,
PostgreSQL 117, AC-29 và provider evidence PASS. P2-C `CLOSED_BOUNDED`, không
gồm offline/realtime, production, P2-D, full-shift exit hay Phase 2 closure.
External/channel ingestion qua Integration Edge là Phase 4 riêng; internal `POST /messages` không chứng minh phần này.
**2026-08-02 (P2-D offline/realtime):** `FREEZE / CLOSED_BOUNDED`; BUILD `6fc4359`, exact 49 path, independent final `REVIEW_PASS`, mọi finding đóng không waiver. Evidence: frontend 119/typecheck/build; Chromium/FastAPI 6/6; Python 1356/127; PostgreSQL 117, migrations 29/0→25/4, exact cleanup; AC-29; repository gates; fresh refusal-zero-call rồi đúng một provider call HTTP 200.
**2026-08-02 (Phase 2 full-shift exit):** `FREEZE / CLOSED_BOUNDED`; BUILD `d02186a`, exact 15 path, independent final post-call `REVIEW_PASS`, mọi finding đóng không waiver. Evidence: frontend 119/typecheck/build; Python 1378/128; real Chromium/FastAPI; PostgreSQL 118, migrations 29/0→25/4, exact cleanup; AC-14; repository gates; provider accounting physical 2/accepted 1 với first call retained invalidated và third call fail-closed. Phase 2 đóng chỉ trong scheduled-lineage boundary, không production/managed/soak/full-offline claim.
**Bước kế tiếp duy nhất:** P3-C SPEC R1 `docs/specs/P3C_RETRIEVAL_READY_DATA_CONTRACT_SPEC.md` (`0e238862...56ed8`) đã sửa `P3C-SPEC-F1` bằng explicit private-helper bypass guards và chờ independent re-review. Chỉ `SPEC_REVIEW_PASS` mới chuyển sang `WORK_ORDER_AUTHOR`. Không có WORK_ORDER drafting/BUILD/helper/provider/product-network/POST/retrieval authority; P3-B/RAG/learning và runner evidence branch vẫn parked.
**Đã đóng, không lặp lại:** freeze bất biến thật (P-FIX-1), audit atomic
(P-FIX-2), evidence persist + approval known-principal (P-FIX-3), migration
Task.version + parity siết chặt (P-FIX-4), catalog `--check` thật (P-FIX-5),
governed shift.close (P-FIX-6), customer_request domain nhân bản đầy đủ
(P2-A-CUSTOMER-REQUEST), authentication thật qua JWT bearer token (P2-B),
tách operations-domain (P1-B), authenticated scope-bound approval receipts
(P2B approver-identity reconciliation), repository-enforced file-split guard
(CVF-FILE-SPLIT-GUARD-HARDENING), PostgreSQL migration-created-schema live
round-trip và Phase 1 exit gate
(P1-POSTGRESQL-LIVE-ROUNDTRIP-2026-07-26), governed incident vertical
(P2A-INCIDENT-VERTICAL-2026-07-26, C3 `eac28f9`), governed handover vertical
(P2A-HANDOVER-VERTICAL-2026-07-26, C3 `8485ef9`), governed shift-create
admission (SHIFT-CREATE-ADMISSION-REPAIR-2026-07-29, C3 `3f9e456`), governed
internal message admission (MESSAGE-ADMISSION-TRUST-REPAIR-2026-07-30, C3
`ab92f51`), governed operational Report and audited `report_approved` freeze
prerequisite (P2R-OPERATIONAL-REPORT-FREEZE-PREREQUISITE-2026-07-30, C3
`18e24e5`), P2-C assignment foundation/enforcement (`ec90c78`, `95b66b1`).
**Còn treo, không được tuyên bố đã sửa:** data_scope/cost/termination chưa
có runtime caller, refusal routing/recording chưa implement, PostgreSQL mới
được chứng minh trong disposable local PostgreSQL 16 chứ chưa production/
managed deployment, retrieval/RAG/
application memory/proactive forecasting mới chỉ nằm trong roadmap, P2-B
chưa có refresh token/revocation hay admin flow cấp user thật
— xem `blocked_work` trong `ACTIVE_SESSION_STATE.json`.

## Cách dùng roadmap này

1. Mỗi phiên: đọc mục có `IN PROGRESS`, lấy item `[ ]` đầu tiên theo thứ tự.
2. Làm xong: tick `[x]`, cập nhật catalog + session state, chạy `make validate`.
3. Không nhảy phase khi exit gate của phase trước chưa đạt (ACCEPTANCE_GATES).
