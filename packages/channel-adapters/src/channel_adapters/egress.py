"""Immutable webhook configuration and fail-closed endpoint authorization."""

from __future__ import annotations

import hashlib
import ipaddress
import math
from collections.abc import Callable, Iterable
from urllib.parse import urlsplit

from channel_sdk import AuthorizedEndpointV1
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class GenericWebhookConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    endpoint_url: str
    allowed_host: str = Field(min_length=1, max_length=253)
    allowed_port: int = Field(ge=1, le=65535)
    allowed_path: str = Field(min_length=1, max_length=2048)
    key_id: str = Field(min_length=1, max_length=128)
    connect_timeout_seconds: float = Field(gt=0, le=10)
    total_timeout_seconds: float = Field(gt=0, le=30)
    max_request_bytes: int = Field(ge=1, le=65536)
    max_response_bytes: int = Field(ge=1, le=65536)

    @field_validator("connect_timeout_seconds", "total_timeout_seconds")
    @classmethod
    def finite_timeout(cls, value: float) -> float:
        if not math.isfinite(value):
            raise ValueError("timeout must be finite")
        return value

    @model_validator(mode="after")
    def validate_endpoint(self) -> "GenericWebhookConfig":
        if self.total_timeout_seconds < self.connect_timeout_seconds:
            raise ValueError("total timeout must cover connect timeout")
        parsed = urlsplit(self.endpoint_url)
        try:
            port = 443 if parsed.port is None else parsed.port
        except ValueError as exc:
            raise ValueError("invalid endpoint port") from exc
        if parsed.scheme != "https" or not parsed.hostname or parsed.port == 0:
            raise ValueError("endpoint must be HTTPS with a hostname")
        if parsed.username is not None or parsed.password is not None or parsed.query or parsed.fragment:
            raise ValueError("endpoint user-info, query and fragment are forbidden")
        host = parsed.hostname
        raw_authority = parsed.netloc
        raw_host = raw_authority.rsplit(":", 1)[0] if ":" in raw_authority else raw_authority
        if raw_host != host:
            raise ValueError("endpoint hostname must already be canonical")
        if _canonical_host(host) != host or _is_ip_literal(host):
            raise ValueError("endpoint hostname must be canonical lowercase IDNA")
        if host != self.allowed_host or port != self.allowed_port or parsed.path != self.allowed_path:
            raise ValueError("endpoint does not match its allowlist")
        _validate_path(parsed.path)
        return self


def _canonical_host(host: str) -> str:
    try:
        return host.encode("idna").decode("ascii").lower().rstrip(".")
    except UnicodeError as exc:
        raise ValueError("invalid IDNA hostname") from exc


def _is_ip_literal(host: str) -> bool:
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return False


def _validate_path(path: str) -> None:
    if not path.startswith("/") or not path.isascii() or any(x in path for x in ("%", "\\", "//")):
        raise ValueError("endpoint path is not canonical ASCII")
    if any(segment in {".", ".."} for segment in path.split("/")):
        raise ValueError("endpoint path contains a dot segment")


def authorize_endpoint(config: GenericWebhookConfig, resolver: Callable[[str, int], Iterable[str]]) -> AuthorizedEndpointV1:
    raw = tuple(resolver(config.allowed_host, config.allowed_port))
    if not raw:
        raise ValueError("resolver returned no addresses")
    try:
        addresses = tuple(ipaddress.ip_address(item) for item in raw)
    except ValueError as exc:
        raise ValueError("resolver returned an invalid address") from exc
    if any(
        not address.is_global
        or address.is_private
        or address.is_loopback
        or address.is_link_local
        or address.is_multicast
        or address.is_reserved
        or address.is_unspecified
        for address in addresses
    ):
        raise ValueError("resolver set contains a non-global address")
    approved = tuple(
        str(address)
        for address in sorted(set(addresses), key=lambda item: (item.version, int(item)))
    )
    audience = f"https://{config.allowed_host}:{config.allowed_port}{config.allowed_path}"
    return AuthorizedEndpointV1(
        hostname=config.allowed_host,
        port=config.allowed_port,
        path=config.allowed_path,
        audience=audience,
        audience_digest=hashlib.sha256(audience.encode("ascii")).hexdigest(),
        approved_ips=approved,
    )
