"""A direct-to-approved-IP stdlib HTTPS transport with no proxy or redirect."""

from __future__ import annotations

import http.client
import ipaddress
import socket
import ssl
import time

from channel_sdk import AuthorizedEndpointV1


class _BoundConnection:
    def __init__(self, sock: ssl.SSLSocket, endpoint: AuthorizedEndpointV1) -> None:
        self._sock = sock
        self._endpoint = endpoint
        self.connected_peer_ip = str(sock.getpeername()[0])
        self.tls_server_name = endpoint.hostname

    def send(
        self,
        *,
        method: str,
        path: str,
        headers,
        body: bytes,
        total_timeout_seconds: float,
        max_response_bytes: int,
    ) -> tuple[int, int]:
        deadline = time.monotonic() + total_timeout_seconds
        self._sock.settimeout(total_timeout_seconds)
        connection = http.client.HTTPConnection(self._endpoint.hostname, self._endpoint.port)
        connection.sock = self._sock
        connection.request(method, path, body=body, headers={"Host": self._endpoint.hostname, **dict(headers)})
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("total HTTPS deadline exceeded")
        self._sock.settimeout(remaining)
        response = connection.getresponse()
        length = 0
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("total HTTPS deadline exceeded")
            self._sock.settimeout(remaining)
            chunk = response.read(min(8192, max_response_bytes + 1 - length))
            if not chunk:
                break
            length += len(chunk)
            if length > max_response_bytes:
                raise OverflowError("response exceeds configured byte ceiling")
        return response.status, length


class StdlibResolvedHttpsTransport:
    """Connects once to the first policy-approved address; resolution is external."""

    def __init__(self, ssl_context: ssl.SSLContext | None = None) -> None:
        self._context = ssl_context or ssl.create_default_context()
        if not self._context.check_hostname or self._context.verify_mode != ssl.CERT_REQUIRED:
            raise ValueError("TLS context must verify certificates and hostnames")

    def connect(
        self,
        authorized_endpoint: AuthorizedEndpointV1,
        connect_timeout_seconds: float,
    ) -> _BoundConnection:
        address = ipaddress.ip_address(authorized_endpoint.approved_ips[0])
        family = socket.AF_INET6 if address.version == 6 else socket.AF_INET
        raw = socket.socket(family, socket.SOCK_STREAM)
        raw.settimeout(connect_timeout_seconds)
        try:
            target = (str(address), authorized_endpoint.port, 0, 0) if address.version == 6 else (str(address), authorized_endpoint.port)
            raw.connect(target)
            tls = self._context.wrap_socket(raw, server_hostname=authorized_endpoint.hostname)
        except Exception:
            raw.close()
            raise
        return _BoundConnection(tls, authorized_endpoint)
    trust_env = False
