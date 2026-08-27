"""Synthetic provider-neutral conformance emitters; never runtime adapters."""

from __future__ import annotations

from channel_sdk import AdapterDeliveryRequestV1, AdapterDeliveryResultV1
from channel_sdk.invariants import adapter_result_matrix


def emit_adapter_result(status: str) -> AdapterDeliveryResultV1:
    matches = [item for item in adapter_result_matrix()["outcomes"] if item["outcomeId"] == status]
    if len(matches) != 1:
        raise ValueError("unknown synthetic adapter result status")
    shape = matches[0]["shapes"][0]
    value = {}
    for field, domain in shape["fieldDomains"].items():
        if "const" in domain:
            value[field] = domain["const"]
        elif "enum" in domain:
            value[field] = domain["enum"][0]
        elif field == "delivery_id":
            value[field] = "gwv1-" + "0" * 64
        else:
            raise ValueError("matrix domain has no deterministic sample")
    return AdapterDeliveryResultV1.model_validate(value)


class _ConformanceAdapter:
    @property
    def adapter_mode(self):
        return "CONFORMANCE_ONLY"

    def __init__(self, outcome: str = "SENT_ACCEPTED") -> None:
        emit_adapter_result(outcome)
        self._outcome = outcome

    def deliver(
        self, *, request: AdapterDeliveryRequestV1, idempotency_key: str
    ) -> AdapterDeliveryResultV1:
        if not isinstance(request, AdapterDeliveryRequestV1) or idempotency_key != request.idempotency_key:
            return emit_adapter_result("NOT_ATTEMPTED")
        return emit_adapter_result(self._outcome)


class ZaloConformanceAdapter(_ConformanceAdapter):
    @property
    def adapter_id(self):
        return "zalo"


class WhatsAppConformanceAdapter(_ConformanceAdapter):
    @property
    def adapter_id(self):
        return "whatsapp"
