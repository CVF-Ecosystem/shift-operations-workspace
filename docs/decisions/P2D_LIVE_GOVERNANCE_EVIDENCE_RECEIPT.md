# P2-D offline/realtime - live governance evidence receipt

Overall outcome: PASS

Sanitized receipt: no key, bearer/JWT, raw provider body, URL userinfo/query/fragment or raw exception.

- Generated at: 2026-08-02T10:17:49.446572+00:00
- Provider: Alibaba DashScope (OpenAI-compatible endpoint)
- Model: qwen3.7-max
- Endpoint (host only): https://ws-remplsp27g5oicq1.ap-southeast-1.maas.aliyuncs.com

## Refusal and ambiguity gates

| Case | Outcome | Detail | Provider calls |
|---|---|---|---|
| anonymous_transition_refused | PASS | status 401 | 0 |
| unassigned_transition_refused | PASS | status 404 | 0 |
| stale_version_transition_refused | PASS | status 409 | 0 |
| ambiguous_transport_not_admitted_or_retried | PASS | browser-owned transport gate; no provider admission | 0 |

## Durable admitted transition

- assigned task CAS transition persisted IN_PROGRESS with exactly one actor-bound task.transition audit

## Real provider call

- Outcome: **PASS**
- Reached provider: **True**
- HTTP status: 200
- Expected token matched: **True**
- Total calls: **1** (zero before admission; exactly one after)

## Claim boundary

This proves one assigned CAS task transition and actor-bound audit remain governed before one real provider call. Browser evidence separately proves bounded offline staging/polling. It does not prove exactly-once, push, full offline, production readiness, full-shift exit or Phase 2 completion.
