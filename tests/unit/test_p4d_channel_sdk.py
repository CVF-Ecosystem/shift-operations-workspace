import json

import pytest
from pydantic import ValidationError

from channel_sdk import AdapterDeliveryRequestV1, AdapterDeliveryResultV1


def request_value(**changes):
    value = {
        "version": "1",
        "command_id": "cmd-1",
        "idempotency_key": "idem-1",
        "correlation_id": "corr-1",
        "workspace_digest": "1" * 64,
        "record_digest": "2" * 64,
        "action_digest": "3" * 64,
        "content_digest": "4" * 64,
        "recipient_digest": "5" * 64,
        "channel_digest": "6" * 64,
        "record_version": 1,
        "policy_version": "policy-1",
        "prerequisite_receipt_refs": ("receipt-b", "receipt-a"),
    }
    value.update(changes)
    return value


def test_request_is_closed_strict_frozen_and_canonical():
    request = AdapterDeliveryRequestV1(**request_value())
    assert request.prerequisite_receipt_refs == ("receipt-a", "receipt-b")
    assert request.canonical_bytes() == json.dumps(
        request.model_dump(mode="json"), ensure_ascii=True, sort_keys=True, separators=(",", ":")
    ).encode()
    for change in ({"extra": True}, {"record_version": "1"}, {"version": 1}):
        with pytest.raises(ValidationError):
            AdapterDeliveryRequestV1(**request_value(**change))
    value = request_value()
    value.pop("version")
    with pytest.raises(ValidationError):
        AdapterDeliveryRequestV1(**value)
    with pytest.raises(ValidationError):
        request.command_id = "changed"


def test_request_rejects_duplicate_empty_and_cleartext_fields():
    for refs in (("x", "x"), ("",), ()):
        with pytest.raises(ValidationError):
            AdapterDeliveryRequestV1(**request_value(prerequisite_receipt_refs=refs))
    with pytest.raises(ValidationError):
        AdapterDeliveryRequestV1(**request_value(message_text="forbidden"))


@pytest.mark.parametrize(
    "value",
    [
        {"status": "NOT_ATTEMPTED", "transport_attempted": False, "reason": "INVALID_REQUEST"},
        {"status": "SENT_ACCEPTED", "transport_attempted": True, "delivery_id": "gwv1-" + "a" * 64},
        {"status": "PROVIDER_REFUSED", "transport_attempted": True, "reason": "PROVIDER_REFUSED"},
        {"status": "TERMINAL_FAILED", "transport_attempted": True, "reason": "INVALID_RESPONSE"},
        {"status": "OUTCOME_UNKNOWN", "transport_attempted": True, "reason": "AMBIGUOUS_TRANSPORT"},
    ],
)
def test_result_accepts_closed_positive_shapes(value):
    assert AdapterDeliveryResultV1(**value).model_dump(exclude_none=True) == value


def test_result_rejects_explicit_null_coercion_and_bad_attempt_fact():
    base = {"status": "SENT_ACCEPTED", "transport_attempted": True, "delivery_id": "gwv1-" + "a" * 64}
    for change in ({"reason": None}, {"transport_attempted": 1}, {"delivery_id": None}):
        with pytest.raises(ValidationError):
            AdapterDeliveryResultV1(**(base | change))
