# Provider Governance

Provider (LLM, speech, OCR, channel, storage...) **không phải trust source** và
không sở hữu workflow. Việc gọi provider bị kiểm soát bởi data class, budget,
health, capability và policy. Credentials chỉ ở backend, không lộ ra frontend.

## Provider contract

LLM provider phải hỗ trợ contract thống nhất
(`packages/ai-gateway/contracts/provider_interface.py`):

```text
generate_structured_output() · classify() · extract_entities() · summarize()
health_check() · estimate_cost() · report_usage() · cancel_request()
```

Không viết business workflow riêng theo từng provider.

## Governance gates áp cho provider call

- **Data placement**: `cvf_runtime/data_scope.py · assert_placement_allowed` —
  classification nào được gửi tới external/enterprise/local.
- **Budget/kill switch**: `cvf_runtime/budget.py · assert_within_budget`.
- **Termination**: `cvf_runtime/termination.py` — timeout, token limit, repeated
  failures, kill switch.
- **Provider authorization / subscription rule**: chỉ dùng cơ chế chính thức
  (OAuth, delegation, SDK, enterprise connector). Không cookie extraction, session
  scraping hay reverse-engineered token.

## Trạng thái

Các gate trên đã có code + test. `ai-gateway` (model router) và `ai-providers`
(adapter) hiện contract-only/stub; chúng sẽ gọi các gate này khi AI mode ngoài
`NO_AI` được bật. Xem [CVF_CONTROL_MAPPING.md](CVF_CONTROL_MAPPING.md).
