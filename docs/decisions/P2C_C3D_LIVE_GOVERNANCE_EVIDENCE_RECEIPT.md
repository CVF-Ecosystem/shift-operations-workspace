# P2-C C3d supervisor closeout - live governance evidence receipt

Overall outcome: PASS

Produced by `scripts/run_p2c_c3d_live_governance_evidence.py` via `scripts/_p2c_c3d_live_evidence_support.py` (P2C-MUTATION-FULL-UI-C3D, SPEC R10). Sanitized: contains no API key, no Authorization header, no JWT, no raw secret, no URL userinfo/query/fragment.

- Generated at: 2026-08-02T05:30:32.102481+00:00
- Provider: Alibaba DashScope (OpenAI-compatible endpoint)
- Model: qwen3.7-max
- Endpoint (host only): https://ws-remplsp27g5oicq1.ap-southeast-1.maas.aliyuncs.com

## 1. Supervisor closeout refusal matrix (real HTTP route chain, observed provider-call delta)

| Case | Outcome | Detail | Provider calls |
|---|---|---|---|
| wrong_role_operator_cannot_acknowledge_incident | PASS | refused: status 403 | 0 |
| unassigned_operator_cannot_use_staffing | PASS | refused: status 403 | 0 |
| stale_version_event_confirm_rejected | PASS | refused: status 409 | 0 |
| missing_approval_confirm_rejected | PASS | refused: status 409 | 0 |
| wrong_destination_assignment_acknowledge_rejected | PASS | refused: status 404 | 0 |
| non_closed_shift_freeze_rejected | PASS | refused: status 409 | 0 |
| retired_override_field_refused | PASS | refused: status 422 | 0 |

## 2. Durable assigned closeout state and actor-bound audits (real HTTP route chain)

- genuine staffing-assigned closeout: c3d-ev-sup1 self-assigned, confirmed an event with a durable approval receipt, acknowledged an incident, reviewed and (via c3d-ev-sup2) acknowledged a cross-shift handover, approved a distinct-receipt END_SHIFT report, then closed and froze the shift - verified via a fresh stored-shift read (status FROZEN) and every required actor-bound audit action present

## 3. Real provider call

Reached only because the closeout above genuinely produced a durable assigned Shift freeze plus every required actor-bound audit record.

- Outcome: **PASS**
- Reached the provider (got any HTTP response): **True**
- HTTP status: 200
- Expected token matched: **True**
- Started at: 2026-08-02T05:30:26.950179+00:00

## 4. Provider-call count (observed, reset per invocation)

- Total provider calls made by this run: **1**
- Expected: 0 for every refusal case above, exactly 1 after the genuine closeout.

## Claim boundary

This receipt evidences only that, within the single workspace, an authenticated actively assigned shift_supervisor uses the C3d staffing/event/approval/incident/handover/report/freeze controls while the backend re-authorizes and audits every action on the proven backends. It does NOT evidence multi-tenant/provider data_scope, destination-only handover discovery, offline/realtime, production PostgreSQL, P2-D, full-shift-exit, or Phase-2 completion.
