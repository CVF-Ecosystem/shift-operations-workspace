# Roadmap tham khảo CQA cho Shift

**Trạng thái:** Đề xuất để review, chưa mở BUILD. **Ngày:** 2026-09-27. **Rủi ro dự kiến khi triển khai:** R2. **Nguồn tham khảo:** bản local `chat-quality-agent` tại commit `6546574b23aded18d292c6382a06727baacfe3fe`. **Nền Shift:** `397bd9fcfdff177ecb0e29511bc4223e2e9b73b3`.

## Mục tiêu và ranh giới

Đưa vào Shift khả năng **đánh giá dữ liệu hội thoại/bàn giao ca theo job, theo dõi lượt chạy và rà soát đề xuất có dẫn chứng**. Người vận hành quyết định việc chấp nhận kết quả; job không được tự tạo, sửa hoặc xác nhận operational record. Tái thiết kế theo hợp đồng Python, ledger, Integration Edge và AI gateway của Shift; không nhập mã Go, cơ sở dữ liệu, tenant model, prompt hay scheduler của CQA.

Roadmap này là phương án bổ sung cho [Execution Roadmap](../implementation/EXECUTION_ROADMAP.md), không thay đổi trạng thái Phase 4 hoặc tự kích hoạt Phase 5. Mỗi giai đoạn dưới đây cần INTAKE → DESIGN → SPEC → WORK_ORDER → BUILD → REVIEW → FREEZE riêng trước khi triển khai. Claim CVF kiểm soát luồng AI phải có bằng chứng gọi provider thật; mock chỉ được dùng cho kiểm tra cấu trúc UI.

## Quyết định ưu tiên

1. **Lát cắt đầu tiên:** job chỉ đọc đánh giá chất lượng bản ghi bàn giao ca/hội thoại nội bộ đã xác nhận. Điều này kiểm tra giá trị của job và kết quả trước khi phụ thuộc vào kênh ngoài.
2. **Kênh ngoài:** Zalo OA và Facebook Messenger là hai ứng viên đầu tiên; chọn một kênh cho pilot sau khi xác minh quyền, API, dữ liệu mẫu, chi phí vận hành và quyền sử dụng dữ liệu. Không suy ra khả năng thu thập chỉ từ mã CQA.
3. **WhatsApp:** giữ ở trạng thái `DEFERRED_OPTION`. Adapter hiện có của Shift chỉ là conformance mock. Mở lại nếu có nhu cầu đo được, tài khoản/luồng WhatsApp Business phù hợp và chi phí tích hợp được chấp nhận; nếu không, bỏ khỏi phạm vi phát hành mà vẫn giữ hợp đồng kênh chung.
4. **Lịch chạy, thông báo và export:** chỉ mở sau khi lượt chạy thủ công, kiểm soát ngân sách, quyền truy cập và chất lượng dẫn chứng đã đạt tiêu chí.

## Hiện trạng cần giữ đúng

| Phần Shift | Trạng thái tại commit nền | Hệ quả cho kế hoạch |
|---|---|---|
| Internal message/operational record | Có các luồng đã đóng trong phạm vi nội bộ; external channel message ingestion chưa hoàn chỉnh | Job đầu tiên đọc confirmed internal data; connector ngoài cần tranche khác |
| Integration Edge / channel SDK | Có ranh giới ingress, receipt, chống trùng và adapter conformance; chưa chứng minh tích hợp vendor thật | Connector phải đi qua Edge, không gọi thẳng route `POST /messages` nội bộ |
| AI gateway | Có dispatch và kiểm soát theo hợp đồng trong phạm vi thư viện; chưa có application caller và usage ledger bền vững | Job phải đi qua gateway; không tuyên bố sản phẩm đã có governance AI khi chưa có live proof |
| `workspace-worker` | Job modules còn là khung | Cần queue, persistence, lease/recovery và trạng thái thực trước khi chạy nền |
| Reporting / notification | Engine tương ứng là stub; operational `END_SHIFT` Report đã có riêng | Kết quả AI là proposal, không thay thế report chính thức; delivery cần thiết kế riêng |

Nguồn hiện trạng: [roadmap chính](../implementation/EXECUTION_ROADMAP.md), [module catalog](../catalog/MODULE_CATALOG_DETAIL.md), `apps/workspace-worker/src/workspace_worker/main.py`.

## Trình tự triển khai đề xuất

### S0 — Chốt nguồn tham khảo và trường hợp sử dụng

**Đầu ra:** receipt nguồn CQA gắn commit bất biến; danh mục file được xét và disposition từng file; ma trận `ADAPT / NO_NEW_VALUE / DEFER / REJECT`; một use case pilot, tập dữ liệu được phép dùng, người review, cách đo thời gian xử lý và chi phí. Đối chiếu từng giá trị với owner hiện có trong Shift/CVF trước khi mở owner mới. Các cuộc đọc CQA trong trao đổi trước chỉ là đánh giá chọn lọc, chưa thay cho corpus receipt hoàn chỉnh.

**Exit:** có bộ ví dụ thật đã được phép dùng và tập mẫu âm gồm sai scope, thiếu dẫn chứng, dữ liệu đã sửa, dữ liệu chưa confirmed. Nếu không xác định được use case hoặc quyền dữ liệu, dừng ở nghiên cứu; không mở job.

### S1 — Hợp đồng nguồn và kết quả đề xuất

**Đầu ra:** định nghĩa phiên bản cho `EvaluationJob`, `JobRun`, `ItemAttempt`, `ResultProposal`, `SourceEvidenceRef` và `HumanDisposition`; mapping từ confirmed source ID/version/digest đến từng kết quả; snapshot của rule/prompt/model; khóa idempotency theo job + source version + rule version; retention/redaction. Định nghĩa outcome tường minh: `QUEUED`, `RUNNING`, `PARTIAL`, `SUCCEEDED`, `FAILED`, `CANCELLED`, cùng lỗi từng item và quy tắc resume. Không dùng ID do model tự khai làm căn cứ gắn bản ghi.

**Owner dự kiến:** `operations-domain`/`workspace-contracts` cho schema, `operations-ledger` cho persistence, `workspace-api` cho quyền và read model. Đăng ký invariant family nếu hợp đồng outcome/receipt kích hoạt [Invariant Family Standard](../cvf/INVARIANT_FAMILY_STANDARD.md).

**Exit:** test bác bỏ ID ngoài batch/scope, source version cũ, duplicate, kết quả thiếu, output sai schema, và mọi nỗ lực ghi vào confirmed operational record. Chưa gọi provider.

### S2 — Job thủ công và chạy thử giới hạn

**Đầu ra:** API tạo/chạy/hủy job có kiểm quyền; worker thực với durable queue/lease hoặc cơ chế tương đương được review; lưu `JobRun` và `ItemAttempt` trước khi dispatch; giới hạn số item và ngân sách cho preview; resume từ item chưa hoàn tất; status terminal phản ánh lỗi lưu kết quả và lỗi kiểm chứng output. Chỉ đọc confirmed snapshot. Điểm gọi AI duy nhất đi qua `ai-gateway`, với evidence/usage receipt gắn run/item.

**Exit:** chạy thử tập nhỏ → kết quả có source link; crash/restart, timeout, cancel, duplicate trigger, hai worker đồng thời và lỗi DB không làm mất item hoặc báo thành công sai. Test âm chứng minh request bị từ chối không gọi provider. Nếu claim governance AI, chạy một proof thật qua đúng application caller và ghi sanitized request/response receipt; unit/mock không đủ.

**Rollback:** tắt job mới, giữ dữ liệu nguồn và lịch sử run để điều tra; không xóa operational records.

### S3 — Bàn rà soát kết quả

**Đầu ra:** màn hình theo dõi job/run/item; lọc và phân trang tại server theo ca, nguồn, thời gian, trạng thái, rule và mức độ; faceted counts khớp bộ lọc; xem trích dẫn gắn source ID/version; người có quyền có thể đánh dấu `ACCEPTED / REJECTED / NEEDS_REVIEW` với actor, thời gian và lý do. Export đúng bộ lọc, giới hạn kích thước, quyền và redaction; export ghi rõ đây là kết quả đánh giá, không phải `END_SHIFT` Report.

**Exit:** không lộ kết quả ngoài scope; link source hỏng/đã đổi hiện trạng thái không xác minh được; phân trang, tổng đếm và CSV/Excel nhất quán trên dữ liệu lớn; review action có audit, không sửa nguồn. Chỉ sau đó mới xem xét dashboard tổng hợp.

### S4 — Nhật ký chi phí và ngân sách bền vững

**Đầu ra:** mỗi attempt ghi provider/model, token, tiền ước tính, tiền thực, đơn giá + nguồn/phiên bản giá và trạng thái `KNOWN / UNKNOWN / PENDING`; gắn với reservation và settlement. Giá chưa biết hiển thị là **chưa xác định**, không là 0; các tổng chi phí cho biết phần chưa tính. Đặt budget cap theo job/run trước khi mở chạy nhiều item hoặc lịch chạy.

**Exit:** retry/duplicate không tính hai lần, crash giữa reserve và settle được đối soát, giá thiếu không làm tổng sai, báo cáo chi phí truy ra từng receipt. Kiểm tra giá theo nguồn được phép và ngày hiệu lực; không tự tin bảng giá tĩnh của CQA là hiện hành.

### S5 — Một connector pilot Zalo hoặc Facebook

**Điều kiện mở:** S1/S2 đã chạy được trên dữ liệu nội bộ; có tài khoản/kênh và quyền API hợp lệ; xác định được phương thức nhận, phạm vi lịch sử, giới hạn và retention theo tài liệu vendor hiện hành. Quyết định Zalo hay Facebook bằng giá trị dữ liệu pilot, không bằng sự hiện diện của adapter CQA.

Nguồn kiểm tra tại S5: [Zalo Developers](https://developers.zalo.me/apps) và [Meta Messenger Platform](https://developers.facebook.com/docs/messenger-platform/); quyền và giới hạn phải được xác minh tại thời điểm mở tranche, không khóa theo tài liệu CQA cũ.

**Đầu ra:** connector vendor riêng xác thực payload/credential, đưa raw evidence qua Integration Edge, chuẩn hóa message/attachment, ánh xạ sender theo P4-E và giữ trạng thái nguồn. Có cursor hoặc event checkpoint theo đúng cơ chế vendor; chỉ nâng mốc sau khi dữ liệu đã được lưu/route thành công. Quarantine dữ liệu lạ và có đường replay/reconciliation; không tự tạo confirmed fact.

**Exit:** dữ liệu trùng, đến muộn, thiếu media, token hết hạn, lỗi từng cuộc hội thoại, replay và đổi người gửi đều có kết quả rõ; end-to-end từ kênh pilot đến proposal có source lineage. Kênh thứ hai là tranche riêng sau khi pilot thứ nhất được review. WhatsApp không nằm trong exit gate.

### S6 — Lịch chạy và thông báo có kiểm soát

**Điều kiện mở:** S2–S4 qua review và pilot cho thấy giá trị thực. **Đầu ra:** lịch bền vững, giới hạn đồng thời, pause/kill switch, retry/backoff; outbox cho từng người nhận/kênh với idempotency và trạng thái `PENDING / SENT / FAILED`. Thông báo gửi link đến kết quả đã phân quyền, không gửi toàn bộ nội dung nhạy cảm mặc định.

**Exit:** một nơi nhận lỗi không đánh dấu các nơi khác đã gửi; re-run không spam; lịch không bỏ qua item sau lỗi hoặc partial; tắt AI/schedule vẫn cho phép xem lịch sử và xử lý thủ công.

### S7 — Pilot, quyết định mở rộng và các lựa chọn để sau

**Pilot:** chạy shadow trên một tập ca và một kênh đã được phép, có người review. Đo thời gian rà soát, tỷ lệ kết quả hữu ích, lỗi gắn nguồn, số lần thiếu dữ liệu, chi phí/run, lỗi connector và chi phí vận hành. Ngưỡng chấp nhận do operator chốt trước pilot; không đặt ngưỡng hồi tố. Review độc lập trên source, test, security/privacy và kết quả thật trước khi mở rộng. Deployment/production cần work order riêng.

**Storage local/S3:** chỉ mở nếu có nhu cầu chuyển attachment thật. Khi đó lấy từ CQA ý tưởng dry-run, copy có thể tiếp tục, đọc dự phòng và verify trước khi xóa nguồn; không nhập implementation Go. **MCP:** để sau khi read API, scope, audit và data minimization được chứng minh. **WhatsApp:** chỉ mở lại theo điều kiện ở mục ưu tiên; chi phí vượt giá trị thì loại khỏi scope.

## Các lỗi từ CQA phải tránh

- Không cập nhật `last_sync_at` khi đồng bộ lỗi; dùng checkpoint thành công và receipt từng item (`backend/engine/sync.go`).
- Không tin `conversation_id` trong output AI; kiểm batch ID/scope/đủ/không trùng trước khi ghi (`backend/engine/analyzer.go`).
- Lỗi lưu kết quả phải đổi trạng thái run/item, không chỉ log rồi báo success (`backend/engine/analyzer.go`).
- Trạng thái thông báo thuộc **từng nơi nhận**; một nơi lỗi không được đánh dấu toàn bộ đã gửi (`backend/notifications/dispatcher.go`).
- Bộ lọc nhiều giá trị phải có test API/UI; hàm `splitCSVParam` của CQA hiện trả `nil` kể cả khi parse được input (`backend/api/handlers/results.go`).
- Giá model không biết phải hiện `UNKNOWN`; CQA ghi `CostUSD=0` và tổng UI cộng như chi phí thực (`backend/engine/analyzer.go`, `frontend/src/views/CostLogs.vue`).

## Cổng quyết định và phạm vi chưa được cấp phép

Roadmap này **không cấp quyền** BUILD, gọi provider, tạo credential, kết nối vendor, migration dữ liệu, deploy, merge hoặc đổi Phase 5 thành đang thực hiện. Mỗi S1–S7 cần work order, exact changed set, budget, tiêu chí pass/fail, reviewer độc lập cho R2 và kế hoạch rollback riêng. Nếu S0 không cho thấy giá trị đủ rõ, dừng tại đó. Nếu S2/S3 không giúp người vận hành quyết định nhanh và đúng hơn so với quy trình hiện tại, không mở lịch/notification chỉ vì CQA có tính năng đó.

## Checker Source Read-Ahead Block

Tài liệu kế hoạch này không có checker nội dung riêng. Các gate hiện hành liên quan đến thay đổi tài liệu/continuity là `scripts/check_session_state.py` (canonical state, bootstrap, mirror, required reads), `scripts/generate_catalog.py --check` và `scripts/sync_cvf_catalog_kit.py` (giữ 26 module facts), `scripts/manage_cvf_downstream_catalog.ps1 -Check` (artifact registry/generated index), `scripts/check_cvf_core_machine_inheritance.py --enforce` (pin/provenance), `scripts/check_file_size.py` và workspace doctor. Đây là kiểm tra tính nhất quán của repository, không là bằng chứng chức năng hoặc provider.
