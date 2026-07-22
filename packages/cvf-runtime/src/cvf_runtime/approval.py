"""Approval gate.

CVF control: ``approval``. This replaces the symbolic check the first EA
review flagged in ``application/services.py`` (``if risk in {R2,R3,R4} and not
approver_id``), which only tested that a string was non-empty and never checked
that the approver held the required authority or that a dual/escalation quorum
was actually met.

Here an approval is a concrete record: who approved, in what role. The gate
verifies that the set of approvals satisfies every role the risk class demands,
that no single principal fills two required seats, and that a confirmer cannot
self-approve when a quorum is required.

2026-07-22 correction (Codex independent review, High Finding #4.1): a second
review proved this gate accepted ANY caller-supplied ``approver_id``/``role``
pair in the same request as fabricated authorization - the quorum *shape* was
checked but the approver's identity/authority was not. This module now cross-
checks every approval against ``known-principals.yaml`` via
``CvfProfile.known_role_for``: the approver_id must be a known principal AND
its registered role must grant the authority the approval claims. This is an
interim measure, not real authentication (no signature/token/session) - see
P2-B in the roadmap for that.
"""

from __future__ import annotations

from pydantic import BaseModel

from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal
from cvf_runtime.permission import has_authority
from cvf_runtime.policy_loader import CvfProfile
from cvf_runtime.risk import requirement_for


class Approval(BaseModel):
    """A single approval seat filled by a principal acting in a role."""

    approver_id: str
    role: str


def assert_approval_satisfied(
    *,
    profile: CvfProfile,
    risk_class: str,
    confirmer: Principal,
    approvals: list[Approval],
) -> None:
    """Raise :class:`CvfDenied` unless the approval quorum is met.

    Rules enforced:
    * Every role listed in approval-policy.yaml for the risk class must be
      filled by an approver with at least that role's authority.
    * Distinct required roles must be filled by distinct principals (no one
      person satisfies a two-person quorum).
    * When any quorum is required, the confirmer cannot also be the sole
      approver of a seat unless another principal fills the remaining seat(s).
    """
    requirement = requirement_for(profile, risk_class)
    required_roles = requirement.required_roles
    if not required_roles:
        return  # R0/R1: no approval quorum required.

    used_principals: set[str] = set()
    for required_role in required_roles:
        seat = _find_seat(profile, approvals, required_role, exclude=used_principals)
        if seat is None:
            raise CvfDenied(
                control="approval",
                reason=(
                    f"{risk_class} requires approval by role {required_role!r} "
                    f"from a distinct, known principal with that authority; "
                    f"quorum not met"
                ),
                http_status=409,
            )
        used_principals.add(seat.approver_id)

    # Self-approval guard: a required quorum cannot be satisfied entirely by the
    # confirmer acting alone.
    if used_principals == {confirmer.user_id}:
        raise CvfDenied(
            control="approval",
            reason=f"{risk_class} requires an approver other than the confirmer",
            http_status=409,
        )


def _find_seat(
    profile: CvfProfile, approvals: list[Approval], required_role: str, exclude: set[str]
) -> Approval | None:
    """Find an unused, KNOWN approval whose role has authority for ``required_role``.

    An approval only counts if:
    1. its approver_id is not already used for another seat in this quorum;
    2. its approver_id is a known principal (registered in
       known-principals.yaml) - a caller can no longer invent an id outright;
    3. the registered role for that principal actually grants the claimed
       authority (a caller can no longer claim a higher role than the
       principal is registered for).
    """
    for approval in approvals:
        if approval.approver_id in exclude:
            continue
        registered_role = profile.known_role_for(approval.approver_id)
        if registered_role is None:
            continue  # unknown principal: cannot be used as an approver seat
        if not has_authority(registered_role, required_role):
            continue  # known, but not authorized enough for this seat
        if not has_authority(approval.role, required_role):
            continue  # declared role (even if honest) doesn't meet the bar
        return approval
    return None
