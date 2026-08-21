# Provider Governance

Provider (LLM, speech, OCR, channel, storage...) **không phải trust source** và
không sở hữu workflow. Việc gọi provider bị kiểm soát bởi data class, budget,
health, capability và policy. Credentials chỉ ở backend, không lộ ra frontend.

## Provider contract

LLM provider phải hỗ trợ `AIProvider` protocol thống nhất
(`packages/ai-gateway/contracts/provider_interface.py`, re-export từ
`ai_gateway.provider`):

```text
generate_structured_output() · health_check() · cancel_request()
```

`AIGateway.execute` (`ai_gateway.service`) là sole dispatch point: gọi provider
đã đăng ký qua `ProviderRegistry` (explicit, deterministic — không auto-route),
đúng một physical attempt mỗi lần thực thi, không retry trong tranche này.
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

Các gate trên đã có code + test, và từ P4-A (2026-08-20) có **real library
caller thật**: `ai_gateway.service.AIGateway.execute` gọi trực tiếp
`assert_placement_allowed`, `assert_within_budget`, `assert_not_terminated`
theo đúng thứ tự trước khi dispatch — chứng minh bằng
`tests/unit/test_p4a_gateway_dependency_boundaries.py` (identity check với hàm
gốc `cvf_runtime`) và một live evidence run thật
(`docs/decisions/P4A_AI_GATEWAY_LIVE_EVIDENCE_RECEIPT.md`). Đây vẫn là **library
call site có giới hạn rõ**: chưa có application/API caller nào trong
`apps/workspace-api` gọi gateway này; `ai-providers` (production adapter) vẫn
stub — P4-B còn mở. Không claim RAG (P4-A2), durable usage accounting, hay
production readiness. Xem [CVF_CONTROL_MAPPING.md](CVF_CONTROL_MAPPING.md).

P4-A đã nhận independent final `REVIEW_PASS` và `CLOSED_BOUNDED` sau
replacement live proof trên Python 3.13.12/Pydantic 2.10.6; sáu refusal case
zero-call và đúng một provider attempt HTTP 200. Closure này không nâng
library caller thành application/production caller.
