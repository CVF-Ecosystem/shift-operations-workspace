# P4-B AI Providers - Live Evidence Receipt

- Tranche: `P4B-AI-PROVIDERS-2026-08-21`
- Generated: `2026-08-22T08:53:28.873858+00:00`
- Disposition: `LIVE_EVIDENCE_PASS`

Sanitized machine-readable record. Contains digests, safe identifiers,
counts, and outcome/reason codes only - no facts, context, rule output,
prompt, provider output, credential, or raw exception.

```json
{
  "adapter_calls": 1,
  "credential_env_var": "ALIBABA_API_KEY",
  "disposition": "LIVE_EVIDENCE_PASS",
  "endpoint_origin": "https://ws-remplsp27g5oicq1.ap-southeast-1.maas.aliyuncs.com",
  "gateway_calls": 1,
  "gateway_physical_attempts": 1,
  "generated_at": "2026-08-22T08:53:28.873858+00:00",
  "http_status": 200,
  "mock_evidence_ineligible_confirmed": true,
  "model_id": "qwen3.7-max-2026-05-17",
  "outcome": "EXTERNAL_ACCEPTED",
  "provider_attempts": 1,
  "provider_id": "p4b_evidence_only_test_provider",
  "reached_server": true,
  "reason_code": "",
  "refusal_cases": [
    {
      "adapter_calls": 0,
      "case": "NO_AI",
      "gateway_calls": 0,
      "gateway_physical_attempts": 0,
      "outcome": "AI_MODE_DISABLED",
      "provider_attempts": 0,
      "reason_code": ""
    },
    {
      "adapter_calls": 0,
      "case": "RULES_NO_MATCH",
      "gateway_calls": 0,
      "gateway_physical_attempts": 0,
      "outcome": "RULES_NO_MATCH",
      "provider_attempts": 0,
      "reason_code": "RULES_NO_MATCH"
    },
    {
      "adapter_calls": 0,
      "case": "EXTERNAL_TASK_TYPE_MISMATCH",
      "gateway_calls": 0,
      "gateway_physical_attempts": 0,
      "outcome": "EXTERNAL_IDENTITY_MISMATCH",
      "provider_attempts": 0,
      "reason_code": "TASK_TYPE_MISMATCH"
    },
    {
      "adapter_calls": 0,
      "case": "EXTERNAL_NO_GATEWAY",
      "gateway_calls": 0,
      "gateway_physical_attempts": 0,
      "outcome": "EXTERNAL_IDENTITY_MISMATCH",
      "provider_attempts": 0,
      "reason_code": "NO_GATEWAY_INJECTED"
    }
  ],
  "tranche": "P4B-AI-PROVIDERS-2026-08-21"
}
```

## Claim boundary

Proves the mandated zero-call refusal cases reached the provider zero
times, MockProviderAdapter output is structurally evidence-ineligible, and
(when past refusals-only) exactly one admitted EXTERNAL_AI dispatch was
attempted. Not proof of a production adapter, automatic routing, durable
usage/audit, a public API/UI, deployment, or production readiness.
