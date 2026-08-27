import hashlib
import hmac
import json
from datetime import datetime, timezone

from channel_adapters.signing import signed_headers, signing_preimage, utc_timestamp
from channel_sdk import AdapterDeliveryRequestV1, AuthorizedEndpointV1


def request(**changes):
    value = dict(
        version="1", command_id="c", idempotency_key="idem", correlation_id="r",
        workspace_digest="1" * 64, record_digest="2" * 64, action_digest="3" * 64,
        content_digest="4" * 64, recipient_digest="5" * 64, channel_digest="6" * 64,
        record_version=1, policy_version="p", prerequisite_receipt_refs=("ref",),
    )
    value.update(changes)
    return AdapterDeliveryRequestV1(**value)


def endpoint(host="example.com", port=443, path="/hook"):
    audience = f"https://{host}:{port}{path}"
    return AuthorizedEndpointV1(
        hostname=host, port=port, path=path, audience=audience,
        audience_digest=hashlib.sha256(audience.encode("ascii")).hexdigest(),
        approved_ips=("8.8.8.8",),
    )


def test_exact_timestamp_preimage_and_header_allowlist():
    now = datetime(2026, 8, 26, 1, 2, 3, 456789, timezone.utc)
    item = request()
    headers = signed_headers(request=item, endpoint=endpoint(), key_id="kid",
                             key=b"unit-test-key", now=now)
    assert headers["X-CVF-Timestamp"] == "2026-08-26T01:02:03.456789Z"
    expected_preimage = json.dumps(
        {"audience": endpoint().audience, "body_sha256": hashlib.sha256(item.canonical_bytes()).hexdigest(),
         "idempotency_key": "idem", "key_id": "kid", "method": "POST",
         "timestamp": headers["X-CVF-Timestamp"], "version": "v1"},
        ensure_ascii=True, sort_keys=True, separators=(",", ":"),
    ).encode()
    assert headers["X-CVF-Signature"] == hmac.new(b"unit-test-key", expected_preimage, hashlib.sha256).hexdigest()
    assert signing_preimage(endpoint=endpoint(), body_sha256=headers["X-CVF-Body-SHA256"],
                            idempotency_key="idem", key_id="kid",
                            timestamp=headers["X-CVF-Timestamp"]) == expected_preimage


def test_every_bound_fact_changes_signature():
    now = datetime(2026, 8, 26, tzinfo=timezone.utc)
    base = signed_headers(request=request(), endpoint=endpoint(), key_id="kid",
                          key=b"unit-test-key", now=now)["X-CVF-Signature"]
    variants = [
        signed_headers(request=request(content_digest="a" * 64), endpoint=endpoint(), key_id="kid", key=b"unit-test-key", now=now),
        signed_headers(request=request(idempotency_key="other"), endpoint=endpoint(), key_id="kid", key=b"unit-test-key", now=now),
        signed_headers(request=request(), endpoint=endpoint("example.net"), key_id="kid", key=b"unit-test-key", now=now),
        signed_headers(request=request(), endpoint=endpoint(port=444), key_id="kid", key=b"unit-test-key", now=now),
        signed_headers(request=request(), endpoint=endpoint(path="/other"), key_id="kid", key=b"unit-test-key", now=now),
        signed_headers(request=request(), endpoint=endpoint(), key_id="other", key=b"unit-test-key", now=now),
        signed_headers(request=request(), endpoint=endpoint(), key_id="kid", key=b"unit-test-key",
                       now=datetime(2026, 8, 26, 0, 0, 1, tzinfo=timezone.utc)),
    ]
    assert all(item["X-CVF-Signature"] != base for item in variants)


def test_naive_clock_is_rejected():
    try:
        utc_timestamp(datetime(2026, 8, 26))
        assert False
    except ValueError:
        pass
