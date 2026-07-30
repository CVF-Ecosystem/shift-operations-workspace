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
    "task.create": "operator",
    "task.transition": "operator",
    # shift.close is the routine, reversible-in-intent action an operator takes
    # at the end of a shift (mirrors event.create/task.create/task.transition,
    # all "operator"). shift.freeze is the durable, effectively irreversible
    # legal-hold action (post-freeze mutation is correction-only) and stays at
    # the higher "shift_supervisor" bar. P-FIX-6 (2026-07-22): shift.close was
    # previously not a governed action at all (no permission check existed) -
    # see docs/decisions/EA_INDEPENDENT_REVIEW_2026-07-22_CODEX.md, the second
    # independent review that rejected the P-FIX-5 closure claim over this gap.
    "shift.close": "operator",
    "shift.freeze": "shift_supervisor",
    # customer_request.create/transition are routine operator actions, same
    # bar as task.create/task.transition - a customer request is not a
    # risk-classed/durable-commitment record (no risk_class column in the
    # migration), so it does not need the higher supervisor bar.
    "customer_request.create": "operator",
    "customer_request.transition": "operator",
    # Incident (fifth vertical, P2-A): reporting is a routine operator action
    # (mirrors event.create/task.create), acknowledgement is the protected R2+
    # decision that requires the same supervisor bar as event.confirm, and
    # post-acknowledgement transition is a routine operator action again
    # (mirrors task.transition).
    "incident.report": "operator",
    "incident.acknowledge": "shift_supervisor",
    "incident.transition": "operator",
    # Handover (P2A-HANDOVER-VERTICAL): creation is a routine operator action
    # (mirrors incident.report/task.create) since the server derives every
    # item from open work - the caller supplies only the two shift ids.
    # Review (sender) and acknowledge (distinct receiver) are both the higher
    # shift_supervisor bar because they gate the real `open_handover_items_
    # linked` freeze prerequisite - the same bar shift.freeze itself uses.
    "handover.create": "operator",
    "handover.review": "shift_supervisor",
    "handover.acknowledge": "shift_supervisor",
    # Shift creation (SHIFT-CREATE-ADMISSION-REPAIR-2026-07-29): routine
    # operator action, same bar as event.create/task.create/incident.report -
    # shift creation is not itself a risk-classed or durable-commitment
    # decision, so it does not need the higher supervisor bar.
    "shift.create": "operator",
    # Message creation (MESSAGE-ADMISSION-TRUST-REPAIR-2026-07-30): routine
    # operator action, same bar as shift.create/event.create/task.create - a
    # message is append-only RAW input, not a risk-classed or durable-
    # commitment decision, so it does not need the higher supervisor bar.
    "message.create": "operator",
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
