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

## Application memory (P4-A3)

`packages/application-memory` + `workspace_api.application.application_memory`
(tranche `P4A3-APPLICATION-MEMORY-2026-08-21`) thêm session/working memory
advisory, process-local. Nó KHÔNG bao giờ recall memory ngầm vào context hay
P4-A2: mỗi entry chỉ được đọc khi một caller tường minh yêu cầu các entry đã
revalidate (owner → shift/scope → TTL → tombstone → source revalidation →
order → limit). Không episodic/semantic memory, không durable persistence,
không public route. Xem
[`docs/specs/P4A3_APPLICATION_MEMORY_SPEC.md`](../specs/P4A3_APPLICATION_MEMORY_SPEC.md).
P4-A3 đã `FREEZE / CLOSED_BOUNDED`: live proof tường minh dùng một entry đã
admit/re-read làm P4-A2 query sau 7 memory + 6 RAG refusals zero-call, rồi đúng
một HTTP 200 qua P4-A2/AIGateway (`1/1/1`, ABSTAINED). Điều này không biến
explicit caller evidence thành implicit recall hay production-memory claim.
