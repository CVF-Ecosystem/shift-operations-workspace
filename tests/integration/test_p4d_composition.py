from datetime import datetime, timezone

from channel_adapters import GenericWebhookConfig
from integration_edge.main import create_app
from integration_edge.outbound import AdapterScopeBindingV1
from integration_edge.storage import InMemoryEdgeStore


class NoNetworkTransport:
    trust_env = False
    def connect(self, *_args):
        raise AssertionError("composition test must not use network")


def config():
    return GenericWebhookConfig(
        endpoint_url="https://example.com:443/hook", allowed_host="example.com",
        allowed_port=443, allowed_path="/hook", key_id="kid",
        connect_timeout_seconds=1, total_timeout_seconds=2,
        max_request_bytes=1024, max_response_bytes=1024,
    )


def verifier(*_args, **_kwargs):
    return True


def test_factory_is_the_runtime_generic_adapter_composition_root():
    binding = AdapterScopeBindingV1(
        workspace_digest="1" * 64, channel_digest="2" * 64, policy_version="p",
        required_prerequisite_receipt_ref="ref", adapter_id="generic-webhook",
    )
    app = create_app(
        adapter_id="generic-webhook", webhook_config=config(), resolver=lambda *_: ("8.8.8.8",),
        transport=NoNetworkTransport(), secret_resolver=lambda *_: b"unit-test-key",
        clock=lambda: datetime(2026, 8, 26, tzinfo=timezone.utc),
        store=InMemoryEdgeStore(), assertion_verifier=verifier, scope_bindings=(binding,),
    )
    assert app.state.outbound_service.adapter.adapter_mode == "DEPLOYABLE"


def test_factory_rejects_unknown_missing_and_conformance_only_ids():
    for adapter_id in (None, "unknown", "zalo", "whatsapp"):
        app = create_app(adapter_id=adapter_id, webhook_config=config(),
                         resolver=lambda *_: ("8.8.8.8",), transport=NoNetworkTransport(),
                         secret_resolver=lambda *_: b"unit-test-key", store=InMemoryEdgeStore(),
                         assertion_verifier=verifier)
        assert app.state.outbound_service.adapter is None
