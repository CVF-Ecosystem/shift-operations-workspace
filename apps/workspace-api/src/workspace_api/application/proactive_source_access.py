"""Server-owned identity and self scope for the read-only proactive source API."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json

from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal
from cvf_runtime.permission import require_action

from .proactive_source import TrustedSourceScope
from .proactive_source_receipt import COHORT_VERSION


class AccessFailure(Exception):
    def __init__(self, status: int):
        self.status = status


@dataclass(frozen=True)
class SourceAccess:
    principal: Principal
    expires_at: datetime
    ledger: object
    instance_id: str
    clock: object


def _now(clock) -> datetime:
    value = clock()
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise AccessFailure(403)
    return value.astimezone(timezone.utc)


def check_access(access: SourceAccess) -> datetime:
    """Check the verified token against current stored identity and action."""
    now = _now(access.clock)
    if access.expires_at <= now:
        raise AccessFailure(401)
    try:
        user = access.ledger.get_user_by_id(access.principal.user_id)
        if user is None or not user.is_active or user.role != access.principal.role:
            raise AccessFailure(403)
        require_action(access.principal, "proactive.source.read")
    except CvfDenied as exc:
        raise AccessFailure(403) from exc
    except AccessFailure:
        raise
    except Exception as exc:
        raise AccessFailure(403) from exc
    return now


def server_scope(access: SourceAccess) -> TrustedSourceScope | None:
    instance = access.instance_id
    if (not isinstance(instance, str) or not 0 < len(instance) <= 128
            or any(ord(char) < 33 or ord(char) > 126 for char in instance)):
        return None
    raw = json.dumps({
        "instance_id": instance,
        "actor_id": access.principal.user_id,
        "cohort_policy_version": COHORT_VERSION,
    }, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
       allow_nan=False).encode("utf-8")
    return TrustedSourceScope(
        "P5A2-SELF-" + sha256(raw).hexdigest(), access.principal.user_id, instance,
    )
