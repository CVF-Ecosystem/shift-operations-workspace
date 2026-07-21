# Shift Operations Workspace

Shift Operations Workspace là không gian vận hành theo ca dành cho hoạt động khai thác tàu, bãi, thiết bị và tương tác khách hàng. Hệ thống giữ trải nghiệm cập nhật nhanh tương tự ứng dụng chat, nhưng chuyển thông tin thành sự kiện vận hành có cấu trúc, công việc cần theo dõi, nhật ký ca, bàn giao và báo cáo cuối ca.

## Kiến trúc đã khóa

- **Mobile PWA và Desktop Web** là giao diện vận hành chính.
- **Operations Ledger** là nguồn sự thật nghiệp vụ.
- **Tin nhắn gốc** được giữ làm evidence; không tự động trở thành sự thật đã xác nhận.
- **CVF** kiểm soát identity, scope, policy, risk, approval, evidence, cost, refusal, audit và freeze.
- **CVF Refinery** làm sạch dữ liệu và tạo context candidates trước khi dữ liệu đi tới rules hoặc LLM.
- **LLM và external channels** chỉ là capability thông qua adapter contracts có thể thay thế.
- Hệ thống vẫn vận hành khi AI, Zalo, WhatsApp hoặc Internet bên ngoài không khả dụng.

## Core workflow

```text
START SHIFT
    ↓
Record operational updates
    ↓
Preserve raw evidence
    ↓
Normalize through CVF Refinery boundary
    ↓
Apply CVF policy and permission gates
    ↓
Rules or LLM produce structured proposals
    ↓
Validate schema and operational truth
    ↓
Human approval when required
    ↓
Write confirmed records to Operations Ledger
    ↓
Track events, tasks and customer requests
    ↓
Prepare shift handover
    ↓
Generate and approve end-shift report
    ↓
FREEZE SHIFT
```

## Main operational domains

- Shift operations
- Vessel and voyage operations
- Yard operations
- Equipment downtime
- Operational incidents
- Customer requests
- Open work
- Shift handover
- End-shift reporting

## Repository map

```text
apps/            Deployable applications
packages/        Domain modules, contracts, bridges and adapters
database/        Schema, migrations, views, functions and fixtures
infrastructure/  Deployment, monitoring, backup and runtime assets
docs/            Canonical product and engineering documentation
tests/           Cross-module, security, resilience and conformance tests
fixtures/        Provider, channel, refinery and domain test data
examples/        Reference operational scenarios
scripts/         Bootstrap, development, database, security and release tools
```

## Front door cho agent/dev (đọc trước tiên)

Mọi agent (bất kỳ provider nào) và mọi dev bắt đầu tại **[CONTRIBUTING.md](CONTRIBUTING.md)**
— front door governance trung lập provider. Nó dẫn tới session state đang hoạt
động (`SESSION/ACTIVE_SESSION_STATE.json`), session memory, và handoff hiện
hành. Không có file điểm-vào riêng theo provider.

## Module Catalog (đọc trước khi làm việc)

Trước khi sửa hoặc bổ sung bất kỳ phần nào, mọi agent/dev đọc **catalog** để biết
chính xác module nào đã có code, module nào chỉ là contract/stub, và CVF control
nào đã được thực thi ở đâu:

- [docs/catalog/MODULE_CATALOG.md](docs/catalog/MODULE_CATALOG.md) — bản người đọc (sinh tự động).
- [docs/catalog/MODULE_REGISTRY.json](docs/catalog/MODULE_REGISTRY.json) — machine source-of-truth (agent đọc/ghi).
- Khi hoàn tất một phần: cập nhật entry của module trong `MODULE_REGISTRY.json`,
  rồi chạy `python scripts/generate_catalog.py --write` để làm mới catalog + số liệu.
- CVF control → điểm enforce: [docs/cvf/CVF_CONTROL_MAPPING.md](docs/cvf/CVF_CONTROL_MAPPING.md).

Xem [TREEVIEW.md](TREEVIEW.md) để xem cây thư mục thô và [docs/implementation/IMPLEMENTATION_PHASES.md](docs/implementation/IMPLEMENTATION_PHASES.md) để xem kế hoạch 5 phase.

## AI operating modes

```text
NO_AI
RULES_ONLY
LOCAL_MODEL
BRING_YOUR_OWN_KEY
ENTERPRISE_GATEWAY
SUBSCRIPTION_CONNECTOR
HYBRID_ROUTING
```

`SUBSCRIPTION_CONNECTOR` chỉ được bật khi nhà cung cấp hỗ trợ chính thức OAuth, account delegation, enterprise connector hoặc cơ chế tương đương. Không dùng cookie extraction, browser session scraping hoặc reverse-engineered tokens.

## Data states

```text
RAW → NORMALIZED → PROPOSED → CONFIRMED
                      ├→ REJECTED
                      └→ CORRECTED → FROZEN
```

Chỉ dữ liệu `CONFIRMED`, `CORRECTED` hợp lệ hoặc `FROZEN` mới được dùng làm official operational fact.

## Local development

Yêu cầu tham chiếu:

- Python 3.12+
- Node.js 22+
- pnpm 9+
- Docker + Docker Compose

```bash
cp .env.example .env
make bootstrap
make dev
```

API mặc định: `http://localhost:8000`  
Integration Edge: `http://localhost:8100`  
Web: `http://localhost:5173`

## Implementation status

Repository này cung cấp:

- Tài liệu kiến trúc đầy đủ cho 5 phase.
- JSON Schemas và CVF policy profiles.
- Skeleton chạy được cho FastAPI API, worker và Integration Edge.
- PWA React/Vite tối thiểu.
- Migration PostgreSQL nền.
- Mock providers, mock channels và test fixtures.
- Test mẫu cho lifecycle, freeze, webhook verification và conformance.

Các connector Zalo/WhatsApp hiện là **mock/conformance skeleton**, không tuyên bố production-ready cho đến khi có credentials, phê duyệt và kiểm thử với API chính thức của từng nhà cung cấp.

## Change control

Architecture baseline, repository structure và implementation phases đã được khóa. Mọi thay đổi ảnh hưởng module ownership, contract, data flow, CVF boundary hoặc dependency direction phải dùng ADR/Change Record trong `docs/decisions/`.

## Author / Owner

**TIEN-TAN THUAN PORT**
