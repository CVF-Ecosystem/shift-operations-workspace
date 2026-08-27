from datetime import datetime, timezone
import http.client
import hashlib

from channel_adapters import GenericWebhookAdapter, GenericWebhookConfig
from channel_sdk import AdapterDeliveryRequestV1


def request():
    return AdapterDeliveryRequestV1(
        version="1", command_id="c", idempotency_key="i", correlation_id="r",
        workspace_digest="1" * 64, record_digest="2" * 64, action_digest="3" * 64,
        content_digest="4" * 64, recipient_digest="5" * 64, channel_digest="6" * 64,
        record_version=1, policy_version="p", prerequisite_receipt_refs=("ref",),
    )


def config(**changes):
    value = dict(endpoint_url="https://example.com:443/hook", allowed_host="example.com",
                 allowed_port=443, allowed_path="/hook", key_id="kid",
                 connect_timeout_seconds=1.0, total_timeout_seconds=2.0,
                 max_request_bytes=4096, max_response_bytes=128)
    value.update(changes)
    return GenericWebhookConfig(**value)


class Connection:
    connected_peer_ip = "8.8.8.8"
    tls_server_name = "example.com"

    def __init__(self, response=(202, 0), error=None):
        self.response, self.error, self.calls, self.sent = response, error, 0, None

    def send(self, **kwargs):
        self.calls += 1
        self.sent = kwargs
        if self.error:
            raise self.error
        return self.response


class Transport:
    trust_env = False

    def __init__(self, connection):
        self.connection, self.calls = connection, 0

    def connect(self, endpoint, timeout):
        self.calls += 1
        return self.connection


def adapter(connection, *, resolver=lambda *_: ("8.8.8.8",), secret=None):
    return GenericWebhookAdapter(
        config=config(), resolver=resolver, transport=Transport(connection),
        secret_resolver=secret or (lambda *_: b"unit-test-key"),
        clock=lambda: datetime(2026, 8, 26, tzinfo=timezone.utc),
    )


def test_success_sends_once_and_is_accepted_not_delivered():
    connection = Connection((204, 0))
    sender = adapter(connection)
    result = sender.deliver(request=request(), idempotency_key="i")
    assert result.status == "SENT_ACCEPTED" and result.transport_attempted
    assert result.delivery_id.startswith("gwv1-") and connection.calls == 1
    assert connection.sent["method"] == "POST" and connection.sent["path"] == "/hook"
    assert set(connection.sent["headers"]) == {
        "Content-Type", "X-CVF-Signature-Version", "X-CVF-Key-Id", "X-CVF-Timestamp",
        "Idempotency-Key", "X-CVF-Body-SHA256", "X-CVF-Audience-SHA256", "X-CVF-Signature",
    }
    try:
        sender.adapter_mode = "CONFORMANCE_ONLY"
        assert False
    except AttributeError:
        pass


def test_http_classes_and_attempted_send_exception_have_no_retry():
    expected = [(404, "PROVIDER_REFUSED"), (503, "TERMINAL_FAILED"), (302, "TERMINAL_FAILED")]
    for status, outcome in expected:
        connection = Connection((status, 0))
        assert adapter(connection).deliver(request=request(), idempotency_key="i").status == outcome
        assert connection.calls == 1
    connection = Connection(error=TimeoutError("synthetic timeout"))
    result = adapter(connection).deliver(request=request(), idempotency_key="i")
    assert result.status == "OUTCOME_UNKNOWN" and result.transport_attempted and connection.calls == 1


def test_pre_attempt_failures_do_not_disclose_key_or_send():
    connection = Connection()
    calls = {"key": 0}
    def secret(*_):
        calls["key"] += 1
        return b"unit-test-key"
    sender = adapter(connection, resolver=lambda *_: ("127.0.0.1",), secret=secret)
    result = sender.deliver(request=request(), idempotency_key="i")
    assert result.status == "NOT_ATTEMPTED" and not result.transport_attempted
    assert calls["key"] == 0 and connection.calls == 0


def test_idempotency_mismatch_is_zero_resolver_connect_secret_send():
    connection = Connection()
    resolver_calls = []
    sender = adapter(connection, resolver=lambda *_: resolver_calls.append(1) or ("8.8.8.8",))
    result = sender.deliver(request=request(), idempotency_key="wrong")
    assert result.reason == "INVALID_REQUEST" and resolver_calls == [] and connection.calls == 0


def test_telemetry_contains_digests_not_payload_signature_or_key_bytes():
    sender = adapter(Connection())
    sender.deliver(request=request(), idempotency_key="i")
    text = repr(dict(sender.last_telemetry))
    assert "unit-test-key" not in text and "X-CVF-Signature" not in text
    assert set(sender.last_telemetry) <= {
        "adapter_id", "adapter_mode", "key_id", "signature_version", "audience_digest",
        "body_digest", "request_byte_length", "transport_attempted", "status_class", "result_status",
    }
    sender.deliver(request=request(), idempotency_key="wrong")
    assert dict(sender.last_telemetry) == {}


def test_exact_pre_attempt_stage_counts_and_audience_bound_secret_args():
    cases = [
        ("connect", "8.8.8.8", "example.com", RuntimeError("connect"), None, (1, 1, 0, 0)),
        ("peer", "1.1.1.1", "example.com", None, None, (1, 1, 0, 0)),
        ("tls", "8.8.8.8", "other.example", None, None, (1, 1, 0, 0)),
        ("secret", "8.8.8.8", "example.com", None, RuntimeError("secret"), (1, 1, 1, 0)),
    ]
    for _name, peer, tls_name, connect_error, secret_error, expected in cases:
        counts = {"resolver": 0, "connect": 0, "secret": 0}
        connection = Connection()
        connection.connected_peer_ip, connection.tls_server_name = peer, tls_name
        class StageTransport:
            trust_env = False
            def connect(self, *_args):
                counts["connect"] += 1
                if connect_error:
                    raise connect_error
                return connection
        def resolver(*_args):
            counts["resolver"] += 1
            return ("8.8.8.8",)
        seen = []
        def secret(*args):
            counts["secret"] += 1
            seen.append(args)
            if secret_error:
                raise secret_error
            return b"unit-test-key"
        sender = GenericWebhookAdapter(config=config(), resolver=resolver, transport=StageTransport(),
                                       secret_resolver=secret,
                                       clock=lambda: datetime(2026, 8, 26, tzinfo=timezone.utc))
        result = sender.deliver(request=request(), idempotency_key="i")
        actual = (counts["resolver"], counts["connect"], counts["secret"], connection.calls)
        assert actual == expected and result.status == "NOT_ATTEMPTED"
        if seen:
            audience_digest = hashlib.sha256(b"https://example.com:443/hook").hexdigest()
            assert seen == [("kid", audience_digest)]


def test_max_request_response_ceiling_and_structural_status_mapping():
    resolver_calls = []
    too_small = GenericWebhookAdapter(
        config=config(max_request_bytes=1),
        resolver=lambda *_: resolver_calls.append(1) or ("8.8.8.8",),
        transport=Transport(Connection()), secret_resolver=lambda *_: b"unit-test-key",
        clock=lambda: datetime(2026, 8, 26, tzinfo=timezone.utc),
    )
    result = too_small.deliver(request=request(), idempotency_key="i")
    assert result.reason == "INVALID_REQUEST" and resolver_calls == []
    oversized = adapter(Connection((200, 129))).deliver(request=request(), idempotency_key="i")
    assert oversized.status == "OUTCOME_UNKNOWN" and oversized.transport_attempted
    malformed_connection = Connection(error=http.client.BadStatusLine("synthetic bad status"))
    malformed = adapter(malformed_connection).deliver(
        request=request(), idempotency_key="i"
    )
    assert malformed.status == "TERMINAL_FAILED" and malformed.reason == "INVALID_RESPONSE"
    assert malformed.transport_attempted and malformed_connection.calls == 1


def test_remote_disconnect_is_ambiguous_after_one_send_with_no_retry():
    connection = Connection(error=http.client.RemoteDisconnected("synthetic remote close"))

    result = adapter(connection).deliver(request=request(), idempotency_key="i")

    assert result.status == "OUTCOME_UNKNOWN"
    assert result.reason == "AMBIGUOUS_TRANSPORT"
    assert result.transport_attempted and connection.calls == 1
