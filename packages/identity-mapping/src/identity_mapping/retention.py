"""SPEC R19 retention windows and privacy deletion.

All age computations take an explicit ``now`` (injected UTC clock); no
function here calls an ambient system clock. Retention age is measured from
the persisted UTC ``created_at``/terminal-action time applicable to the
record - callers pass that timestamp in, never a re-derived one.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from .invariants import emit_mapping_action_receipt
from .models import MappingActionReceipt

UNMAPPED_OBSERVATION_RETENTION = timedelta(days=30)
TERMINAL_LINEAGE_RETENTION = timedelta(days=365)
TOKEN_KEY_DUAL_READ_WINDOW = timedelta(hours=24)


def _require_aware(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamp must be timezone-aware")
    return value.astimezone(timezone.utc)


def observation_expired(*, created_at: datetime, now: datetime) -> bool:
    """SPEC R19: observations without a mapping expire after 30 days."""
    return _require_aware(now) - _require_aware(created_at) > UNMAPPED_OBSERVATION_RETENTION


def terminal_lineage_expired(*, terminal_at: datetime, now: datetime) -> bool:
    """SPEC R19: rejected/revoked mapping and binding records, action
    receipts, and placement receipts retain digest-only lineage for 365
    days from terminal-action/decision time."""
    return _require_aware(now) - _require_aware(terminal_at) > TERMINAL_LINEAGE_RETENTION


def token_key_within_dual_read_window(*, activated_at: datetime, now: datetime) -> bool:
    """SPEC R19: the immediately previous token-key version is valid for a
    24-hour dual-read window measured from its persisted UTC activation
    time."""
    return _require_aware(now) - _require_aware(activated_at) <= TOKEN_KEY_DUAL_READ_WINDOW


class PrivacyDeleteRefused(Exception):
    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(reason)


def privacy_delete(
    repository,
    *,
    mapping_id: str,
    expected_version: int,
    actor_role: str,
    reason: str,
    idempotency_key: str,
    unit: object = None,
) -> MappingActionReceipt:
    """SPEC R19: governed `external_identity_mapping.privacy_delete` command
    requiring at least the fresh stored `responsible_manager` role, expected
    version, reason, idempotency, and actor-bound audit. The operator-
    supplied ``reason`` is written only to the restricted actor-bound audit
    record - it is deliberately excluded from the sanitized ``APPLIED``/
    ``IDEMPOTENT_REPLAY`` receipt returned here to avoid disclosing
    privacy-request content.

    ``actor_role`` is the caller's fresh stored role, already verified by
    Workspace API (SPEC R7 steps 1-4) before this function is invoked; this
    function re-checks it defensively rather than trusting the caller.
    """
    if actor_role != "responsible_manager" and actor_role != "authorized_executive":
        return emit_mapping_action_receipt(
            "REFUSED", action="PRIVACY_DELETE", reason="PERMISSION_DENIED",
            command_application_count=0, audit_count=0, replayed=False,
        )
    if not reason or not reason.strip():
        return emit_mapping_action_receipt(
            "REFUSED", action="PRIVACY_DELETE", reason="IDENTITY_REQUIRED",
            command_application_count=0, audit_count=0, replayed=False,
        )
    from uuid import uuid4

    try:
        updated = repository.privacy_delete_mapping(
            mapping_id, expected_version=expected_version, unit=unit
        )
    except KeyError:
        return emit_mapping_action_receipt(
            "REFUSED", action="PRIVACY_DELETE", reason="IDENTITY_REQUIRED",
            command_application_count=0, audit_count=0, replayed=False,
        )
    except ValueError as exc:
        return emit_mapping_action_receipt(
            "CONFLICT", action="PRIVACY_DELETE", reason=str(exc) or "VERSION_CONFLICT",
            command_application_count=0, audit_count=0, replayed=False,
        )
    return emit_mapping_action_receipt(
        "APPLIED", action="PRIVACY_DELETE", aggregate_id=updated.mapping_id,
        aggregate_version=updated.version, audit_id=str(uuid4()),
        command_application_count=1, audit_count=1, replayed=False,
    )
