# P4-A2 Governed RAG - Live Evidence Receipt

- Tranche: `P4A2-GOVERNED-RAG-2026-08-21`
- Generated: `2026-08-21T13:40:25.103295+00:00`
- Disposition: `LIVE_EVIDENCE_PASS`
- Physical provider calls this run: `1`

Sanitized machine-readable record. Contains digests, safe identifiers, counts,
and outcome/reason codes only - no query text, evidence body, output body,
endpoint path, authorization header, or credential.

```json
{
  "accepted": true,
  "adapter_calls": 1,
  "credential_env_var": "ALIBABA_API_KEY",
  "disposition": "LIVE_EVIDENCE_PASS",
  "endpoint_origin": "https://ws-remplsp27g5oicq1.ap-southeast-1.maas.aliyuncs.com",
  "error_note": "",
  "gateway_attempts": 1,
  "generated_at": "2026-08-21T13:40:25.103295+00:00",
  "http_status": 200,
  "model_id": "qwen3.7-max-2026-05-17",
  "physical_calls": 1,
  "provider_id": "alibaba_dashscope_evidence_only",
  "reached_server": true,
  "receipt": {
    "authorization_scope_digest_sha256": "13cec095baa6b98a02558eb37c137ccb7598004eb7fc196f64b3027a035bb572",
    "context_digest_sha256": "fd8245fdf17dc886aadd488a3dfeafa101257795b26345c9efcb4e03f5b091ad",
    "contract_version": "1.0",
    "corpus_id": "PROJECT_KNOWLEDGE_LOCAL_V1",
    "encoder_id": "PROJECT_CONCEPT_FEATURE_VECTOR_V1",
    "encoder_version": "1.0",
    "final_outcome": "ABSTAINED",
    "gateway_receipt_output_digest_sha256": "ec10fac7a9d4b777bd810cc7986ebd71d16fe8893252882712f63851921f2e31",
    "gateway_request_digest_sha256": "649fe25be3604901a56b65fcbfeb3d1284f82bba4353231c214f6b993db0df31",
    "index_build_digest_sha256": "6e9a5338dd2321733eaf69e715592e7d368ab4d172700421f83674fb03f6afc4",
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
    "provider_response_digest_sha256": "ec10fac7a9d4b777bd810cc7986ebd71d16fe8893252882712f63851921f2e31",
    "reason_code": "",
    "receipt_hash_sha256": "fccb699fcca29ce8af7eb6a0446d6667e316054f945def19bf9dad049f0d6607",
    "retrieval_evidence_set_hash_sha256": "4870499c9a6fa35ad69bedf822c7fbefcc1b0adcf6d1faa643a1ae91007b8f0d",
    "retrieval_receipt_hash_sha256": "5a76bfa192e789265068bcf89f164a2a27a2031ffb76629d67b4a9a1c08d6762",
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
    "validated_answer_digest_sha256": "46d8d3b51714d5419005f71934beed489981d57ab465cbf07ed11739d40ab306"
  },
  "refusal_cases": [
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
  "tranche": "P4A2-GOVERNED-RAG-2026-08-21"
}
```

## Claim boundary

This receipt proves that on the recorded run at least six representative
pre-gateway refusal cases (P4-A1 no-evidence, forged/mismatched positive
binding, stale index, all-evidence injection omission, minimization failure,
context-budget-exceeded) reached the provider zero times, and that the full
admitted application composition (`execute_governed_rag`, `placement=
Placement.EXTERNAL` bound per P4A2-REV-F3) made exactly one HTTPS POST
through the real `AIGateway.execute` against an isolated
synthetic `PROJECT_KNOWLEDGE_LOCAL_V1` fixture containing no operational or
customer data. It does not prove a public endpoint, general semantic
embeddings, operational-corpus RAG, durability, production provider
integration, deployment, or production readiness.
