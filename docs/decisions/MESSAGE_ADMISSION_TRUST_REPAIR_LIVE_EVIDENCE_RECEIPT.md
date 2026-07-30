# Message admission trust repair - live governance evidence receipt

Overall outcome: PASS

Produced by `scripts/run_message_admission_live_governance_evidence.py` via `scripts/_message_admission_live_evidence_support.py` (MESSAGE-ADMISSION-TRUST-REPAIR-2026-07-30, SPEC R16-R18). Sanitized: contains no API key, no Authorization header, no JWT, no raw secret, no URL userinfo/query/fragment.

- Generated at: 2026-07-30T12:19:37.031585+00:00
- Provider: Alibaba DashScope (OpenAI-compatible endpoint)
- Model: qwen3.7-max
- Endpoint (host only): https://ws-remplsp27g5oicq1.ap-southeast-1.maas.aliyuncs.com

## 1. Refusal cases (real HTTP route chain, observed provider-call delta)

| Case | Outcome | Detail | Provider calls |
|---|---|---|---|
| anonymous_create_rejected | PASS | refused: status 401 | 0 |
| malformed_token_create_rejected | PASS | refused: status 401 | 0 |
| viewer_role_create_rejected | PASS | refused: status 403 | 0 |
| sender_mismatch_create_rejected | PASS | refused: status 403 | 0 |
| non_internal_source_create_rejected | PASS | refused: status 422 | 0 |
| unknown_shift_create_rejected | PASS | refused: status 404 | 0 |
| frozen_shift_create_rejected | PASS | refused: status 409 | 0 |

## 2. Genuine admitted create (real HTTP route chain)

- valid operator JWT (msg-ev-op) admitted POST /messages via a minted token and a real HTTP request, persisting exactly one message and one exactly-field-matched actor-bound message.create audit

## 3. Real provider call

Reached only because the create above genuinely admitted a valid operator JWT and persisted the message plus its actor-bound audit.

- Outcome: **PASS**
- Reached the provider (got any HTTP response): **True**
- HTTP status: 200
- Started at: 2026-07-30T12:19:32.983411+00:00
- Response excerpt: `CVF_MESSAGE_ADMISSION_EVIDENCE_OK`

## 4. Provider-call count (observed, reset per invocation)

- Total provider calls made by this run: **1**
- Expected: 0 for every refusal case above, exactly 1 after the genuine admitted create.

## Claim boundary

This receipt evidences that internal POST /messages's real identity/permission/provenance gate correctly refuses anonymous, malformed-token, insufficient-role, sender-mismatch, non-internal-source, unknown-shift and frozen-shift create attempts before any provider call, and correctly admits a genuine valid-operator-JWT create through the real HTTP route chain, persisting exactly one message and one actor-bound audit record. It does NOT evidence external/channel message ingestion, the Canonical Message Contract, or PostgreSQL production readiness.
