import pytest

from channel_adapters import WhatsAppConformanceAdapter, ZaloConformanceAdapter
from channel_sdk import AdapterDeliveryRequestV1
from channel_sdk.invariants import adapter_result_matrix


def request():
    return AdapterDeliveryRequestV1(
        version="1", command_id="c", idempotency_key="i", correlation_id="r",
        workspace_digest="1" * 64, record_digest="2" * 64, action_digest="3" * 64,
        content_digest="4" * 64, recipient_digest="5" * 64, channel_digest="6" * 64,
        record_version=1, policy_version="p", prerequisite_receipt_refs=("ref",),
    )


@pytest.mark.parametrize("adapter_type", [ZaloConformanceAdapter, WhatsAppConformanceAdapter])
def test_conformance_adapters_are_permanently_non_runtime_and_emit_full_corpus(adapter_type, monkeypatch):
    def forbidden(*_args, **_kwargs):
        raise AssertionError("conformance adapter attempted I/O or environment access")
    monkeypatch.setattr("socket.socket", forbidden)
    monkeypatch.setattr("socket.getaddrinfo", forbidden)
    monkeypatch.setattr("os.getenv", forbidden)
    for outcome in [item["outcomeId"] for item in adapter_result_matrix()["outcomes"]]:
        adapter = adapter_type(outcome)
        result = adapter.deliver(request=request(), idempotency_key="i")
        assert adapter.adapter_mode == "CONFORMANCE_ONLY" and result.status == outcome
        with pytest.raises(AttributeError):
            adapter.adapter_mode = "DEPLOYABLE"


def test_unknown_synthetic_fixture_is_rejected_at_construction():
    with pytest.raises(ValueError):
        ZaloConformanceAdapter("UNKNOWN")
