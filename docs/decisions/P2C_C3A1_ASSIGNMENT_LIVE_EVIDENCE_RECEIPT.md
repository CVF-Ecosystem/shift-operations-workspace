# P2C-C3A1 assignment/staffing foundation - live governance evidence receipt

Overall outcome: PASS

Produced by `scripts/run_assignment_live_governance_evidence.py` (P2C-MUTATION-FULL-UI-C3A1, SPEC R10). Sanitized: no API key, Authorization header, JWT, raw secret, or URL userinfo/query/fragment.

- Generated at: 2026-07-31T15:37:03.925277+00:00
- Provider: Alibaba DashScope (OpenAI-compatible endpoint)
- Model: qwen3.7-max
- Endpoint (host only): https://ws-remplsp27g5oicq1.ap-southeast-1.maas.aliyuncs.com

## 1. Refusal cases

| Case | Outcome | Detail | Provider calls |
|---|---|---|---|
| anonymous_staffing_list_rejected | PASS | refused: status 401 | 0 |
| operator_cannot_manage_staffing | PASS | refused: status 403 | 0 |
| capabilities_denied_without_active_assignment | PASS | refused: status 403 | 0 |

## 2. Genuine durable staffing assignment

- valid supervisor JWT (assign-ev-sup) admitted staffing assignment via a minted token and a real HTTP request, persisting exactly one durable ACTIVE assignment and one exactly-field-matched audit

## 3. Real provider call

- Outcome: **PASS**
- Reached the provider: **True**
- HTTP status: 200
- Started at: 2026-07-31T15:37:00.869955+00:00
- Response excerpt: `CVF_ASSIGNMENT_EVIDENCE_OK`

## 4. Provider-call count

- Total provider calls made by this run: **1**
- Expected: 0 for every refusal case above, exactly 1 after the genuine admitted assignment.

## Claim boundary

Evidences that the staffing control plane's real identity/permission/assignment gate correctly refuses anonymous, insufficient-role and unassigned-capability attempts before any provider call, and correctly admits a genuine valid-supervisor-JWT staffing assignment through the real HTTP route chain, persisting exactly one durable ACTIVE assignment and one actor-bound audit record. Does NOT evidence that C3a1 enforces assignment across existing operational routes (C3a2), production PostgreSQL readiness, or frontend mutation.
