# Phase 2 full-shift exit — live governance evidence receipt

Overall outcome: PASS

## Admission disposition after independent review

`INVALIDATED_BY_REVIEW_FAIL` — the HTTP response and all metadata below are
retained as immutable history, but this first call is not accepted as the
tranche's final governance proof. The original pre-call evidence did not prove
whole-ledger refusal immutability, producer-bound browser provenance, complete
PostgreSQL snapshot/receipt/action-actor bindings or exact committed-task GET
before rendering. Amendment 1 authorizes exactly one replacement only after an
independent repaired-candidate pre-call `REVIEW_PASS`.

- Tranche physical calls so far: **1**
- Invalidated calls: **1**
- Accepted final calls: **0**
- Replacement calls remaining: **1**
- Third call: **FORBIDDEN**

Sanitized receipt: no API key, bearer/JWT, DSN, raw provider body, URL credentials/query/fragment or raw exception.

- Generated at: 2026-08-02T12:35:27.559309+00:00
- Provider: Alibaba DashScope (OpenAI-compatible endpoint)
- Model: qwen3.7-max
- Endpoint class: https://ws-remplsp27g5oicq1.ap-southeast-1.maas.aliyuncs.com
- Browser checkpoint: P2_FULL_SHIFT_EXIT

## Zero-call refusal gates

| Case | Outcome | HTTP status | Provider calls |
|---|---|---:|---:|
| anonymous_shift_create | PASS | 401 | 0 |
| anonymous_shift_close | PASS | 401 | 0 |
| unassigned_read | PASS | 404 | 0 |
| unassigned_mutation | PASS | 404 | 0 |
| stale_task_cas | PASS | 409 | 0 |
| stale_close_cas | PASS | 409 | 0 |
| handover_ack_without_destination_assignment | PASS | 404 | 0 |
| freeze_before_close | PASS | 409 | 0 |
| freeze_without_acknowledged_current_handover | PASS | 409 | 0 |
| report_approval_without_receipt | PASS | 409 | 0 |
| stale_freeze_cas | PASS | 409 | 0 |
| freeze_without_current_approved_report | PASS | 409 | 0 |

## Admitted evidence

- Durable scenario: one 12-hour route-level lineage persisted FROZEN with current Report, acknowledged non-empty handover, IN_PROGRESS task and actor-bound audits
- Browser: Playwright PASS; bounded queue PASS; transport ambiguity PASS (one request, zero retry/queue, authoritative reconciliation).

## Real provider call

- Outcome: **PASS**
- Reached provider: **True**
- HTTP status: 200
- Expected token matched: **True**
- Total calls: **1** (zero before admission; exactly one after)

## Claim boundary

This is bounded Phase 2 functional exit evidence on real browser/FastAPI, local durable stores and one provider receipt. It is not a wall-clock soak, push/exactly-once, fully-offline, production-readiness, Phase 3 or external-channel claim.


## Replacement provider attempt reservation

- State: **RESERVED_BEFORE_NETWORK**
- Attempt id: `ecf2b066-438a-415d-9f6b-718cd8cc47ae`
- Budget effect: sole replacement slot consumed; every rerun is fail-closed.

## Replacement provider attempt result

- Attempt id: `ecf2b066-438a-415d-9f6b-718cd8cc47ae`
- Disposition: **ACCEPTED**
- Replacement outcome: PASS

Sanitized replacement receipt: no API key, bearer/JWT, DSN, raw provider body, URL credentials/query/fragment or raw exception.

- Generated at: 2026-08-02T14:51:19.617626+00:00
- Provider: Alibaba DashScope (OpenAI-compatible endpoint)
- Model: qwen3.7-max
- Endpoint class: https://ws-remplsp27g5oicq1.ap-southeast-1.maas.aliyuncs.com
- Browser checkpoint: P2_FULL_SHIFT_EXIT

### Replacement-run zero-call refusal gates

| Case | Outcome | HTTP status | Replacement-run calls |
|---|---|---:|---:|
| anonymous_shift_create | PASS | 401 | 0 |
| anonymous_shift_close | PASS | 401 | 0 |
| unassigned_read | PASS | 404 | 0 |
| unassigned_mutation | PASS | 404 | 0 |
| stale_task_cas | PASS | 409 | 0 |
| stale_close_cas | PASS | 409 | 0 |
| handover_ack_without_destination_assignment | PASS | 404 | 0 |
| report_approval_without_receipt | PASS | 409 | 0 |
| freeze_before_close | PASS | 409 | 0 |
| freeze_without_acknowledged_current_handover | PASS | 409 | 0 |
| stale_freeze_cas | PASS | 409 | 0 |
| freeze_without_current_approved_report | PASS | 409 | 0 |

### Replacement admitted evidence

- Durable scenario: one 12-hour route-level lineage persisted FROZEN with current Report, acknowledged non-empty handover, IN_PROGRESS task and actor-bound audits
- Browser: Playwright PASS; bounded queue PASS; transport ambiguity PASS (one request, zero retry/queue, authoritative reconciliation).

### Replacement provider result

- Outcome: **PASS**
- Reached provider: **True**
- HTTP status: 200
- Expected token matched: **True**
- Replacement-run calls: **1** (zero before admission; exactly one after)
- Tranche physical calls: **2** (first invalidated plus this attempt)
- Accepted final calls: **1**

### Final claim boundary

This is bounded Phase 2 functional exit evidence on real browser/FastAPI, local durable stores and one provider receipt. It is not a wall-clock soak, push/exactly-once, fully-offline, production-readiness, Phase 3 or external-channel claim.
