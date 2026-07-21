# Đánh giá độc lập cấp EA — `shift-operations-workspace`

**Ngày:** 2026-07-21
**Người đánh giá:** Claude (độc lập, không phải tác giả repo)
**Phương pháp:** Quét thực tế theo quy tắc CVF (evidence-based, chống scaffold rỗng, chống over-claim). Đọc code từng file, chạy test, đối chiếu tuyên bố với thực tế. Không kết luận qua tiêu đề/tên thư mục.

---

## Phán quyết tổng thể

> **Đây là một *architecture blueprint có tính chính trực cao*, KHÔNG phải một sản phẩm gần production. Repo tự tuyên bố đúng bản chất của mình — đó là điểm mạnh lớn nhất. Nhưng khoảng cách giữa quy mô kiến trúc được vẽ ra và lượng code thực tế là rất lớn, và các CVF `required_controls` quan trọng nhất hiện chưa tồn tại dưới dạng code.**

| Hạng mục | Điểm | Ghi chú |
|---|---|---|
| Tính chính trực của tuyên bố (anti-over-claim) | **9/10** | Tự khai "SKELETON", không giả vờ production |
| Chất lượng code thực tế (phần đã viết) | **8/10** | Sạch, đúng chuẩn Python 3.12, có test chạy được |
| Độ phủ so với kiến trúc tuyên bố | **2/10** | ~150 thư mục package chỉ chứa 2 file code |
| Thực thi CVF controls trong code | **1.5/10** | 12 control bắt buộc → gần như 0 được enforce |
| Sẵn sàng production | **1/10** | In-memory, không auth, connector là mock |

---

## Bằng chứng đo được (không phải cảm nhận)

- **436 file thực tế**, trong đó **297 file `.md` (68%)** vs **~68 file code** (63 `.py` + 5 `.ts/.tsx`).
- **Tổng code thật: 523 dòng.** File lớn nhất là `models.py` — **88 dòng**.
- **Test: `6 passed` thật** (đã chạy `pytest`). Tuyên bố này trung thực.
- **~150 thư mục con dưới `packages/` chứa đúng 2 file `.py`** (`provider_interface.py`, `adapter.py`). Phần còn lại là `.md` + `.yaml`/`.json` schema. Toàn bộ `ai-gateway/`, `operations-domain/`, `operations-ledger/`, `refinery-bridge/`, `notification-engine/`, `identity-mapping/`… **không có code triển khai**.

---

## Phát hiện quan trọng (xếp theo mức nghiêm trọng)

### 🔴 1. CVF `required_controls` gần như không được thực thi trong code
Profile khai báo 12 control bắt buộc: `identity, permission, domain_lock, data_scope, risk, approval, evidence, audit, cost, refusal, termination, freeze`.

`grep` toàn bộ codebase cho `permission | authorize | authenticate | audit_log | require...` → **trả về RỖNG hoàn toàn**.
- 8/16 API router chỉ có `__init__.py` rỗng: `authentication/`, `approvals/`, `audit/`, `corrections/`, `customers/`, `handovers/`, `incidents/`, `tasks/`.
- Endpoint đang chạy (`shifts/router.py`, `messages/router.py`, `events/router.py`) **không có auth, không có audit-write, không có permission gate**.
- Dấu vết "risk/approval" duy nhất là 2 dòng trong `application/services.py`: `if event.risk_class in {"R2","R3","R4"} and not approver_id` — nhưng chỉ kiểm tra chuỗi `approver_id` khác rỗng, **không xác thực người đó có thẩm quyền**. Đây là kiểm soát mang tính biểu tượng.

→ **Đối với một project mà toàn bộ luận điểm bán hàng là "CVF kiểm soát identity/permission/approval/audit", đây là gap nghiêm trọng nhất.** Kiến trúc CVF hiện sống trong `.md` và `.yaml`, chưa sống trong code.

### 🔴 2. Persistence là in-memory — "Operations Ledger là nguồn sự thật" chưa tồn tại
`infrastructure/repository.py` là `InMemoryLedger` với `dict` + biến global `ledger`. Có SQL migration (87+36 dòng) nhưng **không có tầng nào đọc/ghi Postgres**. "Ledger là source of truth" — mệnh đề trung tâm của README — hiện chỉ là dict RAM, mất sạch khi restart. `version += 1` không phải versioning bất biến; state cũ bị ghi đè, không lưu lịch sử.

### 🟠 3. CORS mở toàn bộ + secret placeholder
`main.py`: `allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]` trên một hệ thống định vị là "governed/enterprise". `WEBHOOK_SHARED_SECRET` mặc định `"replace-me"` và webhook fallback về giá trị này nếu env thiếu → nếu deploy quên set, HMAC vẫn "verify" với secret công khai. Nên fail-closed (từ chối start) thay vì fallback.

### 🟡 4. Thiếu nhất quán số liệu trong artifact "FROZEN"
`IMPLEMENTATION_STATUS.json` khai **439 files / 286 dirs**; thực tế **436 / 285**. Sai lệch nhỏ nhưng với một artifact tự dán nhãn `REPOSITORY_BLUEPRINT_FROZEN`, con số phải khớp tuyệt đối — nếu không, nhãn "frozen" mất giá trị kiểm chứng. Nên sinh tự động bằng `generate_tree.py` trong CI.

### 🟡 5. Tỷ lệ docs/code ~5:1 → rủi ro "spec drift"
2.777 dòng markdown / 86 file docs mô tả 5 phase, nhưng nhiều file docs rất mỏng (phase docs 15 dòng, ADR template 19 dòng). Rủi ro cổ điển: tài liệu mô tả hệ thống **chưa tồn tại**, và khi bắt đầu code thật, docs sẽ lệch nhanh.

---

## Điểm mạnh thật sự (đã kiểm chứng)

1. **Chính trực hiếm có.** `VALIDATION_REPORT.md` tự viết: *"This is recorded as an environment limitation, not as a successful build claim"* và *"official production connector not claimed"*. Đây là chuẩn mực trung thực mà đa số scaffold AI-generated không có — thường over-claim "production-ready".
2. **Code đã viết thì sạch.** State machine (`domain/lifecycle.py`) đúng đắn, dùng `StrEnum`, Pydantic v2 `model_validator`, `RLock` cho concurrency ở dedup store — đúng chuẩn hiện đại.
3. **HMAC verification làm đúng:** `verification/hmac.py` dùng `hmac.compare_digest` (constant-time), không tự chế so sánh chuỗi.
4. **Ranh giới data-state rõ ràng:** RAW→…→FROZEN được model hóa nhất quán giữa docs, enum và state machine.
5. **Freeze semantics có test thật** (`test_freeze.py`, `test_state_machine.py` chạy pass).

---

## Khuyến nghị EA (ưu tiên hành động)

| # | Hành động | Vì sao |
|---|---|---|
| 1 | Đổi trạng thái từ "kiến trúc" → "Phase 1 in progress" và thêm cột "code %" bên cạnh mỗi package trong TREEVIEW | Ngăn người đọc hiểu nhầm 150 thư mục = 150 module đã build |
| 2 | Thực thi tối thiểu 3 CVF control trong code trước khi mở rộng bề rộng: identity/permission (dependency `require_role`), audit-write (mọi mutation ghi audit record), evidence-link | Đây là lời hứa lõi của sản phẩm; hiện chỉ nằm trên giấy |
| 3 | Thay `InMemoryLedger` bằng repository Postgres append-only trước khi thêm bất kỳ domain mới nào | "Ledger source of truth" phải bền vững + versioned mới đúng nghĩa |
| 4 | Fail-closed cho secret & siết CORS theo `APP_ENV` | Bug bảo mật rẻ tiền, sửa sớm |
| 5 | Sinh `IMPLEMENTATION_STATUS.json` + counts bằng CI, không viết tay | Bảo toàn giá trị của nhãn "FROZEN" |
| 6 | Chuyển chiều rộng thành chiều sâu: hoàn thiện 1 domain (shift) đủ 12 control end-to-end làm "golden vertical", rồi nhân bản | Chống spec-drift, tạo mẫu chuẩn |

---

## Kết luận một dòng

> Đây là **bản thiết kế kiến trúc trung thực và sạch sẽ, nhưng mới ~5% được hiện thực hóa bằng code**; giá trị hiện tại nằm ở đặc tả + tính chính trực, không phải ở phần mềm chạy được. **Rủi ro lớn nhất không phải là code sai — mà là khoảng cách giữa quy mô kiến trúc được vẽ và lượng code thực, cùng việc các CVF control cốt lõi chưa rời khỏi trang giấy.** Việc phân loại đúng nó là "blueprint + skeleton" (như repo đã tự làm) là điều kiện bắt buộc để đánh giá này công bằng.
