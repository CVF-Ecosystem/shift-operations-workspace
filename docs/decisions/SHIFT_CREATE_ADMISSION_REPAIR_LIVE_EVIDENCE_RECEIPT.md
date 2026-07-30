# Shift create admission repair - live governance evidence receipt

Overall outcome: PASS

Produced by `scripts/run_shift_create_live_governance_evidence.py` via `scripts/_shift_create_live_evidence_support.py` (SHIFT-CREATE-ADMISSION-REPAIR-2026-07-29, SPEC R12-R14). Sanitized: contains no API key, no Authorization header, no JWT, no raw secret, no URL userinfo/query/fragment.

- Generated at: 2026-07-30T07:04:08.723124+00:00
- Provider: Alibaba DashScope (OpenAI-compatible endpoint)
- Model: qwen3.7-max
- Endpoint (host only): https://ws-remplsp27g5oicq1.ap-southeast-1.maas.aliyuncs.com

## 1. Refusal cases (real HTTP route chain, observed provider-call delta)

| Case | Outcome | Detail | Provider calls |
|---|---|---|---|
| anonymous_create_rejected | PASS | refused: status 401 | 0 |
| malformed_token_create_rejected | PASS | refused: status 401 | 0 |
| viewer_role_create_rejected | PASS | refused: status 403 | 0 |
| invalid_window_create_rejected | PASS | refused: status 422 | 0 |

## 2. Genuine admitted create (real HTTP route chain)

- valid operator JWT (shift-ev-op) admitted POST /shifts via a minted token and a real HTTP request, persisting exactly one shift and one exactly-field-matched actor-bound shift.create audit

## 3. Real provider call

Reached only because the create above genuinely admitted a valid operator JWT and persisted the shift plus its actor-bound audit.

- Outcome: **PASS**
- Reached the provider (got any HTTP response): **True**
- HTTP status: 200
- Started at: 2026-07-30T07:04:03.982154+00:00
- Response excerpt: `CVF_SHIFT_CREATE_EVIDENCE_OK`

## 4. Provider-call count (observed, reset per invocation)

- Total provider calls made by this run: **1**
- Expected: 0 for every refusal case above, exactly 1 after the genuine admitted create.

## Claim boundary

This receipt evidences that POST /shifts's real identity/permission gate correctly refuses anonymous, malformed-token, insufficient-role and invalid-window create attempts before any provider call, and correctly admits a genuine valid-operator-JWT create through the real HTTP route chain, persisting exactly one shift and one actor-bound audit record. It does NOT evidence that the production POST /shifts endpoint calls a provider in production (it does not), does not evidence message-admission identity, and does not evidence PostgreSQL production readiness.
