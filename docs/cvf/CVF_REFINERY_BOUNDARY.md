# CVF Refinery Boundary

CVF Refinery làm sạch và chuẩn hóa dữ liệu **trước khi** dữ liệu đi tới rules
hoặc LLM, nhưng Refinery **không** confirm truth, **không** sở hữu domain
workflow, và **không** xóa raw source.

## Refinery sở hữu

```text
Clean input · Normalize time · Normalize terminology · Deduplicate
Detect missing data · Classify · Redact sensitive data
Produce context candidates · Flag conflicts · Keep link to raw source
```

## Ranh giới (đã khóa)

- Input từ channel ngoài luôn là **untrusted** (contamination_guard).
- Refinery tạo *context candidates*, không tạo *confirmed facts*.
- Raw message được giữ làm evidence với retention theo `data-policy.yaml`
  (`raw_message_retention_days`).
- Redaction/classification kết quả cấp cho `data_scope` gate quyết định nơi dữ
  liệu được phép gửi.

## Trạng thái

Hợp đồng boundary: `packages/refinery-bridge/contracts/refinery_contract.yaml`
(contract-only). Khi triển khai, refinery-bridge gọi `cvf_runtime/data_scope.py`
để phân loại và `cvf_runtime` redaction trước khi context tới AI. Xem
[CVF_CONTROL_MAPPING.md](CVF_CONTROL_MAPPING.md).
