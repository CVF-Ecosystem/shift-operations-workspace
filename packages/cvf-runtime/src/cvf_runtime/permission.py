"""Permission boundary.

CVF control: ``permission``. Having an identity is not authority. This gate
answers "may THIS principal perform THIS action", independent of whether an
approval quorum is later required.

Role authority is ordered: a higher role subsumes the actions of lower ones for
the coarse-grained actions modelled here. Approval quorums (dual/escalation)
are enforced separately in :mod:`cvf_runtime.approval` — permission alone never
substitutes for a required second approver.
"""

from __future__ import annotations

from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal

# Ascending authority. Index is the authority level.
_ROLE_RANK: dict[str, int] = {
    "viewer": 0,
    "operator": 1,
    "shift_supervisor": 2,
    "responsible_manager": 3,
    "authorized_executive": 4,
}

# Minimum role required to perform each governed action.
_ACTION_MIN_ROLE: dict[str, str] = {
    "event.create": "operator",
    "event.confirm": "shift_supervisor",
    "event.correct": "shift_supervisor",
    "shift.freeze": "shift_supervisor",
}


def _rank(role: str) -> int:
    return _ROLE_RANK.get(role, -1)


def require_action(principal: Principal, action: str) -> None:
    """Raise :class:`CvfDenied` if ``principal`` may not perform ``action``."""
    min_role = _ACTION_MIN_ROLE.get(action)
    if min_role is None:
        raise CvfDenied(
            control="permission",
            reason=f"unknown governed action: {action}",
            http_status=403,
        )
    if _rank(principal.role) < _rank(min_role):
        raise CvfDenied(
            control="permission",
            reason=(
                f"role {principal.role!r} may not perform {action!r} "
                f"(requires at least {min_role!r})"
            ),
            http_status=403,
        )


def has_authority(role: str, min_role: str) -> bool:
    """True if ``role`` meets or exceeds ``min_role`` authority."""
    return _rank(role) >= _rank(min_role)
