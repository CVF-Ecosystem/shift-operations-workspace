import json
from pathlib import Path

import jsonschema
import pytest

from channel_adapters.conformance import emit_adapter_result
from channel_sdk import AdapterDeliveryResultV1
from channel_sdk.invariants import adapter_result_matrix


ROOT = Path(__file__).resolve().parents[2]
SCHEMA = json.loads((ROOT / "contracts/channel/adapter-delivery.schema.json").read_text())


def request_value():
    return {
        "version": "1", "command_id": "c", "idempotency_key": "i", "correlation_id": "r",
        "workspace_digest": "1" * 64, "record_digest": "2" * 64,
        "action_digest": "3" * 64, "content_digest": "4" * 64,
        "recipient_digest": "5" * 64, "channel_digest": "6" * 64,
        "record_version": 1, "policy_version": "p", "prerequisite_receipt_refs": ["x"],
    }


def test_schema_is_draft_202012_and_closed():
    jsonschema.Draft202012Validator.check_schema(SCHEMA)
    assert SCHEMA["$schema"].endswith("draft/2020-12/schema")
    objects = [item for item in SCHEMA["$defs"].values() if item.get("type") == "object"]
    objects += SCHEMA["$defs"]["AdapterDeliveryResultV1"]["oneOf"]
    assert all(item["additionalProperties"] is False for item in objects)


def test_schema_accepts_request_and_all_result_outcomes():
    jsonschema.validate(request_value(), SCHEMA)
    positives = [
        emit_adapter_result(item["outcomeId"]).model_dump(exclude_none=True)
        for item in adapter_result_matrix()["outcomes"]
    ]
    for value in positives:
        jsonschema.validate(value, SCHEMA)
        AdapterDeliveryResultV1(**value)


def test_matrix_derived_one_fact_mutations_fail_both_surfaces():
    for outcome in adapter_result_matrix()["outcomes"]:
        value = emit_adapter_result(outcome["outcomeId"]).model_dump(exclude_none=True)
        mutations = [value | {"unexpected": True}, value | {"transport_attempted": not value["transport_attempted"]}]
        missing = dict(value)
        missing.pop("status")
        mutations.append(missing)
        mutations.append(value | {"status": "UNKNOWN"})
        mutations.append(value | {"transport_attempted": 1})
        if "reason" in value:
            mutations.append(value | {"reason": "UNKNOWN_REASON"})
        if "delivery_id" in value:
            mutations.append(value | {"delivery_id": "bad"})
        for mutation in mutations:
            with pytest.raises(jsonschema.ValidationError):
                jsonschema.validate(mutation, SCHEMA)
            with pytest.raises(Exception):
                AdapterDeliveryResultV1(**mutation)


@pytest.mark.parametrize("change", [{"extra": 1}, {"record_version": "1"}, {"version": "2"}])
def test_schema_rejects_request_mutations(change):
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(request_value() | change, SCHEMA)
