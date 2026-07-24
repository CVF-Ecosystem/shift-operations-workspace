# Session Memory

Human companion to [`ACTIVE_SESSION_STATE.json`](ACTIVE_SESSION_STATE.json).
Provider-neutral — for every agent and human. Keep it short; details live in the
handoffs.

_Last updated: 2026-07-24 (XR1S-RECIPROCAL-WORKSPACE-LINK-2026-07-24: authorization repaired round 1, pending independent re-review)_

## Where the project is

Repo bắt đầu là **blueprint trung thực nhưng CVF controls chỉ nằm trên giấy**
(xem `docs/decisions/EA_INDEPENDENT_REVIEW_2026-07-21.md`). Qua các phiên
buildout, CVF controls được đưa vào code + test, và một **review độc lập thứ
hai** (`docs/decisions/EA_INDEPENDENT_REVIEW_2026-07-22_CODEX.md`) chứng minh
bằng probe chạy thật rằng nhiều tuyên bố của các phiên đó — "12/12 enforced",
"golden vertical durable", "PostgreSQL same code path" — **đã over-claim**.
Freeze bypass được, evidence mất trên SqlLedger, approval là tự khai, audit
không atomic, migration Task thiếu cột `version`. Đây là bằng chứng đúng thứ
CVF được thiết kế để bắt: không một agent nào (kể cả agent đã build) được tin
tuyệt đối lời tự khai của chính nó.

**2026-07-22 (P-FIX-6):** một agent tuyên bố tranche P-FIX **CLOSED** sau
P-FIX-5. Một review độc lập **thứ hai** bác bỏ tuyên bố đó: `POST
/shifts/{shift_id}/close` vẫn gọi thẳng `ledger.close_shift()` từ router —
không identity, không permission, không audit (probe: `create=200`,
`anonymous_close=200`, `status=CLOSED`, `audit_count=0`). Vì
`ShiftService.freeze` chỉ kiểm `shift.status == ShiftStatus.CLOSED`, close vô
danh đó có thể âm thầm thỏa mãn tiền đề `shift_closed` của freeze — đúng loại
bypass CVF được thiết kế để bắt, xảy ra ngay trong chính tranche tuyên bố đã
sửa hết các bypass đó. Bài học lặp lại: front-door "CLOSED" là tuyên bố của
agent, không phải bằng chứng — luôn verify bằng probe/test thật trước khi tin.
P-FIX-6 thêm `shift.close` làm governed action thật và sửa toàn bộ front-door
drift bên dưới. Trạng thái đúng bây giờ là **`P-FIX CLOSED_BOUNDED`** — xem
"Không được làm" bên dưới cho danh sách giới hạn vẫn còn treo (KHÔNG phải "tất
cả High Finding đã sửa").

**2026-07-22 (P2-A-CUSTOMER-REQUEST):** với P-FIX đã đóng bounded, operator
mở lại Phase 2 roadmap, chỉ định P2-A: nhân bản CVF chain sang domain thứ năm
— `customer_request`. Đã nhân bản đúng khuôn `TaskService`/`ShiftService`:
`CustomerRequest` model + `CustomerRequestStatus` lifecycle, bảng
`customer_requests` map vào `tables.py` (khớp migration 002 hai chiều qua
schema-parity test), `add/get/put_customer_request` trên cả Protocol/
InMemoryLedger/SqlLedger, `CustomerRequestService` (create: identity→
permission→domain_lock→persist(frozen-shift check chỉ khi có shift_id)→audit;
transition: identity→permission→lifecycle guard→persist→audit), router
`/customer-requests`, 18 test mới. **Chính xác về phạm vi:** P2-A
(customer_request) đã xong; P2-A (incidents, handovers) VẪN còn mở — 2 domain
đó chưa có bảng migration, cần migration mới trước. Không tuyên bố "P2-A đã
đóng" chung chung.

**2026-07-22 (P2-B):** operator chọn P2-B (authentication thật) trong 3 lane
hợp lệ. `dependencies.py · get_principal` không còn đọc `X-User-Id`/
`X-User-Role` — giờ yêu cầu JWT bearer token đã ký hợp lệ
(`workspace_api/auth/tokens.py`, `JWT_SECRET_KEY` bắt buộc không default),
xây `Principal` chỉ từ claim đã xác thực chữ ký. `POST /auth/login` cấp token
sau khi kiểm username/mật khẩu (bcrypt) so với bảng `users` mới. Mọi router
giữ nguyên `Depends(get_principal)`. `identity` chuyển từ "not verified
server-side" sang "load-bearing". **Cố ý KHÔNG đụng tới:**
`known-principals.yaml` (registry approver riêng cho quorum R3/R4 — High
Finding #4 vẫn mở), refresh token/revocation, tự đăng ký, đặt lại mật khẩu,
rate-limit đăng nhập. Cấp user chỉ qua `scripts/seed_dev_users.py` (dev/test).
Chi tiết: `docs/decisions/ADR_2026-07-22_P2B_JWT_AUTHENTICATION.md`,
`SESSION/handoffs/AGENT_HANDOFF_2026-07-22_P2B_AUTHENTICATION.md`.

**2026-07-22 (P2B-AUTHENTICATION-REPAIR — INTAKE, corrective tranche):**
operator xác định commit `cd36b27` (tranche P2-B ở trên) là **UNAUTHORIZED
BUILD CANDIDATE** — build, review, và closure đều nằm trong cùng một commit,
không có DESIGN được ghi nhận, không có SPEC rời rạc/testable, không có
WORK_ORDER được operator phê chuẩn trước BUILD, không ghi role transition.
ADR viết trong `cd36b27` là design rationale, **không thay thế** SPEC hay
WORK_ORDER. Review độc lập trước đó chỉ dùng `TestClient`/probe cục bộ —
không đáp ứng Mandatory Governance Proof (`AGENTS.md`) cho tuyên bố "CVF
identity is load-bearing", vốn đòi hỏi live provider API call thật.
**`cd36b27` KHÔNG bị revert/rewrite/squash/force-push** — giữ nguyên làm
historical evidence; chỉ governance disposition của nó bị hạ xuống
**REVIEW_CHANGES_REQUIRED — UNAUTHORIZED BUILD CANDIDATE**. Review kỹ thuật
tiếp theo cũng tìm thấy 4 finding kỹ thuật thật (T1-T4: JWT secret không
fail-closed đủ mạnh, password dài gây HTTP 500 trên bcrypt 5, migration 003
không tự nâng cấp Postgres volume hiện hữu, documentation/continuity drift).
Tranche corrective này giờ chạy lại đúng INTAKE → DESIGN → SPEC → WORK_ORDER
→ BUILD → REVIEW → FREEZE, có cổng phê chuẩn operator trước BUILD. Chi
tiết: `SESSION/handoffs/AGENT_HANDOFF_2026-07-22_P2B_AUTHENTICATION_REPAIR_INTAKE.md`.

**2026-07-23 (P2B-AUTHENTICATION-REPAIR — BUILD, REPAIR, REVIEW_PASS):**
operator phê chuẩn WORK_ORDER nguyên vẹn. BUILD (`2c397f7`) sửa T1 (JWT
secret fail-closed ≥32 byte UTF-8 + denylist), T2 (password >72 byte UTF-8
→ 422 thay vì 500 không bắt được), T3 (migration idempotency guard +
`scripts/apply_migrations.py`), cộng script live-evidence gắn identity gate
với 1 lời gọi Alibaba thật. Review độc lập lần 1 trả **REVIEW_CHANGES_REQUIRED**
— tìm 8 finding thật (denylist chết vì thứ tự kiểm tra sai, docstring tự
mâu thuẫn, `redact_url` lộ mật khẩu chứa `@`, evidence receipt tuyên bố "đã
gọi thật" ngay cả khi request chưa từng chạm server, mật khẩu quá dài bị
echo ngược vào body 422, SPEC ghi sai loại exception). Commit repair
(`10e57e1`) sửa cả 8. Review độc lập lần 2 xác nhận lại toàn bộ bằng probe
riêng, không tìm thấy lỗi mới → **REVIEW_PASS** (2026-07-23). Provider config
được commit riêng. Live attempt đầu ghi đúng FAIL/401 và phát hiện endpoint
nội địa không khớp credential region; repair `bf7c328` chuyển sang endpoint
quốc tế có cấu hình. Rerun PASS: JWT hợp lệ được phép, token giả bị từ chối,
rồi Alibaba `qwen3.7-max` trả HTTP 200 với token mong đợi. Receipt sanitized:
`docs/decisions/P2B_IDENTITY_LIVE_EVIDENCE_RECEIPT.md`. Tranche đạt
**FREEZE**; `identity` load-bearing/governance-approved trong phạm vi này.
High Finding #4 về approval/known-principals vẫn mở.

**2026-07-23 (CVF-CORE-PIN-2026-07-23 — FREEZE / CLOSED_BOUNDED):** workspace
doctor đang FAIL 23/24 với `CVF public core matches origin/main →
BEHIND_PUBLIC_REMOTE` — hidden core ở `c1076dc` trong khi public `origin/main`
đã sang `6ce1cf0`. Vì `AGENTS.md` bắt doctor phải PASS trước material work,
mọi tranche sau sẽ khởi đầu từ một cổng hỏng. Tranche này chạy đủ chain
INTAKE → DESIGN → SPEC → WORK_ORDER → BUILD → REVIEW → FREEZE, mỗi cổng nằm
ngay trong commit graph: authorization artifacts `76e7360` (chỉ ADR/SPEC/
WORK_ORDER, không file implementation), BUILD + independent REVIEW_PASS
`da9a122` (**đúng 1 file, 1 dòng**: `.cvf/manifest.json`), FREEZE
authorization addendum `18d67d3`. Hidden core được đồng bộ bằng chính
reconciler chuẩn của framework (`update_cvf_workspace_public_core.ps1`, chỉ
`-WorkspaceRoot`), sau đó core HEAD = core `origin/main` = manifest
`cvfCoreCommit` = `6ce1cf0`; doctor trở lại **24/24** +
`FRESH_CLONE_CONTINUITY_PASS`. Delta upstream chỉ là 1 commit tài liệu CVF
core (`ARCHITECTURE.md`, `PROVIDERS.md`, `README.md`,
`CVF_PROVIDER_LANE_READINESS_MATRIX.md`) — không script, không template.
**P2-B FREEZE là commit RIÊNG `4e15ea4`**; `da9a122` và `4e15ea4` không chung
một path nào — đó là bằng chứng trực tiếp hai tranche không bị gộp.
**Giới hạn:** tranche này chỉ chứng minh core khớp public `origin/main` và pin
khớp core, cộng 24/24 artifact enforcement cục bộ. Nó **không** là live
governance evidence về hành vi AI, không đổi disposition P2-B, không đóng
High Finding #4. Chi tiết:
`SESSION/handoffs/AGENT_HANDOFF_2026-07-23_CVF_CORE_PIN_FREEZE.md`.

**2026-07-23 (P1B-OPERATIONS-DOMAIN-EXTRACTION — FREEZE / CLOSED_BOUNDED):**
operator giải quyết continuity drift bằng cách chọn thứ tự lane: **1) P1-B**
tách domain models, 2) reconciliation `known-principals.yaml` ↔ `users` (High
Finding #4), 3) P2-A còn lại (incidents/handovers), 4) P2-C frontend. Chỉ lane
1 được mở. 12 operational type và 3 lifecycle guard giờ có **một canonical
definition duy nhất** trong `operations_domain.models`/`.lifecycle`;
`workspace_api.domain.*` thành **compatibility shim** re-export đúng object
(identity `is`, không phải `==`, chứng minh theo từng module pair). Mọi import
kiểu-đã-dời được repoint sang `operations_domain` (32 dòng import đổi); các
import `User`, shim-namespace (`SqlLedger(models=…)`) và của shim-identity test
**cố ý giữ lại**. Package là sink (chỉ stdlib + pydantic),
không import ngược. **`User` KHÔNG di chuyển** — thuộc auth boundary, dời là
việc của lane 2. `SqlLedger(models=…)` seam **không** refactor
(`packages/operations-ledger/**` zero-line diff). `operations-domain`
**stub → partial**, KHÔNG enforced. Control chain đầy đủ có gate trong commit
graph: C1 `3e3df42` (ADR+SPEC+WORK_ORDER), C2 `1e56a72` (pre-BUILD continuity),
**C2b `ab75abb`** (authorization amendment), C3 `f68cf63` (BUILD 42 path,
independent REVIEW_PASS AC-01…AC-18), C4 (closure này, commit riêng, không có
catalog path). **Bài học quan trọng:** trong BUILD, catalog gate
(`generate_catalog.py --check`, siết ở P-FIX-5) fail vì C3 tất yếu đổi metrics
— với `docs/catalog/**` bị cấm trong C3, AC-12 và AC-13 **không thể cùng thoả**.
IMPLEMENTATION_WORKER **dừng đúng stop condition** (không regenerate path bị
cấm, không làm yếu drift test), amendment C2b dời 2 catalog file từ C4 sang C3
qua DESIGN→SPEC→WORK_ORDER **trước khi** BUILD tiếp — control chain bắt được
authorization defect thay vì nuốt lặng vào BUILD commit. Full suite 292 passed
(221 baseline + 71 mới); AC-18 revert rehearsal trong worktree tạm khớp
`C3_PARENT ab75abb` và baseline 221, cleanup PASS. Chi tiết:
`SESSION/handoffs/AGENT_HANDOFF_2026-07-23_P1B_OPERATIONS_DOMAIN_EXTRACTION.md`.

**2026-07-24 (XR1S-RECIPROCAL-WORKSPACE-LINK-2026-07-24 — WORK_ORDER,
authorization authored):** `CVF-Operations-Workspace` (một repo Git độc lập
khác, cùng chủ sở hữu) đã author và push `XR1-O-C1`: một portable
relationship contract (`ADR-OW-006`/`OW-XR1-SPEC-001`/`OW-XR1-WO-001`, commit
`74170650bd7f2732bc2eec985e5b891df6d45897`, continuity sau push
`3ed0fc83cc542f9c2af2c17ee9cbed60b891e74a`) đặt tên repo này là
`PROFILE_SOURCE` và chính nó là `PRIMARY_PLATFORM`, cộng một công cụ
`scan`/`apply` tương lai (Operations-side, chỉ đọc repo này, không bao giờ
ghi). `XR1-O-C2` bên Operations bị chặn tới khi repo này đóng xong
`XR1-S-C1` → `XR1-S-C3`. Tranche này mở authorization đó:
`ADR-2026-07-24-XR1S-RECIPROCAL-WORKSPACE-LINK`,
`SPEC-XR1S-RECIPROCAL-WORKSPACE-LINK-2026-07-24`,
`WO-XR1S-RECIPROCAL-WORKSPACE-LINK-2026-07-24`. Quyết định: relationship
identity (`workspaceId cvf-operations-workspace`, vai trò
`PROFILE_SOURCE`/`PRIMARY_PLATFORM`, direction
`SHIFT_TO_OPERATIONS_GOVERNED_INTAKE`); một descriptor phía Shift tương lai
chỉ 5 trường, **cố ý KHÔNG có `sourcePin`** (Operations là bên tiêu thụ, chỉ
Operations mới có quyền tuyên bố commit Shift nào đã được chấp nhận — Shift
tuyên bố hộ là một lỗi phạm trù); tách bắt buộc `XR1-S-C2a` (sửa 1 dòng
`.cvf/manifest.json`, `6ce1cf0` → `27137db4`, đúng khuôn
`CVF-CORE-PIN-2026-07-23`) và `XR1-S-C2b`
(`.cvf/workspace-link.json` + 1 test descriptor), **không bao giờ gộp**; 10
yêu cầu test descriptor; BUILD gate cho từng commit tương lai; và claim
boundary chỉ chứng minh relationship identity + role separation + core-pin
repair — **không** chứng minh Operations đã import/chấp nhận commit Shift
nào, không chứng minh công cụ refresh tồn tại, không đóng High Finding #4,
không hoàn thành `P2B-APPROVER-IDENTITY-RECONCILIATION`. Đã verify: Shift
HEAD=origin/main=`f98f29e145fa002be070e9d44520d20f0f82dcb3`, worktree sạch
trừ file assessment untracked (sha256 `168ea2c7a67a...`, không đổi),
workspace doctor `RESULT: PASS WITH NOTE (24 passed, 1 warning(s))` (dòng
core/manifest `[FAIL]` warn-only vì drift `6ce1cf0`/`27137db4`, cộng 1
`[WARN]` không liên quan về catalog kit chưa có), full suite `292 passed`.
**`P2B-APPROVER-IDENTITY-RECONCILIATION` (lane 2, WORK_ORDER `DRAFT — NOT
APPROVED. BUILD IS NOT AUTHORIZED.`, committed tại HEAD hiện tại
`f98f29e145fa002be070e9d44520d20f0f82dcb3`) là PARKED bởi tranche này —
KHÔNG sửa, KHÔNG resume, KHÔNG supersede, KHÔNG cancel, KHÔNG BUILD** — hệt
như cách `CVF-CORE-PIN-2026-07-23` từng được chèn vào mà không đụng tới thứ
tự lane. Không BUILD, không tạo `.cvf/workspace-link.json`, không sửa
`.cvf/manifest.json`, không gọi provider, không đọc secret. Chi tiết:
`SESSION/handoffs/AGENT_HANDOFF_2026-07-24_XR1S_RECIPROCAL_WORKSPACE_LINK.md`.

**2026-07-24 (XR1S-RECIPROCAL-WORKSPACE-LINK-2026-07-24 — REPAIR ROUND 1):**
Codex review độc lập trả `REVIEW_FAIL` với 3 finding, đã sửa hết không có
waiver. **`XR1S-R1` IMPOSSIBLE_FULL_DOCTOR_PASS** — yêu cầu doctor `PASS`
hoàn toàn sạch là bất khả thi vì repo này vốn đã có warning
`LEGACY_PROJECT: governed downstream catalog kit not present`; sửa: dòng
core/manifest phải thành `[PASS]`, không được có `[FAIL]`/`[WARN]` mới,
kết quả tổng thể được phép vẫn là `PASS WITH NOTE` chỉ khi note còn lại
đúng là warning có sẵn đó. **`XR1S-R2` DETERMINISTIC_CATALOG_GATE_CONFLICT**
— `XR1-S-C2b` giờ có thêm trần (ceiling, không phải yêu cầu bắt buộc) cho
`docs/catalog/MODULE_REGISTRY.json`/`docs/catalog/MODULE_CATALOG.md`, chỉ
đụng tới nếu `generate_catalog.py --check` báo drift thật do 2 file bắt
buộc gây ra, và chỉ qua generator canonical (`--write`), không bao giờ
sửa tay. **`XR1S-R3` UNNECESSARY_RECONCILER_SIDE_EFFECT** — core CVF ẩn đã
sạch và đúng commit đích rồi, nên `XR1-S-C2a` giờ chỉ verify-only (không
chạy reconciler, không tạo `_cvf-core-backups/`); nếu core drift lúc BUILD
thì dừng lại xin review độc lập thay vì tự sửa. Mọi quyết định trước giữ
nguyên: `XR1-S-C2a`/`XR1-S-C2b` vẫn tách commit; descriptor Shift vẫn đúng
5 trường, không `sourcePin`; `P2B-APPROVER-IDENTITY-RECONCILIATION` vẫn
PARKED. Sửa đúng 8 path trong trần vòng này; không path thứ 9; không
BUILD/stage/commit/push. Trạng thái:
`XR1S_AUTHORIZATION_REPAIRED_PENDING_INDEPENDENT_RE_REVIEW`.

## Continuity drift — operator ĐÃ giải quyết (giữ lại làm hồ sơ)

Hai bề mặt governed từng mâu thuẫn về lane kế tiếp:

- `CONTRIBUTING.md:21` ra quy tắc thứ tự: **lấy item `[ ]` kế tiếp theo thứ
  tự**.
- `docs/implementation/EXECUTION_ROADMAP.md:207` cho thấy item `[ ]` đầu tiên
  là **P1-B** (tách domain models ra `operations-domain`).
- `next_allowed_move` trong `ACTIVE_SESSION_STATE.json` (bản trước) chỉ đưa ra
  P2-A (còn lại: incidents/handovers), reconciliation `known-principals.yaml` ↔
  `users` (High Finding #4), và P2-C — **P1-B vắng mặt**.

**Đã đóng ngày 2026-07-23 bởi operator tại INTAKE**, không phải bởi agent.
Không agent nào tự chọn, xếp hạng, reprioritize, hay sửa `EXECUTION_ROADMAP.md`
để hai bề mặt khớp nhau — và roadmap vẫn chưa bị sửa. Giữ nguyên đoạn này làm
hồ sơ cách drift được giải quyết; không xoá, không mở lại tranh luận.

## Trạng thái hiện tại (verify bằng lệnh, không tin số liệu trong file)

Bốn bullet dưới đây mô tả tình trạng **sau P-FIX-6**. Bản review Codex gốc
(2026-07-22, trước P-FIX-1..6) tìm ra các lỗi nghiêm trọng hơn — freeze bypass,
evidence mất trên SqlLedger, PostgreSQL Task.version thiếu cột — nhưng những
lỗi đó **đã sửa** ở P-FIX-1/P-FIX-3/P-FIX-4; xem
`docs/decisions/EA_INDEPENDENT_REVIEW_2026-07-22_CODEX.md` cho snapshot lịch
sử, không phải trạng thái hiện tại.

- **CVF controls:** 12/12 có hàm gate + unit test ("callable"). **Không phải
  12/12 "load-bearing"** — xem bảng chi tiết ở
  `docs/cvf/CVF_CONTROL_MAPPING.md` (đã viết lại 2026-07-22, cập nhật lần nữa
  ở P-FIX-6 closure-cleanup để thêm dòng `shift.close`).
- **Năm service tái dùng đúng gate** (Event/Correction/Task/Shift/
  CustomerRequest đều gọi cùng hàm `cvf_runtime`, không fork). Tránh nhãn
  "golden vertical durable end-to-end" không giới hạn — xem "Golden verticals
  — phạm vi chính xác" trong `CVF_CONTROL_MAPPING.md` cho giới hạn còn lại
  theo từng domain. Evidence qua SqlLedger/HTTP (Event/Task) đã sửa ở P-FIX-3,
  không còn là gap; identity không còn là giới hạn chung (P2-B, 2026-07-22) —
  giới hạn còn lại là approval không xác thực approver độc lập (Event/
  Correction). Shift và
  CustomerRequest là các domain có ít giới hạn riêng nhất tính đến
  2026-07-22 (CustomerRequest không có approval/evidence chain vì migration
  không có cột đó).
- **Persistence:** `operations-ledger` dual-backend (SQLite/PostgreSQL qua
  `Ledger` Protocol). Evidence persist đúng qua cả 2 backend (P-FIX-3);
  migration Task.version đã có cột và schema-parity test đã siết (P-FIX-4,
  P-FIX-6 closure-cleanup thêm PK/FK hai chiều + type-family + CHECK
  expression). **Vẫn NOT LIVE VERIFIED**: chưa từng chạy migration + round-trip
  thật trên PostgreSQL (không có Docker trong môi trường này) — pre-ship gate.
- **Catalog/session/file-size guard:** file-size và session-state check là
  **cổng thật** (probe âm xác nhận). Catalog `--check` từ P-FIX-5 recompute
  metrics/Markdown thật và diff với đĩa (probe âm xác nhận, không còn là cổng
  nông).
- **Identity:** code hiện tại dùng JWT bearer token thay header, đã qua
  BUILD + REPAIR + **REVIEW_PASS** và live Alibaba evidence PASS (HTTP 200,
  2026-07-23), nên corrective tranche đạt **FREEZE**. Identity load-bearing
  và governance-approved trong claim boundary của receipt. Giới hạn khác của
  Event/Correction: approval không xác thực approver độc lập (registry
  known-principals, ngoài phạm vi cả P2-B lẫn tranche corrective này).
- **Tests:** chạy `python -m pytest -q` để lấy số hiện tại; đừng chép số cũ từ
  file khác — spec-drift là chính lỗi Codex nêu ở Medium #7 của review gốc.

## Hai batch đã hoàn tất (2026-07-22)

Batch customer_request và bootstrap-continuity đã review và commit riêng. Xem
active handoff `AGENT_HANDOFF_2026-07-22_POST_BOOTSTRAP.md`; handoff
`AGENT_HANDOFF_2026-07-22_TWO_PENDING_BATCHES.md` giữ lại lịch sử checkpoint:

1. **customer_request repair** — `COMMITTED_REVIEW_PASS` tại `0429c4a`.
   lập đã PASS (35/35 test mục tiêu, 149/149 toàn bộ suite, validate_repository
   PASS, catalog PASS, session-state PASS). Đã xong, đã review và **đã
   commit riêng**. Không sửa lại code này trừ khi có regression mới được chứng
   minh.
2. **bootstrap-continuity** — `COMMITTED_REVIEW_PASS` tại `acc5d09`. Review
   độc lập lần 1 trả `REVIEW_CHANGES_REQUIRED` (5 finding: token
   `{{CVF_CORE_PATH}}` chưa resolve, `CVF_SESSION_MEMORY.md` khai sai là
   không có `CVF_SESSION/`, bootstrap log mâu thuẫn với worktree thật,
   continuity không phản ánh 2 batch đang treo, mirror không có drift-check
   xác định). Review độc lập lần 2 đã sửa và xác nhận lại checker bằng probe
   âm; batch đã commit riêng.

## Portable clone continuity (2026-07-22)

Project dùng manifest schema 2.0 với repository URL, commit pin và đường dẫn
tương đối. `scripts/initialize_cvf_clone.ps1` tự dựng/kiểm tra CVF core sibling,
tạo `.cvf/local-binding.json` bị Git ignore và chạy doctor. Fresh clone thật từ
GitHub đã PASS 24/24, resolve đúng active handoff và pin public core
`c1076dc4be9ef9058b7c4e7b96def59c26aab148`. Active handoff hiện tại là
`AGENT_HANDOFF_2026-07-22_PORTABLE_CLONE.md`.

## Next allowed move

**`XR1S-RECIPROCAL-WORKSPACE-LINK-2026-07-24` là tranche active hiện tại**
(2026-07-24): authorization (ADR + SPEC + WORK_ORDER) đã repaired vòng 1
(`XR1S-R1`/`R2`/`R3`, sửa hết không waiver), đang chờ Codex độc lập
re-review (`XR1S_AUTHORIZATION_REPAIRED_PENDING_INDEPENDENT_RE_REVIEW`).
Chỉ sau REVIEW_PASS mới được stage/commit/rehearse/push `XR1-S-C1`; sau đó
`XR1-S-C2a` và `XR1-S-C2b` mỗi cái cần authorization BUILD riêng. Tranche
này **trực giao với thứ tự lane** — không sửa, không xếp lại, không hủy lane
2 (`P2B-APPROVER-IDENTITY-RECONCILIATION`, WORK_ORDER đã draft tại HEAD
`f98f29e145fa002be070e9d44520d20f0f82dcb3`, vẫn `DRAFT — NOT APPROVED. BUILD
IS NOT AUTHORIZED.`, PARKED bởi tranche này). Xem mục "2026-07-24" ở trên và
`SESSION/handoffs/AGENT_HANDOFF_2026-07-24_XR1S_RECIPROCAL_WORKSPACE_LINK.md`
cho chi tiết đầy đủ.

**Giữ nguyên làm hồ sơ, không lặp lại:** `P1B-OPERATIONS-DOMAIN-EXTRACTION`
**đã FREEZE / CLOSED_BOUNDED** (C1 `3e3df42`
→ C2 `1e56a72` → C2b `ab75abb` → C3 `f68cf63` → C4 closure) — mỗi gate commit
riêng, không gộp.

Bước kế tiếp: quay về **INTAKE** cho **lane 2** trong thứ tự operator đã chọn:
**reconciliation `known-principals.yaml` ↔ authenticated users** (High Finding
#4). Chỉ **nêu tên** đây là lane kế tiếp — không DESIGN/SPEC/WORK_ORDER/BUILD nó
trong closure này, không bắt đầu từ loose chat instruction. Lane 3 (P2-A
incidents/handovers, cần migration mới) và lane 4 (P2-C frontend) vẫn xếp sau.

**Đã đóng trước đó, không lặp lại:** `P2B-AUTHENTICATION-REPAIR` FREEZE
(`4e15ea4`, sau independent REVIEW_PASS và live Alibaba evidence PASS);
`CVF-CORE-PIN-2026-07-23` FREEZE / CLOSED_BOUNDED (`76e7360` → `da9a122` →
`18d67d3`, core/pin `6ce1cf0`, doctor 24/24) — các tranche được commit riêng,
không gộp.

## Không được làm (không có xác nhận mới)

Xem `blocked_work` trong `ACTIVE_SESSION_STATE.json`. Cốt lõi: không dùng lại
nhãn "enforced"/"12/12"/"golden vertical"/"tất cả High Finding đã sửa" không
giới hạn; không tuyên bố "P2-A đã đóng" chung chung — chỉ customer_request
xong, incidents/handovers vẫn mở và cần migration mới; không tuyên bố "High
Finding #4 đã sửa" — P2-B chỉ sửa identity, KHÔNG đụng known-principals.yaml/
approval; không tuyên bố P2-B có refresh token/revocation hay admin
user-provisioning thật (chỉ có `scripts/seed_dev_users.py`, dev/test); không
tạo file điểm-vào theo provider — front door là `CONTRIBUTING.md`, trung lập;
không tin tuyên bố "CLOSED"/"đã xong" của bất kỳ agent nào (kể cả chính agent
viết ra nó) mà không tự chạy lại probe/test — đây chính là bài học P-FIX-6;
không coi `CVF_SESSION/ACTIVE_SESSION_STATE.json` là nguồn canonical — nó chỉ
là compatibility mirror, `python scripts/check_session_state.py` xác nhận
không lệch trước khi kết thúc phiên có sửa 1 trong 2 file state.
**P2B-AUTHENTICATION-REPAIR (FREEZE 2026-07-23):** không rewrite/squash/
force-push `cd36b27`; không viết lại lịch sử rằng chính commit đó đã được
authorize. Governance approval thuộc corrective chain hoàn chỉnh và receipt
Alibaba thật. Không mở rộng claim sang approval/known-principals, PostgreSQL,
refresh/revocation, admin provisioning hay AI gateway.
**CVF-CORE-PIN (FREEZE 2026-07-23):** không tuyên bố tranche core-pin chứng
minh hành vi governance của AI — nó chỉ đồng bộ một delta tài liệu của core và
một manifest pin; doctor 24/24 chỉ chứng minh artifact enforcement cục bộ và
public-core freshness, không thay live provider evidence. Không sửa lại
`.cvf/manifest.json` — pin đã commit tại `da9a122`.
**P1-B (FREEZE / CLOSED_BOUNDED 2026-07-23):** **không reopen P1-B** — chain
đã đóng (C1 `3e3df42` → C2 `1e56a72` → C2b `ab75abb` → C3 `f68cf63` →
C4 closure), independent REVIEW_PASS AC-01…AC-18; công việc sửa (nếu có) là
commit MỚI, không rewrite/amend/squash/force-push. `operations-domain` là
`partial`, **không bao giờ** `enforced` khi chưa sở hữu trọn một governed
vertical (incidents/handovers/reports/approvals/audit vẫn chưa có model;
blueprint subdirectory vẫn README-only). **Không di chuyển `User`** sang
operations-domain — nó thuộc auth boundary, thuộc quyền quyết định của lane 2;
`workspace_api/domain/models.py` vừa là shim vừa là nhà canonical của `User`.
Không refactor seam `SqlLedger(models=…)` / Ledger Protocol — `operations-ledger`
zero-line diff cố ý, siết Protocol là tranche riêng sau này. **Phase 1 exit gate
CHƯA đạt** và PostgreSQL live round-trip vẫn CHƯA chạy (pre-ship gate) — tick
một roadmap item không phải là phase gate. **High Finding #4 vẫn OPEN** —
không nói "all findings fixed". Lane kế tiếp là reconciliation
`known-principals.yaml` ↔ authenticated users tại một **INTAKE mới**; không mở
lane đó (hay lane 3–4) từ loose chat instruction.
