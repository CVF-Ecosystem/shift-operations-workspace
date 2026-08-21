"""P4-A3 SPEC R3/R8 - deterministic layer policy and TTL semantics."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from application_memory.errors import RequestInvalidError, ResultLimitError
from application_memory.models import MemoryLayer
from application_memory.policy import (
    MAX_RESULT_LIMIT,
    MIN_RESULT_LIMIT,
    SESSION_MAX_TTL_SECONDS,
    WORKING_MAX_TTL_SECONDS,
    compute_expiry,
    is_expired,
    max_ttl_seconds,
    normalize_content,
    validate_result_limit,
)

NOW = datetime(2026, 8, 21, 12, 0, tzinfo=timezone.utc)


class TestLayerCeilings:
    def test_session_max_ttl_is_8_hours(self):
        assert SESSION_MAX_TTL_SECONDS == 8 * 3600
        assert max_ttl_seconds(MemoryLayer.SESSION) == 8 * 3600

    def test_working_max_ttl_is_24_hours(self):
        assert WORKING_MAX_TTL_SECONDS == 24 * 3600
        assert max_ttl_seconds(MemoryLayer.WORKING) == 24 * 3600


class TestComputeExpiry:
    def test_within_ceiling_succeeds(self):
        assert compute_expiry(
            created_at_utc=NOW, layer=MemoryLayer.SESSION, requested_ttl_seconds=60
        ) == NOW + timedelta(seconds=60)

    def test_zero_ttl_rejected(self):
        with pytest.raises(RequestInvalidError):
            compute_expiry(created_at_utc=NOW, layer=MemoryLayer.SESSION, requested_ttl_seconds=0)

    def test_session_over_ceiling_rejected(self):
        with pytest.raises(RequestInvalidError):
            compute_expiry(
                created_at_utc=NOW, layer=MemoryLayer.SESSION,
                requested_ttl_seconds=SESSION_MAX_TTL_SECONDS + 1,
            )

    def test_working_at_session_ceiling_is_allowed(self):
        # 8h is within the WORKING 24h ceiling.
        assert compute_expiry(
            created_at_utc=NOW, layer=MemoryLayer.WORKING, requested_ttl_seconds=SESSION_MAX_TTL_SECONDS
        ) == NOW + timedelta(seconds=SESSION_MAX_TTL_SECONDS)


class TestIsExpired:
    def test_inclusive_boundary(self):
        expiry = NOW + timedelta(hours=1)
        assert not is_expired(now=NOW, expires_at_utc=expiry)
        assert is_expired(now=expiry, expires_at_utc=expiry)
        assert is_expired(now=expiry + timedelta(seconds=1), expires_at_utc=expiry)


class TestNormalizeContent:
    def test_nfc_normalization(self):
        assert normalize_content("e\u0301") == "\u00e9"

    def test_idempotent_on_nfc(self):
        assert normalize_content("hello") == "hello"


class TestResultLimit:
    def test_bounds(self):
        assert validate_result_limit(MIN_RESULT_LIMIT) == 1
        assert validate_result_limit(MAX_RESULT_LIMIT) == 50

    @pytest.mark.parametrize("bad", [0, 51, -1, 1.5, True, "10"])
    def test_invalid_limits_rejected(self, bad):
        with pytest.raises(ResultLimitError):
            validate_result_limit(bad)
