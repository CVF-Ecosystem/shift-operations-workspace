# SHIFT OPERATIONS WORKSPACE

## Architecture & Scope Freeze

**Status:** FROZEN BASELINE
**Freeze level:** Architecture, ownership boundary, core workflow, provider contracts
**Implementation status:** Đang build (Phase 1-2 in progress). Trạng thái chi tiết, kiểm chứng được: `docs/catalog/MODULE_CATALOG.md` + `docs/implementation/EXECUTION_ROADMAP.md`. Baseline kiến trúc dưới đây vẫn giữ nguyên/frozen; chỉ dòng trạng thái này được cập nhật để không nói sai sự thật.
**Change policy:** Cho phép điều chỉnh có kiểm soát trong quá trình thực hiện

---

## 1. Định vị sản phẩm

**Shift Operations Workspace** là không gian vận hành theo ca dành cho hoạt động khai thác tàu, bãi, thiết bị và tương tác khách hàng.

Hệ thống thay thế việc sử dụng nhóm chat làm nơi lưu trữ thông tin nghiệp vụ chính, nhưng vẫn giữ trải nghiệm cập nhật nhanh tương tự chat.

Luồng giá trị cốt lõi:

```text
Tin nhắn / Quick Action / Voice / Hình ảnh
                    ↓
        Sự kiện vận hành có cấu trúc
                    ↓
       Theo dõi công việc và trạng thái
                    ↓
        Nhật ký ca và bàn giao ca
                    ↓
          Báo cáo cuối ca
```

Hệ thống không được định vị đơn thuần là:

* Chatbot tóm tắt tin nhắn.
* Ứng dụng chat nội bộ.
* Công cụ thay thế hoàn toàn con người.
* Nền tảng CRM tổng quát.
* Hệ thống ERP cảng hoàn chỉnh.
* Một sản phẩm phụ thuộc vào duy nhất một LLM hoặc nền tảng nhắn tin.

---

## 2. Nguyên tắc kiến trúc đã khóa

```text
1. Mobile PWA và Desktop Web là giao diện vận hành chính.

2. Operations Ledger là nguồn sự thật nghiệp vụ.

3. Tin nhắn gốc là evidence, không mặc nhiên là sự thật đã xác nhận.

4. LLM chỉ tạo proposal, không tự xác nhận sự kiện quan trọng.

5. Shift Operations Workspace phải hoạt động được khi không có LLM.

6. Zalo, WhatsApp, email và các kênh ngoài chỉ là adapter.

7. Không provider nào được trở thành trung tâm kiến trúc.

8. CVF là lớp governance và control bao ngoài ứng dụng.

9. CVF Refinery làm sạch dữ liệu trước khi tạo context cho AI.

10. Mọi kết luận nghiệp vụ phải truy ngược được nguồn và lịch sử phê duyệt.

11. AI failure không được trở thành workspace failure.

12. Core workflow không thay đổi khi thay model, channel, database hoặc deployment provider.
```

---

## 3. Phân định quyền sở hữu

### 3.1. Shift Operations Workspace sở hữu

* Ca ngày và ca đêm.
* Nhân viên và vai trò trong ca.
* Tàu và voyage.
* Khu vực bãi.
* Thiết bị.
* Phòng trao đổi vận hành.
* Quick Actions.
* Operational Events.
* Công việc và trạng thái thực hiện.
* Customer Requests.
* Incident Records.
* Shift Handover.
* Báo cáo cuối ca.
* Dashboard vận hành.
* Operations Ledger.

### 3.2. CVF sở hữu

* Identity boundary.
* Permission boundary.
* Data scope.
* Policy.
* Risk classification.
* Context control.
* Provider authorization.
* Cost và quota.
* Approval gate.
* Evidence requirement.
* Audit.
* Escalation.
* Refusal.
* Termination.
* Freeze.

### 3.3. CVF Refinery sở hữu

* Làm sạch input.
* Chuẩn hóa thời gian.
* Chuẩn hóa thuật ngữ.
* Loại trùng.
* Nhận diện dữ liệu thiếu.
* Phân loại dữ liệu.
* Redaction dữ liệu nhạy cảm.
* Tạo context candidates.
* Đánh dấu mâu thuẫn.
* Giữ liên kết với dữ liệu gốc.

### 3.4. Provider chỉ cung cấp capability

* LLM.
* Speech-to-text.
* OCR và vision.
* Zalo.
* WhatsApp.
* Email.
* SMS.
* Object storage.
* Database service.
* Push notification.
* Search engine.

Provider không sở hữu workflow và không quyết định sự thật nghiệp vụ.

---

## 4. Các khối kiến trúc chính

```text
┌──────────────────────────────────────────────┐
│             USER EXPERIENCE                 │
│                                              │
│ Mobile PWA · Desktop Web · Customer Portal   │
└─────────────────────┬────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────┐
│          SHIFT OPERATIONS WORKSPACE          │
│                                              │
│ Chat · Quick Action · Shift · Task · Event   │
│ Customer Request · Handover · Report         │
└─────────────────────┬────────────────────────┘
                      │
          ┌───────────┴────────────┐
          ▼                        ▼
┌───────────────────────┐  ┌───────────────────────┐
│   CVF CONTROL LAYER   │  │     CVF REFINERY      │
│                       │  │                       │
│ Identity              │  │ Clean                 │
│ Permission            │  │ Normalize             │
│ Policy                │  │ Deduplicate           │
│ Risk                  │  │ Classify              │
│ Approval              │  │ Redact                │
│ Evidence              │  │ Context Candidate     │
│ Audit                 │  │ Conflict Detection    │
└───────────┬───────────┘  └───────────┬───────────┘
            │                          │
            └────────────┬─────────────┘
                         ▼
┌──────────────────────────────────────────────┐
│          AI AND CAPABILITY GATEWAY           │
│                                              │
│ Model Router · Context Builder · Budget      │
│ Structured Output · Validation · Fallback    │
└─────────────────────┬────────────────────────┘
                      ▼
┌──────────────────────────────────────────────┐
│              ADAPTER LAYER                   │
│                                              │
│ Local LLM · API Key · Enterprise Gateway     │
│ Subscription · Zalo · WhatsApp · Email       │
│ Speech · OCR · Storage · Generic Webhook     │
└─────────────────────┬────────────────────────┘
                      ▼
┌──────────────────────────────────────────────┐
│         OPERATIONS & EVIDENCE LEDGER         │
│                                              │
│ Raw Message · Event · Task · Ticket          │
│ Approval · Handover · Report · Audit         │
└──────────────────────────────────────────────┘
```

---

## 5. Core workflow đã khóa

```text
START SHIFT
    ↓
Nhân viên gửi cập nhật
    ↓
Raw input được lưu làm evidence
    ↓
CVF Refinery làm sạch và chuẩn hóa
    ↓
Policy và permission gate
    ↓
Rules hoặc LLM phân tích
    ↓
Structured proposal
    ↓
Schema và truth validation
    ↓
Human approval khi cần
    ↓
Ghi Operations Ledger
    ↓
Theo dõi task, event và customer request
    ↓
Tạo shift summary
    ↓
Bàn giao ca
    ↓
Phê duyệt báo cáo cuối ca
    ↓
Freeze ca
```

Sau khi ca được freeze:

* Không sửa trực tiếp dữ liệu đã xác nhận.
* Mọi thay đổi phải tạo correction record.
* Lưu nội dung trước và sau chỉnh sửa.
* Lưu người sửa, thời gian và lý do.
* Báo cáo liên quan phải được đánh dấu lại phiên bản.

---

## 6. Các bề mặt giao diện chính

### 6.1. Unified Operations Chat

Hỗ trợ:

* Tin nhắn nội bộ.
* Tin từ Customer Portal.
* Tin từ Zalo hoặc WhatsApp khi adapter được bật.
* Voice.
* Hình ảnh.
* File.
* Reply.
* Mention.
* Liên kết với tàu, voyage, bãi, thiết bị hoặc khách hàng.
* Chuyển tin thành event, task hoặc ticket.

Mỗi tin phải hiển thị rõ nguồn:

```text
INTERNAL
CUSTOMER_PORTAL
ZALO
WHATSAPP
EMAIL
GENERIC_WEBHOOK
API
```

### 6.2. Quick Actions

Tối thiểu gồm:

* Báo thiết bị dừng.
* Thiết bị hoạt động lại.
* Báo tình hình tàu.
* Cập nhật sản lượng.
* Báo tình hình bãi.
* Báo sự cố.
* Tạo công việc.
* Ghi nhận yêu cầu khách hàng.
* Ghi công việc tồn.
* Bàn giao ca.

### 6.3. Shift Timeline

Hiển thị sự kiện đã được chuẩn hóa theo thời gian.

### 6.4. Open Work

Hiển thị:

* Công việc đang thực hiện.
* Công việc quá hạn.
* Công việc chờ xác nhận.
* Công việc chuyển ca.
* Người phụ trách.
* Evidence liên quan.

### 6.5. Customer Inbox

Quản lý yêu cầu từ:

* Customer Portal.
* Zalo.
* WhatsApp.
* Email.
* Generic API.

### 6.6. End-Shift Report

Tạo bản nháp từ các dữ liệu đã xác nhận, không từ toàn bộ raw chat.

### 6.7. Leadership Dashboard

Chỉ hiển thị dữ liệu theo quyền và trạng thái xác nhận.

---

## 7. Operations Ledger

Operations Ledger là nguồn sự thật của ứng dụng.

Các record chính:

```text
Shift
Message
Attachment
Operational Event
Task
Customer Request
Incident
Handover Item
Report
Approval
Correction
Audit Record
```

Mỗi record quan trọng phải có:

```text
Record ID
Workspace
Shift
Source
Created by
Created time
Status
Evidence links
Confidence
Approval state
Version
Audit history
```

---

## 8. Trạng thái dữ liệu

Dữ liệu phải được phân biệt rõ:

```text
RAW
NORMALIZED
PROPOSED
CONFIRMED
REJECTED
CORRECTED
FROZEN
```

Không được dùng dữ liệu `RAW` hoặc `PROPOSED` như dữ liệu chính thức trên báo cáo lãnh đạo.

---

## 9. Risk và approval class

| Risk | Nội dung                             | Cơ chế                     |
| ---- | ------------------------------------ | -------------------------- |
| R0   | Tin nhắn thông thường                | Lưu tự động                |
| R1   | Cập nhật tiến độ                     | Người gửi xác nhận khi cần |
| R2   | Downtime, thay đổi kế hoạch          | Ca trưởng xác nhận         |
| R3   | Khiếu nại, thiệt hại, hàng nguy hiểm | Dual approval              |
| R4   | Tai nạn, pháp lý, công bố ra ngoài   | Escalation bắt buộc        |

Risk class quyết định:

* Capability được sử dụng.
* Provider được phép gọi.
* Dữ liệu được phép truyền.
* Evidence bắt buộc.
* Người phê duyệt.
* Quyền gửi outbound.

---

## 10. Chế độ AI được khóa mở sẵn

```text
NO_AI
RULES_ONLY
LOCAL_MODEL
BRING_YOUR_OWN_KEY
ENTERPRISE_GATEWAY
SUBSCRIPTION_CONNECTOR
HYBRID_ROUTING
```

### Quy tắc subscription

Chỉ được sử dụng khi provider có cơ chế chính thức:

* OAuth.
* Account delegation.
* SDK chính thức.
* Enterprise connector.
* Điều khoản sử dụng phù hợp.

Không sử dụng:

* Cookie extraction.
* Browser session scraping.
* Reverse-engineered token.
* Automation điều khiển giao diện chatbot cá nhân.

---

## 11. Degraded mode

```text
Cloud model unavailable
        ↓
Local model

Local model unavailable
        ↓
Rules-only

Rules không đủ
        ↓
Quick Action hoặc human input
```

Các chức năng sau phải luôn hoạt động:

* Đăng nhập.
* Bắt đầu ca.
* Gửi cập nhật.
* Quick Action.
* Lưu evidence.
* Tạo task.
* Giao ca.
* Tạo báo cáo theo template.
* Phê duyệt.
* Audit.

---

## 12. Channel Integration Edge

Các kênh ngoài không kết nối trực tiếp với chatbot hoặc database nghiệp vụ.

```text
External channel
       ↓
Webhook Gateway
       ↓
Signature verification
       ↓
Raw payload preservation
       ↓
Deduplication
       ↓
Attachment scanning
       ↓
Canonical Message Contract
       ↓
Identity and conversation mapping
       ↓
Unified Operations Chat
```

Các adapter mở sẵn:

```text
INTERNAL_PWA
CUSTOMER_PORTAL
GENERIC_WEBHOOK
ZALO
WHATSAPP
EMAIL
SMS
```

Zalo và WhatsApp không phải điều kiện bắt buộc để hệ thống hoạt động.

---

## 13. Provider contract

Các LLM provider phải hỗ trợ contract thống nhất:

```text
generate_structured_output()
classify()
extract_entities()
summarize()
health_check()
estimate_cost()
report_usage()
cancel_request()
```

Các channel adapter phải hỗ trợ:

```text
verify_webhook()
parse_message()
download_attachment()
send_message()
get_delivery_status()
health_check()
refresh_credentials()
```

Không viết business workflow riêng theo từng provider.

---

## 14. Context control

Không gửi toàn bộ lịch sử ca vào LLM.

Context Builder chỉ được phép lấy:

```text
Current message
Relevant nearby messages
Active shift
Selected vessel/voyage
Valid equipment registry
Open events
Related customer request
Applicable policy
Required output schema
```

Context phải đi qua:

```text
Permission check
Data classification
PII redaction
Provider policy
Token budget
Risk policy
Audit preparation
```

---

## 15. Các guard CVF áp dụng

### `domain_lock`

Giới hạn chatbot trong các domain đã cho phép.

### `contract_runtime`

Mỗi AI task phải có input, output, capability, budget, timeout và failure contract.

### `contamination_guard`

Nội dung từ channel ngoài luôn được xem là dữ liệu không tin cậy.

### `refusal_router`

Yêu cầu vượt quyền phải được từ chối hoặc chuyển phê duyệt có lý do.

### `creative_control`

Phân biệt rõ:

```text
Confirmed fact
Inferred proposal
Unverified statement
Missing information
```

### Evidence gate

Không xác nhận sự kiện quan trọng khi không có evidence tối thiểu.

### Cost and termination guard

Mỗi AI task phải có giới hạn token, timeout, retry và kill switch.

---

## 16. Phạm vi MVP đã khóa

### Bao gồm

* Mobile PWA.
* Desktop Web.
* Đăng nhập và phân quyền.
* Quản lý ca.
* Unified Operations Chat.
* Quick Actions.
* Shift Timeline.
* Operations Event Ledger.
* Customer Requests.
* Open Work.
* Shift Handover.
* End-Shift Report.
* PDF và Excel export.
* Audit log.
* Generic Webhook Adapter.
* Mock Zalo Adapter.
* Mock WhatsApp Adapter.
* Provider Registry.
* BYOK.
* OpenAI-compatible connection.
* Non-compatible provider contract.
* Local model contract.
* No-AI và rules-only mode.
* CVF Application Profile.
* CVF Refinery integration boundary.
* Risk và approval gates.
* Connection health.
* Budget và kill switch.

### Chưa bao gồm trong MVP

* ERP đầy đủ.
* CRM tổng quát.
* TOS replacement.
* Computer vision tự động kết luận sự cố.
* KPI nhân viên dựa trên số lượng tin nhắn.
* Tự động xử lý sự cố không có human approval.
* Multi-agent orchestration phức tạp.
* Prediction và optimization nâng cao.
* Tích hợp thật với mọi nền tảng ngay từ đầu.
* Đọc tài khoản Zalo hoặc WhatsApp cá nhân.
* Phụ thuộc bắt buộc vào cloud LLM.

---

## 17. Điều kiện nghiệm thu kiến trúc

Kiến trúc chỉ được xem là triển khai đúng khi:

```text
1. Thay LLM provider không sửa business workflow.

2. Tắt LLM, workspace vẫn vận hành được.

3. Tắt Zalo/WhatsApp, workspace vẫn vận hành được.

4. Mọi dòng báo cáo truy ngược được evidence.

5. Raw message không tự trở thành confirmed event.

6. Event quan trọng đi qua đúng approval gate.

7. Dữ liệu cloud và local được kiểm soát theo policy.

8. API key không xuất hiện ở frontend.

9. Provider failure có fallback rõ ràng.

10. Ca đã freeze không bị sửa âm thầm.

11. Context gửi tới AI có scope và audit record.

12. Channel payload không thể điều khiển system instruction.

13. Core application không sở hữu logic riêng của provider.

14. CVF kiểm soát vòng ngoài nhưng không micromanage suy luận của model.
```

---

## 18. Change control

Baseline này được khóa nhưng không bất biến tuyệt đối.

Mọi thay đổi kiến trúc phải tạo một Change Record:

```text
Change ID
Vấn đề cần giải quyết
Thành phần bị ảnh hưởng
Lý do thay đổi
Tác động tới architecture
Tác động tới security
Tác động tới data
Tác động tới CVF controls
Migration requirement
Decision
Owner approval
```

Phân loại thay đổi:

### Implementation Adjustment

Không thay đổi ownership, contract hoặc core workflow.

Có thể thực hiện trong phase tương ứng.

### Architecture Amendment

Thay đổi module boundary, contract hoặc luồng dữ liệu.

Phải review trước khi thực hiện.

### Scope Expansion

Bổ sung sản phẩm hoặc nghiệp vụ mới.

Không được đưa âm thầm vào MVP.

### Owner Directive

Quyết định mới của chủ dự án.

Được ưu tiên nhưng phải ghi rõ phần baseline bị thay thế.

---

## 19. Trình tự thực hiện tiếp theo

```text
FREEZE BASELINE
      ↓
Khóa treeview repository
      ↓
Viết README định vị
      ↓
Viết Architecture Map
      ↓
Viết CVF Application Profile
      ↓
Khóa contracts và schemas
      ↓
Chia implementation phases
      ↓
Viết work orders
      ↓
Build
      ↓
Review
      ↓
Freeze release
```

---

## 20. Freeze statement

Kể từ baseline này:

> Shift Operations Workspace được xác định là một ứng dụng nghiệp vụ vận hành theo ca, sử dụng Operations Ledger làm nguồn sự thật; Mobile PWA và Desktop Web làm giao diện chính; CVF làm lớp governance; CVF Refinery làm sạch dữ liệu và context; LLM và external channels được cung cấp qua adapter contracts có thể thay thế.

Mọi đề xuất sau này phải được đánh giá dựa trên baseline này và không được làm sai lệch các nguyên tắc đã khóa nếu chưa có Architecture Amendment được phê duyệt.
