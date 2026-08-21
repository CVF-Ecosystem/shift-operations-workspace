# P4-A AI Gateway - Live Evidence Receipt

- Tranche: `P4A-AI-GATEWAY-2026-08-20`
- Generated: `2026-08-20T09:19:47.590849+00:00`
- Disposition: `LIVE_EVIDENCE_PASS`
- Physical provider calls this run: `1`

Sanitized machine-readable record. Contains digests, safe identifiers, and gate
outcomes only - no prompt text, context body, output body, endpoint path,
authorization header, or credential.

```json
{
  "accepted": true,
  "adapter_calls": 1,
  "credential_env_var": "ALIBABA_API_KEY",
  "disposition": "LIVE_EVIDENCE_PASS",
  "endpoint_origin": "https://ws-remplsp27g5oicq1.ap-southeast-1.maas.aliyuncs.com",
  "error_note": "",
  "gateway_attempts": 1,
  "generated_at": "2026-08-20T09:19:47.590849+00:00",
  "http_status": 200,
  "model_id": "qwen3.7-max-2026-05-17",
  "physical_calls": 1,
  "provider_id": "alibaba_dashscope_evidence_only",
  "reached_server": true,
  "receipt": {
    "actual_cost_usd_millis": 0,
    "actual_tokens": 339,
    "ai_mode": "EXTERNAL_AI",
    "cancel_attempted": false,
    "classification": "PUBLIC",
    "context_digest": "943eb62b9b6f899c064796fc2379d31c5aa3e31af860847870851054c7add3bf",
    "endpoint_origin": "https://ws-remplsp27g5oicq1.ap-southeast-1.maas.aliyuncs.com",
    "final_outcome": "ACCEPTED",
    "finished_at": "2026-08-20T09:19:58.450497+00:00",
    "gates": [
      {
        "gate": "request_validation",
        "outcome": "PASS",
        "reason_code": ""
      },
      {
        "gate": "ai_mode",
        "outcome": "PASS",
        "reason_code": ""
      },
      {
        "gate": "context_admission",
        "outcome": "PASS",
        "reason_code": ""
      },
      {
        "gate": "data_scope.assert_placement_allowed",
        "outcome": "PASS",
        "reason_code": ""
      },
      {
        "gate": "cost.assert_within_budget",
        "outcome": "PASS",
        "reason_code": ""
      },
      {
        "gate": "termination.assert_not_terminated",
        "outcome": "PASS",
        "reason_code": ""
      },
      {
        "gate": "provider_registry",
        "outcome": "PASS",
        "reason_code": ""
      },
      {
        "gate": "provider_dispatch",
        "outcome": "PASS",
        "reason_code": ""
      },
      {
        "gate": "output_schema",
        "outcome": "PASS",
        "reason_code": ""
      }
    ],
    "model_id": "qwen3.7-max-2026-05-17",
    "output_digest": "45ac22c1522619467bf4ef87ad9fca921279c5d9e2c07460dde6aab7322ae568",
    "output_schema_digest": "ad2d5e0a1b34845ad62895d5ae132d89a5033d0a78001ecb1a2d27355dc934b2",
    "placement": "external",
    "provider_attempts": 1,
    "provider_id": "alibaba_dashscope_evidence_only",
    "reason_code": "",
    "request_digest": "3c2a4b06379b48fca5fec4fc36a82e1d25dfcd7945caf554fff91ffdb4756124",
    "reservation_released": false,
    "reserved_cost_usd_millis": 1,
    "reserved_tokens": 40,
    "started_at": "2026-08-20T09:19:47.598755+00:00",
    "task_type": "p4a_public_canary",
    "timed_out": false,
    "usage_committed": true
  },
  "refusal_cases": [
    {
      "accepted": false,
      "adapter_calls": 0,
      "case": "NO_AI",
      "final_outcome": "REFUSED_PRE_DISPATCH",
      "gateway_attempts": 0,
      "provider_attempts": 0,
      "reason_code": "AI_MODE_DISABLED"
    },
    {
      "accepted": false,
      "adapter_calls": 0,
      "case": "NO_EVIDENCE",
      "final_outcome": "REFUSED_PRE_DISPATCH",
      "gateway_attempts": 0,
      "provider_attempts": 0,
      "reason_code": "NO_EVIDENCE"
    },
    {
      "accepted": false,
      "adapter_calls": 0,
      "case": "P4A1_INTERNAL_WITHOUT_MINIMIZATION",
      "final_outcome": "REFUSED_PRE_DISPATCH",
      "gateway_attempts": 0,
      "provider_attempts": 0,
      "reason_code": "CONTEXT_INADMISSIBLE"
    },
    {
      "accepted": false,
      "adapter_calls": 0,
      "case": "RESTRICTED_EXTERNAL_PLACEMENT",
      "final_outcome": "REFUSED_PRE_DISPATCH",
      "gateway_attempts": 0,
      "provider_attempts": 0,
      "reason_code": "CONTEXT_INADMISSIBLE"
    },
    {
      "accepted": false,
      "adapter_calls": 0,
      "case": "BUDGET_EXCEEDED",
      "final_outcome": "REFUSED_PRE_DISPATCH",
      "gateway_attempts": 0,
      "provider_attempts": 0,
      "reason_code": "BUDGET_UNAVAILABLE"
    },
    {
      "accepted": false,
      "adapter_calls": 0,
      "case": "KILL_SWITCH_ACTIVE",
      "final_outcome": "REFUSED_PRE_DISPATCH",
      "gateway_attempts": 0,
      "provider_attempts": 0,
      "reason_code": "TERMINATED"
    }
  ],
  "tranche": "P4A-AI-GATEWAY-2026-08-20"
}
```

## Claim boundary

This receipt proves that on the recorded run the three CVF gates preceded a
single provider dispatch through `AIGateway.execute`, and that each mandated
refusal case reached the provider zero times. It does not prove an application
API uses the gateway, durable usage accounting, a production provider adapter,
RAG, deployment, or production readiness.
