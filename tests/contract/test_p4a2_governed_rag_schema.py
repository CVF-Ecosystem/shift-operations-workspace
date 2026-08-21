"""P4-A2 contract test - receipts conform to the published JSON schema.

NOT GOVERNANCE PROOF: schema conformance only. The live receipt produced by
the R19 run is validated against this same schema by the evidence runner.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from governed_rag.receipts import RagFinalOutcome, RagStage, build_receipt, build_stages

SCHEMA_PATH = (
    Path(__file__).resolve().parents[2]
    / "packages"
    / "governed-rag"
    / "contracts"
    / "governed_rag.schema.json"
)
DIGEST = "d" * 64

jsonschema = pytest.importorskip("jsonschema", reason="jsonschema is a dev dependency")


@pytest.fixture(scope="module")
def schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _negative_receipt(**overrides):
    fields = dict(
        normalized_query_digest_sha256=DIGEST,
        retrieval_receipt_hash_sha256=DIGEST,
        retrieval_evidence_set_hash_sha256=DIGEST,
        authorization_scope_digest_sha256=DIGEST,
        corpus_id="PROJECT_KNOWLEDGE_LOCAL_V1",
        index_build_digest_sha256=None,
        encoder_version="1.0",
        lexicon_digest_sha256=DIGEST,
        score_policy_digest_sha256=DIGEST,
        pre_injection_citation_ids=(),
        post_injection_citation_ids=(),
        injection_omissions=(),
        minimization_ruleset_digest_sha256=None,
        minimization_input_digest_sha256=None,
        minimization_output_digest_sha256=None,
        minimization_retained_count=0,
        minimization_omitted_count=0,
        context_digest_sha256=None,
        output_schema_digest_sha256=None,
        gateway_request_digest_sha256=None,
        gateway_receipt_output_digest_sha256=None,
        provider_response_digest_sha256=None,
        validated_answer_digest_sha256=None,
        stages=build_stages(terminal_stage=RagStage.RETRIEVAL_BOUND, terminal_reason="RETRIEVAL_NOT_POSITIVE"),
        final_outcome=RagFinalOutcome.RETRIEVAL_NOT_POSITIVE,
        reason_code="RETRIEVAL_NOT_POSITIVE",
        physical_attempt_count=0,
    )
    fields.update(overrides)
    return build_receipt(**fields)


def _positive_receipt(**overrides):
    fields = dict(
        normalized_query_digest_sha256=DIGEST,
        retrieval_receipt_hash_sha256=DIGEST,
        retrieval_evidence_set_hash_sha256=DIGEST,
        authorization_scope_digest_sha256=DIGEST,
        corpus_id="PROJECT_KNOWLEDGE_LOCAL_V1",
        index_build_digest_sha256=DIGEST,
        encoder_version="1.0",
        lexicon_digest_sha256=DIGEST,
        score_policy_digest_sha256=DIGEST,
        pre_injection_citation_ids=(DIGEST,),
        post_injection_citation_ids=(DIGEST,),
        injection_omissions=(),
        minimization_ruleset_digest_sha256=DIGEST,
        minimization_input_digest_sha256=DIGEST,
        minimization_output_digest_sha256=DIGEST,
        minimization_retained_count=1,
        minimization_omitted_count=0,
        context_digest_sha256=DIGEST,
        output_schema_digest_sha256=DIGEST,
        gateway_request_digest_sha256=DIGEST,
        gateway_receipt_output_digest_sha256=DIGEST,
        provider_response_digest_sha256=DIGEST,
        validated_answer_digest_sha256=DIGEST,
        stages=build_stages(terminal_stage=None),
        final_outcome=RagFinalOutcome.ANSWERED,
        reason_code="",
        physical_attempt_count=1,
    )
    fields.update(overrides)
    return build_receipt(**fields)


def test_schema_file_is_valid_json_schema(schema):
    jsonschema.Draft202012Validator.check_schema(schema)


def test_negative_receipt_conforms(schema):
    payload = json.loads(_negative_receipt().model_dump_json())
    jsonschema.validate(payload, schema)


def test_positive_answered_receipt_conforms(schema):
    payload = json.loads(_positive_receipt().model_dump_json())
    jsonschema.validate(payload, schema)


def test_abstained_receipt_conforms(schema):
    payload = json.loads(_positive_receipt(final_outcome=RagFinalOutcome.ABSTAINED).model_dump_json())
    jsonschema.validate(payload, schema)


def test_schema_forbids_additional_properties(schema):
    payload = json.loads(_negative_receipt().model_dump_json())
    payload["unexpected_field"] = "x"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(payload, schema)


def test_schema_caps_physical_attempt_count_at_one(schema):
    payload = json.loads(_positive_receipt().model_dump_json())
    payload["physical_attempt_count"] = 2
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(payload, schema)


def test_schema_requires_digest_format(schema):
    payload = json.loads(_negative_receipt().model_dump_json())
    payload["normalized_query_digest_sha256"] = "short"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(payload, schema)


def test_schema_has_no_query_prompt_or_body_fields(schema):
    """R15: the contract must not even permit carrying raw bodies."""
    properties = set(schema["properties"])
    forbidden = {"query", "prompt", "context", "output", "evidence", "minimized_text", "authorization", "api_key"}
    assert not (properties & forbidden)


def test_schema_requires_all_nine_stages(schema):
    payload = json.loads(_negative_receipt().model_dump_json())
    payload["stages"] = payload["stages"][:8]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(payload, schema)
