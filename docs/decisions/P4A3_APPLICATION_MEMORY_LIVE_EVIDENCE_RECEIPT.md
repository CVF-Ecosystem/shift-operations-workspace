# P4-A3 Application Memory - Live Evidence Receipt

- Tranche: `P4A3-APPLICATION-MEMORY-2026-08-21`
- Generated: `2026-08-21T16:08:31.579298+00:00`
- Disposition: `LIVE_EVIDENCE_PASS`
- Physical provider calls this run: `1`

Sanitized machine-readable record. It contains safe ids, digests, counts,
outcomes and reason codes only; no memory text, query, evidence body, provider
output body, endpoint path, authorization header or credential.

```json
{
  "adapter_calls": 1,
  "credential_env_var": "ALIBABA_API_KEY",
  "disposition": "LIVE_EVIDENCE_PASS",
  "endpoint_origin": "https://ws-remplsp27g5oicq1.ap-southeast-1.maas.aliyuncs.com",
  "error_note": "",
  "gateway_attempts": 1,
  "generated_at": "2026-08-21T16:08:31.579298+00:00",
  "http_status": 200,
  "memory_admission_outcome": "ADMITTED",
  "memory_authorization_scope_digest_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "memory_entry_digest_sha256": "f20fdd68ae002057c433c861e71469d21ab822378b16fa38a494b409a88b4cd2",
  "memory_entry_id": "aed8e3f9-3124-4de8-ae19-a1c7a77bde26",
  "memory_provenance_digest_sha256": "40a54c93939fde946a8b582f661d2852df0bf84ea1692c2e2ca06527fb08a41e",
  "memory_read_outcome": "READ_COMPLETE",
  "memory_refusal_cases": [
    {
      "appended_entries": 0,
      "appended_tombstones": 0,
      "case": "REQUEST_INVALID_TTL",
      "final_outcome": "REQUEST_INVALID",
      "mutations": 0,
      "provider_attempts": 0,
      "reason_code": "REQUEST_INVALID"
    },
    {
      "appended_entries": 0,
      "appended_tombstones": 0,
      "case": "SOURCE_REVALIDATION_FAILED",
      "final_outcome": "SOURCE_REVALIDATION_FAILED",
      "mutations": 0,
      "provider_attempts": 0,
      "reason_code": "SOURCE_REVALIDATION_FAILED"
    },
    {
      "appended_entries": 0,
      "appended_tombstones": 0,
      "case": "AUTHORIZATION_SCOPE_MISMATCH",
      "final_outcome": "AUTHORIZATION_SCOPE_MISMATCH",
      "mutations": 0,
      "provider_attempts": 0,
      "reason_code": "AUTHORIZATION_SCOPE_MISMATCH"
    },
    {
      "appended_entries": 0,
      "appended_tombstones": 0,
      "case": "ENTRY_NOT_FOUND",
      "final_outcome": "ENTRY_NOT_FOUND",
      "mutations": 0,
      "provider_attempts": 0,
      "reason_code": "ENTRY_NOT_FOUND"
    },
    {
      "appended_entries": 0,
      "appended_tombstones": 0,
      "case": "ENTRY_NOT_ACTIVE",
      "final_outcome": "ENTRY_NOT_ACTIVE",
      "mutations": 0,
      "provider_attempts": 0,
      "reason_code": "ENTRY_NOT_ACTIVE"
    },
    {
      "appended_entries": 0,
      "appended_tombstones": 0,
      "case": "ENTRY_EXPIRED",
      "final_outcome": "ENTRY_EXPIRED",
      "mutations": 0,
      "provider_attempts": 0,
      "reason_code": "ENTRY_EXPIRED"
    },
    {
      "appended_entries": 0,
      "appended_tombstones": 0,
      "case": "BUDGET_BREACH",
      "final_outcome": "BUDGET_BREACH",
      "mutations": 0,
      "provider_attempts": 0,
      "reason_code": "BUDGET_BREACH"
    }
  ],
  "memory_source_content_digest_sha256": "fd1c0e4f27d7a61b4cee410a8f859d7bcca1096a632b15607c2c3a94a785ee8a",
  "model_id": "qwen3.7-max-2026-05-17",
  "physical_calls": 1,
  "provider_id": "alibaba_dashscope_evidence_only",
  "rag_receipt": {
    "authorization_scope_digest_sha256": "1524cd3de786b5d5984abc3874adcfe49f5b7874bbc13c629674d39357937269",
    "context_digest_sha256": "fd8245fdf17dc886aadd488a3dfeafa101257795b26345c9efcb4e03f5b091ad",
    "contract_version": "1.0",
    "corpus_id": "PROJECT_KNOWLEDGE_LOCAL_V1",
    "encoder_id": "PROJECT_CONCEPT_FEATURE_VECTOR_V1",
    "encoder_version": "1.0",
    "final_outcome": "ABSTAINED",
    "gateway_receipt_output_digest_sha256": "ce2dfcc4b89f608fb8437fc31bd17bc276e60dafedac80018ffd11edc36fa23f",
    "gateway_request_digest_sha256": "649fe25be3604901a56b65fcbfeb3d1284f82bba4353231c214f6b993db0df31",
    "index_build_digest_sha256": "083923483d4fcc9856df0412a1db5585e05af180d6ebefb0c9e383aa181bb5b4",
    "injection_omissions": [],
    "lexicon_digest_sha256": "14f0e2486e78a35bfa8a6333fc0469d732c6967a8c19e3ed7da1e94e78e7670b",
    "minimization_input_digest_sha256": "c13b372b2c5f1f3e63c872609880afcbdb8bc113c23bbac2e5205beeefaf4781",
    "minimization_omitted_count": 0,
    "minimization_output_digest_sha256": "cd7f25f854f3b038aa7ea7821e63164a60c4fd8ce388872b65205388cc4285b2",
    "minimization_retained_count": 1,
    "minimization_ruleset_digest_sha256": "9abc6628f8813779b9ad5dbb7427005c034e15207a0704f47dc9c4e6127bd28f",
    "normalized_query_digest_sha256": "f342fc8c28ad26e7d1179340ba951457557009bf81c7b73df89e8e8009dfcf83",
    "output_schema_digest_sha256": "74083a5a7f2eae4d4055c57f35b0b82acdb82eb958ca5005a671fdbf37ead4a9",
    "physical_attempt_count": 1,
    "post_injection_citation_ids": [
      "e358b56b7e3308fcbf5a9a2c9310430591ca3ea59e6da38998fadf39e07d57f1"
    ],
    "pre_injection_citation_ids": [
      "e358b56b7e3308fcbf5a9a2c9310430591ca3ea59e6da38998fadf39e07d57f1"
    ],
    "provider_response_digest_sha256": "ce2dfcc4b89f608fb8437fc31bd17bc276e60dafedac80018ffd11edc36fa23f",
    "reason_code": "",
    "receipt_hash_sha256": "979d70b5bf8b463a659b047c8376f7aee6ddd5ee58445b5466935291fc00b105",
    "retrieval_evidence_set_hash_sha256": "4870499c9a6fa35ad69bedf822c7fbefcc1b0adcf6d1faa643a1ae91007b8f0d",
    "retrieval_receipt_hash_sha256": "246a54529f3b036a5f424f545097513091c606b646e3276be7cfa7f08b6ec7b9",
    "score_policy_digest_sha256": "c93f5ba3e8fed621315055e9c78cebc411902c1b3fb623cf4a00c2af228b30c8",
    "stages": [
      {
        "outcome": "PASS",
        "reason_code": "",
        "stage": "REQUEST_VALIDATED"
      },
      {
        "outcome": "PASS",
        "reason_code": "",
        "stage": "RETRIEVAL_BOUND"
      },
      {
        "outcome": "PASS",
        "reason_code": "",
        "stage": "INDEX_VALIDATED"
      },
      {
        "outcome": "PASS",
        "reason_code": "",
        "stage": "RANKED"
      },
      {
        "outcome": "PASS",
        "reason_code": "",
        "stage": "INJECTION_SCREENED"
      },
      {
        "outcome": "PASS",
        "reason_code": "",
        "stage": "MINIMIZED"
      },
      {
        "outcome": "PASS",
        "reason_code": "",
        "stage": "CONTEXT_ASSEMBLED"
      },
      {
        "outcome": "PASS",
        "reason_code": "",
        "stage": "GATEWAY_DISPATCHED"
      },
      {
        "outcome": "PASS",
        "reason_code": "",
        "stage": "ANSWER_VALIDATED"
      }
    ],
    "validated_answer_digest_sha256": "6f2009d3a699ed1127e229c17ea319e9d14458e1e77556d7ba3e8d02a8b3538a"
  },
  "rag_refusal_cases": [
    {
      "accepted": false,
      "adapter_calls": 0,
      "case": "P4A1_NO_EVIDENCE",
      "final_outcome": "RETRIEVAL_NOT_POSITIVE",
      "gateway_attempts": 0,
      "provider_attempts": 0,
      "reason_code": "RETRIEVAL_NOT_POSITIVE"
    },
    {
      "accepted": false,
      "adapter_calls": 0,
      "case": "FORGED_POSITIVE_MISMATCHED_BINDING",
      "final_outcome": "BINDING_MISMATCH",
      "gateway_attempts": 0,
      "provider_attempts": 0,
      "reason_code": "BINDING_MISMATCH"
    },
    {
      "accepted": false,
      "adapter_calls": 0,
      "case": "STALE_INDEX",
      "final_outcome": "STALE_INDEX",
      "gateway_attempts": 0,
      "provider_attempts": 0,
      "reason_code": "STALE_INDEX"
    },
    {
      "accepted": false,
      "adapter_calls": 0,
      "case": "ALL_EVIDENCE_INJECTION_OMITTED",
      "final_outcome": "INJECTION_BLOCKED",
      "gateway_attempts": 0,
      "provider_attempts": 0,
      "reason_code": "INJECTION_BLOCKED"
    },
    {
      "accepted": false,
      "adapter_calls": 0,
      "case": "MINIMIZATION_FAILED_EXTERNAL_PLACEMENT",
      "final_outcome": "MINIMIZATION_FAILED",
      "gateway_attempts": 0,
      "provider_attempts": 0,
      "reason_code": "MINIMIZATION_FAILED"
    },
    {
      "accepted": false,
      "adapter_calls": 0,
      "case": "CONTEXT_BUDGET_EXCEEDED",
      "final_outcome": "CONTEXT_BUDGET_EXCEEDED",
      "gateway_attempts": 0,
      "provider_attempts": 0,
      "reason_code": "CONTEXT_BUDGET_EXCEEDED"
    }
  ],
  "reached_server": true,
  "tranche": "P4A3-APPLICATION-MEMORY-2026-08-21"
}
```

## Claim boundary

This receipt proves the recorded synthetic run: every P4-A3 memory refusal
changed zero state and reached the provider zero times; one admitted memory
entry was independently re-read and its text was used explicitly as the P4-A2
query; the inherited P4-A2 refusal chain stayed zero-call; and the admitted
path made at most one HTTPS POST through the real P4-A2/AIGateway composition.
It does not prove implicit recall, operational data, durable memory, a public
route, production provider integration, deployment or production readiness.
