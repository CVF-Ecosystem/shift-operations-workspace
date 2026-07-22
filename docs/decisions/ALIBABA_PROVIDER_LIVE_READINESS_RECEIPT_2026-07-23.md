# Alibaba provider live-readiness receipt

- Tranche: `PROVIDER-ALIBABA-LIVE-CONFIG`
- Generated at: `2026-07-23T00:46:20+07:00`
- Provider: Alibaba DashScope, OpenAI-compatible international endpoint
- Model selected by catalog for 2026-07-23: `qwen3.7-max`
- Credential source: Windows Current User `ALIBABA_API_KEY`
- Raw credential recorded: **NO**

## Secret-safe readiness check

The pinned CVF core provider checker made a real live request with the selected
model and returned:

- status: `LIVE_VALIDATED`
- key present: `true`
- key source: `ALIBABA_API_KEY`
- HTTP outcome: `200`
- loaded environment files: none

## Recorded request and response

Sanitized request:

```json
{
  "model": "qwen3.7-max",
  "messages": [
    {
      "role": "system",
      "content": "Return exactly the JSON object {\"status\":\"OK\"}. No explanation."
    },
    {
      "role": "user",
      "content": "Alibaba provider configuration live receipt."
    }
  ],
  "temperature": 0,
  "max_tokens": 128,
  "stream": false
}
```

Sanitized response:

```json
{
  "http_status": 200,
  "model": "qwen3.7-max",
  "content": "{\"status\":\"OK\"}",
  "finish_reason": "stop",
  "usage": {
    "prompt_tokens": 36,
    "completion_tokens": 358,
    "total_tokens": 394,
    "reasoning_tokens": 348,
    "cached_prompt_tokens": 0
  }
}
```

## Claim boundary

This receipt proves only that the configured Alibaba credential, selected
catalog model, and live OpenAI-compatible request worked at the recorded time.
It does not by itself prove the P2-B identity governance chain, approval
quorum, AI-gateway integration, provider-wide readiness, or future quota
availability. P2-B requires its separate identity-bound live evidence script
after this provider tranche is committed.
