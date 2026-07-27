# P2-A handover vertical - live governance evidence receipt

Overall outcome: PASS

Produced by `scripts/run_handover_live_governance_evidence.py` via `scripts/_handover_live_evidence_support.py` (P2A-HANDOVER-VERTICAL, SPEC R16/R17). Sanitized: contains no API key, no Authorization header, no JWT, no raw secret, no URL userinfo/query/fragment.

- Generated at: 2026-07-27T13:25:39.919475+00:00
- Provider: Alibaba DashScope (OpenAI-compatible endpoint)
- Model: qwen3.7-max
- Endpoint (host only): https://dashscope-intl.aliyuncs.com

## 1. Freeze-readiness gate-refusal cases (real HTTP route chain, observed provider-call delta)

| Case | Outcome | Detail | Provider calls |
|---|---|---|---|
| missing_handover_freeze_rejected | PASS | refused: status 409 | 0 |
| reviewed_only_handover_freeze_rejected | PASS | refused: status 409 | 0 |
| self_acknowledgement_rejected | PASS | refused: status 409 | 0 |
| stale_snapshot_freeze_rejected | PASS | refused: status 409 | 0 |

## 2. Genuine review, distinct acknowledgement and freeze (real HTTP route chain)

- distinct authenticated reviewer (hov-ev-sup1) and receiver (hov-ev-sup2) satisfied review/acknowledgement via minted JWTs and HTTP requests, then freeze succeeded through the real open_handover_items_linked prerequisite plus the report_approved override

## 3. Real provider call

Reached only because the freeze above genuinely satisfied the real open_handover_items_linked prerequisite.

- Outcome: **PASS**
- Reached the provider (got any HTTP response): **True**
- HTTP status: 200
- Started at: 2026-07-27T13:25:36.090310+00:00
- Response excerpt: `CVF_HANDOVER_EVIDENCE_OK`

## 4. Provider-call count (observed, reset per invocation)

- Total provider calls made by this run: **1**
- Expected: 0 for every gate-refusal case above, exactly 1 after the genuine freeze.

## Claim boundary

This receipt evidences that the handover vertical's real `open_handover_items_linked` freeze prerequisite correctly refuses a missing handover, a DRAFT/REVIEWED-only handover, a self-acknowledgement attempt and a stale source snapshot before any provider call, and correctly admits a genuine, distinct-receiver acknowledged handover through the real HTTP route chain. It does NOT evidence that any production endpoint calls a provider in production (none do), and it does not evidence PostgreSQL production readiness.
