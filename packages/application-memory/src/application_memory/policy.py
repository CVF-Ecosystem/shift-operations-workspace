"""Deterministic layer policy (SPEC R3/R8).

Closed SESSION/WORKING TTL ceilings, content normalization, deterministic
expiry and the read-result-limit bounds. Pure module: standard library plus
the closed enums from ``models``. No I/O, no clock/id creation, no provider
access - ``now`` is always caller-supplied.
"""

from __future__ import annotations

import unicodedata
from datetime import datetime, timedelta

from .errors import RequestInvalidError, ResultLimitError
from .models import (
    LAYER_MAX_TTL_SECONDS,
    MemoryLayer,
    SESSION_MAX_TTL_SECONDS,
    WORKING_MAX_TTL_SECONDS,
)

# SPEC R8 - read result limit bounds.
MIN_RESULT_LIMIT = 1
MAX_RESULT_LIMIT = 50


def max_ttl_seconds(layer: MemoryLayer) -> int:
    """The layer's hard TTL ceiling in seconds (SPEC R3)."""
    return LAYER_MAX_TTL_SECONDS[layer]


def normalize_content(text: str) -> str:
    """SPEC R2 - deterministic Unicode normalization (NFC). The strict model
    also rejects non-NFC input, so this is the explicit canonical form used
    for both storage and digest computation."""
    return unicodedata.normalize("NFC", text)


def compute_expiry(
    *, created_at_utc: datetime, layer: MemoryLayer, requested_ttl_seconds: int
) -> datetime:
    """SPEC R3 - requested TTL must be positive and within the layer ceiling.
    Returns ``created_at + requested_ttl`` on success, else raises."""
    ceiling = max_ttl_seconds(layer)
    if requested_ttl_seconds <= 0:
        raise RequestInvalidError("requested_ttl_seconds must be positive")
    if requested_ttl_seconds > ceiling:
        raise RequestInvalidError("requested TTL exceeds the layer ceiling")
    return created_at_utc + timedelta(seconds=requested_ttl_seconds)


def is_expired(*, now: datetime, expires_at_utc: datetime) -> bool:
    """SPEC R3 - an entry is expired at ``now >= expires_at_utc`` (inclusive)."""
    return now >= expires_at_utc


def validate_result_limit(limit: int) -> int:
    """SPEC R8 - the read limit is the closed interval 1..50."""
    if not isinstance(limit, int) or isinstance(limit, bool):
        raise ResultLimitError("limit must be an integer")
    if limit < MIN_RESULT_LIMIT or limit > MAX_RESULT_LIMIT:
        raise ResultLimitError("limit must be within 1..50")
    return limit
