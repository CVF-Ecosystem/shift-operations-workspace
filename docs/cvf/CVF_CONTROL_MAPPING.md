# CVF Control Mapping

Ánh xạ từng CVF `required_control` (khai báo trong
`packages/cvf-application-profile/profile.yaml`) tới **điểm thực thi bằng code**,
kèm trạng thái thật.

**2026-07-22 correction:** một review độc lập (Codex,
`docs/decisions/EA_INDEPENDENT_REVIEW_2026-07-22_CODEX.md`) chứng minh bằng
probe chạy thật rằng nhãn "enforced" trước đây trong file này đã bị dùng quá
rộng — nó chỉ đúng cho "có hàm gate + unit test", không có nghĩa "chặn được vi
phạm trong request path thật, không bypass được". Bảng dưới đây dùng lại đúng 2
mức đó, tách bạch.

**2026-07-22 P-FIX-6 correction:** một review độc lập **thứ hai** bác bỏ tuyên
bố đóng tranche P-FIX-5. `POST /shifts/{shift_id}/close` vẫn gọi thẳng
`ledger.close_shift()` từ router — không identity, không permission, không
audit (probe: `create=200`, `anonymous_close=200`, `status=CLOSED`,
`audit_count=0`). Vì `ShiftService.freeze` chỉ kiểm
`shift.status == ShiftStatus.CLOSED`, close vô danh này âm thầm thỏa mãn điều
kiện tiên quyết `shift_closed` của freeze — đúng loại bypass CVF được thiết kế
để chặn. P-FIX-6 thêm `shift.close` làm governed action thật (xem dòng
`freeze`/`shift.close` trong bảng dưới); đây KHÔNG đụng tới approval/High
Finding #4 (xem `docs/decisions/EA_INDEPENDENT_REVIEW_2026-07-22_CODEX.md`) —
phạm vi P-FIX-6 chỉ là shift-close.

**2026-07-22 P2-B correction (real authentication):** `identity` chuyển từ
**not verified server-side** sang **load-bearing**. `dependencies.py ·
get_principal` không còn đọc `X-User-Id`/`X-User-Role` trực tiếp — giờ yêu
cầu một JWT bearer token đã ký hợp lệ (`workspace_api/auth/tokens.py`,
HS256, ký bằng `JWT_SECRET_KEY` bắt buộc, không có default nên app fail-closed
lúc khởi động nếu thiếu) và chỉ dựng `Principal` từ claim `sub`/`role` đã xác
thực chữ ký — không còn từ bất kỳ field nào caller tự khai trực tiếp.
`POST /auth/login` (`workspace_api/auth/router.py`) cấp token sau khi kiểm
username/password so với bảng `users` mới (mật khẩu hash bằng bcrypt). **Cố ý
NGOÀI phạm vi tranche này, không tuyên bố đã sửa:** refresh token/revocation,
tự đăng ký, đặt lại mật khẩu, rate-limit đăng nhập, và — quan trọng nhất —
**không đụng tới `known-principals.yaml`** (registry approver riêng dùng cho
quorum approval R3/R4). Vì vậy High Finding #4 vẫn còn nguyên **tại closure
P2-B 2026-07-23**; trạng thái hiện tại đã được tranche 2026-07-26 bên dưới
thay thế.

**2026-07-23 governance closure:** corrective tranche
`P2B-AUTHENTICATION-REPAIR` đã đi đủ INTAKE → DESIGN → SPEC → WORK_ORDER →
BUILD → REVIEW → FREEZE. Review độc lập trả `REVIEW_PASS`; live evidence thật
qua Alibaba (`qwen3.7-max`, HTTP 200) xác nhận identity gate chấp nhận JWT hợp
lệ, từ chối token giả mạo, rồi mới cho phép provider call. Receipt:
`docs/decisions/P2B_IDENTITY_LIVE_EVIDENCE_RECEIPT.md`. Claim này chỉ áp dụng
cho `identity`; tại thời điểm closure đó, approval/known-principals High
Finding #4 vẫn mở.

**2026-07-26 approval closure:** tranche
`P2B-APPROVER-IDENTITY-RECONCILIATION` đã đi đủ control chain và đạt `FREEZE /
CLOSED_BOUNDED`. C3 `9376ddb` (38 path) nhận independent `REVIEW_PASS`.
`known-principals.yaml` bị xóa khỏi runtime authority; approver xác thực JWT
tạo durable receipt qua `/approvals`, authority được đọc lại từ active `users`,
và receipt bind sáu trường `(record_type, record_id, action, target_version,
risk_class, payload_digest)`. Quorum matching deterministic, order-invariant
và chặn self-approval; Task creation dùng durable intent/digest; atomicity được
test trên cả hai ledger. Live Alibaba evidence PASS sau genuine quorum, không
có provider call cho refusal. Receipt:
`docs/decisions/P2B_APPROVER_IDENTITY_LIVE_EVIDENCE_RECEIPT.md`.

**2026-07-26 P2A-INCIDENT-VERTICAL:** thêm `IncidentService` làm service thứ
sáu — domain `equipment_incident` (fifth operational vertical). Khác các
domain trước: report là identity/permission/domain_lock/persist/audit tức
thời (không chờ quorum); riêng `incident.acknowledge` mới là quyết định được
bảo vệ (R2+), tái dùng đúng kiến trúc durable receipt của `event.confirm`
(risk → evidence → approval → lifecycle → persist → audit, receipt bind
`(record_id, target_version)` của chính Incident đã persist, không có creation
intent thứ hai). `incident.transition` chỉ xử lý tiến trình sau acknowledge —
generic transition action từ chối tường minh khi status còn `REPORTED`, dù
lifecycle guard (đầy đủ đồ thị `REPORTED→ACKNOWLEDGED→MITIGATING/RESOLVED→
CLOSED`) về mặt kỹ thuật cho phép chuyển đó; chỉ `acknowledge` mới được thực
hiện bước đó. Bảng `incidents` khớp migration 005 hai chiều (schema-parity
test riêng, không mở rộng `MAPPED` dict dùng chung). Live PostgreSQL 16 xác
nhận bảng/enum/CHECK/FK/round-trip/rollback (`tests/integration/
test_incident_postgres_live.py`); live Alibaba evidence PASS sau một
acknowledge hợp lệ, 0 provider call cho mọi refusal (insufficient evidence,
fabricated, self-approval, inactive approver, stale version). Receipt:
`docs/decisions/P2A_INCIDENT_LIVE_EVIDENCE_RECEIPT.md`. Xem mục 6 trong
"Golden verticals" và dòng `incident.report / .acknowledge / .transition`
trong bảng dưới.

**2026-07-26 P2A-INCIDENT-VERTICAL repair (Amendment 1, INC-REV-F1..F5):**
review độc lập đầu tiên trả `REVIEW_CHANGES_REQUIRED` với 5 finding, sửa hết
không waiver: (F1) golden OpenAPI digest được refresh chỉ sau khi CHỨNG MINH
cơ học delta đúng bằng 5 operation + schema incident, không phải làm mới mù
quáng (`tests/unit/test_p2b_openapi_contract.py::
test_openapi_delta_is_exactly_the_five_incident_operations` dựng lại document
cũ bằng cách xóa đúng các path/schema mới rồi so hash với giá trị gốc); (F2)
`add_incident` giờ ném cùng `ValueError` có kiểm soát trên cả 2 backend khi
trùng id, `put_incident` ném `KeyError` khi thiếu id, list order thêm
tie-break `incident_id` sau `created_at`; (F3) SQL list giờ dựng lại evidence
trong cùng connection/unit như get (trước đây `get=1, list=0` — mất evidence
âm thầm); (F4) `version >= 1` giờ là bất biến thật ở model Pydantic
(`Field(ge=1)`), migration 005 và SQLAlchemy metadata (CHECK cùng tên), có
test dương/âm ở model, SQLite và PostgreSQL live; (F5)
`scripts/_incident_live_evidence_support.py` (mới) sở hữu toàn bộ provider
HTTP/sanitization/safe-endpoint-description/receipt rendering — sanitize
đúng key, bearer/JWT, lỗi HTTP, userinfo/query/fragment của URL; đếm
provider-call qua `ProviderCallCounter` mới mỗi lần chạy (không phải literal
hardcode); test sentinel-bearing chứng minh secret không lộ ra summary,
stdout/stderr lẫn receipt. Re-run độc lập: full suite 507 pass/44 skip;
PostgreSQL 16 live 44 pass, cleanup container/volume sạch; live Alibaba
evidence PASS lại với đúng 0 call refusal/1 call sau acknowledge hợp lệ.

**2026-07-26 P2A-HANDOVER-VERTICAL:** thêm `HandoverService` làm service thứ
bảy — domain `shift_handover`. Ba hành động: `create` (identity/permission
`operator` → `domain_lock shift_handover` → server tự derive toàn bộ
`items` từ đúng tập open work của shift nguồn — `Task` khác `DONE`/
`CANCELLED`, `CustomerRequest` khác `CLOSED`, `Incident` khác `CLOSED` — caller
KHÔNG bao giờ tự cung cấp items/digest/status/actor; mỗi item mang một
SHA-256 digest chuẩn tắc trên snapshot server-derived của chính nó); `review`
(sender, `shift_supervisor`, revalidate destination OPEN/source not-FROZEN và
khớp đúng snapshot trước khi DRAFT→REVIEWED); `acknowledge` (receiver phải là
supervisor xác thực KHÁC người review, cùng revalidate state/snapshot trước
khi REVIEWED→ACKNOWLEDGED). `ACKNOWLEDGED` là terminal; khôi phục từ snapshot
lệch là tạo draft mới, không sửa cái cũ. Không có registry gán nhân sự nào
trong repo, nên acknowledge chỉ chứng minh một supervisor xác thực khác biệt
đã chấp nhận — KHÔNG tuyên bố nhân sự đó được gán vào ca đích.

`ShiftService.freeze`'s `open_handover_items_linked` giờ là tiền đề THẬT
(`assert_freeze_ready`, `workspace_api.application.handover_service`): cần ít
nhất một handover `ACKNOWLEDGED` của đúng ca đó mà snapshot vẫn khớp open work
hiện tại VÀ ca đích vẫn `OPEN` — không cache lại lúc acknowledge, kiểm tra lại
tại chính thời điểm freeze. Readiness check, freeze mutation, và cả hai audit
(freeze + override) giờ dùng chung một transaction. `report_approved` là điều
kiện duy nhất còn lại dùng override tường minh có audit; văn bản audit của
override giờ chỉ nói `report_approved`, không còn nhắc
`open_handover_items_linked` (điều đó đã có kiểm tra thật, không phải bỏ qua).
Bảng `handovers`/`handover_items` khớp migration 006 hai chiều (schema-parity
riêng, gồm cả enum `handover_status` native lẫn `risk_class` tái dùng). Live
PostgreSQL 16 xác nhận bảng/enum/CHECK/FK/round-trip/rollback
(`tests/integration/test_handover_postgres_live.py`); live Alibaba evidence
PASS sau review + acknowledge + freeze hợp lệ qua đúng route HTTP/JWT thật, 0
provider call cho 4 refusal case (thiếu handover, mới REVIEWED chưa
acknowledge, tự acknowledge chính mình, snapshot cũ sau khi source đổi).
Receipt: `docs/decisions/P2A_HANDOVER_LIVE_EVIDENCE_RECEIPT.md`.

**HOV-AUTH-F4 (2026-07-26, sau khi Claude dừng đúng lúc không tự sửa):** full
suite lộ 2 test path ngoài đúng 39-path Work Order
(`tests/cvf/test_atomic_mutation_audit.py`,
`tests/cvf/test_customer_request_vertical.py`) vẫn freeze một ca đã đóng qua
override cũ mà không tạo handover thật. Codex xác nhận độc lập, ra ADR/SPEC/
Work Order Amendment 1 mở đúng 2 path đó (ceiling 41), cấm mọi bypass sản
xuất. Repair: cả hai test giờ dựng đúng chuỗi
`HandoverService.create`→`review`→`acknowledge` (rỗng, không có open work)
trước khi freeze, giữ nguyên assertion rollback/frozen-parent gốc — không
chèn thẳng trạng thái terminal, không mock readiness.

**HOV-REV-F5/F6/F7/F8 (2026-07-26, independent BUILD review Amendment 2):**
Codex review độc lập KHÔNG chấp nhận receipt của worker làm bằng chứng, tự
chạy lại từ nguồn và ra `REVIEW_CHANGES_REQUIRED` với 4 finding, sửa hết
không waiver: (F5 `DEBT_RATCHET_BYPASS`) Amendment 1 cho phép content-edit
`test_customer_request_vertical.py` nhưng vẫn giữ nguyên giới hạn 300 dòng —
BUILD để file ở 321 dòng và chỉ rewrite digest debt entry, phá vỡ đúng ratchet
mà baseline yêu cầu ("mọi content edit buộc split coherent trong cùng changed
set"); giờ file split thành chính nó (create/HTTP, ≤300),
`_customer_request_fixtures.py` (setup dùng chung) và
`test_customer_request_transitions.py` (lifecycle/transition), debt entry bị
xóa hẳn (không rehash); `test_customer_request_repair.py` (ngoài phạm vi
repair này) vẫn import đúng các fixture cũ không đổi vì
`test_customer_request_vertical.py` giờ re-expose chúng từ module dùng chung.
(F6 `CONTINUITY_GATE_RED`) `SESSION/SESSION_MEMORY.md` 607/600 dòng do chính
continuity commit của Codex gây ra, không thuộc 41 BUILD path của worker —
Codex tự sửa riêng ở C2e, không giao cho Claude. (F7
`LEDGER_PARITY_AND_IMMUTABILITY_GAP`) probe độc lập chứng minh
InMemoryLedger chấp nhận item trùng `(source_record_type, source_record_id)`
trong cùng handover và shift nguồn/đích không tồn tại; SqlLedger rò/gắn nhầm
`IntegrityError` thô thành "duplicate handover_id" kể cả khi nguyên nhân thật
là FK thiếu shift; `put_handover` không enforce bất biến snapshot nhất quán ở
cả hai backend. Sửa: `_handover_repository.py`/`_handover_store.py` giờ
prevalidate tồn tại shift nguồn/đích, trùng aggregate id, trùng item source
và item/aggregate mismatch bằng CÙNG connection/unit trước khi ghi bất kỳ
dòng nào — từ chối luôn để lại state sạch, không có `IntegrityError` thô nào
lọt ra; `put_handover` giờ chỉ cho sửa các trường lifecycle (status/reviewer/
receiver/timestamp/version), từ chối mọi thay đổi shift pair/items/evidence
với cùng `ValueError` có kiểm soát trên cả hai backend. Test mới:
`tests/integration/test_handover_ledger_parity.py` (17 test, cả 2 backend,
chứng minh không có partial write). (F8 `BUILD_RECEIPT_DRIFT`) receipt cũ
tuyên bố `571 passed` trong khi rerun độc lập ra `567 passed, 53 skipped, 1
warning`; receipt giờ chỉ trích đúng kết quả rerun tươi sau repair, kèm lịch
sử F5-F8 và việc PostgreSQL/provider re-review đã dừng lại khi F7 được phát
hiện.

**HOV-REV-F9/F10 (2026-07-26, re-review độc lập lần hai, cùng ceiling 44,
không Amendment 3):** (F9 `PARTIAL_SNAPSHOT_COMPARATOR`) comparator bất biến
của `put_handover` trước đây chỉ so `(source_record_type, source_record_id,
source_digest)` mỗi item — `summary`, `evidence`, `owner_id`, `due_at`,
`risk_class`, `item_id`, `handover_id` riêng của item, và `created_at` của
chính aggregate đều có thể bị sửa lặng lẽ. Sửa: `_full_item_key`/`_items_key`
(cả hai backend) giờ so khớp TOÀN BỘ trường của `HandoverItem` cộng
`created_at` của aggregate; `test_handover_ledger_parity.py` thêm test
parametrized riêng cho từng trường trước đây bị bỏ sót, cả hai backend (35
test, tăng từ 17). (F10 `REVIEW_COMMAND_SCOPE_MISCLASSIFICATION`) chẩn đoán
F8 trước đây là lỗi của reviewer: `571` (root `python -m pytest -q`) khác
`567` (`python -m pytest tests/ -q`) đúng 4 test vì
`apps/workspace-api/src/workspace_api/tests/test_lifecycle.py` nằm ngoài
`tests/` nên chỉ root discovery thấy — không phải receipt trôi dạt. Receipt
giờ báo cả hai lệnh tường minh:
`python -m pytest -q` → `606 passed, 53 skipped, 1 warning`;
`python -m pytest tests/ -q` → `602 passed, 53 skipped, 1 warning`.

**2026-07-30 P2R-OPERATIONAL-REPORT-FREEZE-PREREQUISITE:** thêm `ReportService`
làm service thứ tám — domain vertical `Report` (`report_type` cố định
`END_SHIFT`). Bốn hành động: `generate` (identity/permission `report.generate`
role tối thiểu `operator` → yêu cầu shift cha `CLOSED` → server tự derive toàn
bộ snapshot sáu section (`operational_events`, `corrections`, `tasks`,
`customer_requests`, `incidents`, `handovers`) cộng `source_manifest` và
`snapshot_digest` SHA-256 canonical — caller KHÔNG BAO GIỜ tự cung cấp
content/status/version/digest; `Ledger.transaction()` bọc `add_report` +
`append_audit` atomic); `submit_review` (role tối thiểu `operator` → revalidate
snapshot khớp truth hiện tại → DRAFT→IN_REVIEW); `approve` (role tối thiểu
`shift_supervisor` → revalidate lại → tái dùng đúng kiến trúc durable receipt
của `event.confirm`/`incident.acknowledge`, risk cố định `R2`, receipt bind
`(record_id=report_id, target_version=version, payload_digest=snapshot_digest)`
→ IN_REVIEW→APPROVED); `create_successor` (regenerate content mới nhất, đánh
dấu bản trước `is_current=false` và chèn bản kế tiếp trong CÙNG transaction —
không bao giờ ghi đè snapshot cũ; regenerate một bản đã `APPROVED` là
"revoke approval", bắt buộc lý do 1-1000 ký tự và role `shift_supervisor`).

`ShiftService.freeze`'s `report_approved` giờ là tiền đề THẬT (không còn
override): chọn đúng một current `END_SHIFT` Report, yêu cầu `APPROVED`,
revalidate lại snapshot, rồi chuyển cả Report lẫn Shift sang `FROZEN` cùng
`open_handover_items_linked` readiness và cả hai audit (`report.freeze` +
`shift.freeze`) trong một transaction SERIALIZABLE (PostgreSQL; SQLite/
InMemory dùng single-writer lock tương đương), có bounded retry (tối đa 3
lần) khi gặp serialization conflict thật. Hai field override cũ
(`override_unimplemented_prerequisites`/`override_reason`) vẫn còn trên wire
CHỈ ở giá trị mặc định — bất kỳ giá trị khác đều bị từ chối 422 trước khi đọc
gì thêm; OpenAPI đánh dấu cả hai field `deprecated`. Bảng `reports` khớp
migration 002+007 hai chiều (schema-parity riêng vì bảng trải trên hai file
migration — `test_schema_parity_reports.py` không mở rộng `MAPPED` dict dùng
chung). Live PostgreSQL 16 xác nhận bảng/CHECK/UNIQUE/partial-index/round-trip/
successor/rollback/concurrent-freeze-race (`tests/integration/
test_report_postgres_live.py`, gồm cả test SERIALIZABLE hai kết nối tranh chấp
cùng một freeze); live Alibaba evidence PASS sau generate→review→distinct-
approver receipt→approve→freeze hợp lệ, 0 provider call cho bảy refusal case
(thiếu bearer, viewer generate, shift chưa CLOSED, submit-review khi snapshot
đã cũ, approve thiếu receipt, submit-review một report không còn current,
legacy override). Receipt:
`docs/decisions/P2R_OPERATIONAL_REPORT_FREEZE_LIVE_EVIDENCE_RECEIPT.md`.
**Còn hạn chế:** không implement P5-A rendering/export/PDF/Excel; không AI-
generated operational truth; không production endpoint nào gọi provider;
không chứng minh managed/production PostgreSQL readiness; không assignment/
tenant/data_scope; chỉ `END_SHIFT` — không có report type khác.

## Trạng thái (2 mức — không gộp lại thành "enforced")

- **callable** — hàm gate tồn tại trong `cvf_runtime`, có unit test gọi trực
  tiếp và test đó pass. **Không** đảm bảo request path thật (router → service →
  ledger) gọi tới nó đúng lúc, đúng cách, không có đường vòng.
- **load-bearing** — đã xác nhận (bằng test end-to-end qua router/service, hoặc
  probe runtime) rằng vi phạm **thực sự bị chặn** trong luồng thật, ở cả hai
  backend (InMemory và Sql) khi có backend đó tham gia.
- **profile-only** — policy đã có trong YAML nhưng chưa có code đọc/enforce.
- **not verified server-side** — có gate, nhưng gate tin dữ liệu do caller tự
  cung cấp trong cùng request (vd định danh qua header, approver tự khai) thay
  vì xác thực độc lập.

## Golden verticals — phạm vi chính xác

**2026-07-22 P-FIX-6 closure-cleanup:** mục này trước đó chỉ liệt kê 3 service
(`EventService`, `CorrectionService`, `TaskService`) — đã lỗi thời từ khi
P-FIX-6 thêm `ShiftService.close` làm governed action thứ tư. Cập nhật lại:

**2026-07-22 P2-A-CUSTOMER-REQUEST:** thêm `CustomerRequestService` làm
service thứ năm — nhân bản đúng khuôn `TaskService`/`ShiftService` sang domain
`customer_request`. Xem mục 5 bên dưới.

Năm service (`EventService`, `CorrectionService`, `TaskService`,
`ShiftService`, `CustomerRequestService`) **đều import và gọi cùng các hàm
`cvf_runtime`** — không có bản sao logic permission/evidence/approval nào bị
fork. Đây là phần đã xác nhận đúng.

Nhưng gọi bất kỳ đường nào trong số này là "golden vertical durable/end-to-end"
không có giới hạn vẫn là **quá rộng** (đây chính là nhãn Codex gắn cờ ở review
2026-07-22 — xem `docs/decisions/EA_INDEPENDENT_REVIEW_2026-07-22_CODEX.md`).
Chính xác hơn, theo domain:

1. **Operational Event → confirm** — `EventService.confirm`. Load-bearing trên
   cả 2 backend: `operations_ledger/_rows.py` map cột `evidence` qua bảng
   `evidence_links` (P-FIX-3, 2026-07-22) — event ghi evidence rồi đọc lại
   không còn mất, `assert_evidence_sufficient` không còn từ chối sai một event
   đã có đủ evidence lúc ghi. (Critical Finding #2 trong bản review Codex gốc
   — đã sửa; xem mục `evidence` trong bảng dưới cho test xác nhận.) **Còn hạn
   chế hiện tại:** approval chỉ được chứng minh trong boundary durable
   six-field scope-bound receipt (xem mục approval bên dưới); không production
   endpoint nào gọi provider.
2. **Operational Event → correct** — `CorrectionService.correct_event`.
   Load-bearing về mặt state transition; approval quorum dùng authenticated,
   durable scope-bound receipts (xem mục approval bên dưới).
3. **Task → create / transition** — `TaskService`. Chain đúng ở tầng service
   (test trực tiếp construct `Task` kèm evidence, pass). **Qua HTTP cũng đã
   sửa** (P-FIX-3, 2026-07-22): `TaskInput`/`api/tasks/router.py` giờ có field
   `evidence` (`list[EvidenceRef] = []`) và truyền qua service — request thật
   không còn tự động rỗng evidence, task R2+ tạo qua API với evidence hợp lệ
   không còn bị `evidence` gate từ chối sai.
4. **Shift → close / freeze** — `ShiftService.close`/`ShiftService.freeze`
   (P-FIX-6, P-FIX-1). Load-bearing trên cả 2 backend, có test end-to-end qua
   HTTP (`tests/cvf/test_shift_close_governance.py`,
   `tests/cvf/test_freeze_invariant.py`). **Còn hạn chế:** freeze's
   `report_approved`/`open_handover_items_linked` không có model thật, chỉ
   override tường minh có audit. identity giờ xác thực thật qua JWT (P2-B,
   2026-07-22) — không còn là giới hạn ở domain này hay bất kỳ domain nào khác
   trong bảng.
5. **Customer Request → create / transition** — `CustomerRequestService`
   (P2-A-CUSTOMER-REQUEST, 2026-07-22; repaired after independent review,
   2026-07-22). Chain đúng ở tầng service và qua HTTP. Test:
   `tests/cvf/test_customer_request_vertical.py` (18 test: service-level +
   HTTP-level create, 401/403, lifecycle transitions hợp lệ/không hợp lệ,
   rollback atomic trên cả 2 backend, tạo có/không `shift_id`, tạo bị từ chối
   khi shift cha đã `FROZEN`) + `tests/cvf/test_customer_request_repair.py`
   (11 test, thêm sau review độc lập thứ ba: alias-bypass rollback InMemory,
   `source_message_id` hợp lệ/không tồn tại trên cả 2 backend + HTTP không
   còn 500, `promised_at` sai định dạng trả 422 không phải 500, **domain_lock
   negative-profile test thật** — profile loại `customer_request` khỏi
   `allowed_domains` phải bị `CvfDenied(control="domain_lock")`, không có
   customer_request/audit nào được ghi). Trước bản sửa này, tuyên bố
   "domain_lock được exercise" ở `test_customer_request_vertical.py` chỉ đúng
   theo nghĩa happy-path (test dùng profile mặc định luôn cho phép
   `customer_request`) — không có test âm chứng minh việc bị từ chối khi
   domain không được phép; giờ có. Bảng `customer_requests` khớp migration
   002 CHÍNH XÁC theo parity test hai chiều (FK/CHECK/nullability/PK/type
   family/status-CHECK-values — status-CHECK giờ parametrized qua cả
   `tasks` và `customer_requests`, không còn hardcode `tasks` như bản gốc
   tuyên bố nhầm). **Khác Task có chủ đích:** migration không có cột
   `version`/`risk`/`state`/evidence cho bảng này, nên `create` KHÔNG có gate
   risk/evidence/approval — không phải thiếu sót, mà khớp đúng schema đơn giản
   hơn của domain này. `domain_lock` giờ được exercise (cả positive và
   negative) ở một domain thứ hai ngoài `create_event` (xem dòng `domain_lock`
   trong bảng dưới). `source_message_id` (FK tới `messages.message_id`) giờ
   được validate qua `Ledger.message_exists()` trước khi persist trên cả 2
   backend, trả `CvfDenied(control="reference", http_status=404)` nhất quán
   thay vì một backend chấp nhận vô điều kiện còn backend kia rò
   `IntegrityError` thành HTTP 500. **Còn hạn chế:** `messages` vẫn chưa có
   persistence vertical thật (`SqlLedger.add_message` vẫn `NotImplementedError`
   — `message_exists` chỉ là existence-check tối thiểu, không phải write
   path). identity không còn là giới hạn riêng ở đây (P2-B, 2026-07-22).

6. **Incident → report / acknowledge / transition** — `IncidentService`
   (P2A-INCIDENT-VERTICAL, 2026-07-26). Report load-bearing trên cả 2 backend
   (identity/permission/domain_lock `equipment_incident`/persist+evidence/
   audit atomic). Acknowledge (R2+) load-bearing: risk/evidence/approval tái
   dùng đúng receipt architecture của `event.confirm` — fabricated/self/
   inactive-approver/stale-version receipts đều bị từ chối trước khi
   acknowledge chạy, xác nhận bằng cả test service-level
   (`tests/cvf/test_incident_vertical.py`, 19 test) và live provider evidence
   (0 call cho refusal, 1 call sau acknowledge hợp lệ). Transition chỉ xử lý
   sau acknowledge — REPORTED bị từ chối tường minh ở tầng service, không dựa
   vào lifecycle guard (đồ thị đầy đủ vẫn cho phép REPORTED→ACKNOWLEDGED, vì
   đó là bước hợp lệ của chính `acknowledge`). PostgreSQL 16 live: bảng/enum/
   CHECK/FK/round-trip/rollback xác nhận qua
   `tests/integration/test_incident_postgres_live.py`. **Còn hạn chế:** không
   implement handovers/reports; không production endpoint nào gọi provider;
   không chứng minh managed-PostgreSQL/production readiness.

**Không domain nào trong 6 cái trên là "durable end-to-end qua HTTP + SqlLedger
+ evidence + xác thực identity thật" không giới hạn** — ngoại trừ identity, mà
P2-B (2026-07-22) đã sửa thật cho cả 5 domain (xem mục `identity` ở trên).
Evidence persistence (SqlLedger) và evidence qua HTTP (TaskInput) đã sửa ở
P-FIX-3 — không còn là giới hạn của Event/Task. Giới hạn approval hiện tại của
Event/Correction là claim boundary: receipt phải bind đúng sáu trường scope và
current authority, nhưng không production endpoint nào gọi provider; xem mục
`approval`.
`shift.close` và `customer_request` là các domain có ít giới hạn riêng nhất
tính đến 2026-07-22 (customer_request không có approval/evidence chain để
mang giới hạn "không xác thực approver" ngay từ đầu — domain này đơn giản là
không yêu cầu approval theo migration schema).

## Bảng ánh xạ

| CVF control | Trạng thái | Enforce ở đâu (file · symbol) | Giới hạn đã biết |
|---|---|---|---|
| identity | **load-bearing, governance-approved (P2-B closure, 2026-07-23)** | `dependencies.py · get_principal` giải mã/xác thực JWT bearer token qua `workspace_api/auth/tokens.py::decode_access_token` (HS256, `JWT_SECRET_KEY` bắt buộc); `POST /auth/login` (`workspace_api/auth/router.py`) cấp token sau khi kiểm username/password (bcrypt) so với bảng `users` mới | Caller không còn tự đặt header để thành principal — role luôn tới từ claim đã ký. Corrective tranche đã `REVIEW_PASS` và live Alibaba evidence PASS; xem receipt nêu trên. **Còn hạn chế:** không refresh token/revocation (access token TTL cố định, mặc định 60 phút); cấp user chỉ qua `scripts/seed_dev_users.py` (dev/test), chưa có admin flow thật. Approval là control riêng và đã được reconciliation 2026-07-26 đóng bounded trong receipt claim. Test: `tests/cvf/test_auth_tokens.py` (8 test), `tests/cvf/test_auth_login.py` (5 test), `tests/cvf/test_auth_config_secret_validation.py`, và probe hồi quy `tests/cvf/test_shift_close_governance.py::test_old_header_impersonation_no_longer_grants_any_identity`. |
| permission | callable, load-bearing cho role check | `cvf_runtime/permission.py · require_action` | Đúng vai trò tối thiểu theo action; principal đầu vào được xác thực qua JWT bởi shared `get_principal` dependency. Approval identity/quorum là control riêng với durable scope-bound receipt boundary nêu bên dưới. |
| domain_lock | callable, load-bearing tại `create_event` và `create_customer_request`, kiểm cả positive lẫn negative (2026-07-22, P2-A + repair) | `cvf_runtime/domain_lock.py · assert_event_type_in_scope` (event); `CustomerRequestService.create_customer_request · assert_domain_allowed(profile, "customer_request")` | Gắn ở `create_event` và (từ P2-A-CUSTOMER-REQUEST) `create_customer_request`; chưa gắn `create_task` hay các domain khác (Task chưa cần domain_lock vì domain `shift_operation` của nó không nằm trong nhánh event-type-mapping). Test âm thật: `tests/cvf/test_customer_request_repair.py::test_customer_request_denied_when_domain_lock_excludes_it` xây `CvfProfile` loại `customer_request` khỏi `allowed_domains`, xác nhận `CvfDenied(control="domain_lock")` và không có customer_request/audit nào được ghi — trước bản sửa này (independent review thứ ba, 2026-07-22) chỉ có test happy-path, không có test âm. |
| data_scope | callable, **không có runtime caller** | `cvf_runtime/data_scope.py · assert_placement_allowed` | `allow_after_minimization` cho phép external placement mà không yêu cầu bằng chứng đã minimize — chính sách chỉ mang tính khuyến nghị. Chưa có nơi nào trong request path gọi hàm này. |
| risk | callable | `cvf_runtime/risk.py · requirement_for` | Đọc policy đúng; không tự nó là control chặn. |
| approval | **load-bearing, governance-approved within bounded receipt claim (P2B approver reconciliation, 2026-07-26)** | JWT-protected `POST /approvals`; `workspace_api/services/approval_service.py`; `cvf_runtime/approval.py · assert_approval_satisfied`; durable receipt/intent methods on both ledgers | Caller không còn gửi approver name/role vào protected mutation. API re-derives current authority from active `users`, persists a receipt bound to `(record_type, record_id, action, target_version, risk_class, payload_digest)`, and protected actions consume only matching receipts. Deterministic order-invariant quorum matching prevents seat-order bypass; self-approval guard is enforced. `known-principals.yaml` is deleted. Task creation uses durable `TaskCreationIntent` digests; receipt/intent/mutation/audit rollback is atomic on both backends. Independent review: focused 116, full 369 pass; F16 wrong-digest probe 409; live Alibaba receipt PASS; AC-21 rehearsal PASS. **Boundary:** no production endpoint provider call, no refresh/revocation/admin provisioning, no PostgreSQL-live proof. |
| evidence | **load-bearing trên cả 2 backend (P-FIX-3, 2026-07-22)** | `cvf_runtime/evidence.py · assert_evidence_sufficient`; persistence qua `operations_ledger._evidence` (bảng `evidence_links`, map trong `tables.py`) | Sửa Critical Finding #2: trước đây `SqlLedger` không map cột evidence — event R2+ ghi evidence xong đọc lại còn 0, `confirm` bị evidence gate từ chối chính event đã có đủ evidence. Task cũng gãy tương tự qua HTTP (`TaskInput` thiếu field evidence). Cả 2 đã sửa: evidence ghi 1 lần lúc tạo (bảng riêng, giống `corrections`), đọc lại đúng; `TaskInput`/router thêm field `evidence`. Test: `tests/integration/test_evidence_persistence.py` (4 test, reproduce đúng kịch bản probe cũ của Codex) + HTTP probe xác nhận R3 task với evidence qua API trả 200. |
| audit | **load-bearing, atomic với mutation (P-FIX-2, 2026-07-22)** | `Ledger.transaction()` (unit-of-work) qua `Ledger.append_audit(record, unit=unit)` | Sửa High Finding #5: trước đây mutation commit trước, audit ghi sau trong transaction riêng — audit fail thì mutation vẫn đứng không audit. Giờ `EventService.confirm`, `CorrectionService.correct_event`, `TaskService.create_task`/`transition`, `ShiftService.freeze` đều bọc state-change + audit-append trong `transaction()`; `SqlLedger` dùng transaction SQL thật, `InMemoryLedger` snapshot/rollback (deep copy). Test: `tests/cvf/test_atomic_mutation_audit.py` (10 test, failure-injection trên `append_audit`, cả 2 backend, cả 4 service). Phát hiện phụ trong lúc sửa: `InMemoryLedger.get_event/get_task/get_shift` trước đây trả về reference sống, không phải bản sao — service mutate object trước khi vào transaction đã làm rollback vô nghĩa; đã sửa trả `model_copy()`. |
| cost | callable, AI-gated (chưa có runtime caller) | `cvf_runtime/budget.py · assert_within_budget` | Không nơi nào trong request path gọi hàm này; sẽ load-bearing khi ai-gateway wire tới. |
| refusal | callable một phần | `cvf_runtime/errors.py · CvfDenied` → HTTP map | `CvfDenied` chỉ là exception container; refusal-policy.yaml yêu cầu route tới supervisor + ghi lý do — **chưa implement**, không route, không ghi audit riêng cho refusal. |
| termination | callable, AI-gated (chưa có runtime caller) | `cvf_runtime/termination.py` | Tương tự cost — chưa có caller thật. |
| freeze | **load-bearing (P-FIX-1, 2026-07-22; `open_handover_items_linked` real từ P2A-HANDOVER-VERTICAL, 2026-07-26; `report_approved` real từ P2R-OPERATIONAL-REPORT-FREEZE-PREREQUISITE, 2026-07-30 — override RETIRED)** | `ShiftService.freeze` (identity/permission/re-read `shift_closed` → `assert_freeze_ready` thật → `report_freeze.assert_report_freeze_ready` thật (chọn đúng một current `END_SHIFT` Report APPROVED, revalidate snapshot) → `report_freeze.freeze_report` + `freeze_shift` + cả hai audit, tất cả trong một `report_freeze_transaction()` SERIALIZABLE (PostgreSQL) với bounded retry); `InMemoryLedger`/`SqlLedger` chặn mọi mutation (`add_event/put_event/add_task/put_task`) khi shift cha `FROZEN`, trừ `CorrectionService` (`allow_when_frozen=True`, đúng thiết kế "post-freeze correction record only") | Sửa Critical Finding #1: trước đây `freeze_shift` bypass hoàn toàn (HTTP probe trả `200 FROZEN` không điều kiện); giờ trả `409` cho tới khi `shift_closed` + handover thật + report thật đều sẵn sàng. Hai field override cũ chỉ còn được chấp nhận ở giá trị mặc định — bất kỳ giá trị khác trả `422`, không đọc gì thêm; OpenAPI đánh dấu `deprecated`. Test end-to-end: `tests/cvf/test_freeze_invariant.py` (cả 2 backend) + `tests/cvf/test_shift_close_freeze_interaction.py` + `tests/cvf/test_report_freeze.py` + `tests/integration/test_report_postgres_live.py` (gồm concurrent-freeze-race SERIALIZABLE). **Còn hạn chế:** chỉ report type `END_SHIFT`; idempotent frozen-read yêu cầu đúng một current Report cũng `FROZEN`, khác đi là integrity conflict 409, không phải silent success; freeze's `shift_closed` check chỉ đọc `shift.status` — nó tin đúng bằng đúng mức mà `shift.close` (dòng dưới) đáng tin. |
| report.generate / .submit_review / .approve / .create_successor | **load-bearing (P2R-OPERATIONAL-REPORT-FREEZE-PREREQUISITE, 2026-07-30)** | `ReportService.generate` (identity/permission `report.generate` role tối thiểu `operator` → yêu cầu shift `CLOSED` → derive snapshot sáu section + source_manifest + snapshot_digest → transaction atomic) / `.submit_review` (role tối thiểu `operator` → revalidate snapshot → DRAFT→IN_REVIEW atomic) / `.approve` (role tối thiểu `shift_supervisor` → revalidate → tái dùng đúng receipt architecture của `event.confirm`, risk cố định R2, receipt bind `(report_id, version, snapshot_digest)` → IN_REVIEW→APPROVED atomic) / `.create_successor` (revalidate target/lifecycle/parent, derive snapshot mới, đánh dấu bản trước `is_current=false` và chèn bản kế tiếp cùng transaction; regenerate một bản APPROVED bắt buộc role `shift_supervisor` + lý do 1-1000 ký tự) | Domain thứ tám, tái dùng đúng `cvf_runtime` gate. Test: `tests/cvf/test_report_vertical.py`, `test_report_approval.py`, `test_report_freeze.py` (cả 2 backend) + `tests/integration/test_report_ledger_parity.py` (immutable-field rejection từng trường) + `tests/integration/test_schema_parity_reports.py` (parity hai chiều migration 002+007) + `tests/integration/test_report_postgres_live.py` (live PostgreSQL 16: bảng/CHECK/UNIQUE/partial-index/round-trip/successor/rollback/concurrent-freeze). Live Alibaba evidence PASS: 0 provider call cho bảy refusal case, đúng 1 call sau generate→review→distinct-approver receipt→approve→freeze hợp lệ — receipt `docs/decisions/P2R_OPERATIONAL_REPORT_FREEZE_LIVE_EVIDENCE_RECEIPT.md`. **Còn hạn chế:** chỉ `END_SHIFT`; không P5-A rendering/export; không production endpoint nào gọi provider; PostgreSQL live bounded disposable-local. |
| shift.close | **load-bearing (P-FIX-6, 2026-07-22)** | `ShiftService.close` (identity/permission `shift.close` role tối thiểu `operator` + state-check chặn close một shift đã `FROZEN`) → `Ledger.transaction()` bọc `close_shift` + `append_audit` atomic, cùng khuôn `freeze`/`TaskService` | Sửa gap review độc lập thứ hai tìm ra 2026-07-22: `POST /shifts/{shift_id}/close` trước đây gọi thẳng `ledger.close_shift(shift_id)` từ router — không `get_principal`, không `require_action`, không audit; probe xác nhận `anonymous_close=200`, `audit_count=0`. Vì freeze chỉ kiểm `shift.status == CLOSED`, close vô danh đó có thể âm thầm thỏa mãn tiền đề `shift_closed` của freeze. Test: `tests/cvf/test_shift_close_governance.py` (13 test: 401 vô danh, 403 role thấp, 200 + audit cho principal hợp lệ, rollback atomic khi audit fail trên cả 2 backend, chặn close shift đã FROZEN, chuỗi đầy đủ create→close có governance→freeze qua cả service lẫn HTTP). **Không** đụng tới approval/known-principals (High Finding #4) — ngoài phạm vi tranche này. |
| customer_request.create / .transition | **load-bearing (P2-A-CUSTOMER-REQUEST, 2026-07-22; repaired after independent review, 2026-07-22)** | `CustomerRequestService.create_customer_request` (identity/permission `customer_request.create` role tối thiểu `operator` → `domain_lock` `customer_request` → `source_message_id` existence check qua `Ledger.message_exists()` khi được cung cấp → frozen-shift check chỉ khi `shift_id` được cung cấp → `Ledger.transaction()` bọc `add_customer_request` + `append_audit` atomic) / `.transition` (identity/permission `customer_request.transition` → `assert_customer_request_transition` lifecycle guard → transaction atomic) | Domain thứ năm nhân bản cùng khuôn `TaskService`/`ShiftService`. **Không có** risk/evidence/approval gate cho create — `customer_requests` không có cột `risk`/`state`/evidence trong migration 002, nên chain này ngắn hơn Task/Event có chủ đích, không phải thiếu sót. Test: `tests/cvf/test_customer_request_vertical.py` (18 test: service+HTTP create, 401/403, lifecycle hợp lệ/không hợp lệ bao gồm WAITING không được nhảy thẳng CLOSED, CLOSED terminal, rollback atomic cả 2 backend, tạo có/không `shift_id`, tạo bị chặn khi shift cha FROZEN) + `tests/cvf/test_customer_request_repair.py` (11 test: InMemory alias-bypass, `source_message_id` hợp lệ/không tồn tại trên cả 2 backend + HTTP không còn 500, `promised_at` sai định dạng trả 422, domain_lock negative-profile thật). **Sửa sau independent review 2026-07-22:** InMemoryLedger từng lưu/trả về CHÍNH object mutable của caller cho `add/get/put_customer_request` — `created.status = CLOSED` có thể âm thầm đổi state đã lưu, không qua permission/lifecycle/transaction/audit; giờ trả bản `model_copy()` giống mọi entity khác. `source_message_id` từng được kiểm không nhất quán: InMemory chấp nhận vô điều kiện, SqlLedger/SQLite raise `IntegrityError` từ FK không được bắt, có thể lộ ra HTTP 500; giờ validate qua `message_exists()` trước khi persist trên cả 2 backend, trả `CvfDenied(control="reference", http_status=404)` nhất quán. Router's `promised_at` từng khai `str | None`, giá trị sai định dạng chỉ fail khi construct `CustomerRequest(...)` trong route (ValidationError không được router bắt) → lộ HTTP 500; giờ khai `datetime | None` trên `CustomerRequestInput` để Pydantic reject ở request-boundary, trả 422. **Còn hạn chế:** `messages` vẫn chưa có persistence vertical thật; identity không còn là giới hạn ở đây (P2-B, 2026-07-22). |
| incident.report / .acknowledge / .transition | **load-bearing (P2A-INCIDENT-VERTICAL, 2026-07-26)** | `IncidentService.report` (identity/permission `incident.report` role tối thiểu `operator` → `domain_lock` `equipment_incident` → `Ledger.transaction()` bọc `add_incident` + `append_audit` atomic, evidence persist qua `evidence_links`) / `.acknowledge` (identity/permission `incident.acknowledge` role tối thiểu `shift_supervisor` → risk/evidence từ Incident đã persist → `approval_service.collect_receipts_for`/`assert_approval_satisfied` tái dùng đúng receipt architecture của `event.confirm` → `assert_incident_transition` REPORTED→ACKNOWLEDGED → transaction atomic) / `.transition` (identity/permission `incident.transition` → từ chối tường minh khi status còn REPORTED → `assert_incident_transition` cho phần đồ thị còn lại → frozen-parent check → transaction atomic) | Domain thứ sáu, tái dùng đúng `cvf_runtime` gate — không fork logic permission/risk/evidence/approval/audit. Report tức thời (không chờ quorum); chỉ acknowledge là quyết định được bảo vệ R2+. Test: `tests/cvf/test_incident_vertical.py` (19 test: report/acknowledge/transition ở tầng service lẫn HTTP, permission 403, frozen-shift chặn, insufficient-evidence/fabricated/self-approval/inactive-approver/stale-version receipt đều bị từ chối, acknowledge hợp lệ với approver khác biệt, transition chặn REPORTED và frozen shift) + `tests/integration/test_sql_ledger_incidents.py` (9 test persistence/atomicity) + `tests/integration/test_schema_parity_incidents.py` (8 test parity hai chiều với migration 005) + `tests/integration/test_incident_postgres_live.py` (7 test live PostgreSQL 16: bảng/enum/CHECK/FK/round-trip/rollback). Live Alibaba evidence PASS: 0 provider call cho mọi refusal, đúng 1 call sau acknowledge hợp lệ — receipt `docs/decisions/P2A_INCIDENT_LIVE_EVIDENCE_RECEIPT.md`. **Còn hạn chế:** không production endpoint nào gọi provider; PostgreSQL live bounded ở disposable-local, không phải production/managed readiness. |
| handover.create / .review / .acknowledge | **load-bearing (P2A-HANDOVER-VERTICAL, 2026-07-26; HOV-AUTH-F4 repair)** | `HandoverService.create` (identity/permission `handover.create` role tối thiểu `operator` → `domain_lock` `shift_handover` → server tự derive `items` từ đúng open-work set của shift nguồn, mỗi item mang SHA-256 digest chuẩn tắc → `Ledger.transaction()` bọc `add_handover` + `append_audit` atomic) / `.review` (role tối thiểu `shift_supervisor` → revalidate destination OPEN/source not-FROZEN + khớp snapshot → `assert_handover_transition` DRAFT→REVIEWED → transaction atomic) / `.acknowledge` (role tối thiểu `shift_supervisor`, receiver PHẢI khác reviewer → revalidate lại state/snapshot → `assert_handover_transition` REVIEWED→ACKNOWLEDGED → transaction atomic) | Domain thứ bảy, tái dùng đúng `cvf_runtime` gate. `ShiftService.freeze`'s `open_handover_items_linked` giờ gọi `assert_freeze_ready` thật (không còn override được) trong CÙNG transaction với freeze mutation và audit. Test: `tests/cvf/test_handover_vertical.py` (service+HTTP: lifecycle matrix, permission 403, distinct-receiver, stale/new snapshot rejected, shift-state recheck tại create/review) + `tests/cvf/test_freeze_invariant.py`/`test_shift_close_freeze_interaction.py` (freeze chỉ thành công sau handover ACKNOWLEDGED thật) + `tests/integration/test_sql_ledger_handovers.py` (9 test persistence/atomicity) + `tests/integration/test_schema_parity_handovers.py` (15 test parity hai chiều với migration 006, gồm native enum `handover_status`) + `tests/integration/test_handover_postgres_live.py` (9 test live PostgreSQL 16). Live Alibaba evidence PASS: 0 provider call cho 4 refusal case (thiếu handover, chỉ REVIEWED, tự acknowledge, snapshot cũ), đúng 1 call sau review+acknowledge+freeze hợp lệ qua route HTTP/JWT thật — receipt `docs/decisions/P2A_HANDOVER_LIVE_EVIDENCE_RECEIPT.md`. HOV-AUTH-F4: `test_atomic_mutation_audit.py`/`test_customer_request_vertical.py`'s freeze-adjacent fixtures giờ dựng handover thật thay vì dựa vào override đã bị thu hẹp. **Còn hạn chế:** không có registry gán nhân sự nên acknowledge không tuyên bố nhân sự được gán ca đích; `OperationalEvent` cố ý ngoài tập open-work bắt buộc (chưa có ngữ nghĩa open/resolved); không implement reports; không production endpoint nào gọi provider; PostgreSQL live bounded ở disposable-local. |
| shifts.list / events.list / shifts.open-work (read) | **load-bearing, identity-only, governance-approved within the P2C C3a read-surface boundary (2026-07-29)** | `dependencies.py · get_principal` bắt buộc JWT bearer hợp lệ trên `GET /shifts`, `GET /events?shift_id=...` (`workspace_api/api/events/router.py · list_events`, ủy quyền `SqlLedger.list_events_for_shift` → `_event_queries.list_events_for_shift` cho SQL backend), và `GET /shifts/{shift_id}/open-work` (`workspace_api/api/shifts/router.py · get_open_work`, tái dùng nguyên `Ledger.open_work_snapshot`) | Đây là **identity-only read admission** — principal hợp lệ được đọc, KHÔNG kiểm per-shift assignment, tenant isolation hay `data_scope`. `GET /shifts`, `GET /events` và từng open-work group có trần cứng 500 record, đã chứng minh trên InMemory, SQLite và disposable PostgreSQL 16 qua HTTP/API/ledger path thật; event ordering tất định và evidence được giữ nguyên; open-work reuse canonical snapshot và canonical schemas. Live governance receipt `docs/decisions/P2C_READ_LIVE_EVIDENCE_RECEIPT.md` ghi `Overall outcome: PASS`: bốn refusal case đều zero provider calls, admitted JWT reads PASS, sau đó đúng một Alibaba call thật trả HTTP 200. Production read endpoint **không gọi provider AI**; provider call chỉ là governance evidence. `POST /shifts` từng không có JWT (`P2C-DESIGN-F1 UNGOVERNED_SHIFT_CREATE`) — đã đóng bounded bởi `shift.create` dòng dưới (SHIFT-CREATE-ADMISSION-REPAIR-2026-07-29). Evidence: `tests/integration/test_p2c_read_api.py`, `tests/integration/test_p2c_read_postgres_limit_live.py`, `tests/integration/test_p2c_read_ledger_parity.py`, `tests/unit/test_p2c_read_openapi_contract.py`, `tests/unit/test_p2b_openapi_contract.py`, `tests/contract/test_contract_files.py`, `tests/integration/test_sql_ledger_postgres_live.py`. **Giới hạn:** không thay đổi permission/data-scope model; PostgreSQL proof chỉ bounded disposable-local, không phải production readiness. |
| shift.create | **load-bearing (SHIFT-CREATE-ADMISSION-REPAIR-2026-07-29)** | `ShiftService.create` (identity/permission `shift.create` role tối thiểu `operator` → construct canonical `Shift` (server-derived `shift_id`/`status=OPEN`/`version=1`) → `Ledger.transaction()` bọc `create_shift` + `append_audit` atomic, cùng khuôn `close`/`freeze`) | Sửa gap `P2C-DESIGN-F1`/INTAKE probe: `POST /shifts` trước đây gọi thẳng `ledger.create_shift(...)` từ router — không `get_principal`, không `require_action`, không audit; probe xác nhận `ANONYMOUS_SHIFT_CREATE status=200`. Query contract (`name`/`starts_at`/`ends_at`) và canonical `Shift` response giữ nguyên; OpenAPI delta chỉ thêm bearer security lên `POST /shifts`. Test: `tests/cvf/test_shift_create_admission.py` (401 vô danh/malformed token, 403 viewer, 200+audit cho operator/vai trò cao hơn, 422 window sai, router không gọi ledger trực tiếp, rollback atomic cả 2 backend) + `tests/integration/test_shift_create_sqlite.py` (record trả về khớp record đã lưu, sống sót reconnect) + `tests/integration/test_shift_create_postgres_live.py` (4 test live PostgreSQL 16: create/audit/reconnect/rollback + usable connection) + `tests/unit/test_shift_create_openapi_contract.py`. Live Alibaba evidence PASS: 0 provider call cho 4 refusal case (vô danh, malformed token, viewer, window sai), đúng 1 call sau create hợp lệ qua route HTTP/JWT thật — receipt `docs/decisions/SHIFT_CREATE_ADMISSION_REPAIR_LIVE_EVIDENCE_RECEIPT.md`. **Còn hạn chế:** message admission (`POST /messages`) từng vô danh — đã đóng bounded bởi `message.create` dòng dưới (MESSAGE-ADMISSION-TRUST-REPAIR-2026-07-30, chỉ nội bộ); không assignment/tenant/data_scope; PostgreSQL live bounded disposable-local. |
| message.create | **load-bearing, internal-user only (MESSAGE-ADMISSION-TRUST-REPAIR-2026-07-30)** | `MessageService.create` (verify optional legacy sender/source assertion trước bất kỳ permission check nào → identity/permission `message.create` role tối thiểu `operator` → construct canonical internal `Message` (server-derived `sender_id=principal.user_id`, `source="INTERNAL"`, `state=RAW`) → `Ledger.transaction()` bọc `add_message` + `append_audit` atomic, cùng khuôn `shift.create`) | Sửa gap `MAR-INTAKE-F1/F2`: `POST /messages` trước đây vô danh, chấp nhận `sender_id`/`source` do caller cung cấp làm authority (probe: `ANONYMOUS_MESSAGE_CREATE status=200`, `sender_id="forged-executive"` được chấp nhận nguyên vẹn); `SqlLedger.add_message` từng raise `NotImplementedError`. Body JSON giữ `shift_id`/`text` bắt buộc; `sender_id`/`source` chuyển thành optional assertion KHÔNG BAO GIỜ là authority — sai khác bị từ chối (403 sender mismatch, 422 non-INTERNAL source), không có ghi nào xảy ra. Unknown shift → 404; FROZEN shift → 409; OPEN/HANDOVER_PENDING/CLOSED đều chấp nhận message append-only RAW. Test: `tests/cvf/test_message_admission.py` (401/403/422/404/409, router không gọi ledger trực tiếp, rollback atomic cả 2 backend, returned-vs-persisted cả 2 backend) + `tests/integration/test_message_sqlite.py` (SQLite reconnect, duplicate/evidence refusal, InMemory deep-copy isolation, customer-request source reference qua public path) + `tests/integration/test_message_postgres_live.py` (7 test live PostgreSQL 16 qua route HTTP/JWT thật: create/audit/reconnect/raw_payload NULL/rollback/frozen/duplicate/usable connection) + `tests/unit/test_message_openapi_contract.py`. Live Alibaba evidence PASS: 0 provider call cho 7 refusal case (vô danh, malformed token, viewer, sender mismatch, non-INTERNAL source, unknown shift, frozen shift), đúng 1 call sau create hợp lệ với exact-field-matched audit — receipt `docs/decisions/MESSAGE_ADMISSION_TRUST_REPAIR_LIVE_EVIDENCE_RECEIPT.md`. **Còn hạn chế:** external/channel message ingestion (Integration Edge) vẫn hoàn toàn chưa xây — provider payload/canonical envelope KHÔNG BAO GIỜ được vào route này; Canonical Message Contract chưa tương đương với model nội bộ; không assignment/tenant/data_scope; PostgreSQL live bounded disposable-local. |
| shift.assignment.manage | **load-bearing, single-workspace assignment foundation (P2C-MUTATION-FULL-UI-C3A1, 2026-07-31)** | `AssignmentService.assign`/`.revoke` (identity/permission `shift.assignment.manage` role tối thiểu `shift_supervisor` → target-user persisted-active check → `Ledger.transaction()` bọc `add_assignment`/`revoke_assignment` + `append_audit` atomic); `ShiftService.create` giờ atomically gán ACTIVE assignment cho creator cùng transaction với shift + audit; `GET /auth/me` trả verified `user_id`/`role`/token expiry thật; `GET /shifts/{shift_id}/capabilities` yêu cầu ACTIVE assignment, trả advisory action list + bounded reason, không lộ digest/credential/policy internal | `ShiftAssignment`/`AssignmentStatus` package-owned, không có trường tenant hay `data_scope` (ADR mục 3/4.1). Migration 008 không suy diễn/backfill assignment cho shift cũ — supervisor phải dùng staffing control plane để gán. Revoke tăng version đúng một lần, lặp lại ở version hiện tại (đã revoke) là idempotent không audit thứ hai, lặp lại ở version cũ trả 409. Evidence không dùng count dễ stale: `tests/cvf/test_assignment_foundation.py` + companion `test_assignment_foundation_f1.py` chứng minh bootstrap/staffing/session/JWT-exp/capabilities; `tests/unit/test_assignment_model.py` và `test_assignment_openapi_contract.py` giữ model/OpenAPI; `tests/integration/test_assignment_ledger_parity.py` + companion `test_assignment_ledger_parity_f1.py` chứng minh InMemory/SQLite reference, duplicate-id/active, CAS, strict domain/lifecycle parity và no-partial-write; `tests/integration/test_schema_parity_assignments.py` giữ parity migration 008; `tests/integration/test_assignment_postgres_live.py` + companion `test_assignment_postgres_live_f1.py` chứng minh cùng contract trên disposable PostgreSQL 16, gồm concurrency one-winner/one-audit. Live Alibaba evidence PASS: 0 provider call cho 3 refusal case (vô danh, operator không đủ quyền staffing, capabilities thiếu assignment), đúng 1 call sau genuine durable staffing assignment + exact-field-matched audit qua route HTTP/JWT thật — receipt `docs/decisions/P2C_C3A1_ASSIGNMENT_LIVE_EVIDENCE_RECEIPT.md`. **Còn hạn chế:** KHÔNG enforce assignment scope trên route operational hiện có (C3a2, chưa build); không tenant/data_scope claim; không frontend mutation; PostgreSQL live bounded disposable-local. |

## Thứ tự chain trong `EventService.confirm` (thiết kế — chưa phải bảo đảm runtime)

**Lưu ý:** sơ đồ dưới đây là snapshot lịch sử từ trước các tranche P-FIX; chỉ
dòng `identity` được cập nhật ở đây (P2-B, 2026-07-22). Các dòng khác
(freeze/state, evidence, audit) mô tả trạng thái TRƯỚC P-FIX-1/2/3 và đã lỗi
thời — trạng thái đúng hiện tại nằm ở "Golden verticals — phạm vi chính xác"
phía trên, không phải sơ đồ này.

```text
identity        (dependency: get_principal — xác thực thật qua JWT bearer
                 token, P2-B 2026-07-22; xem bảng trên)
   ↓
permission      (require_action "event.confirm")
   ↓
freeze/state    (assert_transition: PROPOSED → CONFIRMED — KHÔNG kiểm shift cha)
   ↓
evidence        (assert_evidence_sufficient — gãy trên SqlLedger)
   ↓
approval        (assert_approval_satisfied — KHÔNG xác thực approver)
   ↓
[mutation]      (state = CONFIRMED, version += 1)
   ↓
audit           (KHÔNG atomic với bước mutation ở trên)
```

## Việc cần làm trước khi dùng lại nhãn "enforced"/"12/12"

Xem `docs/implementation/EXECUTION_ROADMAP.md` các tranche `P-FIX-*`. Tóm tắt:
sửa freeze thành bất biến xuyên-record thật, gộp mutation+audit atomic, lưu
evidence qua SqlLedger + xác thực approval server-side, sửa migration Task và
siết parity test, sửa catalog `--check` và đồng bộ toàn bộ front door, và
(P-FIX-6) đóng gap `shift.close` vô danh không qua governance.

**Trạng thái sau P-FIX-6:** `P-FIX CLOSED_BOUNDED` — bounded nghĩa là: mọi gap
Critical/High mà 2 review độc lập tìm ra tới nay đã có test end-to-end xác
nhận, nhưng KHÔNG có nghĩa "tất cả High Finding đã sửa xong". High Finding #4
sau đó đã được đóng bounded bởi P2B approver reconciliation 2026-07-26; các
giới hạn khác chưa sửa được liệt kê trong
`SESSION/ACTIVE_SESSION_STATE.json` `blocked_work` và
`IMPLEMENTATION_STATUS.json`). **2026-07-22 (P2-B):** identity đã chuyển từ
header-based sang xác thực thật qua JWT — không còn ở danh sách này. Vẫn còn
mở: data minimization chỉ mang tính khuyến nghị; `data_scope`/`cost`/
`termination` chưa có runtime caller; refusal routing/recording chưa
implement; PostgreSQL chưa live verified; refresh/revocation/admin provisioning
chưa có. Không viết
"tất cả High Finding đã sửa" ở bất kỳ đâu.

## C3a2 — route-wide operational assignment enforcement (P2C-MUTATION-FULL-UI-C3A2)

`assignment_scope.py` (`AssignmentScope.require_shift`/`.require_record`,
module-level `require_active_assignment`/`assigned_shifts`) là guard duy nhất
cho ACTIVE-membership: resolve shift từ record đã persist (không bao giờ tin
`shift_id` do caller cung cấp trong body khi record đã tồn tại), rồi yêu cầu
`Ledger.get_active_assignment` trả về khác `None`. Guard này được TẤT CẢ route/
service của R6 (shift list/open-work/close/freeze, message create, event
create/list/confirm/correct, task creation-intent create/get, task create/
transition, customer-request có `shift_id` create/transition, incident report/
get/list/acknowledge/transition, handover create/get/list/review/acknowledge,
report generate/get/list/version/submit/approve, approval receipt cho
supported shift-bound target) gọi trước khi cho phép đọc hoặc ghi — không
router/service nào tự viết lại logic assignment riêng.

Thiếu hoặc không có ACTIVE assignment đều raise `OperationalResourceNotFound`
(subclass của `KeyError`), router bắt qua `except KeyError` và trả 404 —
CÙNG status và CÙNG hình dạng body cho record không tồn tại lẫn record tồn tại
nhưng caller không có assignment (enumeration-safe, không rò rỉ khác biệt).
Handover create/review đòi assignment trên shift NGUỒN; acknowledge đòi
assignment trên shift ĐÍCH — assignment chỉ ở phía còn lại không đủ. Approval
receipt resolve target shift từ record đã lưu (event/incident/report/creation
intent), không bao giờ từ record type/id hay scope do caller khẳng định.
`POST /shifts` giữ nguyên ngoại lệ bootstrap R4 (chưa có assignment nào để
đòi); login/health/staffing control-plane nằm ngoài phạm vi đọc operational
resource; customer-request không có `shift_id` (null-shift) nằm ngoài shift
console nên không mang assignment claim.

Test: `tests/cvf/test_assignment_scope_routes.py` (ma trận R6 đầy đủ qua HTTP),
`tests/cvf/test_assignment_scope_cross_shift.py` (quy tắc nguồn/đích và
stored-target), `tests/cvf/test_assignment_scope_enumeration.py` (401/403 giữ
nguyên, 404 giống hệt giữa missing/inaccessible, list chỉ trả record được gán,
refusal xảy ra trước mọi mutation/audit) +
`tests/integration/test_assignment_scope_postgres_live.py` (cùng hành vi trên
PostgreSQL 16 thật qua `SqlLedger`, opt-in `LIVE_POSTGRES_DATABASE_URL`). Live
governance evidence: `scripts/run_assignment_scope_live_governance_evidence.py`
— refusal case tại 0 provider call, một genuine ACTIVE-assignment-admitted
operation thật qua route HTTP/JWT, rồi đúng một Alibaba call — receipt
`docs/decisions/P2C_C3A2_ASSIGNMENT_SCOPE_LIVE_EVIDENCE_RECEIPT.md`. **Còn hạn
chế:** không đổi assignment schema/lifecycle/staffing (đó là C3a1, zero-diff ở
đây); không tenant/data_scope; không frontend mutation; PostgreSQL live vẫn
bounded disposable-local.

**2026-08-01 P2-C C3b1 (browser read/readiness contract) — không thêm CVF
`required_control` mới.** `GET /messages`, `GET /tasks`, `GET
/customer-requests` chỉ tái dùng đúng guard `require_active_assignment` đã có
sẵn ở trên (verified authentication rồi ACTIVE assignment, không phát minh
read-action permission mới). `GET /approvals/readiness`
(`workspace_api.application.approval_readiness.evaluate_readiness`) là READ,
không phải authorization gate: nó áp coarse `require_action` của action được
yêu cầu, resolve target/shift/version/risk/digest từ stored truth (không nhận
version/risk/digest do caller khai), rồi kiểm ACTIVE assignment, dùng
deterministic maximum bipartite matching trên authority hiện tại (không tin
role lưu trong receipt cũ) — nhưng `ready=true` không authorize hay dự đoán
lifecycle; mutation thật (`approval_receipts.create_approval_receipt`) vẫn
chạy lại toàn bộ gate độc lập, bao gồm cả confirmer/self-approval rule mà
readiness cố ý không áp. Không lộ payload digest, receipt id, approver
identity hay policy internals trong response. C3b1 không gọi provider — claim
governance boundary giữ nguyên như đã ghi ở C3a2 phía trên; không mở rộng sang
mutation/CustomerRequest version (C3b2), React UI (C3c/C3d), tenant/data_scope
hay Phase 2 completion.

**2026-08-01 P2-C C3b2 (CustomerRequest version + mutation preconditions) —
không thêm CVF `required_control` mới; đây là tightening một invariant đã
tồn tại (optimistic concurrency), không phải governance gate mới.**
`CustomerRequest` giờ có `version` (migration 009, backfill 1, CHECK `>= 1`),
theo đúng khuôn mẫu `Task`/`Report`/`Shift`/`Incident`/`Handover` đã có từ
trước; `CustomerRequestService.transition` dùng compare-and-swap atomic
(`transition_customer_request`) thay vì read-then-put. Tám route/service
entry point (shift close/freeze; event confirm; correction; task transition;
CustomerRequest transition; incident acknowledge/transition; handover
review/acknowledge; Report submit-review/approve/version-successor) giờ yêu
cầu `expected_version` (Report còn thêm `expected_status`) — so sánh diễn ra
SAU permission/assignment admission nhưng TRƯỚC lifecycle/quorum, trong CÙNG
transaction với mutation và audit, theo `mutation_preconditions.
assert_version_precondition`/`assert_status_precondition` dùng chung.
Thiếu precondition ở HTTP boundary là 422 do Pydantic (`extra=forbid`, field
required); thiếu ở direct-service boundary cũng là 422 có kiểm soát qua
`CvfDenied`, không permissive default, không caller-derived current value.
Version/status cũ (stale) là 409 có kiểm soát, zero domain/audit/receipt
write khi rollback. `TaskService.transition` và `IncidentService.transition`
trước đây đọc rồi mutate NGOÀI `ledger.transaction()` — C3b2 sửa cả hai vào
trong transaction (điểm đúng theo Work Order review finding C3B2-WO-REV-F2),
đóng một lỗ atomicity thật chứ không chỉ thêm field. Route
create/append/task-intent/approval-receipt (protected boundary) giữ nguyên
contract cũ tuyệt đối — `EventInput`/`CustomerRequestInput` vẫn không khai
`extra=forbid` (pre-existing, không liên quan C3b2, không "sửa"), field lạ
vẫn bị silently drop như trước; các route khác đã có `extra=forbid` từ trước
tiếp tục reject field lạ với 422 như cũ. OpenAPI delta chỉ đúng 9 schema bị
tighten cộng 2 schema mới cộng 3 route thêm requestBody — golden-hash chain
(`test_c3b2_mutation_openapi_contract.py`) strip lại đúng delta này để chứng
minh cấu trúc, không chỉ so text. C3b2 không gọi provider, không claim AI/
agent-governance mới — boundary giữ nguyên như C3a2/C3b1 phía trên; không mở
rộng sang React mutation UI (C3c/C3d), offline/realtime (P2-D), tenant/
data_scope hay Phase 2 completion. Amendment 1 (2026-08-01) thêm đúng một
path ngoài ceiling gốc — `tests/integration/test_handover_live_evidence_
runner.py` — vì regression cũ của nó dùng default `expected_version=1` của
runner, khiến freeze fail vì stale version thay vì đến đúng Report gate;
default đó đã bị xoá khỏi `run_handover_live_governance_evidence.py`
(`expected_version` giờ bắt buộc, keyword-only), test đã thread version thật
từ mỗi response qua review/acknowledge/close/freeze.

**2026-08-01 P2-C C3c (operator mutation UI) — không thêm CVF `required_control` mới.**
Thêm giao diện React cho các thao tác của operator (shift create/close, internal message append, event create, task intent/create và transition, customer request create/transition, incident report/transition, handover create, report generate/version/submit). Mọi thao tác đều gọi API backend thật, dùng token JWT của principal đã đăng nhập, re-fetch dữ liệu sau thành công/xung đột, và khóa nút gửi (outcome_unknown) khi có sự cố mạng chưa xác định được kết quả (yêu cầu refresh trước khi gửi lại). Không dùng queue offline/storage/background retry (thỏa mãn SPEC R19/R20).

**2026-08-01 P2-C C3c independent BUILD review round 1 — `REVIEW_FAIL`, sáu
finding (F1 exact-set false 35/38, F2 backend contract drift, F3 mutation
state broken, F4 operator lifecycle false controls, F5 browser evidence
underproves R18, F6 harness cleanup/regression), tất cả sửa không waiver
trong đúng ceiling 38-path. Chi tiết đầy đủ + repair từng finding nằm trong
receipt `docs/decisions/P2C_C3C_BUILD_EVIDENCE_RECEIPT.md` §1 (giữ nguyên
lịch sử, không rút gọn ở đó).**

**2026-08-02 P2-C C3c independent BUILD review round 2 — `REVIEW_FAIL`, ba
finding còn lại sau round 1, tất cả sửa không waiver, vẫn đúng ceiling 38-path
(0 ngoài, 0 staged). Chi tiết đầy đủ nằm trong receipt §1a:**

- `REREV-F1 REFRESH_COMPLETION_STILL_FALSE`: `refresh()`/`refreshShifts()`
  trả `void` (chỉ tăng state key hoặc nuốt lỗi), nên `refreshAndUnlock()` mở
  khoá trước khi read nào thật sự xong; conflict chỉ chờ người bấm, không tự
  refresh. Sửa: `useOperationsData` tách fetch thành `load()` dùng chung bởi
  effect và `refresh()` — `refresh()` giờ `Promise<void>` chỉ resolve sau khi
  mọi read + capabilities commit thật, vẫn giữ `requestToken`/`AbortSignal`;
  `refreshShifts`/`onRefresh` gộp đều `Promise<void>`, hết `.catch(() => {})`;
  mọi `onRefresh` prop trong cây operator-actions đổi `() => Promise<void>`.
  `useMutationControl(fn, refresh)` nhận `refresh` bắt buộc: thành công await
  trước khi `success`; conflict tự khởi động đúng một `refresh()` (thành công
  → `conflict_resolved` mở khoá nhưng vẫn hiện thông điệp conflict để xem giá
  trị mới; thất bại → giữ khoá, nút refresh thủ công); `outcome_unknown`
  không bao giờ tự refresh. Test mới dùng promise điều khiển được để chứng
  minh: refresh chưa xong chưa mở khoá, refresh reject vẫn khoá, conflict chỉ
  gọi refresh đúng một lần.
- `REREV-F2 BROWSER_MATRIX_STILL_INCOMPLETE`: mở rộng đúng hai spec/helper đã
  duyệt, không thêm path. `operator-flow.spec.ts` thêm successor-version thật
  qua UI (version 2/DRAFT trước khi submit IN_REVIEW) và kịch bản Incident:
  report qua UI operator, JWT supervisor thật (`sup1`) chỉ để tự gán ca rồi
  gọi thật `POST /incidents/{id}/acknowledge` làm test arrangement (không
  render/assert như control operator), reload UI thật rồi chứng minh control
  transition chỉ hiện MITIGATING/RESOLVED, không nút Acknowledge, transition
  MITIGATING qua UI. `operator-flow-accessibility.spec.ts` thay one-in-flight
  cũ bằng `form.requestSubmit()` hai lần đồng bộ chứng minh `inFlight` ref
  chặn lần hai, đếm POST thật qua `page.route`; thêm outcome_unknown dùng
  `context.setOffline(true)` thật, xác nhận không tự thử lại, rồi
  `setOffline(false)` + bấm Refresh thật, chỉ mở khoá sau GET thật thành
  công, tổng POST vẫn đúng 1. Risk R2 cho Incident từng bị 409 vì evidence-
  policy.yaml yêu cầu >=1 evidence cho R2+ trước acknowledge — đổi sang R1.
- `REREV-F3 REPORT_DTO_AND_RECEIPT_OVERCLAIM`: `sections`/`source_manifest`
  vẫn `unknown[]`; `operatorApi.ts` nhận `string` thô dù đã có type union
  chính xác. Sửa: `backendContracts.ts` thêm `ReportSourceRef {record_type,
  record_id, source_version, source_digest}` và `ReportSection {section_type,
  records}` khớp đúng `report_models.py` (không phải client sinh tự động);
  `records` giữ `Record<string, unknown>` cộng `record_type`/`record_id` vì
  backend tự khai `list[dict]` không đồng nhất — đóng chặt hơn sẽ overclaim.
  `operatorApi.ts` mọi tham số đổi `OperationalEventType`/`RiskClass`/
  `TaskStatus`/`CustomerRequestStatus`/`IncidentStatus`/`ReportStatus`. Test
  mới dùng section/manifest đúng shape thật, không còn `{title}` giả.
**2026-08-02 P2-C C3c final repairs.** Round-4 sửa saved-but-unconfirmed thành locked/manual-refresh-only, không auto-retry. Independent final review sau đó tìm Report UI matrix sai và thiếu AC-29: sửa đúng `DRAFT=version+submit`, `IN_REVIEW=version`, `APPROVED/FROZEN=no operator mutation`, thêm four-row test; detached exact-parent `b17a8cb...` rehearsal PASS và cleanup path/registration hoàn tất. Codex không gọi Claude CLI/MCP/provider; receipt trả `READY_FOR_INDEPENDENT_P2C_C3C_BUILD_FINAL_RE_REVIEW`.
