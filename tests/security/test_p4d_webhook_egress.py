import os
import ssl

import pytest
from pydantic import ValidationError

from channel_adapters.egress import GenericWebhookConfig, authorize_endpoint
from channel_adapters.transport import StdlibResolvedHttpsTransport


def values(**changes):
    base = dict(endpoint_url="https://example.com:443/hook", allowed_host="example.com",
                allowed_port=443, allowed_path="/hook", key_id="kid",
                connect_timeout_seconds=1.0, total_timeout_seconds=2.0,
                max_request_bytes=1024, max_response_bytes=1024)
    base.update(changes)
    return base


@pytest.mark.parametrize(
    "endpoint",
    [
        "http://example.com:443/hook", "https://user@example.com:443/hook",
        "https://example.com:443/hook?q=1", "https://example.com:443/hook#f",
        "https://127.0.0.1:443/hook", "https://EXAMPLE.com:443/hook",
        "https://example.com.:443/hook", "https://example.com:443//hook",
        "https://example.com:443/a/../hook", "https://example.com:443/%68ook",
        "https://example.com:443/a\\b",
    ],
)
def test_config_rejects_noncanonical_or_untrusted_endpoint(endpoint):
    with pytest.raises(ValidationError):
        GenericWebhookConfig(**values(endpoint_url=endpoint))


def test_config_rejects_mismatch_nonfinite_and_invalid_bounds():
    for change in (
        {"allowed_host": "other.example"}, {"allowed_port": 444}, {"allowed_path": "/other"},
        {"connect_timeout_seconds": float("inf")}, {"total_timeout_seconds": 0.5},
        {"max_request_bytes": 0}, {"max_response_bytes": 65537},
    ):
        with pytest.raises(ValidationError):
            GenericWebhookConfig(**values(**change))


@pytest.mark.parametrize(
    "answer",
    ["127.0.0.1", "10.0.0.1", "169.254.1.1", "224.0.0.1", "0.0.0.0", "::1", "ff02::1"],
)
def test_resolver_rejects_every_non_global_address_class(answer):
    with pytest.raises(ValueError):
        authorize_endpoint(GenericWebhookConfig(**values()), lambda *_: (answer,))


def test_resolution_is_complete_deduplicated_and_deterministically_ordered():
    endpoint = authorize_endpoint(
        GenericWebhookConfig(**values()), lambda *_: ("2001:4860:4860::8888", "8.8.8.8", "8.8.8.8")
    )
    assert endpoint.approved_ips == ("8.8.8.8", "2001:4860:4860::8888")
    assert endpoint.audience == "https://example.com:443/hook"


def test_empty_invalid_or_mixed_disallowed_resolution_fails_closed():
    config = GenericWebhookConfig(**values())
    for answers in ((), ("not-an-ip",), ("8.8.8.8", "127.0.0.1")):
        with pytest.raises(ValueError):
            authorize_endpoint(config, lambda *_args, answers=answers: answers)


def test_transport_rejects_insecure_tls_context_and_ignores_proxy_environment(monkeypatch):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    with pytest.raises(ValueError):
        StdlibResolvedHttpsTransport(context)
    monkeypatch.setenv("HTTPS_PROXY", "http://127.0.0.1:9")
    assert StdlibResolvedHttpsTransport().trust_env is False
    assert os.environ["HTTPS_PROXY"] == "http://127.0.0.1:9"
