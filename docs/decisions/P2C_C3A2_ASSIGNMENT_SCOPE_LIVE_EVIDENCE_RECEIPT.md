# P2C-C3A2 assignment-scope route enforcement - live governance evidence receipt

Overall outcome: PASS

Produced by `scripts/run_assignment_scope_live_governance_evidence.py` (P2C-MUTATION-FULL-UI-C3A2, WO section 3.6). Sanitized: no API key, Authorization header, JWT, raw secret, or URL userinfo/query/fragment.

- Generated at: 2026-07-31T19:16:11.012190+00:00
- Provider: Alibaba DashScope (OpenAI-compatible endpoint)
- Model: qwen3.7-max
- Endpoint (host only): https://ws-remplsp27g5oicq1.ap-southeast-1.maas.aliyuncs.com

## 1. Refusal cases

| Case | Outcome | Detail | Provider calls |
|---|---|---|---|
| open_work_denied_without_active_assignment | PASS | refused: status 404 | 0 |
| message_create_denied_without_active_assignment | PASS | refused: status 404 | 0 |
| incident_acknowledge_denied_insufficient_role_before_assignment | PASS | refused: status 403 | 0 |

## 2. Genuine ACTIVE-assignment-admitted operation

- valid operator JWT (scope-ev-op) with a durable ACTIVE assignment admitted POST /messages via a real HTTP request through the canonical assignment_scope guard, persisting exactly one exactly-field-matched message.create audit

## 3. Real provider call

- Outcome: **PASS**
- Reached the provider: **True**
- HTTP status: 200
- Started at: 2026-07-31T19:16:08.056614+00:00
- Response excerpt: `CVF_ASSIGNMENT_SCOPE_EVIDENCE_OK`

## 4. Provider-call count

- Total provider calls made by this run: **1**
- Expected: 0 for every refusal case above, exactly 1 after the genuine admitted operation.

## Claim boundary

Evidences that C3a2's route-wide assignment_scope guard correctly refuses unassigned/insufficient-role attempts on a representative sample of R6 routes before any provider call, and admits a genuine valid-operator-JWT ACTIVE-assignment-scoped POST /messages mutation with an exact-field-matched audit through the real HTTP route chain. Does NOT evidence exhaustive R6/R7 coverage (see tests/cvf/test_assignment_scope_*.py), production PostgreSQL, or frontend mutation.
