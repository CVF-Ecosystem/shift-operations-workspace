# P2-C read slice - live governance evidence receipt

Overall outcome: PASS

Produced by `scripts/run_p2c_read_live_governance_evidence.py` (P2C-OPERATIONS-CONSOLE-READ-SLICE Amendment 1, SPEC R16). Sanitized: no API key, Authorization header, JWT, raw secret, or URL userinfo/query/fragment.

- Generated at: 2026-07-29T07:46:18.225781+00:00
- Provider: Alibaba DashScope (OpenAI-compatible endpoint)
- Model: qwen3.7-max
- Endpoint (host only): https://ws-remplsp27g5oicq1.ap-southeast-1.maas.aliyuncs.com

## 1. Refusal cases (real HTTP route chain, observed provider-call delta)

| Case | Outcome | Detail | Provider calls |
|---|---|---|---|
| anonymous_shifts_read_rejected | PASS | refused: status 401 | 0 |
| malformed_token_shifts_read_rejected | PASS | refused: status 401 | 0 |
| anonymous_events_read_rejected | PASS | refused: status 401 | 0 |
| anonymous_open_work_read_rejected | PASS | refused: status 401 | 0 |

## 2. Genuine admitted reads (real HTTP route chain)

- valid JWT (p2c-ev-viewer) admitted GET /shifts, GET /events and GET /shifts/{shift_id}/open-work via minted token and real HTTP requests

## 3. Real provider call

Reached only because the reads above genuinely admitted a valid JWT.

- Outcome: **PASS**
- Reached the provider (got any HTTP response): **True**
- HTTP status: 200
- Started at: 2026-07-29T07:46:14.165368+00:00
- Response excerpt: `CVF_P2C_READ_EVIDENCE_OK`

## 4. Provider-call count (observed, reset per invocation)

- Total provider calls made by this run: **1**
- Expected: 0 for every refusal case above, exactly 1 after the genuine admitted reads.

## Claim boundary

This receipt evidences that the P2C read surfaces' identity-only JWT gate correctly refuses anonymous and malformed-token reads before any provider call, and correctly admits a genuine valid-JWT read of shift, events and open-work through the real HTTP route chain. It does NOT evidence that any production read endpoint calls a provider in production (none do), does not evidence per-shift assignment or data_scope enforcement, and does not evidence PostgreSQL production readiness.
