from channel_adapters.conformance import emit_adapter_result
from integration_edge.outbound import AdapterScopeBindingV1, OutboundService
from integration_edge.storage import InMemoryEdgeStore


def command(**changes):
    value = dict(
        version="1", command_id="c", workspace_digest="1" * 64,
        record_digest="2" * 64, action_digest="3" * 64, record_version=1,
        content_digest="4" * 64, recipient_digest="5" * 64, channel_digest="6" * 64,
        idempotency_key="idem", policy_version="p", prerequisite_receipt_refs=("ref",),
        correlation_id="corr",
    )
    value.update(changes)
    return value


def binding(**changes):
    value = dict(workspace_digest="1" * 64, channel_digest="6" * 64,
                 policy_version="p", required_prerequisite_receipt_ref="ref",
                 adapter_id="generic-webhook")
    value.update(changes)
    return AdapterScopeBindingV1(**value)


class Adapter:
    adapter_mode = "DEPLOYABLE"
    def __init__(self, result):
        self.result, self.calls = result, 0
    def deliver(self, **kwargs):
        self.calls += 1
        return self.result


def verifier(*_args, **_kwargs):
    return True


def run(result, *, bindings=None):
    adapter = Adapter(result)
    receipt = OutboundService(InMemoryEdgeStore(), adapter, verifier,
                              scope_bindings=tuple((binding(),) if bindings is None else bindings)).deliver(command(), "assert")
    return receipt, adapter


def test_total_adapter_result_to_receipt_mapping():
    expected = {
        "NOT_ATTEMPTED": ("NOT_ATTEMPTED", 0), "SENT_ACCEPTED": ("SENT_ACCEPTED", 1),
        "PROVIDER_REFUSED": ("PROVIDER_REFUSED", 1), "TERMINAL_FAILED": ("TERMINAL_FAILED", 1),
        "OUTCOME_UNKNOWN": ("OUTCOME_UNKNOWN", 1),
    }
    for status, receipt_fact in expected.items():
        receipt, adapter = run(emit_adapter_result(status))
        assert (receipt.outcome, receipt.delivery_attempts) == receipt_fact and adapter.calls == 1
        assert receipt.outcome != "DELIVERED"
        if status == "SENT_ACCEPTED":
            assert receipt.delivery_id == "gwv1-" + "0" * 64
        if status == "TERMINAL_FAILED":
            assert receipt.reason == emit_adapter_result(status).reason


def test_zero_duplicate_mismatch_or_conformance_scope_is_zero_call():
    cases = [
        (), (binding(), binding()), (binding(workspace_digest="9" * 64),),
        (binding(channel_digest="9" * 64),), (binding(policy_version="other"),),
        (binding(required_prerequisite_receipt_ref="missing"),),
    ]
    for bindings in cases:
        receipt, adapter = run(emit_adapter_result("SENT_ACCEPTED"), bindings=bindings)
        assert receipt.outcome == "NOT_ATTEMPTED" and receipt.delivery_attempts == 0 and adapter.calls == 0
    adapter = Adapter(emit_adapter_result("SENT_ACCEPTED"))
    adapter.adapter_mode = "CONFORMANCE_ONLY"
    receipt = OutboundService(InMemoryEdgeStore(), adapter, verifier,
                              scope_bindings=(binding(),)).deliver(command(), "assert")
    assert receipt.reason == "ADAPTER_UNAVAILABLE" and adapter.calls == 0


def test_exception_or_malformed_result_is_conservative_terminal_and_no_retry():
    class Bad(Adapter):
        def deliver(self, **kwargs):
            self.calls += 1
            if self.result == "raise":
                raise RuntimeError("synthetic")
            return self.result
    for result in ("raise", {"status": "NOT_ATTEMPTED"}):
        adapter = Bad(result)
        store = InMemoryEdgeStore()
        service = OutboundService(store, adapter, verifier, scope_bindings=(binding(),))
        receipt = service.deliver(command(), "assert")
        again = service.deliver(command(), "assert")
        assert receipt.outcome == again.outcome == "OUTCOME_UNKNOWN"
        assert receipt.delivery_attempts == 1 and adapter.calls == 1


def test_invalid_trusted_binding_and_sdk_projection_fail_closed_before_adapter():
    adapter = Adapter(emit_adapter_result("SENT_ACCEPTED"))
    service = OutboundService(InMemoryEdgeStore(), adapter, verifier,
                              scope_bindings=({"adapter_id": "generic-webhook"},))
    receipt = service.deliver(command(), "assert")
    assert receipt.reason == "ADAPTER_UNAVAILABLE" and adapter.calls == 0
    too_long = command(command_id="x" * 257)
    receipt = OutboundService(InMemoryEdgeStore(), adapter, verifier,
                              scope_bindings=(binding(),)).deliver(too_long, "assert")
    assert receipt.reason == "ADAPTER_UNAVAILABLE" and adapter.calls == 0
