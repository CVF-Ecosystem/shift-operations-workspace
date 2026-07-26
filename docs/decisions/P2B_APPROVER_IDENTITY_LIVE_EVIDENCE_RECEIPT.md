# P2-B approver-identity control - live governance evidence receipt

Overall outcome: PASS

Produced by `scripts/run_approval_governance_evidence.py`
(P2B-APPROVER-IDENTITY-RECONCILIATION, SPEC section 7). Sanitized: contains no API key, no Authorization header, no JWT, no password, no raw secret.

- Generated at: 2026-07-26T04:19:18.089444+00:00
- Provider: Alibaba DashScope (OpenAI-compatible endpoint)
- Model: qwen3.7-max
- Endpoint: https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions

## 1. Gate-refusal cases (in-process, real code path, 0 provider calls each)

| Case | Outcome | Detail | Provider calls |
|---|---|---|---|
| fabricated_approval_rejected | PASS | refused: status 409 | 0 |
| wrong_role_rejected | PASS | refused: status 403 | 0 |
| inactive_user_rejected | PASS | refused: status 403 | 0 |
| self_approval_rejected | PASS | refused: status 409 | 0 |
| insufficient_quorum_rejected | PASS | refused: status 409 | 0 |
| replay_stale_version_rejected | PASS | refused: status 409 | 0 |

## 2. Authenticated-quorum construction (real code path)

- distinct authenticated approvers (evidence-sup5, evidence-mgr2) satisfied the R3 quorum via minted JWTs and HTTP requests

## 3. Real provider call

Reached only because the quorum above genuinely satisfied the R3 requirement.

- Outcome: **PASS**
- Reached the provider (got any HTTP response): **True**
- HTTP status: 200
- Started at: 2026-07-26T04:19:14.054111+00:00
- Response excerpt: `CVF_APPROVAL_EVIDENCE_OK`

## 4. Provider-call count (self-asserted)

- Total provider calls made by this run: **1**
- Expected: 0 for every gate-refusal case above, exactly 1 after the valid quorum.

## Claim boundary

This receipt evidences that the `approval` control - authenticated,
server-derived, scope-bound receipts evaluated by a deterministic,
order-invariant quorum matcher - correctly refuses fabricated, wrong-role,
inactive-user, self-approval, insufficient-quorum, and replayed approvals
before any provider call, and correctly admits a genuine, distinct-approver
quorum through the real application code path. It does NOT evidence that any
production endpoint calls a provider in production (none do). It does not
evidence PostgreSQL production verification (remains NOT LIVE VERIFIED).
