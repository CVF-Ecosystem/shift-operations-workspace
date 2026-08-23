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
(`docs/decisions/P4A_AI_GATEWAY_LIVE_EVIDENCE_RECEIPT.md`). `ai-providers`
(production adapter) vẫn stub — P4-B còn mở. Xem
[CVF_CONTROL_MAPPING.md](CVF_CONTROL_MAPPING.md).

P4-A đã nhận independent final `REVIEW_PASS` và `CLOSED_BOUNDED` sau
replacement live proof trên Python 3.13.12/Pydantic 2.10.6; sáu refusal case
zero-call và đúng một provider attempt HTTP 200. Closure này không nâng
library caller thành application/production caller.

P4-A2 governed RAG (`packages/governed-rag` +
`workspace_api.application.governed_rag.execute_governed_rag`, tranche
`P4A2-GOVERNED-RAG-2026-08-21`) is now the first real application caller of
`AIGateway`: it consumes only P4-A1's positive evidence, builds/validates a
deterministic ephemeral hybrid index, screens for prompt injection, applies
independently-provable extractive minimization, and dispatches the injected
gateway at most once, with strict post-dispatch citation-membership
validation. `GovernedRAG` now binds `placement` at construction from the
real adapter wiring (P4A2-REV-F3 repair) rather than hardcoding it, and
independently re-verifies corpus/authorization-scope equality (F4), context
byte/token facts from the canonical dispatched structure (F5), receipt
integrity/terminal-grammar via the model's own validator (F6), and deep
P4-A1 nested-model recomputation (F7) - see the worker-return document for
the full per-finding evidence. Independent final review returned `REVIEW_PASS`
without finding or waiver and status is `FREEZE / CLOSED_BOUNDED`. Replacement
live proof recorded six zero-call refusals followed by exactly one external
HTTPS POST at HTTP 200, outcome `ABSTAINED`, and secret scan NONE. This
still does not claim a public API/UI route, general embeddings,
operational-corpus RAG, durable usage accounting, or production readiness;
see `docs/specs/P4A2_GOVERNED_RAG_SPEC.md` and
`docs/decisions/DESIGN_2026-08-21_P4A2_GOVERNED_RAG.md` for the exact claim
boundary. The current live-evidence receipt is
`docs/decisions/P4A2_GOVERNED_RAG_LIVE_EVIDENCE_RECEIPT.md`; raw SHA-256 is
`e41549c912020d74e141dbb695da07da0e676f69b7fdf063a4c5b1aba293fb83`
and universal-newline LF SHA-256 is
`7bdf8739c85ccfe216baccd8c1004e7d67068d7ac94b0545949b473239d55bf7`.
No additional provider call is authorized.

P4-A3 application memory (`packages/application-memory`, tranche
`P4A3-APPLICATION-MEMORY-2026-08-21`) is provider-neutral: the package imports
no provider SDK and performs zero provider/network calls. BUILD made no call.
After non-consuming review passed, separate operator authority opened the
existing `scripts/run_p4a3_application_memory_live_evidence.py` for exactly
one synthetic call. It proved seven memory and six inherited P4-A2 refusals
zero-call, then one admitted/re-read entry gated exactly one external HTTPS
POST through P4-A2/AIGateway: HTTP 200, physical/adapter/gateway `1/1/1`,
ABSTAINED, all nine stages PASS, secret scan NONE. Receipt:
`docs/decisions/P4A3_APPLICATION_MEMORY_LIVE_EVIDENCE_RECEIPT.md`. Authority
is exhausted; this is explicit-caller evidence, not implicit recall or a
production provider adapter. See `docs/specs/P4A3_APPLICATION_MEMORY_SPEC.md`.

P4-B AI provider foundation (`packages/ai-providers`, tranche
`P4B-AI-PROVIDERS-2026-08-21`) has been through two independent completion
rereview rounds. Round 1 (`REVIEW_FAIL / REPAIR_REQUIRED`, findings
P4B-REV-F1..F6) and its repair closed F2/F3; rereview round 1
(`REREVIEW_FAIL / RESIDUAL_REPAIR_REQUIRED`) retained residual findings
F1-R1/F4-R1/F5-R1/F6-R1, repaired in round 2. `ProviderModeService.execute`
is the sole mode-selection entry point: zero-call `NO_AI`; deterministic
local `RULES_ONLY` whose immutable rule set rejects ambiguous/duplicate
rules at construction, whose exact-scalar fact matching requires matching
runtime type (no bool/int confusion), and whose winning output is validated
by the real `ai_gateway.validation` function, never falling through to
external AI on schema failure; a `MockProviderAdapter` that structurally
requires `TEST_ONLY_COMPONENT_TEST`/`evidence_eligible=False` authorization
reconstructed from its own primitive dump (never trusting `isinstance`
alone) and is excluded from `ProviderAdapterRegistry`'s production/evidence
projections regardless of caller label; and `EXTERNAL_AI` delegation exactly
once to an injected P4-A `AIGateway`, refusing zero-call on any
outer/nested provider/model/placement/context-digest identity mismatch AND,
independently, on the load-bearing `ProviderAdapterRegistry` lookup, which
(P4B-REV-F1-R1) now permits delegation ONLY when registry-owned metadata is
EXACTLY `kind=EXTERNAL_GATEWAY` AND `evidence_eligible=True` - every other
kind/eligibility combination, including a registered `EXTERNAL_GATEWAY`
entry with `evidence_eligible=False` and a `RULES_ONLY`/`NO_AI` entry
wrongly marked eligible, refuses before the gateway with zero calls.
`ProviderAdapterRegistry.register` and `ProviderModeService.execute`
(P4B-REV-F4-R1) both fully reconstruct/revalidate their untrusted input from
its primitive dump before storing or dispatching - a `model_construct`-
bypassed registry entry or a request whose facts contain a JSON-invalid
value (e.g. a tuple) is rejected with the documented typed error, never
partially stored or silently routed to the wrong outcome. `execute` returns
a strict `ProviderModeResultV1` envelope binding the releasable output
(present only for `RULES_MATCHED`/`EXTERNAL_ACCEPTED`, deep-copy isolated,
digest-bound to the receipt) alongside the sanitized receipt - refusal
outcomes carry no output. Receipts bind digests/counters, recompute their
own hash, and enforce exact cross-field grammar per terminal outcome
(P4B-REV-F5-R1: rule_id present iff a rule actually matched, rules_evaluated
>= 1 whenever rule_id is present, provider_id/model_id present whenever a
gateway call was attempted, and `EXTERNAL_IDENTITY_MISMATCH` requires the
genuine `ai_mode=EXTERNAL_AI` rather than the `UNKNOWN` sentinel); the
published `provider_modes.schema.json` carries matching conditional grammar
so Pydantic and the schema stay mutually exhaustive. `workspace_api.
application.ai_provider_modes` is a no-route, no-persistence composition
function only - not yet wired to any application caller. BUILD and both
repair rounds made zero provider/install/database/commit/push/deployment
calls; the live-evidence support/runner pair's `--refusals-only` rehearsal
is credential-independent and model-selection-independent; its admitted
(consuming) branch (P4B-REV-F6-R1) is now real, tested one-call mechanics -
a hard one-attempt call budget, last-moment credential read, one physical
HTTPS POST, no retry - wired into the runner but still never executed
during BUILD/repair, pending separate post-review authority. Disposition
`READY_FOR_REREVIEW_ROUND_2`; no production adapter, automatic routing,
durable usage/audit, public API/UI, deployment or production-readiness
claim.
