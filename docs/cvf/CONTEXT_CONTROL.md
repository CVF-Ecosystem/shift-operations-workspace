# Context Control

Không gửi toàn bộ lịch sử ca vào LLM. Context Builder chỉ được lấy phần dữ liệu
liên quan, đã qua permission + classification + redaction + budget.

## Context Builder được phép lấy

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

## Context phải đi qua

```text
Permission check      → cvf_runtime/permission.py
Data classification   → cvf_runtime/data_scope.py
PII redaction         → CVF Refinery (refinery-bridge, contract-only)
Provider policy       → data_scope external_ai rule
Token budget          → cvf_runtime/budget.py
Risk policy           → cvf_runtime/risk.py
Audit preparation     → cvf_runtime/audit.py
```

## Trạng thái

`data_scope`, `budget`, `permission`, `risk`, `audit` gate đã tồn tại và có
test. Context Builder tổng hợp (`ai-gateway`) và Refinery redaction
(`refinery-bridge`) hiện là contract-only — sẽ gọi các gate này khi một AI mode
ngoài `NO_AI` được bật. Xem [CVF_CONTROL_MAPPING.md](CVF_CONTROL_MAPPING.md).
