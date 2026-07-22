# P2-B identity control - live governance evidence receipt

Produced by `scripts/run_identity_live_governance_evidence.py`
(P2B-AUTHENTICATION-REPAIR, SPEC SS7). Sanitized: contains no API key,
no Authorization header, and no JWT secret.

- Generated at: 2026-07-22T17:51:32.530658+00:00
- Provider: Alibaba DashScope (OpenAI-compatible endpoint)
- Model: qwen3.7-max
- Endpoint: https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions

## 1. Identity gate (in-process, real code path)

| Case | Outcome | Detail |
|---|---|---|
| valid_token_admitted | PASS | token decoded to user_id=evidence-operator role=operator; require_action('shift.close') allowed |
| forged_token_refused | PASS | tampered signature rejected: Signature verification failed |

## 2. Real provider call

Reached only because case `valid_token_admitted` passed - the identity
gate is what authorized this call.

- Outcome: **PASS**
- Reached the provider (got any HTTP response): **True**
- HTTP status: 200
- Started at: 2026-07-22T17:51:29.342913+00:00
- Response excerpt: `CVF_IDENTITY_EVIDENCE_OK`

## Claim boundary

This receipt evidences that the `identity` control admits a validly
signed principal and refuses a forged token, and that a real (non-mock) provider call was made and returned the expected response under that gate.
It does NOT evidence approval quorum (High Finding #4), PostgreSQL
production verification, or any AI-gateway capability - all
explicitly out of scope for this tranche.
