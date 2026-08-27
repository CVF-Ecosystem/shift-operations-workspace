"""One-shot digest-only generic webhook adapter."""

from __future__ import annotations

import hashlib
import http.client
import ipaddress
from datetime import datetime
from types import MappingProxyType
from typing import Callable

from channel_sdk import AdapterDeliveryRequestV1, AdapterDeliveryResultV1

from .egress import GenericWebhookConfig, authorize_endpoint
from .signing import signed_headers


class GenericWebhookAdapter:
    @property
    def adapter_mode(self):
        return "DEPLOYABLE"

    @property
    def adapter_id(self):
        return "generic-webhook"

    def __init__(
        self,
        *,
        config: GenericWebhookConfig,
        resolver: Callable[[str, int], object],
        transport,
        secret_resolver: Callable[[str, str], bytes],
        clock: Callable[[], datetime],
    ) -> None:
        self._config = config
        self._resolver = resolver
        self._transport = transport
        self._secret_resolver = secret_resolver
        self._clock = clock
        self._last_telemetry = MappingProxyType({})

    @property
    def last_telemetry(self):
        return self._last_telemetry

    @staticmethod
    def _not_attempted(reason: str) -> AdapterDeliveryResultV1:
        return AdapterDeliveryResultV1(
            status="NOT_ATTEMPTED", transport_attempted=False, reason=reason
        )

    def deliver(
        self, *, request: AdapterDeliveryRequestV1, idempotency_key: str
    ) -> AdapterDeliveryResultV1:
        self._last_telemetry = MappingProxyType({})
        if not isinstance(request, AdapterDeliveryRequestV1):
            return self._not_attempted("INVALID_REQUEST")
        if idempotency_key != request.idempotency_key:
            return self._not_attempted("INVALID_REQUEST")
        body = request.canonical_bytes()
        if len(body) > self._config.max_request_bytes:
            return self._not_attempted("INVALID_REQUEST")
        try:
            endpoint = authorize_endpoint(self._config, self._resolver)
        except Exception:
            return self._not_attempted("RESOLUTION_NOT_AUTHORIZED")
        try:
            connection = self._transport.connect(
                endpoint, self._config.connect_timeout_seconds
            )
        except Exception:
            return self._not_attempted("TRANSPORT_UNAVAILABLE")
        try:
            peer = str(ipaddress.ip_address(connection.connected_peer_ip))
        except (ValueError, TypeError):
            return self._not_attempted("CONNECTION_NOT_AUTHORIZED")
        if peer not in endpoint.approved_ips or connection.tls_server_name != endpoint.hostname:
            return self._not_attempted("CONNECTION_NOT_AUTHORIZED")
        try:
            key = self._secret_resolver(self._config.key_id, endpoint.audience_digest)
            if not isinstance(key, bytes) or not key:
                raise ValueError("secret resolver returned no key bytes")
            headers = signed_headers(
                request=request,
                endpoint=endpoint,
                key_id=self._config.key_id,
                key=key,
                now=self._clock(),
            )
        except Exception:
            return self._not_attempted("SIGNING_UNAVAILABLE")
        body_digest = hashlib.sha256(body).hexdigest()
        safe = {
            "adapter_id": self.adapter_id,
            "adapter_mode": self.adapter_mode,
            "key_id": self._config.key_id,
            "signature_version": "v1",
            "audience_digest": endpoint.audience_digest,
            "body_digest": body_digest,
            "request_byte_length": len(body),
            "transport_attempted": True,
        }
        try:
            status, response_bytes = connection.send(
                method="POST",
                path=endpoint.path,
                headers=headers,
                body=body,
                total_timeout_seconds=self._config.total_timeout_seconds,
                max_response_bytes=self._config.max_response_bytes,
            )
        except http.client.RemoteDisconnected:
            result = AdapterDeliveryResultV1(
                status="OUTCOME_UNKNOWN",
                transport_attempted=True,
                reason="AMBIGUOUS_TRANSPORT",
            )
            self._last_telemetry = MappingProxyType(
                {**safe, "status_class": "UNKNOWN", "result_status": result.status}
            )
            return result
        except http.client.BadStatusLine:
            result = AdapterDeliveryResultV1(
                status="TERMINAL_FAILED",
                transport_attempted=True,
                reason="INVALID_RESPONSE",
            )
            self._last_telemetry = MappingProxyType(
                {**safe, "status_class": "INVALID", "result_status": result.status}
            )
            return result
        except Exception:
            result = AdapterDeliveryResultV1(
                status="OUTCOME_UNKNOWN",
                transport_attempted=True,
                reason="AMBIGUOUS_TRANSPORT",
            )
            self._last_telemetry = MappingProxyType(
                {**safe, "status_class": "UNKNOWN", "result_status": result.status}
            )
            return result
        if type(response_bytes) is int and response_bytes > self._config.max_response_bytes:
            result = AdapterDeliveryResultV1(
                status="OUTCOME_UNKNOWN",
                transport_attempted=True,
                reason="AMBIGUOUS_TRANSPORT",
            )
        else:
            result = self._classify(
                status, response_bytes, endpoint.audience_digest, request, body_digest
            )
        status_class = f"{status // 100}xx" if isinstance(status, int) and 100 <= status <= 599 else "INVALID"
        self._last_telemetry = MappingProxyType(
            {**safe, "status_class": status_class, "result_status": result.status}
        )
        return result

    @staticmethod
    def _classify(status, response_bytes, audience_digest, request, body_digest):
        if type(status) is not int or type(response_bytes) is not int or response_bytes < 0:
            return AdapterDeliveryResultV1(
                status="TERMINAL_FAILED", transport_attempted=True, reason="INVALID_RESPONSE"
            )
        if 200 <= status <= 299:
            seed = "\n".join(
                ("generic-webhook-v1", audience_digest, request.idempotency_key, body_digest)
            ).encode("ascii")
            return AdapterDeliveryResultV1(
                status="SENT_ACCEPTED",
                transport_attempted=True,
                delivery_id="gwv1-" + hashlib.sha256(seed).hexdigest(),
            )
        if 400 <= status <= 499:
            return AdapterDeliveryResultV1(
                status="PROVIDER_REFUSED",
                transport_attempted=True,
                reason="PROVIDER_REFUSED",
            )
        reason = "NONRETRYABLE_ERROR" if 500 <= status <= 599 else "INVALID_RESPONSE"
        return AdapterDeliveryResultV1(
            status="TERMINAL_FAILED", transport_attempted=True, reason=reason
        )
