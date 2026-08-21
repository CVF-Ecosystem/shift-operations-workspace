"""P4-A contract test - receipts conform to the published schema.

NOT GOVERNANCE PROOF: schema conformance only. The live receipt produced by the
R13 run is validated against this same schema by the evidence runner.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ai_gateway.models import (
    AIMode,
    Classification,
    FinalOutcome,
    GateOutcome,
    GateRecord,
    GatewayReceipt,
    Placement,
)

SCHEMA_PATH = (
    Path(__file__).resolve().parents[2]
    / "packages"
    / "ai-gateway"
    / "contracts"
    / "ai_gateway.schema.json"
)
DIGEST = "d" * 64

jsonschema = pytest.importorskip("jsonschema", reason="jsonschema is a dev dependency")


@pytest.fixture(scope="module")
def schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _receipt(**overrides) -> GatewayReceipt:
    base = dict(
        task_type="canary",
        provider_id="alibaba_dashscope",
        model_id="model-a",
        endpoint_origin="https://example.invalid",
        ai_mode=AIMode.EXTERNAL_AI,
        classification=Classification.PUBLIC,
        placement=Placement.EXTERNAL,
        request_digest=DIGEST,
        context_digest=DIGEST,
        output_schema_digest=DIGEST,
        gates=(GateRecord(gate="data_scope.assert_placement_allowed", outcome=GateOutcome.PASS),),
        final_outcome=FinalOutcome.REFUSED_PRE_DISPATCH,
        started_at="2026-08-20T00:00:00+00:00",
        finished_at="2026-08-20T00:00:01+00:00",
    )
    base.update(overrides)
    return GatewayReceipt(**base)


def test_schema_file_is_valid_json_schema(schema):
    jsonschema.Draft202012Validator.check_schema(schema)


def test_refusal_receipt_conforms(schema):
    payload = json.loads(_receipt().model_dump_json())
    jsonschema.validate(payload, schema)


def test_accepted_receipt_conforms(schema):
    receipt = _receipt(
        final_outcome=FinalOutcome.ACCEPTED,
        provider_attempts=1,
        output_digest=DIGEST,
        usage_committed=True,
        actual_tokens=12,
        actual_cost_usd_millis=3,
    )
    jsonschema.validate(json.loads(receipt.model_dump_json()), schema)


def test_schema_forbids_additional_properties(schema):
    payload = json.loads(_receipt().model_dump_json())
    payload["unexpected_field"] = "x"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(payload, schema)


def test_schema_caps_provider_attempts_at_one(schema):
    payload = json.loads(_receipt().model_dump_json())
    payload["provider_attempts"] = 2
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(payload, schema)


def test_schema_requires_digest_format(schema):
    payload = json.loads(_receipt().model_dump_json())
    payload["request_digest"] = "short"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(payload, schema)


def test_schema_has_no_prompt_or_output_body_fields(schema):
    """R10: the contract must not even permit carrying raw bodies."""
    properties = set(schema["properties"])
    forbidden = {"prompt", "context", "output", "messages", "authorization", "api_key"}
    assert not (properties & forbidden)
