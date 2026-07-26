# P2-A incident vertical - live governance evidence receipt

Overall outcome: PASS

Produced by `scripts/run_incident_live_governance_evidence.py` via `scripts/_incident_live_evidence_support.py` (P2A-INCIDENT-VERTICAL, SPEC section 6/R14/R15-A). Sanitized: contains no API key, no Authorization header, no JWT, no raw secret, no URL userinfo/query/fragment.

- Generated at: 2026-07-26T12:23:39.611935+00:00
- Provider: Alibaba DashScope (OpenAI-compatible endpoint)
- Model: qwen3.7-max
- Endpoint (host only): https://dashscope-intl.aliyuncs.com

## 1. Gate-refusal cases (in-process, real code path, observed provider-call delta)

| Case | Outcome | Detail | Provider calls |
|---|---|---|---|
| insufficient_evidence_rejected | PASS | refused: status 409 | 0 |
| fabricated_approval_rejected | PASS | refused: status 409 | 0 |
| self_approval_rejected | PASS | refused: status 409 | 0 |
| inactive_approver_rejected | PASS | refused: status 409 | 0 |
| stale_version_rejected | PASS | refused: status 409 | 0 |

## 2. Genuine acknowledgement construction (real code path)

- distinct authenticated approver (inc-ev-sup2) and confirmer (inc-ev-sup1) satisfied the R2 quorum via minted JWTs and HTTP requests

## 3. Real provider call

Reached only because the acknowledgement above genuinely satisfied the R2 quorum.

- Outcome: **PASS**
- Reached the provider (got any HTTP response): **True**
- HTTP status: 200
- Started at: 2026-07-26T12:23:36.277346+00:00
- Response excerpt: `CVF_INCIDENT_EVIDENCE_OK`

## 4. Provider-call count (observed, reset per invocation)

- Total provider calls made by this run: **1**
- Expected: 0 for every gate-refusal case above, exactly 1 after the genuine acknowledgement.

## Claim boundary

This receipt evidences that the incident vertical's `approval` control correctly refuses insufficient-evidence, fabricated, self-approval, inactive-approver and stale-version acknowledgement attempts before any provider call, and correctly admits a genuine, distinct-approver acknowledgement through the real application code path. It does NOT evidence that any production endpoint calls a provider in production (none do), and it does not evidence PostgreSQL production readiness.
