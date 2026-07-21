"""Risk classification lookup.

CVF control: ``risk``. Resolves, for a given risk class, the approval and
evidence requirements declared in the profile YAML. This module reads policy;
it does not decide risk class (the domain sets that on the event).
"""

from __future__ import annotations

from dataclasses import dataclass

from cvf_runtime.errors import CvfDenied
from cvf_runtime.policy_loader import CvfProfile


@dataclass(frozen=True)
class RiskRequirement:
    """The controls a given risk class demands."""

    risk_class: str
    required_roles: list[str]  # roles that must each approve (quorum members)
    min_evidence: int


def _required_roles_for(profile: CvfProfile, risk_class: str) -> list[str]:
    """Read approval-policy.yaml for the roles that must approve this class."""
    for rule in profile.approval.get("policies", []):
        when = str(rule.get("when", ""))
        # Rules are written as "risk_class == R2".
        if when.replace(" ", "") == f"risk_class=={risk_class}":
            return list(rule.get("require", []))
    return []


def _min_evidence_for(profile: CvfProfile, risk_class: str) -> int:
    minimum = profile.evidence.get("minimum", {})
    value = minimum.get(risk_class, 0)
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def requirement_for(profile: CvfProfile, risk_class: str) -> RiskRequirement:
    """Resolve the approval + evidence requirement for ``risk_class``."""
    known = set(profile.risk_classes.keys())
    if known and risk_class not in known:
        raise CvfDenied(
            control="risk",
            reason=f"unknown risk class: {risk_class}",
            http_status=422,
        )
    return RiskRequirement(
        risk_class=risk_class,
        required_roles=_required_roles_for(profile, risk_class),
        min_evidence=_min_evidence_for(profile, risk_class),
    )
